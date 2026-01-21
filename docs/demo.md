# Demo Guide

This demo shows the Multimodal Misinformation Assistant in action.

## 1. Setup

Ensure you have run:
```bash
make setup
make ingest
```
This populates the local Qdrant with synthetic claims (flat earth, 5G, etc.) and synthetic placeholder images.

## 2. CLI Demo

We have provided a CLI script to simulate the Agent API interaction without needing `curl`.

Run:
```bash
make test-demo
```
(Or `python3 -m project.scripts.demo_cli`)

### Expected Output Flow

1.  **Query 1**: "Is the earth flat?"
    *   **Intent**: Check Claim.
    *   **Retrieval**: Fetches "The earth is flat..." (Source: Social Media, Label: fake) and "Global temperatures..." (irrelevant but maybe top-k).
    *   **Response**: "The claim appears to be **fake**. Found evidence..."
    *   **Memory**: Stores this interaction.

2.  **Query 2**: "What did I just ask you regarding the planet?"
    *   **Retrieval**: Fetches memory of Query 1.
    *   **Response**: "Based on your query... (Context from previous sessions: User asked: 'Is the earth flat?')"

3.  **Multimodal Query**: "Show me evidence about 5G viruses."
    *   **Retrieval**: Text: "5G towers cause viruses...", Image: [Image with caption about 5G/Health].
    *   **Response**: "Found evidence in text... Found evidence in image..."

## 3. API Endpoints

You can also interact via Swagger UI:
1.  `make run-api`
2.  Go to `http://localhost:8000/docs`

### Key Endpoints
- `POST /agent/query`: Main entry point.
- `GET /search`: Debug search results.
- `POST /ingest`: Add more data on the fly.
