from typing import List, Dict, Any
from app.embeddings import EmbeddingModel
from app.qdrant_client_wrapper import QdrantHandler
from app.memory import MemoryManager
from app.schemas import AgentQueryRequest, AgentResponse, SearchResultItem
from app.llm_service import LLMService
import uuid

class MisinformationAgent:
    def __init__(self):
        self.db = QdrantHandler()
        self.embedder = EmbeddingModel()
        self.llm = LLMService()
        self.memory = MemoryManager(self.db, self.embedder)
        self.db.init_collections()

    def process_query(self, request: AgentQueryRequest) -> AgentResponse:
        user_id = request.user_id
        session_id = request.session_id
        query = request.query
        
        # 1. Retrieve Context
        past_memories = self.memory.get_context(user_id, query)
        
        # 2. Parallel Search (Facts vs Misinfo)
        q_vec = self.embedder.encode_text(query)
        
        facts = self.db.search(self.db.COL_FACTS, q_vec, top_k=2)
        misinfo = self.db.search(self.db.COL_MISINFO, q_vec, top_k=2)
        images = self.db.search(self.db.COL_IMAGES, self.embedder.encode_text_for_image_search(query), top_k=2)
        
        # 3. Analyze Veracity (Engine Logic)
        best_fact = facts[0] if facts else None
        best_misinfo = misinfo[0] if misinfo else None
        best_image = images[0] if images else None
        
        fact_score = best_fact.score if best_fact else 0.0
        misinfo_score = best_misinfo.score if best_misinfo else 0.0
        image_score = best_image.score if best_image else 0.0
        
        verdict = "Insufficient Evidence"
        reasoning = "No strong evidence was found in the medical knowledge base."
        final_answer = "I could not verify this claim based on trusted medical data."
        recommendations = ["Consult a doctor for personal medical advice.", "Check WHO.org for latest guidelines."]
        
        THRESHOLD = 0.20 # Adjusted for MiniLM cosine similarity range
        
        # Detect Visual Intent (Simple Heuristic or use LLM later)
        visual_intent = any(keyword in query.lower() for keyword in ["show", "image", "picture", "diagram", "scan", "photo", "see"])
        
        # Priority Logic
        # If user WANTS images and we have a good match, prioritize it.
        if visual_intent and image_score > THRESHOLD:
             verdict = "True"
             reasoning = f"Found verifiable medical imagery with high confidence ({image_score:.2f})."
             final_answer = f"**VISUAL CONFIRMATION**: Found relevant medical diagrams for '{best_image.payload.get('caption')}'."
             recommendations.append(f"View the attached anatomical references.")
        
        elif fact_score > THRESHOLD and fact_score > misinfo_score:
            verdict = "True"
            reasoning = f"Matched verifiable medical fact from {best_fact.payload.get('source')} with high confidence ({fact_score:.2f})."
            final_answer = f"**CONFIRMED**: {best_fact.payload.get('body')}"
            recommendations.append(f"Learn more about {best_fact.payload.get('topic', 'health')}.")
            
        elif misinfo_score > THRESHOLD and misinfo_score > fact_score:
            verdict = "False"
            reasoning = f"Matched known health misinformation (Myth: '{best_misinfo.payload.get('body')}') with high confidence ({misinfo_score:.2f})."
            final_answer = f"**DEBUNKED**: This claim is likely false. Accurate information: Medical consensus does not support this."
            recommendations.append("Be cautious of sources promoting this claim.")
            
        elif image_score > THRESHOLD:
            verdict = "True"
            reasoning = f"Found verifiable medical imagery with high confidence ({image_score:.2f})."
            final_answer = f"**VISUAL CONFIRMATION**: Found relevant medical diagrams for '{best_image.payload.get('caption')}'."
            recommendations.append(f"View the attached anatomical references.")
            
        elif fact_score > 0.15 or misinfo_score > 0.15: # Lower fallback threshold
            verdict = "Misleading" if misinfo_score > fact_score else "True"
            reasoning = "Evidence found but confidence is moderate. Context is required."
            if verdict == "True":
                 final_answer = f"Likely True: Evidence suggests {best_fact.payload.get('body')}"
            else:
                 final_answer = f"Likely False: This resembles known myths about {best_misinfo.payload.get('topic')}."
        
        # 4. Prepare Evidence for LLM & Frontend
        evidence_items = []
        llm_context = []
        
        for f in facts:
            item = SearchResultItem(id=str(f.id), score=f.score, content=f.payload.get('body'), metadata=f.payload, type="fact", source_collection="medical_facts")
            evidence_items.append(item)
            llm_context.append({"content": f.payload.get('body'), "score": f.score, "type": "fact", "metadata": f.payload})
            
        for m in misinfo:
            item = SearchResultItem(id=str(m.id), score=m.score, content=m.payload.get('body'), metadata=m.payload, type="misinformation", source_collection="medical_misinfo")
            evidence_items.append(item)
            llm_context.append({"content": m.payload.get('body'), "score": m.score, "type": "misinfo", "metadata": m.payload})
            
        for i in images:
            item = SearchResultItem(id=str(i.id), score=i.score, content=i.payload.get('caption'), metadata=i.payload, type="image", source_collection="medical_images")
            evidence_items.append(item)
            llm_context.append({"content": i.payload.get('caption'), "score": i.score, "type": "image", "metadata": i.payload})

        # 5. Generate Grounded Response (LLM)
        # Pass the rule-based 'final_answer' as fallback. 
        # If LLM fails (Quota/Error), the user still gets the specific "VISUAL CONFIRMATION" or "DEBUNKED" message.
        final_answer = self.llm.generate_grounded_response(query, llm_context, verdict, fallback_text=final_answer)
        
        # 6. Update Memory
        self.memory.add_memory(user_id, session_id, f"Query: {query} | Verdict: {verdict}", memory_type="history")
        
        return AgentResponse(
            final_answer=final_answer,
            verdict=verdict,
            reasoning_trace=reasoning,
            evidence=evidence_items,
            recommendations=recommendations,
            memory_actions=["stored_interaction"]
        )
