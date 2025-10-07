# 🎖️ Air Force Doctrine Interactive Chatbot

An intelligent chatbot that connects to your Air Force doctrine vector database and answers questions about doctrine content with source citations.

## 🚀 Quick Start

### 1. Set Your API Key
```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

### 2. Launch the Chatbot
```bash
python3 launch_chatbot.py
```

Choose between:
- **💻 Command Line Interface** - Terminal-based chat
- **🌐 Web Interface** - Modern web UI with Streamlit

## 📋 Features

### 🎯 Core Capabilities
- **Intelligent Q&A** - Ask questions about Air Force doctrine in natural language
- **Source Citations** - Every answer includes references to specific doctrine publications
- **Context Awareness** - Maintains conversation context for follow-up questions
- **Read-Only Safety** - Cannot modify your vector database
- **Session Management** - Save and export chat sessions

### 📚 Knowledge Base
Your chatbot has access to **99 Air Force doctrine documents** including:
- **AFDPs** (Air Force Doctrine Publications)
- **AFDNs** (Air Force Doctrine Notes) 
- **Training Materials** and Guides
- **Paragon** doctrine newsletters
- **Chennault** exercise reports
- **Doctrine Advisories**

**Total Content**: 4.2 MB of doctrine text across 1,864 document chunks

### 🔍 Search & Retrieval
- **Vector Similarity Search** - Finds most relevant content using embeddings
- **Multi-Document Synthesis** - Combines information from multiple sources
- **Relevance Scoring** - Shows how well sources match your question
- **Page-Level Citations** - References specific pages in doctrine publications

## 🖥️ Interface Options

### Command Line Interface (`doctrine_chatbot.py`)
```bash
python3 doctrine_chatbot.py
```

**Features:**
- Interactive terminal chat
- Real-time source citations
- Session history
- Command shortcuts (`help`, `stats`, `history`, `save`)
- Automatic session saving

**Example Session:**
```
🎖️  Ask about doctrine: What is mission command?

🔍 Searching doctrine database...

📖 Response:
Mission command is the conduct of military operations through decentralized execution based on mission-type orders. It requires commanders to provide clear intent and guidance while empowering subordinates to exercise disciplined initiative within the commander's intent...

📚 Sources (3 found):
  1. AFDP 1-1 Mission Command.pdf (Page 5) - Score: 0.89
  2. AFDP3-0Operations.pdf (Page 12) - Score: 0.82
  3. AFDP-1.pdf (Page 8) - Score: 0.76

⏱️  Response time: 2.3s
```

### Web Interface (`web_chatbot.py`)
```bash
streamlit run web_chatbot.py
```

**Features:**
- Modern web UI accessible at `http://localhost:8501`
- Chat history with expandable source citations
- Database statistics sidebar
- Example question buttons
- Download chat sessions as JSON
- Mobile-friendly responsive design

## 📊 Database Information

Your vector database contains:

| Metric | Value |
|--------|-------|
| **Total Files** | 99 PDFs |
| **Total Chunks** | 1,864 pages/sections |
| **Content Size** | 4.2 MB of text |
| **Average per File** | 18.8 chunks |

### 📚 Major Publications Available
- **AFDP3-0.1 Command and Control** (325 KB)
- **AFDP 3-60 Targeting** (264 KB)
- **AFDP5-0 Planning** (184 KB)
- **AFDP3-0 Operations** (152 KB)
- **AFDN 25-1 Artificial Intelligence** (94 KB)

## 💡 Example Questions

### Strategic & Operational
- "What are the principles of airpower?"
- "How does the Air Force conduct strategic attack?"
- "Explain the targeting process"
- "What is Agile Combat Employment (ACE)?"

### Tactical & Technical
- "How do counterair operations work?"
- "What are the types of intelligence collection?"
- "Describe force protection measures"
- "How does cyberspace operations integrate with kinetic operations?"

### Leadership & Command
- "What is mission command?"
- "How should commanders exercise disciplined initiative?"
- "What are the principles of mission-type orders?"

### Specialized Operations
- "How does the Air Force conduct special operations?"
- "What is the role of weather operations?"
- "Explain electromagnetic spectrum operations"
- "How does AI integrate into Air Force operations?"

## 🔧 Commands (CLI Only)

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `stats` | Display database statistics |
| `history` | Show recent questions |
| `save` | Save current chat session |
| `quit` / `exit` | End the session |

## 💾 Session Management

### Automatic Saving
- CLI automatically saves sessions on exit
- Web interface allows manual download
- Sessions saved as JSON with full metadata

### Session Data Includes
- All questions and responses
- Source citations with relevance scores
- Response times and timestamps
- Database statistics
- Session duration

## 🛠️ Installation & Setup

### Prerequisites
```bash
pip install llama-index llama-index-vector-stores-faiss llama-index-llms-anthropic anthropic streamlit
```

### Environment Setup
1. **API Key**: Set `ANTHROPIC_API_KEY` environment variable
2. **Database**: Ensure `./storage/` directory contains your vector database
3. **Files**: Required files:
   - `storage/docstore.json`
   - `storage/default__vector_store.json`
   - `storage/index_store.json`

### Verification
```bash
python3 -c "
import os
from pathlib import Path
print('API Key:', '✅' if os.getenv('ANTHROPIC_API_KEY') else '❌')
print('Storage:', '✅' if Path('./storage').exists() else '❌')
print('Docstore:', '✅' if Path('./storage/docstore.json').exists() else '❌')
"
```

## 🔒 Security & Safety

### Read-Only Access
- **No database modifications** - Chatbot only reads from your vector database
- **No data persistence** - Conversations don't modify the knowledge base
- **Safe querying** - Cannot delete or corrupt your indexed documents

### API Usage
- Uses Anthropic Claude 3.5 Sonnet model
- Configurable temperature (default: 0.1 for consistency)
- Token limits to prevent excessive usage
- Error handling for API failures

## 🎯 Best Practices

### Asking Effective Questions
1. **Be specific** - "How does targeting work?" vs "What is targeting?"
2. **Use doctrine terminology** - Reference AFDPs, operations, etc.
3. **Ask follow-ups** - The chatbot maintains conversation context
4. **Request citations** - Ask for specific publication references

### Getting Better Answers
- **Context matters** - Provide background for complex questions
- **Break down complex topics** - Ask multiple focused questions
- **Verify important information** - Cross-reference with original documents
- **Use the source citations** - Review the referenced pages for full context

## 🐛 Troubleshooting

### Common Issues

**"API Key not found"**
```bash
export ANTHROPIC_API_KEY="your_key_here"
```

**"Storage directory not found"**
- Ensure you're in the correct directory
- Check that `./storage/` exists with database files

**"No relevant information found"**
- Try rephrasing your question
- Use more specific doctrine terminology
- Check if the topic is covered in your database

**Web interface won't start**
```bash
pip install streamlit
streamlit run web_chatbot.py --server.port 8501
```

### Performance Tips
- **Shorter questions** generally get faster responses
- **Specific topics** yield more relevant sources
- **Clear browser cache** if web interface has issues

## 📈 Advanced Usage

### Custom Configuration
Edit the chatbot files to modify:
- **Model settings** (temperature, max tokens)
- **Search parameters** (similarity_top_k)
- **System prompts** for different response styles
- **Memory settings** for longer conversations

### Integration Options
- **Batch processing** - Use with existing batch query scripts
- **API wrapper** - Create REST API around the chatbot
- **Custom interfaces** - Build your own UI using the core classes

## 📞 Support

For issues with:
- **Vector database** - Check your original indexing process
- **API connectivity** - Verify Anthropic API key and credits
- **Performance** - Monitor system resources and API rate limits
- **Content accuracy** - Cross-reference with original doctrine publications

---

🎖️ **Ready to explore Air Force doctrine with AI assistance!**
