
import os
import shutil
import uuid
from app.embeddings import EmbeddingModel
from app.qdrant_client_wrapper import QdrantHandler
from qdrant_client.http import models

# Source Images (uploaded by user)
SOURCE_IMAGES = [
    "/Users/goturivenkatjyothireddy/.gemini/antigravity/brain/2d82aad5-8cd4-4992-92e7-27c50fb3b07b/uploaded_image_0_1768927881779.png",
    "/Users/goturivenkatjyothireddy/.gemini/antigravity/brain/2d82aad5-8cd4-4992-92e7-27c50fb3b07b/uploaded_image_1_1768927881779.png"
]

DEST_DIR = "project/data/medical_images"
os.makedirs(DEST_DIR, exist_ok=True)

def ingest_manual_images():
    print("🚀 Starting Manual Image Ingestion (True Vision Search)...")
    
    db = QdrantHandler()
    embedder = EmbeddingModel()
    db.init_collections()
    
    points = []
    
    for i, src_path in enumerate(SOURCE_IMAGES):
        if not os.path.exists(src_path):
            print(f"❌ Source image not found: {src_path}")
            continue
            
        # Copy to project data
        filename = f"real_upload_{i}.png"
        dest_path = os.path.join(DEST_DIR, filename)
        shutil.copy(src_path, dest_path)
        print(f"📸 Copied image to {dest_path}")
        
        # Encode Image (Pixel-Level CLIP Embedding)
        try:
            vector = embedder.encode_image(dest_path)
            
            # Create Payload
            payload = {
                "img_id": f"real_upload_{i}",
                "caption": "High-Resolution Anatomical Scan (Trusted Source)",
                "source": "User Uploaded Reference",
                "date": "2025-06-01",
                "topic": "anatomy",
                "content_type": "image",
                "file_path": os.path.abspath(dest_path),
                "veracity": "fact"
            }
            
            points.append(models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, src_path)),
                vector=vector,
                payload=payload
            ))
            print(f"✅ Encoded image {i} successfully.")
            
        except Exception as e:
            print(f"❌ Failed to encode {src_path}: {e}")

    if points:
        db.upsert_points(db.COL_IMAGES, points)
        print(f"🎉 Successfully ingested {len(points)} real images into Qdrant.")

if __name__ == "__main__":
    ingest_manual_images()
