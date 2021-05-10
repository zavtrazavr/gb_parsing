# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from lesson_6.bookparser.items import BookparserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/catalog/fantastika-1649/']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath('//div[@class = "product-card__content"]/a/@href').getall()
        for link in book_links:
            yield response.follow(link, callback=self.process_item)

        next_page = response.xpath('//link[@rel = "next"]/@href').get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def process_item(self, response: HtmlResponse):
        name = response.xpath('//h1/text()').get()
        author = response.xpath('//a[@itemprop="author"]/text()').getall()
        price = response.xpath('//div[@class = "item-actions__price"]/b/text()').get()
        old_price = response.xpath('//div[contains(@class, "price-old")]/text()').get()
        rate = response.xpath('//span[@itemprop = "ratingValue"]/text()').get()

        item = BookparserItem()

        item["url"] = response.url
        item["name"] = name
        item["author"] = author
        item["price"] = price
        item["old_price"] = old_price
        item["rate"] = rate

        yield item

