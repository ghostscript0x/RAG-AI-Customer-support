"""DOCX text extraction using python-docx."""

import logging
from pathlib import Path
from typing import Optional

from docx import Document

logger = logging.getLogger(__name__)


def load_docx(file_path: str) -> Optional[str]:
    """Extract text from a DOCX file.

    Args:
        file_path: Path to the DOCX file.

    Returns:
        Extracted text as a single string, or None if extraction failed.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.error("DOCX file not found: %s", file_path)
            return None

        doc = Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        if not paragraphs:
            logger.warning("No text extracted from DOCX: %s", file_path)
            return None

        return "\n\n".join(paragraphs)
    except Exception as exc:
        logger.exception("Failed to extract text from DOCX %s", file_path)
        return None
