
import openai
import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv() # Load immediately

class LLMService:
    def __init__(self):
        # Allow API key from env or use a placeholder for now if not set
        self.api_key = os.getenv("OPENAI_API_KEY") 
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            print("⚠️ STARTUP WARNING: OPENAI_API_KEY not set. LLM will use mock responses.")
            self.client = None

    def generate_grounded_response(self, user_query: str, evidence: List[Dict], verdict: str, fallback_text: str = "") -> str:
        """
        Generates a response grounded ONLY in the provided evidence.
        Returns fallback_text if LLM is unavailable.
        """
        if not self.client:
            return fallback_text or self._mock_response(user_query, verdict)

        # Construct Context from Evidence
        context_str = ""
        for item in evidence:
            context_str += f"- [{item['type'].upper()} ({item['score']:.2f})]: {item['content']} (Source: {item.get('metadata', {}).get('source', 'Unknown')})\n"

        system_prompt = """You are HealthGuard AI, a medical verification assistant.
Your goal is to answer the user's query based ONLY on the provided retrieval evidence.
1. If the verdict is TRUE, confirm it and cite the specific evidence.
2. If the verdict is MISLEADING/FALSE, debunk it using the evidence.
3. If the verdict is INSUFFICIENT EVIDENCE, politely state you don't know.
4. BE CONCISE. No fluff. Maximum 3 sentences.
5. ALWAYS allow for "Consult a doctor" advice if relevant.
DO NOT use outside knowledge not present in the snippets."""

        user_prompt = f"""
Query: {user_query}
Verdict: {verdict}

Evidence:
{context_str}

Generate a patient-friendly response:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            # Fallback to the Rule-Based Answer (Hybrid Mode)
            return fallback_text if fallback_text else self._mock_response(user_query, verdict, str(e))

    def _mock_response(self, query: str, verdict: str, error_msg: str = "") -> str:
        """Fallback if no API key or error."""
        debug_info = f"\n\n*(Debug: LLM Generation failed. Cause: {error_msg})*" if error_msg else ""
        
        if verdict == "True":
            return f"**Confirmed**: Based on trusted medical data, this appears to be true. logic: {query}{debug_info}"
        elif verdict == "False":
            return f"**Debunked**: This claim is contradicted by medical evidence.{debug_info}"
        else:
            return f"I could not verify this claim in my current knowledge base.{debug_info}"
