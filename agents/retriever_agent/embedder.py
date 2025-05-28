# agents/retriever_agent/embedder.py

import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import time
from .chunker import chunk_text


# Load root .env
from pathlib import Path
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Load environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "stock-insights")

# Initialize embedding model
embedder_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Pinecone with new SDK
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create or connect to index
try:
    # Check if index exists
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    
    if INDEX_NAME not in existing_indexes:
        # Create index with new SDK syntax
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,  # all-MiniLM-L6-v2 produces 384-dimensional vectors
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        
        # Wait for index to be ready
        while not pc.describe_index(INDEX_NAME).status['ready']:
            time.sleep(1)
            
    # Connect to index
    index = pc.Index(INDEX_NAME)
    
except Exception as e:
    print(f"Error initializing Pinecone: {e}")
    raise

def store_embedding(doc_id: str, text: str):
    """Store text embedding in Pinecone, split into chunks"""
    try:
        # Split into chunks
        chunks = chunk_text(text)

        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = embedder_model.encode(chunk).tolist()
            vectors.append({
                "id": f"{doc_id}_{i}",
                "values": embedding,
                "metadata": {"text": chunk}
            })

        # Upsert all chunks to Pinecone
        index.upsert(vectors=vectors)

        return {"status": "success", "chunks_stored": len(chunks)}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def query_embedding(query_text: str, top_k: int = 5):
    """Search for similar documents based on query text"""
    try:
        # Generate query embedding
        query_embedding = embedder_model.encode(query_text).tolist()
        
        # Search in Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        matches = []
        for match in results['matches']:
            doc_id = match['id'].split('_')[0]  # remove chunk suffix
            matches.append({
                "doc_id": doc_id,
                "chunk_id": match['id'],
                "score": match['score'],
                "text": match['metadata'].get('text', '')
            })

        
        return {"status": "success", "matches": matches}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}