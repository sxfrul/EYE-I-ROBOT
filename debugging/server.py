# server original dependencies:
from multiprocessing import Process
import websockets
import asyncio
from cvzone.FaceDetectionModule import FaceDetector
import time
import cv2, base64
import functools

#eyero original dependencies:
import speech_recognition as sr  
from os import system
import openai
import re

#waveshare original dependencies:
import time
import math
import smbus

port = 8000

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



#Server
print("Started server on port : ", port)

def test():
    global number
    number = 10
    while True:
        print(number)
        number += 10
        time.sleep(2)

def cam():
    cap = cv2.VideoCapture(0) 
    detector = FaceDetector(minDetectionCon=0.5)

    while cap.isOpened():
            _, frame = cap.read()
            frame = cv2.flip(frame,1)

            frame, bboxs = detector.findFaces(frame)
            
            encoded = cv2.imencode('.jpg', frame)[1]

async def transmit(websocket, path, initial_number):
    print("Client Connected !")
    print(f"This is initial number: {initial_number}")

    await websocket.send("Connection Established")
    try :

        servoX_pin = 15
        servoY_pin = 14

        pwm = PCA9685(0x40, debug=False)
        pwm.setPWMFreq(50)
        
        #Raspberry Pi Camera
        #cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap = cv2.VideoCapture(0) 
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
                    # print(f"{x_coords} {y_coords}")
                    # print(f"{servoX_coords} {servoY_coords}")

                    pwm.setServoPulse(servoX_pin, servoX_coords)
                    pwm.setServoPulse(servoY_pin, servoY_coords)
                    # pwm.setServoPulse(0,coordinates)
                    # ArduinoSerial.write(coordinates.encode('utf-8'))
            
            encoded = cv2.imencode('.jpg', frame)[1]

            data = str(base64.b64encode(encoded))
            data = data[2:len(data)-1]
            
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

if __name__ == '__main__':
    # p = Process(target=test)
    # p.start()
    test = 10
    start_server = websockets.serve(functools.partial(transmit, initial_number=test), host="192.168.0.170", port=port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    