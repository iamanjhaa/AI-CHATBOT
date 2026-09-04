import os
import traceback

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIProblemResolutionService
from app.services.classifier import build_mock_response
from app.services.helpline_registry import (
    attach_relevant_helplines,
    build_helpline_directory_response,
    is_helpline_directory_request,
)


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, response_model_exclude_none=True)
def chat(request: ChatRequest):
    problem = request.problem.strip()

    if not problem:
        raise HTTPException(status_code=400, detail="Problem text cannot be empty.")

    if is_helpline_directory_request(problem):
        return build_helpline_directory_response(problem)

    if os.getenv("OPENAI_API_KEY"):
        try:
            response = AIProblemResolutionService().generate_response(problem)
            return attach_relevant_helplines(response, problem)
        except Exception as exc:
            print(f"AI service failed; falling back to keyword classifier: {exc}")
            traceback.print_exc()
            pass

    return attach_relevant_helplines(build_mock_response(problem), problem)
