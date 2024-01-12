# HOME AUTOMATION
import RPi.GPIO as GPIO

room_pins = {
    "kitchen": 17,
    "bedroom": 27,
    "toilet": 22,
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Initializing every room pin
for room in room_pins:
    GPIO.setup(room_pins[room], GPIO.OUT)

def home_automation(reply):
    for room in room_pins:
        if room in reply:
            print(f"[{room.upper()} LIGHTS]")
            
            # Check if "on" or "off" is mentioned in the reply
            if "on" in reply:
                GPIO.output(room_pins[room], GPIO.HIGH)
            elif "off" in reply:
                GPIO.output(room_pins[room], GPIO.LOW)