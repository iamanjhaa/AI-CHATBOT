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

    if _is_pressure_cooker_danger(text):
        return _critical_response(
            problem,
            "Pressure cooker explosion or unsafe pressurized cooker situation reported.",
            "pressure_cooker_safety_emergency",
            [
                "Move away from the cooker and keep others away from the kitchen.",
                "Do not touch, open, shake, cool suddenly, or try to repair a hot or pressurized cooker.",
                "Turn off the heat only if you can do it without going close to steam, fire, or damaged parts.",
                "If there is injury, fire, smoke, gas smell, or an active blast risk, call emergency help from a safe place.",
            ],
            "Call 112 in India if there is injury, fire, trapped person, or immediate danger.",
        )

    if _has_any(text, ["battery phool", "battery swollen", "swollen battery", "battery bulge", "battery expanded"]):
        return _critical_response(
            problem,
            "Swollen and overheating phone battery reported.",
            "swollen_battery_danger",
            [
                "Stop using and charging the phone immediately.",
                "Keep it on a non-flammable surface away from people and heat if you can do so safely.",
                "Do not press, puncture, open, or try to repair the battery.",
                "Take it to an authorized service center or battery/e-waste disposal point once it is safe to move.",
            ],
            "Contact an authorized phone service center; call 112 in India if there is smoke, fire, or injury.",
        )

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

    if _has_any(text, ["aag", "fire", "smoke", "dhua", "dhuan", "jal rahi", "jal raha"]):
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

    if _has_any(text, ["gas leak", "gas smell", "gas ki smell", "gas smell aa", "lpg leak", "cylinder leak", "gas leak ho"]):
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

    if _has_any(text, ["spark", "sparking", "shock", "current", "live wire", "chingari"]):
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

    if _is_civic_report(text):
        return _normal_response(
            problem,
            "Civic or public-area problem that should be reported to the responsible local service.",
            "civic_report_complaint",
            SeverityLevel.MEDIUM,
            [
                "Note the exact location, nearby landmark, date/time, and how long the issue has existed.",
                "Take clear photos or videos if it is safe.",
                "Report it through your municipal corporation, ward office, housing society, electricity department, or official local grievance channel as relevant.",
                "Keep the complaint reference number so you can follow up.",
            ],
            tools=["Phone camera", "Location details", "Complaint reference number"],
            precautions=["Avoid direct contact with garbage, sewage, broken wires, or unsafe public infrastructure."],
            escalation_contact="Use the relevant local civic authority or official grievance channel; do not rely on unverified phone numbers.",
            user_intent=UserIntent.REPORT_COMPLAINT,
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

    if appliance == "phone" and issue == "overheating":
        return _clarification_response(
            problem,
            "phone",
            "Phone kitna garam hai, aur kya battery phooli hui hai, smoke, burning smell, ya sudden shutdown ho raha hai?",
            SeverityLevel.MEDIUM,
        )

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

    if appliance == "laptop" and issue == "restart":
        return _normal_response(
            problem,
            "Laptop is restarting repeatedly.",
            "laptop_repeated_restart",
            SeverityLevel.LOW,
            [
                "Save your work and note whether restarts happen during startup, charging, gaming, or normal use.",
                "Check for overheating: keep vents clear and use the laptop on a hard flat surface.",
                "Install pending system updates and run the built-in security scan.",
                "If restarts continue, back up important files and get battery, charger, RAM, storage, and thermal condition checked.",
            ],
            precautions=["Stop using it if there is burning smell, smoke, swelling, or extreme heat."],
            escalation_contact="Visit a laptop technician/service center if restarts continue after basic checks.",
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

    if appliance in {"mixer", "microwave", "oven", "geyser", "fan", "iron", "inverter", "UPS"} and issue == "burning_smell":
        return _normal_response(
            problem,
            f"{appliance.title()} burning smell or overheating reported.",
            f"{appliance.replace(' ', '_').lower()}_burning_smell",
            SeverityLevel.MEDIUM,
            [
                "Switch it off immediately and unplug it if the plug area is safe, dry, and not hot.",
                "Keep it away from cloth, paper, gas stove, and other flammable items.",
                "Do not open the appliance body or continue testing it.",
                "Use it again only after inspection by a qualified technician.",
            ],
            precautions=["Treat smoke, flame, sparks, or shock as an emergency and move away."],
            escalation_contact="Call a qualified appliance technician; call emergency help if there is smoke, fire, or injury.",
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

    if _has_any(text, ["ceiling", "chhat", "roof"]) and _has_any(text, ["paani", "water", "tapak", "leak", "seep"]):
        return _normal_response(
            problem,
            "Water leakage from ceiling or roof reported.",
            "ceiling_water_leakage",
            SeverityLevel.MEDIUM,
            [
                "Move electronics, furniture, and people away from the dripping area.",
                "Do not touch nearby switches, lights, fans, or wet wiring.",
                "Place a bucket only if the spot is safe and mark/take photos of the leak.",
                "Contact building maintenance, landlord, or a plumber/roofer to find the source.",
            ],
            tools=["Bucket", "Phone camera", "Dry footwear"],
            precautions=["Switch off power to affected lights/fans only from a safe dry main switch if water is near electricity."],
            escalation_contact="Get professional inspection urgently if water is near wiring, the ceiling is sagging, or plaster is falling.",
        )

    if _has_any(text, ["ceiling", "plaster", "cracking sound", "crack", "gir raha", "chhat"]):
        if _has_any(text, ["badi crack", "big crack", "wide crack", "girne wali", "collapse", "jhuk", "sag"]):
            return _critical_response(
                problem,
                "Major ceiling or roof crack may indicate structural danger.",
                "structural_collapse_risk",
                [
                    "Move everyone away from the cracked ceiling/roof area immediately.",
                    "Do not stand underneath or try to patch, drill, or hammer the crack.",
                    "Warn others not to enter that room until it is inspected.",
                    "Contact building maintenance, landlord, or a civil/structural engineer urgently.",
                ],
                "Call 112 in India if collapse seems imminent, debris is falling, or anyone is injured/trapped.",
            )
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

    if _has_any(text, ["sink", "kitchen"]) and _has_any(text, ["slow", "slowly", "drain", "jam", "blocked", "block"]):
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

    if _has_any(text, ["bathroom", "toilet", "sink", "drain", "nali"]) and _has_any(text, ["block", "blocked", "jam", "clog"]):
        return _normal_response(
            problem,
            "Bathroom drain blockage reported.",
            "bathroom_drain_blockage",
            SeverityLevel.LOW,
            [
                "Stop adding more water if it is backing up.",
                "Wear gloves and remove visible hair or debris from the drain cover.",
                "Use a plunger gently; avoid forcing rods deep into the pipe.",
                "Call a plumber if water backs up repeatedly, multiple drains are blocked, or sewage smell appears.",
            ],
            tools=["Gloves", "Plunger", "Bucket", "Old brush"],
            precautions=["Do not mix chemical drain cleaners or put bare hands in dirty standing water."],
            escalation_contact="Call a plumber or municipal support if sewage or multiple blocked drains are involved.",
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
    user_intent: UserIntent = UserIntent.SOLUTION,
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
        user_intent=user_intent,
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


def _is_civic_report(text: str) -> bool:
    civic_subjects = [
        "garbage",
        "kachra",
        "trash",
        "waste",
        "sewage",
        "sewer",
        "drain",
        "nali",
        "road",
        "sadak",
        "street light",
        "streetlight",
        "water supply",
        "public toilet",
        "mosquito",
        "machhar",
    ]

    report_signals = [
        "complaint",
        "complain",
        "report",
        "kahan karu",
        "kaha karu",
        "kahan kare",
        "kaha kare",
        "authority",
        "municipal",
        "nagar nigam",
        "nagar palika",
        "government",
        "sarkar",
        "helpline",
    ]

    return _has_any(text, civic_subjects) and _has_any(text, report_signals)


def _is_pressure_cooker_danger(text: str) -> bool:
    pressure_cooker_signals = [
        "pressure cooker",
        "pressure-cooker",
        "cooker se steam",
        "cooker se bhap",
        "cooker phat",
        "cooker blast",
        "cooker ki seeti",
        "cooker ki whistle",
    ]

    danger_signals = [
        "phat",
        "blast",
        "burst",
        "steam leak",
        "bhap leak",
        "pressure",
        "seeti nahi",
        "whistle nahi",
        "stuck",
        "jam",
        "danger",
        "dangerous",
        "dar lag",
    ]

    return _has_any(text, pressure_cooker_signals) and _has_any(
        text, danger_signals
    )



def _normalize(value: str) -> str:
    return " ".join(str(value or "").lower().replace("-", " ").split())
