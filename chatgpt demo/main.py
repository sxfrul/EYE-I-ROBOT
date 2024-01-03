import openai
import RPi.GPIO as GPIO
from os import system

kitchen_pin = 11
bedroom_pin = 13
toilet_pin = 15

GPIO.setup(kitchen_pin, GPIO.OUT)
GPIO.setup(bedroom_pin, GPIO.OUT)
GPIO.setup(toilet_pin, GPIO.OUT)

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
    messages.append({"role": "assistant", "content": reply})

    return reply.lower()
    
def home_automation(reply):
    if "kitchen lights" in reply:
        print("[KITCHEN LIGHTS ARE NOW ON]")
        GPIO.output(kitchen_pin, GPIO.HIGH)
    elif "bedroom lights" in reply:
        print("[BEDROOM LIGHTS ARE NOW ON]")
        GPIO.output(bedroom_pin, GPIO.HIGH)
    elif "toilet lights" in reply:
        print("[TOILET LIGHTS ARE NOW ON]")
        GPIO.output(toilet_pin, GPIO.HIGH)

if __name__ == "__main__":
    openai.api_key = ('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')
    messages = [ {"role": "system", "content": 
                "There are three rooms, kitchen, toilet, bedroom. If asked 'Turn on [room] lights' respond with 'Turning on the [room] lights'"} ]

    while True:
        message = input("Prompt: ")
        respond = assistant()
        home_automation(respond)