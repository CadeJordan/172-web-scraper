# 172-web-scraper
Web scraper project UCR CS 172 

# Dataset
- total size: 672MB (2,000 HTML files)
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
1. cd into scrapy_project folder

2. run this command to start crawling

Linux:
bash ../crawler.sh ../data/seeds.txt 2000 6 ../output

Windows:
crawler.bat ..\data\seeds.txt 2000 6 ..\output

3. to see how much data was collected

du -sh ../output

4. to check how many files (2000)

ls ../output | wc -l

## Run the Flask app

1. Create a Python virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Ensure PyLucene index exists at `./index`.
4. Start the server:
   - `python app.py`
5. Open:
   - `http://localhost:5000`

Search endpoint: `GET /api/search?q=<query>`
Returns top 10 results ordered by descending score.
