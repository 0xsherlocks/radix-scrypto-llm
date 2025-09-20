#!/usr/bin/env python3
"""
RadixDLT / Scrypto Documentation Cleaner
Processes raw files from kb/raw and generates clean, machine-readable versions.
"""

import os
import re
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import html2text

def ensure_directory(file_path):
    """Ensure the directory for a file path exists."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

def clean_html_content(html_content):
    """Clean HTML by removing navigation, headers, footers, and ads."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove common unwanted elements
    unwanted_selectors = [
        'nav', 'header', 'footer', '.nav', '.navbar', '.header', '.footer',
        '.sidebar', '.menu', '.navigation', '.breadcrumb', '.pagination',
        '.ad', '.advertisement', '.ads', '.social', '.share',
        '.cookie-banner', '.cookie-notice', '.banner',
        'script', 'style', 'meta', 'link[rel="stylesheet"]'
    ]
    
    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()
    
    # Try to find main content area
    main_content = None
    main_selectors = [
        'main', '.main', '#main', '.content', '#content', 
        '.main-content', '#main-content', '.post-content',
        'article', '.article', '.documentation', '.docs',
        '.markdown-body', '.wiki-content'
    ]
    
    for selector in main_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    # If no main content found, use body or entire soup
    if not main_content:
        main_content = soup.select_one('body') or soup
    
    return str(main_content)

def extract_rust_code_blocks(content, base_name):
    """Extract Rust code blocks from content and return as list of (filename, code) tuples."""
    rust_blocks = []
    
    # Pattern for Rust code blocks in markdown
    rust_patterns = [
        r'```rust\n(.*?)\n```',
        r'```rs\n(.*?)\n```',
        r'<code[^>]*rust[^>]*>(.*?)</code>',
        r'<pre[^>]*rust[^>]*>(.*?)</pre>'
    ]
    
    for i, pattern in enumerate(rust_patterns):
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for j, code in enumerate(matches):
            # Clean up code
            code = code.strip()
            if len(code) > 50:  # Only save substantial code blocks
                # Generate filename
                filename = f"{base_name}_code_{i}_{j}.rs"
                rust_blocks.append((filename, code))
    
    return rust_blocks

def html_to_markdown(html_content):
    """Convert HTML to Markdown using html2text."""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap lines
    h.unicode_snob = True
    h.skip_internal_links = True
    
    return h.handle(html_content)

def normalize_markdown(content):
    """Normalize Markdown content - clean whitespace, headers, links."""
    # Remove excessive whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r'[ \t]+\n', '\n', content)
    content = re.sub(r'\n[ \t]+', '\n', content)
    
    # Normalize headers (ensure space after #)
    content = re.sub(r'^(#{1,6})([^ #])', r'\1 \2', content, flags=re.MULTILINE)
    
    # Fix broken links (remove empty links)
    content = re.sub(r'\[\]\([^)]*\)', '', content)
    content = re.sub(r'\[([^\]]*)\]\(\)', r'\1', content)
    
    # Clean up code block markers
    content = re.sub(r'```\s*\n```', '', content)
    
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    return content.strip()

def process_html_file(file_path, output_dir):
    """Process a single HTML file."""
    print(f"  📄 Processing HTML: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Clean HTML content
    cleaned_html = clean_html_content(html_content)
    
    # Convert to Markdown
    markdown_content = html_to_markdown(cleaned_html)
    markdown_content = normalize_markdown(markdown_content)
    
    # Save Markdown file
    base_name = file_path.stem
    md_file_path = output_dir / f"{base_name}.md"
    ensure_directory(md_file_path)
    
    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # Extract Rust code blocks
    rust_blocks = extract_rust_code_blocks(markdown_content, base_name)
    examples_dir = output_dir / 'examples'
    examples_dir.mkdir(exist_ok=True)
    
    rust_files_created = 0
    for filename, code in rust_blocks:
        rust_file_path = examples_dir / filename
        with open(rust_file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        rust_files_created += 1
    
    if rust_files_created > 0:
        print(f"    ⚡ Extracted {rust_files_created} Rust code blocks")
    
    return 1, rust_files_created  # md_files, rs_files

def process_zip_file(file_path, output_dir):
    """Process a single ZIP repository file."""
    print(f"  📦 Processing ZIP: {file_path.name}")
    
    repo_name = file_path.stem.replace('_repo', '').replace('-', '_')
    repo_output_dir = output_dir / repo_name
    repo_output_dir.mkdir(exist_ok=True)
    
    md_files = 0
    rs_files = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract ZIP file
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find all README.md and .rs files
        temp_path = Path(temp_dir)
        
        # Copy README.md files
        for readme_file in temp_path.rglob('README.md'):
            relative_path = readme_file.relative_to(temp_path)
            # Create a flattened name for README files
            if len(relative_path.parts) > 1:
                output_name = f"{'_'.join(relative_path.parts[:-1])}_README.md"
            else:
                output_name = "README.md"
            
            output_file = repo_output_dir / output_name
            shutil.copy2(readme_file, output_file)
            md_files += 1
        
        # Copy .rs files from examples or src directories
        for rs_file in temp_path.rglob('*.rs'):
            # Skip test files and build artifacts
            if any(part in rs_file.parts for part in ['target', 'tests', '.git']):
                continue
                
            relative_path = rs_file.relative_to(temp_path)
            
            # Create organized structure
            if 'example' in str(relative_path).lower():
                output_subdir = repo_output_dir / 'examples'
            elif 'src' in relative_path.parts:
                output_subdir = repo_output_dir / 'src' 
            else:
                output_subdir = repo_output_dir
                
            output_subdir.mkdir(exist_ok=True)
            
            # Create flattened filename to avoid conflicts
            if len(relative_path.parts) > 1:
                output_name = f"{'_'.join(relative_path.parts[:-1])}_{rs_file.name}"
            else:
                output_name = rs_file.name
                
            output_file = output_subdir / output_name
            shutil.copy2(rs_file, output_file)
            rs_files += 1
    
    if md_files > 0 or rs_files > 0:
        print(f"    📋 Copied {md_files} MD files and {rs_files} RS files")
    
    return md_files, rs_files

def update_readme(output_dir, total_md_files, total_rs_files):
    """Update the README.md with processing results."""
    readme_path = output_dir / 'README.md'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    readme_content = f"""# RadixDLT / Scrypto Knowledge Base - Cleaned Data

This directory contains processed and cleaned documentation from RadixDLT and Scrypto sources.

## Processing Status ✅
- ✅ Raw files downloaded and stored in `/kb/raw`
- ✅ Content cleaning and processing: COMPLETE
- ✅ HTML to Markdown conversion: COMPLETE  
- ✅ Rust code extraction: COMPLETE
- ✅ Content organization: COMPLETE

**Last processed:** {timestamp}  
**Generated files:** {total_md_files} Markdown files, {total_rs_files} Rust files

## Structure
```
kb/cleaned/
├── README.md                    # This file
├── examples/                    # Extracted Rust code blocks
│   ├── *.rs                    # Individual code examples
├── repo_name/                   # Repository contents
│   ├── README.md               # Repository documentation
│   ├── examples/               # Example code from repos
│   └── src/                    # Source code from repos
└── *.md                        # Converted documentation pages
```

## Content Sources
- **HTML Documentation:** Converted from official Radix docs, developer hub
- **Repository Examples:** Extracted from official GitHub repositories
- **Code Blocks:** Rust examples extracted from documentation
- **README Files:** Repository documentation and guides

## Files Generated
- **Markdown Documentation:** {total_md_files} files
- **Rust Code Examples:** {total_rs_files} files
- **Organized by Source:** Repositories separated into subdirectories
- **Clean Format:** Normalized headers, whitespace, and links

This knowledge base is optimized for RAG (Retrieval-Augmented Generation) applications and provides comprehensive coverage of RadixDLT and Scrypto development resources.

---
*Generated by clean_kb.py - RadixDLT Documentation Cleaner*
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

def main():
    """Main cleaning function."""
    print("RadixDLT / Scrypto Documentation Cleaner")
    print("=" * 50)
    
    # Setup paths
    raw_dir = Path('kb/raw')
    output_dir = Path('kb/cleaned')
    
    if not raw_dir.exists():
        print("❌ Error: kb/raw directory not found!")
        return 1
    
    output_dir.mkdir(exist_ok=True)
    
    total_md_files = 0
    total_rs_files = 0
    processed_files = 0
    
    # Process all files in raw directory
    raw_files = list(raw_dir.glob('*'))
    
    if not raw_files:
        print("❌ No files found in kb/raw!")
        return 1
    
    print(f"📁 Found {len(raw_files)} files to process\n")
    
    for file_path in raw_files:
        if file_path.is_file():
            if file_path.suffix == '.html':
                md_count, rs_count = process_html_file(file_path, output_dir)
                total_md_files += md_count
                total_rs_files += rs_count
                processed_files += 1
                
            elif file_path.suffix == '.zip':
                md_count, rs_count = process_zip_file(file_path, output_dir)
                total_md_files += md_count
                total_rs_files += rs_count
                processed_files += 1
                
            else:
                print(f"  ⚠️  Skipping unsupported file: {file_path.name}")
    
    # Update README with results
    update_readme(output_dir, total_md_files, total_rs_files)
    
    # Print final summary
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "=" * 50)
    print("🎯 CLEANING COMPLETE")
    print("=" * 50)
    print(f"📁 Files processed: {processed_files}")
    print(f"📄 Markdown files generated: {total_md_files}")
    print(f"⚡ Rust files extracted: {total_rs_files}")
    print(f"🕐 Timestamp: {timestamp}")
    print(f"📝 Updated: kb/cleaned/README.md")
    print(f"\n✨ Knowledge base ready for RAG applications!")
    
    return 0

if __name__ == "__main__":
    exit(main())