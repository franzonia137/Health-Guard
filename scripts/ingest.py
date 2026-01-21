import json
import os
import uuid
from qdrant_client.http import models
from app.embeddings import EmbeddingModel
from app.qdrant_client_wrapper import QdrantHandler

# Initialize services
db = QdrantHandler()
embedder = EmbeddingModel()

DATA_DIR = "project/data"
FACTS_FILE = os.path.join(DATA_DIR, "medical_facts.jsonl")
MISINFO_FILE = os.path.join(DATA_DIR, "medical_misinfo.jsonl")
IMG_META_FILE = os.path.join(DATA_DIR, "medical_images.jsonl")

def ingest_file(file_path, collection_name, content_field='body'):
    print(f"Ingesting into {collection_name} from {file_path}...")
    points = []
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r') as f:
        for line in f:
            doc = json.loads(line)
            # Embed based on content type (text body vs image path)
            text_content = doc.get(content_field)
            if not text_content: continue
            
            vector = embedder.encode_text(text_content)
            
            # Using doc_id or img_id as unique key
            unique_id = doc.get('doc_id') or doc.get('img_id')
            
            point = models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_id)),
                vector=vector,
                payload=doc
            )
            points.append(point)
    
    if points:
        db.upsert_points(collection_name, points)
        print(f"Upserted {len(points)} items into {collection_name}.")

def ingest_images():
    print("Ingesting Images...")
    points = []
    if not os.path.exists(IMG_META_FILE):
        print("No image metadata found.")
        return

    with open(IMG_META_FILE, 'r') as f:
        for line in f:
            meta = json.loads(line)
            path = meta['file_path']
            if os.path.exists(path):
                vector = embedder.encode_image(path)
                
                point = models.PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, meta['img_id'])),
                    vector=vector,
                    payload=meta
                )
                points.append(point)
            else:
                print(f"Warning: Image file not found {path}")
    
    if points:
        db.upsert_points(db.COL_IMAGES, points)
        print(f"Upserted {len(points)} images into {db.COL_IMAGES}.")

if __name__ == "__main__":
    db.init_collections()
    
    # Ingest Facts
    ingest_file(FACTS_FILE, db.COL_FACTS)
    
    # Ingest Misinformation (Knowledge of what is fake is as important as what is real)
    ingest_file(MISINFO_FILE, db.COL_MISINFO)
    
    # Ingest Images
    ingest_images()
