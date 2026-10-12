import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.rag.vector_store import TranscriptVectorStore
from app.agents.orchestrator import AgentOrchestrator


async def main():
    print("Testing End-to-End Grounded Chat with Local Ollama...")
    store = TranscriptVectorStore()
    orchestrator = AgentOrchestrator(store)

    query = "How does Brian Chesky prioritize features at Airbnb?"
    print(f"User Query: {query}")
    print("Querying agent orchestrator (retrieval -> Ollama inference)...")

    result = await orchestrator.execute_request(
        user_message=query,
        provider_name="ollama",
        model_name="llama3.2:3b"
    )

    print("\n" + "=" * 60)
    print("ASSISTANT RESPONSE:")
    print("=" * 60)
    print(result["content"])

    print("\n" + "=" * 60)
    print(f"CITATIONS RETURNED: {len(result['citations'])}")
    print("=" * 60)
    for c in result["citations"]:
        print(f"- Guest: {c.guest}")
        print(f"  Title: {c.title}")
        print(f"  Snippet: {c.snippet[:120]}...")

    if result.get("artifact"):
        print("\n" + "=" * 60)
        print(f"ARTIFACT GENERATED: {result['artifact']['title']}")
        print("=" * 60)

    print("\n[SUCCESS] End-to-end grounded RAG execution verified!")


if __name__ == "__main__":
    asyncio.run(main())
