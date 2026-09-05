import json
import logging
import os
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from app.schemas.chat import (
    ChatResponse,
    ProblemUnderstanding,
    SafetyGuidance,
    SeverityLevel,
    SolutionInfo,
)


OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")


class OpenRouterServiceError(Exception):
    """Raised when OpenRouter cannot return a usable chatbot response."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class OpenRouterService:
    def __init__(self, api_key=None, model=None, timeout_seconds=30):
        self.api_key = (api_key or os.getenv("OPENROUTER_API_KEY", "")).strip()
        self.model = (model or os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)).strip()
        self.timeout_seconds = timeout_seconds

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def generate_response(self, problem: str, language: str = "en") -> ChatResponse:
        if not self.api_key:
            raise OpenRouterServiceError("OpenRouter is not configured.")

        language = "hi" if language == "hi" else "en"
        response = self._request_response(problem, language)
        if language == "hi" and not self._contains_devanagari(response):
            response = self._request_response(
                problem,
                language,
                strict_retry=True,
            )
        return response

    def _request_response(self, problem: str, language: str, strict_retry: bool = False) -> ChatResponse:
        language_name = "Hindi" if language == "hi" else "English"
        language_instruction = (
            f"Respond entirely in {language_name} because the user selected {language_name}. "
            "Every user-visible summary, question, step, precaution, escalation, prevention, time, and cost must be in "
            f"{language_name}. Do not use English explanatory sentences."
        )
        if strict_retry:
            language_instruction += " Your previous output violated the language requirement. Rewrite every field now."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{language_instruction}"},
                {"role": "user", "content": f"{language_instruction}\n\nUser message:\n{problem.strip()}"},
            ],
            "temperature": 0.2,
        }
        raw_response = self._send_request(payload)
        answer = self._extract_answer(raw_response)

        try:
            response_data = json.loads(self._strip_code_fences(answer))
        except json.JSONDecodeError:
            return self._text_response(problem, answer, language)

        if not isinstance(response_data, dict):
            raise OpenRouterServiceError("OpenRouter returned an invalid response object.")

        try:
            return ChatResponse(**self._normalize_response_data(response_data))
        except Exception as exc:
            raise OpenRouterServiceError("OpenRouter response did not match the chatbot response schema.") from exc

    @staticmethod
    def _contains_devanagari(response: ChatResponse) -> bool:
        text = json.dumps(response.model_dump(), ensure_ascii=False)
        return any("\u0900" <= character <= "\u097f" for character in text)

    @classmethod
    def _normalize_response_data(cls, response_data: dict) -> dict:
        normalized = dict(response_data)
        normalized["problem"] = cls._text_value(normalized.get("problem", ""))

        understanding = dict(normalized.get("understanding") or {})
        for field in ("summary", "category", "user_intent"):
            if field in understanding and understanding[field] is not None:
                understanding[field] = cls._text_value(understanding[field])
        normalized["understanding"] = understanding

        solution_info = normalized.get("solution_info")
        if isinstance(solution_info, dict):
            solution_info = dict(solution_info)
            for field in ("estimated_time", "estimated_cost"):
                if field in solution_info and solution_info[field] is not None:
                    solution_info[field] = cls._text_value(solution_info[field])
            for field in ("steps", "tools_materials"):
                if field in solution_info and solution_info[field] is not None:
                    solution_info[field] = cls._list_value(solution_info[field])
            normalized["solution_info"] = solution_info

        safety_guidance = normalized.get("safety_guidance")
        if isinstance(safety_guidance, dict):
            safety_guidance = dict(safety_guidance)
            if safety_guidance.get("when_to_stop") is not None:
                safety_guidance["when_to_stop"] = cls._text_value(safety_guidance["when_to_stop"])
            if "precautions" in safety_guidance and safety_guidance["precautions"] is not None:
                safety_guidance["precautions"] = cls._list_value(safety_guidance["precautions"])
            normalized["safety_guidance"] = safety_guidance

        escalation = normalized.get("escalation")
        if isinstance(escalation, dict):
            escalation = dict(escalation)
            for field in ("contact", "reason"):
                if field in escalation and escalation[field] is not None:
                    escalation[field] = cls._text_value(escalation[field])
            normalized["escalation"] = escalation

        if normalized.get("prevention") is not None:
            normalized["prevention"] = cls._list_value(normalized["prevention"])

        return normalized

    @staticmethod
    def _text_value(value) -> str:
        if isinstance(value, list):
            return "; ".join(str(item) for item in value)
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    @classmethod
    def _list_value(cls, value) -> list[str]:
        if isinstance(value, list):
            return [cls._text_value(item) for item in value]
        return [cls._text_value(value)]

    def _send_request(self, payload: dict) -> dict:
        request = urllib.request.Request(
            OPENROUTER_CHAT_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://127.0.0.1:5500",
                "X-Title": "SAHAYAK",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                logger.info("[CHAT] openrouter_status=%s model=%s", response.status, self.model)
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            safe_detail = " ".join(detail.split())[:300]
            logger.error(
                "[CHAT] openrouter_status=%s error=%s",
                exc.code,
                safe_detail or "provider returned an HTTP error",
            )
            raise OpenRouterServiceError(
                "OpenRouter request failed.",
                status_code=exc.code,
            ) from exc
        except urllib.error.URLError as exc:
            logger.error("[CHAT] openrouter_status=network_error reason=%s", exc.reason)
            raise OpenRouterServiceError("OpenRouter network request failed.") from exc
        except TimeoutError as exc:
            logger.error("[CHAT] openrouter_status=timeout")
            raise OpenRouterServiceError("OpenRouter request timed out.") from exc
        except json.JSONDecodeError as exc:
            logger.error("[CHAT] openrouter_status=invalid_json")
            raise OpenRouterServiceError("OpenRouter returned invalid JSON.") from exc

    def _extract_answer(self, raw_response: dict) -> str:
        try:
            content = raw_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenRouterServiceError("OpenRouter response did not contain an answer.") from exc

        if isinstance(content, str) and content.strip():
            return content.strip()

        if isinstance(content, list):
            text = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            ).strip()
            if text:
                return text

        raise OpenRouterServiceError("OpenRouter response did not contain usable text.")

    @staticmethod
    def _strip_code_fences(answer: str) -> str:
        cleaned = answer.strip()
        if cleaned.startswith("```") and cleaned.endswith("```"):
            cleaned = cleaned[3:-3].strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        return cleaned

    @staticmethod
    def _text_response(problem: str, answer: str, language: str) -> ChatResponse:
        return ChatResponse(
            problem=problem,
            understanding=ProblemUnderstanding(
                summary=(
                    "OpenRouter ने समस्या के लिए मार्गदर्शन दिया है।"
                    if language == "hi"
                    else "OpenRouter provided guidance for the reported problem."
                ),
                category="openrouter_fallback",
                user_intent="व्यावहारिक मार्गदर्शन प्राप्त करें" if language == "hi" else "Get practical guidance",
            ),
            severity=SeverityLevel.LOW,
            can_solve_myself=False,
            solution_info=SolutionInfo(steps=[answer]),
            safety_guidance=SafetyGuidance(
                precautions=["Stop and contact a qualified professional if the situation involves immediate danger."]
            ),
        )


def build_openrouter_unavailable_response(problem: str, language: str = "en") -> ChatResponse:
    if language == "hi":
        return ChatResponse(
            problem=problem,
            understanding=ProblemUnderstanding(
                summary="इस संदेश के लिए कोई पूर्वनिर्धारित उत्तर नहीं मिला और एआई सेवा अभी उपलब्ध नहीं है।",
                category="fallback_unavailable",
                user_intent="स्पष्टीकरण आवश्यक है",
            ),
            severity=SeverityLevel.MEDIUM,
            clarification_needed=True,
            clarification_question="कृपया बताएं कि समस्या कहां है और अभी कौन से संकेत दिखाई दे रहे हैं।",
            can_solve_myself=False,
            solution_info=SolutionInfo(
                steps=["कृपया बताएं कि समस्या कहां है और अभी कौन से संकेत दिखाई दे रहे हैं।"]
            ),
            safety_guidance=SafetyGuidance(
                precautions=["गैस, बिजली, आग, चोट या ढांचे से जुड़ी मरम्मत खुद न करें।"]
            ),
        )

    return ChatResponse(
        problem=problem,
        understanding=ProblemUnderstanding(
            summary="OpenRouter fallback is unavailable right now; no predefined answer matched this message.",
            category="fallback_unavailable",
            user_intent="Clarification needed",
        ),
        severity=SeverityLevel.MEDIUM,
        clarification_needed=True,
        clarification_question="Please describe where the problem is and what signs you can see right now.",
        can_solve_myself=False,
        solution_info=SolutionInfo(
            steps=["Please describe where the problem is and what signs you can see right now."]
        ),
        safety_guidance=SafetyGuidance(
            precautions=[
                "Do not attempt repairs involving gas, electricity, fire, injury, or structural damage."
            ]
        ),
    )


SYSTEM_PROMPT = """
You are the fallback AI for SAHAYAK. Answer the user's real-world household or local problem safely and concisely.
Use the same language as the user. Give situation-specific guidance, ask one clarification question when necessary,
and prioritize emergency safety for gas, fire, electricity, injury, violence, flooding, or structural danger.
Return only a JSON object with: problem, understanding {summary, category, user_intent}, severity (LOW, MEDIUM, CRITICAL),
can_solve_myself, solution_info {steps, tools_materials, estimated_time, estimated_cost}, safety_guidance {precautions, when_to_stop},
escalation {required, contact, reason}, and prevention. Omit fields that are not useful. Do not invent helpline numbers.
""".strip()