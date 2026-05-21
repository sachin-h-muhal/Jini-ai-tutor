import os
import sqlite3
from typing import List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from tutor_state import TutorState

# 1. Structural Configuration Foundations & SQLite Connection Fix
MEMORY_DB = "jini_memory.db"
_conn = sqlite3.connect(MEMORY_DB, check_same_thread=False)
memory_checkpointer = SqliteSaver(_conn)

# Module-level client initialization — efficient API reuse
api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    streaming=True
)


# 2. Core Processing Nodes
def teach_node(state: TutorState) -> dict:
    """Delivers content lectures and guides the student conversationally."""
    curr_topic = state["agenda"][state["current_topic_index"]]

    system_prompt = (
        f"You are Jini, an expert conversational AI Tutor. Teach the current topic: '{curr_topic}'.\n"
        f"Guidelines: Keep things highly interactive. If the student demonstrates a complete grasp of the material, "
        f"append '[INTENT: NEXT]' onto a brand new line at the very end of your explanation."
    )

    messages_payload = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages_payload)
    return {"messages": [response]}


def vision_node(state: TutorState) -> dict:
    """Processes images and homework snapshots uploaded by the user."""
    system_prompt = (
        "You are Jini's Vision Matrix Engine. Review the image attachment provided by the student. "
        "Analyze any code handwriting or layout structures, highlight conceptual mistakes, and provide guidance."
    )
    messages_payload = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages_payload)
    return {"messages": [response]}


def evaluation_node(state: TutorState) -> dict:
    """Calculates conceptual comprehension scores objectively from user updates."""
    user_inputs = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    if not user_inputs:
        return {"comprehension_score": 0}

    last_user_msg = user_inputs[-1].content

    eval_prompt = (
        f"Analyze this student response: '{last_user_msg}'.\n"
        f"Rate their conceptual understanding of the topic from 0 to 100.\n"
        f"Output ONLY a single integer score value between 0 and 100. Do not write markdown or prose."
    )

    response = llm.invoke([SystemMessage(content=eval_prompt)])
    try:
        score = int(response.content.strip())
    except ValueError:
        score = 75  # Clean structural fallback

    return {"comprehension_score": score}


# 3. Non-Cyclical Conditional Edge Routing Framework
def route_after_input(state: TutorState) -> str:
    """Determines whether to execute vision processing or analytics tracking."""
    last_msg = state["messages"][-1]

    # Route to vision node if an image attachment payload structure exists
    if hasattr(last_msg, "additional_kwargs") and "image_data" in last_msg.additional_kwargs:
        return "vision_node"
    return "evaluation_node"


def route_after_eval(state: TutorState) -> str:
    """Exits the graph single-turn loop cleanly back to the user view container."""
    return "__end__"


# 4. Building the Complete Multi-Node State Machine
workflow = StateGraph(TutorState)

workflow.add_node("teach_node", teach_node)
workflow.add_node("vision_node", vision_node)
workflow.add_node("evaluation_node", evaluation_node)

workflow.set_entry_point("teach_node")

# Conditional edges mapped strictly without looping cycles
workflow.add_conditional_edges("teach_node", route_after_input, {
    "vision_node": "vision_node",
    "evaluation_node": "evaluation_node"
})
workflow.add_conditional_edges("evaluation_node", route_after_eval, {
    "__end__": END
})
workflow.add_edge("vision_node", END)

ai_tutor_app = workflow.compile(checkpointer=memory_checkpointer)