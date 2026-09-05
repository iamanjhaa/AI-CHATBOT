import logging

from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.classifier import build_contextual_fallback_response
from app.services.helpline_registry import (
    attach_relevant_helplines,
    build_helpline_directory_response,
    is_helpline_directory_request,
)
from app.services.openrouter_service import (
    OpenRouterService,
    build_openrouter_unavailable_response,
)


router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ChatResponse, response_model_exclude_none=True)
def chat(request: ChatRequest):
    problem = request.problem.strip()
    language = request.language

    if not problem:
        raise HTTPException(status_code=400, detail="Problem text cannot be empty.")

    logger.info("[CHAT] input=%s language=%s", problem[:200], language)

    if is_helpline_directory_request(problem):
        logger.info("[CHAT] predefined_match=true classification=helpline_directory using_openrouter=false")
        return build_helpline_directory_response(problem)

    existing_response = build_contextual_fallback_response(problem)
    if existing_response is not None:
        category = existing_response.understanding.category or "known_intent"
        logger.info(
            "[CHAT] predefined_match=true classification=%s using_openrouter=false",
            category,
        )
        return attach_relevant_helplines(existing_response, problem)

    openrouter = OpenRouterService()
    logger.info(
        "[CHAT] predefined_match=false classification=NO_MATCH openrouter_configured=%s using_openrouter=true model=%s",
        openrouter.configured,
        openrouter.model,
    )
    try:
        response = openrouter.generate_response(problem, language=language)
        logger.info("[CHAT] openrouter_status=success")
        return attach_relevant_helplines(response, problem)
    except Exception as exc:
        logger.warning(
            "[CHAT] openrouter_status=unavailable error_type=%s status_code=%s detail=%s",
            type(exc).__name__,
            getattr(exc, "status_code", None),
            str(exc),
        )
        return build_openrouter_unavailable_response(problem, language=language)
