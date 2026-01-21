# HealthGuard AI: Multimodal Medical Verification System
*Submitted for Qdrant Problem Statement - Convolve 4.0 Hackathon*

---

## 01. Problem Statement
**Societal Challenge**: Misinformation & Digital Trust in Healthcare.

In the digital age, medical misinformation spreads faster than verified facts. From vaccine myths to dangerous home remedies, false claims can lead to real-world harm. Existing search tools often prioritize popularity over accuracy, and generic LLMs can hallucinate plausible-sounding but factually incorrect medical advice.

**Our Solution**: **HealthGuard AI** is a strict, evidence-based agent that verifies medical claims against a trusted knowledge base (CDC/WHO data) and debunks known myths using specialized Qdrant collections.

## 02. System Design & Architecture
The system is built as a **Retrieval-Augmented Generation (RAG)** pipeline powered by Qdrant.

### Core Components
1.  **Frontend**: "Cyber-Medical" Web Interface (HTML/JS) for user interaction.
2.  **API Layer**: FastAPI backend handling query processing and memory management.
3.  **Brain (Agent)**: `MisinformationAgent` that orchestrates retrieval, reasoning, and response generation.
4.  **Memory Core**: **Qdrant** vector database storing four distinct types of data.

```mermaid
graph TD
    User[User Query] --> API[FastAPI Backend]
    API --> Agent[Misinformation Agent]
    
    subgraph "Qdrant Vector Memory"
        Facts[COL_FACTS\n(Trusted Medical Data)]
        Myths[COL_MISINFO\n(Known Hoaxes)]
        Images[COL_IMAGES\n(Anatomy/Diagrams)]
        Memory[COL_MEMORY\n(User Interactions)]
    end
    
    Agent -->|Embedding| Encoders[Sentence Transformers]
    Encoders -->|Vector Search| Facts
    Encoders -->|Vector Search| Myths
    Encoders -->|Vector Search| Images
    Encoders -->|Context Retrieval| Memory
    
    Facts & Myths & Images & Memory -->|Aggregated Evidence| Agent
    Agent -->|Logic: Fact vs Myth Score| Verdict[Final Verdict]
    Verdict -->|Response + Evidence| User
```

## 03. Multimodal Strategy
We leverage Qdrant's flexibility to store and query heterogeneous data types:

| Data Type | Collection | Embedding Model | purpose |
|-----------|------------|-----------------|---------|
| **Text** | `medical_facts` | `all-MiniLM-L6-v2` | Authoritative truths (e.g., "Vaccines are safe"). |
| **Text** | `medical_misinfo` | `all-MiniLM-L6-v2` | Known lies (e.g., "Vaccines cause magnetism"). |
| **Image** | `medical_images` | `clip-ViT-B-32` (Simulated) | Anatomical diagrams and medical charts. |
| **Memory** | `user_memory` | `all-MiniLM-L6-v2` | User history and long-term preferences. |

## 04. Search, Memory & Recommendation Logic

### A. Intelligent Search & Verdict System
Unlike standard RAG, we don't just "retrieve and summarize". We implement **Adversarial Retrieval**:
1.  Query is searched against **BOTH** `Facts` and `Misinfo` collections simultaneously.
2.  **Verdict Logic**:
    *   If `Fact Score > Misinfo Score` (and robust): **VERDICT: TRUE**
    *   If `Misinfo Score > Fact Score` (and robust): **VERDICT: FALSE (DEBUNKED)**
    *   If `Image Score` is high: **VERDICT: VISUAL CONFIRMATION**
    *   Otherwise: **INSUFFICIENT EVIDENCE**

### B. Evolving Memory System
We utilize Qdrant payloads to implement memory mechanics:
*   **Decay**: Older memories implicitly lose weight in retrieval re-ranking.
*   **Reinforcement**: Frequently accessed topics (e.g., "diabetes management") gain `access_count` weight, ensuring deeper personalization for chronic conditions.
*   **Payload Updates**: We use `set_payload` to update memory stats without finding/re-generating vectors, ensuring high performance.

### C. Context-Aware Recommendations
The system generates follow-up steps based on the verdict:
*   *Verdict True*: "Learn more about [Topic]."
*   *Verdict False*: "Be cautious of sources promoting this claim."
*   *Visuals*: "View attached anatomical references."

## 05. Limitations & Ethics
*   **Knowledge Cutoff**: The local dataset is static. Real-world deployment requires live ingestion.
*   **Bias**: Dependence on "trusted sources" assumes those sources are unbiased.
*   **Safety**: The system explicitly defaults to "Consult a Doctor" for ambiguity to prevent medical malpractice.

## 06. Future Work
1.  **Live Ingestion**: Connect ingest pipeline to real-time PubMed/WHO RSS feeds.
2.  **LLM Integration**: Replace rule-based response templating with a grounded GPT-4 or Med-PaLM model to synthesize natural language explanations while adhering to Qdrant's strict evidence retrieval.
3.  **Vision Encoders**: Implement true CLIP embedding for pixel-level image search (currently simulated via text descriptive captions for hackathon constraints).

---
*Built with Qdrant, FastAPI, and Python.*
