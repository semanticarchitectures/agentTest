#!/usr/bin/env python3
"""
Simple test that bypasses embedding issues
"""

import os
import json
from llama_index.llms.anthropic import Anthropic

def test_simple_llm():
    """Test just the LLM without vector database."""
    print("🎖️  SIMPLE LLM TEST")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found")
        return False
    
    try:
        # Test LLM directly
        llm = Anthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=api_key,
            max_tokens=1000
        )
        
        # Test with a doctrine question
        question = "What is mission command in military doctrine?"
        response = llm.complete(question)
        
        print(f"✅ Question: {question}")
        print(f"✅ Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_database_content():
    """Test reading database content directly."""
    print("\n📚 DATABASE CONTENT TEST")
    print("=" * 50)
    
    try:
        # Read docstore directly
        with open("storage/docstore.json", "r") as f:
            docstore = json.load(f)
        
        # Look for documents
        if "docstore/data" in docstore:
            docs = docstore["docstore/data"]
            print(f"✅ Found {len(docs)} documents in database")
            
            # Sample a few documents
            sample_keys = list(docs.keys())[:3]
            for key in sample_keys:
                doc = docs[key]
                if "__data__" in doc and "text" in doc["__data__"]:
                    text = doc["__data__"]["text"]
                    print(f"📄 Document sample: {text[:100]}...")
                    
                    # Check if it contains mission command content
                    if "mission command" in text.lower():
                        print(f"✅ Found mission command content!")
                        print(f"📝 Content: {text[:300]}...")
                        break
            
            return True
        else:
            print("❌ No documents found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return False

if __name__ == "__main__":
    llm_success = test_simple_llm()
    db_success = test_database_content()
    
    if llm_success and db_success:
        print("\n🎉 Both tests passed! The issue is likely with embedding compatibility.")
        print("💡 Recommendation: Use the web interface or create a new database with compatible embeddings.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
