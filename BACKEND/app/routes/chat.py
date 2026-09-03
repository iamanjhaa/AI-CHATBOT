import os

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIProblemResolutionService
from app.services.classifier import build_mock_response


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, response_model_exclude_none=True)
def chat(request: ChatRequest):
    problem = request.problem.strip()

    if not problem:
        raise HTTPException(status_code=400, detail="Problem text cannot be empty.")

    if os.getenv("OPENAI_API_KEY"):
        try:
            return AIProblemResolutionService().generate_response(problem)
        except Exception:
            pass

    return build_mock_response(problem)
