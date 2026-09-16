import gradio as gr
import edge_tts
import asyncio
import requests
import os
import urllib.parse
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

VOICES = {
    "English Female": "en-US-AriaNeural",
    "English Male": "en-US-GuyNeural",
    "British Female": "en-GB-SoniaNeural",
    "British Male": "en-GB-RyanNeural",
    "Arabic Female": "ar-SA-ZariyahNeural",
    "Arabic Male": "ar-SA-HamedNeural",
}

async def make_voice(text, voice):
    communicator = edge_tts.Communicate(text, voice)
    await communicator.save("voice.mp3")


def create_video(text, voice_name):

    if not text.strip():
        return None

    # تقسيم النص إلى مشاهد
    sentences = [x.strip() for x in text.split(".") if x.strip()]

    if not sentences:
        sentences = [text]

    # الصوت
    voice = VOICES[voice_name]
    asyncio.run(make_voice(text, voice))

    audio = AudioFileClip("voice.mp3")

    scene_files = []

    # إنشاء صورة لكل مشهد
    for i, sentence in enumerate(sentences[:8]):

        prompt = urllib.parse.quote(
            "cinematic scene, realistic, beautiful, detailed, "
            + sentence
        )

        url = (
            "https://gen.pollinations.ai/image/"
            + prompt
            + "?model=flux&width=1280&height=720"
        )

        filename = f"scene_{i}.jpg"

        response = requests.get(url, timeout=120)

        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)

            scene_files.append(filename)

    if not scene_files:
        return None

    #
