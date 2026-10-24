import speech_recognition as sr
import webbrowser
import sys
import subprocess
import re
import os
from dotenv import load_dotenv
from difflib import SequenceMatcher
import musicLibrery
import json
from urllib.error import URLError
from urllib.request import urlopen

import pyaudiowpatch as pyaudio

load_dotenv()

# SpeechRecognition imports the PyAudio module by this name when opening a mic.
sys.modules["pyaudio"] = pyaudio

recognizer = sr.Recognizer()

newsapi = os.getenv("NEWSAPI_KEY")

# Short pauses end an utterance; a longer phrase limit gives normal speech time.
recognizer.pause_threshold = 0.6
recognizer.non_speaking_duration = 0.4
recognizer.dynamic_energy_threshold = True
recognizer.operation_timeout = 5

def heard_wake_word(transcript):
    # Speech recognition may render the same spoken name as "Jervis" or "Jarvish".
    wake_word_variants = {"jarvis", "jervis", "jarvish"}
    words = re.findall(r"[a-z]+", transcript.casefold())
    return any(
        word in wake_word_variants
        or (len(word) >= 5 and SequenceMatcher(None, word, "jarvis").ratio() >= 0.82)
        for word in words
    )

def speak(text):
    # Use Windows' built-in SAPI voice directly instead of the pyttsx3 wrapper.
    safe_text = text.replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$voice.Volume = 100; $voice.Speak('" + safe_text + "'); "
        "$voice.Dispose()"
    )
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

def processCommand(c):
    if "open google" in c.lower():
        speak("Opening Google.")
        webbrowser.open("https://www.google.com")
    elif "open youtube" in c.lower():
        speak("Opening YouTube.")
        webbrowser.open("https://www.youtube.com")
    elif "open github" in c.lower():
        speak("Opening GitHub.")
        webbrowser.open("https://www.github.com")
    elif "open facebook" in c.lower():
        speak("Opening Facebook.")
        webbrowser.open("https://www.facebook.com")
    elif "open linkedin" in c.lower():
        speak("Opening LinkedIn.")
        webbrowser.open("https://www.linkedin.com")
    elif c.lower().startswith("play"):
        song = c[len("play"):].strip()
        normalized_song = re.sub(r"[^a-z0-9 ]", "", song.casefold())
        song_words = set(normalized_song.split())
        matches = [
            (title, url)
            for title, url in musicLibrery.music.items()
            if title.casefold() == normalized_song
            or title.casefold() in song_words
        ]
        if len(matches) == 1:
            title, link = matches[0]
            speak(f"Playing {title}.")
            webbrowser.open_new_tab(link)
        elif len(matches) > 1:
            titles = " or ".join(title for title, _ in matches)
            speak(f"I found more than one match. Please say play {titles}.")
        else:
            speak(f"I don't have {song} in my music list yet.")

    elif "news" in c.lower():
        if not newsapi:
            speak("News is not configured. Enter your News API key in the NEWSAPI_KEY environment variable.")
            return
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}"
        try:
            with urlopen(url, timeout=5) as response:
                data = json.load(response)
            titles = [
                article["title"]
                for article in data.get("articles", [])
                if article.get("title")
            ]
            if data.get("status") == "ok" and titles:
                speak("Here are the top headlines. " + ". ".join(titles[:3]))
            else:
                speak("I couldn't find any headlines right now.")
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            print(f"Could not fetch news: {error}")
            speak("I couldn't reach the news service.")

    else:
        speak("I don't know how to do that yet.")




if __name__ == "__main__":
    speak("Jarvis is online. Say Jarvis when you need me.")
    try:
        with sr.Microphone() as source:
            # Calibrate once so each listening cycle can start right away.
            print("Calibrating microphone...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening for Jarvis...")

            while True:
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    transcript = recognizer.recognize_google(audio, language="en-IN")
                    print(f"Heard: {transcript}")

                    if heard_wake_word(transcript):
                        print("Wake word detected: Jarvis.")
                        speak("I'm listening.")
                        print("Listening for command...")
                        try:
                            audio = recognizer.listen(source, timeout=8, phrase_time_limit=8)
                            command = recognizer.recognize_google(audio, language="en-IN")
                        except sr.UnknownValueError:
                            print("I couldn't understand the command. Please try again.")
                            speak("Sorry, I didn't catch that command.")
                            continue
                        print(f"Heard: {command}")
                        processCommand(command)

                except sr.UnknownValueError:
                    # Ignore audio that doesn't transcribe while waiting for the wake word.
                    continue
                except sr.WaitTimeoutError:
                    # No speech started before the timeout; return to wake-word listening.
                    continue
                except sr.RequestError as e:
                    print(f"Speech recognition service error: {e}")
                except KeyboardInterrupt:
                    print("\nJarvis stopped.")
                    break
    except OSError as e:
        print(f"Microphone error: {e}")

