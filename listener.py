import speech_recognition as sr
import requests
import io
from PIL import Image, ImageTk
import tkinter as tk
import threading
import re
import spacy
from collections import Counter
import webview
import threading
import time
import os
import time
from key_ext import extract_smart_keyword

# 🔑 Replace these with your actual Google API credentials
GOOGLE_API_KEY = "AIzaSyBDmDnQoT-1CAkqZBCco_wjSdBxV1h8uwc"
CX_ID = "4229dc2e694714f1f"

# ------------------ Keyword Extractor -----------------

nlp = spacy.load("en_core_web_sm")

def extract_keywords(sentence):
    """
    Extract the most meaningful nouns or noun phrases from a user sentence.
    Returns a clean keyword string for image search.
    """
    doc = nlp(sentence.lower())
    candidates = []

    for chunk in doc.noun_chunks:
        # Exclude pronouns, generic terms
        if not any(word.pos_ in ["PRON", "DET"] for word in chunk):
            candidates.append(chunk.text.strip())

    # fallback: if no chunk, pick nouns
    if not candidates:
        candidates = [token.text for token in doc if token.pos_ == "NOUN"]

    # pick the most frequent noun phrase
    if candidates:
        keyword = Counter(candidates).most_common(1)[0][0]
    else:
        keyword = sentence

    # clean up small/common words
    remove_words = {"image", "picture", "photo", "show", "display", "me"}
    words = [w for w in keyword.split() if w not in remove_words]
    return " ".join(words)


# ------------------ Image Fetcher ------------------
def fetch_image_data(query):
    """Fetch a single image using Google Custom Search API."""
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": CX_ID,
        "key": GOOGLE_API_KEY,
        "searchType": "image",
        "num": 3,   # get a few results to increase success chance
        "imgSize": "large"
    }

    response = requests.get(search_url, params=params)
    data = response.json()

    if "items" not in data or len(data["items"]) == 0:
        print("⚠️ No image found for:", query)
        return None

    # Try each link until one works
    for item in data["items"]:
        image_url = item["link"]
        try:
            resp = requests.get(image_url, timeout=5)
            if resp.status_code == 200 and resp.headers.get("Content-Type", "").startswith("image"):
                return io.BytesIO(resp.content)
        except Exception:
            continue

    print("⚠️ No valid image content found.")
    return None


def show_image_popup(image_bytes, title="AI Image"):
    """Display the fetched image as a popup at the bottom-right corner (thread-safe)."""
    def popup():
        try:
            img = Image.open(image_bytes)
        except Exception as e:
            print("⚠️ Image open failed:", e)
            return

        # Create Tk window first
        root = tk.Tk()
        root.title(title)
        root.attributes('-topmost', True)
        root.overrideredirect(True)

        # Position bottom-right
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 400
        window_height = 300
        x = screen_width - window_width - 40
        y = screen_height - window_height - 80
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Convert image before attaching to label
        img.thumbnail((400, 300))
        photo = ImageTk.PhotoImage(img)

        # Keep reference alive using an attribute on root
        label = tk.Label(root, image=photo, bg="black")
        label.image = photo  # <- prevents garbage collection
        label.pack(fill="both", expand=True)

        # Auto-close after 10s
        root.after(10000, root.destroy)
        root.mainloop()

    # Run Tk window in its own thread
    threading.Thread(target=popup, daemon=True).start()



# ------------------ Speech Recognition ------------------
def listen_and_fetch():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Voice assistant active — Speak to fetch images!\n")
    while True:
        with mic as source:
            print("👂 Listening (speak now)...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        print("⏳ Recognizing...")
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")

            keywords = extract_keywords(text)
            if not keywords:
                print("⚠️ No useful keywords found.")
                continue

            print(f"🎯 Extracted keywords: {keywords}")
            image_bytes = fetch_image_data(keywords)
            if image_bytes:
                show_image_popup(image_bytes, title=keywords.title())
                print(f"🖼️ Showing image for: {keywords}")
            else:
                print("⚠️ No image found.")

        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
        except Exception as e:
            print(f"⚠️ Error: {e}")
buffer = ""
last_time = time.time()

def handle_input(fragment):
    global buffer, last_time
    buffer += " " + fragment.strip()
    now = time.time()

    # Wait until user pauses for >1.2 seconds
    if now - last_time > 1.2:
        sentence = buffer.strip()
        buffer = ""
        if len(sentence.split()) >= 3:  # Only process full sentences
            try:
                keyword = extract_smart_keyword(sentence)
                print("🧠 Extracted keyword:", keyword)
                # show_popup(keyword)  # Your function
            except Exception as e:
                print("❌ Error:", e)
    last_time = now
# ------------------ Main ------------------
if __name__ == "__main__":
    listen_and_fetch()
