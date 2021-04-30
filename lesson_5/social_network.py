import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time



def save(data):
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    db = db_client["gb_data_mining"]
    collection = db["posts"]

    collection.insert_one(data)


url = "https://vk.com/tokyofashion"
search_word = 'Токио'
options = Options()
options.add_argument("start-maximized")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.get(url)


search_field = driver.find_element_by_xpath(".//a[contains(@class, 'tab_search')]")
search_link = search_field.get_attribute("href")
driver.get(search_link)

search_page = driver.find_element_by_class_name("ui_search_field")
search_page.send_keys(search_word + Keys.ENTER)

html = driver.find_element_by_tag_name("html")

for i in range(5):
    html.send_keys(Keys.END)
    time.sleep(2)

posts_info = driver.find_elements_by_xpath(".//div[contains(@id,'post-')]")

for item in posts_info:
    post_data = {}
    try:
        post_data["post_date"] = item.find_element_by_class_name("rel_date").text
        post_data["post_text"] = item.find_element_by_class_name("wall_text").text
        post_data["post_link"] = item.find_element_by_class_name("post_link").get_attribute("href")
        post_data["likes_cnt"] = item.find_element_by_xpath(".//a[contains(@class,'like_btn like')]//div[@class = 'like_button_count']").text
        post_data["reposts_cnt"] = item.find_element_by_xpath(".//a[contains(@class,'like_btn share')]//div[@class = 'like_button_count']").text
        save(post_data)
    except Exception as e:
        pass




