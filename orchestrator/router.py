# router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from orchestrator.agent_controller import process_query

router = APIRouter()

class UserQuery(BaseModel):
    query: str

@router.post("/ask")
async def ask_agent(user_input: UserQuery):
    try:
        print("Orchestrator got:", user_input.query)
        #return {"response": data_from_agents}
        response = await process_query(user_input.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
