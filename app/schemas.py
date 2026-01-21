from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

# --- Filter Models ---
class SearchFilters(BaseModel):
    topics: Optional[List[str]] = None
    source: Optional[str] = None
    content_type: Optional[Literal["text", "image", "all"]] = "all"
    min_date: Optional[str] = None

# --- Ingestion Models ---
class TextDoc(BaseModel):
    doc_id: str
    title: str
    body: str
    source: str
    date: str
    topic: str
    url: Optional[str] = None

class ImageDoc(BaseModel):
    img_id: str
    caption: str
    source: str
    date: str
    topic: str
    file_path: str

class IngestTextRequest(BaseModel):
    documents: List[TextDoc]

class IngestImageRequest(BaseModel):
    images: List[ImageDoc]

# --- Search & Agent Models ---
class SearchRequest(BaseModel):
    query: str
    type: Literal["text", "image", "all"] = "all"
    top_k: int = 5
    filters: Optional[SearchFilters] = None

class SearchResultItem(BaseModel):
    id: str
    score: float
    content: str
    metadata: Dict[str, Any]
    type: Literal["fact", "misinformation", "image"] # Explicit classification
    source_collection: str


class SearchResponse(BaseModel):
    results: List[SearchResultItem]

class AgentQueryRequest(BaseModel):
    query: str
    user_id: str
    session_id: str

class AgentResponse(BaseModel):
    final_answer: str
    verdict: Literal["True", "False", "Misleading", "Insufficient Evidence"]
    reasoning_trace: str
    evidence: List[SearchResultItem]
    recommendations: List[str]
    memory_actions: List[str]

# --- Memory Models ---
class MemoryItem(BaseModel):
    user_id: str
    session_id: str
    memory_type: Literal["preference", "prior_claim", "summary", "history"]
    timestamp: str
    raw_text: str
    decay_weight: float = 1.0
    access_count: int = 1
    last_accessed: float = 0.0 # Timestamp

class MemoryUpdateRequest(BaseModel):
    item: MemoryItem
    action: Literal["upsert", "delete"]
