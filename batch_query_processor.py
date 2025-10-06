#!/usr/bin/env python3
"""
Read-Only Vector Database Batch Query Processor
Processes prompts from JSON file and logs responses with metadata.
Prevents accidental database modification.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.faiss import FaissVectorStore

# Load environment variables
load_dotenv()


class ReadOnlyVectorDBProcessor:
    """Read-only processor for vector database queries with comprehensive logging."""
    
    def __init__(self, persist_dir: str = "./storage", log_dir: str = "./logs"):
        """
        Initialize the read-only processor.
        
        Args:
            persist_dir: Path to vector database storage
            log_dir: Directory for log files
        """
        self.persist_dir = persist_dir
        self.log_dir = Path(log_dir)
        self.index = None
        self.query_engine = None
        
        # Create logs directory
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Configure LlamaIndex settings (read-only)
        self._configure_settings()
        
        # Load the index in read-only mode
        self._load_index_readonly()
    
    def _setup_logging(self):
        """Setup comprehensive logging."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Main log file
        log_file = self.log_dir / f"query_batch_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*70)
        self.logger.info("READ-ONLY VECTOR DATABASE BATCH PROCESSOR STARTED")
        self.logger.info("="*70)
        self.logger.info(f"Log file: {log_file}")
        self.logger.info(f"Storage directory: {self.persist_dir}")
        
        # Results log file for structured data
        self.results_file = self.log_dir / f"query_results_{timestamp}.jsonl"
        self.logger.info(f"Results file: {self.results_file}")
    
    def _configure_settings(self):
        """Configure LlamaIndex settings for read-only access."""
        try:
            Settings.llm = Anthropic(
                model="claude-3-5-sonnet-20241022",
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            Settings.embed_model = HuggingFaceEmbedding(
                model_name="BAAI/bge-small-en-v1.5",
                trust_remote_code=True
            )
            self.logger.info("✅ LlamaIndex settings configured")
        except Exception as e:
            self.logger.error(f"❌ Failed to configure settings: {e}")
            raise
    
    def _load_index_readonly(self):
        """Load the vector index in read-only mode."""
        try:
            if not os.path.exists(self.persist_dir):
                raise ValueError(f"Storage directory does not exist: {self.persist_dir}")
            
            self.logger.info(f"Loading vector index from {self.persist_dir}...")
            
            # Load FAISS vector store (read-only)
            vector_store = FaissVectorStore.from_persist_dir(self.persist_dir)
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store,
                persist_dir=self.persist_dir
            )
            
            # Load index (this is inherently read-only)
            self.index = load_index_from_storage(storage_context)
            
            # Create query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=5,
                response_mode="compact"
            )
            
            self.logger.info("✅ Vector index loaded successfully (READ-ONLY)")
            
            # Log database stats
            self._log_database_stats()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load vector index: {e}")
            raise
    
    def _log_database_stats(self):
        """Log database statistics."""
        try:
            storage_path = Path(self.persist_dir)
            total_size = sum(f.stat().st_size for f in storage_path.glob('**/*') if f.is_file())
            
            self.logger.info(f"📊 Database Statistics:")
            self.logger.info(f"   Storage size: {total_size:,} bytes ({total_size/(1024*1024):.1f} MB)")
            
            # Try to get FAISS stats
            if hasattr(self.index, '_vector_store') and hasattr(self.index._vector_store, '_faiss_index'):
                faiss_index = self.index._vector_store._faiss_index
                if hasattr(faiss_index, 'ntotal'):
                    self.logger.info(f"   Vector count: {faiss_index.ntotal:,}")
                    
        except Exception as e:
            self.logger.warning(f"Could not retrieve database stats: {e}")
    
    def load_prompts(self, prompts_file: str) -> List[Dict[str, Any]]:
        """
        Load prompts from JSON file.
        
        Expected JSON format:
        [
            {
                "id": "unique_id",
                "prompt": "Your question here",
                "metadata": {"category": "test", "priority": "high"},
                "similarity_top_k": 5,
                "response_mode": "compact"
            }
        ]
        
        Args:
            prompts_file: Path to JSON file containing prompts
            
        Returns:
            List of prompt dictionaries
        """
        try:
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            
            self.logger.info(f"📋 Loaded {len(prompts)} prompts from {prompts_file}")
            
            # Validate prompt format
            for i, prompt in enumerate(prompts):
                if 'prompt' not in prompt:
                    raise ValueError(f"Prompt {i} missing 'prompt' field")
                if 'id' not in prompt:
                    prompt['id'] = f"prompt_{i+1}"
            
            return prompts
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load prompts from {prompts_file}: {e}")
            raise
    
    def process_single_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single prompt and return results with metadata.
        
        Args:
            prompt_data: Dictionary containing prompt and metadata
            
        Returns:
            Dictionary with query results and metadata
        """
        prompt_id = prompt_data.get('id', 'unknown')
        prompt_text = prompt_data['prompt']
        similarity_top_k = prompt_data.get('similarity_top_k', 5)
        response_mode = prompt_data.get('response_mode', 'compact')
        
        start_time = time.time()
        
        self.logger.info(f"🔍 Processing prompt {prompt_id}: '{prompt_text[:100]}...'")
        
        try:
            # Update query engine parameters if specified
            if similarity_top_k != 5 or response_mode != 'compact':
                self.query_engine = self.index.as_query_engine(
                    similarity_top_k=similarity_top_k,
                    response_mode=response_mode
                )
            
            # Execute query
            response = self.query_engine.query(prompt_text)
            
            end_time = time.time()
            query_duration = end_time - start_time
            
            # Extract source information
            sources = []
            if hasattr(response, 'source_nodes') and response.source_nodes:
                for node in response.source_nodes:
                    source_info = {
                        'file_name': node.node.metadata.get('file_name', 'Unknown'),
                        'page_label': node.node.metadata.get('page_label', 'Unknown'),
                        'score': getattr(node, 'score', None),
                        'text_preview': node.node.text[:200] + "..." if len(node.node.text) > 200 else node.node.text
                    }
                    sources.append(source_info)
            
            # Compile results
            result = {
                'prompt_id': prompt_id,
                'prompt': prompt_text,
                'response': response.response,
                'query_duration_seconds': round(query_duration, 3),
                'timestamp': datetime.now().isoformat(),
                'similarity_top_k': similarity_top_k,
                'response_mode': response_mode,
                'sources_count': len(sources),
                'sources': sources,
                'input_metadata': prompt_data.get('metadata', {}),
                'response_length': len(response.response),
                'status': 'success'
            }
            
            self.logger.info(f"✅ Prompt {prompt_id} completed in {query_duration:.3f}s")
            self.logger.info(f"   Response length: {len(response.response)} chars")
            self.logger.info(f"   Sources found: {len(sources)}")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            query_duration = end_time - start_time
            
            error_result = {
                'prompt_id': prompt_id,
                'prompt': prompt_text,
                'error': str(e),
                'query_duration_seconds': round(query_duration, 3),
                'timestamp': datetime.now().isoformat(),
                'similarity_top_k': similarity_top_k,
                'response_mode': response_mode,
                'input_metadata': prompt_data.get('metadata', {}),
                'status': 'error'
            }
            
            self.logger.error(f"❌ Prompt {prompt_id} failed: {e}")
            return error_result
    
    def process_batch(self, prompts_file: str) -> List[Dict[str, Any]]:
        """
        Process all prompts from file and log results.
        
        Args:
            prompts_file: Path to JSON file containing prompts
            
        Returns:
            List of result dictionaries
        """
        prompts = self.load_prompts(prompts_file)
        results = []
        
        self.logger.info(f"🚀 Starting batch processing of {len(prompts)} prompts")
        
        for i, prompt_data in enumerate(prompts, 1):
            self.logger.info(f"📝 Processing {i}/{len(prompts)}")
            
            result = self.process_single_prompt(prompt_data)
            results.append(result)
            
            # Write result to JSONL file immediately
            with open(self.results_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
            
            # Small delay to be respectful to API
            time.sleep(0.5)
        
        # Log summary
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = len(results) - successful
        
        self.logger.info("="*70)
        self.logger.info("BATCH PROCESSING COMPLETED")
        self.logger.info("="*70)
        self.logger.info(f"Total prompts: {len(results)}")
        self.logger.info(f"Successful: {successful}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Results saved to: {self.results_file}")
        
        return results


def create_sample_prompts_file(filename: str = "sample_prompts.json"):
    """Create a sample prompts file for testing."""
    sample_prompts = [
        {
            "id": "summary_1",
            "prompt": "What is the main topic of these documents?",
            "metadata": {"category": "summary", "priority": "high"},
            "similarity_top_k": 3,
            "response_mode": "compact"
        },
        {
            "id": "detail_1", 
            "prompt": "What are the key recommendations mentioned?",
            "metadata": {"category": "analysis", "priority": "medium"},
            "similarity_top_k": 5,
            "response_mode": "tree_summarize"
        },
        {
            "id": "search_1",
            "prompt": "Are there any mentions of security policies?",
            "metadata": {"category": "search", "priority": "low"},
            "similarity_top_k": 7,
            "response_mode": "compact"
        }
    ]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sample_prompts, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sample prompts file created: {filename}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python batch_query_processor.py <prompts_file.json> [storage_dir]")
        print("\nExample:")
        print("  python batch_query_processor.py prompts.json")
        print("  python batch_query_processor.py prompts.json ./storage")
        print("\nTo create a sample prompts file:")
        print("  python batch_query_processor.py --create-sample")
        sys.exit(1)
    
    if sys.argv[1] == "--create-sample":
        create_sample_prompts_file()
        return
    
    prompts_file = sys.argv[1]
    storage_dir = sys.argv[2] if len(sys.argv) > 2 else "./storage"
    
    # Check for required API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        print("Please create a .env file with your API key or set it as an environment variable")
        sys.exit(1)
    
    try:
        # Initialize processor
        processor = ReadOnlyVectorDBProcessor(persist_dir=storage_dir)
        
        # Process batch
        results = processor.process_batch(prompts_file)
        
        print(f"\n🎉 Batch processing completed!")
        print(f"Results saved to: {processor.results_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
