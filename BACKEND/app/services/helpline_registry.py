from app.schemas.chat import ChatResponse, HelplineEntry


INDIA_PORTAL_HELPLINE_SOURCE = "https://www.india.gov.in/directory/helpline"
ERSS_SOURCE = "https://112.gov.in/"
CYBERCRIME_SOURCE = "https://cybercrime.gov.in/"
CONSUMER_SOURCE = "https://consumerhelpline.gov.in/public/index.php/contact"
UIDAI_SOURCE = "https://uidai.gov.in/en/contact-support"
PASSPORT_SOURCE = "https://www.passportindia.gov.in/psp/CallCenter"
FSSAI_SOURCE = "https://fssai.gov.in/"


HELPLINE_DIRECTORY = [
    HelplineEntry(
        category="Emergency",
        name="Emergency Response Support System",
        number="112",
        purpose="Pan-India emergency assistance for police, fire, rescue, health, and threat-to-life situations.",
        scope="National",
        source=ERSS_SOURCE,
    ),
    HelplineEntry(
        category="Police",
        name="Police Helpline",
        number="100",
        purpose="Police assistance.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Fire & Rescue",
        name="Fire Helpline",
        number="101",
        purpose="Fire and rescue assistance.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Ambulance / Medical",
        name="National Ambulance Service",
        number="102",
        purpose="Ambulance and medical transport assistance.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Cyber Crime / Financial Fraud",
        name="National Cyber Crime Helpline",
        number="1930",
        purpose="Immediate reporting of cyber financial fraud.",
        scope="National",
        source=CYBERCRIME_SOURCE,
    ),
    HelplineEntry(
        category="LPG / Gas Leakage",
        name="LPG Leak Helpline",
        number="1906",
        purpose="LPG/gas leakage reporting and support.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Disaster / Natural Calamity",
        name="Relief Commissioner for Natural Calamities",
        number="1070",
        purpose="Natural calamity relief assistance.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Disaster / Natural Calamity",
        name="NDRF Disaster Helpline",
        number="011-24363260",
        purpose="Earthquake, flood, disaster, and NDRF assistance.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Consumer",
        name="National Consumer Helpline",
        number="1915",
        purpose="Consumer grievance registration and guidance.",
        scope="National",
        source=CONSUMER_SOURCE,
    ),
    HelplineEntry(
        category="Railway",
        name="RailMadad / Railway Helpline",
        number="139",
        purpose="Railway enquiry, assistance, security, medical help, and grievance redressal.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Child Protection",
        name="Child Helpline",
        number="1098",
        purpose="Child protection and child assistance.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Women Assistance",
        name="Women Helpline",
        number="181",
        purpose="Women assistance and domestic violence support.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Women Assistance",
        name="National Commission for Women Helpline",
        number="7827170170",
        purpose="Women assistance and support through NCW.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Senior Citizens",
        name="Senior Citizens Helpline",
        number="14567",
        purpose="Senior citizen assistance.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Persons with Disabilities",
        name="Persons with Disabilities Helpline",
        number="14456",
        purpose="Assistance for persons with disabilities.",
        scope="National",
        source=INDIA_PORTAL_HELPLINE_SOURCE,
    ),
    HelplineEntry(
        category="Aadhaar / UIDAI",
        name="UIDAI Contact Centre",
        number="1947",
        purpose="Aadhaar enrolment, update, status, and grievance support.",
        scope="National",
        source=UIDAI_SOURCE,
    ),
    HelplineEntry(
        category="Passport",
        name="Passport Seva National Call Centre",
        number="1800-258-1800",
        purpose="Passport service information, suggestions, and application status support.",
        scope="National",
        source=PASSPORT_SOURCE,
    ),
    HelplineEntry(
        category="Food Safety",
        name="FSSAI Helpdesk",
        number="1800112100",
        purpose="Food safety, FSSAI licensing, registration, and food grievance support.",
        scope="National",
        source=FSSAI_SOURCE,
    ),
]


DIRECTORY_REQUEST_SIGNALS = [
    "help line number",
    "helpline number",
    "helpline numbers",
    "all helpline",
    "all help line",
    "government helpline",
    "government help number",
    "government numbers",
    "emergency numbers",
    "saare government",
    "india ke helpline",
    "mujhe helpline chahiye",
    "number batao",
    "help chahiye number",
]

CATEGORY_SIGNALS = {
    "Cyber Crime / Financial Fraud": ["cyber", "fraud", "financial fraud", "online scam", "upi"],
    "LPG / Gas Leakage": ["gas leak", "gas smell", "lpg", "cylinder"],
    "Railway": ["railway", "train", "railmadad"],
    "Consumer": ["consumer", "refund", "product complaint", "seller complaint"],
    "Food Safety": ["food", "fssai", "restaurant", "packaged food"],
    "Aadhaar / UIDAI": ["aadhaar", "uidai"],
    "Passport": ["passport"],
    "Child Protection": ["child", "minor", "bachcha"],
    "Women Assistance": ["women", "woman", "domestic violence", "mahila"],
    "Senior Citizens": ["senior citizen", "elderly"],
    "Persons with Disabilities": ["disability", "disabled", "pwd"],
    "Disaster / Natural Calamity": ["earthquake", "bhukamp", "flood", "cyclone", "landslide", "disaster"],
    "Fire & Rescue": ["fire", "aag"],
    "Ambulance / Medical": ["ambulance", "medical", "injury", "unconscious"],
    "Police": ["police", "crime", "violence", "threat"],
}


def is_helpline_directory_request(problem: str) -> bool:
    text = _normalize(problem)
    compact_text = text.replace("help line", "helpline")
    return any(
        _normalize(signal) in text
        or _normalize(signal).replace("help line", "helpline") in compact_text
        for signal in DIRECTORY_REQUEST_SIGNALS
    )


def get_all_helplines() -> list[HelplineEntry]:
    return HELPLINE_DIRECTORY.copy()


def get_relevant_helplines(problem: str) -> list[HelplineEntry]:
    text = _normalize(problem)
    categories = {
        category
        for category, signals in CATEGORY_SIGNALS.items()
        if any(signal in text for signal in signals)
    }

    if categories & {
        "LPG / Gas Leakage",
        "Fire & Rescue",
        "Ambulance / Medical",
        "Police",
        "Disaster / Natural Calamity",
    }:
        categories.add("Emergency")

    return [entry for entry in HELPLINE_DIRECTORY if entry.category in categories]


def build_helpline_directory_response(problem: str) -> ChatResponse:
    return ChatResponse(
        problem=problem,
        understanding={
            "summary": "User requested verified all-India government and emergency helpline numbers.",
            "category": "helpline_directory",
            "user_intent": "REPORT_COMPLAINT; enough information",
        },
        user_intent="REPORT_COMPLAINT",
        severity="LOW",
        immediate_danger=False,
        clarification_needed=False,
        can_solve_myself=False,
        solution_info={
            "steps": [
                "Use the verified helpline entries below based on the category of help needed."
            ]
        },
        helplines=get_all_helplines(),
    )


def attach_relevant_helplines(response: ChatResponse, problem: str) -> ChatResponse:
    helplines = get_relevant_helplines(problem)
    if not helplines:
        return response

    response.helplines = helplines
    return response


def _normalize(value: str) -> str:
    return " ".join(str(value or "").lower().replace("-", " ").split())
