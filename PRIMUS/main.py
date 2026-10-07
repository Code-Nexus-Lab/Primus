from dotenv import load_dotenv
from groq import Groq
import os
import json 

load_dotenv()
client = Groq()

MODEL = "openai/gpt-oss-120b"

SYSTEM = (
    "You are PRIMUS, a friendly desktop copilot for a streamer. "
    "Use your tools to control Spotify, OBS and apps on the user's PC. "
    "Keep replies short."
)

_sp = None

def spotify():
    global _sp
    if _sp is None:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
        _sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                 scope="user-modify-playback-state user-read-playback-state"
                 )
            )
        return _sp
    
def spotify_play(query: str):
    results= spotify().search(q=query, type="track", limit=1)
    items = results["tracks"]["items"]
    if not items:
        return f"No track found for '{query}'."
    track = items[0]
    spotify().start_playback(uris=[track["uri"]])
    return f"Playing {track['name']} by {track['artists'][0]['name']}" 

NEED_CONFIRM = {"obs_stream", "open_app"}
FUNCTIONS = {
    "spotify_play": spotify_play,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "spotify_play",
            "description": " Search Spotify for a song and play it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string","description": "Song and/or artist name"}
                },
                "required": ["query"],
            },
         },
    },
]
def run_tool(name: str, args: dict) -> str:
    if name not in FUNCTIONS:
        return f"Unknown tool: {name}"
    if name in NEED_CONFIRM:
        ok = input(f" ! Run {name}({args})? [y/N]").strip().lower()
        if ok != "y":
            return "User declined this action."
    try:
        result = FUNCTIONS[name](**args)
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"Tool error: {e}"
    
def ask(messages):
    while True:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM}] + messages,
            tools=TOOLS,
            tool_choice="auto",  
        )
        msg = resp.choices[0].message
        
        entry = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            entry["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
        messages.append(entry)
        
        if msg.content:
            print("primus:", msg.content)
        if not msg.tool_calls:
            return
        
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments or "{}")
            print("  ->", tc.function.name,args)
            result = run_tool(tc.function.name, args)
            messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": result}
            )
            
def main():
    messages = []
    print("Primus ready. Type 'quit' to exit.")
    while True:
        text = input("\nYou: ").strip()
        if text.lower() in ("quit", "exit"):
            break
        if not text:
            continue
        messages.append({"role": "user", "content": text})
        ask(messages)
        
if __name__ == "__main__":
    main()         