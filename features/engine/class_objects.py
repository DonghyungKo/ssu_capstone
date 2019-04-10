#-*- coding:utf-8 -*-
import os
import time
import random
import requests
from bs4 import BeautifulSoup

import sys, re
sys.path.append('../youtube/')
from youtube_audio import *

# 노래봇 - 동형   : 2019.04.10 구현 완료
# 번역 기능 - 동형
# 점심에 뭐 먹을까? - 영훈
# 날씨 어때? - 영훈
#


class SoongSiri(object):
    def __init__(self):

        self.keyword_dic = {
            self.say_hi : ['안녕', '반갑', '반가', '방가', '하이', '헬로'],
            self.say_thank_you : ['고마워', '땡큐', '잘했어', '감사'],
            #self.say_love_you' : ['사랑해'],
            self.ask_hungry : ['밥먹었', '밥먹엇'],
            self.recommend_movie : ['영화추', '재밌는영화', '볼만한영화', '재밋는영화','영화추천','영하추', '영화알'],
            self.say_something_funny : ['웃긴이야기', '웃긴얘기', '재밌는얘기', '재밌는이야기'],
            self.ask_how_do_I_look : ['나예','나잘생','나멋', '나좀예', '나좀잘', '나좀멋'],
            self.play_music : ['틀어', '들려', '재생해', '들어']
        }



    def recognize_speech(self, txt):
        self.txt = txt

        # 의도 파악하여 적절한 함수 호출
        for func, keyword_ls in self.keyword_dic.items():
            if any (word in txt for word in keyword_ls if type(word)==str):
                return func()

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
        print(movie_ls)
        return ['이번 주의 영화 일위부터 십위까지 말씀드릴게요'] + movie_ls + ['마음에 드는 영화가 있으면 좋겠어요']

    def say_something_funny(self):
        #os.system('mplayer sounds/what_dog_sound.mp4')
        return ['거울을 보시면 어떨까요', '하하']

    def ask_how_do_I_look(self):
        return random.choice(['일일구를 불러드릴까요?'])

    def play_music(self):
        # 가수 정보, 노래 제목 추출
        for keyword in self.keyword_dic[self.play_music]:
            if keyword in self.txt:
                title = re.findall('.+(?=%s)'%keyword, self.txt).pop().strip()
                break

        # youtube_audio 객체 생성
        self.youtube_audio = YoutubeAudio()
        self.youtube_audio.play_audio(title)
        return


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
        os.system('rm stt.wav')
        return txt





from gtts import gTTS
import os

class TextToSpeech(object):
    def __init__(self):
        return

    def text_to_speech(self, text):
        '''
        tts = gTTS(text=text, lang='ko')
        tts.save("speech.mp3")
        os.system('mplayer speech.mp3')
        '''
        os.system('gtts-cli --lang ko --nocheck --output tts.mp3 "%s"'%text)
        os.system('mplayer tts.mp3')
        os.system('rm tts.mp3')
        return
