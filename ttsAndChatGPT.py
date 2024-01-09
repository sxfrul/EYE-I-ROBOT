from multiprocessing import Process

# IMPORT SPEECHRECOGNITION
import openai
from transcript import recordAndTranscript

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


if __name__ == "__main__":
    status = 1

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