#!/usr/bin/env python3
"""
Debug script for the Air Force Doctrine Chatbot
"""

import os
from llama_index.core import load_index_from_storage, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.llms.anthropic import Anthropic
from llama_index.core import Settings

def debug_chatbot():
    """Debug the chatbot components step by step."""
    print("🔍 CHATBOT DEBUG")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Test LLM directly
        print("\n1️⃣ Testing LLM directly...")
        llm = Anthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=api_key,
            max_tokens=1000
        )
        
        # Simple test
        response = llm.complete("What is 2+2?")
        print(f"✅ LLM Response: {response}")
        
        # Test with doctrine question
        doctrine_response = llm.complete("What is mission command in military doctrine?")
        print(f"✅ Doctrine Response: {doctrine_response}")
        
        # Load vector database
        print("\n2️⃣ Loading vector database...")
        vector_store = FaissVectorStore.from_persist_dir("./storage")
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir="./storage"
        )
        index = load_index_from_storage(storage_context)
        print("✅ Vector database loaded")
        
        # Test retrieval
        print("\n3️⃣ Testing retrieval...")
        retriever = index.as_retriever(similarity_top_k=3)
        nodes = retriever.retrieve("mission command")
        print(f"✅ Retrieved {len(nodes)} nodes")
        
        for i, node in enumerate(nodes[:2]):
            print(f"Node {i+1}: {node.text[:100]}...")
            print(f"Metadata: {node.metadata}")
        
        # Test query engine with different configurations
        print("\n4️⃣ Testing query engines...")
        
        # Configure settings
        Settings.llm = llm
        
        # Test simple query engine
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )
        
        response = query_engine.query("What is mission command?")
        print(f"✅ Query Engine Response: {response}")
        print(f"Response type: {type(response)}")
        print(f"Response str: {str(response)}")
        
        # Test with different response mode
        query_engine2 = index.as_query_engine(
            similarity_top_k=3,
            response_mode="tree_summarize"
        )
        
        response2 = query_engine2.query("What is mission command?")
        print(f"✅ Tree Summarize Response: {response2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_chatbot()
