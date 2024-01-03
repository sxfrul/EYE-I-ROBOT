import openai
from os import system

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
    elif "bedroom lights" in reply:
        print("[BEDROOM LIGHTS ARE NOW ON]")
    elif "toilet lights" in reply:
        print("[TOILET LIGHTS ARE NOW ON]")

if __name__ == "__main__":
    openai.api_key = ('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')
    messages = [ {"role": "system", "content": 
                "There are three rooms, kitchen, toilet, bedroom. If asked 'Turn on [room] lights' respond with 'Turning on the [room] lights'"} ]

    while True:
        message = input("Prompt: ")
        respond = assistant()
        home_automation(respond)