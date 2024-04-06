import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QPoint
import cv2
import threading
from cvzone.FaceDetectionModule import FaceDetector
import re
from time import sleep

class VideoThread(threading.Thread):
    def __init__(self, eye_widget):
        super().__init__()
        self.eye_widget = eye_widget
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, 640)  # Set width of the frame
        cap.set(4, 480)  # Set height of the frame
        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("no camera detected")
                break
            frame = cv2.flip(frame, 1)
            frame, bboxs = self.eye_widget.face_detector.findFaces(frame)
            myList = []

            for bbox in bboxs:
                x, y, w, h = bbox["bbox"]
                area = w * h
                bbox["area"] = area
                myList.append(bbox)

            if myList:
                max_area_dict = max(myList, key=lambda x: x["area"])
                if max_area_dict:
                    center = max_area_dict["center"]
                    coordinates = str(center)
                    x_coords, y_coords = re.findall(r'\d+', coordinates)
                    x_coords = int(x_coords)
                    y_coords = int(y_coords)

                    face_center = [x_coords, y_coords]
                    self.eye_widget.updateEyePosition(face_center)

            cv2.waitKey(1)

        cap.release()

class EyeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: black;") 
        self.setGeometry(100, 100, 1024, 600)
        self.setWindowTitle('Eyeball')
        self.setMouseTracking(True)
        self.eye_center = QPoint(512, 300) # Position of main eyeball
        self.eye_radius = 110  # Adjust eyeball radius

        self.pupil_radius = 40  # Adjust pupil radius
        self.pupil_center = QPoint(512, 300)

        self.face_detector = FaceDetector(minDetectionCon=0.5)
        self.video_thread = VideoThread(self)
        self.video_thread.start()

        # Label for displaying direction
        self.direction_label = QLabel(self)
        self.direction_label.setGeometry(450, 20, 150, 30)
        self.direction_label.setStyleSheet("color: white; font-size: 20px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw eyeball
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(self.eye_center, self.eye_radius, self.eye_radius)

        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(self.pupil_center, self.pupil_radius, self.pupil_radius)

    def updateEyePosition(self, face_coords):
        if face_coords:
            x, y = face_coords

            tempValueX = self.pupil_center.x()

            maxRight = 560
            maxLeft = 460
            maxMiddle = 512

            if x >= 200 and x <= 400: #badcode
                self.direction_label.setText("")
                if tempValueX > 512:
                    tempValueX -= 10
                    barrierValue = max(maxMiddle, tempValueX)
                    self.pupil_center = QPoint(barrierValue, 300)
                elif tempValueX < 512:
                    tempValueX += 10
                    barrierValue = min(maxMiddle, tempValueX)
                    self.pupil_center = QPoint(barrierValue, 300)
                else:
                    pass
            
            # RIGHT-SIDE
            elif x > 400: 
                tempValueX += 10
                barrierValue = min(maxRight, tempValueX)
                self.pupil_center = QPoint(barrierValue, 300)
                self.direction_label.setText("RIGHT")

            # LEFT-SIDE
            else:
                tempValueX -= 10
                barrierValue = max(maxLeft, tempValueX)
                self.pupil_center = QPoint(barrierValue, 300)
                self.direction_label.setText("LEFT")

            self.update()

        # def typewriterAnimation(self, text):
        # split_text = [*text]
        # string = ""
        # for c in split_text:
        #     string += c
        #     self.direction_label.setText(string)
        #     sleep(0.1)

    def closeEvent(self, event):
        self.video_thread.stop()
        self.video_thread.join()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EyeWidget()
    ex.show()
    sys.exit(app.exec_())
