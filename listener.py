import speech_recognition as sr
import time
from googleapiclient.discovery import build
API_KEY = "AIzaSyBDmDnQoT-1CAkqZBCco_wjSdBxV1h8uwc"
CX_ID = "4229dc2e694714f1f"

recognizer = sr.Recognizer()
mic = sr.Microphone()

def search_images(query):
    print(f"\n🔍 Searching images for: {query}")
    service = build("customsearch", "v1", developerKey=API_KEY)
    results = service.cse().list(q=query, cx=CX_ID, searchType="image", num=3).execute()

    image_items = results.get("items", [])
    if not image_items:
        print("⚠️ No images found.")
        return

    print("\n🖼️ Top 3 image results:")
    for i, item in enumerate(image_items, start=1):
        print(f"{i}. {item['title']}")
        print(f"   {item['link']}")
    print("\n👂 Listening again...")

def listen_loop():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎤 Voice agent ON — speak freely...")

        while True:
            print("👂 Listening...")
            audio = recognizer.listen(source)
            print("⏳ Processing speech...")

            try:
                text = recognizer.recognize_google(audio)
                print(f"👤 You said: {text}")
                search_images(text)
            except sr.UnknownValueError:
                print("❌ Couldn't understand. Listening again...")
            except Exception as e:
                print(f"⚠️ Error: {e}")

            time.sleep(1)

if __name__ == "__main__":
    listen_loop()