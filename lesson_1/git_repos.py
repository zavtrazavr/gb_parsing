import os
from dotenv import load_dotenv
import requests
import json


def get_repos(url, params):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        response_json = response.json()
        return response_json
    else:
        print(f'Error while API call. Response code {response.status_code}')


def main(username: str):
    load_dotenv()
    token = os.getenv("GIT_TOKEN")

    params = {"type": "owner",
              "page": 0,
              "per_page": 100,
              "access_token": token}
    url = f'https://api.github.com/users/{username}/repos'

    while 1:
        params["page"] += 1
        res = get_repos(url, params)

        if not res:
            break

        with open(f"{username}_repos.json", "a") as f:
            json.dump(res, f, indent=4)

        for repo in res:
            print(repo["name"], repo["html_url"])


if __name__ == '__main__':
    main("benjamn")


