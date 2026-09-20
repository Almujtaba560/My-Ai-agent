import gradio as gr
import edge_tts
import asyncio
import subprocess
import os
import shutil
from google import genai
from google.genai import types


# =========================================================
# SETTINGS
# =========================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Please add your Gemini API key in Colab first."
    )

client = genai.Client(api_key=GEMINI_API_KEY)

TEXT_MODEL = "gemini-3.6-flash"
IMAGE_MODEL = "gemini-2.5-flash-image"


VOICES = {
    "English Female": "en-US-AriaNeural",
    "English Male": "en-US-GuyNeural",
    "British Female": "en-GB-SoniaNeural",
    "British Male": "en-GB-RyanNeural",
    "Arabic Female": "ar-SA-ZariyahNeural",
    "Arabic Male": "ar-SA-HamedNeural",
}


# =========================================================
# FOLDERS
# =========================================================

WORK_DIR = "extro_output"

if os.path.exists(WORK_DIR):
    shutil.rmtree(WORK_DIR)

os.makedirs(WORK_DIR, exist_ok=True)


# =========================================================
# GEMINI - CREATE SCENES
# =========================================================

def create_scenes(story):

    prompt = f"""
You are a professional cinematic story director.

Convert the following story into exactly 6 visual scenes.

Story:
{story}

Return ONLY the 6 scenes.

Format:

SCENE 1:
Narration: ...

Image Prompt: ...

SCENE 2:
Narration: ...

Image Prompt: ...

SCENE 3:
Narration: ...

Image Prompt: ...

SCENE 4:
Narration: ...

Image Prompt: ...

SCENE 5:
Narration: ...

Image Prompt: ...

SCENE 6:
Narration: ...

Image Prompt: ...

Make the image prompts cinematic and detailed.

Keep the main characters visually consistent between scenes.
Describe characters, clothing, environment, lighting and camera style.
Do not include text or subtitles inside the generated images.
"""

    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=prompt
    )

    return response.text


# =========================================================
# PARSE SCENES
# =========================================================

def parse_scenes(text):

    scenes = []

    blocks = text.split("SCENE ")

    for block in blocks:

        if not block.strip():
            continue

        narration = ""
        image_prompt = ""

        if "Narration:" in block:
            narration_part = block.split("Narration:", 1)[1]

            if "Image Prompt:" in narration_part:
                narration = narration_part.split(
                    "Image Prompt:", 1
                )[0].strip()

                image_prompt = narration_part.split(
                    "Image Prompt:", 1
                )[1].strip()

        if narration and image_prompt:

            scenes.append({
                "narration": narration,
                "image": image_prompt
            })

    return scenes[:6]


# =========================================================
# GEMINI - GENERATE IMAGE
# =========================================================

def generate_image(prompt, filename):

    full_prompt = f"""
Create a cinematic 16:9 image for a story.

{prompt}

Style:
cinematic animated movie,
high quality,
dramatic lighting,
detailed environment,
consistent character appearance,
professional composition,
16:9 landscape.

Do not add text, captions, logos or subtitles.
"""

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["Image"]
        )
    )

    for part in response.parts:

        if part.inline_data is not None:

            image = part.as_image()
            image.save(filename)

            return filename

    raise RuntimeError("Gemini did not return an image.")


# =========================================================
# TEXT TO SPEECH
# =========================================================

async def make_voice(text, voice, filename):

    communicator = edge_tts.Communicate(
        text,
        voice
    )

    await communicator.save(filename)


def create_voice(text, voice, filename):

    asyncio.run(
        make_voice(
            text,
            voice,
            filename
        )
    )


# =========================================================
# GET AUDIO DURATION
# =========================================================

def get_duration(filename):

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        filename
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )

    return float(result.stdout.strip())


# =========================================================
# CREATE VIDEO
# =========================================================

def build_video(image_files, audio_file, output_file):

    duration = get_duration(audio_file)

    scene_duration = duration / len(image_files)

    video_parts = []

    for i, image in enumerate(image_files):

        part_file = os.path.join(
            WORK_DIR,
            f"scene_{i}_video.mp4"
        )

        command = [
            "ffmpeg",
            "-y",

            "-loop",
            "1",

            "-i",
            image,

            "-t",
            str(scene_duration),

            "-vf",
            "scale=1280:720:force_original_aspect_ratio=decrease,"
            "pad=1280:720:(ow-iw)/2:(oh-ih)/2",

            "-r",
            "30",

            "-c:v",
            "libx264",

            "-preset",
            "veryfast",

            "-pix_fmt",
            "yuv420p",

            part_file
        ]

        subprocess.run(
            command,
            check=True
        )

        video_parts.append(part_file)

    concat_file = os.path.join(
        WORK_DIR,
        "concat.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as f:

        for video in video_parts:

            f.write(
                f"file '{os.path.abspath(video)}'\n"
            )

    silent_video = os.path.join(
        WORK_DIR,
        "silent_video.mp4"
    )

    command = [
        "ffmpeg",
        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        concat_file,

        "-c",
        "copy",

        silent_video
    ]

    subprocess.run(
        command,
        check=True
    )

    command = [
        "ffmpeg",
        "-y",

        "-i",
        silent_video,

        "-i",
        audio_file,

        "-c:v",
        "copy",

        "-c:a",
        "aac",

        "-shortest",

        output_file
    ]

    subprocess.run(
        command,
        check=True
    )

    return output_file


# =========================================================
# MAIN EXTRO AGENT
# =========================================================

def create_video(story, voice_name):

    if not story or not story.strip():

        raise gr.Error(
            "Please write your story first."
        )

    if voice_name not in VOICES:

        raise gr.Error(
            "Please choose a voice."
        )

    # Clean previous files

    if os.path.exists(WORK_DIR):

        shutil.rmtree(WORK_DIR)

    os.makedirs(
        WORK_DIR,
        exist_ok=True
    )

    # -----------------------------------------------------
    # STEP 1 - CREATE SCENES
    # -----------------------------------------------------

    scene_text = create_scenes(
        story
    )

    scenes = parse_scenes(
        scene_text
    )

    if len(scenes) == 0:

        raise gr.Error(
            "Extro could not create scenes."
        )

    # -----------------------------------------------------
    # STEP 2 - CREATE NARRATION
    # -----------------------------------------------------

    narration = "\n\n".join(
        scene["narration"]
        for scene in scenes
    )

    audio_file = os.path.join(
        WORK_DIR,
        "voice.mp3"
    )

    create_voice(
        narration,
        VOICES[voice_name],
        audio_file
    )

    # -----------------------------------------------------
    # STEP 3 - CREATE IMAGES
    # -----------------------------------------------------

    image_files = []

    for i, scene in enumerate(scenes):

        image_file = os.path.join(
            WORK_DIR,
            f"scene_{i + 1}.png"
        )

        generate_image(
            scene["image"],
            image_file
        )

        image_files.append(
            image_file
        )

    # -----------------------------------------------------
    # STEP 4 - CREATE FINAL VIDEO
    # -----------------------------------------------------

    output_file = os.path.join(
        WORK_DIR,
        "Extro_AI_Video.mp4"
    )

    build_video(
        image_files,
        audio_file,
        output_file
    )

    return output_file


# =========================================================
# GRADIO INTERFACE
# =========================================================

demo = gr.Interface(

    fn=create_video,

    inputs=[

        gr.Textbox(
            label="Write your story",
            lines=12,
            placeholder=(
                "Write your story here..."
            )
        ),

        gr.Dropdown(
            choices=list(
                VOICES.keys()
            ),

            value="English Female",

            label="Choose Voice"
        )
    ],

    outputs=gr.Video(
        label="Your Extro AI Video"
    ),

    title="Extro AI Agent",

    description=(
        "Story → AI Scenes → AI Images → "
        "Voice → MP4 Video"
    )
)


# =========================================================
# START EXTRO
# =========================================================

demo.launch(
    share=True
    )
