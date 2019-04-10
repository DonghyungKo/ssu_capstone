from __future__ import unicode_literals
import youtube_dl

import requests
from bs4 import BeautifulSoup
import os
import time

from subprocess import Popen

class YoutubeAudio(object):
    def __init__(self):
        # 최초 파일 제거
        os.system('rm music.wav')
        return

    def get_url(self, txt):
        search_url = 'https://www.youtube.com/results?search_query=%s'%txt
        body = requests.get(search_url).content
        soup = BeautifulSoup(body, 'html.parser')

        return 'https://www.youtube.com' + soup.find('a',{'class':'yt-uix-tile-link'}).get('href')

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

if __name__=='__main__':
    youtube_audio = YoutubeAudio()
    youtube_audio.play_audio('장범준 노래방에서')

    time.sleep(5)
    youtube_audio.stop_audio()
