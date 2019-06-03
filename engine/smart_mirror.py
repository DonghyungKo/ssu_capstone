#-*- coding:utf-8 -*-

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
        self.root.geometry('1600x1000')
        self.root.bind("<Return>", self.ask_mirror) # return key와 stt binding

        # top Frame
        self.top_frame = Frame(self.root, bg='black', width=1600, height=150)
        self.top_frame.pack(side='top', fill='both')
        # middle Frame
        self.middle_frame = Frame(self.root, bg='black', width=1600, height=500)
        self.middle_frame.pack(fill='x')
        # bottom Frame
        self.bottom_frame = Frame(self.root, bg='black', width=1600, height=350)
        self.bottom_frame.pack(side='bottom', fill='both', expand='True')

        # Background GIF -> middle frame
        self.background_gif = BackgroundGIF(self.middle_frame, 'data/2.gif')
        self.background_gif.place(x=850, y=200, anchor='center')
        self.root.after(100, self.background_gif.animate)

        # Clock -> top_frame
        self.clock_frame = Clock(self.top_frame)
        self.clock_frame.pack(side='top', anchor='e', padx=30, pady=30)

        # Weather
        self.weather_frame = Weather(self.top_frame)
        self.weather_frame.place(x=30, y=30)

        # Headline -> top_frame
        self.headline_frame = HeadLine(self.bottom_frame)
        #self.headline_frame.place(x=1700, y=10, anchor='e') # 헤드라인은 요청할 때만 띄움

        # Answer -> bottom frame
        #self.answer_label = Answer(self.bottom_frame)
        #self.answer_label.pack(fill='both')
        #self.root.after(100, self.show_answer)

        # youtube video frame
        self.video_frame = VideoFrame(self.root)

        # Icon
        self.youtube_icon = Icon(self.bottom_frame)
        self.youtube_icon.pack(side='bottom', anchor='w', padx=30, pady=10)


        # mainloop
        self.root.mainloop()
        return

    def ask_mirror(self, event):
        # 3초 이내에서는 중복실행 불가
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
        # top - middle - bottom 순으로 packing
        self.top_frame.pack(side='top', fill='both')
        self.middle_frame.pack(fill='both')
        self.bottom_frame.pack(side='bottom', fill='both', expand='True')

    def hide_background(self):
        self.top_frame.pack_forget()
        self.middle_frame.pack_forget()
        self.bottom_frame.pack_forget()

    # play youtube video1
    def play_video(self):
        # 재생 중이던 영상이 있으면 이어서 재생
        if self.video_frame.on_air == True:
            self.video_frame.player.play()
            return

        # 현재 재생중인 영상이 없으면 새로운 영상 재생
        elif self.video_frame.on_air == False:
            for keyword in self.keyword_dic[self.play_video]:
                for txt in self.txt_ls:
                    if keyword in txt:
                        self.kakao.text_to_speech('영상 틀어드릴게요')

                        title = re.findall('.+(?=%s)'%keyword, txt).pop().strip()

                        player = self.youtube_video.get_video(title) # YoutubeVideo에서 video player 가져옴
                        self.video_frame.pack(player)       # VideoFrame packing
                        self.hide_background()

    # pause youtube video
    def pause_video(self):
        self.video_frame.player.pause() # 영상 정지
        return

    def stop_video(self):
        self.video_frame.on_air = False
        self.video_frame.pack_forget()   # 영상 정지 및 영상을 mirror 화면에서 제거
        self.show_background()           # background를 다시 packing
        return

    def show_news(self):
        self.kakao.text_to_speech('오늘의 주요 언론 헤드라인 보여드릴게요')
        self.headline_frame.place(x=1700, y=140, anchor='e') # 헤드라인은 요청할 때만 띄움
        return

    def hide_news(self):
        '''추후 구현'''
        return


# 기본 배경화면을 재생하는 Background
class BackgroundGIF(Label):
    def __init__(self, frame, path_to_file, delay=1):
        Label.__init__(self, frame, bg='black')
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
        Frame.__init__(self, parent, bg='black', width=500, height=300)
        self.parent = parent
        self.small_font=tkinter.font.Font(family="helvetica", size=40)
        self.large_font=tkinter.font.Font(family="helvetica", size=60)

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

class HeadLine(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg='black', width=1600, height=800)
        self.parent = parent
        self.news_url = 'https://news.naver.com/'
        self.small_font=tkinter.font.Font(size=40, font=('Times', 18))

        # headlines
        self.headline_ls = self.get_headline()

        # labels
        self.label_ls = [Label(self, bg='black', fg='white', font=self.small_font) for _ in range(5)]
        for label in self.label_ls:
            label.pack(side='top', anchor='w', padx=0, pady=5)
        self.animate()

    def get_headline(self):
        req = requests.get(self.news_url)
        soup = BeautifulSoup(req.content, 'html.parser')
        headline_ls = [i.text.strip().split('\n')[0] for i in soup.select('#today_main_news > div.hdline_news > ul > li')]
        headline_ls = [head for head in headline_ls if head]
        return headline_ls

    def animate(self):
        if True:
            for label, headline in zip(self.label_ls, self.headline_ls):
                label.config(text = headline)

            self.parent.after(10000, self.animate)


# 숭비스의 대답을 출력하는 Label
class Answer(Label):
    def __init__(self, frame):
        Label.__init__(self, frame)
        self.frame = frame
        self.txt = '안녕하세요'
        self.config(text=self.txt, bg='black', fg='white', font='Times 30')
        self.pack(side='top', anchor='n')
        self.frame.after(100, self.animate)
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

from PIL import ImageTk, Image

# Youtube Video를 재생하는 Frame
class Icon(Frame):
    def __init__(self, root, width=800, height=300):
        Frame.__init__(self, root, width=width, height=height, bg='black')
        self.youtube_img = ImageTk.PhotoImage(Image.open('data/youtube.png').resize((150,150)))
        self.youtube_label = Label(self, bg='black', width=150, height=150, image=self.youtube_img)
        self.youtube_label.pack(side='left', anchor='w', padx=15)

        self.music_img = ImageTk.PhotoImage(Image.open('data/music.png').resize((120,120)))
        self.music_label = Label(self, bg='black', image= self.music_img)
        self.music_label.pack(side='left', anchor='w')


from engine import WeatherForecast

class Weather(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, bg='black', width=1000, height=400)
        self.parent = parent
        self.weather = WeatherForecast()
        self.temperature, self.img_path = self.weather.requestCurrentWeather()
        self.small_font=tkinter.font.Font(family="맑은 고딕", size=65)

        # labels
        self.txt_label = Label(self, bg='black', fg='white', font=self.small_font)
        self.txt_label.config(text=self.temperature)
        self.txt_label.pack(side='left', anchor='w', padx=10, pady=5)

        self.img = ImageTk.PhotoImage(Image.open(self.img_path).resize((120,120)))
        self.img_label = Label(self, bg='black', image=self.img)
        self.img_label.pack(side='left', anchor='w', padx=15)
