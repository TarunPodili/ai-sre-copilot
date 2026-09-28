import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from analyzer import parse_logs
from rag import (
    search_knowledge,
    search_similar_incidents
)
from llm import investigate_incident


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="AI SRE Copilot",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# GEMINI CLIENT
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found in .env")
    st.stop()

client = genai.Client(
    api_key=api_key
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🤖 AI SRE Copilot")

st.caption(
    "Evidence-Grounded Deployment Incident Investigator"
)


# ============================================================
# SESSION STATE
# ============================================================

if "incident" not in st.session_state:
    st.session_state.incident = None

if "knowledge" not in st.session_state:
    st.session_state.knowledge = []

if "similar_incidents" not in st.session_state:
    st.session_state.similar_incidents = []

if "result" not in st.session_state:
    st.session_state.result = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR - INCIDENT INPUT
# ============================================================

with st.sidebar:

    st.header("📥 Incident Input")

    uploaded_file = st.file_uploader(
        "Upload deployment log",
        type=["log", "txt"]
    )

    st.write("Or paste deployment logs below.")

    log_text = st.text_area(
        "Deployment Logs",
        height=300,
        placeholder="""2026-09-27 10:30:01 INFO Deployment started
2026-09-27 10:30:05 INFO Pod payment-api created
2026-09-27 10:30:08 ERROR Failed to pull image payment-api:v1.8
2026-09-27 10:30:09 ERROR ImagePullBackOff
2026-09-27 10:30:12 ERROR Deployment failed"""
    )

    if uploaded_file:

        log_text = uploaded_file.read().decode(
            "utf-8"
        )

    investigate_button = st.button(
        "🔍 Investigate Incident",
        use_container_width=True
    )


# ============================================================
# INCIDENT INVESTIGATION
# ============================================================

if investigate_button:

    if not log_text.strip():

        st.warning(
            "Please provide deployment logs first."
        )

    else:

        with st.spinner(
            "🔎 Investigating deployment incident..."
        ):

            # ------------------------------------------------
            # 1. Parse logs
            # ------------------------------------------------

            incident = parse_logs(
                log_text
            )


            # ------------------------------------------------
            # 2. Build RAG query
            # ------------------------------------------------

            query = "\n".join(
                incident["errors"]
            )

            if not query.strip():

                query = log_text


            # ------------------------------------------------
            # 3. Search troubleshooting knowledge
            # ------------------------------------------------

            knowledge = search_knowledge(
                query,
                top_k=3
            )


            # ------------------------------------------------
            # 4. Search historical incidents
            # ------------------------------------------------

            similar_incidents = search_similar_incidents(
                query,
                top_k=3
            )


            # ------------------------------------------------
            # 5. Gemini investigation
            # ------------------------------------------------

            result = investigate_incident(
                incident,
                knowledge,
                similar_incidents
            )


            # ------------------------------------------------
            # 6. Save results
            # ------------------------------------------------

            st.session_state.incident = incident

            st.session_state.knowledge = knowledge

            st.session_state.similar_incidents = (
                similar_incidents
            )

            st.session_state.result = result


            # ------------------------------------------------
            # 7. Reset chatbot
            # ------------------------------------------------

            st.session_state.messages = []


        st.success(
            "✅ Investigation completed."
        )


# ============================================================
# RCA DASHBOARD
# ============================================================

if st.session_state.result:

    result = st.session_state.result

    st.divider()

    st.header(
        "🚨 Incident Investigation"
    )


    # ========================================================
    # TOP METRICS
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Severity",
            result.get(
                "severity",
                "UNKNOWN"
            )
        )


    with col2:

        st.metric(
            "Confidence",
            f"{result.get('confidence', 0)}%"
        )


    with col3:

        st.metric(
            "Errors",
            st.session_state.incident.get(
                "error_count",
                0
            )
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    st.subheader(
        "📋 Summary"
    )

    st.write(
        result.get(
            "summary",
            "No summary available."
        )
    )


    # ========================================================
    # PRIMARY HYPOTHESIS
    # ========================================================

    st.subheader(
        "🎯 Primary Hypothesis"
    )

    st.info(
        result.get(
            "primary_hypothesis",
            "No hypothesis available."
        )
    )


    # ========================================================
    # EVIDENCE
    # ========================================================

    st.subheader(
        "🔎 Evidence"
    )

    evidence = result.get(
        "evidence",
        []
    )

    if evidence:

        for item in evidence:

            st.write(
                f"• {item}"
            )

    else:

        st.write(
            "No evidence identified."
        )


    # ========================================================
    # ALTERNATIVE CAUSES
    # ========================================================

    st.subheader(
        "🔀 Alternative Causes"
    )

    alternatives = result.get(
        "alternative_causes",
        []
    )

    if alternatives:

        for item in alternatives:

            st.write(
                f"• {item}"
            )

    else:

        st.write(
            "No alternative causes identified."
        )


    # ========================================================
    # IMPACT
    # ========================================================

    st.subheader(
        "💥 Impact"
    )

    st.write(
        result.get(
            "impact",
            "No impact information available."
        )
    )


    # ========================================================
    # ACTIONS
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "⚡ Immediate Action"
        )

        st.write(
            result.get(
                "immediate_action",
                "No immediate action provided."
            )
        )


    with col2:

        st.subheader(
            "🔧 Permanent Fix"
        )

        st.write(
            result.get(
                "permanent_fix",
                "No permanent fix provided."
            )
        )


    # ========================================================
    # PREVENTION
    # ========================================================

    st.subheader(
        "🛡️ Prevention"
    )

    st.write(
        result.get(
            "prevention",
            "No prevention recommendation provided."
        )
    )


    # ========================================================
    # MISSING EVIDENCE
    # ========================================================

    missing = result.get(
        "missing_evidence",
        []
    )

    if missing:

        st.subheader(
            "🕵️ Additional Evidence Required"
        )

        for item in missing:

            st.warning(
                item
            )


    # ========================================================
    # TROUBLESHOOTING KNOWLEDGE
    # ========================================================

    st.divider()

    with st.expander(
        "📚 Retrieved Troubleshooting Knowledge"
    ):

        for item in st.session_state.knowledge:

            st.markdown(
                f"### {item['source']}"
            )

            st.caption(
                f"Semantic similarity: "
                f"{item['score']:.3f}"
            )


    # ========================================================
    # HISTORICAL INCIDENTS
    # ========================================================

    st.subheader(
        "🧠 Similar Historical Incidents"
    )

    if st.session_state.similar_incidents:

        for incident in (
            st.session_state.similar_incidents
        ):

            with st.expander(
                f"{incident['source']} — "
                f"{incident['score']:.1%} similarity"
            ):

                st.markdown(
                    incident["content"]
                )

    else:

        st.info(
            "No similar historical incidents found."
        )


    # ========================================================
    # INTERACTIVE INVESTIGATION CHATBOT
    # ========================================================

    st.divider()

    st.header(
        "💬 Investigate Further"
    )

    st.caption(
        "Ask follow-up questions about the current incident."
    )


    # --------------------------------------------------------
    # Display chat history
    # --------------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    # --------------------------------------------------------
    # Chat input
    # --------------------------------------------------------

    question = st.chat_input(
        "Ask about this incident..."
    )


    if question:

        # ====================================================
        # USER MESSAGE
        # ====================================================

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        with st.chat_message(
            "user"
        ):

            st.write(
                question
            )


        # ====================================================
        # BUILD CHAT CONTEXT
        # ====================================================

        context = f"""

========================
CURRENT INCIDENT
========================

{st.session_state.incident}


========================
AI INVESTIGATION
========================

{st.session_state.result}


========================
TROUBLESHOOTING KNOWLEDGE
========================

{st.session_state.knowledge}


========================
SIMILAR HISTORICAL INCIDENTS
========================

{st.session_state.similar_incidents}


========================
USER QUESTION
========================

{question}

"""


        # ====================================================
        # ASK GEMINI
        # ====================================================

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "🧠 Investigating..."
            ):

                response = client.models.generate_content(

                    model="gemini-3.5-flash-lite",

                    contents=f"""

You are an SRE troubleshooting assistant.

Your job is to help investigate the CURRENT
deployment incident.

Use:

1. Current incident data
2. AI investigation
3. Troubleshooting knowledge
4. Similar historical incidents

IMPORTANT:

The CURRENT INCIDENT is the primary source
of truth.

Historical incidents are supporting evidence only.

Do NOT assume that a historical incident has
the same root cause as the current incident.

Do not invent evidence.

If the available evidence is insufficient,
clearly say so.

When appropriate:

- Explain why a cause is likely.
- Explain alternative causes.
- Identify missing evidence.
- Recommend diagnostic commands.
- Explain how to distinguish between possible causes.
- Reference similar historical incidents when useful.

{context}

"""

                )

                answer = response.text


                # ------------------------------------------------
                # Display answer
                # ------------------------------------------------

                st.write(
                    answer
                )


        # ====================================================
        # SAVE ASSISTANT MESSAGE
        # ====================================================

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

# import streamlit as st

# from analyzer import parse_logs
# from rag import search_knowledge
# from llm import investigate_incident


# st.set_page_config(
#     page_title="AI SRE Copilot",
#     page_icon="🤖",
#     layout="wide"
# )


# st.title("🤖 AI SRE Copilot")
# st.caption("Evidence-Grounded Deployment Incident Investigator")


# # -----------------------------
# # Session State
# # -----------------------------

# if "incident" not in st.session_state:
#     st.session_state.incident = None

# if "knowledge" not in st.session_state:
#     st.session_state.knowledge = None

# if "result" not in st.session_state:
#     st.session_state.result = None

# if "messages" not in st.session_state:
#     st.session_state.messages = []


# # -----------------------------
# # Sidebar
# # -----------------------------

# with st.sidebar:
#     st.header("Incident Input")

#     uploaded_file = st.file_uploader(
#         "Upload deployment log",
#         type=["log", "txt"]
#     )

#     st.write("Or paste logs below.")

#     log_text = st.text_area(
#         "Deployment Logs",
#         height=250,
#         placeholder="""2026-09-27 10:30:01 INFO Deployment started
# 2026-09-27 10:30:05 INFO Pod payment-api created
# 2026-09-27 10:30:08 ERROR Failed to pull image payment-api:v1.8
# 2026-09-27 10:30:09 ERROR ImagePullBackOff
# 2026-09-27 10:30:12 ERROR Deployment failed"""
#     )

#     if uploaded_file:
#         log_text = uploaded_file.read().decode("utf-8")

#     investigate_button = st.button(
#         "🔍 Investigate Incident",
#         use_container_width=True
#     )


# # -----------------------------
# # Investigation
# # -----------------------------

# if investigate_button:

#     if not log_text.strip():
#         st.warning("Please provide deployment logs first.")

#     else:

#         with st.spinner("Analyzing incident..."):

#             # 1. Parse logs
#             incident = parse_logs(log_text)

#             # 2. Create RAG query
#             query = "\n".join(
#                 incident["errors"]
#             )

#             if not query:
#                 query = log_text

#             # 3. Retrieve knowledge
#             knowledge = search_knowledge(
#                 query,
#                 top_k=3
#             )

#             # 4. Gemini investigation
#             result = investigate_incident(
#                 incident,
#                 knowledge
#             )

#             # Save everything
#             st.session_state.incident = incident
#             st.session_state.knowledge = knowledge
#             st.session_state.result = result

#             # Reset chatbot
#             st.session_state.messages = []

#         st.success("Investigation completed.")


# # -----------------------------
# # RCA Dashboard
# # -----------------------------

# if st.session_state.result:

#     result = st.session_state.result

#     st.divider()

#     st.subheader("🚨 Incident Investigation")

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         st.metric(
#             "Severity",
#             result.get("severity", "UNKNOWN")
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

#     # Summary
#     st.subheader("📋 Summary")

#     st.write(
#         result.get("summary", "")
#     )

#     # Root cause
#     st.subheader("🎯 Primary Hypothesis")

#     st.info(
#         result.get(
#             "primary_hypothesis",
#             ""
#         )
#     )

#     # Evidence
#     st.subheader("🔎 Evidence")

#     evidence = result.get(
#         "evidence",
#         []
#     )

#     for item in evidence:
#         st.write(f"• {item}")

#     # Alternative causes
#     st.subheader("🔀 Alternative Causes")

#     alternatives = result.get(
#         "alternative_causes",
#         []
#     )

#     for item in alternatives:
#         st.write(f"• {item}")

#     # Impact
#     st.subheader("💥 Impact")

#     st.write(
#         result.get("impact", "")
#     )

#     # Actions
#     col1, col2 = st.columns(2)

#     with col1:

#         st.subheader("⚡ Immediate Action")

#         st.write(
#             result.get(
#                 "immediate_action",
#                 ""
#             )
#         )

#     with col2:

#         st.subheader("🔧 Permanent Fix")

#         st.write(
#             result.get(
#                 "permanent_fix",
#                 ""
#             )
#         )

#     # Prevention
#     st.subheader("🛡️ Prevention")

#     st.write(
#         result.get(
#             "prevention",
#             ""
#         )
#     )

#     # Missing evidence
#     missing = result.get(
#         "missing_evidence",
#         []
#     )

#     if missing:

#         st.subheader(
#             "🕵️ Additional Evidence Required"
#         )

#         for item in missing:
#             st.warning(item)


#     # -----------------------------
#     # Retrieved Knowledge
#     # -----------------------------

#     with st.expander(
#         "📚 Retrieved Troubleshooting Knowledge"
#     ):

#         for item in st.session_state.knowledge:

#             st.markdown(
#                 f"**{item['source']}**"
#             )

#             st.caption(
#                 f"Similarity: {item['score']:.3f}"
#             )


#     # -----------------------------
#     # Chatbot
#     # -----------------------------

#     st.divider()

#     st.subheader("💬 Investigate Further")

#     st.caption(
#         "Ask questions about the current incident."
#     )


#     # Display previous messages

#     for message in st.session_state.messages:

#         with st.chat_message(
#             message["role"]
#         ):

#             st.write(
#                 message["content"]
#             )


#     # Chat input

#     question = st.chat_input(
#         "Ask about this incident..."
#     )


#     if question:

#         # User message
#         st.session_state.messages.append(
#             {
#                 "role": "user",
#                 "content": question
#             }
#         )

#         with st.chat_message("user"):
#             st.write(question)


#         # Build context
#         context = f"""
# CURRENT INCIDENT:

# {st.session_state.incident}

# AI INVESTIGATION:

# {st.session_state.result}

# RETRIEVED KNOWLEDGE:

# {st.session_state.knowledge}

# USER QUESTION:

# {question}
# """


#         # Ask Gemini
#         with st.chat_message("assistant"):

#             with st.spinner(
#                 "Investigating..."
#             ):

#                 from google import genai
#                 import os

#                 client = genai.Client(
#                     api_key=os.getenv(
#                         "GEMINI_API_KEY"
#                     )
#                 )

#                 response = client.models.generate_content(
#                     model="gemini-3.5-flash-lite",
#                     contents=f"""
# You are an SRE troubleshooting assistant.

# Answer the user's question using ONLY
# the incident context and retrieved knowledge.

# Do not invent evidence.

# If the available information is insufficient,
# say so clearly and identify what evidence
# would be needed.

# {context}
# """
#                 )

#                 answer = response.text

#                 st.write(answer)

#         st.session_state.messages.append(
#             {
#                 "role": "assistant",
#                 "content": answer
#             }
#         )