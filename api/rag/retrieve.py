"""
Document retrieval from data directories
"""
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


def retrieve(query: str, k: int = 3) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Retrieve documents from data directories

    Reads from data/docs first, then data/poisoned
    Returns top k documents (naive retrieval - no actual ranking)

    Args:
        query: User query string
        k: Number of documents to retrieve

    Returns:
        List of tuples: (content, metadata_dict)
    """
    results = []

    # Read from clean docs first
    docs_path = Path("data/docs")
    if docs_path.exists():
        for md_file in sorted(docs_path.glob("*.md")):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                metadata = {
                    "filename": md_file.name,
                    "path": str(md_file),
                    "source": "docs",
                    "size": len(content)
                }

                results.append((content, metadata))

            except Exception as e:
                logger.error(f"Error reading {md_file}: {e}")

    # Then read from poisoned directory
    poisoned_path = Path("data/poisoned")
    if poisoned_path.exists():
        for md_file in sorted(poisoned_path.glob("*.md")):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                metadata = {
                    "filename": md_file.name,
                    "path": str(md_file),
                    "source": "poisoned",
                    "size": len(content)
                }

                results.append((content, metadata))

            except Exception as e:
                logger.error(f"Error reading {md_file}: {e}")

    # Return top k results (naive - just take first k)
    return results[:k]


def sanitize_document(content: str) -> str:
    """
    ✅ DEFENDED: Sanitize document content

    Strips instruction-like lines that could be prompt injections

    Args:
        content: Raw document content

    Returns:
        Sanitized content
    """
    lines = content.split('\n')
    sanitized_lines = []

    # Patterns that look like instructions/injections
    instruction_patterns = [
        r'^\s*ignore\s+(previous|above|prior)',
        r'^\s*disregard\s+',
        r'^\s*you\s+are\s+now\s+',
        r'^\s*system\s*:',
        r'^\s*new\s+(instructions|system)',
        r'^\s*<\|.*?\|>',
        r'^\s*###\s*(instruction|system)',
    ]

    for line in lines:
        # Check if line matches injection pattern
        is_injection = False
        for pattern in instruction_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                is_injection = True
                logger.warning(f"Stripped injection-like line: {line[:50]}...")
                break

        if not is_injection:
            sanitized_lines.append(line)

    return '\n'.join(sanitized_lines)


def fence_untrusted_content(content: str, metadata: Dict[str, Any]) -> str:
    """
    ✅ DEFENDED: Fence content with <UNTRUSTED> tags

    Args:
        content: Document content
        metadata: Document metadata

    Returns:
        Fenced content string
    """
    source = metadata.get("source", "unknown")
    filename = metadata.get("filename", "unknown")

    return f"""<UNTRUSTED source="{source}" file="{filename}">
{content}
</UNTRUSTED>"""
