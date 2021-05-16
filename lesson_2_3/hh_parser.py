import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import re
from time import sleep
import pymongo


class HHParser:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'}
    search_url = 'https://hh.ru/search/vacancy'
    site_url = 'https://hh.ru'

    def __init__(self, vacancy, db_client):
        self.vacancy = vacancy
        self.db = db_client["gb_data_mining"]
        self.collection = self.db["vacancies"]

    def main(self):
        for vacancy in self._get_data(HHParser.search_url):
            self._save(vacancy)

    def _get_response(self, url, params=None):
        response = requests.get(url, headers=HHParser.headers, params=params)
        r_soup = bs(response.text, "html.parser")
        return r_soup

    def _get_data(self, url):
        params = {"text": self.vacancy}

        url_list = [f'{url}?text={self.vacancy}']

        response = self._get_response(url, params=params)
        raw_urls = response.find('span', attrs={'class': 'bloko-button-group'}).find_all("a")
        for item in raw_urls:
            plain_url = item.attrs.get("href")
            url_list.append(urljoin(HHParser.site_url, plain_url))

        for curr_url in url_list:
            response = self._get_response(curr_url)
            sleep(1)
            vacancy_catalogue = response.find('div',
                                              attrs={
                                                  'class': 'bloko-gap bloko-gap_s-top bloko-gap_m-top bloko-gap_l-top'})

            for vacancy in vacancy_catalogue.find_all('div', attrs={'class': 'vacancy-serp-item'}):
                vacancy_data = self._parse(vacancy)
                yield vacancy_data

    def _get_template(self):
        return ({
            "vacancy_name": lambda a: a.find('a').text,
            "vacancy_link": lambda a: a.find('a').attrs.get('href'),
            "salary": lambda a: re.sub('\\u202f', '', a.find('div', attrs={'class': 'vacancy-serp-item__sidebar'})
                                       .find('span').text)

        })

    def _parse(self, vacancy):
        data = {}
        for key, func in self._get_template().items():
            try:
                data[key] = func(vacancy)
            except AttributeError:
                pass

        return data

    def _save(self, data):
        self.collection.update_one({"vacancy_link": data["vacancy_link"]}, {"$set": data}, upsert=True)


if __name__ == "__main__":
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    test = HHParser('дата аналитик', db_client)
    test.main()


