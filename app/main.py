from dotenv import load_dotenv
load_dotenv() # Load env vars from .env BEFORE other imports

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from app.schemas import (
    IngestTextRequest, IngestImageRequest, SearchRequest, SearchResponse,
    AgentQueryRequest, AgentResponse, MemoryUpdateRequest, SearchResultItem
)
from app.agent import MisinformationAgent
from app.qdrant_client_wrapper import QdrantHandler
from qdrant_client.http import models
import uuid
import os

app = FastAPI(title="Multimodal Misinformation Assistant")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('app/static/index.html')

agent = MisinformationAgent()
# Re-init db handler for direct access if needed
db = QdrantHandler() 

@app.post("/ingest/text")
async def ingest_text(request: IngestTextRequest):
    points = []
    embedder = agent.embedder
    for doc in request.documents:
        vector = embedder.encode_text(doc.body)
        points.append(models.PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.doc_id)),
            vector=vector,
            payload=doc.dict()
        ))

    db.upsert_points(db.COL_FACTS, points)
    return {"status": "success", "count": len(points)}

@app.post("/ingest/images")
async def ingest_images(request: IngestImageRequest):
    points = []
    embedder = agent.embedder
    for img in request.images:
        # Note: In a real API, we might fetch image from URL or path. 
        # Here we assume file_path is local and valid as per simplified requirements.
        try:
            vector = embedder.encode_image(img.file_path)
            points.append(models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, img.img_id)),
                vector=vector,
                payload=img.dict()
            ))
        except Exception as e:
            print(f"Failed to process image {img.file_path}: {e}")
            continue
            
    db.upsert_points(db.COL_IMAGES, points)
    return {"status": "success", "count": len(points)}

@app.get("/search", response_model=SearchResponse)
async def search(q: str, type: str = "all", top_k: int = 5):
    # Direct search endpoint
    results = []
    
    # Text Search matches
    # Text Search matches (Searching FACTS only for direct search endpoint)
    if type in ["text", "all"]:
        q_vec = agent.embedder.encode_text(q)
        hits = db.search(db.COL_FACTS, q_vec, top_k=top_k)
        for h in hits:
            results.append(SearchResultItem(
                id=str(h.id),
                score=h.score,
                content=h.payload.get('body', ''),
                metadata=h.payload,
                type="fact",
                source_collection="medical_facts"
            ))

    # Image Search matches
    if type in ["image", "all"]:
        q_vec = agent.embedder.encode_text_for_image_search(q)
        hits = db.search(db.COL_IMAGES, q_vec, top_k=top_k)
        for h in hits:
            results.append(SearchResultItem(
                id=str(h.id),
                score=h.score,
                content=h.payload.get('caption', ''),
                metadata=h.payload,
                type="image",
                source_collection="medical_images"
            ))
            
    # Sort composite results by score
    results.sort(key=lambda x: x.score, reverse=True)
    return SearchResponse(results=results[:top_k])

@app.post("/agent/query", response_model=AgentResponse)
async def agent_query(request: AgentQueryRequest):
    return agent.process_query(request)

@app.get("/memory")
async def get_memory(user_id: str, query: str):
    return agent.memory.get_context(user_id, query)

@app.post("/memory/update")
async def update_memory(request: MemoryUpdateRequest):
    # Manual memory override
    if request.action == "upsert":
        agent.memory.add_memory(
            request.item.user_id, 
            request.item.session_id, 
            request.item.raw_text, 
            request.item.memory_type
        )
    return {"status": "updated"}
