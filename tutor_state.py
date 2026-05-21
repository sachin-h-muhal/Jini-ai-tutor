from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class StudentProfile(TypedDict):
    student_id: str
    student_name: str
    current_grade_level: str
    strengths: List[str]
    weaknesses: List[str]
    learning_pace: str

class WorkAnalysis(TypedDict):
    image_url: Optional[str]
    extracted_text: Optional[str]
    is_correct: bool
    conceptual_flaw_detected: Optional[str]
    suggested_hint: Optional[str]

class AssessmentReport(TypedDict):
    question_asked: str
    student_answer: str
    score_percentage: int  # 0 to 100 evaluation score
    passed_gate: bool      # Becomes True only if score_percentage >= 70
    evaluation_rationale: str

class TutorState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    student_profile: StudentProfile
    current_work: Optional[WorkAnalysis]
    current_lesson_plan: List[str]
    current_topic_index: int
    teaching_style_guide: str
    next_action: str
    # 🟩 NEW PARAMETERS FOR GRAPH-LEVEL STATE ENFORCEMENT
    active_assessment: Optional[AssessmentReport]
    session_metrics: List[Dict[str, Any]]  # Stores timestamped event sequences for Phase 2 Analytics