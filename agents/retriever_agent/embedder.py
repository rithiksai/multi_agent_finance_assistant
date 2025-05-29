import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pathlib import Path
import time

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "stock-insights")

# Initialize embedding model
embedder_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create or connect to index
try:
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        while not pc.describe_index(INDEX_NAME).status['ready']:
            time.sleep(1)

    index = pc.Index(INDEX_NAME)

except Exception as e:
    print(f"Error initializing Pinecone: {e}")
    raise

def store_embedding(doc_id: str, text: str):
    """Embed and store a single chunk of text"""
    try:
        embedding = embedder_model.encode(text).tolist()
        index.upsert(vectors=[
            {
                "id": doc_id,
                "values": embedding,
                "metadata": {"text": text}
            }
        ])
        return {"status": "success", "chunks_stored": 1}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def query_embedding(query_text: str, top_k: int = 5):
    """
    Search for similar documents based on query text.
    This version assumes chunks were already passed with clean doc_ids and no further subchunking (i.e., no _0, _1).
    """
    try:
        # Generate query embedding
        query_embedding = embedder_model.encode(query_text).tolist()

        # Query Pinecone index
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Format results
        matches = []
        for match in results['matches']:
            matches.append({
                "doc_id": match['id'],  # doc_id is same as chunk ID
                "score": match['score'],
                "text": match['metadata'].get('text', '')
            })

        return {"status": "success", "matches": matches}

    except Exception as e:
        return {"status": "error", "message": str(e)}
