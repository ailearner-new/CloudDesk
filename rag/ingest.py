"""Knowledge base ingestion for CloudDesk Support Platform."""

import asyncio
from pathlib import Path

from rag.retriever import ingest_knowledge_base


async def main():
    """Main ingestion entry point."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    import os
    os.environ.setdefault("DEMO_MODE", "true")
    os.environ.setdefault("VECTOR_STORE", "memory")
    os.environ.setdefault("EMBEDDING_PROVIDER", "fake")

    sample_data_dir = Path(os.getenv("SAMPLE_DATA_DIR", "sample_data"))
    kb_dir = sample_data_dir / "knowledge_base"

    if not kb_dir.exists():
        print(f"Knowledge base directory not found: {kb_dir}")
        sys.exit(1)

    md_files = list(kb_dir.glob("*.md"))
    print(f"Found {len(md_files)} markdown files in {kb_dir}")

    result = await ingest_knowledge_base(kb_dir)

    print(f"Indexed {result['chunks']} chunks from {result['articles']} articles")


if __name__ == "__main__":
    asyncio.run(main())