from multiprocessing import Process

# IMPORT SPEECHRECOGNITION
import openai
from transcript import recordAndTranscript

# IMPORT TRACKERMODULE
import servoModule

# TRACKER
from cvzone.FaceDetectionModule import FaceDetector
import cv2, base64 #encoding-purpose
import re

# TTS
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 155)
engine.setProperty('volume', 5.5)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# MAIN FUNCTIONS
def tracker():
    servoX_pin = 15
    servoY_pin = 14

    pwm = servoModule.PCA9685(0x40, debug=False)
    pwm.setPWMFreq(50)
    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
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
                coordinates = str(center)
                x_coords, y_coords = re.findall(r'\d+', coordinates)

                # Mapping coords to servo range
                servoX_coords = ((int(x_coords)*1200) / 1024) + 1200
                servoY_coords = ((int(y_coords)*1500) / 768) + 1200

                pwm.setServoPulse(servoX_pin, servoX_coords)
                pwm.setServoPulse(servoY_pin, servoY_coords)

        # No imshow for no gui use case
        #cv2.imshow("EYE(i) ROBOT", img)
        cv2.waitKey(1)

def assistant():
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    reply = chat.choices[0].message.content
    print(reply)
    speak(reply)
    messages.append({"role": "assistant", "content": reply})

    return reply.lower()

def assistant2():
    if __name__ == "__main__":
    openai.api_key = ('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')
    messages = [ {"role": "system", "content":
                "There are three rooms, kitchen, toilet, bedroom. If asked 'Turn on/off [room] lights' respond with 'Turning on/off the [room] lights'"} ]
    while status == 1:
        message = recordAndTranscript()
        if "exit" not in message:
            respond = assistant()
            #home_automation(respond)
        elif "exit" in message:
            status = 0
            #GPIO.cleanup()

if __name__ == "__main__":
    message = recordAndTranscript()
    print(message)

    p = Process(target=assistant2)
    p2 = Process(target=tracker)
    p.start()
    p2.start()