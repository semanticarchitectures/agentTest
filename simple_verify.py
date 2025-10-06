#!/usr/bin/env python3
"""
Simple Vector Database Verification (no external dependencies)
Basic checks to verify your vector database files.
"""

import os
import json
import sys
from pathlib import Path

def simple_verify(persist_dir="./storage"):
    """Simple verification of vector database files."""
    print("🔍 Simple Vector Database Verification")
    print("="*50)
    
    storage_path = Path(persist_dir)
    
    # 1. Check if storage directory exists
    if not storage_path.exists():
        print(f"❌ Storage directory missing: {persist_dir}")
        return False
    
    print(f"✅ Storage directory exists: {persist_dir}")
    
    # 2. Check required files and their sizes
    required_files = [
        "default__vector_store.json",
        "docstore.json",
        "index_store.json"
    ]
    
    missing_files = []
    total_size = 0
    file_info = {}
    
    for file_name in required_files:
        file_path = storage_path / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            total_size += size
            file_info[file_name] = size
            print(f"✅ {file_name}: {size:,} bytes ({size/(1024*1024):.1f} MB)")
        else:
            missing_files.append(file_name)
            print(f"❌ Missing: {file_name}")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    # 3. Validate file contents
    print("\n📋 Validating file contents...")
    
    # Check vector store (FAISS binary format)
    try:
        vector_store_path = storage_path / "default__vector_store.json"
        vector_size = vector_store_path.stat().st_size

        # FAISS files are binary, so we check size and basic structure
        if vector_size > 1000:  # Should be substantial if it contains embeddings
            print(f"✅ Vector store (FAISS binary): {vector_size:,} bytes")

            # Try to read the first few bytes to check FAISS signature
            with open(vector_store_path, 'rb') as f:
                header = f.read(4)
                if header.startswith(b'IxF'):  # FAISS file signature
                    print("✅ Valid FAISS file format detected")
                else:
                    print("⚠️  Unexpected file format (not standard FAISS)")
        else:
            print("❌ Vector store file too small")
            return False

    except Exception as e:
        print(f"❌ Error reading vector store: {e}")
        return False
    
    # Check document store
    try:
        docstore_path = storage_path / "docstore.json"
        with open(docstore_path, 'r') as f:
            docstore_data = json.load(f)
        
        if 'docstore/data' in docstore_data:
            documents = docstore_data['docstore/data']
            num_docs = len(documents)
            print(f"✅ Document chunks: {num_docs:,}")
            
            # Analyze documents
            if num_docs > 0:
                # Count unique source files
                source_files = set()
                total_text_length = 0
                
                for doc in documents.values():
                    if 'metadata' in doc and 'file_name' in doc['metadata']:
                        source_files.add(doc['metadata']['file_name'])
                    if 'text' in doc:
                        total_text_length += len(doc['text'])
                
                print(f"✅ Source PDF files: {len(source_files)}")
                print(f"✅ Total text content: {total_text_length:,} characters")
                
                if source_files:
                    print("📁 Source files found:")
                    for i, filename in enumerate(sorted(source_files), 1):
                        print(f"   {i}. {filename}")
            else:
                print("❌ No documents found in docstore")
                return False
        else:
            print("❌ No documents found in docstore")
            return False
            
    except json.JSONDecodeError:
        print("❌ Document store file is corrupted (invalid JSON)")
        return False
    except Exception as e:
        print(f"❌ Error reading docstore: {e}")
        return False
    
    # Check index store
    try:
        index_store_path = storage_path / "index_store.json"
        with open(index_store_path, 'r') as f:
            index_data = json.load(f)
        
        if 'index_store/data' in index_data:
            print("✅ Index store structure valid")
        else:
            print("⚠️  Index store structure unexpected")
            
    except json.JSONDecodeError:
        print("❌ Index store file is corrupted (invalid JSON)")
        return False
    except Exception as e:
        print(f"❌ Error reading index store: {e}")
        return False
    
    # Summary
    print(f"\n📊 Storage Summary:")
    print(f"   Total size: {total_size:,} bytes ({total_size/(1024*1024):.1f} MB)")
    print(f"   Vector store: {vector_size:,} bytes (FAISS binary)")
    print(f"   Documents: {num_docs:,}")
    print(f"   Source files: {len(source_files)}")
    
    # Size validation
    if total_size < 1024:  # Less than 1KB is suspicious
        print("⚠️  Storage size seems very small - database might be empty")
        return False
    
    print("\n🎉 Simple verification PASSED!")
    print("\nNext steps to test functionality:")
    print("1. Run: python3 query.py \"What is this document about?\"")
    print("2. Run: python3 pdf_agent.py <your_pdf_directory>")
    print("3. Run: python3 verify_vector_db.py (for comprehensive testing)")
    
    return True

def check_dependencies():
    """Check if required dependencies are available."""
    print("\n🔍 Checking Dependencies...")
    
    required_packages = [
        'llama_index',
        'faiss',
        'transformers',
        'torch',
        'anthropic'
    ]
    
    available = []
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            available.append(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install llama-index faiss-cpu transformers torch anthropic")
        return False
    else:
        print("\n✅ All required packages available")
        return True

if __name__ == "__main__":
    print("VECTOR DATABASE VERIFICATION")
    print("="*50)
    
    # Run simple file verification
    files_ok = simple_verify()
    
    if files_ok:
        # Check if we can test functionality
        deps_ok = check_dependencies()
        
        if not deps_ok:
            print("\n⚠️  Cannot test query functionality - install missing packages")
            print("But your vector database files appear to be valid!")
    
    sys.exit(0 if files_ok else 1)
