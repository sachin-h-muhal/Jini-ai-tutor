import os
import re
import base64
import mimetypes
import sqlite3
from typing import Dict, Any, List, Optional

from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END, START
# 🟩 THE CORRECT PYTHON LAYOUT
from langgraph.checkpoint.sqlite import SqliteSaver
from tutor_state import TutorState
from langchain_google_genai import ChatGoogleGenerativeAI

# ── Startup & Initialization ──────────────────────────────────────────────────
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_KEY:
    print("\n❌ CRITICAL: GOOGLE_API_KEY not found in .env file!")
    exit(1)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=GOOGLE_KEY,
    model_kwargs={"transport": "rest"}
)


# ── YouTube Style Ingestion ───────────────────────────────────────────────────
def extract_youtube_id(url: str) -> Optional[str]:
    pattern = (
        r'(?:https?://)?(?:www\.)?'
        r'(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)'
        r'([^"&?/ ]{11})'
    )
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_youtube_style_profile(urls: List[str]) -> str:
    if not urls or not urls[0]:
        return "Standard concise, direct, step-by-step engineering tutorial voice."

    combined_transcripts = ""
    ytt_api = YouTubeTranscriptApi()

    for url in urls:
        video_id = extract_youtube_id(url)
        if not video_id:
            continue
        try:
            fetched = ytt_api.fetch(video_id, languages=["en", "hi", "ja"])
            text_run = " ".join([item["text"] for item in fetched.to_raw_data()[:120]])
            combined_transcripts += f"\n--- VIDEO ({video_id}) ---\n{text_run}\n"
        except Exception:
            pass

    if not combined_transcripts:
        return "Standard conceptual coding instructor persona."

    prompt = (
        f"Analyze the linguistic fingerprint, vocabulary style, and explanation patterns "
        f"in these transcripts:\n{combined_transcripts}\n\n"
        f"Generate a clear 3-sentence persona instruction set telling an AI how to mimic "
        f"this exact teaching voice, catchphrases, structural rhythm, and explanation style."
    )
    try:
        return llm.invoke([HumanMessage(content=prompt)]).content.strip()
    except Exception:
        return "Standard adaptive technical mentor persona."


# ── Image Helpers ─────────────────────────────────────────────────────────────
def encode_image_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ── Phase 4: Automated Weakness Diagnostics Engine ────────────────────────────
def extract_and_update_weaknesses(state: dict) -> dict:
    """Background analytics engine that parses failures and adds precise conceptual gaps to state."""
    profile = state.get("student_profile", {})
    report = state.get("active_assessment")

    if not report or report.get("passed_gate", True):
        return {}

    current_weaknesses = profile.get("weaknesses", [])
    failed_concept = report.get("question_asked", "")
    student_flawed_answer = report.get("student_answer", "")
    instructor_rationale = report.get("evaluation_rationale", "")

    analyzer_prompt = (
        f"You are an advanced academic data diagnostics engine.\n"
        f"A student failed a comprehension checkpoint gate.\n"
        f"Concept Focus: {failed_concept}\n"
        f"Student's Flawed Response: {student_flawed_answer}\n"
        f"Grader Evaluation Notes: {instructor_rationale}\n\n"
        f"Identify the precise, core technical weakness (e.g., 'Confusing conditional checking with exception handling').\n"
        f"Output ONLY the concise weakness phrase. Do not write introductory prose, bullets, or extra characters."
    )

    try:
        extracted_weakness = llm.invoke([SystemMessage(content=analyzer_prompt)]).content.strip()
        # Clean up any residual markdown formatting
        extracted_weakness = extracted_weakness.replace("`", "").replace("'", "").replace('"', "")

        if extracted_weakness and extracted_weakness not in current_weaknesses:
            current_weaknesses.append(extracted_weakness)
    except Exception:
        pass

    profile["weaknesses"] = current_weaknesses
    return {"student_profile": profile}


# ── Node 1: Work Checker ──────────────────────────────────────────────────────
def work_checker_node(state: TutorState) -> Dict[str, Any]:
    current_work = state.get("current_work")
    if not current_work or not current_work.get("image_url"):
        return {"next_action": "route_to_dialogue"}

    target_path = current_work["image_url"]

    if os.path.exists(target_path):
        guess, _ = mimetypes.guess_type(target_path)
        mime_type = guess if guess else "image/png"
        img_url = f"data:{mime_type};base64,{encode_image_to_base64(target_path)}"
    else:
        img_url = target_path

    message = HumanMessage(content=[
        {
            "type": "text",
            "text": (
                "Analyze this solution step-by-step. Pinpoint conceptual gaps without "
                "giving away the answer. If it is fully correct, reply with the word 'CORRECT'."
            )
        },
        {"type": "image_url", "image_url": {"url": img_url}}
    ])

    try:
        response = llm.invoke([message])
        is_correct = "CORRECT" in response.content.upper()
        extracted_text = response.content
    except Exception:
        is_correct = False
        extracted_text = "Vision sync failed."

    return {
        "current_work": {
            "image_url": target_path,
            "extracted_text": extracted_text,
            "is_correct": is_correct,
            "conceptual_flaw_detected": None if is_correct else "Conceptual gap detected",
            "suggested_hint": "Review the execution syntax and logical flow carefully."
        },
        "next_action": "route_to_dialogue" if is_correct else "route_to_hint"
    }


# ── Node 2: Dialogue Manager ──────────────────────────────────────────────────
MAX_HISTORY = 10


def dialogue_manager_node(state: TutorState, config: RunnableConfig) -> Dict[str, Any]:
    messages = state["messages"]
    work = state.get("current_work")
    profile = state["student_profile"]
    agenda = state.get("current_lesson_plan", ["1. Core Concepts"])

    current_index = min(state.get("current_topic_index", 0), len(agenda) - 1)
    style_guide = state.get("teaching_style_guide", "Be a helpful, clear teacher.")
    current_topic = agenda[current_index]

    student_name = profile.get("student_name", "Explorer")
    grade_level = profile.get("current_grade_level", "Beginner")
    learning_pace = profile.get("learning_pace", "Conceptual & Deep-Dive")

    system_prompt = (
        f"You are a patient virtual classroom teacher named Jini.\n\n"
        f"━━ PERSONA & SPEECH STYLE ━━\n"
        f"{style_guide}\n\n"
        f"━━ STUDENT PROFILE ━━\n"
        f"Name: {student_name}\n"
        f"Level: {grade_level}  |  Pace: {learning_pace}\n"
        f"Strengths: {profile.get('strengths', [])}\n"
        f"Logically Tracked Weaknesses to Remediate: {profile.get('weaknesses', [])}\n\n"
        f"━━ ACTIVE LESSON ━━\n"
        f"Current active topic: '{current_topic}'\n\n"
        f"━━ COMPREHENSION GATE RULES ━━\n"
        f"When the student claims to understand or asks to move on:\n"
        f"  1. Ask a single focused conceptual challenge question testing '{current_topic}'.\n"
        f"  2. Do NOT advance them yourself. Tell them they must verify their grasp first.\n"
        f"  3. Once you present the question, add the hidden anchor token [INTENT: NEXT] at the end of your response.\n\n"
        f"━━ RESPONSE FORMAT RULES ━━\n"
        f"1. ALWAYS start your reply with '[INTENT: DOUBT]' or '[INTENT: NEXT]' followed by two newlines.\n"
        f"2. Address the student as '{student_name}' naturally.\n"
        f"3. Frame explanations matching their grade tier: {grade_level}."
    )

    if work and work.get("extracted_text") and work["extracted_text"] != "Vision sync failed.":
        system_prompt += f"\n\n━━ HOMEWORK IMAGE ANALYSIS ━━\n{work['extracted_text']}\n"

    cleaned_history = [
        m for m in messages if isinstance(m, (HumanMessage, AIMessage, SystemMessage))
    ][-MAX_HISTORY:]

    full_payload = [SystemMessage(content=system_prompt)] + cleaned_history

    chunks = []
    for chunk in llm.stream(full_payload, config):
        chunks.append(chunk.content)

    full_response = "".join(chunks)

    return {
        "messages": [AIMessage(content=full_response)],
        "current_topic_index": current_index,
        "current_lesson_plan": agenda,
        "teaching_style_guide": style_guide
    }


# ── Node 3: Hardened Assessment Gate ──────────────────────────────────────────
def assessment_node(state: TutorState) -> Dict[str, Any]:
    messages = state["messages"]
    agenda = state.get("current_lesson_plan", [])
    curr_idx = state.get("current_topic_index", 0)

    if len(messages) < 2:
        return {"next_action": "continue_dialogue"}

    last_ai_message = None
    last_human_message = None

    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not last_ai_message:
            last_ai_message = msg.content
        elif isinstance(msg, HumanMessage) and not last_human_message:
            last_human_message = msg.content
        if last_ai_message and last_human_message:
            break

    is_eval_context = "[INTENT: NEXT]" in str(last_ai_message) or "confirm your grasp" in str(last_ai_message).lower()

    if not is_eval_context:
        return {"next_action": "continue_dialogue"}

    evaluator_prompt = (
        f"You are a strict grading framework analyzing an engineering student response.\n"
        f"Target Concept Focus: {agenda[curr_idx] if curr_idx < len(agenda) else 'General Concept'}\n"
        f"Question Posed by Tutor: {last_ai_message}\n"
        f"Student Answer: {last_human_message}\n\n"
        f"Score response accurately. Output exactly in this structural format:\n"
        f"SCORE: [Integer 0 to 100]\n"
        f"RATIONALE: [One clear descriptive feedback sentence]\n"
        f"PASSED: [TRUE or FALSE] (Set TRUE only if score >= 70)"
    )

    try:
        eval_response = llm.invoke([SystemMessage(content=evaluator_prompt)]).content.strip()
        score_match = re.search(r"SCORE:\s*(\d+)", eval_response)
        passed_match = re.search(r"PASSED:\s*(TRUE|FALSE)", eval_response, re.IGNORECASE)
        rationale_match = re.search(r"RATIONALE:\s*(.*)", eval_response)

        score = int(score_match.group(1)) if score_match else 0
        passed = (passed_match.group(1).upper() == "TRUE") if passed_match else False
        rationale = rationale_match.group(1) if rationale_match else "Evaluation standard dropped."
    except Exception:
        score, passed, rationale = 0, False, "Grading system timeout exception."

    report = {
        "question_asked": last_ai_message[:150] + "...",
        "student_answer": last_human_message,
        "score_percentage": score,
        "passed_gate": passed,
        "evaluation_rationale": rationale
    }

    new_index = curr_idx
    updated_profile = state["student_profile"]

    # If the student fails, trigger Phase 4 Weakness Extraction and update the profile state
    if passed and curr_idx < len(agenda) - 1:
        new_index += 1
    elif not passed:
        analytics_result = extract_and_update_weaknesses({
            "student_profile": state["student_profile"],
            "active_assessment": report
        })
        if analytics_result and "student_profile" in analytics_result:
            updated_profile = analytics_result["student_profile"]

    return {
        "active_assessment": report,
        "current_topic_index": new_index,
        "student_profile": updated_profile,
        "next_action": "advance_topic" if passed else "remediate_doubt"
    }


# ── Routing Maps ──────────────────────────────────────────────────────────────
def route_start(state: TutorState) -> str:
    if state.get("current_work") and state["current_work"].get("image_url"):
        return "work_checker"
    return "dialogue_manager"


# ── Graph Synthesis ───────────────────────────────────────────────────────────
workflow = StateGraph(TutorState)
workflow.add_node("work_checker", work_checker_node)
workflow.add_node("dialogue_manager", dialogue_manager_node)
workflow.add_node("assessment_node", assessment_node)

workflow.add_conditional_edges(START, route_start)
workflow.add_conditional_edges(
    "work_checker",
    lambda state: state["next_action"],
    {"route_to_hint": "dialogue_manager", "route_to_dialogue": "dialogue_manager"}
)
workflow.add_edge("dialogue_manager", "assessment_node")
workflow.add_edge("assessment_node", END)

_db_conn = sqlite3.connect("jini_memory.db", check_same_thread=False)
memory = SqliteSaver(_db_conn)

ai_tutor_app = workflow.compile(checkpointer=memory)