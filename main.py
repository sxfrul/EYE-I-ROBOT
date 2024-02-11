from multiprocessing import Process
import numpy as np

# WS SERVER
import websockets
import socket
import asyncio

serverPort = 8000
serverAddress = socket.gethostbyname(socket.gethostname())

# IMPORT SPEECHRECOGNITION
import openai
from transcript import recordAndTranscript

# TRACKER
from cvzone.FaceDetectionModule import FaceDetector
import cv2
import re
import servoModule

# TTS
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 5.5)

# IMPORT HOMEAUTOMATION
from homeAutomation import home_automation

# LED INDICATOR
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26, GPIO.OUT)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def vision():
    print("Starting camera")

    try :

        servoX_pin = 3
        servoY_pin = 0

        pwm = servoModule.PCA9685(0x40, debug=False)
        pwm.setPWMFreq(50)

        #Raspberry Pi Camera
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

        detector = FaceDetector(minDetectionCon=0.5)
        servo_Xi = 1500
        servo_Yi = 1200

        pwm.setServoPulse(servoX_pin, servo_Xi)
        pwm.setServoPulse(servoY_pin, servo_Yi)

        while cap.isOpened():
            _, frame = cap.read()
            frame = cv2.flip(frame,1)

            frame, bboxs = detector.findFaces(frame)

            myList = []

            # Compute area of BBOXs
            for bbox in bboxs:
                x, y, w, h = bbox["bbox"]
                area = w*h
                bbox["area"] = area
                myList.append(bbox)

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

                    int_Xcoords = int(x_coords)
                    int_Ycoords = int(y_coords)

                    # coords_matrix = np.array([int_Xcoords, int_Ycoords])

                    # coefficient to quadratic

                    a2 = 1/640
                    b2 = -1 / 2
                    # #Quadratic eqn to accelerate
                    steps_Y = (a2*(int_Ycoords**2)) + (b2*int_Ycoords) + 40
                    steps_X = (a2*(int_Xcoords**2)) + (b2*int_Xcoords) + 40
                    # with acceleration (from quadratic)
                    if int_Xcoords > 190:
                        servo_Xi += steps_X
                    elif int_Xcoords < 150:
                        servo_Xi -= steps_X

                    if int_Ycoords > 190:
                        servo_Yi += steps_Y
                    elif int_Ycoords < 150:
                        servo_Yi -= steps_Y

                    pwm.setServoPulse(servoY_pin, servo_Yi)
                    pwm.setServoPulse(servoX_pin, servo_Xi)

            encoded = cv2.imencode('.jpg', frame)[1].tobytes()
            data = bytes(encoded)

            # cv2.imshow("Transimission", frame)

            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        cap.release()
    except Exception as e:
        print("Client Disconnected !")
        cap.release()
    # except:
    #     print("Someting went Wrong !")

async def transmit(websocket, path):
    print("Client Connected !")

    await websocket.send("Connection Established")
    try :

        servoX_pin = 3
        servoY_pin = 0

        pwm = servoModule.PCA9685(0x40, debug=False)
        pwm.setPWMFreq(50)

        #Raspberry Pi Camera
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

        detector = FaceDetector(minDetectionCon=0.5)
        servo_Xi = 1500
        servo_Yi = 1500

        pwm.setServoPulse(servoX_pin, servo_Xi)
        pwm.setServoPulse(servoY_pin, servo_Yi)

        while cap.isOpened():
            _, frame = cap.read()
            frame = cv2.flip(frame,1)

            frame, bboxs = detector.findFaces(frame)

            myList = []

            # Compute area of BBOXs
            for bbox in bboxs:
                x, y, w, h = bbox["bbox"]
                area = w*h
                bbox["area"] = area
                myList.append(bbox)

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

                    int_Xcoords = int(x_coords)
                    int_Ycoords = int(y_coords)

                    # coords_matrix = np.array([int_Xcoords, int_Ycoords])

                    # coefficient to quadratic

                    a2 = 1/640
                    b2 = -1 / 2
                    # #Quadratic eqn to accelerate
                    steps_Y = (a2*(int_Ycoords**2)) + (b2*int_Ycoords) + 40
                    steps_X = (a2*(int_Xcoords**2)) + (b2*int_Xcoords) + 40
                    # with acceleration (from quadratic)
                    if int_Xcoords > 190:
                        servo_Xi += steps_X
                    elif int_Xcoords < 150:
                        servo_Xi -= steps_X

                    if int_Ycoords > 190:
                        servo_Yi += steps_Y
                    elif int_Ycoords < 150:
                        servo_Yi -= steps_Y

                    pwm.setServoPulse(servoY_pin, servo_Yi)
                    pwm.setServoPulse(servoX_pin, servo_Xi)

            encoded = cv2.imencode('.jpg', frame)[1].tobytes()
            data = bytes(encoded)

            await websocket.send(data)

            # cv2.imshow("Transimission", frame)

            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        cap.release()
    except Exception as e:
        print("Client Disconnected !")
        cap.release()
    # except:
    #     print("Someting went Wrong !")

def server_process():
    print("Server process is starting..")
    start_server = websockets.serve(transmit, host="192.168.0.170", port=serverPort)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    # server = Process(target=server_process)
    # server.start()
    camera = Process(target=vision)
    camera.start()

    openai.api_key = ('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')
    messages = [ {"role": "system", "content":
                "There are three rooms, kitchen, toilet, bedroom. If asked 'Turn on/off [room] lights' respond with 'Turning on/off the [room] lights'"} ]

    GPIO.output(26, GPIO.HIGH)
    #speak("Please wait, calibrating microphone..")

    #speak("eye robot is now online")
    while True:
        listening = True
        while listening:
            try:
                message = recordAndTranscript()

                if "robot" in message:
                    speak("Yes how can i assist you?")
                    listening = False
            except:
                continue
        takingInput = True
        while takingInput:
            try:
                message = recordAndTranscript()
                # message = ("Talk like a human and give me the simplest answers only, " + message)
                speak("Please wait while i look through my database    ")
                if message:
                    messages.append(
                        {"role": "user", "content": message},
                    )
                    chat = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo", messages=messages
                    )
                reply = chat.choices[0].message.content
                speak("According to my database")
                speak(reply)
                messages.append({"role": "assistant", "content": reply})
                home_automation(reply)
                takingInput = False
            except:
                speak("no command given. please retry")
                takingInput=False