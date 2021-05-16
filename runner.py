from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess

from lesson_7 import settings
from lesson_7.spiders.leroymerlin import LeroymerlinSpider
from urllib.parse import quote_plus

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    search = quote_plus(input("Введите товар\n"))

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinSpider, search=search)

    process.start()
