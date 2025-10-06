#!/usr/bin/env python3
"""
Vector Database Verification Script
Comprehensive verification of the PDF vector database build.
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.faiss import FaissVectorStore
import numpy as np

# Load environment variables
load_dotenv()

def setup_settings():
    """Configure LlamaIndex settings."""
    Settings.llm = Anthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5",
        trust_remote_code=True
    )

def verify_storage_files(persist_dir="./storage"):
    """Verify that all required storage files exist and have content."""
    print("="*70)
    print("1. STORAGE FILES VERIFICATION")
    print("="*70)
    
    storage_path = Path(persist_dir)
    if not storage_path.exists():
        print(f"❌ Storage directory does not exist: {persist_dir}")
        return False
    
    required_files = [
        "default__vector_store.json",
        "docstore.json", 
        "index_store.json"
    ]
    
    all_files_exist = True
    total_size = 0
    
    for file_name in required_files:
        file_path = storage_path / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            total_size += size
            print(f"✅ {file_name}: {size:,} bytes ({size/(1024*1024):.2f} MB)")
        else:
            print(f"❌ Missing: {file_name}")
            all_files_exist = False
    
    print(f"\n📊 Total storage size: {total_size:,} bytes ({total_size/(1024*1024):.2f} MB)")
    
    if all_files_exist:
        print("✅ All required storage files present")
    else:
        print("❌ Some storage files are missing")
    
    return all_files_exist

def verify_vector_store_content(persist_dir="./storage"):
    """Verify the vector store contains embeddings."""
    print("\n" + "="*70)
    print("2. VECTOR STORE CONTENT VERIFICATION")
    print("="*70)
    
    try:
        vector_store_path = Path(persist_dir) / "default__vector_store.json"
        
        with open(vector_store_path, 'r') as f:
            vector_data = json.load(f)
        
        # Check if we have embeddings
        if 'embedding_dict' in vector_data:
            num_embeddings = len(vector_data['embedding_dict'])
            print(f"✅ Found {num_embeddings:,} embeddings in vector store")
            
            # Sample a few embeddings to check dimensions
            if num_embeddings > 0:
                sample_key = list(vector_data['embedding_dict'].keys())[0]
                sample_embedding = vector_data['embedding_dict'][sample_key]
                embedding_dim = len(sample_embedding)
                print(f"✅ Embedding dimension: {embedding_dim} (expected: 384)")
                
                if embedding_dim == 384:
                    print("✅ Embedding dimensions match expected model output")
                else:
                    print(f"⚠️  Unexpected embedding dimension: {embedding_dim}")
            
            return num_embeddings > 0
        else:
            print("❌ No embeddings found in vector store")
            return False
            
    except Exception as e:
        print(f"❌ Error reading vector store: {e}")
        return False

def verify_document_store(persist_dir="./storage"):
    """Verify the document store contains text chunks."""
    print("\n" + "="*70)
    print("3. DOCUMENT STORE VERIFICATION")
    print("="*70)
    
    try:
        docstore_path = Path(persist_dir) / "docstore.json"
        
        with open(docstore_path, 'r') as f:
            docstore_data = json.load(f)
        
        if 'docstore/data' in docstore_data:
            documents = docstore_data['docstore/data']
            num_docs = len(documents)
            print(f"✅ Found {num_docs:,} document chunks in docstore")
            
            # Analyze document content
            if num_docs > 0:
                # Sample document analysis
                sample_doc = list(documents.values())[0]
                if 'text' in sample_doc:
                    sample_text = sample_doc['text']
                    print(f"✅ Sample text length: {len(sample_text)} characters")
                    print(f"📄 Sample text preview: {sample_text[:200]}...")
                
                # Check for metadata
                if 'metadata' in sample_doc:
                    metadata = sample_doc['metadata']
                    if 'file_name' in metadata:
                        print(f"✅ Documents have file metadata: {metadata['file_name']}")
                
                # Count unique source files
                source_files = set()
                for doc in documents.values():
                    if 'metadata' in doc and 'file_name' in doc['metadata']:
                        source_files.add(doc['metadata']['file_name'])
                
                print(f"📚 Number of unique source files: {len(source_files)}")
                if source_files:
                    print("📁 Source files:")
                    for i, file_name in enumerate(sorted(source_files), 1):
                        print(f"   {i}. {file_name}")
            
            return num_docs > 0
        else:
            print("❌ No documents found in docstore")
            return False
            
    except Exception as e:
        print(f"❌ Error reading docstore: {e}")
        return False

def verify_index_loading(persist_dir="./storage"):
    """Verify that the index can be loaded successfully."""
    print("\n" + "="*70)
    print("4. INDEX LOADING VERIFICATION")
    print("="*70)
    
    try:
        setup_settings()
        
        # Load the FAISS vector store
        vector_store = FaissVectorStore.from_persist_dir(persist_dir)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir=persist_dir
        )
        index = load_index_from_storage(storage_context)
        
        print("✅ Index loaded successfully")
        
        # Get some basic stats
        if hasattr(index, '_vector_store') and hasattr(index._vector_store, '_faiss_index'):
            faiss_index = index._vector_store._faiss_index
            if hasattr(faiss_index, 'ntotal'):
                print(f"✅ FAISS index contains {faiss_index.ntotal:,} vectors")
        
        return True, index
        
    except Exception as e:
        print(f"❌ Error loading index: {e}")
        return False, None

def test_basic_query(index, test_questions=None):
    """Test basic querying functionality."""
    print("\n" + "="*70)
    print("5. BASIC QUERY TESTING")
    print("="*70)
    
    if index is None:
        print("❌ Cannot test queries - index not loaded")
        return False
    
    if test_questions is None:
        test_questions = [
            "What is this document about?",
            "summary",
            "main topics"
        ]
    
    try:
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🔍 Test Query {i}: '{question}'")
            try:
                response = query_engine.query(question)
                
                if response and response.response:
                    print(f"✅ Query successful - Response length: {len(response.response)} chars")
                    print(f"📝 Response preview: {response.response[:150]}...")
                    
                    # Check sources
                    if hasattr(response, 'source_nodes') and response.source_nodes:
                        print(f"📚 Found {len(response.source_nodes)} source chunks")
                        for j, node in enumerate(response.source_nodes[:2], 1):
                            if hasattr(node, 'score'):
                                print(f"   Source {j} relevance score: {node.score:.3f}")
                    else:
                        print("⚠️  No source nodes returned")
                else:
                    print("⚠️  Empty response received")
                    
            except Exception as e:
                print(f"❌ Query failed: {e}")
                return False
        
        print("\n✅ All test queries completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up query engine: {e}")
        return False

def main():
    """Run comprehensive verification."""
    print("PDF VECTOR DATABASE VERIFICATION")
    print("="*70)
    
    persist_dir = "./storage"
    
    # Run all verification steps
    results = []
    
    # 1. Storage files
    results.append(verify_storage_files(persist_dir))
    
    # 2. Vector store content
    results.append(verify_vector_store_content(persist_dir))
    
    # 3. Document store
    results.append(verify_document_store(persist_dir))
    
    # 4. Index loading
    index_loaded, index = verify_index_loading(persist_dir)
    results.append(index_loaded)
    
    # 5. Query testing
    if index_loaded:
        results.append(test_basic_query(index))
    else:
        results.append(False)
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    test_names = [
        "Storage Files",
        "Vector Store Content", 
        "Document Store",
        "Index Loading",
        "Query Testing"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, result) in enumerate(zip(test_names, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i}. {test_name}: {status}")
    
    print(f"\n📊 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Vector database verification SUCCESSFUL!")
        print("Your database is ready for use.")
    else:
        print("⚠️  Some issues detected. Please review the failed tests above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
