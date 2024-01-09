import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 155)
engine.setProperty('volume', 5.5)

def speak(text):
    engine.say(text)
    engine.runAndWait()