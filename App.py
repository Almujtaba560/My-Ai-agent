import gradio as gr
import edge_tts
import asyncio

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
    output = "voice.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output)
    return output

def create_voice(text, voice_name):
    if not text.strip():
        return None

    voice = VOICES[voice_name]
    asyncio.run(make_voice(text, voice))
    return "voice.mp3"

demo = gr.Interface(
    fn=create_voice,
    inputs=[
        gr.Textbox(
            label="Write your text",
            lines=8,
            placeholder="Write your story here..."
        ),
        gr.Dropdown(
            choices=list(VOICES.keys()),
            value="🇺🇸 English - Female",
            label="Choose Voice"
        )
    ],
    outputs=gr.Audio(label="Generated Voice"),
    title="🎬 AI Text to Voice Agent",
    description="Choose a voice and convert your text to speech."
)

demo.launch(share=True)
