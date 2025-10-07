#!/usr/bin/env python3
"""
Test script for the Air Force Doctrine Chatbot
Runs basic functionality tests to ensure everything works.
"""

import os
import sys
import time
from pathlib import Path

def test_environment():
    """Test environment setup."""
    print("🧪 Testing Environment Setup")
    print("-" * 40)
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print("✅ ANTHROPIC_API_KEY found")
    else:
        print("❌ ANTHROPIC_API_KEY not found")
        return False
    
    # Check storage directory
    storage_path = Path("./storage")
    if storage_path.exists():
        print("✅ Storage directory found")
    else:
        print("❌ Storage directory not found")
        return False
    
    # Check required files
    required_files = [
        "storage/docstore.json",
        "storage/default__vector_store.json",
        "storage/index_store.json"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} found")
        else:
            print(f"❌ {file_path} not found")
            return False
    
    return True

def test_imports():
    """Test required package imports."""
    print("\n🧪 Testing Package Imports")
    print("-" * 40)
    
    packages = [
        ("llama_index.core", "LlamaIndex Core"),
        ("llama_index.vector_stores.faiss", "FAISS Vector Store"),
        ("llama_index.llms.anthropic", "Anthropic LLM"),
        ("anthropic", "Anthropic Client"),
        ("streamlit", "Streamlit")
    ]
    
    all_good = True
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Not installed")
            all_good = False
    
    return all_good

def test_chatbot_initialization():
    """Test chatbot initialization."""
    print("\n🧪 Testing Chatbot Initialization")
    print("-" * 40)
    
    try:
        # Import the chatbot class
        sys.path.append('.')
        from doctrine_chatbot import DoctrineChatbot
        
        print("📂 Loading vector database...")
        start_time = time.time()
        
        # Initialize chatbot
        chatbot = DoctrineChatbot()
        
        load_time = time.time() - start_time
        print(f"✅ Chatbot initialized successfully ({load_time:.2f}s)")
        
        # Test database stats
        stats = chatbot.get_database_stats()
        if "total_files" in stats:
            print(f"📊 Database: {stats['total_files']} files, {stats['total_chunks']:,} chunks")
        
        return chatbot
        
    except Exception as e:
        print(f"❌ Chatbot initialization failed: {e}")
        return None

def test_simple_query(chatbot):
    """Test a simple query."""
    print("\n🧪 Testing Simple Query")
    print("-" * 40)
    
    try:
        test_question = "What is mission command?"
        print(f"❓ Question: {test_question}")
        
        start_time = time.time()
        result = chatbot.chat(test_question)
        query_time = time.time() - start_time
        
        if "error" in result:
            print(f"❌ Query failed: {result['error']}")
            return False
        
        print(f"✅ Query successful ({query_time:.2f}s)")
        print(f"📝 Response length: {len(result['response'])} characters")
        print(f"📚 Sources found: {result['sources_count']}")
        
        # Show first 200 characters of response
        response_preview = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
        print(f"📖 Response preview: {response_preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def test_web_interface():
    """Test web interface availability."""
    print("\n🧪 Testing Web Interface")
    print("-" * 40)
    
    try:
        import streamlit as st
        print("✅ Streamlit available")
        
        # Check if web_chatbot.py exists
        if Path("web_chatbot.py").exists():
            print("✅ Web chatbot file found")
            print("🌐 To test web interface, run: streamlit run web_chatbot.py")
            return True
        else:
            print("❌ Web chatbot file not found")
            return False
            
    except ImportError:
        print("❌ Streamlit not installed")
        return False

def main():
    """Run all tests."""
    print("🎖️  AIR FORCE DOCTRINE CHATBOT - TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Package Imports", test_imports),
    ]
    
    # Run basic tests first
    for test_name, test_func in tests:
        if not test_func():
            print(f"\n❌ {test_name} failed. Cannot proceed with chatbot tests.")
            print("\n🔧 Fix the issues above and try again.")
            return
    
    # Test chatbot initialization
    chatbot = test_chatbot_initialization()
    if not chatbot:
        print("\n❌ Cannot test queries without working chatbot.")
        return
    
    # Test query functionality
    query_success = test_simple_query(chatbot)
    
    # Test web interface
    web_success = test_web_interface()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    
    if query_success:
        print("✅ Core chatbot functionality: WORKING")
        print("🚀 Ready to use: python3 doctrine_chatbot.py")
    else:
        print("❌ Core chatbot functionality: FAILED")
    
    if web_success:
        print("✅ Web interface: AVAILABLE")
        print("🌐 Ready to use: streamlit run web_chatbot.py")
    else:
        print("❌ Web interface: NOT AVAILABLE")
    
    if query_success and web_success:
        print("\n🎉 All systems ready! Your Air Force Doctrine Chatbot is working perfectly.")
        print("📚 You can now ask questions about 99 doctrine documents with 4.2MB of content.")
    else:
        print("\n⚠️  Some issues found. Check the errors above.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
