import speech_recognition as sr
import time
from googleapiclient.discovery import build

API_KEY = "ABC"
CX_ID = "CXX"

recognizer = sr.Recognizer()
mic = sr.Microphone()

def search_images(query):
    print(f"\n🔍 Searching images for: {query}")
    service = build("customsearch", "v1", developerKey=API_KEY)
    results = service.cse().list(q=query, cx=CX_ID, searchType="image", num=3).execute()
    
    image_urls = [item["link"] for item in results.get("items", [])]
    print("✅ Found image URLs:")
    for url in image_urls:
        print(url)
    print("👂 Listening again...\n")

def listen_loop():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎤 Voice agent ON — speak freely...")

        while True:
            audio = recognizer.listen(source, phrase_time_limit=None)  # wait for complete sentence

            print("⏳ Processing speech...")
            try:
                text = recognizer.recognize_google(audio)
                print(f"👤 You said: {text}")

                # You can add keyword filters later, for now search everything
                search_images(text)

            except sr.UnknownValueError:
                print("❌ Didn't catch that. Listening again...")
            except Exception as e:
                print(f"⚠️ Error: {e}")

            time.sleep(0.5)  # slight pause before listening again

if __name__ == "__main__":
    listen_loop()
