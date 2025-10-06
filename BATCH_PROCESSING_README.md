# Read-Only Vector Database Batch Processing

This directory contains scripts for safely processing batches of queries against your vector database without risk of accidental modification.

## 🔒 **Read-Only Safety Features**

- **No write operations** to the vector database
- **Load-only access** to existing storage
- **Comprehensive logging** of all operations
- **Error handling** prevents crashes from corrupting data
- **Immediate result saving** prevents data loss

## 📁 **Files Overview**

### Core Scripts
- `simple_batch_processor.py` - Main batch processing script (recommended)
- `batch_query_processor.py` - Full-featured version with advanced logging
- `sample_prompts.json` - Example prompts file format

### Supporting Files
- `BATCH_PROCESSING_README.md` - This documentation
- `logs/` - Directory for all log files and results (auto-created)

## 🚀 **Quick Start**

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

### 3. Run Batch Processing
```bash
python3 simple_batch_processor.py sample_prompts.json
```

## 📋 **Prompts File Format**

Create a JSON file with your prompts in this format:

```json
[
  {
    "id": "unique_identifier",
    "prompt": "Your question here",
    "metadata": {
      "category": "summary",
      "priority": "high",
      "custom_field": "value"
    },
    "similarity_top_k": 5,
    "response_mode": "compact"
  }
]
```

### Required Fields
- `prompt` - The question/query text

### Optional Fields
- `id` - Unique identifier (auto-generated if missing)
- `metadata` - Custom metadata for categorization/tracking
- `similarity_top_k` - Number of similar chunks to retrieve (default: 5)
- `response_mode` - Response synthesis mode (default: "compact")

### Response Modes
- `"compact"` - Concise responses
- `"tree_summarize"` - Hierarchical summarization
- `"simple_summarize"` - Basic summarization
- `"no_text"` - Just return source chunks

## 📊 **Output Files**

### Results File (`results_TIMESTAMP.jsonl`)
Each line contains a complete result record:

```json
{
  "prompt_id": "summary_1",
  "prompt": "What is the main topic?",
  "response": "The main topic is...",
  "duration_seconds": 2.345,
  "timestamp": "2024-10-06T14:30:00",
  "similarity_top_k": 5,
  "response_mode": "compact",
  "sources_count": 3,
  "sources": [
    {
      "file_name": "document.pdf",
      "page": "1",
      "score": 0.85,
      "text_preview": "Relevant text excerpt..."
    }
  ],
  "metadata": {"category": "summary"},
  "response_length": 156,
  "status": "success"
}
```

### Log File (`batch_queries_TIMESTAMP.log`)
Detailed processing log with timestamps and status updates.

### Summary Report (`summary_report_TIMESTAMP.json`)
Statistical summary of the batch processing:

```json
{
  "batch_summary": {
    "total_prompts": 6,
    "successful": 5,
    "failed": 1,
    "success_rate": 0.833,
    "total_duration_seconds": 12.456,
    "average_duration_seconds": 2.076,
    "average_response_length": 234.5,
    "average_sources_per_query": 3.2
  },
  "prompt_categories": {
    "summary": {"total": 2, "successful": 2},
    "analysis": {"total": 3, "successful": 2}
  },
  "errors": ["Error message if any"],
  "timestamp": "2024-10-06T14:35:00"
}
```

## 🔧 **Usage Examples**

### Basic Usage
```bash
# Process sample prompts
python3 simple_batch_processor.py sample_prompts.json

# Use custom storage directory
python3 simple_batch_processor.py prompts.json ./my_storage
```

### Advanced Usage with Full Processor
```bash
# Use the full-featured processor
python3 batch_query_processor.py prompts.json

# Create sample prompts file
python3 batch_query_processor.py --create-sample
```

## 📈 **Monitoring Progress**

The script provides real-time progress updates:

```
2024-10-06 14:30:00 - INFO - READ-ONLY BATCH PROCESSOR STARTED
2024-10-06 14:30:01 - INFO - ✅ Settings configured
2024-10-06 14:30:02 - INFO - ✅ Index loaded (READ-ONLY)
2024-10-06 14:30:03 - INFO - 📋 Loaded 6 prompts
2024-10-06 14:30:04 - INFO - 🚀 Processing 6 prompts
2024-10-06 14:30:05 - INFO - 📝 1/6
2024-10-06 14:30:07 - INFO - 🔍 Processing: summary_1
2024-10-06 14:30:09 - INFO - ✅ summary_1 completed (2.1s, 3 sources)
```

## ⚠️ **Safety Considerations**

### Read-Only Guarantees
- Scripts only use `load_index_from_storage()` - no write operations
- No calls to `persist()` or `save()` methods
- Vector store loaded with `from_persist_dir()` (read-only)
- No index building or modification operations

### Error Handling
- Individual prompt failures don't stop batch processing
- All errors logged with full context
- Partial results saved immediately to prevent data loss
- Graceful handling of API rate limits

### Resource Management
- Small delays between queries to respect API limits
- Memory-efficient processing (one prompt at a time)
- Automatic cleanup of resources

## 🛠 **Customization**

### Custom Metadata
Add any fields to the `metadata` object for tracking:

```json
{
  "metadata": {
    "department": "engineering",
    "project": "security_audit",
    "reviewer": "john_doe",
    "urgency": "high"
  }
}
```

### Query Parameters
Adjust retrieval behavior per prompt:

```json
{
  "similarity_top_k": 10,     // More sources
  "response_mode": "tree_summarize"  // Different synthesis
}
```

## 📝 **Best Practices**

1. **Start Small** - Test with a few prompts first
2. **Use Descriptive IDs** - Makes analysis easier
3. **Categorize Prompts** - Use metadata for organization
4. **Monitor Logs** - Watch for errors or performance issues
5. **Backup Results** - Save important result files
6. **Rate Limiting** - Don't overwhelm the API

## 🔍 **Troubleshooting**

### Common Issues

**"Storage directory not found"**
- Ensure your vector database is built first
- Check the storage path is correct

**"ANTHROPIC_API_KEY not set"**
- Set the environment variable or add to .env file

**"Module not found"**
- Install requirements: `pip install -r requirements.txt`

**Empty responses**
- Check if your prompts are too specific
- Try increasing `similarity_top_k`

### Performance Tips
- Use `similarity_top_k=3-5` for faster queries
- Use `response_mode="compact"` for speed
- Process large batches during off-peak hours

## 📞 **Support**

For issues or questions:
1. Check the log files for detailed error messages
2. Verify your vector database with `python3 simple_verify.py`
3. Test individual queries with `python3 query.py "test question"`
