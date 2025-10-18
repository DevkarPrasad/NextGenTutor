# NexGenTutor

NexGenTutor is an enhanced multimodal video-generation pipeline with a polished Streamlit UI, richer model-selection and configuration controls, scene-level preview and playback logic, improved error handling and compatibility shims, developer-friendly run/debug tooling, and usability improvements for creating STEM explanatory videos (math, physics, chemistry, CS, etc.). It streamlines interactive workflows — from planning and RAG-enabled generation to rendering and evaluation — and packages core capabilities for easier local use and rapid iteration.
<img width="1919" height="1050" alt="image" src="https://github.com/user-attachments/assets/c0a9c1dd-5188-4fb7-857e-adaca8e17d3c" />



https://github.com/user-attachments/assets/1b035047-8015-4147-87f9-61e6c5e50b24



Key features:
- Select dataset theorems or provide a custom topic + description.
- Choose Main and Helper LLM models (populated from `src/utils/allowed_models.json` or custom string).
- Start the full generation pipeline (planning + rendering) from the UI.
- Preview combined topic video if present; otherwise preview main scene files only (scene1.mp4, scene2.mp4, ...).
- The UI injects a small compatibility shim (a CLI-like `args` namespace) when running the generator so no changes to `src/` are necessary.

## Downloading Generated Video Data
Skip this section if you just want to try out the code.
If you are researchers who just need the baseline videos as baseline comparison, download it here:
```shell
wget --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=18kmzXvbxaFGyJw-g51jnq9m93v_ez4aJ' -O /tmp/gdrive.html && wget --load-cookies /tmp/cookies.txt -O baseline_videos.zip "https://drive.usercontent.google.com/download?id=18kmzXvbxaFGyJw-g51jnq9m93v_ez4aJ&export=download&confirm=$(sed -rn 's/.*name="confirm" value="([^"]+)".*/\\1/p' /tmp/gdrive.html)&uuid=$(sed -rn 's/.*name="uuid" value="([^"]+)".*/\\1/p' /tmp/gdrive.html)" && rm /tmp/gdrive.html /tmp/cookies.txt
```

## Installation

> **Look at the [FAQ section in this README doc](https://github.com/CodewithAbhi7/NexGenTutor?tab=readme-ov-file#-faq) if you encountered any errors. If that didnt help, create a issue**<br>

1. Setting up conda environment
```shell
conda create --name tea python=3.12.8
conda activate tea
pip install -r requirements.txt
```

2. You may also need to install latex and other dependencies for Manim Community. Look at [Manim Installation Docs](https://docs.manim.community/en/stable/installation.html) for more details.
```shell
# You might need these dependencies if you are using Linux Ubuntu:
sudo apt-get install portaudio19-dev
sudo apt-get install libsdl-pango-dev
```

3. Then Download the Kokoro model and voices using the commands to enable TTS service.

```shell
mkdir -p models && wget -P models https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx && wget -P models https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin
```

4. Create `.env` based on `.env.template`, filling in the environmental variables according to the models you choose to use.
See [LiteLLM](https://docs.litellm.ai/docs/providers) for reference.

```shell
touch .env
```
Then open the `.env` file and edit it with whatever text editor you like.

Your `.env` file should look like the following:
```shell
# OpenAI
OPENAI_API_KEY=""

# Azure OpenAI
AZURE_API_KEY=""
AZURE_API_BASE=""
AZURE_API_VERSION=""

# Google Vertex AI
VERTEXAI_PROJECT=""
VERTEXAI_LOCATION=""
GOOGLE_APPLICATION_CREDENTIALS=""

# Google Gemini
GEMINI_API_KEY=""

...

# Kokoro TTS Settings
KOKORO_MODEL_PATH="models/kokoro-v0_19.onnx"
KOKORO_VOICES_PATH="models/voices.bin"
KOKORO_DEFAULT_VOICE="af"
KOKORO_DEFAULT_SPEED="1.0"
KOKORO_DEFAULT_LANG="en-us"
```
Fill in the API keys according to the model you wanted to use.

5. Configure Python path. Note that you need to configure the python path to make it work. Otherwise you may encounter import issues (like not being able to import src etc.)
```shell
export PYTHONPATH=$(pwd):$PYTHONPATH
```

6. (Optional) To setup RAG, See [https://github.com/CodewithAbhi7/NexGenTutor?tab=readme-ov-file#generation-with-rag](https://github.com/CodewithAbhi7/NexGenTutor?tab=readme-ov-file#generation-with-rag).

> **Look at the [FAQ section in this README doc](https://github.com/TIGER-AI-Lab/TheoremExplainAgent?tab=readme-ov-file#-faq) if you encountered any errors. If that didnt help, create a issue**<br>

## Generation

### Supported Models
<!--You can customize the allowed models by editing the `src/utils/allowed_models.json` file. This file specifies which `model` and `helper_model` the system is permitted to use.--> 
The model naming follows the LiteLLM convention. For details on how models should be named, please refer to the [LiteLLM documentation](https://docs.litellm.ai/docs/providers).

## NextGenTutor frontend — full integration notes

This section documents the NextGenTutor Streamlit frontend integration and how to use it alongside the TEA backend. The file `app_streamlit.py` included in this repository contains the complete UI integration. 
Key implementation notes:

- The Streamlit app loads allowed models from `src/utils/allowed_models.json` if present and populates Main and Helper model selectors in the sidebar. A custom model override is also supported.
- When triggering generation from the UI the app instantiates `VideoGenerator` with `LiteLLMWrapper` instances for planner/helper models and calls `generate_video_pipeline(...)` and `combine_videos(...)` where appropriate.
- The UI displays combined topic video if `<topic>_combined.mp4` exists; if not it searches for main scene MP4 files matching patterns like `scene1.mp4`, `scene_1.mp4`, or `<topic>_scene1.mp4` and displays those. Small partial clips are ignored.

### Run via frontend or CLI

NexGenTutor includes a Streamlit frontend that exposes almost all generation workflows — planning, RAG-enabled generation, rendering, and scene/video preview — so you can run and monitor experiments from your browser. Note: the frontend does not currently include the evaluation sub-workflow; use the CLI for evaluation or other advanced batch operations.

- To use the frontend (recommended for interactive testing and preview):
```powershell
python -m streamlit run app_streamlit.py --server.port 8501
```
- To run generation directly from the terminal (CLI examples):
Single-topic generation:
```shell
python generate_video.py \
      --model "openai/o3-mini" \
      --helper_model "openai/o3-mini" \
      --output_dir "output/your_exp_name" \
      --topic "your_topic" \
      --context "description of your topic, e.g. 'This is a topic about the properties of a triangle'" \
```

Example:
```shell
python generate_video.py \
      --model "openai/o3-mini" \
      --helper_model "openai/o3-mini" \
      --output_dir "output/my_exp_name" \
      --topic "Big O notation" \
      --context "most common type of asymptotic notation in computer science used to measure worst case complexity" \
```

### Generation (in batch)
```shell
python generate_video.py \
      --model "openai/o3-mini" \
      --helper_model "openai/o3-mini" \
      --output_dir "output/my_exp_name" \
      --theorems_path data/thb_easy/math.json \
      --max_scene_concurrency 7 \
      --max_topic_concurrency 20 \
```

### Generation with RAG
Before using RAG, download the RAG documentation from this [Google Drive link](https://drive.google.com/file/d/1Tn6J_JKVefFZRgZbjns93KLBtI9ullRv/view?usp=sharing). After downloading, unzip the file. For example, if you unzip it to `data/rag/manim_docs`, then you should set `--manim_docs_path` to `data/rag/manim_docs`. The vector database will be created the first time you run with RAG.

```shell
python generate_video.py \
            --model "openai/o3-mini" \
            --helper_model "openai/o3-mini" \
            --output_dir "output/with_rag/o3-mini/vtutorbench_easy/math" \
            --topic "Big O notation" \
            --context "most common type of asymptotic notation in computer science used to measure worst case complexity" \
            --use_rag \
            --chroma_db_path "data/rag/chroma_db" \
            --manim_docs_path "data/rag/manim_docs" \
            --embedding_model "vertex_ai/text-embedding-005"
```

We support more options for generation, see below for more details:
```shell
usage: generate_video.py [-h]
                         [--model]
                         [--topic TOPIC] [--context CONTEXT]
                         [--helper_model]
                         [--only_gen_vid] [--only_combine] [--peek_existing_videos] [--output_dir OUTPUT_DIR] [--theorems_path THEOREMS_PATH]
                         [--sample_size SAMPLE_SIZE] [--verbose] [--max_retries MAX_RETRIES] [--use_rag] [--use_visual_fix_code]
                         [--chroma_db_path CHROMA_DB_PATH] [--manim_docs_path MANIM_DOCS_PATH]
                         [--embedding_model {azure/text-embedding-3-large,vertex_ai/text-embedding-005}] [--use_context_learning]
                         [--context_learning_path CONTEXT_LEARNING_PATH] [--use_langfuse] [--max_scene_concurrency MAX_SCENE_CONCURRENCY]
                         [--max_topic_concurrency MAX_TOPIC_CONCURRENCY] [--debug_combine_topic DEBUG_COMBINE_TOPIC] [--only_plan] [--check_status]
                         [--only_render] [--scenes SCENES [SCENES ...]]

Generate Manim videos using AI

options:
  -h, --help            show this help message and exit
  --model               Select the AI model to use
  --topic TOPIC         Topic to generate videos for
  --context CONTEXT     Context of the topic
  --helper_model        Select the helper model to use
  --only_gen_vid        Only generate videos to existing plans
  --only_combine        Only combine videos
  --peek_existing_videos, --peek
                        Peek at existing videos
  --output_dir OUTPUT_DIR
                        Output directory
  --theorems_path THEOREMS_PATH
                        Path to theorems json file
  --sample_size SAMPLE_SIZE, --sample SAMPLE_SIZE
                        Number of theorems to sample
  --verbose             Print verbose output
  --max_retries MAX_RETRIES
                        Maximum number of retries for code generation
  --use_rag, --rag      Use Retrieval Augmented Generation
  --use_visual_fix_code, --visual_fix_code
                        Use VLM to fix code with rendered visuals
  --chroma_db_path CHROMA_DB_PATH
                        Path to Chroma DB
  --manim_docs_path MANIM_DOCS_PATH
                        Path to manim docs
  --embedding_model {azure/text-embedding-3-large,vertex_ai/text-embedding-005}
                        Select the embedding model to use
  --use_context_learning
                        Use context learning with example Manim code
  --context_learning_path CONTEXT_LEARNING_PATH
                        Path to context learning examples
  --use_langfuse        Enable Langfuse logging
  --max_scene_concurrency MAX_SCENE_CONCURRENCY
                        Maximum number of scenes to process concurrently
  --max_topic_concurrency MAX_TOPIC_CONCURRENCY
                        Maximum number of topics to process concurrently
  --debug_combine_topic DEBUG_COMBINE_TOPIC
                        Debug combine videos
  --only_plan           Only generate scene outline and implementation plans
  --check_status        Check planning and code status for all theorems
  --only_render         Only render scenes without combining videos
  --scenes SCENES [SCENES ...]
                        Specific scenes to process (if theorems_path is provided)
```

## Evaluation
Note that Gemini and GPT4o is required for evaluation.

Currently, evaluation requires a video file and a subtitle file (SRT format).

Video evaluation:
```shell
usage: evaluate.py [-h]
                   [--model_text {gemini/gemini-1.5-pro-002,gemini/gemini-1.5-flash-002,gemini/gemini-2.0-flash-001,vertex_ai/gemini-1.5-flash-002,vertex_ai/gemini-1.5-pro-002,vertex_ai/gemini-2.0-flash-001,openai/o3-mini,gpt-4o,azure/gpt-4o,azure/gpt-4o-mini,bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0,bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0,bedrock/anthropic.claude-3-5-haiku-20241022-v1:0,bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0}]
                   [--model_video {gemini/gemini-1.5-pro-002,gemini/gemini-2.0-flash-exp,gemini/gemini-2.0-pro-exp-02-05}]
                   [--model_image {gemini/gemini-1.5-pro-002,gemini/gemini-1.5-flash-002,gemini/gemini-2.0-flash-001,vertex_ai/gemini-1.5-flash-002,vertex_ai/gemini-1.5-pro-002,vertex_ai/gemini-2.0-flash-001,openai/o3-mini,gpt-4o,azure/gpt-4o,azure/gpt-4o-mini,bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0,bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0,bedrock/anthropic.claude-3-5-haiku-20241022-v1:0,bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0}]
                   [--eval_type {text,video,image,all}] --file_path FILE_PATH --output_folder OUTPUT_FOLDER [--retry_limit RETRY_LIMIT] [--combine] [--bulk_evaluate] [--target_fps TARGET_FPS]
                   [--use_parent_folder_as_topic] [--max_workers MAX_WORKERS]

Automatic evaluation of theorem explanation videos with LLMs

options:
  -h, --help            show this help message and exit
  --model_text {gemini/gemini-1.5-pro-002,gemini/gemini-1.5-flash-002,gemini/gemini-2.0-flash-001,vertex_ai/gemini-1.5-flash-002,vertex_ai/gemini-1.5-pro-002,vertex_ai/gemini-2.0-flash-001,openai/o3-mini,gpt-4o,azure/gpt-4o,azure/gpt-4o-mini,bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0,bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0,bedrock/anthropic.claude-3-5-haiku-20241022-v1:0,bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0}
                        Select the AI model to use for text evaluation
  --model_video {gemini/gemini-1.5-pro-002,gemini/gemini-2.0-flash-exp,gemini/gemini-2.0-pro-exp-02-05}
                        Select the AI model to use for video evaluation
  --model_image {gemini/gemini-1.5-pro-002,gemini/gemini-1.5-flash-002,gemini/gemini-2.0-flash-001,vertex_ai/gemini-1.5-flash-002,vertex_ai/gemini-1.5-pro-002,vertex_ai/gemini-2.0-flash-001,openai/o3-mini,gpt-4o,azure/gpt-4o,azure/gpt-4o-mini,bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0,bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0,bedrock/anthropic.claude-3-5-haiku-20241022-v1:0,bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0}
                        Select the AI model to use for image evaluation
  --eval_type {text,video,image,all}
                        Type of evaluation to perform
  --file_path FILE_PATH
                        Path to a file or a theorem folder
  --output_folder OUTPUT_FOLDER
                        Directory to store the evaluation files
  --retry_limit RETRY_LIMIT
                        Number of retry attempts for each inference
  --combine             Combine all results into a single JSON file
  --bulk_evaluate       Evaluate a folder of theorems together
  --target_fps TARGET_FPS
                        Target FPS for video processing. If not set, original video FPS will be used
  --use_parent_folder_as_topic
                        Use parent folder name as topic name for single file evaluation
  --max_workers MAX_WORKERS
                        Maximum number of concurrent workers for parallel processing
```
* For `file_path`, it is recommended to pass a folder containing both an MP4 file and an SRT file.

## Misc: Modify the system prompt in TheoremExplainAgent

If you want to modify the system prompt, you need to:

1. Modify files in `task_generator/prompts_raw` folder.
2. Run `task_generator/parse_prompt.py` to rebuild the `__init__.py` file.

```python
cd task_generator
python parse_prompt.py
cd ..
```

## ❓ FAQ

The FAQ should cover the most common errors you could encounter. If you see something new, report it on issues.

Q: Error `src.utils.kokoro_voiceover import KokoroService  # You MUST import like this as this is our custom voiceover service. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ModuleNotFoundError: No module named 'src'`. <br>
A: Please run `export PYTHONPATH=$(pwd):$PYTHONPATH` when you start a new terminal. <br>

Q: Error `Files not found` <br>
A: Check your Manim installation. <br>

Q: Error `latex ...` <br>
A: Check your latex installation. <br>

Q: The output log is not showing response? <br>
A: It could be API-related issues. Make sure your `.env` file is properly configured (fill in your API keys), or you can enable litellm debug mode to figure out the issues. <be>

Q: Plans / Scenes are missing? <br>
A: It could be API-related issues. Make sure your `.env` file is properly configured (fill in your API keys), or you can enable litellm debug mode to figure out the issues. <br>

## Acknowledgements
 Big thanks to the [TheoremExplainAgent](https://github.com/TIGER-AI-Lab/TheoremExplainAgent) team for the core pipeline and research — for more information visit their repository and paper.

For full details and the original project, see: https://github.com/TIGER-AI-Lab/TheoremExplainAgent

Also Thanks to
* [Manim Community](https://www.manim.community/)
* [kokoro-manim-voiceover](https://github.com/xposed73/kokoro-manim-voiceover)
* [manim-physics](https://github.com/Matheart/manim-physics)
* [manim-Chemistry](https://github.com/UnMolDeQuimica/manim-Chemistry)
* [ManimML](https://github.com/helblazer811/ManimML)
* [manim-dsa](https://github.com/F4bbi/manim-dsa)
* [manim-circuit](https://github.com/Mr-FuzzyPenguin/manim-circuit)

## 🎫 License

This project is released under the [the MIT License](LICENSE).

## 🚨 Disclaimer

**This work is intended for research purposes only. The authors do not encourage or endorse the use of this codebase for commercial applications. The code is provided "as is" without any warranties, and users assume all responsibility for its use.**
