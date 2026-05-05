
# pipelines.py
#import os
#import hashlib

#class SaveHtmlPipeline:
    #def __init__(self, output_dir):
       # self.output_dir = output_dir
        #os.makedirs(output_dir, exist_ok=True)

    #@classmethod
   # def from_crawler(cls, crawler):
     #   return cls(output_dir=crawler.settings.get("OUTPUT_DIR", "crawled_pages"))

   # def process_item(self, item, spider):
    #    filename = hashlib.md5(item["url"].encode()).hexdigest() + ".html"
     #   filepath = os.path.join(self.output_dir, filename)
      #  with open(filepath, "wb") as f:
       #     f.write(item["body"])
        #return item
# pipelines.py
import os
import json
import hashlib


class SaveHtmlPipeline:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.pages_dir = os.path.join(output_dir, "pages")
        self.metadata_path = os.path.join(output_dir, "metadata.jsonl")

        os.makedirs(self.pages_dir, exist_ok=True)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(output_dir=crawler.settings.get("OUTPUT_DIR", "crawled_pages"))

    def process_item(self, item, spider):
        # Create a safe and consistent filename from the URL
        filename = hashlib.md5(item["url"].encode("utf-8")).hexdigest() + ".html"
        filepath = os.path.join(self.pages_dir, filename)

        # Save raw HTML page
        with open(filepath, "wb") as f:
            f.write(item["body"])

        # Save metadata for later indexing/search
        metadata = {
            "url": item.get("url", ""),
            "filename": os.path.join("pages", filename),
            "title": item.get("title", ""),
            "depth": item.get("depth", ""),
            "status": item.get("status", ""),
            "content_type": item.get("content_type", ""),
        }

        with open(self.metadata_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(metadata, ensure_ascii=False) + "\n")

        return item