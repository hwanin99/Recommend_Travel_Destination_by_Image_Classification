''' 일반적인 이미지 크롤링 '''
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time
import os
from urllib.request import urlretrieve


class ImageScraper:
    def __init__(self):
        self.keyword = ""
        self.image_name = ""
        self.image_cnt = 0
        self.driver = None

    def get_input(self):
        """사용자로부터 검색 키워드, 이미지 이름, 개수를 입력받음"""
        self.keyword = input("검색할 키워드 : ")
        self.image_name = input("저장할 이미지 이름 : ")
        self.image_cnt = int(input("저장할 이미지 개수 : "))

    def start_driver(self):
        options = Options()
#         options.add_argument('--headless')  # 창 숨기기
        options.add_argument('--no-sandbox')
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")
        options.add_argument("lang=ko_KR")
        options.add_argument('--disable-dev-shm-usage')

        service = Service(executable_path="./chromedriver.exe")
        self.driver = webdriver.Chrome(service=service, options=options)

    def search_images(self):
        self.driver.get('http://www.google.co.kr/imghp')
        search_box = self.driver.find_element(By.NAME, 'q')
        search_box.send_keys(self.keyword)
        search_box.send_keys(Keys.RETURN)

    def scroll_and_download(self):
        saved = 0
        seen_urls = set()
        os.makedirs(f'./{self.image_name}', exist_ok=True)

        while saved < self.image_cnt:
            time.sleep(2)
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)

            thumbnails = self.driver.find_elements(By.CSS_SELECTOR, ".YQ4gaf")

            for thumb in thumbnails:
                try:
                    thumb.click()
                    time.sleep(1.5)

                    img = self.driver.find_element(By.XPATH, "//*[@id='Sva75c']//img[@jsname='kn3ccd']")
                    url = img.get_attribute('src') or img.get_attribute('data-src')

                    if url and url.startswith("http") and url not in seen_urls:
                        seen_urls.add(url)
                        file_path = f'./{self.image_name}/{self.image_name}_{saved}.jpg'
                        urlretrieve(url, file_path)
                        print(f"[{saved + 1}] 저장 완료: {file_path}")
                        saved += 1

                    if saved >= self.image_cnt:
                        break

                except Exception as e:
                    continue

            # '더보기' 버튼 클릭
            try:
                load_more = self.driver.find_element(By.XPATH, '//input[@value="더보기"]')
                if load_more.is_displayed():
                    load_more.click()
                    time.sleep(1)
            except:
                pass

        print(f"\n✅ 총 {saved}장의 이미지를 저장했습니다.")

    def quit_driver(self):
        self.driver.quit()

    def scrape_images(self):
        self.get_input()
        self.start_driver()
        self.search_images()
        self.scroll_and_download()
        self.quit_driver()



''' 특정 페이지에서 이미지 크롤링 '''
import os
import requests as rq
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlretrieve


class ImageScraper_on_SpecificPage:
    def __init__(self):
        self.page_url = ""
        self.image_name = ""
        
    def get_input(self):
        self.page_url = input("이미지를 가져올 페이지 URL : ")
        self.image_name = input("저장할 이미지 이름 : ")

    def download_image(self):
        res = rq.get(self.page_url)
        soup = BeautifulSoup(res.text, 'lxml')

        tags1 = soup.select('.tt_article_useless_p_margin.contents_style b')
        tags2 = soup.select_one('.tt_article_useless_p_margin.contents_style').select('img')

        for idx, tag in enumerate(tags1):
            title = tag.text
            title = title.split(' ')
            del title[0]
            title = '_'.join(map(str, title))
            img_path = f'./{self.image_name}/{title}.jpg'

            tag2 = tags2[idx]
            img_url = tag2.get('src')
            img_url = urljoin(self.page_url, img_url)  # 상대 경로를 절대 경로로 변환

            os.makedirs(f'./{self.image_name}', exist_ok=True)

            urlretrieve(img_url, img_path)  # 이미지 다운로드

            print(f'Saved image: {img_path}')
    
    def scrape_images(self):
        self.get_input()
        self.download_image()
