#!/usr/bin/env python3
"""
Working Air Force Doctrine Chatbot - Bypasses embedding issues
"""

import os
import json
import time
import streamlit as st
from datetime import datetime
from llama_index.llms.anthropic import Anthropic

class WorkingDoctrineChatbot:
    """A working chatbot that bypasses vector search issues."""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            st.error("❌ ANTHROPIC_API_KEY not found! Please set your API key.")
            st.stop()
        
        self.llm = Anthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=self.api_key,
            max_tokens=4000,
            temperature=0.1
        )
        
        self.documents = self._load_documents()
        
    def _load_documents(self):
        """Load documents directly from the docstore."""
        try:
            with open("storage/docstore.json", "r") as f:
                docstore = json.load(f)
            
            documents = []
            if "docstore/data" in docstore:
                for doc_id, doc_data in docstore["docstore/data"].items():
                    if "__data__" in doc_data and "text" in doc_data["__data__"]:
                        text = doc_data["__data__"]["text"]
                        metadata = doc_data["__data__"].get("metadata", {})
                        
                        documents.append({
                            "id": doc_id,
                            "text": text,
                            "metadata": metadata,
                            "file_name": metadata.get("file_name", "Unknown"),
                            "page": metadata.get("page_label", "Unknown")
                        })
            
            return documents
            
        except Exception as e:
            st.error(f"Error loading documents: {e}")
            return []
    
    def _search_documents(self, query, max_results=5):
        """Simple text-based search through documents."""
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            text_lower = doc["text"].lower()
            
            # Simple relevance scoring based on keyword matches
            score = 0
            query_words = query_lower.split()
            
            for word in query_words:
                if len(word) > 2:  # Skip very short words
                    score += text_lower.count(word)
            
            if score > 0:
                results.append({
                    "document": doc,
                    "score": score,
                    "preview": doc["text"][:300] + "..." if len(doc["text"]) > 300 else doc["text"]
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    def chat(self, message):
        """Process a chat message and return response."""
        try:
            start_time = time.time()
            
            # Search for relevant documents
            search_results = self._search_documents(message)
            
            if not search_results:
                return {
                    "response": "I couldn't find specific information about that topic in the Air Force doctrine database. Could you try rephrasing your question or asking about a different doctrine topic?",
                    "duration": time.time() - start_time,
                    "sources": [],
                    "error": "No relevant documents found"
                }
            
            # Prepare context from search results
            context_parts = []
            sources = []
            
            for i, result in enumerate(search_results):
                doc = result["document"]
                context_parts.append(f"Document {i+1} ({doc['file_name']}, Page {doc['page']}):\n{result['preview']}")
                
                sources.append({
                    "file_name": doc["file_name"],
                    "page": doc["page"],
                    "score": result["score"],
                    "text_preview": result["preview"]
                })
            
            context = "\n\n".join(context_parts)
            
            # Create prompt for the LLM
            prompt = f"""You are an expert Air Force doctrine assistant. Based on the following Air Force doctrine documents, please answer the user's question comprehensively and accurately.

DOCTRINE CONTEXT:
{context}

USER QUESTION: {message}

Please provide a detailed answer based on the doctrine content above. If the context doesn't fully address the question, acknowledge this and provide what information you can from the available content. Always cite which documents you're referencing in your response."""

            # Get response from LLM
            response = self.llm.complete(prompt)
            
            return {
                "response": str(response),
                "duration": time.time() - start_time,
                "sources": sources
            }
            
        except Exception as e:
            return {
                "response": f"I encountered an error while processing your question: {str(e)}",
                "duration": time.time() - start_time,
                "sources": [],
                "error": str(e)
            }
    
    def get_stats(self):
        """Get database statistics."""
        return {
            "total_documents": len(self.documents),
            "total_characters": sum(len(doc["text"]) for doc in self.documents),
            "unique_files": len(set(doc["file_name"] for doc in self.documents))
        }

# Streamlit App
def main():
    st.set_page_config(
        page_title="Air Force Doctrine Chatbot",
        page_icon="🎖️",
        layout="wide"
    )
    
    st.title("🎖️ Air Force Doctrine Chatbot")
    st.markdown("*Working Version - Bypasses Vector Search Issues*")
    
    # Initialize chatbot
    if "chatbot" not in st.session_state:
        with st.spinner("Loading Air Force doctrine database..."):
            st.session_state.chatbot = WorkingDoctrineChatbot()
    
    chatbot = st.session_state.chatbot
    
    # Sidebar with stats
    with st.sidebar:
        st.header("📊 Database Stats")
        stats = chatbot.get_stats()
        st.metric("Documents", f"{stats['total_documents']:,}")
        st.metric("Unique Files", stats['unique_files'])
        st.metric("Content Size", f"{stats['total_characters']/(1024*1024):.1f} MB")
        
        st.header("💡 Example Questions")
        examples = [
            "What is mission command?",
            "Explain counterair operations",
            "What are the principles of targeting?",
            "How does the Air Force conduct intelligence operations?",
            "What is Agile Combat Employment?",
            "Describe force protection doctrine"
        ]
        
        for example in examples:
            if st.button(example, key=f"ex_{example[:20]}"):
                st.session_state.example_question = example
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Handle example question
    if "example_question" in st.session_state:
        st.session_state.messages.append({
            "role": "user",
            "content": st.session_state.example_question
        })
        del st.session_state.example_question
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("error"):
                st.error(f"❌ {message['content']}")
            else:
                st.markdown(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                with st.expander(f"📚 Sources ({len(message['sources'])} found)"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**{i}. {source['file_name']}** (Page {source['page']})")
                        st.write(f"*Relevance Score: {source['score']}*")
                        st.write(f"Preview: {source['text_preview']}")
                        st.divider()
            
            # Show response time
            if message["role"] == "assistant" and "duration" in message:
                st.caption(f"⏱️ Response time: {message['duration']:.1f}s")
    
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
                
                if result.get("error") and result["error"] != "No relevant documents found":
                    st.error(f"❌ {result['response']}")
                elif result.get("error") == "No relevant documents found":
                    st.warning(f"⚠️ {result['response']}")
                else:
                    st.markdown(result["response"])
                
                # Store message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "sources": result.get("sources", []),
                    "duration": result.get("duration", 0),
                    "error": result.get("error")
                })
                
                # Show sources
                if result.get("sources"):
                    with st.expander(f"📚 Sources ({len(result['sources'])} found)"):
                        for i, source in enumerate(result["sources"], 1):
                            st.write(f"**{i}. {source['file_name']}** (Page {source['page']})")
                            st.write(f"*Relevance Score: {source['score']}*")
                            st.write(f"Preview: {source['text_preview']}")
                            st.divider()
                
                # Show response time
                if result.get("duration", 0) > 0:
                    st.caption(f"⏱️ Response time: {result['duration']:.1f}s")

if __name__ == "__main__":
    main()
