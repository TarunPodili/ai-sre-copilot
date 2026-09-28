# import os

# import streamlit as st
# from dotenv import load_dotenv
# from google import genai

# from analyzer import parse_logs
# from rag import (
#     search_knowledge,
#     search_similar_incidents
# )
# from llm import investigate_incident


# # ============================================================
# # CONFIGURATION
# # ============================================================

# load_dotenv()

# st.set_page_config(
#     page_title="AI SRE Copilot",
#     page_icon="🤖",
#     layout="wide"
# )


# # ============================================================
# # GEMINI CLIENT
# # ============================================================

# api_key = os.getenv("GEMINI_API_KEY")

# if not api_key:
#     st.error("GEMINI_API_KEY not found in .env")
#     st.stop()

# client = genai.Client(
#     api_key=api_key
# )


# # ============================================================
# # PAGE HEADER
# # ============================================================

# st.title("🤖 AI SRE Copilot")

# st.caption(
#     "Evidence-Grounded Deployment Incident Investigator"
# )


# # ============================================================
# # SESSION STATE
# # ============================================================

# if "incident" not in st.session_state:
#     st.session_state.incident = None

# if "knowledge" not in st.session_state:
#     st.session_state.knowledge = []

# if "similar_incidents" not in st.session_state:
#     st.session_state.similar_incidents = []

# if "result" not in st.session_state:
#     st.session_state.result = None

# if "messages" not in st.session_state:
#     st.session_state.messages = []


# # ============================================================
# # SIDEBAR - INCIDENT INPUT
# # ============================================================

# with st.sidebar:

#     st.header("📥 Incident Input")

#     uploaded_file = st.file_uploader(
#         "Upload deployment log",
#         type=["log", "txt"]
#     )

#     st.write("Or paste deployment logs below.")

#     log_text = st.text_area(
#         "Deployment Logs",
#         height=300,
#         placeholder="""2026-09-27 10:30:01 INFO Deployment started
# 2026-09-27 10:30:05 INFO Pod payment-api created
# 2026-09-27 10:30:08 ERROR Failed to pull image payment-api:v1.8
# 2026-09-27 10:30:09 ERROR ImagePullBackOff
# 2026-09-27 10:30:12 ERROR Deployment failed"""
#     )

#     if uploaded_file:

#         log_text = uploaded_file.read().decode(
#             "utf-8"
#         )

#     investigate_button = st.button(
#         "🔍 Investigate Incident",
#         use_container_width=True
#     )


# # ============================================================
# # INCIDENT INVESTIGATION
# # ============================================================

# if investigate_button:

#     if not log_text.strip():

#         st.warning(
#             "Please provide deployment logs first."
#         )

#     else:

#         with st.spinner(
#             "🔎 Investigating deployment incident..."
#         ):

#             # ------------------------------------------------
#             # 1. Parse logs
#             # ------------------------------------------------

#             incident = parse_logs(
#                 log_text
#             )


#             # ------------------------------------------------
#             # 2. Build RAG query
#             # ------------------------------------------------

#             query = "\n".join(
#                 incident["errors"]
#             )

#             if not query.strip():

#                 query = log_text


#             # ------------------------------------------------
#             # 3. Search troubleshooting knowledge
#             # ------------------------------------------------

#             knowledge = search_knowledge(
#                 query,
#                 top_k=3
#             )


#             # ------------------------------------------------
#             # 4. Search historical incidents
#             # ------------------------------------------------

#             similar_incidents = search_similar_incidents(
#                 query,
#                 top_k=3
#             )


#             # ------------------------------------------------
#             # 5. Gemini investigation
#             # ------------------------------------------------

#             result = investigate_incident(
#                 incident,
#                 knowledge,
#                 similar_incidents
#             )


#             # ------------------------------------------------
#             # 6. Save results
#             # ------------------------------------------------

#             st.session_state.incident = incident

#             st.session_state.knowledge = knowledge

#             st.session_state.similar_incidents = (
#                 similar_incidents
#             )

#             st.session_state.result = result


#             # ------------------------------------------------
#             # 7. Reset chatbot
#             # ------------------------------------------------

#             st.session_state.messages = []


#         st.success(
#             "✅ Investigation completed."
#         )


# # ============================================================
# # RCA DASHBOARD
# # ============================================================

# if st.session_state.result:

#     result = st.session_state.result

#     st.divider()

#     st.header(
#         "🚨 Incident Investigation"
#     )


#     # ========================================================
#     # TOP METRICS
#     # ========================================================

#     col1, col2, col3 = st.columns(3)


#     with col1:

#         st.metric(
#             "Severity",
#             result.get(
#                 "severity",
#                 "UNKNOWN"
#             )
#         )


#     with col2:

#         st.metric(
#             "Confidence",
#             f"{result.get('confidence', 0)}%"
#         )


#     with col3:

#         st.metric(
#             "Errors",
#             st.session_state.incident.get(
#                 "error_count",
#                 0
#             )
#         )


#     # ========================================================
#     # SUMMARY
#     # ========================================================

#     st.subheader(
#         "📋 Summary"
#     )

#     st.write(
#         result.get(
#             "summary",
#             "No summary available."
#         )
#     )


#     # ========================================================
#     # PRIMARY HYPOTHESIS
#     # ========================================================

#     st.subheader(
#         "🎯 Primary Hypothesis"
#     )

#     st.info(
#         result.get(
#             "primary_hypothesis",
#             "No hypothesis available."
#         )
#     )


#     # ========================================================
#     # EVIDENCE
#     # ========================================================

#     st.subheader(
#         "🔎 Evidence"
#     )

#     evidence = result.get(
#         "evidence",
#         []
#     )

#     if evidence:

#         for item in evidence:

#             st.write(
#                 f"• {item}"
#             )

#     else:

#         st.write(
#             "No evidence identified."
#         )


#     # ========================================================
#     # ALTERNATIVE CAUSES
#     # ========================================================

#     st.subheader(
#         "🔀 Alternative Causes"
#     )

#     alternatives = result.get(
#         "alternative_causes",
#         []
#     )

#     if alternatives:

#         for item in alternatives:

#             st.write(
#                 f"• {item}"
#             )

#     else:

#         st.write(
#             "No alternative causes identified."
#         )


#     # ========================================================
#     # IMPACT
#     # ========================================================

#     st.subheader(
#         "💥 Impact"
#     )

#     st.write(
#         result.get(
#             "impact",
#             "No impact information available."
#         )
#     )


#     # ========================================================
#     # ACTIONS
#     # ========================================================

#     col1, col2 = st.columns(2)


#     with col1:

#         st.subheader(
#             "⚡ Immediate Action"
#         )

#         st.write(
#             result.get(
#                 "immediate_action",
#                 "No immediate action provided."
#             )
#         )


#     with col2:

#         st.subheader(
#             "🔧 Permanent Fix"
#         )

#         st.write(
#             result.get(
#                 "permanent_fix",
#                 "No permanent fix provided."
#             )
#         )


#     # ========================================================
#     # PREVENTION
#     # ========================================================

#     st.subheader(
#         "🛡️ Prevention"
#     )

#     st.write(
#         result.get(
#             "prevention",
#             "No prevention recommendation provided."
#         )
#     )


#     # ========================================================
#     # MISSING EVIDENCE
#     # ========================================================

#     missing = result.get(
#         "missing_evidence",
#         []
#     )

#     if missing:

#         st.subheader(
#             "🕵️ Additional Evidence Required"
#         )

#         for item in missing:

#             st.warning(
#                 item
#             )


#     # ========================================================
#     # TROUBLESHOOTING KNOWLEDGE
#     # ========================================================

#     st.divider()

#     with st.expander(
#         "📚 Retrieved Troubleshooting Knowledge"
#     ):

#         for item in st.session_state.knowledge:

#             st.markdown(
#                 f"### {item['source']}"
#             )

#             st.caption(
#                 f"Semantic similarity: "
#                 f"{item['score']:.3f}"
#             )


#     # ========================================================
#     # HISTORICAL INCIDENTS
#     # ========================================================

#     st.subheader(
#         "🧠 Similar Historical Incidents"
#     )

#     if st.session_state.similar_incidents:

#         for incident in (
#             st.session_state.similar_incidents
#         ):

#             with st.expander(
#                 f"{incident['source']} — "
#                 f"{incident['score']:.1%} similarity"
#             ):

#                 st.markdown(
#                     incident["content"]
#                 )

#     else:

#         st.info(
#             "No similar historical incidents found."
#         )


#     # ========================================================
#     # INTERACTIVE INVESTIGATION CHATBOT
#     # ========================================================

#     st.divider()

#     st.header(
#         "💬 Investigate Further"
#     )

#     st.caption(
#         "Ask follow-up questions about the current incident."
#     )


#     # --------------------------------------------------------
#     # Display chat history
#     # --------------------------------------------------------

#     for message in st.session_state.messages:

#         with st.chat_message(
#             message["role"]
#         ):

#             st.write(
#                 message["content"]
#             )


#     # --------------------------------------------------------
#     # Chat input
#     # --------------------------------------------------------

#     question = st.chat_input(
#         "Ask about this incident..."
#     )


#     if question:

#         # ====================================================
#         # USER MESSAGE
#         # ====================================================

#         st.session_state.messages.append(
#             {
#                 "role": "user",
#                 "content": question
#             }
#         )


#         with st.chat_message(
#             "user"
#         ):

#             st.write(
#                 question
#             )


#         # ====================================================
#         # BUILD CHAT CONTEXT
#         # ====================================================

#         context = f"""

# ========================
# CURRENT INCIDENT
# ========================

# {st.session_state.incident}


# ========================
# AI INVESTIGATION
# ========================

# {st.session_state.result}


# ========================
# TROUBLESHOOTING KNOWLEDGE
# ========================

# {st.session_state.knowledge}


# ========================
# SIMILAR HISTORICAL INCIDENTS
# ========================

# {st.session_state.similar_incidents}


# ========================
# USER QUESTION
# ========================

# {question}

# """


#         # ====================================================
#         # ASK GEMINI
#         # ====================================================

#         with st.chat_message(
#             "assistant"
#         ):

#             with st.spinner(
#                 "🧠 Investigating..."
#             ):

#                 response = client.models.generate_content(

#                     model="gemini-3.5-flash-lite",

#                     contents=f"""

# You are an SRE troubleshooting assistant.

# Your job is to help investigate the CURRENT
# deployment incident.

# Use:

# 1. Current incident data
# 2. AI investigation
# 3. Troubleshooting knowledge
# 4. Similar historical incidents

# IMPORTANT:

# The CURRENT INCIDENT is the primary source
# of truth.

# Historical incidents are supporting evidence only.

# Do NOT assume that a historical incident has
# the same root cause as the current incident.

# Do not invent evidence.

# If the available evidence is insufficient,
# clearly say so.

# When appropriate:

# - Explain why a cause is likely.
# - Explain alternative causes.
# - Identify missing evidence.
# - Recommend diagnostic commands.
# - Explain how to distinguish between possible causes.
# - Reference similar historical incidents when useful.

# {context}

# """

#                 )

#                 answer = response.text


#                 # ------------------------------------------------
#                 # Display answer
#                 # ------------------------------------------------

#                 st.write(
#                     answer
#                 )


#         # ====================================================
#         # SAVE ASSISTANT MESSAGE
#         # ====================================================

#         st.session_state.messages.append(
#             {
#                 "role": "assistant",
#                 "content": answer
#             }
#         )

import uuid
import streamlit as st

from langgraph.types import Command

from analyzer import parse_logs
from graph import incident_graph


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI SRE Copilot",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "started" not in st.session_state:
    st.session_state.started = False

if "waiting_for_evidence" not in st.session_state:
    st.session_state.waiting_for_evidence = False

if "final_result" not in st.session_state:
    st.session_state.final_result = None

if "current_interrupt" not in st.session_state:
    st.session_state.current_interrupt = None


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ AI SRE Copilot")

st.caption(
    "Evidence-Grounded Deployment Incident Investigator"
)

st.markdown(
    """
AI-assisted incident investigation using:

**Log Analysis → RAG → Historical Incidents → Gemini → "
"Evidence Evaluation → Human-in-the-Loop → RCA**
"""
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Investigation")

    if st.button(
        "🆕 New Investigation",
        use_container_width=True
    ):
        st.session_state.thread_id = None
        st.session_state.started = False
        st.session_state.waiting_for_evidence = False
        st.session_state.final_result = None
        st.session_state.current_interrupt = None

        st.rerun()

    st.divider()

    st.markdown("### Architecture")

    st.markdown(
        """
        📝 Deployment Logs  
        ↓  
        🔎 Log Analyzer  
        ↓  
        📚 Knowledge RAG  
        ↓  
        🧠 Historical Incident RAG  
        ↓  
        🤖 Gemini Investigation  
        ↓  
        📊 Evidence Evaluation  
        ↓  
        👨‍💻 Human Evidence  
        ↓  
        🧾 Final RCA
        """
    )

    st.divider()

    st.caption(
        "AI SRE Copilot v1.0"
    )


# ============================================================
# LOG INPUT
# ============================================================

st.header("1️⃣ Incident Input")

uploaded_file = st.file_uploader(
    "Upload deployment log",
    type=["log", "txt"]
)

log_text = st.text_area(
    "Or paste deployment logs",
    height=250,
    placeholder="""2026-09-28 11:20:01 INFO Deployment started
2026-09-28 11:20:15 INFO Loading recommendation model
2026-09-28 11:20:32 INFO Loading model weights: 1.8 GB
2026-09-28 11:20:45 WARN Memory usage exceeded 80 percent
2026-09-28 11:20:54 ERROR Reason: OOMKilled
"""
)


# ============================================================
# HANDLE FILE
# ============================================================

if uploaded_file is not None:

    uploaded_content = uploaded_file.read()

    try:
        log_text = uploaded_content.decode("utf-8")
    except UnicodeDecodeError:
        log_text = uploaded_content.decode(
            "latin-1"
        )

    st.success(
        f"Loaded `{uploaded_file.name}`"
    )


# ============================================================
# START INVESTIGATION
# ============================================================

st.header("2️⃣ Start Investigation")

start_button = st.button(
    "🚀 Investigate Incident",
    type="primary",
    use_container_width=True
)


if start_button:

    if not log_text.strip():

        st.error(
            "Please upload or paste deployment logs."
        )

    else:

        # Create a completely new investigation thread.
        thread_id = str(
            uuid.uuid4()
        )

        st.session_state.thread_id = thread_id
        st.session_state.started = True
        st.session_state.final_result = None
        st.session_state.waiting_for_evidence = False
        st.session_state.current_interrupt = None

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        initial_state = {
            "logs": log_text,
            "diagnostic_results": "",
            "investigation_round": 0
        }

        with st.spinner(
            "AI SRE Copilot is investigating..."
        ):

            try:

                result = incident_graph.invoke(
                    initial_state,
                    config=config
                )

                st.session_state.current_interrupt = (
                    result.get("__interrupt__")
                )

                if st.session_state.current_interrupt:

                    st.session_state.waiting_for_evidence = True

                else:

                    st.session_state.final_result = result

            except Exception as error:

                st.error(
                    f"Investigation failed: {error}"
                )


# ============================================================
# HUMAN-IN-THE-LOOP SECTION
# ============================================================

if st.session_state.waiting_for_evidence:

    st.divider()

    st.header(
        "👨‍💻 Engineer Action Required"
    )

    st.warning(
        "The AI needs additional evidence before "
        "it can confidently determine the root cause."
    )

    # --------------------------------------------------------
    # Retrieve current graph state
    # --------------------------------------------------------

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    try:

        graph_state = incident_graph.get_state(
            config
        )

        state_values = graph_state.values

    except Exception as error:

        state_values = {}

        st.error(
            f"Unable to read investigation state: {error}"
        )


    # --------------------------------------------------------
    # Current Investigation
    # --------------------------------------------------------

    investigation = state_values.get(
        "investigation",
        {}
    )

    if investigation:

        st.subheader(
            "Current AI Assessment"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Confidence",
                f"{investigation.get('confidence', 0)}%"
            )

        with col2:

            st.metric(
                "Severity",
                investigation.get(
                    "severity",
                    "UNKNOWN"
                )
            )

        st.markdown(
            "### Current Hypothesis"
        )

        st.info(
            investigation.get(
                "primary_hypothesis",
                "No hypothesis available."
            )
        )


    # --------------------------------------------------------
    # Missing Evidence
    # --------------------------------------------------------

    missing_evidence = state_values.get(
        "missing_evidence",
        []
    )

    if missing_evidence:

        st.subheader(
            "🔍 Missing Evidence"
        )

        for item in missing_evidence:

            st.markdown(
                f"- {item}"
            )


    # --------------------------------------------------------
    # Diagnostic Commands
    # --------------------------------------------------------

    diagnostic_commands = state_values.get(
        "diagnostic_commands",
        []
    )

    if diagnostic_commands:

        st.subheader(
            "🛠️ Recommended Diagnostic Commands"
        )

        st.code(
            "\n".join(
                diagnostic_commands
            ),
            language="bash"
        )

        st.caption(
            "Run these commands in your environment "
            "and paste the results below."
        )


    # --------------------------------------------------------
    # Evidence Input
    # --------------------------------------------------------

    st.subheader(
        "📥 Paste Diagnostic Results"
    )

    diagnostic_results = st.text_area(
        "Engineer-provided evidence",
        height=250,
        key="diagnostic_input",
        placeholder="""Example:

kubectl describe pod recommendation-service

Limits:
  memory: 2Gi

kubectl top pod

NAME                    MEMORY
recommendation-service   1.95Gi

kubectl top node

worker-01                25%
"""
    )


    # --------------------------------------------------------
    # Resume Graph
    # --------------------------------------------------------

    submit_evidence = st.button(
        "🔄 Submit Evidence & Continue Investigation",
        type="primary",
        use_container_width=True
    )


    if submit_evidence:

        if not diagnostic_results.strip():

            st.error(
                "Please provide the diagnostic results."
            )

        else:

            config = {
                "configurable": {
                    "thread_id":
                    st.session_state.thread_id
                }
            }

            with st.spinner(
                "Resuming AI investigation..."
            ):

                try:

                    result = incident_graph.invoke(
                        Command(
                            resume=diagnostic_results
                        ),
                        config=config
                    )

                    interrupt_data = result.get(
                        "__interrupt__"
                    )

                    if interrupt_data:

                        # Another investigation round
                        st.session_state.current_interrupt = (
                            interrupt_data
                        )

                        st.session_state.waiting_for_evidence = True

                    else:

                        # Investigation completed
                        st.session_state.final_result = (
                            result
                        )

                        st.session_state.waiting_for_evidence = (
                            False
                        )

                        st.session_state.current_interrupt = (
                            None
                        )

                except Exception as error:

                    st.error(
                        f"Unable to resume investigation: {error}"
                    )

            st.rerun()


# ============================================================
# FINAL RCA
# ============================================================

if st.session_state.final_result:

    result = st.session_state.final_result

    investigation = result.get(
        "investigation",
        {}
    )

    st.divider()

    st.header(
        "3️⃣ Incident Investigation Result"
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    st.success(
        "✅ Investigation completed"
    )


    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Severity",
            investigation.get(
                "severity",
                "UNKNOWN"
            )
        )

    with col2:

        st.metric(
            "Confidence",
            f"{investigation.get('confidence', 0)}%"
        )

    with col3:

        st.metric(
            "Investigation Round",
            result.get(
                "investigation_round",
                "-"
            )
        )

    with col4:

        st.metric(
            "Evidence Status",
            "Sufficient"
            if result.get(
                "evidence_sufficient"
            )
            else "Insufficient"
        )


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    st.subheader(
        "📋 Incident Summary"
    )

    st.write(
        investigation.get(
            "summary",
            "No summary available."
        )
    )


    # --------------------------------------------------------
    # Root Cause
    # --------------------------------------------------------

    st.subheader(
        "🎯 Probable Root Cause"
    )

    st.info(
        investigation.get(
            "primary_hypothesis",
            "No root cause identified."
        )
    )


    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    st.subheader(
        "🔎 Evidence"
    )

    evidence = investigation.get(
        "evidence",
        []
    )

    if evidence:

        for item in evidence:

            st.markdown(
                f"✅ {item}"
            )

    else:

        st.write(
            "No evidence provided."
        )


    # --------------------------------------------------------
    # Alternative Causes
    # --------------------------------------------------------

    alternative_causes = investigation.get(
        "alternative_causes",
        []
    )

    if alternative_causes:

        st.subheader(
            "🔀 Alternative Causes"
        )

        for item in alternative_causes:

            st.markdown(
                f"- {item}"
            )


    # --------------------------------------------------------
    # Impact
    # --------------------------------------------------------

    st.subheader(
        "💥 Impact"
    )

    st.write(
        investigation.get(
            "impact",
            "Impact not determined."
        )
    )


    # --------------------------------------------------------
    # Immediate Action
    # --------------------------------------------------------

    st.subheader(
        "🚑 Immediate Mitigation"
    )

    st.warning(
        investigation.get(
            "immediate_action",
            "No immediate action available."
        )
    )


    # --------------------------------------------------------
    # Permanent Fix
    # --------------------------------------------------------

    st.subheader(
        "🔧 Permanent Fix"
    )

    st.write(
        investigation.get(
            "permanent_fix",
            "No permanent fix available."
        )
    )


    # --------------------------------------------------------
    # Prevention
    # --------------------------------------------------------

    st.subheader(
        "🛡️ Prevention"
    )

    st.write(
        investigation.get(
            "prevention",
            "No prevention recommendation available."
        )
    )


    # --------------------------------------------------------
    # Missing Evidence
    # --------------------------------------------------------

    remaining_missing = investigation.get(
        "missing_evidence",
        []
    )

    if remaining_missing:

        st.subheader(
            "⚠️ Remaining Missing Evidence"
        )

        for item in remaining_missing:

            st.markdown(
                f"- {item}"
            )


# ============================================================
# INCIDENT DATA
# ============================================================

if st.session_state.started:

    st.divider()

    st.header(
        "📊 Parsed Incident Data"
    )

    try:

        parsed = parse_logs(
            log_text
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Severity",
                parsed["severity"]
            )

        with col2:

            st.metric(
                "Total Events",
                parsed["total_events"]
            )

        with col3:

            st.metric(
                "Errors",
                parsed["error_count"]
            )

        with col4:

            st.metric(
                "Warnings",
                parsed["warning_count"]
            )

        with st.expander(
            "View detected errors"
        ):

            for error in parsed["errors"]:

                st.code(
                    error
                )

        with st.expander(
            "View detected warnings"
        ):

            for warning in parsed["warnings"]:

                st.code(
                    warning
                )

    except Exception as error:

        st.error(
            f"Log analysis failed: {error}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI SRE Copilot — Evidence-Grounded Incident Investigation"
)