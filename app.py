import streamlit as st
import pandas as pd
from langchain_core.messages import HumanMessage, AssistantMessage
from auth_manager import init_auth_db, register_user, verify_user
from agent import ai_tutor_app

# 1. Initialize Database Foundations
init_auth_db()
st.set_page_config(page_title="Jini AI Classroom", layout="wide")

# FIX 2: Progress Bar Color Overrides
st.markdown("""
<style>
div[data-testid="stProgressBar"] > div > div > div { background-color: #00c853 !important; }
div[data-testid="stProgressBar"] > div > div { background-color: #2a2a2a !important; }
</style>
""", unsafe_allow_html=True)

# 2. Gatekeeper Identity Authentication Matrix
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

if not st.session_state.authenticated:
    st.title("🛡️ Jini Secure Gateway Login")
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])

    with tab1:
        u1 = st.text_input("Username:", key="u1")
        p1 = st.text_input("Password:", type="password", key="p1")
        if st.button("Access Dashboard"):
            if verify_user(u1, p1):
                st.session_state.authenticated = True
                st.session_state.username = u1.strip().lower()
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab2:
        u2 = st.text_input("Choose Username:", key="u2")
        p2 = st.text_input("Choose Secure Password:", type="password", key="p2")
        if st.button("Register Workspace"):
            if register_user(u2, p2):
                st.success("Registration successful! Proceed to Sign In.")
            else:
                st.error("Username taken or missing values.")
    st.stop()

# 3. Synchronize Active Multi-User Thread Coordinates
user = st.session_state.username
config = {"configurable": {"thread_id": f"session_thread_{user}"}}

# FIX 10: StateSnapshot check syntax routing correction
state_snapshot = ai_tutor_app.get_state(config)
if not state_snapshot.values.get("messages"):
    initial_profile = {
        "user_id": user,
        "username": user,
        "agenda": ["Introduction to Python Logic", "Control Flow Structures", "Function Blocks", "Algorithmic Loops"],
        "current_topic_index": 0,
        "comprehension_score": 0,
        "messages": [AssistantMessage(
            content=f"Welcome back, Developer {user}. I have initialized your custom curriculum workspace. Let's begin.")]
    }
    ai_tutor_app.update_state(config, initial_profile)
    state_snapshot = ai_tutor_app.get_state(config)

# Hydrate metrics out from snapshot core
graph_data = state_snapshot.values
agenda = graph_data["agenda"]
curr_idx = graph_data["current_topic_index"]
score = graph_data.get("comprehension_score", 0)

# 4. Standard Collapsible Sidebar UI Layout Container
with st.sidebar:
    st.header("📊 Student Analytics")
    st.metric(label="Active Workspace", value=user)
    st.metric(label="Comprehension Rating", value=f"{score} / 100")

    # Progress Calculation Display
    total_topics = len(agenda)
    progress_val = float(curr_idx / total_topics) if total_topics > 0 else 0.0
    st.progress(min(max(progress_val, 0.0), 1.0))
    st.caption(f"Topic Focus: {curr_idx + 1} of {total_topics}")

    # FIX 5: Dynamic Diagnostics Chart Data Source Calculation
    completed = curr_idx
    remaining = max(0, total_topics - completed - 1)

    chart_df = pd.DataFrame({
        "Status": ["Completed", "Remaining"],
        "Count": [completed, remaining]
    })
    st.bar_chart(chart_df.set_index("Status"))

    st.subheader("📚 Learning Syllabus")
    for idx, topic in enumerate(agenda):
        if idx < curr_idx:
            st.markdown(f"✅ ~~{topic}~~")
        elif idx == curr_idx:
            st.markdown(f"👉 **{topic}**")
        else:
            st.markdown(f"⏳ {topic}")

    if st.button("Secure Logout"):
        st.session_state.authenticated = False
        st.session_state.clear()
        st.rerun()

# 5. Primary Classroom Chat Interface Viewport
st.header("🤖 Interacting with Jini Classroom Engine")

for msg in graph_data["messages"]:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# FIX 1: Native JavaScript Auto-Scroll Engine Escape
st.markdown("""
    <script>
        const chatContainer = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
        if (chatContainer) { chatContainer.scrollTop = chatContainer.scrollHeight; }
    </script>
    """, unsafe_allow_html=True)

# Process active chat turn execution payloads
if prompt := st.chat_input("Engage with your tutor here...", key="chat_user_input"):
    with st.chat_message("user"):
        st.markdown(prompt)

    # FIX 6: Pass exact payload map to invoke parameter layers cleanly
    output_state = ai_tutor_app.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config
    )

    # Issue 8 Resolved: Inspect intent token in app view loop after response finishes compiling
    last_response_text = output_state["messages"][-1].content
    if "[INTENT: NEXT]" in last_response_text and curr_idx < len(agenda) - 1:
        next_idx = curr_idx + 1
        ai_tutor_app.update_state(config, {"current_topic_index": next_idx})
        st.toast(f"✅ Advancing syllabus focus to: {agenda[next_idx]}")

    st.rerun()