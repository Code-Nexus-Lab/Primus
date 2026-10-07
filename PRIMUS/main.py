from dotenv import load_dotenv
from groq import Groq

load_dotenv()
import os

client = Groq()

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hi"}],
)
print(response.choices[0].message.content)

_sp = None

def spotify():
    global _sp
    if _sp is None:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
        _sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="..."))
        return _sp
    
def spotify_play(query: str):
    results= spotify().search(q=query, type="track", limit=1)
    items = results["tracks"]["items"]
    if not items:
        return f"No track found for '{query}'."
    track = items[0]
    spotify().start_playback(uris=[track["uri"]])
    return f"Playing {track['name']} by {track['artists'][0]['name']}" 

