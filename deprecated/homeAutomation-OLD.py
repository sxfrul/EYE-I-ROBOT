# HOME AUTOMATION
import RPi.GPIO as GPIO

kitchen_pin = 17
bedroom_pin = 27
toilet_pin = 22

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

def home_automation(reply):
    if "kitchen" in reply:
        print("[KITCHEN LIGHTS]")
        if "on" in reply:
            GPIO.output(kitchen_pin, GPIO.HIGH)
        elif "off" in reply:
            GPIO.output(kitchen_pin, GPIO.LOW)

    elif "bedroom" in reply:
        print("[BEDROOM LIGHTS]")
        if "on" in reply:
            GPIO.output(bedroom_pin, GPIO.HIGH)
        elif "off" in reply:
            GPIO.output(bedroom_pin, GPIO.LOW)

    elif "toilet" in reply:
        print("[TOILET LIGHTS]")
        if "on" in reply:
            GPIO.output(toilet_pin, GPIO.HIGH)
        elif "off" in reply:
            GPIO.output(toilet_pin, GPIO.LOW)