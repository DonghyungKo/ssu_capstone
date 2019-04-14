import subprocess
import json
import re


with open('kakao_api.txt', 'r') as f:
    kakao_api = f.readline().replace('\n','')

import requests

url = 'https://kapi.kakao.com/v1/translation/translate'
headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Authorization' : 'Kakao AK %s'%kakao_api,
}

params = {
    'query' : '안녕하세요',#.encode('utf-8'),
    'src_lang' : 'kr',
    'target_lang' : 'en',
}

req = requests.post(url=url, headers=headers, data=params)
print(req)
