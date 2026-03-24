import speech_recognition as sr 
import requests
from PIL import Image, ImageTk
import io
import tkinter as tk
import threading
import spacy
from googleapiclient.discovery import build
import time
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv(".env")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def rewrite_query(user_text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Rewrite the user's text into a short, precise image search query. Focus on meaning. Avoid long sentences."
            },
            {
                "role": "user",
                "content": user_text
            }
        ],
        max_tokens=20
    )
    refined = response.choices[0].message.content.strip()
    return refined


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CX_ID = os.getenv("CX_ID")

# ------------------ NLP Setup ------------------
nlp = spacy.load("en_core_web_sm")

def extract_keywords(sentence):
    doc = nlp(sentence)

    nouns = [t.text for t in doc if t.pos_ in ["NOUN", "PROPN"]]

    if not nouns:
        return sentence.lower()

    return " ".join(nouns[:3])




# ------------------ GOOGLE SEARCH (from 2nd code) ------------------
def google_fetch_urls(query):
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        results = service.cse().list(
            q=f"{query} high quality realistic photo",
            cx=CX_ID,
            searchType="image",
            num=5,
            safe="active"
        ).execute()

        urls = [item["link"] for item in results.get("items", [])]
        return urls

    except Exception as e:
        print("⚠️ Google search error:", e)
        return []


# ------------------ DOWNLOAD AND VALIDATE IMAGE ------------------
def get_valid_image(urls):
    for url in urls:
        try:
            img_res = requests.get(url, timeout=6)

            if "image" not in img_res.headers.get("Content-Type", ""):
                continue

            img = Image.open(io.BytesIO(img_res.content))
            w, h = img.size

            if w < 300 or h < 200:
                continue
            if "logo" in url.lower() or "icon" in url.lower():
                continue

            return img_res.content

        except:
            continue

    return None


# ------------------ POPUP ------------------
def show_image_popup(image_bytes):
    def run():
        try:
            img = Image.open(io.BytesIO(image_bytes))
        except:
            print("⚠️ Invalid image")
            return

        img.thumbnail((500, 500))
        w, h = img.size

        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        root.configure(bg="black")

        tk_img = ImageTk.PhotoImage(img)
        label = tk.Label(root, image=tk_img, bg="black")
        label.image = tk_img
        label.pack()

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = sw - w - 20
        y = sh - h - 60
        root.geometry(f"{w}x{h}+{x}+{y}")

        root.after(8000, root.destroy)
        root.mainloop()

    threading.Thread(target=run, daemon=True).start()


# ------------------ MAIN LISTENER ------------------
def listen_and_fetch():
    r = sr.Recognizer()
    mic = sr.Microphone()

    print("\n🎤 Voice assistant active...\n")

    while True:
        with mic as source:
            r.adjust_for_ambient_noise(source)
            print("👂 Listening...")
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print(f"🗣️ You said: {text}")

            query = rewrite_query(text)
            print("🎯 Refined Query:", query)

            urls = google_fetch_urls(query)
            print("🔗 URLs found:", urls)

            img_bytes = get_valid_image(urls)

            if img_bytes:
                show_image_popup(img_bytes)
                print("🖼️ Image shown.")
            else:
                print("❌ No valid image found.")

        except sr.UnknownValueError:
            print("❌ Didn't catch that.")
        except Exception as e:
            print("⚠️ Error:", e)

        time.sleep(0.2)


if __name__ == "__main__":
    listen_and_fetch()
