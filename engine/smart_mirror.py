#-*- coding:utf-8 -*-

# 노래봇 - 동형   : 2019.04.10 구현 완료
# 번역 기능 - 동형
# 스마트 미러 GUI - 동형
# 점심에 뭐 먹을까? - 영훈
# 날씨 어때? - 영훈

from engine import *

import tkinter
from tkinter import Label, PhotoImage, Frame, Canvas

import queue, threading
import time

import functools

class Mirror(Engine):
    def __init__(self):
        Engine.__init__(self)
        self.time = time.time()
        self.main_thread = threading.Thread(target=self.run)
        self.main_thread.start()

    def run(self):
        # main GUI
        self.root = tkinter.Tk()
        self.root.geometry('1300x1000+100+100')
        self.root.bind("<Return>", self.ask_mirror) # return key와 stt binding

        # Background Label
        self.background_label = Background(self.root, 'data/2.gif')
        self.background_label.pack()
        self.root.after(100, self.background_label.animate)

        # Answer Label
        #self.answer_label = Answer(self.root)
        #self.answer_label.pack()

        # youtube video frame
        self.video_frame = VideoFrame(self.root)

        # mainloop
        self.root.mainloop()
        return

    def ask_mirror(self, event):
        # 2초 이내에서는 중복실행 불가
        if time.time() - self.time > 2:
            self.time = time.time()
            # multi-threading으로 명령 처리
            self.q = queue.Queue()
            self.thread = threading.Thread(target=self.ask_me, args=(self.q, ))
            self.thread.start()
            #self.root.after(100, self.answer_label.animate, None)
        return

    # play youtube video1
    def play_video(self):
        # 현재 재생중인 영상이 없으면 새로운 영상 재생
        if self.video_frame.on_air == False:
            for txt in self.txt_ls:
                for keyword in self.keyword_dic[self.play_video]:
                    if keyword in txt:
                        title = re.findall('.+(?=%s)'%keyword, txt).pop().strip()
                        self.kakao.text_to_speech('영상 틀어드릴게요')

                        self.background_label.pack_forget()         # background 화면 중지
                        player = self.youtube_video.get_video(title) # YoutubeVideo에서 video player 가져옴
                        self.video_frame.pack(player)       # VideoFrame packing
        # 재생 중이던 영상이 있으면 이어서 재생en
        elif self.video_frame.on_air == True:
            self.video_frame.player.play()

    # pause youtube video
    def pause_video(self):
        self.video_frame.player.pause() # 영상 정지
        return

    def stop_video(self):
        self.video_frame.pack_forget()   # 영상 정지 및 영상을 mirror 화면에서 제거
        self.background_label.pack()     # background를 다시 packing
        return


# 기본 배경화면을 재생하는 Background
class Background(Label):
    def __init__(self, root, path_to_file, delay=0.001):
        Label.__init__(self, root)
        self.config(bg='black', width=1300, height=1000)
        self.root = root
        self.path_to_file = path_to_file
        self.delay = delay
        self.idx = 0

    def animate(self):
        try:
            self.gif = PhotoImage(file=self.path_to_file, format='gif -index %i'%(self.idx))  # Looping through the frames
            self.gif = self.gif.zoom(2)
            self.configure(image=self.gif)
            self.idx += 1
        except tkinter.TclError:  # When we try a frame that doesn't exist, we know we have to start over from zero
            self.idx = 0
        if True:
            self.root.after(int(self.delay*1000), self.animate)

# 숭비스의 대답을 출력하는 Label
class Answer(Label):
    def __init__(self, root):
        Label.__init__(self, root)
        self.config(bg='white', width=200, height=150, font=('NanumGothic', 30))
        self.root = root

    def animate(self, answer):
        try :
            self.config(text=answer)
        except:
            pass
        if not answer:
            self.root.after(100, self.animate, answer)

import platform

# Youtube Video를 재생하는 Frame
class VideoFrame(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.root = root
        self.video_panel = Frame(self.root)
        self.canvas = Canvas(self.video_panel).pack(fill='both', expand=1)
        self.on_air = False

    def pack(self, player):
        self.on_air = True
        self.player = player

        # set the window id where to render VLC's video output
        if platform.system() == 'Windows':
            self.player.set_hwnd(self.get_handle())
        else:
            self.player.set_xwindow(self.get_handle()) # this line messes up windows
        self.player.play()
        self.video_panel.pack(fill='both', expand=1)
        return

    def pack_forget(self):
        self.on_air=False    # 현재 state를 False로 전환
        self.player.stop()
        self.video_panel.pack_forget()
        return

    def get_handle(self):
        return self.video_panel.winfo_id()
