# orchestrator_service.py
from fastapi import FastAPI
from router import router 

app = FastAPI(title="Orchestrator Agent")

app.include_router(router.router)
