import streamlit as st
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import os
import uuid
import tempfile
import subprocess

# Manim scene template with placeholder text
MANIM_TEMPLATE = """
from manim import *

class TheoremScene(Scene):
    def construct(self):
        theorem = Text("{text}", font_size=48, color=WHITE)
        self.play(Write(theorem))
        self.wait(5)
"""

# Streamlit setup
st.set_page_config(page_title="Theorem Explain Agent + Manim")
st.title("🎥 Theorem Explain Agent with Manim Animation")

# Input
theorem_input = st.text_area("Enter a theorem or concept:")

@st.cache_resource
def load_llm():
    model_name = "tiiuae/falcon-rw-1b"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return pipeline("text-generation", model=model, tokenizer=tokenizer)

llm = load_llm()

def generate_manim_scene(text: str, scene_path: str):
    code = MANIM_TEMPLATE.format(text=text.replace('"', '\\"'))
    with open(scene_path, "w") as f:
        f.write(code)

def render_manim(scene_file: str, output_dir: str):
    # Run manim render command
    # -ql: low quality for speed, change to -qm or -qh for better quality
    cmd = [
        "manim",
        "-pql",
        scene_file,
        "TheoremScene",
        "--media_dir",
        output_dir
    ]
    subprocess.run(cmd, check=True)

if st.button("Generate Video"):
    if not theorem_input.strip():
        st.warning("Please enter a theorem or concept!")
    else:
        with st.spinner("Generating explanation text..."):
            result = llm(theorem_input, max_new_tokens=200, do_sample=True)[0]['generated_text']
            explanation = result.strip()

        st.text_area("Explanation:", value=explanation, height=150)

        with st.spinner("Generating audio..."):
            tts = gTTS(explanation)
            audio_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}_audio.mp3")
            tts.save(audio_path)

        with st.spinner("Generating Manim animation..."):
            # Prepare temp directory and file paths
            temp_dir = tempfile.mkdtemp()
            scene_file = os.path.join(temp_dir, "theorem_scene.py")
            generate_manim_scene(theorem_input, scene_file)
            
            try:
                render_manim(scene_file, temp_dir)
            except subprocess.CalledProcessError:
                st.error("Failed to render Manim animation. Make sure Manim is installed and ffmpeg is available.")
                st.stop()

            # The output video path
            manim_video_path = os.path.join(temp_dir, "media", "videos", "theorem_scene", "1080p30", "TheoremScene.mp4")

        with st.spinner("Combining audio and video..."):
            video_clip = VideoFileClip(manim_video_path)
            audio_clip = AudioFileClip(audio_path)
            final_video = video_clip.set_audio(audio_clip)

            output_video_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_final.mp4")
            final_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

        st.success("Video generated!")
        st.video(output_video_path)
