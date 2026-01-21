import uuid
import time
from typing import List, Optional
from qdrant_client.http import models
from app.qdrant_client_wrapper import QdrantHandler
from app.embeddings import EmbeddingModel
from app.schemas import MemoryItem

class MemoryManager:
    def __init__(self, db: QdrantHandler, embedder: EmbeddingModel):
        self.db = db
        self.embedder = embedder
        self.COLLECTION = db.COL_MEMORY

    def add_memory(self, user_id: str, session_id: str, text: str, memory_type: str = "summary"):
        vector = self.embedder.encode_text(text)
        mem_id = str(uuid.uuid4())
        
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "memory_type": memory_type,
            "timestamp": str(time.time()),
            "raw_text": text,
            "decay_weight": 1.0,
            "access_count": 1,
            "last_accessed": time.time()
        }
        
        point = models.PointStruct(id=mem_id, vector=vector, payload=payload)
        self.db.upsert_points(self.COLLECTION, [point])
        print(f"[Memory] Stored ({memory_type}): {text[:30]}...")
        return mem_id

    def get_context(self, user_id: str, query: str, top_k=3) -> List[MemoryItem]:
        query_vector = self.embedder.encode_text(query)
        filters = {"user_id": user_id}
        
        results = self.db.search(self.COLLECTION, query_vector, top_k=top_k, filters=filters)
        
        memories = []
        updates = []
        
        for res in results:
            data = res.payload
            mem_item = MemoryItem(**data)
            
            # --- MEMORY EVOLUTION LOGIC ---
            # 1. Decay: Older memories accessed less frequently might have lower relevance (simulated here)
            # 2. Reinforcement: Every time we retrieve it, we boost its "access_count"
            
            new_count = mem_item.access_count + 1
            new_weight = mem_item.decay_weight + 0.1 # Boost importance on recall
            
            # Update local object
            mem_item.access_count = new_count
            mem_item.decay_weight = new_weight
            mem_item.last_accessed = time.time()
            
            memories.append(mem_item)
            
            # Queue update to DB (Reinforcement) - Use payload update to avoid vector requirement
            try:
                self.db.update_payload(self.COLLECTION, mem_item.dict(), str(res.id))
            except Exception as e:
                print(f"[Memory] Failed to reinforce memory {res.id}: {e}")
            
        print(f"[Memory] Reinforced {len(memories)} memories.")

            
        return memories

    def forget_memory(self, user_id: str, memory_id: str):
        # Implementation for "Deletion" requirement
        self.db.delete_point(self.COLLECTION, memory_id)
        print(f"[Memory] Deleted memory {memory_id}")
