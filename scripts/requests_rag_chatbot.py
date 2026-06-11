from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rag.python_library_docs import docs_to_documents, fetch_requests_docs
from src.rag.rag_chain import TechStoreRAGAssistant
from src.rag.text_splitter import split_documents
from src.rag.vector_store import create_or_load_vector_store


DOCS_DIR = Path("docs/python_library_docs/requests")
PERSIST_DIR = Path("chroma_db/requests_docs")
COLLECTION = "requests_docs"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RAG chatbot over the official Requests Python library documentation."
    )
    parser.add_argument("--refresh", action="store_true", help="Fetch official docs before indexing.")
    parser.add_argument("--question", help="Ask one question and exit.")
    args = parser.parse_args()

    load_dotenv()
    if args.refresh or not list(DOCS_DIR.glob("requests_*.txt")):
        fetch_requests_docs(DOCS_DIR)

    documents = docs_to_documents(DOCS_DIR)
    chunks = split_documents(documents)
    vector_store = create_or_load_vector_store(
        persist_directory=PERSIST_DIR,
        collection_name=COLLECTION,
    )
    vector_store.add_documents(chunks)
    assistant = TechStoreRAGAssistant(
        retriever=vector_store,
        system_prompt="You are a Requests Python library documentation assistant.",
        not_found_message="I could not find that answer in the Requests documentation.",
    )

    if args.question:
        print(assistant.answer(args.question))
        return

    print("Requests RAG chatbot. Type 'exit' to quit.")
    while True:
        question = input("Question> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if question:
            print(assistant.answer(question))


if __name__ == "__main__":
    main()
