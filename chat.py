import json
import random
import tkinter as tk
import threading
import speech_recognition as sr
from gtts import gTTS
import os
import pywhatkit
import torch
import datetime

from ttkthemes.themed_style import ThemedStyle

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import webbrowser


def talk(text):
    tts = gTTS(text=text, lang='en')
    tts.save('output.mp3')
    os.system('mpg123 output.mp3')


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Max"

# Tkinter UI

root = tk.Tk()
root.title("Max")

# Set the window size and position
root.geometry("400x400")
root.attributes("-alpha", 0.5)

style = ThemedStyle(root)
style.set_theme("clam")  # Use a modern theme


output_text = tk.Text(root, width=50, height=5, borderwidth=0, wrap=tk.WORD)
output_text.pack(fill=tk.BOTH, expand=True)


def display_text(text):
    output_text.config(state=tk.NORMAL)  # Enable editing
    output_text.delete(1.0, tk.END)  # Clear previous text

    container_text = f"\u25A0 {text}\n"
    output_text.insert(tk.END, container_text, "container")

    output_text.config(state=tk.DISABLED)  # Disable editing
    output_text.see(tk.END)  # Scroll to the bottom


container_style = {
    "background": "grey",
    "foreground": "black",
    "font": ("Nunito", 25),
    "borderwidth": 3,
    "relief": "solid",
    "padx": 20,
    "pady": 20,
    "wrap": tk.WORD
}
style.configure("TText", **container_style)

output_text.tag_configure("container", font=("Nunito", 25))


def open_whatsapp():
    url = "https://web.whatsapp.com/"
    webbrowser.open(url)
    talk("Opening WhatsApp...")


def listen():
    display_text("Listening...")

    r = sr.Recognizer()

    with sr.Microphone() as source:
        display_text("Speak:")
        audio = r.listen(source)

    try:
        sentence = r.recognize_google(audio)
        display_text("You said: " + sentence)
    except sr.UnknownValueError:
        display_text("I could not understand audio")
    except sr.RequestError as e:
        display_text("Could not request results from Google Speech Recognition service; {}".format(e))


def start_listening():
    wakeup_word_spoken = False
    speak_prompt_displayed = False

    while not wakeup_word_spoken:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            if not speak_prompt_displayed:
                talk("I am Max, your personal assistant. How may I help you?")
                display_text("Listening")
                speak_prompt_displayed = True
            audio = r.listen(source)

            try:
                sentence = r.recognize_google(audio)
                display_text("You said: " + sentence)
            except sr.UnknownValueError:
                talk("sorry, I couldn't catch that")
                continue
            except sr.RequestError as e:
                display_text("Could not request results from Google Speech Recognition service; {}".format(e))
                continue

            if "hi max" in sentence.lower():
                talk("How may I help you?")
                wakeup_word_spoken = True
            else:
                display_text("Please say 'hi max' to wake me up.")

            while wakeup_word_spoken:
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    display_text("Listening")
                    audio = r.listen(source)

                    try:
                        sentence = r.recognize_google(audio)
                        display_text("You said: " + sentence)
                    except sr.UnknownValueError:
                        talk("sorry, I couldn't catch that")
                        continue
                    except sr.RequestError as e:
                        display_text("Could not request results from Google Speech Recognition service; {}".format(e))
                        continue

                    if sentence == "stop":
                        talk("See you next time")
                        wakeup_word_spoken = False
                        break

                    sentence = tokenize(sentence)
                    X = bag_of_words(sentence, all_words)
                    X = X.reshape(1, X.shape[0])
                    X = torch.from_numpy(X).to(device)

                    output = model(X)
                    _, predicted = torch.max(output, dim=1)

                    tag = tags[predicted.item()]

                    probs = torch.softmax(output, dim=1)
                    prob = probs[0][predicted.item()]

                    if prob.item() > 0.75:
                        for intent in intents['intents']:
                            if tag == intent["tag"]:
                                if tag == 'play':
                                    song = ' '.join(sentence).replace('play', '').strip()
                                    display_text("{}: {} {}".format(bot_name, intent['responses'][0], song))
                                    pywhatkit.playonyt(song)
                                    talk("{} {}".format(intent['responses'][0], song))
                                elif 'time' in sentence:
                                    time = datetime.datetime.now().strftime('%I:%M %p')
                                    display_text("{}: Current time is {}".format(bot_name, time))
                                    talk('Current time is ' + time)
                                elif tag == 'day':
                                    day = datetime.datetime.now().strftime('%A')
                                    display_text("{}: Today is {}".format(bot_name, day))
                                    talk('Today is ' + day)
                                elif tag == 'whois':
                                    query = ' '.join(sentence)
                                    url = f"https://www.google.com/search?q={query}"
                                    webbrowser.open(url)
                                    talk("Here's what I found for {}".format(query))
                                elif tag == 'weather':
                                    query = ' '.join(sentence)
                                    url = f"https://www.google.com/search?q={query}"
                                    webbrowser.open(url)
                                    talk("Here's the weather report for {}".format(query))
                                elif tag.lower() == 'search':
                                    query = ' '.join(sentence)
                                    query = query.replace("search ", "")
                                    url = f"https://www.google.com/search?q={query}"
                                    webbrowser.open(url)
                                    talk("Let me look it up for you: {}".format(query))
                                elif tag == 'emergency':
                                    talk("Let me help")
                                    open_whatsapp()
                                else:
                                    response = random.choice(intent['responses'])
                                    talk(response)

                    else:
                        talk("I do not understand")

            start_listening()


listen_thread = threading.Thread(target=start_listening)
listen_thread.daemon = True
listen_thread.start()

root.mainloop()
