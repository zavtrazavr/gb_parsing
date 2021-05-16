import os
from dotenv import load_dotenv
import requests


def get_weather(city):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    load_dotenv()
    token = os.getenv("WEATHER_TOKEN")

    params = {"q": city,
              "appid": token,
              "units": "metric",
              "lang": "ru"}

    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        res = response.json()

        cur_weather = f'{res["weather"][0]["description"]}\n' \
                      f'температура: {res["main"]["temp"]} градусов\n' \
                      f'ощущается как {res["main"]["feels_like"]} градусов'

        return cur_weather
    else:
        print(f'Error while API call. Response code: {response.status_code}')

if __name__ == '__main__':
	city = input("Введите название города\n")
	print(get_weather(city))

