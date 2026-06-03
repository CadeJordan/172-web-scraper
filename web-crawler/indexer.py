import os
import re
from pathlib import Path

from bs4 import BeautifulSoup


DEFAULT_OUTPUT_DIR = "./output/html"
DEFAULT_INDEX_DIR = "./index"
SNIPPET_LENGTH = 240


def _require_lucene():
    try:
        import lucene
        from java.nio.file import Paths
        from org.apache.lucene.analysis.standard import StandardAnalyzer
        from org.apache.lucene.document import Document, Field, StringField, TextField
        from org.apache.lucene.index import DirectoryReader, IndexWriter, IndexWriterConfig
        from org.apache.lucene.queryparser.classic import MultiFieldQueryParser, QueryParser
        from org.apache.lucene.search import IndexSearcher
        from org.apache.lucene.store import FSDirectory
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyLucene is not installed. Run this in the PyLucene environment used for the project."
        ) from exc

    return {
        "lucene": lucene,
        "Paths": Paths,
        "StandardAnalyzer": StandardAnalyzer,
        "Document": Document,
        "Field": Field,
        "StringField": StringField,
        "TextField": TextField,
        "DirectoryReader": DirectoryReader,
        "IndexWriter": IndexWriter,
        "IndexWriterConfig": IndexWriterConfig,
        "MultiFieldQueryParser": MultiFieldQueryParser,
        "QueryParser": QueryParser,
        "IndexSearcher": IndexSearcher,
        "FSDirectory": FSDirectory,
    }


def _ensure_vm():
    lucene_deps = _require_lucene()
    lucene = lucene_deps["lucene"]
    if not lucene.getVMEnv():
        lucene.initVM()
    return lucene_deps


def _iter_html_files(output_dir):
    base = Path(output_dir)
    if not base.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")
    return sorted(path for path in base.rglob("*.html") if path.is_file())


def _extract_page_fields(filepath):
    with open(filepath, "rb") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    title = soup.title.get_text(" ", strip=True) if soup.title else ""

    date = ""
    date_selectors = [
        ("meta", {"property": "article:published_time"}),
        ("meta", {"name": "pubdate"}),
        ("meta", {"name": "publishdate"}),
        ("meta", {"name": "date"}),
        ("meta", {"itemprop": "datePublished"}),
    ]
    for tag_name, attrs in date_selectors:
        tag = soup.find(tag_name, attrs=attrs)
        if tag and tag.get("content"):
            date = tag["content"].strip()
            break

    body = soup.get_text(separator=" ", strip=True)
    return title, body, date


def build_index(output_dir=DEFAULT_OUTPUT_DIR, index_dir=DEFAULT_INDEX_DIR):
    deps = _ensure_vm()
    analyzer = deps["StandardAnalyzer"]()
    index_path = deps["FSDirectory"].open(deps["Paths"].get(index_dir))
    config = deps["IndexWriterConfig"](analyzer)
    writer = deps["IndexWriter"](index_path, config)

    files = _iter_html_files(output_dir)
    print(f"Indexing {len(files)} files from {output_dir}...")

    for i, filepath in enumerate(files):
        title, body, date = _extract_page_fields(filepath)
        relative_path = str(filepath.relative_to(output_dir))

        doc = deps["Document"]()
        doc.add(deps["TextField"]("title", title or "", deps["Field"].Store.YES))
        doc.add(deps["TextField"]("body", body, deps["Field"].Store.YES))
        doc.add(deps["StringField"]("url", relative_path, deps["Field"].Store.YES))
        doc.add(deps["StringField"]("date", date, deps["Field"].Store.YES))
        writer.addDocument(doc)

        if (i + 1) % 100 == 0:
            print(f"Indexed {i + 1} / {len(files)}")

    writer.commit()
    writer.close()
    print("Indexing complete.")


def _query_terms(query):
    return [term.lower() for term in re.findall(r"[A-Za-z0-9]+", query) if len(term) > 1]


def _make_snippet(text, query, max_length=SNIPPET_LENGTH):
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return ""

    terms = _query_terms(query)
    lower_text = normalized.lower()
    hit_positions = [
        lower_text.find(term)
        for term in terms
        if lower_text.find(term) != -1
    ]
    center = min(hit_positions) if hit_positions else 0

    start = max(center - max_length // 3, 0)
    end = min(start + max_length, len(normalized))
    start = max(end - max_length, 0)

    if start > 0:
        next_space = normalized.find(" ", start)
        if next_space != -1 and next_space < center:
            start = next_space + 1

    snippet = normalized[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(normalized):
        snippet = snippet + "..."
    return snippet

def search(query, top_n=10, index_dir=DEFAULT_INDEX_DIR):
    query = (query or "").strip()
    if not query:
        return []

    from org.apache.lucene.queryparser.classic import QueryParser

    deps = _ensure_vm()
    analyzer = deps["StandardAnalyzer"]()
    index_path = deps["FSDirectory"].open(deps["Paths"].get(index_dir))
    reader = deps["DirectoryReader"].open(index_path)

    try:
        searcher = deps["IndexSearcher"](reader)
        parser = QueryParser("body", analyzer)
        lucene_query = parser.parse(query)
        hits = searcher.search(lucene_query, top_n).scoreDocs

        results = []
        for hit in hits:
            doc = searcher.doc(hit.doc)
            body = doc.get("body") or ""
            results.append(
                {
                    "documentId": hit.doc,
                    "score": float(hit.score),
                    "title": doc.get("title") or "(untitled)",
                    "url": doc.get("url") or "",
                    "date": doc.get("date") or "",
                    "snippet": _make_snippet(body, query),
                }
            )
        return results
    finally:
        reader.close()

if __name__ == "__main__":
    build_index()
