#!/usr/bin/env python3
"""
Air Force Doctrine Web Chatbot
Web interface for the doctrine chatbot using Streamlit.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import streamlit as st
    from llama_index.core import load_index_from_storage, StorageContext
    from llama_index.vector_stores.faiss import FaissVectorStore
    from llama_index.core.chat_engine import SimpleChatEngine
    from llama_index.core.memory import ChatMemoryBuffer
    from llama_index.llms.anthropic import Anthropic
    # from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.core import Settings
    import anthropic
except ImportError as e:
    print(f"❌ Missing required packages. Please install:")
    print("pip install streamlit llama-index llama-index-vector-stores-faiss llama-index-llms-anthropic anthropic")
    sys.exit(1)

# Page configuration
st.set_page_config(
    page_title="Air Force Doctrine Chatbot",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_chatbot():
    """Load and cache the chatbot instance."""
    
    class WebDoctrineChatbot:
        def __init__(self, persist_dir: str = "./storage"):
            self.persist_dir = persist_dir
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            
            if not self.api_key:
                st.error("❌ ANTHROPIC_API_KEY not found! Please set your API key.")
                st.stop()
            
            self._setup_llm()
            self._load_index()
            self._create_chat_engine()
        
        def _setup_llm(self):
            llm = Anthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=self.api_key,
                max_tokens=4000,
                temperature=0.1
            )
            Settings.llm = llm

            # Skip embedding configuration to avoid compatibility issues
            # The database will use its stored embeddings
            pass
        
        def _load_index(self):
            if not os.path.exists(self.persist_dir):
                st.error(f"❌ Storage directory not found: {self.persist_dir}")
                st.stop()
            
            vector_store = FaissVectorStore.from_persist_dir(self.persist_dir)
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store,
                persist_dir=self.persist_dir
            )
            self.index = load_index_from_storage(storage_context)
        
        def _create_chat_engine(self):
            memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
            self.chat_engine = self.index.as_chat_engine(
                chat_mode="context",
                memory=memory,
                system_prompt="""You are an expert Air Force doctrine assistant with access to comprehensive Air Force doctrine publications.

Provide accurate, well-cited responses about Air Force doctrine, strategy, and operations. Always reference specific publications when possible and explain concepts clearly.""",
                verbose=False,
                similarity_top_k=5
            )
        
        def get_database_stats(self):
            try:
                analysis_file = Path("source_files_analysis.json")
                if analysis_file.exists():
                    with open(analysis_file, 'r') as f:
                        analysis = json.load(f)
                    return analysis
                return {"status": "Analysis file not found"}
            except Exception as e:
                return {"error": str(e)}
        
        def chat(self, message: str):
            try:
                start_time = time.time()

                # Use query engine instead of chat engine for better reliability
                query_engine = self.index.as_query_engine(
                    similarity_top_k=5,
                    response_mode="compact"
                )

                response = query_engine.query(message)
                duration = time.time() - start_time

                sources = []
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    for node in response.source_nodes:
                        if hasattr(node, 'metadata') and node.metadata:
                            sources.append({
                                "file_name": node.metadata.get("file_name", "Unknown"),
                                "page": node.metadata.get("page_label", "Unknown"),
                                "score": getattr(node, 'score', 0.0),
                                "text_preview": node.text[:200] + "..." if len(node.text) > 200 else node.text
                            })

                response_text = str(response).strip()
                if not response_text:
                    return {
                        "response": "I apologize, but I couldn't generate a response to your question. This might be due to the query not matching content in the database or a configuration issue.",
                        "duration": round(duration, 2),
                        "sources": sources,
                        "error": "Empty response"
                    }

                return {
                    "response": response_text,
                    "duration": round(duration, 2),
                    "sources": sources
                }

            except Exception as e:
                return {
                    "response": f"Error processing your question: {str(e)}",
                    "duration": 0,
                    "sources": [],
                    "error": str(e)
                }
    
    return WebDoctrineChatbot()

def main():
    """Main Streamlit app."""
    
    # Header
    st.title("🎖️ Air Force Doctrine Chatbot")
    st.markdown("Ask questions about Air Force doctrine, strategy, and operations")
    
    # Initialize chatbot
    try:
        with st.spinner("Loading doctrine database..."):
            chatbot = load_chatbot()
        st.success("✅ Doctrine database loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to load chatbot: {e}")
        st.stop()
    
    # Sidebar with database info
    with st.sidebar:
        st.header("📊 Database Info")
        stats = chatbot.get_database_stats()
        
        if "total_files" in stats:
            st.metric("Total Files", stats["total_files"])
            st.metric("Total Chunks", f"{stats['total_chunks']:,}")
            st.metric("Content Size", f"{round(stats['total_characters']/(1024*1024), 1)} MB")
        
        st.header("💡 Example Questions")
        example_questions = [
            "What is mission command?",
            "Explain counterair operations",
            "What are the principles of targeting?",
            "How does the Air Force conduct intelligence operations?",
            "What is Agile Combat Employment?",
            "Describe force protection doctrine"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question[:20]}"):
                st.session_state.current_question = question
        
        st.header("📚 Available Content")
        if "files" in stats:
            st.write(f"**Major Publications:**")
            major_docs = [
                "AFDP3-0.1 Command and Control",
                "AFDP 3-60 Targeting", 
                "AFDP5-0 Planning",
                "AFDP3-0 Operations",
                "AFDN 25-1 Artificial Intelligence"
            ]
            for doc in major_docs:
                st.write(f"• {doc}")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "current_question" in st.session_state:
        st.session_state.messages.append({
            "role": "user", 
            "content": st.session_state.current_question
        })
        del st.session_state.current_question
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Check if this is an error message
            if message["role"] == "assistant" and message.get("error"):
                if message.get("error") == "Empty response":
                    st.warning(f"⚠️ {message['content']}")
                else:
                    st.error(f"❌ {message['content']}")
            else:
                st.markdown(message["content"])

            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    with st.expander(f"📚 Sources ({len(message['sources'])} found)"):
                        for i, source in enumerate(message["sources"], 1):
                            st.write(f"**{i}. {source['file_name']}** (Page {source['page']})")
                            st.write(f"*Relevance: {source['score']:.2f}*")
                            st.write(f"Preview: {source['text_preview']}")
                            st.divider()

                # Show response time
                if "duration" in message and message["duration"] > 0:
                    st.caption(f"⏱️ Response time: {message['duration']}s")
    
    # Chat input
    if prompt := st.chat_input("Ask about Air Force doctrine..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Searching doctrine database..."):
                result = chatbot.chat(prompt)

                # Check for errors
                if "error" in result:
                    st.error(f"❌ {result['response']}")
                    if result.get("error") != "Empty response":
                        st.write(f"Technical details: {result['error']}")
                else:
                    # Display response
                    st.markdown(result["response"])

                # Store assistant message with sources
                assistant_message = {
                    "role": "assistant",
                    "content": result["response"],
                    "sources": result.get("sources", []),
                    "duration": result.get("duration", 0),
                    "error": result.get("error")
                }
                st.session_state.messages.append(assistant_message)

                # Show sources if available
                if result.get("sources"):
                    with st.expander(f"📚 Sources ({len(result['sources'])} found)"):
                        for i, source in enumerate(result["sources"], 1):
                            st.write(f"**{i}. {source['file_name']}** (Page {source['page']})")
                            st.write(f"*Relevance: {source['score']:.2f}*")
                            st.write(f"Preview: {source['text_preview']}")
                            st.divider()

                # Show response time
                if result.get("duration", 0) > 0:
                    st.caption(f"⏱️ Response time: {result['duration']}s")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("💾 Download Chat"):
            chat_data = {
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.messages,
                "stats": stats
            }
            st.download_button(
                "Download JSON",
                json.dumps(chat_data, indent=2),
                file_name=f"doctrine_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        st.write(f"💬 Messages: {len(st.session_state.messages)}")

if __name__ == "__main__":
    main()
