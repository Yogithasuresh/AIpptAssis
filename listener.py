import speech_recognition as sr
import time
from googleapiclient.discovery import build
import requests
import subprocess
import base64
import sys
import traceback

API_KEY = "AIzaSyBDmDnQoT-1CAkqZBCco_wjSdBxV1h8uwc"
CX_ID = "4229dc2e694714f1f"
IMAGE_TIMEOUT = 6          # seconds

def search_first_image_url(query):
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        resp = service.cse().list(q=query, cx=CX_ID, searchType="image", num=1).execute()
        items = resp.get("items")
        if not items:
            print("⚠️ Search returned no items. Response keys:", list(resp.keys()))
            return None
        return items[0].get("link")
    except Exception as e:
        print("⚠️ Error calling Custom Search API:", str(e))
        traceback.print_exc()
        return None

def fetch_image_base64(url):
    try:
        r = requests.get(url, timeout=IMAGE_TIMEOUT)
        if r.status_code == 200 and r.content:
            return base64.b64encode(r.content).decode("utf-8")
        else:
            print(f"⚠️ Image request status {r.status_code}")
            return None
    except Exception as e:
        print("⚠️ requests error fetching image:", e)
        return None

def spawn_popup_with_base64(b64):
    try:
        # call popup.py and pass base64 string as argument
        subprocess.Popen([sys.executable, "popup.py", b64], creationflags=0)
    except Exception as e:
        print("⚠️ Failed to spawn popup:", e)

def choose_mic_index():
    names = sr.Microphone.list_microphone_names()
    print("Available microphones:")
    for i, n in enumerate(names):
        print(i, n)
    # try default - if it fails, user can re-run after checking index
    return None

def main():
    mic_index = choose_mic_index()  # prints devices; set explicitly here if needed
    r = sr.Recognizer()
    try:
        with sr.Microphone(device_index=mic_index) as source:
            r.adjust_for_ambient_noise(source, duration=1)
            print("🎤 Voice assistant active — Speak to fetch images!")
            while True:
                try:
                    print("\n👂 Listening (speak now)...")
                    audio = r.listen(source, timeout=None, phrase_time_limit=8)
                    print("⏳ Recognizing...")
                    text = r.recognize_google(audio)
                    print(f"👤 You said: {text}")
                    # fetch image
                    url = search_first_image_url(text)
                    if not url:
                        print("❌ No image URL found for:", text)
                        continue
                    print("🔗 Image URL:", url)
                    b64 = fetch_image_base64(url)
                    if not b64:
                        print("⚠️ Failed to fetch image bytes, trying again once...")
                        b64 = fetch_image_base64(url)
                        if not b64:
                            print("❌ Could not fetch image bytes.")
                            continue
                    spawn_popup_with_base64(b64)
                except sr.UnknownValueError:
                    print("❌ Didn't catch that, say again.")
                except sr.RequestError as e:
                    print("⚠️ Speech recognition service error:", e)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping.")
                    break
                except Exception as e:
                    print("⚠️ Unexpected error in loop:", e)
                    traceback.print_exc()
                time.sleep(0.5)
    except Exception as e:
        print("⚠️ Could not open Microphone:", e)
        traceback.print_exc()
        print("Try running list_mics.py and set the device_index in code.")

if __name__ == "__main__":
    main()
