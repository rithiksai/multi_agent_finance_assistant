# agents/retriever_agent/retriever_service.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from embedder import store_embedding,query_embedding

app = FastAPI(title="Retriever Agent", description="Stores scraped documents as embeddings in Pinecone")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StoreRequest(BaseModel):
    doc_id: str
    text: str

class DocumentQuery(BaseModel):
    query: str

@app.post("/store")
async def store(request: StoreRequest):
    try:
        result = store_embedding(request.doc_id, request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/query")
async def query_docs(payload: DocumentQuery):
    try:
        results = query_embedding(payload.query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
