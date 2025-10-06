#!/usr/bin/env python3
"""
PDF Question-Answering Agent
Recursively processes PDFs from a directory and builds a vector database for Q&A.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss

# Load environment variables
load_dotenv()


class PDFAgent:
    def __init__(self, pdf_directory, persist_dir="./storage", chunk_size=512, chunk_overlap=50):
        """
        Initialize the PDF Agent.

        Args:
            pdf_directory: Path to directory containing PDFs (searched recursively)
            persist_dir: Directory to store the vector database
            chunk_size: Size of text chunks for embeddings
            chunk_overlap: Overlap between chunks
        """
        self.pdf_directory = Path(pdf_directory)
        self.persist_dir = persist_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.index = None

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
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        if not self.pdf_directory.exists():
            raise ValueError(f"Directory does not exist: {pdf_directory}")

    def build_index(self, force_rebuild=False):
        """
        Build or load the vector index from PDFs.

        Args:
            force_rebuild: If True, rebuild index even if it exists
        """
        # Check if index already exists
        if os.path.exists(self.persist_dir) and not force_rebuild:
            print(f"Loading existing index from {self.persist_dir}...")
            # Load FAISS vector store
            vector_store = FaissVectorStore.from_persist_dir(self.persist_dir)
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store,
                persist_dir=self.persist_dir
            )
            self.index = load_index_from_storage(storage_context)
            print("Index loaded successfully!")
            return

        print(f"Scanning for PDFs in {self.pdf_directory}...")

        # Find all PDFs recursively
        pdf_files = list(self.pdf_directory.rglob("*.pdf"))

        if not pdf_files:
            raise ValueError(f"No PDF files found in {self.pdf_directory}")

        print(f"Found {len(pdf_files)} PDF files")
        print("Loading and processing PDFs...")

        # Load documents from all PDFs
        documents = SimpleDirectoryReader(
            input_dir=str(self.pdf_directory),
            required_exts=[".pdf"],
            recursive=True
        ).load_data()

        print(f"Loaded {len(documents)} document chunks")
        print("Building vector index with FAISS (this may take a while)...")

        # Create FAISS index with dimension 384 (for bge-small-en-v1.5)
        faiss_index = faiss.IndexFlatL2(384)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Build the index
        self.index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )

        # Persist the index
        print(f"Saving index to {self.persist_dir}...")
        self.index.storage_context.persist(persist_dir=self.persist_dir)
        print("Index built and saved successfully!")

    def query(self, question, similarity_top_k=5, response_mode="compact"):
        """
        Query the vector database.

        Args:
            question: The question to ask
            similarity_top_k: Number of similar chunks to retrieve
            response_mode: How to synthesize the response ('compact', 'tree_summarize', etc.)

        Returns:
            Query response with answer and source information
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")

        query_engine = self.index.as_query_engine(
            similarity_top_k=similarity_top_k,
            response_mode=response_mode
        )

        response = query_engine.query(question)
        return response

    def interactive_mode(self):
        """Start an interactive Q&A session."""
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")

        print("\n" + "="*70)
        print("PDF Question-Answering Agent - Interactive Mode")
        print("="*70)
        print("Ask questions about your PDF documents. Type 'quit' or 'exit' to stop.\n")

        while True:
            try:
                question = input("\nQuestion: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                if not question:
                    continue

                print("\nThinking...")
                response = self.query(question)

                print("\n" + "-"*70)
                print("Answer:")
                print("-"*70)
                print(response.response)

                # Show sources if available
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    print("\n" + "-"*70)
                    print("Sources:")
                    print("-"*70)
                    for i, node in enumerate(response.source_nodes, 1):
                        metadata = node.node.metadata
                        file_name = metadata.get('file_name', 'Unknown')
                        page = metadata.get('page_label', 'Unknown')
                        print(f"{i}. {file_name} (Page {page})")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")


def main():
    """Main entry point for the PDF agent."""
    if len(sys.argv) < 2:
        print("Usage: python pdf_agent.py <pdf_directory> [--rebuild]")
        print("\nExample:")
        print("  python pdf_agent.py ./my_pdfs")
        print("  python pdf_agent.py ./my_pdfs --rebuild")
        sys.exit(1)

    pdf_directory = sys.argv[1]
    force_rebuild = "--rebuild" in sys.argv

    # Check for required API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        print("Please create a .env file with your API key or set it as an environment variable")
        sys.exit(1)

    try:
        # Initialize the agent
        agent = PDFAgent(pdf_directory)

        # Build or load the index
        agent.build_index(force_rebuild=force_rebuild)

        # Start interactive mode
        agent.interactive_mode()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
