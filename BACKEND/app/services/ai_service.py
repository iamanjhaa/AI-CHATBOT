import json
import os
import urllib.error
import urllib.request
from typing import Any, Optional

from app.schemas.chat import (
    ChatResponse,
    EscalationGuidance,
    ProblemUnderstanding,
    SafetyGuidance,
    SeverityLevel,
    SolutionInfo,
    UserIntent,
)


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5-mini"


class AIServiceError(Exception):
    """Raised when the AI service cannot return a validated chatbot response."""


class AIProblemResolutionService:
    _conversation_context: list[dict[str, str]] = []

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: int = 30,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.timeout_seconds = timeout_seconds

    def generate_response(self, problem: str) -> ChatResponse:
        cleaned_problem = problem.strip()
        if not cleaned_problem:
            raise AIServiceError("Problem text cannot be empty.")
        if not self.api_key:
            raise AIServiceError("OPENAI_API_KEY environment variable is not configured.")

        payload = self._build_payload(cleaned_problem)
        raw_response = self._send_request(payload)
        response_data = self._extract_json(raw_response)

        try:
            response = ChatResponse(**response_data)
        except Exception as exc:
            raise AIServiceError("AI response did not match the chatbot response schema.") from exc

        if (
            response.severity == SeverityLevel.CRITICAL
            or getattr(response, "immediate_danger", False)
            or self._should_force_critical(
            cleaned_problem,
            response,
            )
        ):
            source_response = response
            response = self._build_critical_emergency_response(cleaned_problem, response)
            response = self._with_phase2_metadata(
                response,
                source_response,
                forced_critical=True,
            )
            self._remember_turn(cleaned_problem, response)
            return response

        response = self._normalize_non_critical_response(cleaned_problem, response)
        response = self._with_phase2_metadata(response, response)
        self._remember_turn(cleaned_problem, response)
        return response

    def _build_payload(self, problem: str) -> dict[str, Any]:
        context = self._format_context()
        user_text = problem
        if context:
            user_text = f"Recent conversation context:\n{context}\n\nCurrent user message:\n{problem}"

        return {
            "model": self.model,
            "instructions": SYSTEM_PROMPT,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": user_text,
                        }
                    ],
                }
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "problem_resolution_response",
                    "description": "Structured response for a safety-first household/local problem resolution chatbot.",
                    "schema": RESPONSE_SCHEMA,
                    "strict": False,
                }
            },
        }

    def _send_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            OPENAI_RESPONSES_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise AIServiceError(f"AI service request failed with status {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise AIServiceError("AI service request failed due to a network error.") from exc
        except json.JSONDecodeError as exc:
            raise AIServiceError("AI service returned invalid JSON.") from exc

    def _extract_json(self, raw_response: dict[str, Any]) -> dict[str, Any]:
        output_text = raw_response.get("output_text")
        if output_text:
            return self._parse_json_text(output_text)

        for output_item in raw_response.get("output", []):
            for content_item in output_item.get("content", []):
                text = content_item.get("text")
                if text:
                    return self._parse_json_text(text)

        raise AIServiceError("AI service response did not contain structured output text.")

    def _parse_json_text(self, text: str) -> dict[str, Any]:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIServiceError("AI service structured output was not valid JSON.") from exc

        if not isinstance(parsed, dict):
            raise AIServiceError("AI service structured output must be a JSON object.")

        return parsed

    def _normalize_non_critical_response(
        self,
        original_problem: str,
        response: ChatResponse,
    ) -> ChatResponse:
        solution_info = getattr(response, "solution_info", None)
        safety_guidance = getattr(response, "safety_guidance", None)
        escalation = getattr(response, "escalation", None)
        clarification_question = getattr(response, "clarification_question", None)
        if getattr(response, "clarification_needed", False):
            steps = getattr(solution_info, "steps", None) if solution_info else None
            question = clarification_question or (steps[0] if steps else None)
            clarification_question = question
            solution_info = SolutionInfo(steps=[question] if question else None)
            safety_guidance = None
            escalation = None
            return ChatResponse(
                problem=original_problem,
                understanding=response.understanding,
                user_intent=getattr(response, "user_intent", None),
                severity=response.severity,
                immediate_danger=getattr(response, "immediate_danger", None),
                clarification_needed=True,
                clarification_question=clarification_question,
                can_solve_myself=False,
                solution_info=solution_info,
                solution=[question] if question else None,
            )

        return ChatResponse(
            problem=original_problem,
            understanding=response.understanding,
            user_intent=getattr(response, "user_intent", None),
            severity=response.severity,
            immediate_danger=getattr(response, "immediate_danger", None),
            clarification_needed=getattr(response, "clarification_needed", None),
            clarification_question=clarification_question,
            can_solve_myself=response.can_solve_myself,
            solution_info=solution_info,
            safety_guidance=safety_guidance,
            escalation=escalation,
            prevention=None
            if getattr(response, "clarification_needed", False)
            else getattr(response, "prevention", None),
            solution=getattr(response, "solution", None)
            or (getattr(solution_info, "steps", None) if solution_info else None),
            required_tools=getattr(response, "required_tools", None)
            or (getattr(solution_info, "tools_materials", None) if solution_info else None),
            estimated_time=getattr(response, "estimated_time", None)
            or (getattr(solution_info, "estimated_time", None) if solution_info else None),
            estimated_cost=getattr(response, "estimated_cost", None)
            or (getattr(solution_info, "estimated_cost", None) if solution_info else None),
            safety_precautions=getattr(response, "safety_precautions", None)
            or (getattr(safety_guidance, "precautions", None) if safety_guidance else None),
            when_to_stop=getattr(response, "when_to_stop", None)
            or (getattr(safety_guidance, "when_to_stop", None) if safety_guidance else None),
            when_to_contact_authority=getattr(response, "when_to_contact_authority", None)
            or (getattr(escalation, "contact", None) if escalation else None),
        )

    def _with_phase2_metadata(
        self,
        response: ChatResponse,
        source_response: ChatResponse,
        forced_critical: bool = False,
    ) -> ChatResponse:
        user_intent = getattr(source_response, "user_intent", None)
        if forced_critical:
            user_intent = UserIntent.EMERGENCY_HELP

        immediate_danger = getattr(source_response, "immediate_danger", None)
        if forced_critical or response.severity == SeverityLevel.CRITICAL:
            immediate_danger = True

        clarification_needed = getattr(source_response, "clarification_needed", None)
        if forced_critical or response.severity == SeverityLevel.CRITICAL:
            clarification_needed = False

        return ChatResponse(
            problem=response.problem,
            understanding=response.understanding,
            user_intent=user_intent,
            severity=response.severity,
            immediate_danger=immediate_danger,
            clarification_needed=clarification_needed,
            clarification_question=None
            if forced_critical or response.severity == SeverityLevel.CRITICAL
            else getattr(source_response, "clarification_question", None),
            can_solve_myself=response.can_solve_myself,
            solution_info=response.solution_info,
            safety_guidance=response.safety_guidance,
            escalation=response.escalation,
            prevention=getattr(response, "prevention", None),
            solution=getattr(response, "solution", None),
            required_tools=getattr(response, "required_tools", None),
            estimated_time=getattr(response, "estimated_time", None),
            estimated_cost=getattr(response, "estimated_cost", None),
            safety_precautions=getattr(response, "safety_precautions", None),
            when_to_stop=getattr(response, "when_to_stop", None),
            when_to_contact_authority=getattr(response, "when_to_contact_authority", None),
        )

    def _remember_turn(self, problem: str, response: ChatResponse) -> None:
        summary = response.understanding.summary
        self._conversation_context.append(
            {
                "user": problem,
                "summary": summary,
                "severity": response.severity.value
                if hasattr(response.severity, "value")
                else str(response.severity),
            }
        )
        max_turns = self._max_context_turns()
        if len(self._conversation_context) > max_turns:
            del self._conversation_context[:-max_turns]

    def _format_context(self) -> str:
        if not self._conversation_context:
            return ""

        lines = []
        for item in self._conversation_context[-self._max_context_turns() :]:
            lines.append(
                f"- User: {item['user']}\n  Understanding: {item['summary']}\n  Severity: {item['severity']}"
            )
        return "\n".join(lines)

    def _max_context_turns(self) -> int:
        raw_value = os.getenv("AI_CONTEXT_TURNS", "4")
        try:
            return max(1, min(int(raw_value), 8))
        except ValueError:
            return 4

    def _build_critical_emergency_response(
        self,
        original_problem: str,
        ai_response: ChatResponse,
    ) -> ChatResponse:
        emergency_type = self._resolve_emergency_type(original_problem, ai_response)
        actions = CRITICAL_EMERGENCY_ACTIONS.get(
            emergency_type,
            CRITICAL_EMERGENCY_ACTIONS["life_threatening"],
        )
        summary = ai_response.understanding.summary
        category = ai_response.understanding.category or emergency_type
        follow_up = self._build_critical_follow_up(emergency_type)

        steps = actions["steps"].copy()
        if follow_up:
            steps.append(follow_up)

        frontend_problem = f"{actions['frontend_marker']}: {original_problem}"
        contact = actions.get(
            "contact",
            "Call 112 in India or your local emergency number immediately.",
        )

        return ChatResponse(
            problem=frontend_problem,
            understanding=ProblemUnderstanding(
                summary=summary,
                category=category,
                user_intent="Emergency safety guidance; no DIY repair instructions.",
            ),
            severity=SeverityLevel.CRITICAL,
            can_solve_myself=False,
            solution_info=SolutionInfo(steps=steps),
            safety_guidance=SafetyGuidance(
                precautions=actions["precautions"],
                when_to_stop="Do not attempt repair or rescue if it puts you in danger.",
            ),
            escalation=EscalationGuidance(
                required=True,
                contact=contact,
                reason=actions["reason"],
            ),
            solution=steps,
            safety_precautions=actions["precautions"],
            when_to_stop="Do not attempt repair or rescue if it puts you in danger.",
            when_to_contact_authority=contact,
        )

    def _resolve_emergency_type(self, problem: str, ai_response: ChatResponse) -> str:
        text = " ".join(
            [
                problem,
                ai_response.understanding.summary,
                ai_response.understanding.category or "",
                ai_response.understanding.user_intent or "",
            ]
        ).lower()

        emergency_signals = [
            ("earthquake", ["earthquake", "bhukamp"]),
            ("gas_leak", ["gas", "lpg", "cylinder", "गैस", "सिलेंडर"]),
            ("fire", ["fire", "aag", "आग", "burn", "smoke", "धुआ", "धुआं"]),
            ("electric_shock", ["shock", "current", "live wire", "electric", "करंट", "बिजली", "तार"]),
            ("flood_drowning", ["flood", "drown", "water level", "बाढ़", "डूब", "पानी भर"]),
            ("building_collapse", ["collapse", "building", "wall fell", "roof fell", "gir", "गिर", "मलबा"]),
            ("serious_injury", ["injury", "injured", "bleeding", "unconscious", "चोट", "खून", "बेहोश"]),
            ("cyclone_storm", ["cyclone", "storm", "toofan", "severe wind"]),
            ("landslide", ["landslide", "pahad gir", "slope collapse"]),
            ("lightning", ["lightning", "bijli gir"]),
            ("chemical_emergency", ["chemical", "acid", "toxic", "poison gas"]),
        ]

        for emergency_type, signals in emergency_signals:
            if any(signal in text for signal in signals):
                return emergency_type

        return "life_threatening"

    def _should_force_critical(self, problem: str, ai_response: ChatResponse) -> bool:
        text = " ".join(
            [
                problem,
                ai_response.understanding.summary,
                ai_response.understanding.category or "",
                ai_response.understanding.user_intent or "",
            ]
        ).lower()

        immediate_danger_signals = [
            "active emergency",
            "life-threatening",
            "immediate danger",
            "trapped",
            "phansa",
            "evacuate",
            "emergency safety",
            "call emergency",
            "112",
        ]
        disaster_signals = [
            "earthquake",
            "bhukamp",
            "fire",
            "aag",
            "gas leak",
            "electric shock",
            "live wire",
            "drowning",
            "building collapse",
            "cyclone",
            "severe storm",
            "landslide",
            "lightning",
            "chemical spill",
            "unconscious",
            "serious injury",
        ]

        return any(signal in text for signal in immediate_danger_signals) or any(
            signal in text for signal in disaster_signals
        )

    def _build_critical_follow_up(self, emergency_type: str) -> Optional[str]:
        if emergency_type == "earthquake":
            return "Kya aap building ke andar hain ya bahar safe jagah par hain?"
        if emergency_type in {"fire", "gas_leak", "building_collapse", "life_threatening"}:
            return "Kya aap abhi safe jagah par hain?"
        if emergency_type == "electric_shock":
            return "Kya main power supply band hai aur aap safe distance par hain?"
        if emergency_type == "flood_drowning":
            return "Kya aap paani se door safe jagah par hain?"
        if emergency_type == "serious_injury":
            return "Kya injured person hosh mein hai?"
        if emergency_type in {"cyclone_storm", "landslide", "lightning", "chemical_emergency"}:
            return "Kya aap abhi safe location par hain?"
        return None


def generate_ai_problem_resolution(problem: str) -> ChatResponse:
    return AIProblemResolutionService().generate_response(problem)


CRITICAL_EMERGENCY_ACTIONS = {
    "earthquake": {
        "frontend_marker": "critical emergency",
        "steps": [
            "Drop, Cover, and Hold On immediately.",
            "Protect your head and neck under a sturdy table or beside an interior wall.",
            "Stay away from windows, glass, shelves, and heavy objects.",
            "Do not use elevators.",
            "If you are already outside, move away from buildings, power lines, trees, and walls.",
            "Call 112 in India if anyone is trapped, injured, or in immediate danger.",
        ],
        "precautions": [
            "Be alert for aftershocks.",
            "Do not run outside while shaking is strong if debris may fall.",
            "If trapped, cover your mouth, stay as calm as possible, and signal for help.",
        ],
        "contact": "Call 112 in India if anyone is trapped, injured, or in immediate danger.",
        "reason": "Earthquakes can cause falling objects, structural damage, aftershocks, and injuries.",
    },
    "fire": {
        "frontend_marker": "fire emergency",
        "steps": [
            "Evacuate immediately if you can do so safely.",
            "Warn others nearby and stay low if there is smoke.",
            "Do not try to repair anything or fight a spreading fire yourself.",
            "Call 112 in India or the fire service immediately from a safe place.",
        ],
        "precautions": [
            "Do not go back inside for belongings.",
            "Do not use lifts during a fire.",
            "Do not put yourself in danger attempting rescue.",
        ],
        "contact": "Call 112 in India or the fire service immediately.",
        "reason": "Fire can spread quickly and can cause smoke inhalation, burns, or trapping.",
    },
    "gas_leak": {
        "frontend_marker": "gas leak emergency",
        "steps": [
            "Move everyone away from the area immediately.",
            "Do not use switches, flames, lighters, phones near the leak, or appliances.",
            "Open doors/windows only if it is safe and quick.",
            "Call 112 in India, fire service, or your gas agency from a safe place.",
        ],
        "precautions": [
            "Do not search for the leak with a flame.",
            "Do not try to repair the cylinder, pipe, or regulator yourself.",
            "Do not re-enter until trained personnel say it is safe.",
        ],
        "contact": "Call 112 in India, fire service, or your gas agency immediately.",
        "reason": "Gas leaks can ignite or explode and require trained emergency handling.",
    },
    "electric_shock": {
        "frontend_marker": "electric shock emergency",
        "steps": [
            "Keep everyone away from the person, wire, water, or electrical source.",
            "Switch off the main power only if you can do it safely without touching the victim or live source.",
            "Call 112 in India or emergency medical help immediately.",
            "Do not touch the person directly until the power source is isolated.",
        ],
        "precautions": [
            "Do not stand in water near electricity.",
            "Do not use metal or wet objects to move wires.",
            "Do not put yourself in danger attempting rescue.",
        ],
        "contact": "Call 112 in India or emergency medical help immediately.",
        "reason": "Live electricity can injure rescuers and cause cardiac or burn injuries.",
    },
    "flood_drowning": {
        "frontend_marker": "flood emergency",
        "steps": [
            "Move to higher ground or a dry safe place immediately.",
            "Keep away from fast-moving water, open drains, and submerged electrical areas.",
            "Call 112 in India or local disaster/emergency services immediately.",
            "If someone is drowning, call emergency help and avoid entering dangerous water yourself.",
        ],
        "precautions": [
            "Do not walk or drive through floodwater.",
            "Do not touch electrical switches or appliances while wet or standing in water.",
            "Do not attempt rescue if the water is fast, deep, or unsafe.",
        ],
        "contact": "Call 112 in India or local disaster/emergency services immediately.",
        "reason": "Flooding and drowning risks can become life-threatening very quickly.",
    },
    "building_collapse": {
        "frontend_marker": "collapse emergency",
        "steps": [
            "Move away from the damaged structure immediately if you can do so safely.",
            "Warn others not to enter the building or stand near unstable walls/ceilings.",
            "Call 112 in India or local fire/disaster response immediately.",
            "If someone is trapped, wait for trained rescuers and do not put yourself in danger.",
        ],
        "precautions": [
            "Do not re-enter the building.",
            "Do not move heavy debris yourself.",
            "Do not stand under cracked, sagging, or unstable structures.",
        ],
        "contact": "Call 112 in India or local fire/disaster response immediately.",
        "reason": "Structural collapse can cause secondary collapse, trapping, or severe injury.",
    },
    "serious_injury": {
        "frontend_marker": "medical emergency",
        "steps": [
            "Call 112 in India or emergency medical help immediately.",
            "Move the person only if staying there is more dangerous.",
            "If there is heavy bleeding, apply firm pressure with clean cloth if safe.",
            "Stay with the injured person and follow emergency operator instructions.",
        ],
        "precautions": [
            "Do not give food or drink to an unconscious or seriously injured person.",
            "Do not move suspected neck, spine, or head injuries unless there is immediate danger.",
            "Do not put yourself in danger while helping.",
        ],
        "contact": "Call 112 in India or emergency medical help immediately.",
        "reason": "Serious injury may need urgent medical care.",
    },
    "cyclone_storm": {
        "frontend_marker": "critical emergency",
        "steps": [
            "Move indoors to the strongest interior room away from windows.",
            "Stay away from glass, balconies, loose objects, and flood-prone areas.",
            "Do not go outside during strong winds or flying debris.",
            "Call 112 in India if anyone is injured, trapped, or in immediate danger.",
        ],
        "precautions": [
            "Avoid elevators and damaged electrical areas.",
            "Follow official local warnings and evacuation orders.",
            "If flooding starts, move to higher ground inside a safe structure.",
        ],
        "contact": "Call 112 in India or local disaster response if there is immediate danger.",
        "reason": "Cyclones and severe storms can cause flying debris, flooding, electrical danger, and structural damage.",
    },
    "landslide": {
        "frontend_marker": "critical emergency",
        "steps": [
            "Move away from the slope, falling debris, or unstable ground immediately.",
            "Warn nearby people if you can do so safely.",
            "Do not cross active mud, rocks, or flowing debris.",
            "Call 112 in India or local disaster response from a safe place.",
        ],
        "precautions": [
            "Stay away from damaged roads, hillsides, retaining walls, and power lines.",
            "Do not re-enter an affected building or slope area.",
            "If someone is trapped, wait for trained rescuers.",
        ],
        "contact": "Call 112 in India or local disaster response immediately.",
        "reason": "Landslides can continue moving and can trap or injure people without warning.",
    },
    "lightning": {
        "frontend_marker": "critical emergency",
        "steps": [
            "Move indoors immediately or into a hard-topped vehicle if no building is nearby.",
            "Stay away from open fields, rooftops, trees, poles, water, and metal objects.",
            "Do not use wired electrical devices or plumbing during lightning.",
            "Call 112 in India if someone is struck, unconscious, burned, or not breathing normally.",
        ],
        "precautions": [
            "Do not shelter under isolated trees.",
            "Stay inside until the storm has clearly passed.",
            "If someone is struck, it is safe to touch them after the strike, but call emergency help first.",
        ],
        "contact": "Call 112 in India for lightning injury or immediate danger.",
        "reason": "Lightning can cause cardiac arrest, burns, and secondary electrical hazards.",
    },
    "chemical_emergency": {
        "frontend_marker": "critical emergency",
        "steps": [
            "Move away from the chemical, fumes, spill, or gas cloud immediately.",
            "Avoid touching, smelling, or trying to clean the substance.",
            "If exposed, remove contaminated clothing only if safe and rinse affected skin with clean water.",
            "Call 112 in India, fire service, or poison/emergency medical support from a safe place.",
        ],
        "precautions": [
            "Do not mix chemicals or pour water unless emergency responders advise it.",
            "Do not stay in enclosed areas with fumes.",
            "Keep others away from the affected area.",
        ],
        "contact": "Call 112 in India, fire service, or emergency medical support immediately.",
        "reason": "Chemical exposure can cause poisoning, burns, breathing difficulty, or fire risk.",
    },
    "life_threatening": {
        "frontend_marker": "critical emergency",
        "steps": [
            "Move yourself and others to a safe place immediately if possible.",
            "Avoid touching or fixing anything that may be dangerous.",
            "Call 112 in India or the appropriate local emergency service immediately.",
            "If someone is trapped or injured, wait for trained responders and do not put yourself in danger.",
        ],
        "precautions": [
            "Do not attempt DIY repair during an active emergency.",
            "Do not re-enter an unsafe area.",
            "Follow instructions from emergency responders.",
        ],
        "contact": "Call 112 in India or the appropriate local emergency service immediately.",
        "reason": "The situation may involve immediate risk to life or safety.",
    },
}


SYSTEM_PROMPT = """
You are the AI service for SIH26043, a problem-resolution chatbot for real-life household and local societal problems.

Understand Hindi, Hinglish, English, and mixed Hindi-English naturally. Do semantic problem understanding first; do not behave like a keyword/category bot. The user may describe any household appliance issue, home safety issue, local sanitation problem, water issue, public infrastructure problem, neighborhood concern, or other real-life problem.

For every response:
- Identify what object/place/system the user is talking about, such as AC, washing machine, phone battery, kitchen tap, road, drain, wiring, gas cylinder, building, or public area.
- Identify the actual problem in context, such as AC water leakage, AC not cooling, appliance fire, swollen battery, gas smell, water near socket, blocked drain, or waterlogging outside the home.
- Determine the user's likely intent: solution, diagnosis, immediate safety help, explanation, professional help, authority escalation, or clarification.
- Assess severity from meaning and context, not from keywords alone.
- Generate guidance specific to the described problem.
- Include only useful fields. Do not fill tools, cost, time, prevention, or escalation unless they help for this problem.
- Do not invent or generate helpline phone numbers; verified helpline numbers are attached separately by the backend registry.
- If the message is vague, such as "AC kharab hai", ask one concise clarification question instead of guessing.
- If the latest message is a follow-up, use recent conversation context to refine the same problem.

Phase 1 understanding contract:
- understanding.summary must state what happened and the main object/place/situation involved in one specific sentence.
- understanding.category must be a short free-form label for the specific situation, not a forced predefined category.
- understanding.user_intent must state the likely intent and whether the information is sufficient, for example "diagnosis requested; enough information for basic checks" or "solution requested; clarification needed".
- If clarification is needed, ask exactly one concise question in solution_info.steps and avoid giving a guessed full solution.
- For unseen problems, reason from the described situation and common-sense safety, not from a stored list of categories.

Phase 2 intent and severity engine:
- Set user_intent to exactly one of SOLUTION, DIAGNOSIS, INFORMATION, PREVENTION, EMERGENCY_HELP, REPORT_COMPLAINT, PROFESSIONAL_HELP, or AMBIGUOUS.
- Set immediate_danger to true only when there is an immediate or potentially immediate threat to life/safety.
- Set clarification_needed to true when the user's message lacks enough detail to safely choose the next action.
- If clarification_needed is true, set clarification_question to exactly one concise question and put the same question as the only item in solution_info.steps.
- If clarification_needed is false, omit clarification_question.
- Do not guess a full cause or full solution for ambiguous messages such as "AC kharab hai" or unclear overheating like "Mera phone garam ho raha hai".
- Severity must depend on context, not only the object: AC remote failure is LOW; water near an electrical socket is MEDIUM or CRITICAL; geyser sparking and earthquakes are CRITICAL.

Phase 3 dynamic resolution engine:
- Use user_intent, severity, immediate_danger, and clarification_needed to decide the response content.
- If clarification_needed is true, ask exactly one useful clarification question, do not guess the problem, and do not provide a full solution until clarified.
- For LOW and MEDIUM, generate situation-specific guidance for the user's actual problem, not generic household advice.
- For LOW and MEDIUM, include only sections that are genuinely useful: solution_info.steps, safety_guidance, escalation, tools_materials, estimated_time, estimated_cost, and prevention are all optional.
- Do not force tools/materials, time, cost, escalation, or prevention when they are not meaningful for that situation.
- For DIAGNOSIS, explain likely causes only as practical checks; for SOLUTION, prioritize actionable steps; for REPORT_COMPLAINT, explain what to report and who to contact; for PROFESSIONAL_HELP, explain what expert is needed and what details to share.
- Never use a fixed problem template as the main response. Reason semantically from the user's exact words and recent context.

Classify severity as:
- LOW: safe, simple, non-urgent issues where cautious DIY guidance is appropriate.
- MEDIUM: issues that may affect safety, hygiene, utilities, shared infrastructure, or need a professional.
- CRITICAL: immediate danger such as fire, gas leak, electric shock, violence, medical emergency, collapse risk, or serious injury.

Examples of context-sensitive severity:
- "AC se paani tapak raha hai" is usually LOW or MEDIUM depending on amount/location; give AC drain/filter/safe power-off checks.
- "AC ki cooling nahi ho rahi" is usually LOW; ask about filter, mode, temperature, outdoor unit, and service history if needed.
- "AC me aag lag gayi hai" is CRITICAL appliance fire; emergency safety only.
- "AC me aag lag gayi hai aur main andar phansa hoon" is CRITICAL trapped-in-fire emergency; prioritize escape/emergency assistance.
- "Kitchen ke tap se paani leak ho raha hai" is usually LOW plumbing guidance.
- "Kitchen ke tap se paani electrical socket ke paas ja raha hai" is higher risk; prioritize electricity/water safety and professional help.
- "Phone ki battery phool gayi hai" is dangerous battery swelling; do not advise puncturing or charging, recommend safe isolation and professional disposal/service.

Use the same language as the user message whenever the frontend has not provided a selected language. Use Devanagari Hindi for Hindi responses, English for English responses, and natural Hinglish only when the user writes in Hinglish.

Return only JSON matching the provided schema. Include only fields that are relevant to the specific problem. Do not force tools, cost, time, or prevention when they are not useful. For LOW severity, provide safe DIY steps. For MEDIUM severity, provide safe guidance and professional or authority escalation. For CRITICAL severity, prioritize immediate human safety and emergency escalation over all other content.

For CRITICAL emergencies:
- Do not provide DIY repair instructions.
- Do not provide tools/materials, estimated repair time, estimated cost, prevention tips, or unnecessary diagnosis.
- Give concise immediate safety actions relevant to the emergency type.
- Tell the user to evacuate or move to a safe location when appropriate.
- For India, mention 112 for emergency assistance when appropriate.
- If someone is trapped or injured, tell the user not to put themselves in danger attempting rescue.
- Ask at most one short safety follow-up question only if useful.

Treat earthquake, fire, gas leak, electric shock/live wire, flood/drowning, building collapse, serious injury, cyclone/severe storm, landslide, lightning, chemical emergency, violence, and similar life-threatening situations as CRITICAL based on context and intent, including Hindi and Hinglish wording such as "bhukamp aa gaya", "ghar me aag", "aag lag gayi", "gas leak ho raha hai", "current lag gaya", "flood aa gaya", "building girne wali hai", "phansa hoon", or "jaan ko danger hai".

For earthquake specifically, prioritize Drop, Cover, Hold On; protect head and neck; stay away from windows, glass, and heavy objects; do not use elevators; if outside, move away from buildings, power lines, trees, and walls; stay alert for aftershocks; and call emergency help if anyone is trapped or injured.

For short follow-up messages like "ab kya karu?", "main building ke andar hu", "third floor par hu", or "bahar aa gaya hu", use recent conversation context to understand whether the active situation is an emergency and respond accordingly.

If the information is insufficient and the situation is not clearly critical, ask one clarification question.
""".strip()


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "problem": {"type": "string"},
        "understanding": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "category": {"type": "string"},
                "user_intent": {"type": "string"},
            },
            "required": ["summary"],
            "additionalProperties": False,
        },
        "user_intent": {
            "type": "string",
            "enum": [
                "SOLUTION",
                "DIAGNOSIS",
                "INFORMATION",
                "PREVENTION",
                "EMERGENCY_HELP",
                "REPORT_COMPLAINT",
                "PROFESSIONAL_HELP",
                "AMBIGUOUS",
            ],
        },
        "severity": {"type": "string", "enum": ["LOW", "MEDIUM", "CRITICAL"]},
        "immediate_danger": {"type": "boolean"},
        "clarification_needed": {"type": "boolean"},
        "clarification_question": {"type": "string"},
        "can_solve_myself": {"type": "boolean"},
        "solution_info": {
            "type": "object",
            "properties": {
                "steps": {"type": "array", "items": {"type": "string"}},
                "tools_materials": {"type": "array", "items": {"type": "string"}},
                "estimated_time": {"type": "string"},
                "estimated_cost": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "safety_guidance": {
            "type": "object",
            "properties": {
                "precautions": {"type": "array", "items": {"type": "string"}},
                "when_to_stop": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "escalation": {
            "type": "object",
            "properties": {
                "required": {"type": "boolean"},
                "contact": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["required"],
            "additionalProperties": False,
        },
        "prevention": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "problem",
        "understanding",
        "user_intent",
        "severity",
        "immediate_danger",
        "clarification_needed",
        "can_solve_myself",
    ],
    "additionalProperties": False,
}
