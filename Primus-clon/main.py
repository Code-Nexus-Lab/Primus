from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
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