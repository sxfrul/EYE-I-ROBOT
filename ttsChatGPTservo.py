from multiprocessing import Process

# IMPORT SPEECHRECOGNITION
import openai
from transcript import recordAndTranscript

# TRACKER
from cvzone.FaceDetectionModule import FaceDetector
import cv2, base64 #encoding-purpose
import re

# SERVO CONTROLLER
import time
import math
import smbus

# Waveshare Module
class PCA9685:

  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  def __init__(self, address=0x40, debug=False):
    self.bus = smbus.SMBus(1)
    self.address = address
    self.debug = debug
    if (self.debug):
      print("Reseting PCA9685")
    self.write(self.__MODE1, 0x00)
	
  def write(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    self.bus.write_byte_data(self.address, reg, value)
    if (self.debug):
      print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
	  
  def read(self, reg):
    "Read an unsigned byte from the I2C device"
    result = self.bus.read_byte_data(self.address, reg)
    if (self.debug):
      print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
	
  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
      print("Setting PWM frequency to %d Hz" % freq)
      print("Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
      print("Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    self.write(self.__PRESCALE, int(math.floor(prescale)))
    self.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.write(self.__MODE1, oldmode | 0x80)

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
    self.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
    if (self.debug):
      print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))
	  
  def setServoPulse(self, channel, pulse):
    "Sets the Servo Pulse,The PWM frequency must be 50HZ"
    pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us
    self.setPWM(channel, 0, int(pulse))

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

def tracker():
    servoX_pin = 15
    servoY_pin = 14

    pwm = PCA9685(0x40, debug=False)
    pwm.setPWMFreq(50)
    # cap = cv2.VideoCapture(0)
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
        # cv2.imshow("EYE(i) ROBOT", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    p1 = Process(target=tracker)
    p1.start()
    # openai.api_key = ('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')
    messages = [ {"role": "system", "content": 
                "You are a intelligent assistant."} ]
    
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
                takingInput = False
            except:
                speak("no command given. please retry")
                takingInput=False