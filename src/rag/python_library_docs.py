from __future__ import annotations

from pathlib import Path

import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document


REQUESTS_DOC_PAGES = {
    "quickstart": {
        "title": "Quickstart",
        "url": "https://requests.readthedocs.io/en/latest/user/quickstart/",
    },
    "advanced": {
        "title": "Advanced Usage",
        "url": "https://requests.readthedocs.io/en/latest/user/advanced/",
    },
    "api": {
        "title": "Developer Interface",
        "url": "https://requests.readthedocs.io/en/latest/api/",
    },
}


def fetch_requests_docs(output_dir: str | Path) -> list[Path]:
    """Fetch selected official Requests documentation pages as local text files."""
    output = Path(output_dir)
    saved_paths = []
    for slug, page in REQUESTS_DOC_PAGES.items():
        response = requests.get(page["url"], timeout=30)
        response.raise_for_status()
        text = parse_html_to_text(response.text)
        saved_paths.append(
            save_doc_text(
                output_dir=output,
                slug=slug,
                title=page["title"],
                source_url=page["url"],
                text=text,
            )
        )
    return saved_paths


def parse_html_to_text(html: str) -> str:
    """Extract readable documentation text from a Sphinx/ReadTheDocs HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    for selector in ["nav", "header", "footer", "script", "style", ".wy-nav-side"]:
        for element in soup.select(selector):
            element.decompose()

    main = soup.select_one("main") or soup.select_one("[role='main']") or soup.body or soup
    parts = []
    for element in main.find_all(["h1", "h2", "h3", "p", "li", "pre", "code"]):
        text = element.get_text(" ", strip=True)
        if text:
            parts.append(text)
    return "\n\n".join(_dedupe_preserve_order(parts))


def save_doc_text(
    *,
    output_dir: str | Path,
    slug: str,
    title: str,
    source_url: str,
    text: str,
) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / f"requests_{slug}.txt"
    path.write_text(
        f"Title: {title}\nSource URL: {source_url}\nLibrary: requests\n\n{text.strip()}\n",
        encoding="utf-8",
    )
    return path


def docs_to_documents(path: str | Path) -> list[Document]:
    """Load saved Requests documentation text files with source metadata."""
    root = Path(path)
    documents = []
    for file_path in sorted(root.glob("requests_*.txt")):
        raw_text = file_path.read_text(encoding="utf-8").strip()
        metadata = _metadata_from_header(raw_text)
        metadata.update(
            {
                "source": str(file_path),
                "document_type": "txt",
                "library": "requests",
            }
        )
        documents.append(Document(page_content=raw_text, metadata=metadata))
    return documents


def _metadata_from_header(raw_text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in raw_text.splitlines()[:4]:
        if line.startswith("Title: "):
            metadata["title"] = line.removeprefix("Title: ").strip()
        elif line.startswith("Source URL: "):
            metadata["source_url"] = line.removeprefix("Source URL: ").strip()
    return metadata


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for item in items:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped
