# popup.py
import sys
import tkinter as tk
from PIL import Image, ImageTk
import base64
from io import BytesIO
import traceback

def show_image(base64_data):
    try:
        img_bytes = base64.b64decode(base64_data)
        img = Image.open(BytesIO(img_bytes)).convert("RGBA")
        # resize to reasonable preview
        w, h = img.size
        max_size = 360
        scale = min(max_size / max(w, h), 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        # position bottom-right
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = screen_w - new_w - 30
        y = screen_h - new_h - 70
        root.geometry(f"{new_w}x{new_h}+{x}+{y}")
        tk_img = ImageTk.PhotoImage(img)
        lbl = tk.Label(root, image=tk_img, bd=0)
        lbl.pack()
        root.after(10000, root.destroy)  # close after 10s
        root.mainloop()
    except Exception as e:
        print("⚠️ popup error:", e)
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No image data provided")
    else:
        show_image(sys.argv[1])
