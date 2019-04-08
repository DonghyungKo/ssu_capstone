#-*- coding:utf-8 -*-
import os
import time
import random
import requests
from bs4 import BeautifulSoup


# 1. 나 우울해 : 명언 골라주기
# 2. 점심에 뭐 먹을까?
# 3.


class SoongSiri(object):
    def __init__(self):
        self.keyword_dic = {
            'say_hi' : ['안녕', '반갑', '반가', '방가', '하이', '헬로'],
            'say_thank_you' : ['고마워', '땡큐', '잘했어', '감사'],
            'say_love_you' : ['사랑해' ,'사랑'],
            'ask_hungry' : ['밥먹었', '밥먹엇'],
            'recommend_movie' : ['영화추', '재밌는영화', '볼만한영화', '재밋는영화','영화추천','영하추', '영화알'],
            'say_something_funny' : ['웃긴이야기', '웃긴얘기', '재밌는얘기', '재밌는이야기'],
            'ask_how_do_I_look' : ['나예','나잘생','나멋', '나좀예', '나좀잘', '나좀멋']

        }

        self.function_dic = {
            'say_hi' : self.say_hi,
            'say_thank_you' : self.say_thank_you,
            'say_love_you' : self.say_love_you,
            'ask_hungry' : self.ask_hungry,
            'recommend_movie' : self.recommend_movie,
            'say_something_funny' : self.say_something_funny,
            'ask_how_do_I_look' : self.ask_how_do_I_look,
        }
        return


    def recognize_speech(self, txt):
        # 의도 파악하여 적절한 함수 호출
        for intend, keyword_ls in self.keyword_dic.items():
            if any (word in txt for word in keyword_ls):
                return self.function_dic[intend]()

        return '잘 모르겠어요'


    def say_hi(self):
        return random.choice(['안녕하세요', '반갑습니다', '반가워요'])

    def say_thank_you(self):
        return random.choice(['도움이 되어서 기뻐요', '좋은 하루 되세요'])

    def say_love_you(self):
        return random.choice(['기계도 사랑을 할 수 있을까요'])

    def ask_hungry(self):
        return random.choice(['저는 전기만 먹고 살아요'])

    def recommend_movie(self):
        # 네이버 영화 랭킹 크롤링
        body = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.nhn').content
        soup = BeautifulSoup(body, 'html.parser')

        movie_ls = [movie.text.strip() for movie in soup.find_all('td', {'class' : 'title'})][:10]
        return ['이번 주의 영화 일위부터 십위까지 말씀드릴게요'] + movie_ls + ['마음에 드는 영화가 있으면 좋겠어요']

    def say_something_funny(self):
        #os.system('mplayer sounds/what_dog_sound.mp4')
        return ['거울을 보시면 어떨까요', '하하']

    def ask_how_do_I_look(self):
        return random.choice(['일일구를 불러드릴까요?'])






import urllib3
import json
import base64
import os

class SpeechToText(object):
    def __init__(self):
        self._api_key = self.read_api_key('api_key.txt')
        #os.system('mplayer sound.mp3')
        return

    def record_speech(self):
        os.system('arecord --format=S16_LE --duration=3 --rate=16000 --file-type=wav stt.wav')
        return

    def read_api_key(self, path_to_file):
        with open(path_to_file, 'r') as f:
            return f.readline().replace('\n','')

    def speech_to_text(self):
        # record speech
        self.record_speech()

        openApiURL = "http://aiopen.etri.re.kr:8000/WiseASR/Recognition"
        accessKey = self._api_key
        audioFilePath = 'stt.wav'
        languageCode = 'korean'

        with open(audioFilePath, "rb") as f:
            audioContents = base64.b64encode(f.read()).decode("utf8")

        requestJson = {
            "access_key": accessKey,
            "argument": {
                "language_code": languageCode,
                "audio": audioContents
            }
        }

        http = urllib3.PoolManager()
        response = http.request(
            "POST",
            openApiURL,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=json.dumps(requestJson)
        )

        #print("[responseCode] " + str(response.status))
        #print("[responBody]")
        txt = json.loads(response.data.decode('utf-8'))['return_object']['recognized'].replace(' ','')
        return txt





from gtts import gTTS
import os

class TextToSpeech(object):
    def __init__(self):

        return

    def text_to_speech(self, text):
        tts = gTTS(text=text, lang='ko')
        tts.save("speech.mp3")
        os.system('mplayer speech.mp3')
        return
