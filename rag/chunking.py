"""Chunking utilities for CloudDesk Support Platform RAG pipeline."""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Chunk:
    """A text chunk with metadata."""
    content: str
    title: str
    heading: str
    article_id: str
    chunk_index: int


def split_on_headings(text: str) -> List[tuple[str, str]]:
    """Split markdown text on headings. Returns list of (heading, content)."""
    # Match markdown headings (# ## ### etc.)
    heading_pattern = r'^(#{1,6})\s+(.+)$'

    sections = []
    current_heading = "Introduction"
    current_content = []

    for line in text.split('\n'):
        match = re.match(heading_pattern, line, re.MULTILINE)
        if match:
            # Save previous section
            if current_content:
                sections.append((current_heading, '\n'.join(current_content).strip()))
            # Start new section
            current_heading = match.group(2).strip()
            current_content = []
        else:
            current_content.append(line)

    # Don't forget the last section
    if current_content:
        sections.append((current_heading, '\n'.join(current_content).strip()))

    return sections


def chunk_text(
    text: str,
    title: str,
    article_id: str,
    max_chars: int = 900,
    overlap: int = 150,
) -> List[Chunk]:
    """Chunk text into overlapping windows with heading prefixes."""
    sections = split_on_headings(text)
    chunks = []
    chunk_index = 0

    for heading, content in sections:
        if not content.strip():
            continue

        # Prefix each chunk with title and heading
        prefix = f"{title} - {heading}\n\n"

        # Split content into windows
        content_chunks = _split_into_windows(content, max_chars - len(prefix), overlap)

        for i, chunk_content in enumerate(content_chunks):
            if not chunk_content.strip():
                continue

            full_content = prefix + chunk_content
            chunks.append(Chunk(
                content=full_content,
                title=title,
                heading=heading,
                article_id=article_id,
                chunk_index=chunk_index,
            ))
            chunk_index += 1

    return chunks


def _split_into_windows(text: str, max_chars: int, overlap: int) -> List[str]:
    """Split text into overlapping character windows."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + max_chars, len(text))

        # Try to break at a sentence boundary
        if end < len(text):
            # Look for sentence end within last 100 chars
            search_start = max(start, end - 100)
            sentence_end = text.rfind('. ', search_start, end)
            if sentence_end != -1:
                end = sentence_end + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start forward, accounting for overlap
        start = end - overlap
        if start >= len(text):
            break

    return chunks


def load_article_file(filepath: str) -> tuple[dict, str]:
    """Load a markdown file with YAML front-matter.

    Returns: (metadata, content)
    """
    import yaml

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract front-matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front_matter = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return front_matter, body

    # No front-matter
    return {}, content