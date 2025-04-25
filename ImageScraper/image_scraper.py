#!/usr/bin/env python
# coding: utf-8

# In[21]:

''' 일반적인 이미지 크롤링 '''
import os
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.request import urlretrieve


class ImageScraper:
    def __init__(self):
        self.keyword = ""
        self.image_name = ""
        self.image_cnt = 0
        self.images_url = []
        self.driver = None

    def get_input(self):
        """사용자로부터 검색 키워드, 이미지 이름, 개수를 입력받음"""
        self.keyword = input("검색할 키워드 : ")
        self.image_name = input("저장할 이미지 이름 : ")
        self.image_cnt = int(input("저장할 이미지 개수 : "))

    def scroll_down(self):
        while len(self.images_url) < self.image_cnt:
            time.sleep(3)
            # 페이지 맨 아래로 스크롤
            self.driver.find_element(By.XPATH, '//body').send_keys(Keys.END)
            time.sleep(3)
            
            # 이미지 요소 가져오기
            images = self.driver.find_elements(By.CSS_SELECTOR, ".YQ4gaf")
            
            # 새로운 이미지 URL을 추가
            for image in images:
                try:
                    image.click()
                    time.sleep(1)
                    img = self.driver.find_element(By.XPATH, "//*[@id='Sva75c']/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img[2]")
                    url = img.get_attribute('src') or img.get_attribute('data-src')
                    if url and url not in self.images_url:
                        self.images_url.append(url)
                except:
                    pass
                
                # 원하는 개수만큼 URL이 모였으면 종료
                if len(self.images_url) == self.image_cnt:
                    break
            
            # '더보기' 버튼이 보이면 클릭
            try:
                load_more_button = self.driver.find_element(By.XPATH, '//*[@id="islmp"]/div/div/div/div/div[1]/div[2]/div[2]/input')
                if load_more_button.is_displayed():
                    load_more_button.click()
            except:
                pass
            
            # '더 이상 표시할 콘텐츠가 없습니다.' 메시지가 보이면 종료
            try:
                no_more_content = self.driver.find_element(By.XPATH, '//div[@class="K25wae"]//*[text()="더 이상 표시할 콘텐츠가 없습니다."]')
                if no_more_content.is_displayed():
                    break
            except:
                pass
        
        return self.images_url

    def start_driver(self):
        op = Options()
        # op.add_argument('--headless')
        op.add_argument('--no-sandbox')
        op.add_argument("window-size=1920x1080")
        op.add_argument("disable-gpu")
        op.add_argument("lang=ko_KR")
        op.add_argument('--disable-dev-shm-usage')

        # Service 객체로 ChromeDriver 경로 지정
        service = Service(executable_path="./chromedriver.exe")
        self.driver = webdriver.Chrome(service=service, options=op)

    def search_images(self):
        # 구글 이미지 검색 페이지로 이동
        self.driver.get('http://www.google.co.kr/imghp')

        # 검색어 입력
        browser = self.driver.find_element(By.NAME, 'q')
        browser.send_keys(self.keyword)
        browser.send_keys(Keys.RETURN)

    def download_images(self):
        # 이미지 URL 수집
        self.images_url = self.scroll_down()

        # 중복된 URL 제거
        self.images_url = pd.DataFrame(self.images_url)[0].unique()

        # 이미지 다운로드
        os.makedirs(f'./{self.image_name}', exist_ok=True)
        for i, url in enumerate(self.images_url[:self.image_cnt]):
            urlretrieve(url, f'./{self.image_name}/{self.image_name}_{i}.jpg')

    def quit_driver(self):
        # 브라우저 종료
        self.driver.quit()

    def scrape_images(self):
        # 사용자 입력 받기
        self.get_input()

        self.start_driver()
        self.search_images()
        self.download_images()
        self.quit_driver()


''' 특정 페이지에서 이미지 크롤링 '''
import os
import requests as rq
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlretrieve


class ImageScraper_on_Specific_Page:
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
