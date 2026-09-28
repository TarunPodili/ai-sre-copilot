# from typing import TypedDict

# from langgraph.graph import StateGraph, START, END

# from analyzer import parse_logs
# from rag import (
#     search_knowledge,
#     search_similar_incidents
# )
# from llm import investigate_incident


# # ============================================================
# # INCIDENT STATE
# # ============================================================

# class IncidentState(TypedDict, total=False):
#     logs: str

#     incident: dict

#     knowledge: list

#     similar_incidents: list

#     investigation: dict

#     evidence_sufficient: bool

#     missing_evidence: list

#     diagnostic_commands: list

#     investigation_status: str


# # ============================================================
# # 1. ANALYZE LOGS
# # ============================================================

# def analyze_logs(state: IncidentState):

#     print("\n🔎 Analyzing deployment logs...")

#     incident = parse_logs(
#         state["logs"]
#     )

#     return {
#         "incident": incident
#     }


# # ============================================================
# # 2. RETRIEVE KNOWLEDGE
# # ============================================================

# def retrieve_knowledge(state: IncidentState):

#     print("📚 Retrieving troubleshooting knowledge...")

#     incident = state["incident"]

#     query = "\n".join(
#         incident.get("errors", [])
#     )

#     if not query.strip():
#         query = state["logs"]

#     knowledge = search_knowledge(
#         query,
#         top_k=3
#     )

#     return {
#         "knowledge": knowledge
#     }


# # ============================================================
# # 3. RETRIEVE HISTORICAL INCIDENTS
# # ============================================================

# def retrieve_historical_incidents(
#     state: IncidentState
# ):

#     print("🧠 Searching historical incidents...")

#     incident = state["incident"]

#     query = "\n".join(
#         incident.get("errors", [])
#     )

#     if not query.strip():
#         query = state["logs"]

#     similar_incidents = search_similar_incidents(
#         query,
#         top_k=3
#     )

#     return {
#         "similar_incidents": similar_incidents
#     }


# # ============================================================
# # 4. AI INVESTIGATION
# # ============================================================

# def investigate(state: IncidentState):

#     print("🤖 Running AI investigation...")

#     result = investigate_incident(
#         state["incident"],
#         state["knowledge"],
#         state["similar_incidents"]
#     )

#     return {
#         "investigation": result,
#         "missing_evidence": result.get(
#             "missing_evidence",
#             []
#         )
#     }


# # ============================================================
# # 5. EVALUATE EVIDENCE
# # ============================================================

# def evaluate_evidence(
#     state: IncidentState
# ):

#     print("📊 Evaluating evidence...")

#     investigation = state["investigation"]

#     confidence = investigation.get(
#         "confidence",
#         0
#     )

#     missing_evidence = investigation.get(
#         "missing_evidence",
#         []
#     )

#     # We intentionally keep these two concepts separate:
#     #
#     # confidence = how strongly the AI believes
#     # the hypothesis.
#     #
#     # evidence sufficiency = whether enough
#     # evidence exists to finalize the investigation.

#     if (
#         confidence >= 70
#         and not missing_evidence
#     ):
#         sufficient = True
#         status = "RCA_READY"

#         print(
#             f"✅ Investigation ready for RCA "
#             f"({confidence}% confidence)"
#         )

#     else:
#         sufficient = False
#         status = "MORE_EVIDENCE_REQUIRED"

#         print(
#             f"⚠️ More evidence required "
#             f"({confidence}% hypothesis confidence)"
#         )

#     return {
#         "evidence_sufficient": sufficient,
#         "investigation_status": status
#     }


# # ============================================================
# # 6. GENERATE DIAGNOSTIC COMMANDS
# # ============================================================

# def generate_diagnostics(
#     state: IncidentState
# ):

#     print("🛠️ Generating diagnostic steps...")

#     investigation = state["investigation"]

#     missing_evidence = state.get(
#         "missing_evidence",
#         []
#     )

#     commands = []

#     # --------------------------------------------------------
#     # Generic diagnostic commands
#     # --------------------------------------------------------

#     commands.append(
#         "kubectl describe pod <pod-name>"
#     )

#     commands.append(
#         "kubectl logs <pod-name> --previous"
#     )

#     commands.append(
#         "kubectl get pod <pod-name> -o yaml"
#     )

#     # --------------------------------------------------------
#     # Add memory-specific diagnostics
#     # --------------------------------------------------------

#     hypothesis = investigation.get(
#         "primary_hypothesis",
#         ""
#     ).lower()

#     if (
#         "memory" in hypothesis
#         or "oom" in hypothesis
#     ):
#         commands.append(
#             "kubectl top pod <pod-name>"
#         )

#         commands.append(
#             "kubectl get pod <pod-name> "
#             "-o jsonpath="
#             "\"{.spec.containers[*].resources}\""
#         )

#     # --------------------------------------------------------
#     # Add database-specific diagnostics
#     # --------------------------------------------------------

#     if (
#         "database" in hypothesis
#         or "postgres" in hypothesis
#     ):
#         commands.append(
#             "kubectl get svc"
#         )

#         commands.append(
#             "kubectl get endpoints"
#         )

#     # --------------------------------------------------------
#     # Add network-specific diagnostics
#     # --------------------------------------------------------

#     if (
#         "network" in hypothesis
#         or "connection" in hypothesis
#     ):
#         commands.append(
#             "kubectl get svc"
#         )

#         commands.append(
#             "kubectl get endpoints"
#         )

#     print(
#         f"🧪 Generated {len(commands)} diagnostic commands."
#     )

#     return {
#         "diagnostic_commands": commands
#     }


# # ============================================================
# # 7. CONDITIONAL ROUTING
# # ============================================================

# def route_after_evaluation(
#     state: IncidentState
# ):

#     if state.get(
#         "evidence_sufficient",
#         False
#     ):
#         return "complete"

#     return "diagnostics"


# # ============================================================
# # 8. BUILD GRAPH
# # ============================================================

# builder = StateGraph(
#     IncidentState
# )


# builder.add_node(
#     "analyze_logs",
#     analyze_logs
# )

# builder.add_node(
#     "retrieve_knowledge",
#     retrieve_knowledge
# )

# builder.add_node(
#     "retrieve_historical_incidents",
#     retrieve_historical_incidents
# )

# builder.add_node(
#     "investigate",
#     investigate
# )

# builder.add_node(
#     "evaluate_evidence",
#     evaluate_evidence
# )

# builder.add_node(
#     "generate_diagnostics",
#     generate_diagnostics
# )


# # ============================================================
# # 9. GRAPH FLOW
# # ============================================================

# builder.add_edge(
#     START,
#     "analyze_logs"
# )

# builder.add_edge(
#     "analyze_logs",
#     "retrieve_knowledge"
# )

# builder.add_edge(
#     "retrieve_knowledge",
#     "retrieve_historical_incidents"
# )

# builder.add_edge(
#     "retrieve_historical_incidents",
#     "investigate"
# )

# builder.add_edge(
#     "investigate",
#     "evaluate_evidence"
# )


# # ============================================================
# # 10. CONDITIONAL EDGE
# # ============================================================

# builder.add_conditional_edges(
#     "evaluate_evidence",
#     route_after_evaluation,
#     {
#         "complete": END,
#         "diagnostics": "generate_diagnostics"
#     }
# )


# builder.add_edge(
#     "generate_diagnostics",
#     END
# )


# # ============================================================
# # 11. COMPILE
# # ============================================================

# incident_graph = builder.compile()


# # ============================================================
# # 12. TEST
# # ============================================================

# if __name__ == "__main__":

#     test_logs = """
#     2026-09-28 11:20:01 INFO Deployment started for recommendation-service
#     2026-09-28 11:20:04 INFO Pod recommendation-service-5f76bc created
#     2026-09-28 11:20:07 INFO Container started
#     2026-09-28 11:20:15 INFO Loading recommendation model
#     2026-09-28 11:20:32 INFO Loading model weights: 1.8 GB
#     2026-09-28 11:20:45 WARN Memory usage exceeded 80 percent
#     2026-09-28 11:20:51 WARN Memory usage exceeded 95 percent
#     2026-09-28 11:20:54 ERROR Container terminated
#     2026-09-28 11:20:54 ERROR Reason: OOMKilled
#     2026-09-28 11:20:55 WARN Container restart initiated
#     2026-09-28 11:21:18 ERROR Reason: OOMKilled
#     2026-09-28 11:21:19 ERROR CrashLoopBackOff
#     2026-09-28 11:21:20 ERROR Deployment failed
#     """

#     result = incident_graph.invoke(
#         {
#             "logs": test_logs
#         }
#     )

#     print("\n")
#     print("=" * 60)
#     print("FINAL INVESTIGATION")
#     print("=" * 60)

#     print(
#         result["investigation"]
#     )

#     print("\n")
#     print(
#         "Evidence sufficient:",
#         result.get(
#             "evidence_sufficient"
#         )
#     )

#     print("\n")
#     print(
#         "Investigation status:",
#         result.get(
#             "investigation_status"
#         )
#     )

#     if result.get("diagnostic_commands"):

#         print("\n")
#         print("DIAGNOSTIC COMMANDS")
#         print("=" * 60)

#         for command in result["diagnostic_commands"]:
#             print(
#                 f"→ {command}"
#             )





from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from analyzer import parse_logs
from rag import (
    search_knowledge,
    search_similar_incidents
)
from llm import investigate_incident


# ============================================================
# CONFIGURATION
# ============================================================

MAX_ROUNDS = 3


# ============================================================
# INCIDENT STATE
# ============================================================

class IncidentState(TypedDict, total=False):

    # Original incident
    logs: str

    # Evidence supplied by engineer
    diagnostic_results: str

    # Parsed incident
    incident: dict

    # RAG results
    knowledge: list
    similar_incidents: list

    # AI investigation
    investigation: dict

    # Evidence evaluation
    evidence_sufficient: bool
    missing_evidence: list

    # Diagnostics
    diagnostic_commands: list

    # Workflow
    investigation_status: str
    investigation_round: int


# ============================================================
# 1. ANALYZE LOGS
# ============================================================

def analyze_logs(state: IncidentState):

    print("\n🔎 Analyzing deployment logs...")

    incident = parse_logs(
        state["logs"]
    )

    return {
        "incident": incident,
        "investigation_round": 1
    }


# ============================================================
# 2. KNOWLEDGE RAG
# ============================================================

def retrieve_knowledge(state: IncidentState):

    print("📚 Retrieving troubleshooting knowledge...")

    incident = state["incident"]

    query = "\n".join(
        incident.get("errors", [])
    )

    if not query.strip():
        query = state["logs"]

    knowledge = search_knowledge(
        query,
        top_k=3
    )

    return {
        "knowledge": knowledge
    }


# ============================================================
# 3. HISTORICAL INCIDENT RAG
# ============================================================

def retrieve_historical_incidents(
    state: IncidentState
):

    print("🧠 Searching historical incidents...")

    incident = state["incident"]

    query = "\n".join(
        incident.get("errors", [])
    )

    if not query.strip():
        query = state["logs"]

    similar_incidents = search_similar_incidents(
        query,
        top_k=3
    )

    return {
        "similar_incidents": similar_incidents
    }


# ============================================================
# 4. AI INVESTIGATION
# ============================================================

def investigate(state: IncidentState):

    round_number = state.get(
        "investigation_round",
        1
    )

    print(
        f"🤖 Running AI investigation "
        f"(round {round_number})..."
    )

    incident = dict(
        state["incident"]
    )

    diagnostic_results = state.get(
        "diagnostic_results",
        ""
    )

    if diagnostic_results.strip():

        incident[
            "additional_diagnostic_evidence"
        ] = diagnostic_results

    result = investigate_incident(
        incident,
        state["knowledge"],
        state["similar_incidents"]
    )

    return {
        "investigation": result,
        "missing_evidence": result.get(
            "missing_evidence",
            []
        )
    }


# ============================================================
# 5. EVALUATE EVIDENCE
# ============================================================

def evaluate_evidence(
    state: IncidentState
):

    print("📊 Evaluating evidence...")

    investigation = state["investigation"]

    confidence = investigation.get(
        "confidence",
        0
    )

    missing_evidence = investigation.get(
        "missing_evidence",
        []
    )

    round_number = state.get(
        "investigation_round",
        1
    )

    if (
        confidence >= 70
        and not missing_evidence
    ):

        sufficient = True
        status = "RCA_READY"

        print(
            f"✅ Evidence sufficient "
            f"({confidence}% confidence)"
        )

    elif round_number >= MAX_ROUNDS:

        sufficient = True
        status = "MAX_ROUNDS_REACHED"

        print(
            "⚠️ Maximum investigation rounds reached."
        )

    else:

        sufficient = False
        status = "MORE_EVIDENCE_REQUIRED"

        print(
            f"⚠️ More evidence required "
            f"({confidence}% hypothesis confidence)"
        )

    return {
        "evidence_sufficient": sufficient,
        "investigation_status": status
    }


# ============================================================
# 6. GENERATE DIAGNOSTIC COMMANDS
# ============================================================

def generate_diagnostics(
    state: IncidentState
):

    print("🛠️ Generating diagnostic steps...")

    investigation = state["investigation"]

    hypothesis = investigation.get(
        "primary_hypothesis",
        ""
    ).lower()

    commands = [
        "kubectl describe pod <pod-name>",
        "kubectl logs <pod-name> --previous",
        "kubectl get pod <pod-name> -o yaml"
    ]

    if (
        "memory" in hypothesis
        or "oom" in hypothesis
    ):

        commands.extend([
            "kubectl top pod <pod-name>",
            (
                "kubectl get pod <pod-name> "
                "-o jsonpath="
                "\"{.spec.containers[*].resources}\""
            ),
            "kubectl top node"
        ])

    if (
        "database" in hypothesis
        or "postgres" in hypothesis
    ):

        commands.extend([
            "kubectl get svc",
            "kubectl get endpoints"
        ])

    if (
        "network" in hypothesis
        or "connection" in hypothesis
    ):

        commands.extend([
            "kubectl get svc",
            "kubectl get endpoints"
        ])

    commands = list(
        dict.fromkeys(commands)
    )

    print(
        f"🧪 Generated {len(commands)} diagnostic commands."
    )

    return {
        "diagnostic_commands": commands
    }


# ============================================================
# 7. HUMAN-IN-THE-LOOP
# ============================================================

def request_human_evidence(
    state: IncidentState
):

    round_number = state.get(
        "investigation_round",
        1
    )

    investigation = state["investigation"]

    missing_evidence = state.get(
        "missing_evidence",
        []
    )

    diagnostic_commands = state.get(
        "diagnostic_commands",
        []
    )

    print("\n")
    print("=" * 60)
    print(
        f"🛑 HUMAN INPUT REQUIRED — ROUND {round_number}"
    )
    print("=" * 60)

    print("\nMissing evidence:")

    for item in missing_evidence:
        print(f"→ {item}")

    print("\nRecommended diagnostic commands:")

    for command in diagnostic_commands:
        print(f"→ {command}")

    # --------------------------------------------------------
    # LangGraph pauses here.
    #
    # The value supplied when resuming becomes the return
    # value of interrupt().
    # --------------------------------------------------------

    diagnostic_results = interrupt(
        {
            "type": "diagnostic_evidence_request",

            "message": (
                "Additional diagnostic evidence is required "
                "before the investigation can continue."
            ),

            "round": round_number,

            "missing_evidence": missing_evidence,

            "diagnostic_commands": diagnostic_commands,

            "current_hypothesis": investigation.get(
                "primary_hypothesis",
                ""
            ),

            "current_confidence": investigation.get(
                "confidence",
                0
            )
        }
    )

    if not isinstance(
        diagnostic_results,
        str
    ):

        diagnostic_results = str(
            diagnostic_results
        )

    return {
        "diagnostic_results": diagnostic_results,
        "investigation_round": round_number + 1
    }


# ============================================================
# 8. ROUTING AFTER EVIDENCE EVALUATION
# ============================================================

def route_after_evaluation(
    state: IncidentState
):

    if state.get(
        "evidence_sufficient",
        False
    ):
        return "complete"

    return "diagnostics"


# ============================================================
# 9. BUILD GRAPH
# ============================================================

builder = StateGraph(
    IncidentState
)


builder.add_node(
    "analyze_logs",
    analyze_logs
)

builder.add_node(
    "retrieve_knowledge",
    retrieve_knowledge
)

builder.add_node(
    "retrieve_historical_incidents",
    retrieve_historical_incidents
)

builder.add_node(
    "investigate",
    investigate
)

builder.add_node(
    "evaluate_evidence",
    evaluate_evidence
)

builder.add_node(
    "generate_diagnostics",
    generate_diagnostics
)

builder.add_node(
    "request_human_evidence",
    request_human_evidence
)


# ============================================================
# 10. INITIAL INVESTIGATION FLOW
# ============================================================

builder.add_edge(
    START,
    "analyze_logs"
)

builder.add_edge(
    "analyze_logs",
    "retrieve_knowledge"
)

builder.add_edge(
    "retrieve_knowledge",
    "retrieve_historical_incidents"
)

builder.add_edge(
    "retrieve_historical_incidents",
    "investigate"
)

builder.add_edge(
    "investigate",
    "evaluate_evidence"
)


# ============================================================
# 11. CONDITIONAL ROUTING
# ============================================================

builder.add_conditional_edges(
    "evaluate_evidence",

    route_after_evaluation,

    {
        "complete": END,

        "diagnostics":
            "generate_diagnostics"
    }
)


# ============================================================
# 12. DIAGNOSTICS → HUMAN
# ============================================================

builder.add_edge(
    "generate_diagnostics",
    "request_human_evidence"
)


# ============================================================
# 13. HUMAN → RE-INVESTIGATION
# ============================================================

builder.add_edge(
    "request_human_evidence",
    "investigate"
)


# ============================================================
# 14. CHECKPOINT
# ============================================================

memory = MemorySaver()


incident_graph = builder.compile(
    checkpointer=memory
)


# ============================================================
# 15. TEST
# ============================================================

if __name__ == "__main__":

    test_logs = """
    2026-09-28 11:20:01 INFO Deployment started for recommendation-service
    2026-09-28 11:20:04 INFO Pod recommendation-service-5f76bc created
    2026-09-28 11:20:07 INFO Container started
    2026-09-28 11:20:15 INFO Loading recommendation model
    2026-09-28 11:20:32 INFO Loading model weights: 1.8 GB
    2026-09-28 11:20:45 WARN Memory usage exceeded 80 percent
    2026-09-28 11:20:51 WARN Memory usage exceeded 95 percent
    2026-09-28 11:20:54 ERROR Container terminated
    2026-09-28 11:20:54 ERROR Reason: OOMKilled
    2026-09-28 11:20:55 WARN Container restart initiated
    2026-09-28 11:21:18 ERROR Reason: OOMKilled
    2026-09-28 11:21:19 ERROR CrashLoopBackOff
    2026-09-28 11:21:20 ERROR Deployment failed
    """

    # --------------------------------------------------------
    # IMPORTANT:
    # thread_id identifies this investigation.
    # LangGraph uses it to persist/resume state.
    # --------------------------------------------------------

    config = {
        "configurable": {
            "thread_id": "incident-demo-001"
        }
    }

    print("\n")
    print("=" * 60)
    print("AI SRE COPILOT")
    print("STATEFUL LANGGRAPH INVESTIGATION")
    print("=" * 60)

    # --------------------------------------------------------
    # ROUND 1
    # --------------------------------------------------------

    print("\n")
    print("🚀 Starting investigation...")

    result = incident_graph.invoke(
        {
            "logs": test_logs
        },
        config
    )

    # --------------------------------------------------------
    # Check whether LangGraph paused
    # --------------------------------------------------------

    if "__interrupt__" in result:

        interrupt_data = result[
            "__interrupt__"
        ][0].value

        print("\n")
        print("=" * 60)
        print("🛑 INVESTIGATION PAUSED")
        print("=" * 60)

        print(
            "\nMessage:"
        )

        print(
            interrupt_data["message"]
        )

        print(
            "\nRound:",
            interrupt_data["round"]
        )

        print(
            "\nCurrent hypothesis:"
        )

        print(
            interrupt_data[
                "current_hypothesis"
            ]
        )

        print(
            "\nConfidence:",
            interrupt_data[
                "current_confidence"
            ]
        )

        print(
            "\nMissing evidence:"
        )

        for item in interrupt_data[
            "missing_evidence"
        ]:

            print(
                f"→ {item}"
            )

        print(
            "\nDiagnostic commands:"
        )

        for command in interrupt_data[
            "diagnostic_commands"
        ]:

            print(
                f"→ {command}"
            )

        # ----------------------------------------------------
        # Simulate engineer running commands
        # ----------------------------------------------------

        diagnostic_results = """
Kubernetes diagnostic results:

Pod resource configuration:

recommendation-service:
  Requests:
    memory: 1Gi
  Limits:
    memory: 2Gi

kubectl top pod:

NAME                           MEMORY
recommendation-service-5f76bc  1.95Gi

kubectl top node:

NAME       CPU%   MEMORY%
worker-01  30%    25%

The pod reached approximately 1.95Gi memory usage
before termination.
"""

        print("\n")
        print("=" * 60)
        print("👨‍💻 ENGINEER PROVIDED DIAGNOSTIC EVIDENCE")
        print("=" * 60)

        print(
            diagnostic_results
        )

        # ----------------------------------------------------
        # RESUME GRAPH
        # ----------------------------------------------------

        print("\n")
        print("🔄 Resuming investigation...")

        result = incident_graph.invoke(
            Command(
                resume=diagnostic_results
            ),
            config
        )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n")
    print("=" * 60)
    print("🏁 INVESTIGATION RESULT")
    print("=" * 60)

    print(
        "\nStatus:"
    )

    print(
        result.get(
            "investigation_status"
        )
    )

    print(
        "\nRound:"
    )

    print(
        result.get(
            "investigation_round"
        )
    )

    print(
        "\nEvidence sufficient:"
    )

    print(
        result.get(
            "evidence_sufficient"
        )
    )

    print(
        "\nAI Investigation:"
    )

    print(
        result.get(
            "investigation"
        )
    )

    if result.get(
        "missing_evidence"
    ):

        print(
            "\nRemaining missing evidence:"
        )

        for item in result[
            "missing_evidence"
        ]:

            print(
                f"→ {item}"
            )