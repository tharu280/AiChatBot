import speech_recognition as sr

# Initialize the recognizer
r = sr.Recognizer()


def recognize_speech():
    with sr.Microphone() as source:
        print("Speak:")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print("You said:", text)
    except sr.UnknownValueError:
        print("Speech recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")


# Call the speech recognition function
recognize_speech()




