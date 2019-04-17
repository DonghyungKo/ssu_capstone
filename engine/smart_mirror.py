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

import tkinter.font

class Mirror(Engine):
    def __init__(self):
        Engine.__init__(self)
        self.time = time.time()
        self.main_thread = threading.Thread(target=self.run)
        self.main_thread.start()

    def run(self):
        # main GUI
        self.root = tkinter.Tk()
        self.root.geometry('1200x1000')
        self.root.bind("<Return>", self.ask_mirror) # return key와 stt binding

        # top Frame
        self.top_frame = Frame(self.root, bg='black', width=1200, height=150)
        self.top_frame.pack(side='top', fill='both')
        # bottom Frame
        self.bottom_frame = Frame(self.root, bg='black', width=1200, height=200)
        self.bottom_frame.pack(side='bottom')
        # middle Frame
        self.middle_frame = Frame(self.root, bg='red', width=1200, height=650)
        self.middle_frame.pack(fill='both')

        # Background GIF -> middle frame
        self.background_gif = BackgroundGIF(self.middle_frame, 'data/2.gif')
        self.background_gif.place(x=600, y=300, anchor='center')
        self.root.after(100, self.background_gif.animate)

        # Clock -> top_frame
        self.clock_frame = Clock(self.top_frame)
        self.clock_frame.pack(side='top', anchor='e', padx=30, pady=30)

        # Answer -> bottom frame
        self.answer_label = Answer(self.bottom_frame)
        self.answer_label.place(x=500, y=0)
        self.root.after(100, self.show_answer)
        self.root.after(100, self.answer_label.animate)

        # youtube video frame
        self.video_frame = VideoFrame(self.root)

        # mainloop
        self.root.mainloop()
        return

    def ask_mirror(self, event):
        # 2초 이내에서는 중복실행 불가
        if time.time() - self.time > 3:
            self.time = time.time()
            # multi-threading으로 명령 처리
            self.thread = threading.Thread(target=self.ask_me)
            self.thread.start()
        return

    def show_answer(self):
        if self.q.qsize() > 0:
            self.answer_label.txt = self.q.get()
        if True:
            self.root.after(100, self.show_answer)

    def show_background(self):
        self.top_frame.pack(side='top', fill='both')
        self.bottom_frame.pack(side='bottom', fill='both')
        self.middle_frame.pack(fill='both')

    def hide_background(self):
        self.top_frame.pack_forget()
        self.middle_frame.pack_forget()
        self.bottom_frame.pack_forget()

    # play youtube video1
    def play_video(self):
        # 현재 재생중인 영상이 없으면 새로운 영상 재생
        if self.video_frame.on_air == False:
                for keyword in self.keyword_dic[self.play_video]:
                    for txt in self.txt_ls:
                        if keyword in txt:
                            title = re.findall('.+(?=%s)'%keyword, txt).pop().strip()
                            self.kakao.text_to_speech('영상 틀어드릴게요')

                            player = self.youtube_video.get_video(title) # YoutubeVideo에서 video player 가져옴
                            self.video_frame.pack(player)       # VideoFrame packing
                            self.hide_background()

        # 재생 중이던 영상이 있으면 이어서 재생
        elif self.video_frame.on_air == True:
            self.video_frame.player.play()

    # pause youtube video
    def pause_video(self):
        self.video_frame.player.pause() # 영상 정지
        return

    def stop_video(self):
        self.video_frame.pack_forget()   # 영상 정지 및 영상을 mirror 화면에서 제거
        self.show_background()           # background를 다시 packing
        return


# 기본 배경화면을 재생하는 Background
class BackgroundGIF(Label):
    def __init__(self, frame, path_to_file, delay=1):
        Label.__init__(self, frame, bg='black', width=1200, height=600)
        self.frame = frame
        self.path_to_file = path_to_file
        self.delay = delay
        self.idx = 0

        # 배경 이미지

    def animate(self):
        try:
            self.gif = PhotoImage(file=self.path_to_file, format='gif -index %i'%(self.idx))  # Looping through the frames
            self.gif = self.gif.zoom(1)
            self.configure(image=self.gif)
            self.idx += 1
        except tkinter.TclError:  # When we try a frame that doesn't exist, we know we have to start over from zero
            self.idx = 0
        if True:
            self.frame.after(self.delay, self.animate)


class Clock(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg='black')
        self.parent = parent
        self.small_font=tkinter.font.Font(family="맑은 고딕", size=30)
        self.large_font=tkinter.font.Font(family="맑은 고딕", size=48)

        # date
        self.date_label = Label(self, bg='black', fg='white', font=self.small_font)
        self.date_label.pack(side='top', anchor='e')

        # day
        self.day_label = Label(self, bg='black', fg='white', font=self.small_font)
        self.day_label.pack(side='top', anchor='e')

        # time
        self.time_label = Label(self, bg='black', fg='white', font=self.large_font)
        self.time_label.pack(side='top', anchor='e')
        self.animate()

    def animate(self):
        if True:
            cur_time = time.strftime('%H:%M')
            self.time_label.config(text=cur_time)

            day = time.strftime('%A')
            self.day_label.config(text=day)

            date = time.strftime('%b %d, %Y')
            self.date_label.config(text=date)

            self.parent.after(1000, self.animate)


# 숭비스의 대답을 출력하는 Label
class Answer(Label):
    def __init__(self, frame):
        Label.__init__(self, frame)
        self.frame = frame
        self.txt = ''
        self.config(text=self.txt, bg='black', fg='white', font='Times 30')
        self.pack(side='top', anchor='center', fill='both')
        return

    def animate(self):
        self.config(text=self.txt)
        if True:
            self.frame.after(100, self.animate)


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
