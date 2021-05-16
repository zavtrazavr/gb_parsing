import scrapy
from scrapy.http import HtmlResponse
from lesson_7.items import Lesson7Item
from scrapy.loader import ItemLoader

class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super().__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response:HtmlResponse):
        product_links = response.xpath('//div[@class="phytpj4_plp largeCard"]/a')

        for link in product_links:
            yield response.follow(link, callback=self.parse_item)

    def parse_item(self, response:HtmlResponse):
        loader = ItemLoader(item=Lesson7Item(), response=response)

        loader.add_xpath("name", '//h1/text()')
        loader.add_value("url", response.url)
        loader.add_xpath("price", '//span[@slot="price"]/text()')

        param_keys = loader.get_xpath('//dt[@class="def-list__term"]/text()')
        param_values = loader.get_xpath('//dd[@class="def-list__definition"]/text()')
        loader.add_value("parameters", dict([[y, param_values[x]] for x, y in enumerate(param_keys)]))

        loader.add_xpath("photos", '//img[@alt="product image"]/@src')

        yield loader.load_item()
