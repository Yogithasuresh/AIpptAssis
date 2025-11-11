import speech_recognition as sr
import requests
from PIL import Image, ImageTk, UnidentifiedImageError
import io
import tkinter as tk
import threading
import tempfile
import os

API_KEY = "AIzaSyBDmDnQoT-1CAkqZBCco_wjSdBxV1h8uwc"
CX = "4229dc2e694714f1f"

def fetch_image_data(query):
    """Fetch raw image bytes directly from a valid image URL."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "searchType": "image",
        "num": 5,
        "safe": "active"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        items = data.get("items", [])
        if not items:
            print("❌ No images found.")
            return None
        for item in items:
            img_url = item.get("link")
            if not img_url:
                continue
            try:
                img_res = requests.get(img_url, timeout=8)
                img_res.raise_for_status()
                if "image" in img_res.headers.get("Content-Type", ""):
                    return img_res.content  # return actual image bytes
            except Exception:
                continue
        return None
    except Exception as e:
        print(f"⚠️ Error fetching image: {e}")
        return None

def show_image_overlay(image_bytes):
    """Display the downloaded image as an always-on-top overlay for 10 seconds."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((350, 350))

        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.configure(bg="white")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = screen_width - 380
        y = screen_height - 420
        root.geometry(f"360x360+{x}+{y}")

        tk_img = ImageTk.PhotoImage(img)
        label = tk.Label(root, image=tk_img, bg="white", borderwidth=5, relief="ridge")
        label.pack(fill="both", expand=True)

        root.after(10000, root.destroy)
        root.mainloop()
    except UnidentifiedImageError:
        print("❌ Invalid image format received.")
    except Exception as e:
        print(f"⚠️ Image display failed: {e}")

def voice_listener():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("\n🎤 Speak what image you want:")
            audio = recognizer.listen(source)
        try:
            print("⏳ Recognizing speech...")
            query = recognizer.recognize_google(audio)
            print(f"✅ You said: {query}")
            image_bytes = fetch_image_data(query)
            if image_bytes:
                threading.Thread(target=show_image_overlay, args=(image_bytes,), daemon=True).start()
            else:
                print("❌ Couldn’t find a valid image.")
        except sr.UnknownValueError:
            print("❌ Couldn’t understand audio.")
        except sr.RequestError as e:
            print(f"⚠️ Speech recognition error: {e}")

if __name__ == "__main__":
    voice_listener()
