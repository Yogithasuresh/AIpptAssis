from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/record", methods=["POST"])
def record():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files["audio"]
    file_path = "voice.wav"
    audio_file.save(file_path)

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)
        return jsonify({"text": text})

    except sr.UnknownValueError:
        return jsonify({"text": "Could not understand audio"})
    except Exception as e:
        return jsonify({"text": "Error: " + str(e)})

if __name__ == "__main__":
    app.run(debug=True)
