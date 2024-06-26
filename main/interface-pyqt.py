import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QPoint
import cv2
import threading
from cvzone.FaceDetectionModule import FaceDetector
import re
from time import sleep

import websockets
import asyncio
from PIL import Image

# GEN AI
import google.generativeai as genai
import config

# TTS
import pyttsx3
from transcript import recordAndTranscript
from os import system

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 5.5)

class VideoThread(threading.Thread):
    def __init__(self, eye_widget):
        super().__init__()
        self.log = 0
        self.eye_widget = eye_widget
        self.stop_event = threading.Event()
        self.server_thread = threading.Thread(target=self.server_thread)

    async def transmit(self, websocket, path):
        print("Connection Established")
        try:
            while True:
                await websocket.send(self.video_bytes)
        except:
            print("Connection closed!")

    def server_thread(self):
        print("Test")
        asyncio.set_event_loop(asyncio.new_event_loop())
        start_server = websockets.serve(self.transmit, host="172.20.10.4", port=8000)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def stop(self):
        self.stop_event.set()

    def run(self):
        self.server_thread.start()

        cap = cv2.VideoCapture(0)
        cap.set(3, 640)  # Set width of the frame
        cap.set(4, 480)  # Set height of the frame
        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("no camera detected")
                break
            frame = cv2.flip(frame, 1)
            self.videoPIL = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
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

            encoded = cv2.imencode('.jpg', frame)[1].tobytes()
            video_bytes = bytes(encoded)

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
        self.eye_center = QPoint(512, 300) # Position of main eyeball
        self.eye_radius = 110  # Adjust eyeball radius

        self.pupil_radius = 40  # Adjust pupil radius
        self.pupil_center = QPoint(512, 300)

        self.face_detector = FaceDetector(minDetectionCon=0.5)
        self.video_thread = VideoThread(self)
        self.video_thread.start()

        self.genai_thread = threading.Thread(target=self.genAI)
        self.genai_thread.start()

        # Label for displaying direction
        self.genai_label = QLabel(self)
        self.genai_label.setWordWrap(True)
        self.genai_label.setAlignment(Qt.AlignCenter)
        self.genai_label.setGeometry(115, 100, 800, 50)
        self.genai_label.setStyleSheet("color: white; font-size: 20px;")

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 5.5)
        self.showFullScreen()
        
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def genAI(self):
        GOOGLE_API_KEY = config.get("gemini-api-key")

        genai.configure(api_key=GOOGLE_API_KEY)

        model = genai.GenerativeModel('gemini-1.0-pro') # Model : Gemini Pro
        self.modelVision = genai.GenerativeModel('gemini-pro-vision')
        chat = model.start_chat(history=[])

        response = chat.send_message("If i say turn on the kitchen/bedroom/toilet lights, response with 'Turning on the kitchen/bedroom/toilet lights'")

        while True:
            asleep = True
            while asleep:
                try:
                    passiveRecord = recordAndTranscript()
                    if "robot" in passiveRecord or "iRobot" in passiveRecord or "i robot" in passiveRecord:
                        system("aplay wakeup.wav")
                        self.genai_label.setText("LISTENING!")
                        asleep = False
                except :
                    self.genai_label.setText("")
                    continue
            takingInput = True
            while takingInput:
                try:
                    message = recordAndTranscript() 
                    print(message)
                    if message == "use camera":
                        system("aplay wakeup.wav")
                        self.genAIVision()
                        print("Vision closed.")
                        break
                    print("after camera, this message doesnt appear")
                    message += "? answer concisely in complete sentence."
                    response = chat.send_message(message)
                    print(response.text)
                    self.typewriterAnimation(response.text)
                    asyncio.run(self.async_main(response.text))
                    takingInput = False
                except:
                    print("No command given please retry...")
                    takingInput = False

    def genAIVision(self):
        self.genai_label.setText("CAMERA MODE")
        try:
            message = recordAndTranscript() 
            response = self.modelVision.generate_content([message, self.video_thread.videoPIL])
            self.typewriterAnimation(response.text)
        except Exception as e:
            print("Camera prompt failed...")
        return


    async def homeAutomationDebug(self, reply):
        uri = "ws://172.20.10.7:80"  # Replace <nodeMCU_IP_address> with NodeMCU's IP address
        print(reply)

        try:
            async with websockets.connect(uri) as websocket:
                data = ""
                if "kitchen" in reply and "on" in reply:
                    data += "led1:on"
                elif "kitchen" in reply and "off" in reply:
                    data += "led1:off"
                if "bedroom" in reply and "on" in reply:
                    data += "led2:on"
                elif "bedroom" in reply and "off" in reply:
                    data += "led2:off"
                if "toilet" in reply and "on" in reply:
                    data += "led3:on"
                elif "toilet" in reply and "off" in reply:
                    data += "led3:off"
                else:
                    pass
                if data != "":
                    print(data)
                    await websocket.send(data)

        except Exception as e:
            print(f"Failed to connect: {e}")

    async def async_main(self, reply):
        await self.homeAutomationDebug(reply)

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

            # LEFT-SIDE
            else:
                tempValueX -= 10
                barrierValue = max(maxLeft, tempValueX)
                self.pupil_center = QPoint(barrierValue, 300)

            self.update()

    def typewriterAnimation(self, text):
        self.tts_thread = threading.Thread(target=self.tts, args=(text,))
        self.tts_thread.start()

        split_text = text.split()
        string = ""
        textCount = 0
        for sentence in split_text:
            if textCount > 20:
                string = "- "
                textCount = 0

            split_character = [*sentence]

            for c in split_character:
                string += c
                self.genai_label.setText(string)
                sleep(0.07)

            string += " "
            self.genai_label.setText(string)
            sleep(0.05)
            textCount += 1

    def tts(self, text):
        message = text.replace("'", "")
        message = text.replace("*", "")
        message = message.replace("Im", "I am")
        self.speak(message)

    def closeEvent(self, event):
        self.video_thread.stop()
        self.video_thread.join()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EyeWidget()
    ex.show()
    sys.exit(app.exec_())
