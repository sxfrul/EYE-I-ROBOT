import sys
from math import atan2
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QPoint
import cv2
import threading
from cvzone.FaceDetectionModule import FaceDetector
import re

class VideoThread(threading.Thread):
    def __init__(self, eye_widget):
        super().__init__()
        self.eye_widget = eye_widget
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        cap = cv2.VideoCapture(0)
        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
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
        self.setGeometry(100, 100, 1024, 600)
        self.setWindowTitle('Eyeball')
        self.setMouseTracking(True)
        self.eye_center = QPoint(512, 300)
        self.eye_radius = 110  # Adjust eyeball radius
        self.pupil_radius = 40  # Adjust pupil radius
        self.pupil_center = self.eye_center
        self.face_detector = FaceDetector(minDetectionCon=0.5)
        self.video_thread = VideoThread(self)
        self.video_thread.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw eyeball
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(self.eye_center, self.eye_radius, self.eye_radius)

        # Draw pupil
        pupil_x = int(self.pupil_center.x() - self.pupil_radius)
        pupil_y = int(self.pupil_center.y() - self.pupil_radius)
        pupil_diameter = int(2 * self.pupil_radius)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(pupil_x, pupil_y, pupil_diameter, pupil_diameter)

    def updateEyePosition(self, face_coords):
        if face_coords:
            x, y = face_coords
            face_center = QPoint(x, y)

            # Calculate angle from center of the eyeball to face center
            dx = face_center.x() - self.eye_center.x()
            angle = atan2(0, dx)  # Only consider difference in x-coordinate

            # Limit the pupil's movement within the eyeball
            max_radius = self.eye_radius - self.pupil_radius
            radius = min(abs(dx), max_radius) * (1 if dx >= 0 else -1)  # Only consider horizontal movement

            # Update pupil position
            self.pupil_center = self.eye_center + QPoint(round(radius), 0)

            self.update()


    def closeEvent(self, event):
        self.video_thread.stop()
        self.video_thread.join()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EyeWidget()
    ex.show()
    sys.exit(app.exec_())
