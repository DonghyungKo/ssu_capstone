#-*- coding:utf-8 -*-

# 노래봇 - 동형   : 2019.04.10 구현 완료
# 번역 기능 - 동형
# GUI - 동형
# 점심에 뭐 먹을까? - 영훈
# 날씨 어때? - 영훈

from engine import *

import tkinter
from tkinter import Label, PhotoImage

import queue, threading

class SmartMirror(object):

    def __init__(self):
        self.engine = Engine()

        # GUI는 main-thread로 재생
        self.main_thread = threading.Thread(target=self.run)
        self.main_thread.start()

        #self.full_screen = False
        #self.tk.bind("<Escape>", self.end_fullscreen)

    def run(self):
        self.tk = tkinter.Tk()
        self.tk.geometry('1024x768+100+100')
        img = tkinter.PhotoImage(file='on.png')
        #img = img.zoom(2)
        self.background = Label(self.tk, image=img, width=512, height=512)
        self.background.place(relx=.5, rely=.5, anchor='center')

        self.tk.bind("<Return>", self.ask_siri) # return key와 stt binding
        self.tk.mainloop()
        return

    def ask_siri(self, event):
        # multi-threading으로 명령 처리
        thread = threading.Thread(target=self.engine.ask_me)
        thread.start()
        return


    def toggle_fullscreen(self, event=None):
        self.full_screen = not self.full_screen  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.full_screen)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"
