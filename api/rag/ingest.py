#!/usr/bin/env python3
"""
Simple document ingestion CLI script
Prints ingested markdown files from paths passed as CLI args
"""
import sys
from pathlib import Path
from typing import List, Dict


def ingest_documents(paths: List[str]) -> List[Dict[str, str]]:
    """
    Ingest markdown documents from specified paths

    Args:
        paths: List of file or directory paths

    Returns:
        List of document metadata dicts
    """
    docs = []

    for path_str in paths:
        path = Path(path_str)

        if not path.exists():
            print(f"⚠️  Path not found: {path_str}", file=sys.stderr)
            continue

        # Handle directory
        if path.is_dir():
            md_files = list(path.glob("**/*.md"))
            print(f"📁 Directory: {path_str} ({len(md_files)} markdown files)")

            for md_file in md_files:
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    doc = {
                        "filename": md_file.name,
                        "path": str(md_file),
                        "content": content,
                        "size": len(content),
                        "lines": content.count('\n') + 1
                    }
                    docs.append(doc)

                    print(f"  ✓ {md_file.name} ({doc['size']} bytes, {doc['lines']} lines)")

                except Exception as e:
                    print(f"  ✗ Error reading {md_file.name}: {e}", file=sys.stderr)

        # Handle single file
        elif path.is_file() and path.suffix == '.md':
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                doc = {
                    "filename": path.name,
                    "path": str(path),
                    "content": content,
                    "size": len(content),
                    "lines": content.count('\n') + 1
                }
                docs.append(doc)

                print(f"📄 File: {path.name} ({doc['size']} bytes, {doc['lines']} lines)")

            except Exception as e:
                print(f"✗ Error reading {path_str}: {e}", file=sys.stderr)

        else:
            print(f"⚠️  Not a markdown file: {path_str}", file=sys.stderr)

    return docs


if __name__ == "__main__":
    print("🔍 LLMSec RAG Document Ingestion\n")

    # Get paths from command line args
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        # Default paths if no args provided
        print("No paths specified, using defaults: data/docs, data/poisoned\n")
        paths = ["data/docs", "data/poisoned"]

    # Ingest documents
    docs = ingest_documents(paths)

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Summary: Ingested {len(docs)} documents")
    print(f"   Total size: {sum(d['size'] for d in docs)} bytes")
    print(f"   Total lines: {sum(d['lines'] for d in docs)}")
    print(f"{'='*60}")

    # Exit with error if no docs found
    if not docs:
        print("\n⚠️  No documents ingested!", file=sys.stderr)
        sys.exit(1)
