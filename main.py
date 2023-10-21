from multiprocessing import Process
from cvzone.FaceDetectionModule import FaceDetector
import speech_recognition as sr  
from os import system
import openai
import cv2
import serial

ArduinoSerial=serial.Serial('/dev/cu.usbmodem101',9600,timeout=0.1)

def tracker():
    cap = cv2.VideoCapture(0)
    detector = FaceDetector(minDetectionCon=0.5)

    while True:
        success, img = cap.read()
        img=cv2.flip(img,1)
        img, bboxs = detector.findFaces(img)

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
                print(center)
                coordinates = str(center)
                ArduinoSerial.write(coordinates.encode('utf-8'))


        cv2.imshow("Image", img)
        cv2.waitKey(1)

def assistant():
    openai.api_key = ('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')
    messages = [ {"role": "system", "content": 
                "You are a intelligent assistant."} ]
    
    # obtain audio from the microphone  
    r = sr.Recognizer()  
    source = sr.Microphone()

    outputting = ("output")
    processing = ("process")
    inputting = ("input")
    
    with source:
        #processing
        #ArduinoSerial.write(processing.encode('utf-8'))
        system("say Please wait, calibrating microphone..")
        r.adjust_for_ambient_noise(source, duration=1.5)
        #ArduinoSerial.write(outputting.encode('utf-8'))
        system("say your personal robot companion is now online")
        while True:
            #inputting
            listening = True
            while listening:
                #ArduinoSerial.write(inputting.encode('utf-8'))
                audio = r.listen(source)
                try:
                    message = r.recognize_google(audio)
                    message = message.lower()

                    if "computer" in message:
                        #outputting
                        #ArduinoSerial.write(outputting.encode('utf-8'))
                        system("say Yes how can i assist you?")
                        listening = False
                except:
                    continue
            #inputting
            #ArduinoSerial.write(inputting.encode('utf-8'))
            takingInput = True
            while takingInput: #make the led go orange
                audio = r.listen(source)
                try:
                    #ArduinoSerial.write(processing.encode('utf-8'))
                    message = r.recognize_google(audio)
                    message = message.lower()
                    #processing
                    message = ("Talk like a human and give me the simplest answers only, " + message)
                    print(message)
                    system("say Please wait while i look through my database    ")
                    if message:
                        messages.append(
                            {"role": "user", "content": message},
                        )
                        chat = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo", messages=messages
                        )
                    reply = chat.choices[0].message.content
                    #make led go green
                    #outputting
                    #ArduinoSerial.write(outputting.encode('utf-8'))
                    system("say According to my database")
                    system('say "{}"'. format(reply))
                    messages.append({"role": "assistant", "content": reply})
                    takingInput = False
                except:
                    #outputting
                    #ArduinoSerial.write(outputting.encode('utf-8'))
                    system("say no command given. please retry")
                    takingInput=False

if __name__ == '__main__':
    p = Process(target=assistant)
    p2 = Process(target=tracker)
    p.start()
    p2.start()