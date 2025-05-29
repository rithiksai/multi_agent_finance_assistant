# orchestrator_service.py
from fastapi import FastAPI
from router import router 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Orchestrator Agent")

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)