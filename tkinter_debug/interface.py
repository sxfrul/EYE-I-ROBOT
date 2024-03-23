import tkinter as tk
import cv2
from PIL import Image, ImageTk
from cvzone.FaceDetectionModule import FaceDetector
import re

class WebcamApp:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("500x500")
        self.window.resizable(0,0)
        
        self.vid = cv2.VideoCapture(video_source)
        
        self.canvas = tk.Canvas(window, width=500, height=500, bg="black")
        self.canvas.pack()

        self.wheel2 = self.canvas.create_oval(100, 120, 400, 420, tags="eye oval", fill="white")
        self.wheel1 = self.canvas.create_oval(250, 220, 350, 320, tags="iris oval", fill="black")
        
        self.delay = 50
        self.update()
        
        self.window.mainloop()
        
    def update(self):
        pos = self.canvas.coords("iris")

        ret, frame = self.vid.read()
        detector = FaceDetector(minDetectionCon=0.5)
        frame = cv2.flip(frame,1)
        frame, bboxs = detector.findFaces(frame)

        myList = []

        # Compute area of BBOXs
        for bbox in bboxs:
            x, y, w, h = bbox["bbox"]
            area = w*h
            bbox["area"] = area
            myList.append(bbox)
            print(myList)

        # if myList is empty
        if not myList:
            # does not exist
            pass
        else:
            # Compares between dicts in list, select dict with higher AREA
            max_area_dict = max(myList, key=lambda x: x["area"])
            if max_area_dict:
                center = max_area_dict["center"]
                coordinates = str(center)
                x_coords, y_coords = re.findall(r'\d+', coordinates)
                x_coords = int(x_coords)

        try:
            if x_coords > 300 and pos[2] < 380:
                self.canvas.move("iris", 10, 0)
            elif x_coords <= 300 and pos[0] > 150:
                self.canvas.move("iris", -10, 0)
        except:
            pass

        self.window.after(self.delay, self.update)

# Create a window and pass it to the WebcamApp class
root = tk.Tk()
app = WebcamApp(root, "EYE (i) ROBOT")
