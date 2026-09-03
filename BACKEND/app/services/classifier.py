from app.schemas.chat import (
    ChatResponse,
    EscalationGuidance,
    ProblemUnderstanding,
    SafetyGuidance,
    SeverityLevel,
    SolutionInfo,
)


CRITICAL_KEYWORDS = [
    "fire",
    "aag",
    "आग",
    "gas leak",
    "gas smell",
    "गैस",
    "cylinder leak",
    "spark",
    "shock",
    "electric shock",
    "current",
    "करंट",
    "collapse",
    "gir gaya",
    "गिर",
    "bleeding",
    "medical emergency",
    "violence",
    "attack",
]

MEDIUM_KEYWORDS = [
    "wiring",
    "wire",
    "electric",
    "बिजली",
    "sewage",
    "नाली",
    "drain blocked",
    "pipe burst",
    "leakage",
    "leak",
    "roof",
    "छत",
    "crack",
    "structural",
    "water supply",
    "pest",
    "termite",
]


def classify_severity(problem: str) -> SeverityLevel:
    text = problem.lower()

    if any(keyword in text for keyword in CRITICAL_KEYWORDS):
        return SeverityLevel.CRITICAL

    if any(keyword in text for keyword in MEDIUM_KEYWORDS):
        return SeverityLevel.MEDIUM

    return SeverityLevel.LOW


def build_mock_response(problem: str) -> ChatResponse:
    severity = classify_severity(problem)

    if severity == SeverityLevel.CRITICAL:
        solution = [
            "Move people away from the danger area immediately.",
            "Do not attempt DIY repair or inspection.",
            "If safe, switch off the main electricity/gas supply from a distance.",
            "Call the appropriate emergency service or local authority.",
        ]
        safety_precautions = [
            "Do not touch exposed wires, leaking cylinders, fire sources, or unstable structures.",
            "Keep children, elderly people, and pets away from the area.",
            "Avoid using switches, flames, or electrical appliances near suspected gas leaks.",
        ]
        when_to_stop = "Stop all DIY action immediately. Leave the area if there is active danger."
        when_to_contact_authority = "Contact emergency services, fire department, electricity board, gas agency, police, or municipal authority immediately depending on the situation."
        prevention = [
            "Schedule regular inspection of electrical, gas, and structural systems.",
            "Install smoke detectors and keep emergency contacts visible at home.",
            "Do not ignore repeated smells, sparks, cracks, or overheating.",
        ]
        return ChatResponse(
            problem=problem,
            understanding=ProblemUnderstanding(
                summary=f"Potential emergency or high-risk issue reported: {problem}",
                category="emergency_or_high_risk",
                user_intent="Get immediate safety and escalation guidance",
            ),
            severity=severity,
            can_solve_myself=False,
            solution_info=SolutionInfo(
                steps=solution,
                estimated_time="Immediate action required",
                estimated_cost="Depends on emergency/professional service",
            ),
            safety_guidance=SafetyGuidance(
                precautions=safety_precautions,
                when_to_stop=when_to_stop,
            ),
            escalation=EscalationGuidance(
                required=True,
                contact=when_to_contact_authority,
                reason="The reported problem may involve immediate danger to people or property.",
            ),
            prevention=prevention,
            solution=solution,
            estimated_time="Immediate action required",
            estimated_cost="Depends on emergency/professional service",
            safety_precautions=safety_precautions,
            when_to_stop=when_to_stop,
            when_to_contact_authority=when_to_contact_authority,
        )

    if severity == SeverityLevel.MEDIUM:
        solution = [
            "Do a visual check only from a safe distance.",
            "Turn off the related supply if it is safe to do so.",
            "Avoid opening sealed panels, breaking walls, or handling electrical/plumbing internals.",
            "Contact a verified professional or local authority if the issue continues.",
        ]
        required_tools = ["Torch", "Phone camera for documentation", "Notebook"]
        safety_precautions = [
            "Do not touch wet electrical areas or exposed wiring.",
            "Wear footwear and keep the area dry where possible.",
            "Do not use temporary unsafe fixes for wiring, sewage, or structural problems.",
        ]
        when_to_stop = "Stop if you see sparks, smell gas, notice spreading cracks, hear unusual sounds, or feel unsafe."
        when_to_contact_authority = "Contact a professional, municipal body, electricity board, plumber, or housing society when the problem affects safety, public hygiene, or shared infrastructure."
        prevention = [
            "Maintain regular cleaning and inspection schedules.",
            "Report shared-area issues early.",
            "Keep photos and dates of recurring problems for escalation.",
        ]
        return ChatResponse(
            problem=problem,
            understanding=ProblemUnderstanding(
                summary=f"Non-emergency issue that may need professional support: {problem}",
                category="requires_professional_review",
                user_intent="Understand the issue and decide whether escalation is needed",
            ),
            severity=severity,
            can_solve_myself=False,
            solution_info=SolutionInfo(
                steps=solution,
                tools_materials=required_tools,
                estimated_time="15-30 minutes for basic checks",
                estimated_cost="Basic check: Rs. 0-200; professional service may vary",
            ),
            safety_guidance=SafetyGuidance(
                precautions=safety_precautions,
                when_to_stop=when_to_stop,
            ),
            escalation=EscalationGuidance(
                required=True,
                contact=when_to_contact_authority,
                reason="The issue may affect safety, hygiene, utilities, or shared infrastructure.",
            ),
            prevention=prevention,
            solution=solution,
            required_tools=required_tools,
            estimated_time="15-30 minutes for basic checks",
            estimated_cost="Basic check: Rs. 0-200; professional service may vary",
            safety_precautions=safety_precautions,
            when_to_stop=when_to_stop,
            when_to_contact_authority=when_to_contact_authority,
        )

    solution = [
        "Identify the exact location and visible cause of the problem.",
        "Gather basic tools and keep the area clean and well-lit.",
        "Try the simplest safe fix first.",
        "Check if the problem is solved and monitor it for a few hours.",
    ]
    required_tools = ["Cleaning cloth", "Basic screwdriver", "Gloves", "Bucket or container if needed"]
    safety_precautions = [
        "Keep children away while working.",
        "Do not use force on electrical, gas, or structural parts.",
        "Wash hands after cleaning or handling household waste.",
    ]
    when_to_stop = "Stop if the problem becomes worse, spreads, involves electricity/gas, or you are unsure about the cause."
    when_to_contact_authority = "Contact a local technician or municipal support if the issue repeats or affects public/shared areas."
    prevention = [
        "Clean and inspect the area regularly.",
        "Fix small issues early before they become larger.",
        "Keep basic tools and emergency contacts available.",
    ]
    return ChatResponse(
        problem=problem,
        understanding=ProblemUnderstanding(
            summary=f"Likely low-risk household or local issue reported: {problem}",
            category="basic_household_or_local_issue",
            user_intent="Get practical self-help guidance",
        ),
        severity=severity,
        can_solve_myself=True,
        solution_info=SolutionInfo(
            steps=solution,
            tools_materials=required_tools,
            estimated_time="10-30 minutes",
            estimated_cost="Rs. 0-300",
        ),
        safety_guidance=SafetyGuidance(
            precautions=safety_precautions,
            when_to_stop=when_to_stop,
        ),
        escalation=EscalationGuidance(
            required=False,
            contact=when_to_contact_authority,
            reason="Escalation is only needed if the issue repeats, worsens, or affects a shared/public area.",
        ),
        prevention=prevention,
        solution=solution,
        required_tools=required_tools,
        estimated_time="10-30 minutes",
        estimated_cost="Rs. 0-300",
        safety_precautions=safety_precautions,
        when_to_stop=when_to_stop,
        when_to_contact_authority=when_to_contact_authority,
    )
