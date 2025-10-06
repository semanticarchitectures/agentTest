#!/usr/bin/env python3
"""
Simple script to build the index without interactive mode
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss

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
Settings.node_parser = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=50
)

if len(sys.argv) < 2:
    print("Usage: python build_index.py <pdf_directory>")
    sys.exit(1)

pdf_directory = Path(sys.argv[1])
persist_dir = "./storage"

print(f"Scanning for PDFs in {pdf_directory}...")

# Find all PDFs recursively
pdf_files = list(pdf_directory.rglob("*.pdf"))

if not pdf_files:
    raise ValueError(f"No PDF files found in {pdf_directory}")

print(f"Found {len(pdf_files)} PDF files")
print("Loading and processing PDFs...")

# Load documents from all PDFs
documents = SimpleDirectoryReader(
    input_dir=str(pdf_directory),
    required_exts=[".pdf"],
    recursive=True
).load_data()

print(f"Loaded {len(documents)} document chunks")
print("Building vector index with FAISS and local embeddings...")
print("(This will take a while - downloading embedding model on first run)")

# Create FAISS index with dimension 384 (for bge-small-en-v1.5)
faiss_index = faiss.IndexFlatL2(384)
vector_store = FaissVectorStore(faiss_index=faiss_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Build the index
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    show_progress=True
)

# Persist the index
print(f"Saving index to {persist_dir}...")
index.storage_context.persist(persist_dir=persist_dir)
print("Index built and saved successfully!")

# Show storage size
storage_path = Path(persist_dir)
total_size = sum(f.stat().st_size for f in storage_path.glob('**/*') if f.is_file())
print(f"Total storage size: {total_size / (1024*1024):.2f} MB")
