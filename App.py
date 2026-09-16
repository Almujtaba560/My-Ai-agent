import gradio as gr
import edge_tts
import asyncio
from moviepy.editor import ColorClip, AudioFileClip

VOICES = {
    "🇺🇸 English - Female": "en-US-AriaNeural",
    "🇺🇸 English - Male": "en-US-GuyNeural",
    "🇬🇧 British English - Female": "en-GB-SoniaNeural",
    "🇬🇧 British English - Male": "en-GB-RyanNeural",
    "🇸🇦 Arabic - Female": "ar-SA-ZariyahNeural",
    "🇸🇦 Arabic - Male": "ar-SA-HamedNeural",
    "🇪🇬 Arabic Egyptian - Female": "ar-EG-SalmaNeural",
}

async def make_voice(text, voice):
    await edge_tts.Communicate(text, voice).save("voice.mp3")

def create_video(text, voice_name):
    if not text.strip():
        return None

    voice = VOICES[voice_name]

    asyncio.run(make_voice
