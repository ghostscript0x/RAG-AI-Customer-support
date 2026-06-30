"""CSV text extraction."""

import csv
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def load_csv(file_path: str) -> Optional[str]:
    """Extract text from a CSV file, converting rows to readable text.

    Args:
        file_path: Path to the CSV file.

    Returns:
        Extracted text as a single string, or None if extraction failed.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.error("CSV file not found: %s", file_path)
            return None

        rows = []
        with open(str(path), newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if headers:
                rows.append(" | ".join(headers))
            for row in reader:
                rows.append(" | ".join(row))

        if not rows:
            logger.warning("No data in CSV: %s", file_path)
            return None

        return "\n".join(rows)
    except Exception as exc:
        logger.exception("Failed to extract text from CSV %s", file_path)
        return None
