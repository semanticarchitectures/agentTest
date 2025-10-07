#!/usr/bin/env python3
"""
Demo script for the Air Force Doctrine Chatbot
Shows example interactions and capabilities.
"""

import os
import sys
import time
from datetime import datetime

def run_demo():
    """Run a demonstration of the chatbot."""
    
    print("🎖️  AIR FORCE DOCTRINE CHATBOT - DEMO")
    print("=" * 50)
    print("This demo shows how the chatbot works with your doctrine database.")
    print("The chatbot has access to 99 Air Force doctrine documents.")
    print("=" * 50)
    
    # Check if we can actually run the demo
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Demo requires ANTHROPIC_API_KEY to be set")
        print("This is just a preview of what the chatbot would do.")
        print("\n🔑 To run the real chatbot:")
        print("1. Set your API key: export ANTHROPIC_API_KEY='your_key'")
        print("2. Run: python3 doctrine_chatbot.py")
        return
    
    try:
        # Try to import and initialize
        from doctrine_chatbot import DoctrineChatbot
        
        print("📂 Loading doctrine database...")
        chatbot = DoctrineChatbot()
        
        # Demo questions
        demo_questions = [
            "What is mission command?",
            "How does the Air Force conduct counterair operations?",
            "What are the principles of targeting?",
            "Explain Agile Combat Employment",
            "What role does artificial intelligence play in Air Force operations?"
        ]
        
        print(f"\n🎯 Running {len(demo_questions)} demo questions...")
        print("=" * 50)
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n📝 Demo Question {i}/{len(demo_questions)}")
            print(f"❓ {question}")
            print("-" * 40)
            
            start_time = time.time()
            result = chatbot.chat(question)
            duration = time.time() - start_time
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            # Show response preview
            response = result['response']
            if len(response) > 300:
                response_preview = response[:300] + "..."
            else:
                response_preview = response
            
            print(f"🤖 Response: {response_preview}")
            
            # Show sources
            if result['sources_count'] > 0:
                print(f"\n📚 Sources ({result['sources_count']} found):")
                for j, source in enumerate(result['sources'][:2], 1):
                    print(f"  {j}. {source['file_name']} (Page {source['page']}) - Relevance: {source['score']:.2f}")
            
            print(f"⏱️  Response time: {duration:.2f}s")
            
            # Pause between questions
            if i < len(demo_questions):
                time.sleep(1)
        
        # Show session summary
        print("\n" + "=" * 50)
        print("📊 DEMO SUMMARY")
        print("=" * 50)
        print(f"Questions asked: {len(demo_questions)}")
        print(f"Total responses: {len(chatbot.chat_history)}")
        
        # Save demo session
        filename = chatbot.save_session("demo_session.json")
        print(f"💾 Demo session saved to: {filename}")
        
        print("\n🎉 Demo completed successfully!")
        print("\n🚀 Ready to try the full chatbot:")
        print("   • Command line: python3 doctrine_chatbot.py")
        print("   • Web interface: streamlit run web_chatbot.py")
        
    except ImportError:
        print("❌ Required packages not installed")
        print("Install with: pip install -r chatbot_requirements.txt")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\n🔧 Try running the test first: python3 test_chatbot.py")

def show_mock_demo():
    """Show a mock demo when real chatbot can't run."""
    
    print("🎬 MOCK DEMO - Air Force Doctrine Chatbot")
    print("=" * 50)
    print("This shows what the chatbot would do with your doctrine database.")
    print("=" * 50)
    
    mock_interactions = [
        {
            "question": "What is mission command?",
            "response": "Mission command is the conduct of military operations through decentralized execution based on mission-type orders. It requires commanders to provide clear intent and guidance while empowering subordinates to exercise disciplined initiative within the commander's intent. The philosophy emphasizes trust, mutual understanding, and shared purpose between commanders and subordinates.",
            "sources": [
                {"file": "AFDP 1-1 Mission Command.pdf", "page": "5", "score": 0.89},
                {"file": "AFDP3-0Operations.pdf", "page": "12", "score": 0.82}
            ],
            "duration": 2.3
        },
        {
            "question": "How does the Air Force conduct counterair operations?",
            "response": "Counterair operations are conducted to attain and maintain a desired degree of control of the air by the destruction or neutralization of enemy forces. These operations include both offensive counterair (OCA) and defensive counterair (DCA). OCA operations destroy, disrupt, or limit enemy air and missile threats at their source, while DCA operations detect, identify, intercept, and destroy enemy forces attempting to attack friendly forces.",
            "sources": [
                {"file": "3-01-AFDP-COUNTERAIR.pdf", "page": "8", "score": 0.91},
                {"file": "AFDP3-0Operations.pdf", "page": "23", "score": 0.85}
            ],
            "duration": 2.7
        },
        {
            "question": "What are the principles of targeting?",
            "response": "The targeting process follows six key principles: 1) Focus on achieving the commander's objectives, 2) Understand the operational environment, 3) Think systematically about effects, 4) Apply appropriate capabilities against targets, 5) Assess results and adapt, and 6) Coordinate with joint and coalition partners. The targeting cycle consists of decide, detect, deliver, and assess phases.",
            "sources": [
                {"file": "3-60-AFDP-TARGETING.pdf", "page": "15", "score": 0.93},
                {"file": "AFDP5-0Planning.pdf", "page": "34", "score": 0.78}
            ],
            "duration": 3.1
        }
    ]
    
    for i, interaction in enumerate(mock_interactions, 1):
        print(f"\n📝 Example {i}")
        print(f"❓ {interaction['question']}")
        print("-" * 40)
        print(f"🤖 {interaction['response']}")
        print(f"\n📚 Sources ({len(interaction['sources'])} found):")
        for j, source in enumerate(interaction['sources'], 1):
            print(f"  {j}. {source['file']} (Page {source['page']}) - Relevance: {source['score']}")
        print(f"⏱️  Response time: {interaction['duration']}s")
    
    print("\n" + "=" * 50)
    print("🎯 CAPABILITIES DEMONSTRATED")
    print("=" * 50)
    print("✅ Natural language question answering")
    print("✅ Multi-document information synthesis") 
    print("✅ Source citation with relevance scores")
    print("✅ Page-level references to doctrine publications")
    print("✅ Fast response times (2-3 seconds)")
    
    print("\n🚀 TO USE THE REAL CHATBOT:")
    print("1. Set API key: export ANTHROPIC_API_KEY='your_key'")
    print("2. Install packages: pip install -r chatbot_requirements.txt")
    print("3. Run: python3 doctrine_chatbot.py")

def main():
    """Main demo function."""
    
    # Check if we can run the real demo
    if os.getenv("ANTHROPIC_API_KEY") and os.path.exists("./storage"):
        try:
            run_demo()
        except Exception as e:
            print(f"❌ Real demo failed: {e}")
            print("\n🎬 Showing mock demo instead...")
            show_mock_demo()
    else:
        show_mock_demo()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
