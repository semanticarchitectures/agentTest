#!/usr/bin/env python3
"""
Simple Read-Only Vector Database Batch Query Processor
Processes prompts from JSON file and logs responses with metadata.
No external dependencies beyond LlamaIndex.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Try to import required modules
try:
    from llama_index.core import (
        StorageContext,
        load_index_from_storage,
        Settings
    )
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.llms.anthropic import Anthropic
    from llama_index.vector_stores.faiss import FaissVectorStore
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)


class SimpleReadOnlyProcessor:
    """Simple read-only processor for vector database queries."""
    
    def __init__(self, persist_dir: str = "./storage", log_dir: str = "./logs"):
        """Initialize the processor."""
        self.persist_dir = persist_dir
        self.log_dir = Path(log_dir)
        self.index = None
        self.query_engine = None
        
        # Create logs directory
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Configure settings
        self._configure_settings()
        
        # Load index
        self._load_index()
    
    def _setup_logging(self):
        """Setup logging."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"batch_queries_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.results_file = self.log_dir / f"results_{timestamp}.jsonl"
        
        self.logger.info("="*60)
        self.logger.info("READ-ONLY BATCH PROCESSOR STARTED")
        self.logger.info("="*60)
    
    def _configure_settings(self):
        """Configure LlamaIndex settings."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        Settings.llm = Anthropic(
            model="claude-3-5-sonnet-20241022",
            api_key=api_key
        )
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            trust_remote_code=True
        )
        
        self.logger.info("✅ Settings configured")
    
    def _load_index(self):
        """Load the vector index (read-only)."""
        if not os.path.exists(self.persist_dir):
            raise ValueError(f"Storage directory not found: {self.persist_dir}")
        
        self.logger.info(f"Loading index from {self.persist_dir}...")
        
        vector_store = FaissVectorStore.from_persist_dir(self.persist_dir)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir=self.persist_dir
        )
        self.index = load_index_from_storage(storage_context)
        
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact"
        )
        
        self.logger.info("✅ Index loaded (READ-ONLY)")
    
    def load_prompts(self, prompts_file: str) -> List[Dict[str, Any]]:
        """Load prompts from JSON file."""
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        # Add IDs if missing
        for i, prompt in enumerate(prompts):
            if 'id' not in prompt:
                prompt['id'] = f"prompt_{i+1}"
        
        self.logger.info(f"📋 Loaded {len(prompts)} prompts")
        return prompts
    
    def process_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single prompt."""
        prompt_id = prompt_data.get('id', 'unknown')
        prompt_text = prompt_data['prompt']
        similarity_top_k = prompt_data.get('similarity_top_k', 5)
        response_mode = prompt_data.get('response_mode', 'compact')
        
        start_time = time.time()
        
        self.logger.info(f"🔍 Processing: {prompt_id}")
        
        try:
            # Update query engine if needed
            if similarity_top_k != 5 or response_mode != 'compact':
                self.query_engine = self.index.as_query_engine(
                    similarity_top_k=similarity_top_k,
                    response_mode=response_mode
                )
            
            # Execute query
            response = self.query_engine.query(prompt_text)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Extract sources
            sources = []
            if hasattr(response, 'source_nodes') and response.source_nodes:
                for node in response.source_nodes:
                    source = {
                        'file_name': node.node.metadata.get('file_name', 'Unknown'),
                        'page': node.node.metadata.get('page_label', 'Unknown'),
                        'score': getattr(node, 'score', None),
                        'text_preview': node.node.text[:150] + "..." if len(node.node.text) > 150 else node.node.text
                    }
                    sources.append(source)
            
            result = {
                'prompt_id': prompt_id,
                'prompt': prompt_text,
                'response': response.response,
                'duration_seconds': round(duration, 3),
                'timestamp': datetime.now().isoformat(),
                'similarity_top_k': similarity_top_k,
                'response_mode': response_mode,
                'sources_count': len(sources),
                'sources': sources,
                'metadata': prompt_data.get('metadata', {}),
                'response_length': len(response.response),
                'status': 'success'
            }
            
            self.logger.info(f"✅ {prompt_id} completed ({duration:.2f}s, {len(sources)} sources)")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            result = {
                'prompt_id': prompt_id,
                'prompt': prompt_text,
                'error': str(e),
                'duration_seconds': round(duration, 3),
                'timestamp': datetime.now().isoformat(),
                'metadata': prompt_data.get('metadata', {}),
                'status': 'error'
            }
            
            self.logger.error(f"❌ {prompt_id} failed: {e}")
            return result
    
    def process_batch(self, prompts_file: str) -> List[Dict[str, Any]]:
        """Process all prompts and save results."""
        prompts = self.load_prompts(prompts_file)
        results = []
        
        self.logger.info(f"🚀 Processing {len(prompts)} prompts")
        
        for i, prompt_data in enumerate(prompts, 1):
            self.logger.info(f"📝 {i}/{len(prompts)}")
            
            result = self.process_prompt(prompt_data)
            results.append(result)
            
            # Save result immediately
            with open(self.results_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
            
            # Brief pause
            time.sleep(0.5)
        
        # Summary
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = len(results) - successful
        
        self.logger.info("="*60)
        self.logger.info("BATCH COMPLETED")
        self.logger.info(f"Total: {len(results)}, Success: {successful}, Failed: {failed}")
        self.logger.info(f"Results: {self.results_file}")
        
        return results
    
    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """Generate a summary report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.log_dir / f"summary_report_{timestamp}.json"
        
        # Calculate statistics
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']
        
        total_duration = sum(r.get('duration_seconds', 0) for r in results)
        avg_duration = total_duration / len(results) if results else 0
        
        # Response length stats
        response_lengths = [len(r.get('response', '')) for r in successful]
        avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
        
        # Source count stats
        source_counts = [r.get('sources_count', 0) for r in successful]
        avg_sources = sum(source_counts) / len(source_counts) if source_counts else 0
        
        summary = {
            'batch_summary': {
                'total_prompts': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': len(successful) / len(results) if results else 0,
                'total_duration_seconds': round(total_duration, 3),
                'average_duration_seconds': round(avg_duration, 3),
                'average_response_length': round(avg_response_length, 1),
                'average_sources_per_query': round(avg_sources, 1)
            },
            'prompt_categories': {},
            'errors': [r.get('error') for r in failed],
            'timestamp': datetime.now().isoformat()
        }
        
        # Category breakdown
        for result in results:
            category = result.get('metadata', {}).get('category', 'unknown')
            if category not in summary['prompt_categories']:
                summary['prompt_categories'][category] = {'total': 0, 'successful': 0}
            summary['prompt_categories'][category]['total'] += 1
            if result['status'] == 'success':
                summary['prompt_categories'][category]['successful'] += 1
        
        # Save summary
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📊 Summary report saved: {report_file}")
        return summary


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python simple_batch_processor.py <prompts_file.json> [storage_dir]")
        print("\nExample:")
        print("  python simple_batch_processor.py sample_prompts.json")
        print("  python simple_batch_processor.py prompts.json ./storage")
        sys.exit(1)
    
    prompts_file = sys.argv[1]
    storage_dir = sys.argv[2] if len(sys.argv) > 2 else "./storage"
    
    if not os.path.exists(prompts_file):
        print(f"❌ Prompts file not found: {prompts_file}")
        sys.exit(1)
    
    try:
        processor = SimpleReadOnlyProcessor(persist_dir=storage_dir)
        results = processor.process_batch(prompts_file)
        summary = processor.generate_summary_report(results)
        
        print(f"\n🎉 Batch processing completed!")
        print(f"📊 Success rate: {summary['batch_summary']['success_rate']:.1%}")
        print(f"📁 Results: {processor.results_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
