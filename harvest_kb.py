#!/usr/bin/env python3
"""
RadixDLT / Scrypto Documentation Harvester
Loads suncrypt.json and downloads all specified documentation sources.
"""

import json
import requests
import os
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import zipfile

def load_config(config_file):
    """Load configuration from JSON file."""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def ensure_directory(file_path):
    """Ensure the directory for a file path exists."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

def download_html(url, target_path):
    """Download HTML content from URL and save to target path."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    ensure_directory(target_path)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    return len(response.text.encode('utf-8'))

def download_github_repo(url, target_path):
    """Download GitHub repository as zip file."""
    # Convert GitHub repo URL to zip download URL
    if not url.startswith('https://github.com/'):
        raise ValueError(f"Not a GitHub URL: {url}")
    
    # Remove trailing slash and convert to zip download URL
    repo_url = url.rstrip('/')
    
    # Try main branch first, then master as fallback
    for branch in ['main', 'master']:
        zip_url = f"{repo_url}/archive/{branch}.zip"
        try:
            response = requests.get(zip_url, timeout=30)
            response.raise_for_status()
            break
        except requests.exceptions.HTTPError:
            if branch == 'master':  # Last attempt failed
                raise
            continue
    
    ensure_directory(target_path)
    with open(target_path, 'wb') as f:
        f.write(response.content)
    
    return len(response.content)

def clone_repo_to_zip(url, target_path):
    """Alternative method using git clone (requires git installed)."""
    import subprocess
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_name = url.split('/')[-1].replace('.git', '')
        clone_path = os.path.join(temp_dir, repo_name)
        
        # Clone repository
        subprocess.run([
            'git', 'clone', '--depth', '1', url, clone_path
        ], check=True, capture_output=True)
        
        # Create zip file
        ensure_directory(target_path)
        shutil.make_archive(target_path.replace('.zip', ''), 'zip', clone_path)
        
        # Get file size
        return os.path.getsize(target_path)

def main():
    """Main harvesting function."""
    print("RadixDLT / Scrypto Documentation Harvester")
    print("=" * 50)
    
    # Load configuration
    try:
        config = load_config('suncrypt.json')
    except FileNotFoundError:
        print("Error: suncrypt.json not found!")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing suncrypt.json: {e}")
        return 1
    
    # Ensure directories exist
    Path('kb/raw').mkdir(parents=True, exist_ok=True)
    Path('kb/cleaned').mkdir(parents=True, exist_ok=True)
    
    files_downloaded = 0
    total_size_bytes = 0
    failed_downloads = []
    
    # Process each file target
    for i, file_target in enumerate(config.get('file_targets', []), 1):
        url = file_target['url']
        target_path = file_target['target_path']
        
        print(f"\n[{i}/{len(config['file_targets'])}] {url}")
        print(f"  -> {target_path}")
        
        try:
            if target_path.endswith('.html'):
                size_bytes = download_html(url, target_path)
            elif target_path.endswith('.zip'):
                size_bytes = download_github_repo(url, target_path)
            elif target_path.endswith('.md') or target_path.endswith('.rs'):
                # Handle markdown/rust files if present
                size_bytes = download_html(url, target_path)
            else:
                print(f"  ⚠️  Unsupported file type: {target_path}")
                continue
            
            files_downloaded += 1
            total_size_bytes += size_bytes
            size_kb = size_bytes / 1024
            print(f"  ✅ Success ({size_kb:.1f} KB)")
            
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
            failed_downloads.append((url, str(e)))
    
    # Create placeholder README in cleaned directory
    readme_content = """# RadixDLT / Scrypto Knowledge Base - Cleaned Data

This directory contains processed and cleaned documentation from RadixDLT and Scrypto sources.

## Status
- ✅ Raw files downloaded and stored in `/kb/raw`
- ⏳ Content cleaning and processing: TODO
- ⏳ HTML to Markdown conversion: TODO  
- ⏳ Rust code extraction: TODO
- ⏳ Content organization: TODO

## Processing Pipeline
1. Extract content from HTML files (remove nav, headers, footers)
2. Convert HTML documentation to clean Markdown
3. Extract Rust code blocks to individual `.rs` files
4. Parse GitHub repositories for examples and documentation
5. Organize content by topic and create unified references

## Structure
```
kb/
├── raw/           # Original downloaded files
└── cleaned/       # Processed, machine-readable content
    ├── core_concepts.md
    ├── blueprint_examples.md  
    ├── api_reference.md
    └── examples/
        ├── hello_world.rs
        ├── token_creation.rs
        └── nft_minting.rs
```

Generated by harvest_kb.py
"""
    
    with open('kb/cleaned/README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Print final summary
    total_size_kb = total_size_bytes / 1024
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "=" * 50)
    print("🎯 HARVEST COMPLETE")
    print("=" * 50)
    print(f"📁 Files downloaded: {files_downloaded}")
    print(f"📊 Total size: {total_size_kb:.1f} KB")
    print(f"🕐 Timestamp: {timestamp}")
    print(f"📝 Created: kb/cleaned/README.md")
    
    if failed_downloads:
        print(f"\n⚠️  {len(failed_downloads)} downloads failed:")
        for url, error in failed_downloads:
            print(f"   • {url}: {error}")
    
    print(f"\n✨ Ready for cleaning pipeline!")
    return 0 if not failed_downloads else 1

if __name__ == "__main__":
    exit(main())