#!/usr/bin/env python3
"""
Air Force Doctrine Interactive Chatbot
Connects to the vector database and answers questions about doctrine content.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from llama_index.core import load_index_from_storage, StorageContext
    from llama_index.vector_stores.faiss import FaissVectorStore
    from llama_index.core.chat_engine import SimpleChatEngine
    from llama_index.core.memory import ChatMemoryBuffer
    from llama_index.llms.anthropic import Anthropic
    # from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.core import Settings
    import anthropic
except ImportError as e:
    print(f"❌ Missing required packages. Please install:")
    print("pip install llama-index llama-index-vector-stores-faiss llama-index-llms-anthropic anthropic")
    sys.exit(1)

class DoctrineChatbot:
    """Interactive chatbot for Air Force doctrine queries."""
    
    def __init__(self, persist_dir: str = "./storage", api_key: Optional[str] = None):
        """Initialize the chatbot with vector database connection."""
        self.persist_dir = persist_dir
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.index = None
        self.chat_engine = None
        self.chat_history = []
        self.session_start = datetime.now()
        
        # Validate API key
        if not self.api_key:
            print("❌ ANTHROPIC_API_KEY not found!")
            print("Set it with: export ANTHROPIC_API_KEY='your_key_here'")
            sys.exit(1)
        
        # Initialize the system
        self._setup_llm()
        self._load_index()
        self._create_chat_engine()
        
    def _setup_llm(self):
        """Configure the LLM and embedding model settings."""
        try:
            # Configure Anthropic LLM
            llm = Anthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=self.api_key,
                max_tokens=4000,
                temperature=0.1
            )
            Settings.llm = llm

            # Skip embedding configuration for now to avoid compatibility issues
            # The database will use its stored embeddings
            pass

            print("✅ LLM and embedding model configured successfully")
        except Exception as e:
            print(f"❌ Error configuring LLM/embeddings: {e}")
            sys.exit(1)
    
    def _load_index(self):
        """Load the vector database index."""
        try:
            if not os.path.exists(self.persist_dir):
                print(f"❌ Storage directory not found: {self.persist_dir}")
                sys.exit(1)
            
            print(f"📂 Loading vector database from {self.persist_dir}...")
            
            # Load FAISS vector store
            vector_store = FaissVectorStore.from_persist_dir(self.persist_dir)
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store,
                persist_dir=self.persist_dir
            )
            
            # Load the index (READ-ONLY)
            self.index = load_index_from_storage(storage_context)
            print("✅ Vector database loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading vector database: {e}")
            sys.exit(1)
    
    def _create_chat_engine(self):
        """Create the chat engine with memory."""
        try:
            # Create chat memory
            memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
            
            # Create chat engine
            self.chat_engine = self.index.as_chat_engine(
                chat_mode="context",
                memory=memory,
                system_prompt="""You are an expert Air Force doctrine assistant. You have access to comprehensive Air Force doctrine publications, including AFDPs, AFDNs, training materials, and operational guidance.

Your role is to:
1. Answer questions about Air Force doctrine, strategy, and operations
2. Provide specific references to doctrine publications when possible
3. Explain complex concepts in clear, accessible language
4. Cite specific pages or sections when referencing doctrine
5. Maintain accuracy and avoid speculation beyond the provided content

When answering:
- Be precise and cite specific doctrine publications
- Use military terminology appropriately
- Provide context for doctrine concepts
- Reference page numbers or sections when available
- If information isn't in the database, clearly state that

You have access to 99 Air Force doctrine documents covering operations, intelligence, support, leadership, and specialized functions.""",
                verbose=True,
                similarity_top_k=5
            )
            print("✅ Chat engine created successfully")
            
        except Exception as e:
            print(f"❌ Error creating chat engine: {e}")
            sys.exit(1)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded database."""
        try:
            # Load source analysis if available
            analysis_file = Path("source_files_analysis.json")
            if analysis_file.exists():
                with open(analysis_file, 'r') as f:
                    analysis = json.load(f)
                return {
                    "total_files": analysis.get("total_files", "Unknown"),
                    "total_chunks": analysis.get("total_chunks", "Unknown"),
                    "total_characters": analysis.get("total_characters", "Unknown"),
                    "content_size_mb": round(analysis.get("total_characters", 0) / (1024*1024), 2)
                }
            else:
                return {"status": "Analysis file not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Send a message to the chatbot and get response."""
        try:
            start_time = time.time()

            # Get response from chat engine
            response = self.chat_engine.chat(message)

            end_time = time.time()
            duration = end_time - start_time

            # Extract source information
            sources = []
            if hasattr(response, 'source_nodes') and response.source_nodes:
                for node in response.source_nodes:
                    if hasattr(node, 'metadata') and node.metadata:
                        source_info = {
                            "file_name": node.metadata.get("file_name", "Unknown"),
                            "page": node.metadata.get("page_label", "Unknown"),
                            "score": getattr(node, 'score', 0.0),
                            "text_preview": node.text[:200] + "..." if len(node.text) > 200 else node.text
                        }
                        sources.append(source_info)

            # Check if response is empty
            response_text = str(response).strip()
            if not response_text:
                error_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "question": message,
                    "error": "Empty response from chat engine. This may indicate an issue with the LLM configuration or query processing.",
                    "duration_seconds": round(duration, 2),
                    "sources_count": len(sources),
                    "sources": sources
                }
                self.chat_history.append(error_entry)
                return error_entry

            # Store in chat history
            chat_entry = {
                "timestamp": datetime.now().isoformat(),
                "question": message,
                "response": response_text,
                "duration_seconds": round(duration, 2),
                "sources_count": len(sources),
                "sources": sources
            }
            self.chat_history.append(chat_entry)

            return chat_entry

        except Exception as e:
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "question": message,
                "error": str(e),
                "duration_seconds": 0,
                "sources_count": 0,
                "sources": []
            }
            self.chat_history.append(error_entry)
            return error_entry
    
    def save_session(self, filename: Optional[str] = None):
        """Save the chat session to a file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_session_{timestamp}.json"
        
        session_data = {
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "total_questions": len(self.chat_history),
            "database_stats": self.get_database_stats(),
            "chat_history": self.chat_history
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def print_welcome(self):
        """Print welcome message and database info."""
        print("\n" + "="*70)
        print("🎖️  AIR FORCE DOCTRINE CHATBOT")
        print("="*70)
        
        stats = self.get_database_stats()
        if "total_files" in stats:
            print(f"📚 Database: {stats['total_files']} doctrine files")
            print(f"📄 Content: {stats['total_chunks']:,} chunks ({stats['content_size_mb']} MB)")
        
        print(f"🤖 Model: Claude 3.5 Sonnet")
        print(f"🔍 Search: Vector similarity with source citations")
        print("="*70)
        print("\n💡 Ask me about Air Force doctrine, operations, strategy, or procedures!")
        print("📖 I can reference specific AFDPs, AFDNs, and training materials.")
        print("\n🔧 Commands:")
        print("  'help' - Show available commands")
        print("  'stats' - Show database statistics") 
        print("  'history' - Show recent questions")
        print("  'save' - Save chat session")
        print("  'quit' or 'exit' - End session")
        print("-"*70)

def main():
    """Main interactive chat loop."""
    print("🚀 Starting Air Force Doctrine Chatbot...")
    
    # Initialize chatbot
    try:
        chatbot = DoctrineChatbot()
    except KeyboardInterrupt:
        print("\n👋 Startup cancelled by user")
        return
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        return
    
    # Show welcome message
    chatbot.print_welcome()
    
    # Main chat loop
    try:
        while True:
            try:
                # Get user input
                user_input = input("\n🎖️  Ask about doctrine: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    print("\n📋 Available Commands:")
                    print("  help - Show this help message")
                    print("  stats - Show database statistics")
                    print("  history - Show recent chat history")
                    print("  save - Save current session")
                    print("  quit/exit - End the session")
                    print("\n💡 Example questions:")
                    print("  'What is mission command?'")
                    print("  'Explain counterair operations'")
                    print("  'What are the principles of targeting?'")
                    continue
                elif user_input.lower() == 'stats':
                    stats = chatbot.get_database_stats()
                    print(f"\n📊 Database Statistics:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                    continue
                elif user_input.lower() == 'history':
                    print(f"\n📜 Recent Questions ({len(chatbot.chat_history)} total):")
                    for i, entry in enumerate(chatbot.chat_history[-5:], 1):
                        print(f"  {i}. {entry['question'][:60]}...")
                    continue
                elif user_input.lower() == 'save':
                    filename = chatbot.save_session()
                    print(f"💾 Session saved to: {filename}")
                    continue
                
                # Process question
                print("🔍 Searching doctrine database...")
                result = chatbot.chat(user_input)
                
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    print(f"\n📖 Response:")
                    print(f"{result['response']}")
                    
                    if result['sources']:
                        print(f"\n📚 Sources ({result['sources_count']} found):")
                        for i, source in enumerate(result['sources'][:3], 1):
                            print(f"  {i}. {source['file_name']} (Page {source['page']}) - Score: {source['score']:.2f}")
                    
                    print(f"\n⏱️  Response time: {result['duration_seconds']}s")
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error processing question: {e}")
                continue
    
    finally:
        # Save session on exit
        if chatbot.chat_history:
            try:
                filename = chatbot.save_session()
                print(f"\n💾 Chat session automatically saved to: {filename}")
            except Exception as e:
                print(f"⚠️  Could not save session: {e}")
        
        print(f"\n📊 Session Summary:")
        print(f"  Questions asked: {len(chatbot.chat_history)}")
        print(f"  Session duration: {datetime.now() - chatbot.session_start}")
        print("\n🎖️  Thank you for using the Air Force Doctrine Chatbot!")

if __name__ == "__main__":
    main()
