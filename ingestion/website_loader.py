"""Website text extraction using requests and BeautifulSoup."""

import logging
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30


def load_website(url: str) -> Optional[str]:
    """Extract readable text content from a URL.

    Args:
        url: The website URL to scrape.

    Returns:
        Extracted text as a single string, or None if extraction failed.
    """
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)

        text = re.sub(r"\n{3,}", "\n\n", text)

        if not text:
            logger.warning("No text extracted from URL: %s", url)
            return None

        return text
    except requests.RequestException as exc:
        logger.error("Failed to fetch URL %s: %s", url, exc)
        return None
    except Exception as exc:
        logger.exception("Failed to extract text from URL %s", url)
        return None
