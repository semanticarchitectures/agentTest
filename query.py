#!/usr/bin/env python3
"""
Simple query script for the PDF agent
Usage: python query.py "your question here"
"""

import os
import sys
from dotenv import load_dotenv
from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.faiss import FaissVectorStore

# Load environment variables
load_dotenv()

# Configure LlamaIndex settings
Settings.llm = Anthropic(
    model="claude-3-5-sonnet-20241022",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    trust_remote_code=True
)

def query(question, persist_dir="./storage", similarity_top_k=3):
    """Query the PDF database."""
    # Load the FAISS vector store
    vector_store = FaissVectorStore.from_persist_dir(persist_dir)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=persist_dir
    )
    index = load_index_from_storage(storage_context)

    # Create query engine
    query_engine = index.as_query_engine(
        similarity_top_k=similarity_top_k,
        response_mode="compact"
    )

    # Query
    response = query_engine.query(question)

    return response

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query.py \"your question here\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    print(f"Question: {question}\n")
    print("Searching PDFs...\n")

    response = query(question)

    print("="*70)
    print("Answer:")
    print("="*70)
    print(response.response)

    # Show sources
    if hasattr(response, 'source_nodes') and response.source_nodes:
        print("\n" + "="*70)
        print("Sources:")
        print("="*70)
        for i, node in enumerate(response.source_nodes, 1):
            metadata = node.node.metadata
            file_name = metadata.get('file_name', 'Unknown')
            page = metadata.get('page_label', 'Unknown')
            score = node.score if hasattr(node, 'score') else 'N/A'
            print(f"{i}. {file_name} (Page {page}) - Relevance: {score}")
