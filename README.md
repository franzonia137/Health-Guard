# 🏥 HealthGuard AI: Multimodal Medical Verification Agent

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.13-yellow.svg) ![Qdrant](https://img.shields.io/badge/vector_db-Qdrant-red.svg) ![OpenAI](https://img.shields.io/badge/LLM-GPT--4o-green.svg)

**A "Real AI" System tackling Healthcare Misinformation using Qdrant, CLIP Vision, and Grounded Reasoning.**

---

## 🏆 Hackathon Submission Details

### 1. Problem Statement: The Misinformation Epidemic
**Societal Issue**: False medical claims spread faster than facts. From "vaccine magnetism" to dangerous home remedies, unverified information risks lives.
**Why It Matters**: Current search engines rely on keywords, not medical consensus. Users need a system that can "see" their medical images, "read" the latest CDC reports, and "reason" about contradictions, rather than just generating confident hallucinations.

---

### 2. System Design
Our solution is a **Modular RAG Architecture** built entirely around **Qdrant**.

**Architecture Overview**:
1.  **Ingestion Layer**: Real-time scripts (`ingest_live.py`) fetch RSS feeds from WHO/CDC.
2.  **Multimodal Storage**: Qdrant stores vectors for Text (Facts/Myths), Images (CLIP), and History (Memory).
3.  **The "Trust Engine"**: A Python-based agent (`agent.py`) that orchestrates parallel retrieval and logic checks.
4.  **Hybrid Generation**: Uses OpenAI GPT-4o-mini for synthesis, falling back to a deterministic Rule Engine if APIs fail.

**Critical Role of Qdrant**:
Qdrant is not just a database here; it is the **cortex**. It unifies:
*   Semantic Text (for facts)
*   Visual Embeddings (for images)
*   Interaction History (for memory)
...into a single, queryable interface that drives 100% of the agent's decisions.

---

### 3. Multimodal Strategy
We demonstrate "True Multimodality" by processing distinct data types in shared vector spaces.

| Data Type | Embedding Model | Qdrant Collection | Purpose |
| :--- | :--- | :--- | :--- |
| **Medical Text** | `all-MiniLM-L6-v2` | `medical_facts` | Ground truth from PubMed/CDC. |
| **Medical Myths** | `all-MiniLM-L6-v2` | `medical_misinfo` | Known lies for active debunking. |
| **Images** | `clip-ViT-B-32` | `medical_images` | Pixel-level anatomical search. |
| **User History** | `all-MiniLM-L6-v2` | `user_memory` | Long-term context retention. |

**Query Logic**:
When a user asks "Show me heart anatomy":
1.  We detect **Visual Intent**.
2.  We encode the *text query* using the CLIP Text Encoder.
3.  We search the `medical_images` collection (Vectors created by CLIP Image Encoder).
4.  This Cross-Modal search retrieves the correct diagram without needing filename matches.

---

### 4. Search, Memory & Recommendation Logic
**Retrieval ("The Trust Engine")**:
The system performs a **3-Way Parallel Search** for every query:
*   *Fact Search* vs. *Misinfo Search*: Comparing similarity scores determines if a claim is verified or debunked.
*   *Re-Ranking*: We prioritize "Visual Matches" if the user explicitly asks for images (e.g., "Show me...").

**Memory (Beyond Single Prompt) - "Evolving Representations"**:
We implemented a dynamic `MemoryManager` (`app/memory.py`) that strictly satisfies the hackathon's "Evolving Representations" requirement:
*   **Reinforcement**: Every time a memory is retrieved, the system increments its `access_count` and boosts its `decay_weight` (Line 53 of `memory.py`).
*   **Real-time Updates**: These modified weights are written back to the Qdrant index immediately avoiding static memory.
*   **Decay Simulation**: The retrieval logic favors higher-weight memories, allowing unused interactions to naturally fade while important context ("knowledge") is reinforced over time.

---

### 5. Limitations & Ethics
**Ethical Guardrails**:
*   **Bias Mitigation**: We explicitly ingest "Medical Myths" (`medical_misinfo`) to train the vector space on what *not* to believe, reducing the chance of accidental agreement with popular conspiracies.
*   **Deployment**: The system runs locally (privacy-first). No private medical data is sent to the cloud processing pipeline except the anonymized final prompt.

**Known Limitations**:
*   **Latency**: CLIP encoding on CPU can take ~200ms per interactive query (acceptable for demo).
*   **Visual Scope**: Currently limited to pre-ingested anatomical references (extensible).

---

## 📦 Installation & Demo

### 1. Setup
```bash
make setup
```

### 2. Configure (Optional)
```bash
# Add API Key for GPT-4 Reasoning (System runs in Rule-Mode without it)
echo "OPENAI_API_KEY=sk-..." > project/.env
```

### 3. Ingest Real Data
```bash
# Fetch Live RSS & Index Images
python3 scripts/ingest_live.py
python3 scripts/ingest_manual_images.py
```

### 4. Run UI
```bash
make run-api
```
**URL**: [http://localhost:8000](http://localhost:8000)

**Try these inputs**:
1.  *"Show me heart anatomy"* (Tests **Multimodal/CLIP**)
2.  *"Is it true that vaccines cause magnetism?"* (Tests **Debunking/Reasoning**)
3.  *"What are latest Bird Flu updates?"* (Tests **Live Ingestion**)

---
*Submitted for the 2026 AI Hackathon*
