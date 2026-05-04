BOT_NAME = "tech_news_crawler"
SPIDER_MODULES = ["tech_news_crawler.spiders"]
NEWSPIDER_MODULE = "tech_news_crawler.spiders"
ROBOTSTXT_OBEY = True
USER_AGENT = "tech_news_crawler (+https://github.com/educational-use) Scrapy"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
DEPTH_STATS_VERBOSE = True
SPIDER_MIDDLEWARES = {"scrapy.spidermiddlewares.depth.DepthMiddleware": None,}
