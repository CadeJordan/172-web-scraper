import scrapy


class CrawledPage(scrapy.Item):
    url = scrapy.Field()
    depth = scrapy.Field()
    status = scrapy.Field()
    content_type = scrapy.Field()
    body = scrapy.Field()
