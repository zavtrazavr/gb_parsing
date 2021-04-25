import requests
from lxml import html
from urllib.parse import urljoin
from datetime import datetime
from abc import ABC, abstractmethod
import pymongo

class NewsParser(ABC):

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'}

    def __init__(self, site_info: dict, db_client):
        self.site_info = site_info
        self.db = db_client["gb_data_mining"]
        self.collection = self.db["news"]

    def main(self):
        page = self._get_response(self.site_info["url"])
        for result in self._parse(page):
            self._save(result)
        return 'News has been updated'

    @classmethod
    def _get_response(cls, url):
        response = requests.get(url, headers=NewsParser.headers)
        if response.status_code == 200:
            return html.fromstring(response.text)
        else:
            print(f'Bad status code: {response.status_code}')
            return None

    def _get_template(self, type):
        if type == "main page":
            return ({"name": lambda a: a.xpath(self.site_info["news_name"])[0],
                     "link": lambda a: urljoin(self.site_info["url"], a.xpath(self.site_info["news_link"])[0])
                     })
        else:

            return ({"news_dttm": lambda a: a.xpath(self.site_info["datetime"])[0],
                     "source": lambda a: a.xpath(self.site_info["news_source"])[0]
                     })

    def _parse(self, news_page):

        news_data = news_page.xpath(self.site_info["news_block"])

        for item in news_data:
            data = {}
            for key, func in self._get_template("main page").items():
                data[key] = func(item)
            data.update(self._get_add_info(data["link"]))

            yield data

    @abstractmethod
    def _get_add_info(self, link):
        pass

    def _save(self, data):
        self.collection.update_one({"name": data["name"]}, {"$set": data}, upsert=True)


class LentaParser(NewsParser):

    def _get_template(self, type):
        if type == "main page":
            return ({"name": lambda a: a.xpath(self.site_info["news_name"])[0],
                     "link": lambda a: urljoin(self.site_info["url"], a.xpath(self.site_info["news_link"])[0])
                     })
        else:
            return ({"news_dttm": lambda a: datetime.fromisoformat(a.xpath(self.site_info["dttm_attr"])[0]),
                     })

    def _get_add_info(self, link):
        response = NewsParser._get_response(link)
        dttm_block = response.xpath(self.site_info["dttm_block"])

        for item in dttm_block:
            data = {}
            for key, func in self._get_template("news page").items():
                data[key] = func(item)
                data["source"] = self.site_info["url"]
            return data


class MailruParser(NewsParser):


    def _get_add_info(self, link):
        response = NewsParser._get_response(link)
        add_info_block = response.xpath(self.site_info["add_info_block"])

        for item in add_info_block:
            data = {}
            for key, func in self._get_template("news page").items():
                data[key] = func(item)
            return data


class YanewsParser(NewsParser):

    def _get_add_info(self, link):
        pass

    def _get_template(self, type):
        return ({"name": lambda a: a.xpath(self.site_info["news_name"])[0],
                 "link": lambda a: urljoin(self.site_info["url"], a.xpath(self.site_info["news_link"])[0]),
                 "news_dttm": lambda a: datetime.combine(datetime.date(datetime.now()),
                                                         datetime.strptime(a.xpath(self.site_info["datetime"])[0], '%H:%M').time()),
                 "source": lambda a: a.xpath(self.site_info["news_source"])[0]
                 })

    def _parse(self, news_page):
        news_data = news_page.xpath(self.site_info["news_block"])

        for item in news_data:
            for i in range(len(item)):
                data = {}
                for key, func in self._get_template("main page").items():
                    data[key] = func(item[i])
                yield data


if __name__ == "__main__":
    lenta_info = {'url': 'https://lenta.ru/',
            'news_block':'//div[contains(@class,"yellow-box")]/div[@class = "item"]',
            'news_name': './/text()',
            'news_link': './/@href',
            'dttm_block': '//div[contains(@class, "topic__info")]',
            'dttm_attr': './/time/@datetime'}

    mailru_info = {'url': 'https://news.mail.ru/',
            'news_block': '//div[contains(@class,"daynews__item")]',
            'news_name': './/text()',
            'news_link': './/@href',
            'add_info_block': '//div[contains(@class,"article")]',
            'datetime': './/span[contains(@class, "ago")]/@datetime',
            'news_source': './/a/@href'
                   }

    yanews_info = {'url': 'https://yandex.com/news/',
            'news_block': '//div[contains(@class, "news-top-flexible")]',
            'news_name': './/h2/text()',
            'news_link': './/@href',
            'datetime': './/span[contains(@class, "__time")]/text()',
            'news_source': './/span[contains(@class, "__source")]/a/text()'
                   }

    db_client = pymongo.MongoClient("mongodb://localhost:27017")

    lenta = LentaParser(lenta_info, db_client)
    mailru = MailruParser(mailru_info, db_client)
    yanews = YanewsParser(yanews_info, db_client)

    lenta.main()
    mailru.main()
    yanews.main()