#크롤링 라이브러리 import
from bs4 import BeautifulSoup 
#셀레늄 라이브러리 불러오기
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
#셀레늄에서 html문서가 생성될 때까지 대기하는 함수 불러오기
from selenium.webdriver.support.ui import WebDriverWait
#셀레늄에서 조건을 걸어줄 수 있는 함수 불러오기
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import random

class Crawler(object):
    def __init__(self, app_name, target_rating):
        self.json_file = None
        self.app_name = app_name
        self.target_rating = target_rating

        #User-Agent 지정
        self.headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

        # URL 설정 
        self.start_URL = f'https://play.google.com/store/search?q={app_name}&c=apps'

        # id 
        self.id_start = '//*[@id="yDmH0d"]/div[5]/div[2]/div/div/div/div/div[2]/div/div[1]/div['
        self.id_end = ']/header/div[1]/div[1]/div'

        # date
        self.date_start = '//*[@id="yDmH0d"]/div[5]/div[2]/div/div/div/div/div[2]/div/div[1]/div['
        self.date_end =']/header/div[2]/span'

        # rating 
        self.rating_start = '//*[@id="yDmH0d"]/div[5]/div[2]/div/div/div/div/div[2]/div/div[1]/div['
        self.rating_end =']/header/div[2]/div'

        # review
        self.review_start = '//*[@id="yDmH0d"]/div[5]/div[2]/div/div/div/div/div[2]/div/div[1]/div['
        self.review_end =']/div[1]'

        # 유용
        self.useful_start = '//*[@id="yDmH0d"]/div[5]/div[2]/div/div/div/div/div[2]/div/div[1]/div['
        self.useful_end =']/div[2]/div'

        #리뷰 개수 
        self.review_num = '//*[@id="yDmH0d"]/c-wiz[3]/div/div/div[1]/div[1]/div/div/c-wiz/div[2]/div[2]/div/div/div[1]/div[2]'

        # 모든 리뷰 버튼 
        self.all_review = '//*[@id="yDmH0d"]/c-wiz[3]/div/div/div[1]/div[2]/div/div[1]/c-wiz[4]/section/div/div/div[5]/div/div/button/span'

        self.browser = webdriver.Chrome(service = Service(ChromeDriverManager().install()))

        self.review_dict_total = {}

    def scroll(self, modal):
        try:        
            # 스크롤 높이 받아오기
            last_height = self.browser.execute_script("return arguments[0].scrollHeight", modal)
            while True:
                pause_time = random.uniform(0.5, 0.8)
                # 최하단까지 스크롤
                self.browser.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", modal)
                # 페이지 로딩 대기
                time.sleep(pause_time)
                # 무한 스크롤 동작을 위해 살짝 위로 스크롤
                self.browser.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight-50);", modal)
                time.sleep(pause_time)
                # 스크롤 높이 새롭게 받아오기
                new_height = self.browser.execute_script("return arguments[0].scrollHeight", modal)
                try:
                    # '더보기' 버튼 있을 경우 클릭
                    all_review_button = self.browser.find_element_by_xpath('/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div/main/div/div[1]/div[2]/div[2]/div/span/span').click()
                except:
                    # 스크롤 완료 경우
                    if new_height == last_height:
                        print("scrolled")
                        break
                    last_height = new_height
        except: 
            pass

    def crawl(self):
        
        self.browser.get(self.start_URL)

        try:
            self.browser.find_element(by = By.XPATH, value = '//*[@id="yDmH0d"]/c-wiz[2]/div/div/c-wiz/c-wiz[1]/c-wiz/section/div/div/a').click()
        except:
            self.browser.find_element(by = By.XPATH, value = '//*[@id="yDmH0d"]/c-wiz[2]/div/div/c-wiz/c-wiz[1]/c-wiz/section/div/div/div/div/div[1]/div[1]').click()
        # self.browser.find_element(by = By.XPATH, value = '//*[@id="yDmH0d"]/c-wiz[2]/div/div/c-wiz/c-wiz[1]/c-wiz/section/div/div/div/div/div[1]/div[1]').click()

        # 크롤링할 리뷰 개수
        review_count = WebDriverWait(self.browser, 2).until(EC.visibility_of_element_located((By.XPATH, self.review_num)))
        review_count = self.browser.find_element(by = By.XPATH, value = self.review_num).text

        ten_thousand = '만' in review_count
        thousand = '천' in review_count

        if ten_thousand:
            start = review_count.find('뷰')
            end = review_count.find('만')
            
            review_count = (float(review_count[start+2:end])+0.01) * 10000
            
        elif thousand:
            start = review_count.find('뷰')
            end = review_count.find('천')
            review_count = (float(review_count[start+2:end]) + 0.01)  * 1000

        else:
            start = review_count.find('뷰')
            end = review_count.find('개')
            review_count = review_count[start+2:end]

        review_count = int(review_count)
        print('review count :', review_count)

        WebDriverWait(self.browser, 2).until(EC.visibility_of_element_located((By.XPATH, self.all_review)))
        self.browser.find_element(by = By.XPATH, value = self.all_review).click()   

        modal = WebDriverWait(self.browser, 2).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='fysCi']")))
        self.scroll(modal)
        

        # rating만 따로 받아 옴
        # html parsing하기
        html_source = self.browser.page_source
        soup_source = BeautifulSoup(html_source, 'html.parser')
        review_source = soup_source.find_all(class_ = 'RHo1pe')

        rating_list = []
        for review in review_source:
            rating = review.find_all(class_ = "iXRFPc")[0]['aria-label'][10] # 평점 데이터 추출
            rating_list.append(rating)

        if review_count > 10000:
            review_count = 10000

        user_cnt = 0
        for count in range(review_count):

            count += 1
            try:
                review_dict = {}
                id_ = self.browser.find_element(by = By.XPATH, value = self.id_start + str(count) + self.id_end).text
                date_ = self.browser.find_element(by = By.XPATH, value = self.date_start + str(count) + self.date_end).text
                # rating_ = self.browser.find_element(by = By.XPATH, value = self.rating_start + str(count) + self.rating_end).text
                review_ = self.browser.find_element(by = By.XPATH, value = self.review_start + str(count) + self.review_end).text
            #    useful_ = browser.find_element(by = By.XPATH, value = useful_start + str(count) + useful_end).text

                if self.target_rating != None:
                    if int(rating_list[count-1]) != int(self.target_rating):
                        continue

                review_dict['id'] = id_
                review_dict['date'] = date_
                review_dict['rating'] = rating_list[count-1]
                review_dict['review'] = review_
            #    review_dict['useful'] = useful_

                user_cnt += 1
                self.review_dict_total['user_' + str(user_cnt)] = review_dict
            except:
                continue

        print('review from user1 :', self.review_dict_total['user_1']['review'])