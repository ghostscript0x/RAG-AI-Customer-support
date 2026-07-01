"""PDF text extraction using pypdf."""

import logging
from pathlib import Path
from typing import Optional

from pypdf import PdfReader
from pypdf.errors import EmptyFileError

logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> Optional[str]:
    """Extract text from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text as a single string, or None if extraction failed.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.error("PDF file not found: %s", file_path)
            return None

        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages.append(text)

        if not pages:
            logger.warning("No text extracted from PDF: %s", file_path)
            return None

        return "\n\n".join(pages)
    except EmptyFileError:
        logger.error("PDF file is empty: %s", file_path)
        return None
    except Exception as exc:
        logger.exception("Failed to extract text from PDF %s", file_path)
        return None
