import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional

class QdrantHandler:
    def __init__(self, host="localhost", port=6333):
        self.client = QdrantClient(host=host, port=port)
        
        # Specialized Collections
        self.COL_FACTS = "medical_facts"
        self.COL_MISINFO = "medical_misinfo" # For debunking
        self.COL_IMAGES = "medical_images"
        self.COL_MEMORY = "user_memory"
        
        # Dimensions
        self.TEXT_DIM = 384
        self.IMAGE_DIM = 512

    def init_collections(self):
        self._create_collection_if_not_exists(self.COL_FACTS, self.TEXT_DIM)
        self._create_collection_if_not_exists(self.COL_MISINFO, self.TEXT_DIM)
        self._create_collection_if_not_exists(self.COL_IMAGES, self.IMAGE_DIM)
        self._create_collection_if_not_exists(self.COL_MEMORY, self.TEXT_DIM)

    def _create_collection_if_not_exists(self, name: str, vector_size: int):
        if not self.client.collection_exists(name):
            self.client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
            )
            print(f"Created collection: {name}")

    def upsert_points(self, collection_name: str, points: List[models.PointStruct]):
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    def search(self, collection_name: str, query_vector: List[float], top_k=5, filters: Optional[Dict] = None) -> List[models.ScoredPoint]:
        query_filter = None
        if filters:
            conditions = []
            for key, val in filters.items():
                if val is not None:
                     conditions.append(models.FieldCondition(key=key, match=models.MatchValue(value=val)))
            if conditions:
                query_filter = models.Filter(must=conditions)

        # Use query_points instead of search (which is missing in this client version/build)
        response = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k
        )
        # response is a QueryResponse, which should have a 'points' attribute
        # If response is just a list (in some versions), we handle that too
        if hasattr(response, 'points'):
            return response.points
        return response

    def delete_point(self, collection_name: str, point_id: str):
        self.client.delete(
            collection_name=collection_name,
            points_selector=models.PointIdsList(points=[point_id])
        )

    def update_payload(self, collection_name: str, payload: Dict[str, Any], point_id: str):
        self.client.set_payload(
            collection_name=collection_name,
            payload=payload,
            points=[point_id]
        )

