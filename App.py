import gradio as gr
import edge_tts
import asyncio
import subprocess
import os

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

    asyncio.run(make_voice(text, VOICES[voice_name]))

    output = "AI_video.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-framerate", "2",
        "-f", "lavfi",
        "-i", "color=c=black:s=1280x720",
        "-i", "voice.mp3",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        output
    ]

    subprocess.run(command, check=True)

    return output


demo = gr.Interface(
    fn=create_video,
    inputs=[
        gr.Textbox(
            label="Write your story",
            lines=10,
            placeholder="Write your story here..."
        ),
        gr.Dropdown(
            choices=list(VOICES.keys()),
            value="English Female",
            label="Choose Voice"
        )
    ],
    outputs=gr.Video(label="Your AI Video"),

    title="AI Text to Video Agent",

    description="Text → Voice → MP4 Video"
)

demo.launch(share=True)
