# 172-web-scraper
Web scraper project UCR CS 172 

# Dataset
- total size: ~700 MB (2,000 HTML files)
- sample size: 2.8 MB under sample_output folder

# Requirements: 
- pip install scrapy
- Python 3.10+

# Important files & descriptions:
1. scrapy_project/technews_crawler/spiders/technews_spider.py - crawler
2. scrapy_project/technews_crawler/items.py - data structure
3. scrapy_project/technews_crawler/pipelines.py - saves html to disk
4. scrapy_project/technews_crawler/settings.py - config
5. data/seeds.txt - starting URLS
6. crawler.sh / crawler.bat - runs crawler

# How to Run

## Crawl

1. cd into `web-crawler/scrapy_project`

2. Run this command to start crawling:

Linux/macOS:
```bash
bash ../crawler.sh ../data/seeds.txt 2000 6 ../output/html
```

Windows:
```bat
crawler.bat ..\data\seeds.txt 2000 6 ..\output\html
```

3. To see how much data was collected:
```bash
du -sh ../output
```

4. To check how many files (should be ~2000):
```bash
ls ../output/html | wc -l
```

## Build the PyLucene Index

Run these commands from `web-crawler`:

Linux/macOS:
```bash
chmod +x indexer.sh
./indexer.sh output/html index
```

Windows:
```bat
indexer.bat output\html index
```

Or run directly:
```bash
python3 indexer.py
```

## Run the Flask Search App

1. Install Python dependencies from `web-crawler`:
```bash
pip3 install -r requirements.txt
```

2. Make sure the PyLucene index exists at `web-crawler/index`.

3. Start the server from `web-crawler`:
```bash
python3 app.py
```

4. Open `http://class-057.cs.ucr.edu:8080` in your browser.

The search endpoint is `GET /api/search?q=<query>`. It returns the top 10 PyLucene results in decreasing score order with title, URL/file id, date when available, document id, score, and an extra-credit snippet generated from the stored body text.
