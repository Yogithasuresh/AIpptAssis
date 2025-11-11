import speech_recognition as sr
import time
from googleapiclient.discovery import build
import webbrowser
API_KEY = "REMOVEDSyBDmDnQoT-1CAkqZBCco_wjSdBxV1h8uwc"
CX_ID = "4229dc2e694714f1f"

recognizer = sr.Recognizer()
mic = sr.Microphone()

def search_images(query):
    print(f"\n🔍 Searching images for: {query}")
    service = build("customsearch", "v1", developerKey=API_KEY)
    results = service.cse().list(q=query, cx=CX_ID, searchType="image", num=3).execute()

    image_urls = [item["link"] for item in results.get("items", [])]

    if not image_urls:
        print("⚠️ No images found.")
        return

    # Create simple HTML file to display images
    html_content = "<html><head><title>Fetched Images</title></head><body>"
    html_content += f"<h3>Results for '{query}'</h3>"
    for url in image_urls:
        html_content += f'<img src="{url}" width="400" style="margin:10px;"><br>'
    html_content += "</body></html>"

    # Save and open automatically in browser
    file_path = "results.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    webbrowser.open(file_path)
    print("✅ Opened fetched images in browser.")

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