import os
from bs4 import BeautifulSoup

def _require_lucene():
    try:
        import lucene
        from java.nio.file import Paths
        from org.apache.lucene.analysis.standard import StandardAnalyzer
        from org.apache.lucene.document import Document, Field, StringField, TextField
        from org.apache.lucene.index import DirectoryReader, IndexWriter, IndexWriterConfig
        from org.apache.lucene.queryparser.classic import QueryParser
        from org.apache.lucene.search import BooleanClause, BooleanQuery, BoostQuery, IndexSearcher
        from org.apache.lucene.store import FSDirectory
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PyLucene is not installed"
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
        "QueryParser": QueryParser,
        "BooleanClause": BooleanClause,
        "BooleanQuery": BooleanQuery,
        "BoostQuery": BoostQuery,
        "IndexSearcher": IndexSearcher,
        "FSDirectory": FSDirectory,
    }


def _ensure_vm():
    lucene_deps = _require_lucene()
    lucene = lucene_deps["lucene"]
    if not lucene.getVMEnv():
        lucene.initVM()
    return lucene_deps


def build_index():
    OUTPUT_DIR = "./output"
    INDEX_DIR = "./index"
    deps = _ensure_vm()
    analyzer = deps["StandardAnalyzer"]()
    index_path = deps["FSDirectory"].open(deps["Paths"].get(INDEX_DIR))
    config = deps["IndexWriterConfig"](analyzer)
    writer = deps["IndexWriter"](index_path, config)

    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".html")]
    print(f"Indexing {len(files)} files...")

    for i, filename in enumerate(files):
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "rb") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            title = soup.title.string if soup.title else ""
            body = soup.get_text(separator=" ", strip=True)
            url = filename

        doc = deps["Document"]()
        doc.add(deps["TextField"]("title", title or "", deps["Field"].Store.YES))
        doc.add(deps["TextField"]("body", body, deps["Field"].Store.YES))
        doc.add(deps["StringField"]("url", url, deps["Field"].Store.YES))
        writer.addDocument(doc)

        if (i + 1) % 100 == 0:
            print(f"Indexed {i + 1} / {len(files)}")

    writer.commit()
    writer.close()
    print("Indexing complete.")

# TODO: Implement search function
# def search(query: str, top_n: int = 10):


if __name__ == "__main__":
    build_index()