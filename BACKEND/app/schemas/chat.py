from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    CRITICAL = "CRITICAL"


class ChatRequest(BaseModel):
    problem: str = Field(..., min_length=1, description="User's household or local societal problem")


class ProblemUnderstanding(BaseModel):
    summary: str
    category: Optional[str] = None
    user_intent: Optional[str] = None


class SolutionInfo(BaseModel):
    steps: Optional[list[str]] = None
    tools_materials: Optional[list[str]] = None
    estimated_time: Optional[str] = None
    estimated_cost: Optional[str] = None


class SafetyGuidance(BaseModel):
    precautions: Optional[list[str]] = None
    when_to_stop: Optional[str] = None


class EscalationGuidance(BaseModel):
    required: bool
    contact: Optional[str] = None
    reason: Optional[str] = None


class ChatResponse(BaseModel):
    problem: str
    understanding: ProblemUnderstanding
    severity: SeverityLevel
    can_solve_myself: bool
    solution_info: Optional[SolutionInfo] = None
    safety_guidance: Optional[SafetyGuidance] = None
    escalation: Optional[EscalationGuidance] = None
    prevention: Optional[list[str]] = None

    # Legacy fields retained for existing clients while the frontend moves to the
    # structured response above.
    solution: Optional[list[str]] = None
    required_tools: Optional[list[str]] = None
    estimated_time: Optional[str] = None
    estimated_cost: Optional[str] = None
    safety_precautions: Optional[list[str]] = None
    when_to_stop: Optional[str] = None
    when_to_contact_authority: Optional[str] = None
