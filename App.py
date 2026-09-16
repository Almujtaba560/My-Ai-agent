import gradio as gr
import edge_tts
import asyncio
import os

async def make_voice(text):
    output = "voice.mp3"
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output)
    return output

def create_video(text):
    if not text.strip():
        return None

    asyncio.run(make_voice(text))
    return "voice.mp3"

demo = gr.Interface(
    fn=create_video,
    inputs=gr.Textbox(
        label="Write your text",
        lines=8,
        placeholder="Write your story here..."
    ),
    outputs=gr.Audio(label="Generated Voice"),
    title="🎬 AI Text to Video Agent",
    description="Text → AI Voice"
)

demo.launch(share=True)
