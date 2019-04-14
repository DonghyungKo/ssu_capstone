import os
import time
import requests
import random
import re

class Engine(object):
    def __init__(self):
        # 클래스 호출
        self.kakao = KakaoSpeech()
        self.youtube = Youtube()

        self.keyword_dic = {
            self.exit : ['쉬어'],
            self.say_hi : ['안녕', '반갑', '반가', '방가', '하이', '헬로'],
            self.say_thank_you : ['고마워', '땡큐', '잘했어', '감사'],
            #self.say_love_you' : ['사랑해', ''],
            self.ask_hungry : ['밥먹었', '밥먹엇'],
            self.recommend_movie : ['영화추', '영화순', '재밌는영화', '볼만한영화', '재밋는영화','영화추천','영하추', '영화알'],
            self.play_music : ['틀어', '들려', '재생해', '들어'],
            self.stop_music : ['노래꺼','음악꺼','악꺼줘', '소리꺼'],
            self.volumn_up : [
                '소리켜', '소리키','소리크','소리높', '음량켜','음량키','음량크', '음량높', '볼륨키', '볼륨크', '볼륨켜',
                '소리더키','소리더켜','볼륨더키','볼륨더크','볼룸더켜'
            ],
            self.volumn_down : ['소리줄', '소리작','음량줄','음량작','볼륨작', '볼륨줄'],
        }



    def recognize_speech(self, txt_ls):
        self.txt_ls = txt_ls

        # 의도 파악하여 적절한 함수 호출
        for txt in txt_ls:
            for func, keyword_ls in self.keyword_dic.items():
                if any (word in txt for word in keyword_ls if type(word)==str):
                    return func()
        return '잘 모르겠어요'

    def exit(self):
        return 'stop'

    def say_hi(self):
        return random.choice(['안녕하세요', '반가워요'])

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

        # 가수 정보, 노래 제목 추출
    def play_music(self):
        for keyword in self.keyword_dic[self.play_music]:
            for txt in self.txt_ls:
                if keyword in txt:
                    title = re.findall('.+(?=%s)'%keyword, txt).pop().strip()
                    self.kakao.text_to_speech('노래 들려드릴게요')

                    # youtube_audio 객체 생성
                    self.youtube = Youtube()
                    self.youtube.play_audio(title)
                    return

    def stop_music(self):
        os.system('pkill -9 mplayer')
        return

    def volumn_up(self):
        os.system('pactl set-sink-volume 0 +10%')

    def volumn_down(self):
        os.system('pactl set-sink-volume 0 -20%')

    def ask_me(self):
        error_cnt = 0

        while True:
            speaker = self.kakao.speech_to_text()
            answer = self.recognize_speech(speaker)

            # 음성 재생은 none을 반환
            if answer == '잘 모르겠어요':
                if error_cnt < 2:
                    txt = '다시 한번 말씀해주시겠어요?'
                    self.kakao.text_to_speech(txt)
                    error_cnt += 1
                    continue

                else:
                    txt = '죄송해요 제가 더 공부할게요'
                    self.kakao.text_to_speech(txt)
                    break

            elif answer == 'stop':
                txt = '네 좋은 하루 되세요'
                self.kakao.text_to_speech(txt)
                return

            # str은 한 문장짜리 답변
            if type(answer) == str:
                self.kakao.text_to_speech(answer)
                return answer

            # 답변이 복잡할 때, list로 여러개 담음
            elif type(answer) == list:
                for text in answer:
                    self.kakao.text_to_speech(text)
                return ' '.join(answer)

        return

#kakao STT API
import os
import subprocess
import json
import re

class KakaoSpeech(object):
    def __init__(self):
        with open('kakao_api.txt', 'r') as f:
            self.kakao_api = f.readline().replace('\n','')
            return

    def record_speech(self):
        os.system('arecord --format=S16_LE --duration=3 --rate=16000 --file-type=wav stt.wav')
        return

    def set_volumn(self, volume):
        os.system('amixer -c 0 set PCM %s'%volume)


    def speech_to_text(self):
        # volumn down when person speaks
        os.system('mplayer sound.mp3')
        self.set_volumn(200)

        # record speech
        self.record_speech()

        # speech to text
        sh = ' '.join([
            'curl -v -X POST "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"',
            '-H "Transfer-Encoding: chunked"' ,
            '-H "Content-Type: application/octet-stream"',
            '-H "X-DSS-Service: DICTATION"',
            '-H "Authorization:KakaoAK %s"'%self.kakao_api,
            '--data-binary @stt.wav',
        ])

        proc = subprocess.Popen(sh, stdout=subprocess.PIPE, shell=True)
        result = proc.stdout.read().decode('utf-8')

        # 녹음한 파일 삭제
        os.system('rm stt.wav')

        # volumn back to normal state
        self.set_volumn(255)

        txt_ls = re.findall('(?<=value":")(.+)(?=")', result)
        txt_ls.append(txt_ls.pop().split(',')[0].replace('"',''))
        txt_ls = [txt.replace(' ','') for txt in txt_ls]
        txt_ls.reverse()
        return txt_ls

    def text_to_speech(self, txt):
        sh = [
            'curl -v -X POST "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize"',
            '-H "Content-Type: application/xml"',
            '-H "Authorization: %s"'%self.kakao_api,
            "-d '<speak>",
        ]

        if type(txt) == str:
            sh.append('<voice> %s </voice>'%txt)

        elif type(txt) == list:
            for t in txt:
                sh.append('<voice> %s </voice>'%t)

        sh.append("</speak>' > tts.mp3")
        sh = ' '.join(sh)

        # tts 요청
        os.system(sh)
        os.system('mplayer tts.mp3')
        os.system('rm tts.mp3')

    def translate(self, to='en'):
        txt = '안녕하세요를 영어로 번역해줘'


import youtube_dl

import requests
from bs4 import BeautifulSoup
import os
import time

from subprocess import Popen
import json

class Youtube(object):
    def __init__(self):
        # 최초 파일 제거
        os.system('rm music.wav')
        with open('youtube_api.txt', 'r') as f:
            self._api_key = f.readline().replace('\n','')
        return


    def get_url(self, txt):
        # get url with api
        url = 'https://www.googleapis.com/youtube/v3/search?'
        params = {
            'q' : '%s'%txt,
            'part' : 'id',
            'key' : '%s'%self._api_key,
            'maxResults' : 1,
            'type' : 'video',
        }

        for key, val in params.items():
            url += '%s=%s&'%(key,val)

        req = requests.get(url)
        id = json.loads(req.content.decode('utf-8'))['items'].pop()['id']['videoId']
        print('https://www.youtube.com/watch?v=%s'%id)
        return 'https://www.youtube.com/watch?v=%s'%id


    def download_audio(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl' : 'music.wav',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return


    def play_audio(self, txt):
        # 음원 파일 링크 추출
        url = self.get_url(txt)

        # 음원 파일 다운로드
        self.download_audio(url)

        # subprocess에 mplayer 할당
        self.proc = Popen(['mplayer', 'music.wav'])
        self.music_pid = self.proc.pid


    def stop_audio(self):
        print(self.music_pid)
        os.system('kill -9 %s'%self.music_pid)
        os.system('rm music.wav')


import urllib3
import json
import base64
import os

'''
#Etri STT API
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

'''



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
