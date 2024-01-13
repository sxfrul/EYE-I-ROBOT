from multiprocessing import Process

# WS SERVER
import websockets
import socket
import asyncio

server_port = 8000
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

def speak(text):
    engine.say(text)
    engine.runAndWait()

async def transmit(websocket, path):
    print("Client Connected !")

    await websocket.send("Connection Established")
    try :

        servoX_pin = 15
        servoY_pin = 14

        pwm = servoModule.PCA9685(0x40, debug=False)
        pwm.setPWMFreq(50)
        
        #Raspberry Pi Camera
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        
        detector = FaceDetector(minDetectionCon=0.5)

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

                    # Mapping coords to servo range
                    servoX_coords = ((int(x_coords)*1200) / 1024) + 1200
                    servoY_coords = ((int(y_coords)*1500) / 768) + 1200

                    pwm.setServoPulse(servoX_pin, servoX_coords)
                    pwm.setServoPulse(servoY_pin, servoY_coords)
            
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
        
def serverProcess():
    print("Server process is starting..")
    start_server = websockets.serve(transmit, host=serverAddress, port=server_port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    server = Process(target=serverProcess)
    server.start()

    openai.api_key = ('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')
    messages = [ {"role": "system", "content":
                "There are three rooms, kitchen, toilet, bedroom. If asked 'Turn on/off [room] lights' respond with 'Turning on/off the [room] lights'"} ]
    
    speak("Please wait, calibrating microphone..")

    speak("eye robot is now online")
    while True:
        listening = True
        while listening:
            try:
                message = recordAndTranscript()

                if "robot" in message:
                    print("It worked")
                    speak("Yes how can i assist you?")
                    listening = False
            except:
                print("Retrying..")
                continue
        takingInput = True
        while takingInput:
            try:
                message = recordAndTranscript()
                # message = ("Talk like a human and give me the simplest answers only, " + message)
                print(message)
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