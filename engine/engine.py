#-*- coding:utf-8 -*-

import os
import time
import requests
import random
import re
import queue

class Engine():
    def __init__(self):
        self.kakao = KakaoSpeech()
        self.youtube_video = YoutubeVideo()
        self.youtube_audio = YoutubeAudio()

        # queue
        self.q = queue.Queue()


        self.keyword_dic = {
            self.say_hi : ['안녕', '반갑', '반가', '방가', '하이', '헬로', '자비숭', '자비'],
            self.say_thank_you : ['고마워', '땡큐', '잘했어', '감사'],
            self.called_other_name : ['시리야', '빅스비', '카카오', '누구'],
            #self.say_love_you' : ['사랑해', ''],
            self.recommend_movie : ['영화추', '영화순', '재밌는영화', '볼만한영화', '재밋는영화','영화추천','영하추', '영하순',],
            self.play_video : [
                '동영상틀', '동영상들', '동영상재생', '동영상켜', '영상틀', '영상들', '영상재', '영상켜', '영상다시x',
            ],
            self.pause_video : ['영상멈', '영상중', '영상재생중', '영상정'],
            self.stop_video : ['영상꺼', '영상끄', '영상닫','영상그만꺼'],
            self.play_audio : ['틀어', '들려', '재생해', '들어'],
            self.stop_audio : ['노래꺼','음악꺼','악꺼줘', '소리꺼', '노래그만꺼','노래이제꺼','음악그만꺼','음악이제꺼'],
            self.volumn_up : [
                '소리켜', '소리키','소리크','소리높', '음량켜','음량키','음량크', '음량높', '볼륨키', '볼륨크', '볼륨켜',
                '소리더키','소리더켜','볼륨더키','볼륨더크','볼룸더켜'
            ],
            self.volumn_down : ['소리줄', '소리작','음량줄','음량작','볼륨작', '볼륨줄'],
            self.show_news : ['뉴스', '헤드라인']
        }

    def recognize_speech(self, txt_ls):
        self.txt_ls = txt_ls

        # 의도 파악하여 적절한 함수 호출
        for txt in txt_ls:
            for func, keyword_ls in self.keyword_dic.items():
                if any (word in txt for word in keyword_ls if type(word)==str):
                    return func()
        return '잘 모르겠어요'

    def say_hi(self):
        return random.choice(['안녕하세요', '반가워요'])

    def say_thank_you(self):
        return random.choice(['도움이 되어서 기뻐요', '좋은 하루 되세요'])

    def called_other_name(self):
        return '제 이름을 모르시다니, 상처 받았어요'

    def say_love_you(self):
        return random.choice(['기계도 사랑을 할 수 있을까요'])

    def recommend_movie(self):
        # 네이버 영화 랭킹 크롤링
        body = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.nhn').content
        soup = BeautifulSoup(body, 'html.parser')

        movie_ls = [movie.text.strip() for movie in soup.find_all('td', {'class' : 'title'})][:10]
        print(movie_ls)
        return ['이번 주의 영화 순위 말씀드릴게요'] + movie_ls + ['마음에 드는 영화가 있으면 좋겠어요']

    def play_video(self):
        ''' Mirror에서 구현 '''
        return

    def pause_video(self):
        ''' Mirror에서 구현'''
        return

    def stop_video(self):
        ''' Mirror에서 구현'''
        return

    # 가수 정보, 노래 제목 추출
    def play_audio(self):
        for txt in self.txt_ls:
            for keyword in self.keyword_dic[self.play_audio]:
                if keyword in txt:
                    title = re.findall('.+(?=%s)'%keyword, txt).pop().strip()
                    self.kakao.text_to_speech('노래 들려드릴게요')

                    # youtube_audio 객체 생성
                    self.youtube_audio = YoutubeAudio()
                    self.youtube_audio.play(title)
                    return

    def stop_audio(self):
        self.youtube_audio.stop()

    def volumn_up(self):
        os.system('pactl set-sink-volume 0 +15%')

    def volumn_down(self):
        os.system('pactl set-sink-volume 0 -25%')

    def ask_me(self):
        speaker = self.kakao.speech_to_text()
        answer = self.recognize_speech(speaker)
        # queue에 저장
        self.q.put(answer)

        # str은 한 문장짜리 답변
        if type(answer) == str:
            self.kakao.text_to_speech(answer)

        # 답변이 복잡할 때, list로 여러개 담음
        elif type(answer) == list:
            for text in answer:
                self.kakao.text_to_speech(text)

        # 만약 미러가 작동해야 하는 경우
        else:
            return

    def show_news(self):
        'Mirror에서 구현'
        return


#kakao STT API
import os
import subprocess
import json
import re

class KakaoSpeech(object):
    def __init__(self):
        with open('data/kakao_api.txt', 'r') as f:
            self.kakao_api = f.readline().replace('\n','')
            return

    def record_speech(self):
        os.system('arecord --format=S16_LE --duration=3 --rate=16000 --file-type=wav stt.wav')
        return

    def set_volumn(self, volume):
        os.system('amixer -c 0 set PCM %s'%volume)


    def speech_to_text(self):
        # volumn down when person speaks
        os.system('mplayer data/sound.mp3')
        self.set_volumn(150)

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


        #################################################################
        # set stt result manually
        #txt_ls = ['어벤저스 엔드게임 예고편 영상틀어줘']
        #################################################################

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
        os.system('ffplay -nodisp -autoexit tts.mp3')
        os.system('rm tts.mp3')
        return


import youtube_dl
import requests
from bs4 import BeautifulSoup
import os
import time
from subprocess import Popen
import json
import pafy
import vlc

class Youtube(object):
    def __init__(self):
        # 최초 파일 제거
        with open('data/youtube_api.txt', 'r') as f:
            self._api_key = f.readline().replace('\n','')
        return

    def get_title(self, url):
        req = requests.get(url)
        soup = BeautifulSoup(req.content.decode('utf-8'), 'html.parser')
        return soup.find('title').text

    def get_playlist(self, txt, num_video=5):
        '''
        해당 txt로 검색했을 때, 재생 가능한 동영상 목록 list를 반환
        {
            title,, id, url
        }
        '''

        playlist_ls = []

        # get url with api
        url = 'https://www.googleapis.com/youtube/v3/search?'
        params = {
            'q' : '%s'%txt,
            'part' : 'id',
            'key' : '%s'%self._api_key,
            'maxResults' : num_video,
            'type' : 'video',
        }

        for key, val in params.items():
            url += '%s=%s&'%(key,val)

        req = requests.get(url).content.decode('utf-8')

        for item in json.loads(req)['items']:
            id = item['id']['videoId']
            url = 'https://www.youtube.com/watch?v=%s'%id
            title = self.get_title(url)

            playlist_ls.append({
                'title' : title,
                'id' : id,
                'url' : url,
            })

        print('================================================================================')
        print([item for item in playlist_ls])
        print('================================================================================')
        return playlist_ls

    def get_url(self, playlist_ls, idx=0):
        print(playlist_ls)
        print(idx)
        id = playlist_ls[idx]['id']
        video_url = 'https://www.youtube.com/watch?v=%s'%id
        return video_url


class YoutubeVideo(Youtube):
    def __init__(self):
        Youtube.__init__(self)

    def get_video(self, txt):
        # 영상 파일 링크 추출
        playlist_ls = self.get_playlist(txt)
        video_url = self.get_url(playlist_ls, idx=0) # idx는 나중에 이용자가 입력하도록 수정
        video = pafy.new(video_url)
        best = video.getbest()
        play_url = best.url
        Instance = vlc.Instance()
        self.player = Instance.media_player_new()
        Media = Instance.media_new(play_url)
        Media.get_mrl()
        self.player.set_media(Media)
        return self.player

    def play(self, txt):
        self.get_video(txt)
        self.player.play()
        return

    def pause(self):
        self.player.pause()
        return

    def stop(self):
        self.player.stop()
        return

class YoutubeAudio(Youtube):
    def __init__(self):
        Youtube.__init__(self)
        os.system('rm audio.wav')

    def download(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl' : 'audio.wav',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return

    def play(self, txt):
        # Playlist 
        playlist_ls = self.get_playlist(txt)
        # 음원 파일 링크 추출
        url = self.get_url(playlist_ls)
        # 음원 파일 다운로드
        self.download(url)
        # subprocess에 mplayer 할당
        self.proc = Popen(['mplayer', 'audio.wav'])
        self.audio_pid = self.proc.pid

    def stop(self):
        print(self.audio_pid)
        os.system('kill -9 %s'%self.audio_pid)
        os.system('rm audio.wav')

import urllib3
import json
import base64
import os
import requests

class WeatherForecast(object):
    def __init__(self):
        with open('data/skt_apikey.txt', 'r') as f:
            self.appKey = f.readline().replace('\n','')
        self.appKey = 'd23883b9-07c0-4f2b-a2b8-138fce5b1bf8'

        self.city = '서울'
        self.county = '강남구'
        self.village = '삼성동'

        # 현재 날씨(시간별)
        self.url_hourly = "https://api2.sktelecom.com/weather/current/hourly"

        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'appKey': self.appKey
        }

        self.params = {
            "version": "1",
            "city": self.city,
            "county": self.county,
            "village": self.village
        }

    #현재 날씨(시간별)
    def hourly(self, weather):
        # 기온 정보
        # 오늘의 최고기온
        #temperature_tmax = weather['temperature']['tmax']
        # 1시간 현재기온
        temperature_tc = '%.01f°C'%float(weather['temperature']['tc'])
        print(temperature_tc)
        # 오늘의 최저기온
        #temperature_tmin = weather['temperature']['tmin']

        # 하늘 상태 정보
        # 하늘상태코드명
        skycode_dic = {
            'SKY_O01' : 'data/sunny.png',
            'SKY_O02' : 'data/partly_sunny.png',
            'SKY_O03' : 'data/cloud.png',
            'SKY_O04' : 'data/rain.png',
            'SKY_O05' : 'data/snow.png',
            'SKY_O06' : 'data/snow.png',
            'SKY_O07' : 'data/cloud.png',
            'SKY_O08' : 'data/rain.png',
            'SKY_O09' : 'data/snow.png',
            'SKY_O10' : 'data/rain.png',
            'SKY_O11' : 'data/storm.png',
            'SKY_O12' : 'data/storm.png',
            'SKY_O13' : 'data/storm.png',
            'SKY_O14' : 'data/storm.png',
        }
        skycode = weather['sky']['code']
        img_path = skycode_dic[skycode]

        return temperature_tc, img_path

    def requestCurrentWeather(self):
        response = requests.get(self.url_hourly, params=self.params, headers=self.headers)

        if response.status_code == 200:
            response_body = response.json()

            #날씨 정보
            try:
                weather_data = response_body['weather']['hourly'][0]
                temp, sky = self.hourly(weather_data)

                return temp, sky
            except:
                pass
        else:
            pass



'''
#Etri STT API
class SpeechToText(object):
    def __init__(self):
        self._api_key = self.read_api_key('api_key.txt')
        #os.system('mplayer sound.mp3')
        return

    def record_speech(self):
        os.system('arecor   d --format=S16_LE --duration=3 --rate=16000 --file-type=wav stt.wav')
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
        os.system('gtts-cli --lang ko --nocheck --output tts.mp3 "%s"'%text)
        os.system('mplayer tts.mp3')
        os.system('rm tts.mp3')
        return

'''
