# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from lesson_6.bookparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/genres/2791/']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath('//div[@data-title= "Все в жанре «Фантастика»"]'
                                    '/div[contains(@class, "col-xl-2")]//a[contains(@class, "title-link")]/@href').getall()
        for link in book_links:
            yield response.follow(link, callback=self.process_item)

        next_page = response.xpath('//a[contains(@class, "pagination-next")]/@href').get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def process_item(self, response: HtmlResponse):
        name = response.xpath('//h1/text()').get()
        author = response.xpath('//div[@class="authors"][position()=1]/a/text()').getall()
        price = response.xpath('//span[contains(@class, "buying-price")]/text()').getall()
        rate = response.xpath('//div[@id="rate"]/text()').get()

        item = BookparserItem()

        item["url"] = response.url
        item["name"] = name
        item["author"] = author
        item["price"] = price
        item["rate"] = rate

        yield item

