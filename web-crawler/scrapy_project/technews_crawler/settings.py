BOT_NAME = "technews_crawler"
SPIDER_MODULES = ["technews_crawler.spiders"]
NEWSPIDER_MODULE = "technews_crawler.spiders"
ROBOTSTXT_OBEY = True
USER_AGENT = "technews_crawler (+https://github.com/educational-use) Scrapy"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
DEPTH_STATS_VERBOSE = True
SPIDER_MIDDLEWARES = {"scrapy.spidermiddlewares.depth.DepthMiddleware": None,}

ITEM_PIPELINES = {"technews_crawler.pipelines.SaveHtmlPipeline": 300}
OUTPUT_DIR = "crawled_pages"

DUPEFILTER_CLASS = "scrapy.dupefilters.RFPDupeFilter"
DUPEFILTER_DEBUG = True

DOWNLOAD_HANDLERS = {}
DENY_EXTENSIONS = [
    'pdf', 'jpg', 'jpeg', 'png', 'gif', 'svg', 'mp4',
    'mp3', 'zip', 'tar', 'gz', 'doc', 'docx', 'xls'
]

CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 4
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 5
