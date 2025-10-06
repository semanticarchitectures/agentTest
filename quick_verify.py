#!/usr/bin/env python3
"""
Quick Vector Database Verification
Fast checks to verify your vector database is working.
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def quick_verify(persist_dir="./storage"):
    """Quick verification of vector database."""
    print("🔍 Quick Vector Database Verification")
    print("="*50)
    
    storage_path = Path(persist_dir)
    
    # 1. Check if storage directory exists
    if not storage_path.exists():
        print(f"❌ Storage directory missing: {persist_dir}")
        return False
    
    print(f"✅ Storage directory exists: {persist_dir}")
    
    # 2. Check required files
    required_files = [
        "default__vector_store.json",
        "docstore.json",
        "index_store.json"
    ]
    
    missing_files = []
    total_size = 0
    
    for file_name in required_files:
        file_path = storage_path / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            total_size += size
            print(f"✅ {file_name}: {size/(1024*1024):.1f} MB")
        else:
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    # 3. Check vector store content
    try:
        vector_store_path = storage_path / "default__vector_store.json"
        with open(vector_store_path, 'r') as f:
            vector_data = json.load(f)
        
        if 'embedding_dict' in vector_data:
            num_embeddings = len(vector_data['embedding_dict'])
            print(f"✅ Vector embeddings: {num_embeddings:,}")
        else:
            print("❌ No embeddings found")
            return False
    except Exception as e:
        print(f"❌ Error reading vector store: {e}")
        return False
    
    # 4. Check document store
    try:
        docstore_path = storage_path / "docstore.json"
        with open(docstore_path, 'r') as f:
            docstore_data = json.load(f)
        
        if 'docstore/data' in docstore_data:
            documents = docstore_data['docstore/data']
            num_docs = len(documents)
            print(f"✅ Document chunks: {num_docs:,}")
            
            # Count unique source files
            source_files = set()
            for doc in documents.values():
                if 'metadata' in doc and 'file_name' in doc['metadata']:
                    source_files.add(doc['metadata']['file_name'])
            
            print(f"✅ Source PDF files: {len(source_files)}")
        else:
            print("❌ No documents found")
            return False
    except Exception as e:
        print(f"❌ Error reading docstore: {e}")
        return False
    
    print(f"\n📊 Total storage: {total_size/(1024*1024):.1f} MB")
    print("🎉 Quick verification PASSED!")
    print("\nTo test queries, run:")
    print('python query.py "your question here"')
    
    return True

def test_simple_query():
    """Test if we can load and query the index."""
    print("\n🔍 Testing Query Capability...")
    
    try:
        from llama_index.core import StorageContext, load_index_from_storage, Settings
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        from llama_index.llms.anthropic import Anthropic
        from llama_index.vector_stores.faiss import FaissVectorStore
        
        # Configure settings
        Settings.llm = Anthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            trust_remote_code=True
        )
        
        # Load index
        vector_store = FaissVectorStore.from_persist_dir("./storage")
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir="./storage"
        )
        index = load_index_from_storage(storage_context)
        
        print("✅ Index loaded successfully")
        
        # Test a simple query
        query_engine = index.as_query_engine(similarity_top_k=2)
        response = query_engine.query("What is this about?")
        
        if response and response.response:
            print("✅ Query test successful")
            print(f"📝 Response preview: {response.response[:100]}...")
            return True
        else:
            print("❌ Query returned empty response")
            return False
            
    except ImportError as e:
        print(f"⚠️  Cannot test queries - missing dependencies: {e}")
        return None
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

if __name__ == "__main__":
    # Run quick verification
    basic_ok = quick_verify()
    
    if basic_ok:
        # Test query capability if API key is available
        if os.getenv("ANTHROPIC_API_KEY"):
            query_ok = test_simple_query()
            if query_ok is False:
                sys.exit(1)
        else:
            print("\n⚠️  ANTHROPIC_API_KEY not set - skipping query test")
    else:
        sys.exit(1)
