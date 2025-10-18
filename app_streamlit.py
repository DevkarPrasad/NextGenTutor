import os
import json
import asyncio
import streamlit as st
from pathlib import Path

# Import the VideoGenerator class from the project's generate_video.py
from generate_video import VideoGenerator, LiteLLMWrapper
import importlib
import argparse

# Ensure the generate_video module has an `args` object (some CLI paths expect it).
# We create a minimal Namespace with only_render=False so the pipeline doesn't error.
_gv_mod = importlib.import_module('generate_video')
if not hasattr(_gv_mod, 'args'):
    _gv_mod.args = argparse.Namespace(only_render=False)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"


def list_available_theorems():
    theorems = []
    # scan data folders for json files and collect their keys
    for difficulty in DATA_DIR.iterdir():
        if difficulty.is_dir():
            for jf in difficulty.glob("*.json"):
                try:
                    obj = json.load(open(jf))
                    if isinstance(obj, list):
                        for t in obj:
                            theorems.append({"theorem": t.get("theorem"), "description": t.get("description"), "source": str(jf)})
                except Exception:
                    continue
    return theorems


def list_generated_topics():
    topics = []
    if OUTPUT_DIR.exists():
        for d in OUTPUT_DIR.iterdir():
            if d.is_dir():
                topics.append(d.name)
    return topics


def create_video_generator(model_name, helper_model, use_rag=False, use_visual_fix_code=False, verbose=False):
    planner_model = LiteLLMWrapper(
        model_name=model_name,
        temperature=0.7,
        print_cost=False,
        verbose=verbose,
        use_langfuse=False
    )
    helper = LiteLLMWrapper(
        model_name=helper_model if helper_model else model_name,
        temperature=0.7,
        print_cost=False,
        verbose=verbose,
        use_langfuse=False
    )
    scene_model = planner_model
    vg = VideoGenerator(
        planner_model=planner_model,
        scene_model=scene_model,
        helper_model=helper,
        output_dir=str(OUTPUT_DIR),
        verbose=verbose,
        use_rag=use_rag,
        use_visual_fix_code=use_visual_fix_code,
        use_context_learning=False,
        max_scene_concurrency=1
    )
    return vg


st.set_page_config(page_title="NextGen Tutor - Generator", layout="wide")

st.title("NextGen Tutor — STEM Video Generator")

# Load allowed models from src/utils/allowed_models.json (if present)
allowed_models = []
allowed_models_path = BASE_DIR / "src" / "utils" / "allowed_models.json"
if allowed_models_path.exists():
    try:
        with open(allowed_models_path, 'r', encoding='utf-8') as fh:
            jm = json.load(fh)
            allowed_models = jm.get('allowed_models', []) if isinstance(jm, dict) else []
    except Exception:
        allowed_models = []

with st.sidebar:
    st.header("Generation Options")
    if allowed_models:
        model_name = st.selectbox("Main model", options=allowed_models, index=0)
        helper_model_choice = st.selectbox("Helper model (choose 'Custom' to type)", options=["(none)"] + allowed_models)
        custom_model = st.text_input("Custom model override (optional)", value="")
        # Determine final helper model value
        if custom_model.strip():
            model_name = custom_model.strip()
            helper_model = custom_model.strip() if helper_model_choice == "(none)" else helper_model_choice
        else:
            helper_model = None if helper_model_choice == "(none)" else helper_model_choice
    else:
        model_name = st.text_input("Model name", value="gemini/gemini-2.0-flash-001")
        helper_model = st.text_input("Helper model (optional)", value="")

    use_rag = st.checkbox("Use RAG (chroma)", value=False)
    use_visual_fix = st.checkbox("Use visual fix code (VLM)", value=False)
    verbose = st.checkbox("Verbose logs", value=False)

st.markdown("## Choose a topic to generate")

theorems = list_available_theorems()
theorem_options = [t['theorem'] for t in theorems if t.get('theorem')]
selected = st.selectbox("Pick a topic from dataset (or enter custom)", ["-- custom --"] + theorem_options)

custom_topic = None
custom_description = None
if selected == "-- custom --":
    custom_topic = st.text_input("Custom topic/theorem title")
    custom_description = st.text_area("Description / context")
else:
    # find description
    match = next((t for t in theorems if t.get('theorem') == selected), None)
    if match:
        st.write("**Description (from dataset):**")
        st.write(match.get('description') or "")

if st.button("Generate video for selected topic"):
    topic = custom_topic if custom_topic else selected
    description = custom_description if custom_description else (match.get('description') if match else "")
    if not topic or not description:
        st.error("Provide both topic and description/context before generating.")
    else:
        st.info(f"Starting generation for: {topic}")
        vg = create_video_generator(model_name, helper_model, use_rag=use_rag, use_visual_fix_code=use_visual_fix, verbose=verbose)

        # Run generation asynchronously and stream logs
        async def run_generation():
            await vg.generate_video_pipeline(topic, description, max_retries=2, only_plan=False)
            vg.combine_videos(topic)

        with st.spinner("Running generation (this may take a long time)..."):
            try:
                asyncio.run(run_generation())
                st.success("Generation finished — check Output section below.")
            except Exception as e:
                st.exception(e)

st.markdown("## Output — Generated topics and videos")

topics = list_generated_topics()
sel_topic = st.selectbox("Select generated topic", ["-- none --"] + topics)
if sel_topic and sel_topic != "-- none --":
    topic_dir = OUTPUT_DIR / sel_topic
    combined = topic_dir / f"{sel_topic}_combined.mp4"
    st.write(f"Files in {topic_dir}:")
    all_files = list(topic_dir.rglob("*"))
    file_list = [str(p.relative_to(topic_dir)) for p in all_files]
    st.write(file_list)

    if combined.exists():
        st.video(str(combined))
    else:
        st.info("No combined video found yet for this topic. Showing available partial/scene videos below.")

        # Look specifically for main scene files. We prefer files named like:
        # - scene1.mp4, scene2.mp4, ... inside the topic root or scene folders
        # - <topic>_scene1.mp4 or similar patterns
        main_scene_files = []

        # helper to accept a candidate as a main scene file
        def is_main_scene_file(p: Path):
            name = p.name.lower()
            # skip files that contain 'partial', 'clip', 'part', or 'render_temp'
            bad_tokens = ('partial', 'clip', 'part', 'temp', 'render_temp', '_part')
            if any(tok in name for tok in bad_tokens):
                return False
            # accept names like scene1.mp4 or scene_1.mp4 or scene-1.mp4
            import re
            if re.search(r'scene[_\- ]?\d+\.mp4$', name):
                return True
            # accept topic_scene1.mp4 or topic-scene1.mp4
            if re.search(r'_?scene[_\- ]?\d+\.mp4$|scene[_\- ]?\d+\.mp4$', name):
                return True
            # accept files that start with 'scene' and are mp4
            if name.startswith('scene') and name.endswith('.mp4'):
                return True
            return False

        for p in topic_dir.rglob('*.mp4'):
            if p.name == combined.name:
                continue
            try:
                if is_main_scene_file(p):
                    # compute scene index if possible for sorting
                    import re
                    m = re.search(r'(?:scene[_\- ]?(\d+))', p.name.lower())
                    idx = int(m.group(1)) if m else 999
                    main_scene_files.append((idx, p))
            except Exception:
                continue

        main_scene_files.sort(key=lambda x: x[0])

        if not main_scene_files:
            st.info("No main scene files (e.g. scene1.mp4) found in the topic output folder.")
        else:
            for idx, vp in main_scene_files:
                caption = f"Scene {idx} — {vp.name}"
                st.markdown(f"**{caption}**")
                try:
                    st.video(str(vp))
                except Exception as e:
                    st.write(f"Cannot play {vp.name}: {e}")

st.markdown("---")
st.write("Notes: This UI starts the project's internal generation pipeline. Generating full videos requires model API keys and dependencies configured in your environment (see README). Use with caution: generation can consume a lot of compute and time.")
