# import os
# import json

# from dotenv import load_dotenv
# from google import genai


# load_dotenv()


# # ============================================================
# # GEMINI CONFIGURATION
# # ============================================================

# api_key = os.getenv("GEMINI_API_KEY")

# if not api_key:
#     raise ValueError(
#         "GEMINI_API_KEY not found in .env"
#     )

# client = genai.Client(
#     api_key=api_key
# )


# # ============================================================
# # SYSTEM PROMPT
# # ============================================================

# SYSTEM_PROMPT = """
# You are an AI SRE incident investigation assistant.

# Your job is to investigate deployment incidents using
# the current incident evidence, troubleshooting knowledge,
# and similar historical incidents.

# IMPORTANT RULES:

# 1. Do not invent evidence.

# 2. Separate evidence from inference.

# 3. Generate a probable root cause based primarily
#    on the current incident evidence.

# 4. Provide a confidence score from 0 to 100.

# 5. Provide alternative causes when appropriate.

# 6. If the current evidence is insufficient,
#    clearly say so.

# 7. Recommend diagnostic steps for missing evidence.

# 8. Historical incidents are supporting evidence only.
#    Do NOT assume that a similar historical incident
#    has the same root cause.

# 9. Recommendations must be practical for
#    DevOps/SRE engineers.

# 10. Use the current incident logs as the primary
#     source of truth.

# Return valid JSON with exactly this structure:

# {
#     "summary": "string",
#     "severity": "LOW | MEDIUM | HIGH | CRITICAL",
#     "primary_hypothesis": "string",
#     "confidence": 0,
#     "evidence": [],
#     "alternative_causes": [],
#     "impact": "string",
#     "immediate_action": "string",
#     "permanent_fix": "string",
#     "prevention": "string",
#     "missing_evidence": []
# }
# """


# # ============================================================
# # INCIDENT INVESTIGATION
# # ============================================================

# def investigate_incident(
#     incident_data,
#     retrieved_knowledge,
#     similar_incidents=None
# ):

#     # --------------------------------------------------------
#     # Handle historical incidents
#     # --------------------------------------------------------

#     if similar_incidents is None:
#         similar_incidents = []


#     # --------------------------------------------------------
#     # Convert retrieved knowledge into text
#     # --------------------------------------------------------

#     knowledge_text = "\n\n".join(
#         [
#             f"SOURCE: {item['source']}\n"
#             f"{item['content']}"
#             for item in retrieved_knowledge
#         ]
#     )


#     # --------------------------------------------------------
#     # Convert historical incidents into text
#     # --------------------------------------------------------

#     historical_text = "\n\n".join(
#         [
#             f"HISTORICAL INCIDENT: {item['source']}\n"
#             f"SIMILARITY: {item['score']:.3f}\n"
#             f"{item['content']}"
#             for item in similar_incidents
#         ]
#     )


#     # --------------------------------------------------------
#     # Build Gemini prompt
#     # --------------------------------------------------------

#     user_prompt = f"""
# Analyze this deployment incident.

# ========================
# CURRENT INCIDENT DATA
# ========================

# {json.dumps(incident_data, indent=2)}


# ========================
# TROUBLESHOOTING KNOWLEDGE
# ========================

# {knowledge_text}


# ========================
# SIMILAR HISTORICAL INCIDENTS
# ========================

# {historical_text}


# ========================
# INVESTIGATION INSTRUCTIONS
# ========================

# Determine the most probable root cause.

# Use the CURRENT INCIDENT DATA as the primary
# source of evidence.

# Use troubleshooting knowledge to understand
# possible causes and diagnostic procedures.

# Use historical incidents only as supporting
# context.

# Do NOT assume a historical incident has the
# same root cause as the current incident.

# If evidence is insufficient, do NOT guess.

# Instead:
# 1. Explain what is currently known.
# 2. Identify possible causes.
# 3. Identify the missing evidence.
# 4. Recommend specific diagnostic steps.

# Use the logs and retrieved knowledge as evidence.
# """


#     # --------------------------------------------------------
#     # Call Gemini
#     # --------------------------------------------------------

#     response = client.models.generate_content(
#         model="gemini-3.5-flash-lite",
#         contents=[
#             SYSTEM_PROMPT,
#             user_prompt
#         ],
#         config={
#             "response_mime_type": "application/json"
#         }
#     )


#     # --------------------------------------------------------
#     # Parse JSON response
#     # --------------------------------------------------------

#     return json.loads(
#         response.text
#     )


import os
import json
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

client = genai.Client(
    api_key=api_key
)


SYSTEM_PROMPT = """
You are an AI SRE incident investigation assistant.

Your job is to investigate deployment incidents using:
1. Current incident evidence
2. Troubleshooting knowledge
3. Similar historical incidents

IMPORTANT RULES:

1. Do not invent evidence.

2. Separate evidence from inference.

3. Generate a probable root cause based primarily
   on the current incident evidence.

4. Provide a confidence score from 0 to 100.

5. Provide alternative causes when appropriate.

6. If the current evidence is insufficient,
   clearly say so.

7. Recommend diagnostic steps for missing evidence.

8. Historical incidents are supporting evidence only.
   Do NOT assume that a similar historical incident
   has the same root cause.

9. Recommendations must be practical for
   DevOps/SRE engineers.

10. Use the current incident logs as the primary
    source of truth.

Return valid JSON with exactly this structure:

{
    "summary": "string",
    "severity": "LOW | MEDIUM | HIGH | CRITICAL",
    "primary_hypothesis": "string",
    "confidence": 0,
    "evidence": [],
    "alternative_causes": [],
    "impact": "string",
    "immediate_action": "string",
    "permanent_fix": "string",
    "prevention": "string",
    "missing_evidence": []
}
"""


def investigate_incident(
    incident_data,
    retrieved_knowledge,
    similar_incidents=None
):

    if similar_incidents is None:
        similar_incidents = []

    knowledge_text = "\n\n".join(
        [
            f"SOURCE: {item['source']}\n"
            f"{item['content']}"
            for item in retrieved_knowledge
        ]
    )

    historical_text = "\n\n".join(
        [
            f"HISTORICAL INCIDENT: {item['source']}\n"
            f"SIMILARITY: {item['score']:.3f}\n"
            f"{item['content']}"
            for item in similar_incidents
        ]
    )

    user_prompt = f"""
Analyze this deployment incident.

========================
CURRENT INCIDENT DATA
========================

{json.dumps(incident_data, indent=2)}

========================
TROUBLESHOOTING KNOWLEDGE
========================

{knowledge_text}

========================
SIMILAR HISTORICAL INCIDENTS
========================

{historical_text}

========================
INVESTIGATION INSTRUCTIONS
========================

Determine the most probable root cause.

Use CURRENT INCIDENT DATA as the primary
source of evidence.

Use troubleshooting knowledge to understand
possible causes and diagnostic procedures.

Use historical incidents only as supporting
context.

Do NOT assume a historical incident has the
same root cause as the current incident.

If evidence is insufficient, do NOT guess.

Instead:
1. Explain what is currently known.
2. Identify possible causes.
3. Identify missing evidence.
4. Recommend specific diagnostic steps.

Use the logs and retrieved knowledge as evidence.
"""

    # --------------------------------------------------------
    # Gemini request with controlled retry
    # --------------------------------------------------------

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:

            print(
                f"🧠 Gemini request "
                f"(attempt {attempt}/{max_attempts})..."
            )

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=[
                    SYSTEM_PROMPT,
                    user_prompt
                ],
                config={
                    "response_mime_type": "application/json"
                }
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return json.loads(
                response.text
            )

        except Exception as error:

            print(
                f"⚠️ Gemini request failed: {error}"
            )

            if attempt < max_attempts:

                wait_time = attempt * 2

                print(
                    f"⏳ Retrying in "
                    f"{wait_time} seconds..."
                )

                time.sleep(
                    wait_time
                )

            else:

                raise RuntimeError(
                    "Gemini investigation failed "
                    "after multiple attempts."
                ) from error