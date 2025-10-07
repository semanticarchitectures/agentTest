#!/usr/bin/env python3
"""
Analyze Source Files in Vector Database
Determines what files were used to build the vector database.
"""

import json
import os
from pathlib import Path
from collections import defaultdict, Counter

def analyze_docstore_files(persist_dir="./storage"):
    """Analyze the document store to find source files and their details."""
    print("🔍 ANALYZING SOURCE FILES IN VECTOR DATABASE")
    print("="*60)
    
    docstore_path = Path(persist_dir) / "docstore.json"
    
    if not docstore_path.exists():
        print(f"❌ Document store not found: {docstore_path}")
        return None
    
    print(f"📂 Reading document store: {docstore_path}")
    print(f"📊 File size: {docstore_path.stat().st_size:,} bytes ({docstore_path.stat().st_size/(1024*1024):.1f} MB)")
    
    try:
        with open(docstore_path, 'r', encoding='utf-8') as f:
            docstore_data = json.load(f)
        
        # Check for both data structures
        documents = docstore_data.get('docstore/data', {})
        ref_doc_info = docstore_data.get('docstore/ref_doc_info', {})

        print(f"✅ Found {len(documents):,} document chunks")
        print(f"✅ Found {len(ref_doc_info):,} reference documents")

        # Analyze reference documents (contains file metadata)
        source_files = defaultdict(list)
        metadata_fields = Counter()
        total_text_length = 0
        chunks_with_metadata = 0
        chunks_with_filenames = 0

        print("\n🔍 Analyzing reference documents...")

        for ref_id, ref_info in ref_doc_info.items():
            metadata = ref_info.get('metadata', {})
            node_ids = ref_info.get('node_ids', [])

            if metadata:
                chunks_with_metadata += 1

                # Count all metadata fields
                for field in metadata.keys():
                    metadata_fields[field] += 1

                # Extract file information
                file_name = metadata.get('file_name', metadata.get('filename', metadata.get('source', None)))
                if file_name:
                    chunks_with_filenames += 1

                    # Get text length from associated nodes
                    text_length = 0
                    for node_id in node_ids:
                        if node_id in documents:
                            doc = documents[node_id]
                            # Handle the nested structure: __data__ contains the actual content
                            if '__data__' in doc and 'text' in doc['__data__']:
                                text_length += len(doc['__data__']['text'])
                            elif 'text' in doc:  # Fallback for different structure
                                text_length += len(doc['text'])

                    total_text_length += text_length

                    # Store chunk info for this file
                    chunk_info = {
                        'ref_id': ref_id,
                        'node_ids': node_ids,
                        'text_length': text_length,
                        'page': metadata.get('page_label', metadata.get('page', 'Unknown')),
                        'metadata': metadata
                    }
                    source_files[file_name].append(chunk_info)
        
        print(f"✅ Analysis complete!")
        print(f"   📄 Total text content: {total_text_length:,} characters")
        print(f"   📋 Chunks with metadata: {chunks_with_metadata:,}")
        print(f"   📁 Chunks with filenames: {chunks_with_filenames:,}")
        
        # Show metadata fields found
        print(f"\n📊 Metadata fields found:")
        for field, count in metadata_fields.most_common():
            print(f"   {field}: {count:,} chunks")
        
        # Analyze source files
        if source_files:
            print(f"\n📁 SOURCE FILES ANALYSIS")
            print("="*40)
            print(f"Found {len(source_files)} unique source files:")
            
            total_chunks = 0
            for i, (filename, chunks) in enumerate(sorted(source_files.items()), 1):
                total_chunks += len(chunks)
                total_chars = sum(chunk['text_length'] for chunk in chunks)

                print(f"\n{i}. {filename}")
                print(f"   📄 Pages/Chunks: {len(chunks):,}")
                print(f"   📝 Text: {total_chars:,} characters ({total_chars/(1024):.1f} KB)")

                # Show page distribution
                pages = [chunk['page'] for chunk in chunks]
                page_counter = Counter(pages)
                if len(page_counter) <= 15:  # Show all pages if not too many
                    page_list = sorted(page_counter.keys(), key=lambda x: int(x) if str(x).isdigit() else float('inf'))
                    print(f"   📖 Pages: {', '.join(str(p) for p in page_list)}")
                else:
                    min_page = min(int(p) for p in pages if str(p).isdigit())
                    max_page = max(int(p) for p in pages if str(p).isdigit())
                    print(f"   📖 Pages: {min_page} - {max_page} ({len(page_counter)} unique pages)")

                # Show sample metadata
                sample_metadata = chunks[0]['metadata']
                interesting_fields = ['file_path', 'file_size', 'creation_date', 'last_modified_date']
                sample_info = []
                for field in interesting_fields:
                    if field in sample_metadata:
                        value = sample_metadata[field]
                        if field == 'file_size':
                            value = f"{value:,} bytes ({value/(1024*1024):.1f} MB)"
                        elif field == 'file_path':
                            value = f"...{value[-50:]}" if len(value) > 50 else value
                        sample_info.append(f"{field}: {value}")

                if sample_info:
                    print(f"   ℹ️  {'; '.join(sample_info)}")
            
            print(f"\n📊 SUMMARY")
            print("="*20)
            print(f"Total source files: {len(source_files)}")
            print(f"Total chunks: {total_chunks:,}")
            print(f"Average chunks per file: {total_chunks/len(source_files):.1f}")
            print(f"Total content: {total_text_length:,} characters ({total_text_length/(1024*1024):.1f} MB)")
            
            return {
                'source_files': dict(source_files),
                'total_files': len(source_files),
                'total_chunks': total_chunks,
                'total_characters': total_text_length,
                'metadata_fields': dict(metadata_fields)
            }
        
        else:
            print(f"\n⚠️  NO SOURCE FILES FOUND")
            print("This could mean:")
            print("1. Files were processed without preserving filename metadata")
            print("2. Metadata is stored in a different format")
            print("3. The vector database was built from text directly")
            
            # Try to find any identifying information
            print(f"\n🔍 Looking for alternative file identifiers...")
            
            sample_docs = list(documents.values())[:5]
            for i, doc in enumerate(sample_docs, 1):
                print(f"\nSample document {i}:")
                if 'metadata' in doc:
                    print(f"   Metadata keys: {list(doc['metadata'].keys())}")
                    for key, value in doc['metadata'].items():
                        if isinstance(value, str) and len(value) < 100:
                            print(f"   {key}: {value}")
                
                if 'text' in doc:
                    text_preview = doc['text'][:200].replace('\n', ' ')
                    print(f"   Text preview: {text_preview}...")
            
            return None
            
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Error analyzing docstore: {e}")
        return None

def save_source_analysis(analysis, output_file="source_files_analysis.json"):
    """Save the analysis results to a file."""
    if analysis:
        # Convert for JSON serialization
        json_data = {
            'total_files': analysis['total_files'],
            'total_chunks': analysis['total_chunks'], 
            'total_characters': analysis['total_characters'],
            'metadata_fields': analysis['metadata_fields'],
            'files': {}
        }
        
        for filename, chunks in analysis['source_files'].items():
            json_data['files'][filename] = {
                'chunk_count': len(chunks),
                'total_characters': sum(chunk['text_length'] for chunk in chunks),
                'pages': sorted(list(set(chunk['page'] for chunk in chunks))),
                'sample_metadata': chunks[0]['metadata'] if chunks else {}
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Analysis saved to: {output_file}")

def main():
    """Main analysis function."""
    persist_dir = "./storage"
    
    if not os.path.exists(persist_dir):
        print(f"❌ Storage directory not found: {persist_dir}")
        print("Make sure you're in the directory with your vector database.")
        return
    
    analysis = analyze_docstore_files(persist_dir)
    
    if analysis:
        save_source_analysis(analysis)
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Review the source files list above")
        print("2. Check source_files_analysis.json for detailed breakdown")
        print("3. Use this info to understand what content is in your database")
    else:
        print(f"\n🔧 TROUBLESHOOTING:")
        print("1. Check if the vector database was built correctly")
        print("2. Verify the PDF files had proper metadata during indexing")
        print("3. Try rebuilding the index with --rebuild flag")

if __name__ == "__main__":
    main()
