# Project Report: Multimodal Misinformation & Digital Trust Assistant

## Problem Statement
In the age of rapid information spread, distinguishing between real and fake news is increasingly difficult. Misinformation often spreads not just through text, but through memes, manipulated images, and out-of-context media. A purely text-based fact-checker is insufficient. We need a system that can understand and verify claims across modalities (text and image) while retaining user trust through persistent memory and evidence-based reasoning.

## System Design
The system is built as a Retrieval-Augmented Generation (RAG) agent using **Qdrant** as the central nervous system.

### Architecture
- **Frontend/Client**: Communicates via REST API.
- **Backend Service**: FastAPI handling intent parsing and orchestration.
- **Vector Database**: Qdrant (Dockerized).
  - `kb_text`: Stores text claims/articles with `all-MiniLM-L6-v2` embeddings.
  - `kb_image`: Stores images/memes with `CLIP-ViT-B-32` embeddings.
  - `memory_longterm`: Stores user sessions and summary facts.
- **Agent Logic**: 
  - Parses queries to determine intent (Search vs. Verify vs. Recommend).
  - Performs hybrid/multimodal retrieval.
  - Generates responses grounded in the retrieved "Evidence" list.

**Why Qdrant?**
Qdrant is critical because it supports:
1.  **Multiple Collections**: Clean separation of Text, Image, and Memory vectors.
2.  **Filtering**: metadata filtering (source, date, topic) ensures precise retrieval.
3.  **Performance**: Fast local vector search suitable for real-time agent responses.

## Multimodal Strategy
The system handles two primary modalities:
1.  **Text**: Encoded using Sentence-Transformers (`all-MiniLM-L6-v2`). Used for claims and article bodies.
2.  **Image**: Encoded using CLIP (`clip-ViT-B-32`). Used for memes and news images. 
    - *Cross-Modal Search*: When a user queries in text, we map the text to the CLIP embedding space to find semantically relevant images (e.g., query "fake moon landing" retrieves image of a moon set).

## Search, Memory, and Recommendation Logic
1.  **Search**: 
    - Incoming query is embedded into Text Vector and Image Vector.
    - Parallel search across `kb_text` and `kb_image`.
    - Results are merged and re-ranked (currently simple score sort).
2.  **Memory**:
    - User interactions are summarized and stored in `memory_longterm`.
    - Before answering a new query, the agent searches memory for relevant past context (e.g., "User previously asked about climate change").
    - This allows the agent to tailor responses or reference prior verdicts.
3.  **Recommendations**:
    - Based on the retrieved topic, the agent can recommend next steps (e.g., "Check this related verified article").

## Limitations & Ethics
- **Bias in Embeddings**: Pre-trained models like CLIP can exhibit social biases.
- **Fact-Checking Limitation**: The system relies on the *retrieved context*. If the knowledge base contains false info labelled as true, the agent will hallucinate correctness. (Garbage In, Garbage Out).
- **Privacy**: Storing user queries in persistent memory requires strict access controls (simulated here via user_id partitioning).

## Setup Instructions

### Prerequisites
- Python 3.9+
- Docker & Docker Compose

### Commands
1.  **Setup Environment & Qdrant**:
    ```bash
    make setup
    ```
2.  **Ingest Data** (Synthetic):
    ```bash
    make ingest
    ```
3.  **Run API**:
    ```bash
    make run-api
    ```
4.  **Run Demo CLI**:
    ```bash
    make test-demo
    ```
