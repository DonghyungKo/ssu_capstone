import tkinter
import PIL.Image
import PIL.ImageTk
import cv2


class App:
    def __init__(self, window, video_source1):
        self.window = window
        self.window.title("KEC MEDIA PLAYER")
        self.video_source1 = video_source1
        self.photo1 = ""

        # open video source
        self.vid1 = MyVideoCapture(self.video_source1)

        # Create a canvas that can fit the above video source size
        self.canvas1 = tkinter.Canvas(window, width=500, height=500)
        self.canvas1.pack(padx=5, pady=10, side="left")

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        # Get a frame from the video source
        ret1, frame1 = self.vid1.get_frame

        if ret1 :
                self.photo1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame1))
                self.canvas1.create_image(0, 0, image=self.photo1, anchor=tkinter.NW)

        self.window.after(self.delay, self.update)


class MyVideoCapture:
    def __init__(self, video_source1):
        # Open the video source
        self.vid1 = cv2.VideoCapture(video_source1)

        if not self.vid1.isOpened():
            raise ValueError("Unable to open video source", video_source1)

    @property
    def get_frame(self):
        ret1 = ""
        if self.vid1.isOpened():
            ret1, frame1 = self.vid1.read()
            frame1 = cv2.resize(frame1, (500, 500))
            if ret1:
                # Return a boolean success flag and the current frame converted to BGR
                return ret1, cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)

        return ret1, None, ret2, None

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid1.isOpened():
            self.vid1.release()


def callback():
    global v1
    v1=E1.get()
    if v1 == "":
        L3.pack()
        return
    initial.destroy()


v1 = ""

initial = tkinter.Tk()
initial.title("KEC MEDIA PLAYER")
L0 = tkinter.Label(initial, text="Enter the full path")
L0.pack()
L1 = tkinter.Label(initial, text="Video 1")
L1.pack()
E1 = tkinter.Entry(initial, bd =5)
E1.pack()

B = tkinter.Button(initial, text ="Next", command = callback)
B.pack()
L3 = tkinter.Label(initial, text="Enter both the names")

initial.mainloop()


# Create a window and pass it to the Application object
App(tkinter.Tk(),v1)
