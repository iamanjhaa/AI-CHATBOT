from app.schemas.chat import (
    ChatResponse,
    EscalationGuidance,
    ProblemUnderstanding,
    SafetyGuidance,
    SeverityLevel,
    SolutionInfo,
    UserIntent,
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
    dynamic_response = build_contextual_fallback_response(problem)
    if dynamic_response:
        return dynamic_response

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


def build_contextual_fallback_response(problem: str) -> ChatResponse | None:
    text = _normalize(problem)

    if _has_any(text, ["earthquake", "bhukamp"]):
        return _critical_response(
            problem,
            "Earthquake emergency reported.",
            "earthquake_emergency",
            [
                "Drop, Cover, and Hold On immediately.",
                "Protect your head and neck under a sturdy table or beside an interior wall.",
                "Stay away from windows, glass, shelves, and heavy objects.",
                "Do not use elevators.",
                "Call 112 in India if anyone is trapped, injured, or in immediate danger.",
            ],
            "Call 112 in India if anyone is trapped, injured, or in immediate danger.",
        )

    if _has_any(text, ["aag", "fire", "smoke", "burning"]):
        return _critical_response(
            problem,
            "Active fire or smoke emergency reported.",
            "fire_emergency",
            [
                "Evacuate immediately if you can do so safely.",
                "Warn others nearby and stay low if there is smoke.",
                "Do not try to repair the appliance or fight a spreading fire yourself.",
                "Call 112 in India or the fire service from a safe place.",
            ],
            "Call 112 in India or the fire service immediately.",
        )

    if _has_any(text, ["gas leak", "gas smell", "lpg", "cylinder leak"]):
        return _critical_response(
            problem,
            "Possible gas leak emergency reported.",
            "gas_leak_emergency",
            [
                "Move everyone away from the area immediately.",
                "Do not use switches, flames, lighters, phones near the leak, or appliances.",
                "Open doors or windows only if it is safe and quick.",
                "Call 112 in India, fire service, or your gas agency from a safe place.",
            ],
            "Call 112 in India, fire service, or your gas agency immediately.",
        )

    if _has_any(text, ["spark", "shock", "current", "live wire"]):
        return _critical_response(
            problem,
            "Electrical shock, spark, or live-power danger reported.",
            "electrical_emergency",
            [
                "Keep everyone away from the appliance, wire, water, or electrical source.",
                "Switch off the main power only if you can do it safely without touching the danger area.",
                "Do not touch the appliance, person, or wire directly.",
                "Call 112 in India or a qualified electrician/emergency service immediately.",
            ],
            "Call 112 in India for injury or immediate danger; call a qualified electrician for electrical faults.",
        )

    if _is_ambiguous(text):
        subject = _subject_from_text(text)
        question = f"What exactly is wrong with the {subject}: not working, leaking, overheating, noise/vibration, smell, or something else?"
        if subject == "phone" and _has_any(text, ["garam", "hot", "overheat", "heating"]):
            question = "Is your phone only warm during charging/use, or is it very hot, swollen, smoking, or shutting down?"
        if subject == "AC":
            question = "What exactly is wrong with the AC: cooling problem, water leakage, noise, remote issue, smell, or something else?"
        return _clarification_response(problem, subject, question, SeverityLevel.MEDIUM if "phone" in subject.lower() else SeverityLevel.LOW)

    appliance = _detect_appliance(text)
    issue = _detect_issue(text)

    if appliance == "washing machine" and issue in {"vibration_noise", "noise"}:
        return _normal_response(
            problem,
            "Washing machine vibration and unusual noise during operation.",
            "washing_machine_vibration_noise",
            SeverityLevel.LOW,
            [
                "Pause the cycle and check whether the load is uneven or too heavy.",
                "Redistribute clothes evenly and remove a few items if the drum is overloaded.",
                "Check that all four feet touch the floor and adjust the leveling feet if needed.",
                "Run a short spin cycle empty; if the noise remains, stop using it and book service.",
            ],
            precautions=["Do not put hands inside while the drum is moving.", "Stop using it if you hear grinding, burning smell, or loud banging."],
            escalation_contact="Call an appliance technician if leveling and load balancing do not fix the vibration.",
        )

    if appliance == "AC" and issue == "water_leak":
        return _normal_response(
            problem,
            "AC water leakage reported.",
            "ac_water_leakage",
            SeverityLevel.LOW,
            [
                "Switch off the AC and keep water away from sockets or extension boards.",
                "Clean the indoor-unit filter if it is dusty.",
                "Check whether the drain pipe is bent, blocked, or not sloping outward.",
                "If water still drips after cleaning/checking the drain path, call an AC technician.",
            ],
            precautions=["Do not open sealed AC panels or touch wiring.", "Treat it as higher risk if water is near electricity."],
            escalation_contact="Call an AC technician for blocked drain tray/pipe, ice formation, or repeated leakage.",
        )

    if appliance == "AC" and issue == "cooling":
        return _normal_response(
            problem,
            "AC cooling is weak or not working.",
            "ac_cooling_problem",
            SeverityLevel.LOW,
            [
                "Confirm the AC is on Cool mode and the temperature is set lower than room temperature.",
                "Clean the air filter and make sure airflow is not blocked.",
                "Check whether the outdoor unit fan is running and has open space around it.",
                "If cooling is still poor after 20-30 minutes, arrange AC service for gas level, coil, or compressor checks.",
            ],
            precautions=["Do not open refrigerant lines or electrical panels yourself."],
            escalation_contact="Call an AC technician if there is no cooling, ice buildup, unusual noise, or repeated tripping.",
        )

    if appliance == "fridge" and issue == "cooling":
        return _normal_response(
            problem,
            "Fridge cooling has become weak.",
            "fridge_cooling_problem",
            SeverityLevel.LOW,
            [
                "Check that the temperature setting has not been changed accidentally.",
                "Make sure the door gasket seals properly and the door is not being opened too often.",
                "Leave space behind the fridge for ventilation and clean visible dust from the back grille if accessible.",
                "If cooling does not improve within a few hours, call a refrigerator technician.",
            ],
            precautions=["Do not scrape ice with sharp tools or open sealed compressor parts."],
            escalation_contact="Call a technician if food is spoiling, compressor is very hot/noisy, or cooling stays weak.",
        )

    if appliance == "phone" and issue == "charging":
        return _normal_response(
            problem,
            "Phone charging problem reported.",
            "phone_charging_problem",
            SeverityLevel.LOW,
            [
                "Try a known-good charger and cable with the correct rating.",
                "Check the charging port gently for dust; clean only with a dry soft brush or air, not metal pins.",
                "Restart the phone and test another wall socket.",
                "If the port is loose, the phone heats a lot, or charging still fails, visit an authorized service center.",
            ],
            precautions=["Do not use a damaged cable, wet port, or swollen battery."],
            escalation_contact="Visit a service center if the battery swells, the port is damaged, or the phone overheats while charging.",
        )

    if appliance == "laptop" and issue == "slow":
        return _normal_response(
            problem,
            "Laptop is running slowly.",
            "laptop_slow_performance",
            SeverityLevel.LOW,
            [
                "Restart the laptop and close unused startup/background apps.",
                "Check free storage space and remove unnecessary temporary files.",
                "Run the built-in security scan and install pending system updates.",
                "If it is still slow, check RAM/storage health or ask a technician about SSD/RAM upgrade options.",
            ],
            precautions=["Back up important files before major cleanup, reset, or repair."],
        )

    if "battery" in text and _has_any(text, ["phool", "swollen", "bulge", "expanded"]):
        return _critical_response(
            problem,
            "Swollen phone battery reported.",
            "swollen_battery_danger",
            [
                "Stop using and charging the phone immediately.",
                "Keep it on a non-flammable surface away from people and heat if you can do so safely.",
                "Do not press, puncture, open, or try to repair the battery.",
                "Take it to an authorized service center or e-waste/battery disposal point.",
            ],
            "Contact an authorized phone service center or local e-waste/battery disposal service.",
        )

    if _has_any(text, ["cyber", "online fraud", "financial fraud", "upi fraud", "scam"]):
        return _normal_response(
            problem,
            "Online fraud or cyber financial fraud reported.",
            "cyber_financial_fraud",
            SeverityLevel.MEDIUM,
            [
                "Do not share OTP, PIN, password, CVV, screen-sharing access, or remote-control app access with anyone.",
                "Immediately contact your bank/payment app to block the transaction/account if money was involved.",
                "Save screenshots, transaction IDs, phone numbers, messages, and timestamps as evidence.",
                "Report the incident through the official cybercrime helpline/portal as soon as possible.",
            ],
            precautions=["Do not call back suspicious numbers or click new links sent by the suspected fraudster."],
            escalation_contact="Use the verified cybercrime helpline attached below for cyber financial fraud reporting.",
        )

    if _has_any(text, ["ceiling", "plaster", "cracking sound", "crack", "gir raha"]):
        return _normal_response(
            problem,
            "Ceiling cracking sound or falling plaster reported.",
            "ceiling_plaster_structural_risk",
            SeverityLevel.MEDIUM,
            [
                "Move people and valuables away from the affected ceiling area.",
                "Do not stand under the cracked or falling plaster section.",
                "Take photos/videos from a safe distance for the owner/society/engineer.",
                "Arrange inspection by building maintenance, landlord, or a civil engineer promptly.",
            ],
            precautions=["Do not scrape, hammer, or patch a ceiling that may be loose.", "Leave the room if cracks spread or pieces continue falling."],
            escalation_contact="Contact building maintenance, landlord, or a civil engineer urgently.",
        )

    if _has_any(text, ["bike", "motorcycle", "scooter"]) and _has_any(text, ["start", "band", "stall"]):
        return _normal_response(
            problem,
            "Two-wheeler starts but stalls or does not keep running.",
            "bike_starting_stalling",
            SeverityLevel.LOW,
            [
                "Check fuel level and whether the fuel tap/kill switch is in the correct position.",
                "If it has been unused, try starting with choke only briefly, then let the engine idle.",
                "Check for a weak battery, loose spark-plug cap, or blocked air filter if accessible.",
                "If it repeatedly stalls in traffic or after warming up, visit a mechanic.",
            ],
            precautions=["Do not keep cranking continuously; it can drain the battery.", "Avoid riding if it stalls unpredictably."],
            escalation_contact="Call a mechanic if the bike stalls repeatedly, leaks fuel, or smells strongly of petrol.",
        )

    if _has_any(text, ["sink", "drain"]) and _has_any(text, ["slow", "slowly", "drain", "jam"]):
        return _normal_response(
            problem,
            "Kitchen sink water is draining slowly.",
            "slow_sink_drain",
            SeverityLevel.LOW,
            [
                "Remove visible food particles from the sink strainer.",
                "Pour hot water slowly if the pipe is not plastic-sensitive and there is no chemical cleaner already inside.",
                "Clean the removable trap only if you are comfortable and can place a bucket underneath.",
                "Call a plumber if water backs up, smells bad, or multiple drains are slow.",
            ],
            tools=["Gloves", "Bucket", "Old brush or cloth"],
            precautions=["Do not mix drain chemicals.", "Stop if sewage-like water backs up."],
            escalation_contact="Call a plumber if basic cleaning does not improve drainage.",
        )

    if _has_any(text, ["shoes", "shoe"]) and _has_any(text, ["smell", "bad smell", "odor", "badbu"]):
        return _normal_response(
            problem,
            "Bad smell in shoes reported.",
            "shoe_odor",
            SeverityLevel.LOW,
            [
                "Dry the shoes completely in shade with good airflow.",
                "Remove and wash/dry the insoles if they are washable.",
                "Sprinkle baking soda overnight and shake it out fully before wearing.",
                "Use clean dry socks and rotate shoes so each pair dries between uses.",
            ],
            tools=["Baking soda", "Clean socks", "Soft brush"],
            prevention=["Keep shoes dry after rain/sweat.", "Use breathable socks and rotate footwear."],
        )

    if _has_any(text, ["machhar", "mosquito", "mosquitoes"]):
        return _normal_response(
            problem,
            "Repeated mosquito problem in the room reported.",
            "mosquito_control",
            SeverityLevel.LOW,
            [
                "Remove standing water from buckets, plant trays, coolers, drains, and nearby containers.",
                "Use window mesh or keep doors/windows closed during peak mosquito hours.",
                "Clean hidden damp corners and use a covered bin.",
                "If mosquitoes are coming from drains or nearby stagnant water, report it to local municipal/vector-control staff.",
            ],
            tools=["Window mesh", "Covered dustbin", "Mosquito repellent as per label directions"],
            precautions=["Use repellents/coils only with ventilation and keep them away from children."],
            escalation_contact="Contact municipal/vector-control services if breeding is outside your home or recurring.",
            prevention=["Empty stagnant water weekly.", "Keep coolers and drains clean.", "Repair window mesh gaps."],
        )

    return None


def _normal_response(
    problem: str,
    summary: str,
    category: str,
    severity: SeverityLevel,
    steps: list[str],
    tools: list[str] | None = None,
    precautions: list[str] | None = None,
    escalation_contact: str | None = None,
    prevention: list[str] | None = None,
) -> ChatResponse:
    escalation = EscalationGuidance(
        required=severity == SeverityLevel.MEDIUM or bool(escalation_contact),
        contact=escalation_contact,
        reason="Professional help is useful if the safe checks do not solve the issue."
        if escalation_contact
        else None,
    )
    return ChatResponse(
        problem=problem,
        understanding=ProblemUnderstanding(
            summary=summary,
            category=category,
            user_intent="Get a practical, situation-specific solution",
        ),
        user_intent=UserIntent.SOLUTION,
        severity=severity,
        immediate_danger=False,
        clarification_needed=False,
        can_solve_myself=severity == SeverityLevel.LOW,
        solution_info=SolutionInfo(steps=steps, tools_materials=tools),
        safety_guidance=SafetyGuidance(precautions=precautions) if precautions else None,
        escalation=escalation,
        prevention=prevention,
        solution=steps,
        required_tools=tools,
        safety_precautions=precautions,
        when_to_contact_authority=escalation_contact,
    )


def _critical_response(
    problem: str,
    summary: str,
    category: str,
    steps: list[str],
    contact: str,
) -> ChatResponse:
    precautions = [
        "Do not attempt DIY repair during active danger.",
        "Do not put yourself in danger attempting rescue.",
    ]
    return ChatResponse(
        problem=problem,
        understanding=ProblemUnderstanding(
            summary=summary,
            category=category,
            user_intent="Emergency safety guidance; no DIY repair instructions.",
        ),
        user_intent=UserIntent.EMERGENCY_HELP,
        severity=SeverityLevel.CRITICAL,
        immediate_danger=True,
        clarification_needed=False,
        can_solve_myself=False,
        solution_info=SolutionInfo(steps=steps),
        safety_guidance=SafetyGuidance(
            precautions=precautions,
            when_to_stop="Do not attempt repair or rescue if it puts you in danger.",
        ),
        escalation=EscalationGuidance(
            required=True,
            contact=contact,
            reason="The situation may involve immediate danger to life or safety.",
        ),
        solution=steps,
        safety_precautions=precautions,
        when_to_stop="Do not attempt repair or rescue if it puts you in danger.",
        when_to_contact_authority=contact,
    )


def _clarification_response(
    problem: str,
    subject: str,
    question: str,
    severity: SeverityLevel,
) -> ChatResponse:
    return ChatResponse(
        problem=problem,
        understanding=ProblemUnderstanding(
            summary=f"More detail is needed about the {subject} problem.",
            category=f"{subject.lower()}_clarification",
            user_intent="Clarification needed before giving a safe solution",
        ),
        user_intent=UserIntent.AMBIGUOUS,
        severity=severity,
        immediate_danger=False,
        clarification_needed=True,
        clarification_question=question,
        can_solve_myself=False,
        solution_info=SolutionInfo(steps=[question]),
        solution=[question],
    )


def _detect_appliance(text: str) -> str | None:
    if _has_any(text, ["washing machine", "washer"]):
        return "washing machine"
    if "ac" in text or "a c" in text:
        return "AC"
    if _has_any(text, ["fridge", "refrigerator"]):
        return "fridge"
    if "phone" in text:
        return "phone"
    if "laptop" in text:
        return "laptop"
    return None


def _detect_issue(text: str) -> str | None:
    if _has_any(text, ["paani leak", "water leak", "leak", "tapak"]):
        return "water_leak"
    if _has_any(text, ["cooling", "thanda", "kam ho gayi", "cold"]):
        return "cooling"
    if _has_any(text, ["vibration", "vibrate", "hilti", "awaaz", "noise", "sound"]):
        return "vibration_noise"
    if _has_any(text, ["charge", "charging"]):
        return "charging"
    if _has_any(text, ["slow", "hang", "lag"]):
        return "slow"
    return None


def _is_ambiguous(text: str) -> bool:
    if ("phone" in text and _has_any(text, ["garam", "hot", "overheat", "heating"])):
        return True
    return (
        ("ac" in text or "a c" in text)
        and _has_any(text, ["kharab", "problem", "issue"])
        and not _detect_issue(text)
    )


def _subject_from_text(text: str) -> str:
    return _detect_appliance(text) or "reported item"


def _has_any(text: str, signals: list[str]) -> bool:
    return any(signal in text for signal in signals)


def _normalize(value: str) -> str:
    return " ".join(str(value or "").lower().replace("-", " ").split())
