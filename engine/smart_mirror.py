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
        self.root.geometry('1000x750+100+100')
        self.root.bind("<Return>", self.ask_mirror) # return key와 stt binding

        # Background Label
        self.background_label = Background(self.root, 'data/2.gif')
        self.background_label.pack()
        self.root.after(100, self.background_label.animate)

        # Answer Label
        self.answer_label = Answer(self.root)
        self.answer_label.pack()

        # video frame
        self.video_frame = VideoFrame(self.root)
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
        for txt in self.txt_ls:
            for keyword in self.keyword_dic[self.play_video]:
                if keyword in txt:
                    title = re.findall('.+(?=%s)'%keyword, txt).pop().strip()
                    self.kakao.text_to_speech('영상 틀어드릴게요')

                    self.background_label.pack_forget()         # background 화면 중지
                    player = self.youtube_video.get_video(title) # video player 가져옴
                    self.video_frame.pack(player)  # VideoFrame packing
                    return

    # pause youtube video
    def pause_video(self):
        self.youtube_video.pause_video() # 영상 정지
        return

    def stop_video(self):
        self.youtube_video.stop_video()  # 영상 정지
        self.video_frame.pack_forget()   # 영상을 mirror 화면에서 제거
        self.background_label.pack()     # background 다시 재생
        return



class Background(Label):
    def __init__(self, root, path_to_file, delay=0.001):
        Label.__init__(self, root)
        self.config(bg='black', width=1000, height=750)
        self.root = root
        self.path_to_file = path_to_file
        self.delay = delay
        self.idx = 0

    def animate(self):
        try:
            self.gif = PhotoImage(file=self.path_to_file, format='gif -index %i'%(self.idx))  # Looping through the frames
            self.configure(image=self.gif)
            self.idx += 1
        except tkinter.TclError:  # When we try a frame that doesn't exist, we know we have to start over from zero
            self.idx = 0
        if True:
            self.root.after(int(self.delay*1000), self.animate)


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

class VideoFrame(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.root = root
        self.video_panel = Frame(self.root)
        self.canvas = Canvas(self.video_panel).pack(fill='both', expand=1)

    def pack(self, player):
        self.player = player

        # set the window id where to render VLC's video output
        if platform.system() == 'Windows':
            self.player.set_hwnd(self.get_handle())
        else:
            self.player.set_xwindow(self.get_handle()) # this line messes up windows

        #self.player.video_set_deinterlace(str_to_bytes('yadif'))
        self.player.play()
        self.video_panel.pack(fill='both', expand=1)
        return

    def pack_forget(self):
        self.video_panel.pack_forget()
        return

    def get_handle(self):
        return self.video_panel.winfo_id()

class ThreadedTasl(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.engine= Engine()
        self.engine.q = q

    def run(self):
        self.engine.ask_me()
        return

    '''
    def toggle_fullscreen(self, event=None):
        self.full_screen = not self.full_screen  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.full_screen)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"
    '''
