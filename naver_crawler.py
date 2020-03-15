from selenium import webdriver
from datetime import datetime

def get_hot_keywords():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    with webdriver.Chrome('./chromedriver', options=options) as driver:
        driver.implicitly_wait(60)
        driver.get('https://www.naver.com')

        content = str()
        tags = list()
        before = 0
        for keyword in driver.find_element_by_class_name('ah_l').find_elements_by_class_name('ah_item'):
            keyword.location_once_scrolled_into_view # wow such a good fuction!!!!!!!!!!!!!! that's coool!!! love it!

            if before > int(keyword.find_element_by_class_name('ah_r').text):
                break

            content +=('{0}위  : {1} <br><br>'.format(keyword.find_element_by_class_name('ah_r').text, keyword.find_element_by_class_name('ah_k').text))
            tags.append(keyword.find_element_by_class_name('ah_k').text)

            before = int(keyword.find_element_by_class_name('ah_r').text)

        title = '{0} 네이버 실시간 검색어 순위'.format(datetime.fromtimestamp(int(datetime.now().timestamp())))
        content = content

        return [title, content,','.join(tags)]