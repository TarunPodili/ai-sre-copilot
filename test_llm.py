from analyzer import parse_logs
from rag import search_knowledge
from llm import investigate_incident


logs = """
2026-09-27 10:30:01 INFO Deployment started
2026-09-27 10:30:05 INFO Pod payment-api created
2026-09-27 10:30:08 ERROR Failed to pull image payment-api:v1.8
2026-09-27 10:30:09 ERROR ImagePullBackOff
2026-09-27 10:30:12 ERROR Deployment failed
"""


incident = parse_logs(logs)

query = "\n".join(
    incident["errors"]
)

knowledge = search_knowledge(
    query,
    top_k=3
)

result = investigate_incident(
    incident,
    knowledge
)

print("\n==============================")
print("AI INVESTIGATION RESULT")
print("==============================")

print(result)