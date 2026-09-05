import unittest
import json
from unittest.mock import patch

from app.routes.chat import chat
from app.schemas.chat import ChatRequest, ChatResponse, ProblemUnderstanding, SeverityLevel
from app.services.openrouter_service import (
    OpenRouterService,
    OpenRouterServiceError,
    build_openrouter_unavailable_response,
)
from app.services.classifier import build_mock_response, classify_severity
from app.services.openrouter_service import OpenRouterService


class ChatFallbackTests(unittest.TestCase):
    def test_chat_request_language_defaults_to_english(self):
        request = ChatRequest(problem="hii")
        self.assertEqual(request.language, "en")

    def test_selected_language_is_passed_to_openrouter(self):
        openrouter_response = ChatResponse(
            problem="Explain blockchain in simple words",
            understanding=ProblemUnderstanding(
                summary="ब्लॉकचेन की सरल व्याख्या।",
                category="openrouter_answer",
                user_intent="INFORMATION",
            ),
            severity=SeverityLevel.LOW,
            can_solve_myself=True,
        )

        with patch(
            "app.routes.chat.OpenRouterService.generate_response",
            return_value=openrouter_response,
        ) as generate_response:
            chat(
                ChatRequest(
                    problem="Explain blockchain in simple words",
                    language="hi",
                )
            )

        generate_response.assert_called_once_with(
            "Explain blockchain in simple words",
            language="hi",
        )

    def test_openrouter_prompt_contains_selected_language(self):
        provider_json = {
            "problem": "hii",
            "understanding": {"summary": "नमस्ते का उत्तर"},
            "severity": "LOW",
            "can_solve_myself": True,
        }
        raw_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(provider_json, ensure_ascii=False),
                    }
                }
            ]
        }
        service = OpenRouterService(api_key="test-key", model="minimax/minimax-m3:free")

        with patch.object(service, "_send_request", return_value=raw_response) as send_request:
            service.generate_response("hii", language="hi")

        payload = send_request.call_args.args[0]
        self.assertIn("Respond entirely in Hindi", payload["messages"][0]["content"])
        self.assertIn("Respond entirely in Hindi", payload["messages"][1]["content"])

    def test_hindi_openrouter_response_retries_when_first_response_is_english(self):
        english_response = {
            "choices": [{"message": {"content": json.dumps({
                "problem": "hiii",
                "understanding": {"summary": "The user sent a greeting."},
                "severity": "LOW",
                "can_solve_myself": True,
            })}}]
        }
        hindi_response = {
            "choices": [{"message": {"content": json.dumps({
                "problem": "hiii",
                "understanding": {"summary": "उपयोगकर्ता ने अभिवादन किया है।"},
                "severity": "LOW",
                "can_solve_myself": True,
            }, ensure_ascii=False)}}]
        }
        service = OpenRouterService(api_key="test-key", model="minimax/minimax-m3:free")

        with patch.object(
            service,
            "_send_request",
            side_effect=[english_response, hindi_response],
        ) as send_request:
            response = service.generate_response("hiii", language="hi")

        self.assertEqual(response.understanding.summary, "उपयोगकर्ता ने अभिवादन किया है।")
        self.assertEqual(send_request.call_count, 2)

    def test_unavailable_response_uses_selected_hindi_language(self):
        response = build_openrouter_unavailable_response("hiii", language="hi")
        self.assertIn("पूर्वनिर्धारित", response.understanding.summary)
        self.assertIn("कृपया", response.clarification_question)

    def test_openrouter_response_type_normalization(self):
        response = OpenRouterService._normalize_response_data(
            {
                "problem": "Explain blockchain",
                "understanding": {"summary": "A simple explanation."},
                "severity": "LOW",
                "can_solve_myself": True,
                "solution_info": {"estimated_cost": 0},
                "safety_guidance": {
                    "when_to_stop": [],
                    "precautions": "Use this only for informational purposes.",
                },
                "prevention": "Review the topic further if needed.",
            }
        )

        self.assertEqual(response["solution_info"]["estimated_cost"], "0")
        self.assertEqual(response["safety_guidance"]["when_to_stop"], "")
        self.assertEqual(
            response["safety_guidance"]["precautions"],
            ["Use this only for informational purposes."],
        )
        self.assertEqual(response["prevention"], ["Review the topic further if needed."])

    def test_unmatched_classifier_result_is_unknown(self):
        self.assertIsNone(classify_severity("hii"))
        self.assertIsNone(build_mock_response("hii"))

    def test_known_question_uses_existing_response_without_openrouter(self):
        with patch("app.routes.chat.OpenRouterService.generate_response") as generate_response:
            response = chat(ChatRequest(problem="Mere AC se paani leak ho raha hai."))

        generate_response.assert_not_called()
        self.assertEqual(response.understanding.category, "ac_water_leakage")
        self.assertEqual(response.severity, SeverityLevel.LOW)

    def test_hindi_known_question_still_skips_openrouter(self):
        with patch("app.routes.chat.OpenRouterService.generate_response") as generate_response:
            response = chat(
                ChatRequest(
                    problem="Mere AC se paani leak ho raha hai.",
                    language="hi",
                )
            )

        generate_response.assert_not_called()
        self.assertEqual(response.understanding.category, "ac_water_leakage")

    def test_requested_unknown_messages_use_openrouter(self):
        unknown_messages = [
            "hii",
            "Explain blockchain in simple words",
            "My phone is getting heatup",
            "There is server line brust in my neighborhood",
            "earthquick occur",
        ]

        for message in unknown_messages:
            openrouter_response = ChatResponse(
                problem=message,
                understanding=ProblemUnderstanding(
                    summary="OpenRouter handled the unmatched message.",
                    category="openrouter_answer",
                    user_intent="INFORMATION",
                ),
                severity=SeverityLevel.LOW,
                can_solve_myself=True,
            )
            with self.subTest(message=message), patch(
                "app.routes.chat.OpenRouterService.generate_response",
                return_value=openrouter_response,
            ) as generate_response:
                response = chat(ChatRequest(problem=message))

            generate_response.assert_called_once_with(message, language="en")
            self.assertEqual(response.understanding.category, "openrouter_answer")

    def test_casual_message_uses_openrouter_instead_of_generic_household_response(self):
        openrouter_response = ChatResponse(
            problem="hii",
            understanding=ProblemUnderstanding(
                summary="The user sent a casual greeting.",
                category="casual_conversation",
                user_intent="INFORMATION",
            ),
            severity=SeverityLevel.LOW,
            can_solve_myself=True,
        )

        with patch(
            "app.routes.chat.OpenRouterService.generate_response",
            return_value=openrouter_response,
        ) as generate_response:
            response = chat(ChatRequest(problem="hii"))

        generate_response.assert_called_once_with("hii", language="en")
        self.assertEqual(response.understanding.category, "casual_conversation")
        self.assertNotIn("basic_household_or_local_issue", response.understanding.category)

    def test_unknown_question_uses_openrouter_response(self):
        openrouter_response = ChatResponse(
            problem="Suggest a name for my community project",
            understanding=ProblemUnderstanding(
                summary="The user wants help naming a community project.",
                category="creative_naming",
                user_intent="Get practical guidance",
            ),
            severity=SeverityLevel.LOW,
            can_solve_myself=True,
        )

        with patch(
            "app.routes.chat.OpenRouterService.generate_response",
            return_value=openrouter_response,
        ) as generate_response:
            response = chat(ChatRequest(problem="Suggest a name for my community project"))

        generate_response.assert_called_once_with(
            "Suggest a name for my community project",
            language="en",
        )
        self.assertEqual(response.understanding.category, "creative_naming")

    def test_openrouter_failure_returns_safe_compatible_response(self):
        with patch(
            "app.routes.chat.OpenRouterService.generate_response",
            side_effect=OpenRouterServiceError("provider unavailable"),
        ):
            response = chat(ChatRequest(problem="How should I plan an unusual event?"))

        self.assertEqual(response.severity, SeverityLevel.MEDIUM)
        self.assertTrue(response.clarification_needed)
        self.assertFalse(response.can_solve_myself)


if __name__ == "__main__":
    unittest.main()