import os

from googleapiclient.discovery import build

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CX_ID = os.getenv("CX_ID")


service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)

result = service.cse().list(
    q="cat",
    cx=CX_ID,
    searchType="image"
).execute()

print([item["link"] for item in result.get("items", [])])

