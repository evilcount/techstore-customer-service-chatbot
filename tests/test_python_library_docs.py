from src.rag.python_library_docs import docs_to_documents, parse_html_to_text, save_doc_text


def test_parse_html_to_text_keeps_title_headings_and_code():
    html = """
    <html>
      <head><title>Quickstart - Requests</title></head>
      <body>
        <nav>Navigation should be removed</nav>
        <main>
          <h1>Quickstart</h1>
          <p>Use requests.get to make a request.</p>
          <pre><code>requests.get("https://example.com", timeout=5)</code></pre>
        </main>
      </body>
    </html>
    """

    text = parse_html_to_text(html)

    assert "Quickstart" in text
    assert "Use requests.get" in text
    assert 'requests.get("https://example.com", timeout=5)' in text
    assert "Navigation should be removed" not in text


def test_save_doc_text_writes_metadata_header(tmp_path):
    output_path = save_doc_text(
        output_dir=tmp_path,
        slug="quickstart",
        title="Quickstart",
        source_url="https://requests.readthedocs.io/en/latest/user/quickstart/",
        text="Use params to pass query strings.",
    )

    written = output_path.read_text(encoding="utf-8")

    assert output_path.name == "requests_quickstart.txt"
    assert "Title: Quickstart" in written
    assert "Source URL: https://requests.readthedocs.io/en/latest/user/quickstart/" in written
    assert "Use params to pass query strings." in written


def test_docs_to_documents_loads_saved_txt_with_metadata(tmp_path):
    save_doc_text(
        output_dir=tmp_path,
        slug="api",
        title="Developer Interface",
        source_url="https://requests.readthedocs.io/en/latest/api/",
        text="Session objects persist cookies across requests.",
    )

    docs = docs_to_documents(tmp_path)

    assert len(docs) == 1
    assert "persist cookies" in docs[0].page_content
    assert docs[0].metadata["library"] == "requests"
    assert docs[0].metadata["title"] == "Developer Interface"
    assert docs[0].metadata["source_url"] == "https://requests.readthedocs.io/en/latest/api/"
