# pipelines.py
import os
import hashlib

class SaveHtmlPipeline:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(output_dir=crawler.settings.get("OUTPUT_DIR", "crawled_pages"))

    def process_item(self, item, spider):
        filename = hashlib.md5(item["url"].encode()).hexdigest() + ".html"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(item["body"])
        return item