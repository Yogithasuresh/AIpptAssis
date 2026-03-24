import speech_recognition as sr 
import requests
from PIL import Image, ImageTk
import io
import tkinter as tk
import threading  # ← ADDED
import spacy
from googleapiclient.discovery import build
import time
import base64  # ← ADDED
from io import BytesIO  # ← ADDED
from openai import OpenAI  # ← CHANGED (use OpenAI instead of openai)
import sys
import traceback
import os
# Your OpenAI client (moved to top)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def rewrite_query(user_text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # ← FIXED model name
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

# ------------------ Keys ------------------
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

# ------------------ AI DESCRIPTION ← NEW! ------------------
def generate_description(img_bytes):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": [
                    {"type": "input_text", "text": "Describe this image in at least 25 words. Keep it simple and explain what the image represents."},
                    {"type": "input_image", "image_base64": base64.b64encode(img_bytes).decode()}
                ]}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Description error: {str(e)[:50]}...)"

# ------------------ GOOGLE SEARCH ------------------
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

# ------------------ DOWNLOAD IMAGE ------------------
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

# ------------------ FULL POPUP WITH DESCRIPTION ← UPGRADED! ------------------
def show_image_popup(image_bytes):
    def run():
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            
            # Resize (max 720px)
            w, h = img.size
            max_size = 720
            scale = min(max_size / max(w, h), 1.0)
            new_w, new_h = int(w * scale), int(h * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            
            # Popup window
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.configure(bg="black")
            
            # Bottom-right position
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            x = screen_w - new_w - 50
            y = screen_h - (new_h + 120)
            root.geometry(f"{new_w}x{new_h + 110}+{x}+{y}")
            
            # Image label
            tk_img = ImageTk.PhotoImage(img)
            img_label = tk.Label(root, image=tk_img, bg="black", bd=0)
            img_label.image = tk_img
            img_label.pack()
            
            # AI Description
            description = generate_description(image_bytes)
            desc_label = tk.Label(
                root,
                text=description,
                wraplength=new_w - 16,
                justify="left",
                bg="white",
                fg="black",
                padx=8,
                pady=6,
                font=("Arial", 10)
            )
            desc_label.pack(fill="both")
            
            # Auto-close 12s
            root.after(12000, root.destroy)
            root.mainloop()
            
        except Exception as e:
            print("⚠️ Popup error:", e)
            traceback.print_exc()
    
    threading.Thread(target=run, daemon=True).start()

# ------------------ MAIN VOICE LISTENER ------------------
def listen_and_fetch():
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("\n🎤 Voice assistant active (with AI descriptions!)...\n")
    
    while True:
        with mic as source:
            r.adjust_for_ambient_noise(source)
            print("👂 Listening...")
            audio = r.listen(source)
        
        try:
            text = r.recognize_google(audio)
            print(f"🗣️ You said: {text}")
            
            query = rewrite_query(text)
            print("🎯 Refined: ", query)
            
            urls = google_fetch_urls(query)
            print("🔗 URLs:", len(urls))
            
            img_bytes = get_valid_image(urls)
            
            if img_bytes:
                show_image_popup(img_bytes)
                print("🖼️✅ Image + AI Description shown!")
            else:
                print("❌ No valid image found.")
                
        except sr.UnknownValueError:
            print("❌ Didn't understand.")
        except Exception as e:
            print("⚠️ Error:", e)
        
        time.sleep(0.2)

if __name__ == "__main__":
    listen_and_fetch()
