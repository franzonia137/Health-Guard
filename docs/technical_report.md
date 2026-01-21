# HealthGuard AI: Technical Report

## 1. Problem Statement
**The Challenge**: Misinformation in healthcare is not just annoying; it is dangerous. From fake cancer cures to vaccine myths, unverified advice spreads faster than truth.
**The Solution**: HealthGuard AI is a **multimodal verification system** designed to act as a digital immune system. It doesn't just "chat"; it performs **retrieval-augmented verification** using trusted sources (PubMed, CDC, WHO) and analyzes visual claims (e.g., "Is this a real heart diagram?").

## 2. System Design
The system follows a strict **Retrieval-Augmented Generation (RAG)** pipeline, prioritized for accuracy over creativity.

### Architecture
1.  **Ingestion Layer**:
    *   **Live Feeds**: Fetches real-time RSS data from PubMed and WHO.
    *   **Visual Indexing**: Uses `clip-ViT-B-32` to embed medical imagery (not just text descriptions).
2.  **Storage Layer (Qdrant)**:
    *   `medical_facts`: Trusted knowledge base.
    *   `medical_images`: Visual reference database.
    *   `medical_misinfo`: Known myths database.
    *   `user_memory`: Long-term session history (Evolving Representations).
3.  **Agentic Layer**:
    *   **Hybrid Logic**: If a query matches a known visual concept ("Show me..."), it prioritizes **Vision Search**. If it's a claim, it routes to **Fact-Checking**.
    *   **Grounded LLM**: GPT-4 is used *only* to synthesize fetched evidence, not to hallucinate answers.

## 3. Multimodal Strategy
We specifically chose **CLIP (Contrastive Language-Image Pre-training)** because medical queries are often visual ("What does a melanoma look like?").
*   **Text-to-Image**: User asks "Show me a kidney", we embed the text and find the closest image vector.
*   **Image-to-Image**: (Future scope) User uploads a rash, we match it against verified dermatology databases.

## 4. Search, Memory & Recommendation
*   **Search**: We usage **Hybrid Search** (Dense Vector Search + Keyword Filtering).
*   **Memory ("Evolving Representations")**: The system implements a **Reinforcement Mechanism**:
    *   memories start with a default `decay_weight`.
    *   Every time a topic is recalled (e.g., "flu"), its `access_count` increments and its signal is boosted (`reinforce_memory`).
    *   This mimics biological memory (Long-Term Potentiation), ensuring frequent health concerns stay "top of mind" for the agent.

## 5. Limitations & Ethical Considerations
*   **No Diagnosis**: The system explicitly refuses to diagnose. It provides *information*, not medical advice.
*   **Bias**: Taking data only from Western sources (CDC/WHO) might introduce geographic bias.
*   **Fallback**: If the LLM goes down, we have a hard-coded "Safe Mode" that returns raw database hits without synthesis.
