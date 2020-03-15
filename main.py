import requests
import argparse
import configparser
import json
from naver_crawler import get_hot_keywords
from time import sleep
import logging


def write_post(access_token, blog_name, title, content, category, tag):
    url = 'https://www.tistory.com/apis/post/write'
    data = {
        'access_token':access_token,
        'blogName': blog_name,
        'title': title,
        'content': content,
        'category': category,
        'visibility': 3,
        'tag': tag, # separated by ','
        'output':'json'
    }
    res = requests.post(url, data=data)

    if res.status_code != 200:
        logging.getLogger('logger').exception('Server response error')
        return

    if res.json()['tistory']['status'] != '200':
        logging.getLogger('logger').exception('Posting error : {0}'.format(res.json()))

    logging.getLogger('logger').info('Success to posting : {0}'.format(res.json()['tistory']['url']))




def get_categories(access_token, blog_name):
    url = 'https://www.tistory.com/apis/category/list'

    res = requests.get(url, params={'access_token':access_token, 'blogName':blog_name, 'output': 'json'})

    categories = dict()
    for category in res.json()['tistory']['item']['categories']:
        categories.update( {category['name'] : category['id'] })

    return categories


def get_auth_token(client_id, response_uri):
    url = 'https://www.tistory.com/oauth/authorize'

    params = {'client_id':client_id, 'response_type':'code', 'response_uri':response_uri}
    res = requests.get(url, params=params)

    return res.url # return code param value but I didn't update it


def get_access_token(client_id, client_secret, response_uri):
    url = 'https://www.tistory.com/oauth/access_token'
    code = get_auth_token(client_id, response_uri)

    params = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri' : '127.0.0.1/oauth',
        'grant_type': 'authorization_code'

    }
    res = requests.get(url, params=params)

    print(res.json()) # save to tistory.ini


# NEED TO UPDATE OAuth2 LOGIC BUT I AM LAZY 1) get auth token (at this time have to login in web, selenium can be used for automation -> get access token)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--target', dest='targets', type=str, default='', nargs='+', required=True)
    parser.add_argument('--time-interval', dest='time_interval', type=int, default=600)

    args = parser.parse_args()
    targets = args.targets
    time_interval = args.time_interval

    logger = logging.getLogger('logger')
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[ %(levelname)s | %(filename)s: %(lineno)s] %(asctime)s > %(message)s')
        file_handler = logging.FileHandler('log.log')
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)


    config = configparser.ConfigParser()
    config.read('tistory.ini')

    client_id = config['tistory']['client_id']
    client_secret = config['tistory']['secret_key']
    access_token = config['tistory']['access_token']
    blog_name = config['tistory']['blog_name']


    categories =  get_categories(access_token,blog_name)

    while True:
        for target in targets:
            if target == 'hot':
                naver_hot_keywords = get_hot_keywords()
                write_post(access_token, blog_name, naver_hot_keywords[0], naver_hot_keywords[1], categories['실시간 검색어'], naver_hot_keywords[2])

        logger.info('Wating for {0}...'.format(time_interval))
        sleep(time_interval)

