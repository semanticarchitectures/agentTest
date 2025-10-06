# PDF Question-Answering Agent

A RAG (Retrieval-Augmented Generation) system that recursively processes PDF documents and enables natural language Q&A using vector search and Claude.

## Features

- 🔍 Recursive PDF discovery in directories
- 📊 Vector database with persistent storage
- 🤖 Claude-powered responses with source citations
- 💾 Automatic index persistence (rebuild only when needed)
- 🎯 Configurable chunk size and retrieval parameters

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up API keys:**

Create a `.env` file in the project root:
```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
```

Or export as environment variables:
```bash
export ANTHROPIC_API_KEY=your_anthropic_key_here
export OPENAI_API_KEY=your_openai_key_here
```

## Usage

### Basic Usage

```bash
python pdf_agent.py /path/to/pdf/directory
```

This will:
1. Recursively scan the directory for all PDFs
2. Build a vector index (saved to `./storage`)
3. Start an interactive Q&A session

### Rebuild Index

To force a rebuild of the index (e.g., after adding new PDFs):

```bash
python pdf_agent.py /path/to/pdf/directory --rebuild
```

### Interactive Mode

Once running, ask questions about your documents:

```
Question: What are the main recommendations in the security policy?

Answer: [AI-generated answer based on PDF content]

Sources:
1. security_policy.pdf (Page 3)
2. guidelines.pdf (Page 12)
```

Type `quit`, `exit`, or `q` to stop.

## How It Works

1. **PDF Processing**: Recursively finds all PDFs in the specified directory
2. **Chunking**: Splits documents into overlapping chunks (default: 1024 tokens, 200 overlap)
3. **Embedding**: Generates embeddings using OpenAI's `text-embedding-3-small`
4. **Vector Storage**: Stores embeddings in ChromaDB (persisted to disk)
5. **Retrieval**: Uses semantic search to find relevant chunks
6. **Generation**: Claude synthesizes answers from retrieved context

## Configuration

You can modify the agent's behavior in `pdf_agent.py`:

```python
agent = PDFAgent(
    pdf_directory="./pdfs",
    persist_dir="./storage",      # Where to save the index
    chunk_size=1024,               # Size of text chunks
    chunk_overlap=200              # Overlap between chunks
)
```

Query parameters:
```python
response = agent.query(
    question="Your question",
    similarity_top_k=5,            # Number of chunks to retrieve
    response_mode="compact"        # Response synthesis mode
)
```

## Cost Considerations

- **Embeddings**: ~$0.02 per 1M tokens (OpenAI text-embedding-3-small)
- **LLM**: Claude Sonnet pricing per query
- Index is cached locally to avoid re-embedding

## Troubleshooting

**No PDFs found:**
- Ensure PDFs have `.pdf` extension (case-sensitive)
- Check directory path is correct

**API Key errors:**
- Verify `.env` file exists and contains valid keys
- Check environment variables are set

**Out of memory:**
- Reduce `chunk_size` parameter
- Process PDFs in smaller batches

## Project Structure

```
.
├── pdf_agent.py          # Main agent implementation
├── requirements.txt      # Python dependencies
├── .env                  # API keys (create this)
├── storage/              # Vector database (auto-created)
└── README.md            # This file
```
