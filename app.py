from flask import Flask, jsonify
from googleapiclient.discovery import build

API_KEY = "AIzaSyBDmDnQoT-1CAkqZBCco_wjSdBxV1h8uwc"
CX_ID = "4229dc2e694714f1f"

app = Flask(__name__)

@app.route("/search/<query>")
def search_images(query):
    service = build("customsearch", "v1", developerKey=API_KEY)
    results = service.cse().list(q=query, cx=CX_ID, searchType="image", num=4).execute()

    image_urls = [item["link"] for item in results.get("items", [])]
    return jsonify(image_urls)

if __name__ == "__main__":
    app.run(debug=True)
