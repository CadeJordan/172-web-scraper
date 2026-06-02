import lucene
import os
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.document import Document, Field, TextField, StringField
from org.apache.lucene.analysis.standard import StandardAnalyzer
from java.nio.file import Paths
from bs4 import BeautifulSoup

lucene.initVM()

OUTPUT_DIR = "./output"
INDEX_DIR = "./index"

analyzer = StandardAnalyzer()
index_path = FSDirectory.open(Paths.get(INDEX_DIR))
config = IndexWriterConfig(analyzer)
writer = IndexWriter(index_path, config)

files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".html")]
print(f"Indexing {len(files)} files...")

for i, filename in enumerate(files):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "rb") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        title = soup.title.string if soup.title else ""
        body = soup.get_text(separator=" ", strip=True)
        url = filename

    doc = Document()
    doc.add(TextField("title", title or "", Field.Store.YES))
    doc.add(TextField("body", body, Field.Store.YES))
    doc.add(StringField("url", url, Field.Store.YES))
    writer.addDocument(doc)

    if (i + 1) % 100 == 0:
        print(f"Indexed {i + 1} / {len(files)}")

writer.commit()
writer.close()
print("Indexing complete.")