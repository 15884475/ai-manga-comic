# AI Manga Comic (AI漫剧)

End-to-end pipeline for creating manga-style comic videos with AI.

## Pipeline

```
剧本(Story) → 分镜(Panel) → 生图(Image Gen) → 排版(Layout) → 配音(TTS) → 成片(Video)
```

## Features

- **Story Generation** — LLM-powered script & panel descriptions
- **Manga Image Generation** — AI generates manga-style panels via ComfyUI (recommended) or Diffusers
- **Manga Layout** — arrange panels into manga/漫画 page layouts (右→左 reading)
- **TTS Narration** — edge-tts for narration & dialogue (中文声优)
- **Video Assembly** — panels + narration → MP4 video, FFmpeg auto-downloaded

## Quick Start

```bash
# 1. 创建虚拟环境 + 安装依赖
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. 一键全流程（生成故事→布局→配音→成片）
PYTHONPATH=src:$PYTHONPATH python -m ai_manga.cli.main run "你的故事梗概" --scenes 4

# 或分步执行:
# 先写剧本
PYTHONPATH=src python -m ai_manga.cli.main story "故事梗概" -o story.json
# 生成分镜图（需安装 ComfyUI 或 diffusers）
PYTHONPATH=src python -m ai_manga.cli.main images --story-file story.json
# 排列页面
PYTHONPATH=src python -m ai_manga.cli.main layout --panels-dir ./outputs/panels
# 合成视频
PYTHONPATH=src python -m ai_manga.cli.main video --pages-dir ./outputs/pages
```

## Directory Structure

```
bin/              # Local ffmpeg (gitignored, auto-downloaded on first use)
configs/          # YAML configs (models, styles, voices)
src/ai_manga/
  story/          # Story & script generation
  image_gen/      # Image generation (ComfyUI / Diffusers)
  layout/         # Manga panel layout & text bubbles
  video/          # Video assembly & transitions
  audio/          # TTS & audio mixing
  cli/            # CLI entry point
  run.py          # One-shot full pipeline
examples/         # Example scripts
outputs/          # Generated outputs (gitignored)
workflows/        # ComfyUI workflow JSONs (manga_txt2img.json)
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `story` | Generate story/script from text prompt |
| `images` | Generate panel images from story JSON |
| `layout` | Arrange panels into manga pages |
| `tts` | Generate narration audio |
| `video` | Assemble pages + audio into MP4 |
| `run` | **Full pipeline** — all steps at once |

## First Production Run: 「雨巷青春」

See [PRODUCTION_REPORT.md](./PRODUCTION_REPORT.md) for the full post-mortem.

| Item | Detail |
|------|--------|
| Story | 90s campus love story — rainy day sheltering together |
| Status | ⚠️ Panels are PIL placeholder images (no image gen API available) |
| Duration | ~60s (12 pages × 5s) |
| Video | 1080×1920 portrait, H.264 + AAC, ~3MB |
| Root Cause | No FAL_KEY / SiliconFlow image gen access / ComfyUI |
| Fix | Configure FAL_KEY or SiliconFlow image models, then re-run with real images |

## Requirements

- Python 3.9+
- **Optional (for image gen):** ComfyUI (GPU recommended) or `torch` + `diffusers`
- **Auto-downloaded:** FFmpeg (~43MB, cached at `~/.cache/ai-manga/`)

## Install Image Generation Engine

### Option A: ComfyUI (Recommended)

```bash
pipx install comfy-cli
comfy --skip-prompt install --m-series  # Apple Silicon
comfy launch --background
comfy model download --url https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors --relative-path models/checkpoints
```

### Option B: Diffusers (Lighter, CPU works)

```bash
pip install torch diffusers transformers
# Configure in configs/default.yaml: engine: diffusers
```
