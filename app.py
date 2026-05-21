import os
import re
import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from agent import ai_tutor_app, get_youtube_style_profile
from auth_manager import register_user, verify_user

st.set_page_config(page_title="Jini AI Classroom", page_icon="🎓", layout="wide")

# ==========================================
# 🔐 INITIAL STATE & SECURITY CORE SETUP
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4().hex[:8]}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "grade_level" not in st.session_state:
    st.session_state.grade_level = "B.Tech AI Prep"
if "learning_pace" not in st.session_state:
    st.session_state.learning_pace = "Conceptual & Deep-Dive"
if "strengths" not in st.session_state:
    st.session_state.strengths = "Python basic syntax"
if "weaknesses" not in st.session_state:
    st.session_state.weaknesses = "None recorded yet"
if "current_topic_index" not in st.session_state:
    st.session_state.current_topic_index = 0
if "teaching_style" not in st.session_state:
    st.session_state.teaching_style = "Standard concise, direct engineering tutorial voice."
if "current_work" not in st.session_state:
    st.session_state.current_work = None
if "agenda" not in st.session_state:
    st.session_state.agenda = [
        "1. Core Purpose of Try-Except blocks",
        "2. Handling Specific Errors (ZeroDivisionError)",
        "3. Managing Missing Files (FileNotFoundError)",
        "4. Executing File Writing Streams ('w' mode)"
    ]

# ==========================================
# 🔐 ENTERPRISE AUTHENTICATION GATEWAY
# ==========================================
if not st.session_state.authenticated:
    st.title("🎓 Jini AI Enterprise Portal")
    st.caption("Secure Multi-User Student Sign-In Gateway")

    tabs = st.tabs(["🔐 Sign In", "📝 Create Account"])

    with tabs[0]:
        st.subheader("Login to your Classroom Thread")
        login_user = st.text_input("Username:", key="login_user_key").strip()
        login_pass = st.text_input("Password:", type="password", key="login_pass_key")

        if st.button("🚀 Enter Sandbox", use_container_width=True):
            profile = verify_user(login_user, login_pass)
            if profile:
                st.session_state.authenticated = True
                st.session_state.session_id = f"user_{profile['username']}"
                st.session_state.user_name = str(profile['username']).capitalize()
                st.session_state.grade_level = str(profile['grade_level'])
                st.session_state.learning_pace = str(profile['learning_pace'])
                st.session_state.strengths = str(profile['strengths'])
                st.session_state.weaknesses = str(profile['weaknesses'])
                st.session_state.messages = [{
                    "role": "assistant",
                    "content": f"🤖 **Jini:** Secure connection established! Welcome, **{st.session_state.user_name}**. Your personal history profile and background checkpointer are fully synched. What subject are we mastering today?",
                    "is_system_message": True
                }]
                st.success("Access Granted! Syncing state engine layers...")
                st.rerun()
            else:
                st.error("Invalid username signature or password mapping match failed.")

    with tabs[1]:
        st.subheader("Register a New Student Account Profile")
        reg_user = st.text_input("Choose Username:", key="reg_user_key").strip()
        reg_pass = st.text_input("Create Password:", type="password", key="reg_pass_key")
        reg_grade = st.selectbox("Your Academic Level:",
                                 ["High School", "B.Tech AI Prep", "Working Professional", "Hobbyist"],
                                 key="reg_grade_key", index=1)
        reg_pace = st.selectbox("Learning Speed Preference:",
                                ["Conceptual & Deep-Dive", "Fast-Track / Bootcamp", "Step-by-Step Patient"],
                                key="reg_pace_key")
        reg_str = st.text_input("Current Core Strengths:", value="Python syntax fundamentals", key="reg_str_key")
        reg_weak = st.text_input("Current Known Gaps:", value="None recorded yet", key="reg_weak_key")

        if st.button("💾 Initialize Profile Account", use_container_width=True):
            if reg_user and reg_pass:
                if register_user(reg_user, reg_pass, reg_grade, reg_pace, reg_str, reg_weak):
                    st.success(
                        "Account created successfully! Jump over to the 'Sign In' tab to initialize your session.")
                else:
                    st.error("Registration rejected. That username is already claimed inside users.db.")
            else:
                st.warning("Please fill out username and password configurations.")

    st.stop()

# ==========================================
# 📊 SIDEBAR CONTROL PANEL (POST-AUTH)
# ==========================================
with st.sidebar:
    st.title("⚙️ Classroom Controls")
    st.caption(f"👤 Account: **{st.session_state.user_name}**")
    st.caption(f"🆔 Active Thread: `{st.session_state.session_id}`")
    st.markdown("---")

    # Logged-in Metadata Overview Container
    st.subheader("📋 Student Metadata")
    st.markdown(f"**Level:** `{st.session_state.grade_level}`")
    st.markdown(f"**Pace:** `{st.session_state.learning_pace}`")

    if st.button("🚪 Logout Account", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.session_state.user_name = ""
        st.rerun()

    # ── Phase 4 Diagnostics Dashboard Container with Bar Chart ──
    st.markdown("---")
    st.subheader("📊 Phase 4 AI Diagnostics")
    if st.session_state.user_name:
        total_topics = len(st.session_state.agenda)
        completed_topics = st.session_state.current_topic_index
        remaining_topics = max(0, total_topics - completed_topics)

        chart_data = {
            "Status": ["Completed", "Remaining"],
            "Count": [completed_topics, remaining_topics]
        }
        st.bar_chart(data=chart_data, x="Status", y="Count", color="#4285F4", height=140)

        if st.session_state.weaknesses and st.session_state.weaknesses != "None recorded yet":
            st.info("🎯 **Active Conceptual Blindspots:**")
            active_gaps = [w.strip() for w in str(st.session_state.weaknesses).split(",") if w.strip()]
            for idx, gap in enumerate(active_gaps):
                st.markdown(f"🚨 *Diagnostic {idx + 1}:* `{gap}`")
        else:
            st.caption("No real-time diagnostic flags logged yet.")

    st.markdown("---")

    # ── Agenda Management Layout ──
    st.subheader("📚 Curriculum Management")
    agenda_text = st.text_area("Topics (one per line):", value="\n".join(st.session_state.agenda), height=110)
    if st.button("✅ Force Reload Curriculum", use_container_width=True):
        new_agenda = [t.strip() for t in agenda_text.split("\n") if t.strip()]
        if new_agenda:
            st.session_state.agenda = new_agenda
            st.session_state.current_topic_index = 0
            st.success("Syllabus configuration updated!")
            st.rerun()

    st.markdown("---")

    # ── Voice Clone Interface ──
    st.subheader("🎭 Clone Lecturer Persona")
    yt_input = st.text_input("YouTube Link Input:")
    if st.button("🔬 Ingest Persona Voice", use_container_width=True) and yt_input:
        with st.spinner("Analyzing audio-text semantic structures..."):
            st.session_state.teaching_style = get_youtube_style_profile(
                [u.strip() for u in yt_input.split(",") if u.strip()])
            st.success("Linguistic voice vectors applied!")

    st.markdown("---")

    # ── Vision Handling Interface with Type Guards ──
    st.subheader("📸 Assignment Snapshot Upload")
    uploaded_image = st.file_uploader("Drop code screen screenshot:", type=["png", "jpg", "jpeg"])

    if uploaded_image is not None and not isinstance(uploaded_image, list):
        expected_path = f"temp_{st.session_state.session_id}_{uploaded_image.name}"
        if st.session_state.current_work is None or st.session_state.current_work.get("image_url") != expected_path:
            with open(expected_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
            st.session_state.current_work = {
                "image_url": expected_path, "extracted_text": None,
                "is_correct": False, "conceptual_flaw_detected": None, "suggested_hint": None
            }
            st.toast("Vision input stacked for evaluation turn.")

    if st.session_state.current_work:
        if st.button("🗑️ Wipe Active Image Trace", use_container_width=True):
            path = st.session_state.current_work.get("image_url", "")
            if path and os.path.exists(path):
                os.remove(path)
            st.session_state.current_work = None
            st.rerun()

    st.markdown("---")

    # ── Real-Time Progress Mapping Readout ──
    st.subheader("📋 Core Syllabus Tracking")
    for idx, topic in enumerate(st.session_state.agenda):
        if idx == st.session_state.current_topic_index:
            st.markdown(f"👉 **{topic}** *(Active)*")
        elif idx < st.session_state.current_topic_index:
            st.markdown(f"✅ ~~{topic}~~")
        else:
            st.markdown(f"⏳ {topic}")

    st.progress((st.session_state.current_topic_index + 1) / len(st.session_state.agenda))

# ==========================================
# 💬 MAIN INTERACTIVE CONVERSATION SCREEN
# ==========================================
st.title("🎓 Jini AI Classroom")
st.caption(f"⚡ Active Cloned Persona Instruction Matrix: *\"{st.session_state.teaching_style[:85]}...\"*")
st.markdown("---")

if st.session_state.messages:
    export_md = f"# 🎓 Jini Classroom Session Log\n\n" + "\n\n".join(
        f"**{m['role'].upper()}:** {m['content']}" for m in st.session_state.messages)
    st.download_button(label="📥 Export Complete Session Markdown (.md)", data=export_md,
                       file_name=f"jini_{st.session_state.session_id}.md", mime="text/markdown")
    st.markdown("---")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if student_input := st.chat_input("Submit response or puzzle solution..."):
    with st.chat_message("user"):
        st.markdown(student_input)
    st.session_state.messages.append({"role": "user", "content": student_input})

    input_payload = {
        "messages": [HumanMessage(content=str(student_input))],
        "student_profile": {
            "student_id": st.session_state.session_id, "student_name": st.session_state.user_name,
            "current_grade_level": st.session_state.grade_level, "learning_pace": st.session_state.learning_pace,
            "strengths": [s.strip() for s in str(st.session_state.strengths).split(",") if s.strip()],
            "weaknesses": [w.strip() for w in str(st.session_state.weaknesses).split(",") if w.strip()]
        },
        "current_work": st.session_state.current_work,
        "current_lesson_plan": st.session_state.agenda,
        "current_topic_index": st.session_state.current_topic_index,
        "teaching_style_guide": st.session_state.teaching_style,
        "next_action": "route_to_dialogue"
    }

    with st.chat_message("assistant"):
        try:
            config = {"configurable": {"thread_id": st.session_state.session_id}}
            full_text_buffer = []


            def response_generator():
                pending = ""
                for message_chunk, metadata in ai_tutor_app.stream(input_payload, config=config,
                                                                   stream_mode="messages"):
                    if metadata.get("langgraph_node") == "dialogue_manager" and hasattr(message_chunk,
                                                                                        "content") and message_chunk.content:
                        full_text_buffer.append(message_chunk.content)
                        pending += message_chunk.content

                        # Filter custom orchestration layout routing tags without redundant escapes
                        pending, _ = re.subn(r'\[INTENT:\s*(DOUBT|NEXT)]', '', pending)

                        if len(pending) > 30:
                            yield pending
                            pending = ""
                if pending:
                    yield pending


            final_reply = st.write_stream(response_generator)

            if final_reply:
                st.session_state.messages.append({"role": "assistant", "content": final_reply})

                # ── State Sync Execution Phase ──
                updated = ai_tutor_app.get_state(config)
                if updated and updated.values:
                    state_vals = updated.values

                    # Phase 4 Dashboard Weakness Extraction Sync
                    if state_vals.get("student_profile"):
                        graph_prof = state_vals["student_profile"]
                        if graph_prof.get("weaknesses"):
                            st.session_state.weaknesses = ", ".join(graph_prof["weaknesses"])

                    # Phase 3 Assessment Gate Sync Container Visualization
                    if state_vals.get("active_assessment"):
                        report = state_vals["active_assessment"]
                        with st.expander("📊 Structural Assessment Verification Board", expanded=True):
                            if report["passed_gate"]:
                                st.success(f"🎯 **Score: {report['score_percentage']}%** — Conceptual Gate Unlocked!")
                                st.markdown(f"*{report['evaluation_rationale']}*")
                            else:
                                st.error(f"🛑 **Score: {report['score_percentage']}%** — Review Threshold Not Met.")
                                st.info(f"📝 **Grader Diagnostic Note:** {report['evaluation_rationale']}")

                    # Phase 3 Syllabus Index Layout Position Sync
                    if "current_topic_index" in state_vals:
                        old_idx = st.session_state.current_topic_index
                        st.session_state.current_topic_index = state_vals["current_topic_index"]

                        if state_vals.get("current_lesson_plan"):
                            st.session_state.agenda = state_vals["current_lesson_plan"]

                        if st.session_state.current_topic_index > old_idx:
                            st.toast(f"🚀 Advanced to: {st.session_state.agenda[st.session_state.current_topic_index]}")

                    # Multi-Turn Vision Processing Verification Loop
                    if state_vals.get("current_work"):
                        st.session_state.current_work = state_vals["current_work"]
                        cw = st.session_state.current_work
                        if cw.get("extracted_text") and cw["extracted_text"] != "Vision sync failed.":
                            with st.expander("📋 Assignment Layout Extracted Data", expanded=False):
                                st.markdown(cw["extracted_text"])

            st.rerun()

        except Exception as e:
            # Perfectly aligned internal exception handler layout blocks
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                st.error(
                    "🛑 **Google API 429 Limit Breached.** Let things settle down for 60 seconds before sending another message.")
            else:
                st.error(f"⚠️ Pipeline execution error: {e}")