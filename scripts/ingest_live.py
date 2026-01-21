
import feedparser
import uuid
import time
from app.qdrant_client_wrapper import QdrantHandler
from app.embeddings import EmbeddingModel
from qdrant_client.http import models

# RSS Feeds for Real-Time Medical Data
FEEDS = [
    "https://pubmed.ncbi.nlm.nih.gov/rss/search/1/pmc_essential_collection.xml", # PubMed Essential
    "https://tools.cdc.gov/api/v2/resources/media/132608.rss", # CDC Outbreaks
    "https://www.who.int/feeds/entity/news/en/rss.xml" # WHO News
]

def ingest_live_feeds():
    print("🚀 Starting Live BioMedical Ingestion...")
    
    # Initialize Core Systems
    db = QdrantHandler()
    embedder = EmbeddingModel()
    db.init_collections() # Ensure collections exist
    
    total_ingested = 0
    
    for feed_url in FEEDS:
        print(f"📡 Fetching: {feed_url}...")
        try:
            feed = feedparser.parse(feed_url)
            print(f"   Found {len(feed.entries)} entries.")
            
            points = []
            for entry in feed.entries:
                # Extract Data
                title = entry.get('title', 'No Title')
                summary = entry.get('summary', '') or entry.get('description', '')
                link = entry.get('link', '')
                published = entry.get('published', time.strftime("%Y-%m-%d"))
                
                # Create Body Text for Embedding
                # We combine Title + Summary for better semantic search context
                text_content = f"{title}. {summary}"
                
                # Check for duplicates (Optional simple check or just upsert)
                # We use uuid5 based on link to ensure idempotency (deduplication)
                doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, link))
                
                # Create Vector
                vector = embedder.encode_text(text_content)
                
                # Create Payload
                payload = {
                    "doc_id": doc_id,
                    "title": title,
                    "body": summary[:1000], # Limit payload size
                    "source": f"Live Feed ({feed.feed.get('title', 'Medical RSS')})",
                    "date": published,
                    "topic": "live_medical_news",
                    "content_type": "text",
                    "url": link,
                    "veracity": "fact" # Assume trusted sources like NIH/WHO are facts
                }
                
                points.append(models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=payload
                ))
            
            # Batch Upsert
            if points:
                db.upsert_points(db.COL_FACTS, points)
                print(f"   ✅ Ingested {len(points)} articles from {feed_url}")
                total_ingested += len(points)
                
        except Exception as e:
            print(f"   ❌ Failed to process feed {feed_url}: {e}")

    print(f"\n🎉 Live Ingestion Complete! Total new records: {total_ingested}")

if __name__ == "__main__":
    ingest_live_feeds()
