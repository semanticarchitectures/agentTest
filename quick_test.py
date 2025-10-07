#!/usr/bin/env python3
"""
Quick test script for the Air Force Doctrine Chatbot
"""

import os
import sys
from doctrine_chatbot import DoctrineChatbot

def test_chatbot():
    """Test the chatbot with a simple query."""
    print("🎖️  QUICK CHATBOT TEST")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found")
        print("💡 Run: source ~/api_keys.txt")
        return False
    
    try:
        # Initialize chatbot
        print("📂 Initializing chatbot...")
        chatbot = DoctrineChatbot()
        
        # Test query
        test_question = "What is mission command?"
        print(f"❓ Testing question: {test_question}")
        
        result = chatbot.chat(test_question)
        
        if "error" in result and result["error"]:
            print(f"❌ Error: {result['error']}")
            return False
        
        if not result.get("response") or result["response"].strip() == "":
            print("❌ Empty response received")
            return False
        
        print("✅ SUCCESS!")
        print(f"📝 Response: {result['response'][:200]}...")
        print(f"📚 Sources found: {result['sources_count']}")
        print(f"⏱️  Duration: {result['duration_seconds']}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_chatbot()
    sys.exit(0 if success else 1)
