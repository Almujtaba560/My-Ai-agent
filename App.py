import gradio as gr
import edge_tts
import asyncio
from moviepy.editor import ColorClip, AudioFileClip

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

    voice = VOICES[voice_name]
    asyncio.run(make_voice(text, voice))

    audio = AudioFileClip("voice.mp3")
    duration = audio.duration

    video = ColorClip(
        size=(1280, 720),
        color=(20, 20, 20),
        duration=duration
    )

    video = video.set_audio(audio)

    output = "video.mp4"

    video.write_videofile(
        output,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    video.close()
    audio.close()

    return output

demo = gr.Interface(
    fn=create_video,
    inputs=[
        gr.Textbox(
            label="Write your text",
            lines=8,
            placeholder="Write your story here..."
        ),
        gr.Dropdown(
            choices=list(VOICES.keys()),
            value="English Female",
            label="Choose Voice"
        )
    ],
    outputs=gr.Video(label="Generated Video"),
    title="AI Text to Video Agent",
    description="Text → Voice → MP4 Video"
)

demo.launch(share=True)
