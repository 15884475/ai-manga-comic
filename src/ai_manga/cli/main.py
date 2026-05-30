"""AI漫剧 — main CLI entry point."""

import asyncio
import json
import os
from pathlib import Path

import click

from ai_manga.story.generator import StoryGenerator
from ai_manga.image_gen.generator import ComfyUIGenerator, DiffusersGenerator
from ai_manga.layout.manga_layout import MangaLayout, TextBubble
from ai_manga.audio.tts import TTSGenerator, AudioMixer
from ai_manga.video.assembler import VideoAssembler


@click.group()
def cli():
    """AI漫剧 — AI-powered manga comic video creator."""
    pass


@cli.command()
@click.argument("prompt")
@click.option("--scenes", default=4, help="Number of scenes")
@click.option("--panels", default=3, help="Panels per scene")
@click.option("--style", default="manga", help="Art style")
@click.option("--output", "-o", default="story.json", help="Output file")
def story(prompt, scenes, panels, style, output):
    """Generate a story from a text prompt."""
    click.echo(f"🎬 Generating {style} story: {prompt[:50]}...")
    gen = StoryGenerator()
    s = gen.generate(prompt, style=style, num_scenes=scenes, panels_per_scene=panels)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(s.to_dict(), f, ensure_ascii=False, indent=2)
    click.echo(f"📝 Story saved to {output}")
    click.echo(f"📖 {len(s.scenes)} scenes, {sum(len(sc.panels) for sc in s.scenes)} panels")


@cli.command()
@click.option("--story-file", default="story.json", help="Story JSON file")
@click.option("--output", "-o", default="./outputs/panels", help="Output directory")
@click.option("--engine", type=click.Choice(["comfyui", "diffusers"]), default="diffusers",
              help="Image generation engine")
def images(story_file, output, engine):
    """Generate manga panel images from story."""
    with open(story_file, encoding="utf-8") as f:
        story_dict = json.load(f)

    from ai_manga.story.generator import Story
    story_obj = Story.from_dict(story_dict)
    prompts = story_obj.to_prompts()

    click.echo(f"🖼️ Generating {len(prompts)} panel images using {engine}...")

    if engine == "comfyui":
        gen = ComfyUIGenerator()
        if not gen.is_available():
            click.echo("⚠️  ComfyUI not available, falling back to diffusers")
            gen = DiffusersGenerator()
    else:
        gen = DiffusersGenerator()

    if not gen.is_available():
        click.echo("❌ No image generation engine available. Install torch + diffusers.")
        return

    panel_paths = []
    for p in prompts:
        click.echo(f"   Panel {p['scene']}-{p['panel']}: {p['prompt'][:60]}...")
        try:
            paths = gen.generate(p["prompt"], output_dir=output)
            panel_paths.extend(paths)
        except Exception as e:
            click.echo(f"   ⚠️  Failed: {e}")

    # Save mapping
    mapping = [{"prompt": p, "path": panel_paths[i] if i < len(panel_paths) else None}
               for i, p in enumerate(prompts)]
    with open(os.path.join(output, "panel_mapping.json"), "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    click.echo(f"✅ Generated {len(panel_paths)} images in {output}/")


@cli.command()
@click.option("--panels-dir", default="./outputs/panels", help="Panels directory")
@click.option("--layout", default="auto", help="Layout: auto, 2x2, 3x2, 1x3, etc")
@click.option("--output", "-o", default="./outputs/pages", help="Output directory")
@click.option("--direction", type=click.Choice(["rtl", "ltr"]), default="rtl",
              help="Reading direction (rtl=manga, ltr=comic)")
def layout(panels_dir, layout, output, direction):
    """Arrange panels into manga-style pages."""
    mapping_path = os.path.join(panels_dir, "panel_mapping.json")
    if os.path.exists(mapping_path):
        with open(mapping_path) as f:
            mapping = json.load(f)
        panel_paths = [m["path"] for m in mapping if m.get("path") and os.path.exists(m["path"])]
    else:
        # Just find all PNGs
        panel_paths = sorted(Path(panels_dir).glob("*.png"))
        panel_paths = [str(p) for p in panel_paths]

    if not panel_paths:
        click.echo("❌ No panel images found")
        return

    click.echo(f"📐 Arranging {len(panel_paths)} panels into manga pages...")

    ml = MangaLayout(direction=direction)
    pages = ml.arrange([str(p) for p in panel_paths], layout=layout, output_dir=output)
    click.echo(f"✅ Created {len(pages)} pages in {output}/")


@cli.command()
@click.option("--story-file", default="story.json", help="Story JSON file")
@click.option("--output", "-o", default="./outputs/audio", help="Output directory")
@click.option("--voice", default="zh-CN-XiaoxiaoNeural", help="TTS voice")
def tts(story_file, output, voice):
    """Generate TTS narration for the story."""
    with open(story_file, encoding="utf-8") as f:
        story_dict = json.load(f)

    from ai_manga.story.generator import Story
    story_obj = Story.from_dict(story_dict)

    click.echo("🎙️ Generating narration audio...")
    tts_gen = TTSGenerator(voice=voice)

    audio_files = []
    for scene in story_obj.scenes:
        for panel in scene.panels:
            if panel.narration:
                try:
                    path = tts_gen.generate(panel.narration, output_dir=output)
                    audio_files.append({"scene": scene.index, "panel": panel.panel_index,
                                        "text": panel.narration, "path": path})
                except Exception as e:
                    click.echo(f"   ⚠️  TTS failed: {e}")

    with open(os.path.join(output, "audio_mapping.json"), "w", encoding="utf-8") as f:
        json.dump(audio_files, f, ensure_ascii=False, indent=2)

    click.echo(f"✅ Generated {len(audio_files)} audio clips in {output}/")


@cli.command()
@click.option("--pages-dir", default="./outputs/pages", help="Pages directory")
@click.option("--audio-dir", default="./outputs/audio", help="Audio directory")
@click.option("--output", "-o", default="./outputs/manga_video.mp4", help="Output video path")
@click.option("--duration", default=5.0, help="Seconds per page")
def video(pages_dir, audio_dir, output, duration):
    """Assemble pages into a video with narration."""
    pages = sorted(Path(pages_dir).glob("page_*.png"))
    if not pages:
        click.echo("❌ No page images found in {pages_dir}")
        return

    # Find audio: use first audio file or mix all
    audio_mapping = os.path.join(audio_dir, "audio_mapping.json")
    audio_path = None
    if os.path.exists(audio_mapping):
        with open(audio_mapping) as f:
            audio_files = json.load(f)
        if audio_files:
            # Mix all audio into one
            mixer = AudioMixer()
            first = audio_files[0]["path"]
            mixed_path = os.path.join(audio_dir, "mixed_narration.mp3")
            mixed = mixer.mix(first, output_path=mixed_path)
            audio_path = mixed

    click.echo(f"🎬 Assembling {len(pages)} pages into video...")
    va = VideoAssembler(duration_per_page=duration)
    result = va.assemble([str(p) for p in pages], audio_path=audio_path, output_path=output)
    click.echo(f"✅ Video saved to {result}")


@cli.command()
@click.argument("prompt")
@click.option("--scenes", default=4, help="Number of scenes")
@click.option("--panels-per-scene", default=3, help="Panels per scene")
@click.option("--style", default="manga", help="Art style")
@click.option("--engine", default="diffusers", help="Image engine: comfyui or diffusers")
@click.option("--voice", default="zh-CN-XiaoxiaoNeural", help="TTS voice")
@click.option("--output", "-o", default="./outputs", help="Output directory")
def run(prompt, scenes, panels_per_scene, style, engine, voice, output):
    """Run the full AI漫剧 pipeline end-to-end."""
    click.echo("=" * 50)
    click.echo("🎬 AI漫剧 — Full Pipeline")
    click.echo("=" * 50)

    os.makedirs(output, exist_ok=True)

    # Step 1: Story
    click.echo("\n[1/5] 📝 Generating story...")
    gen = StoryGenerator()
    story_obj = gen.generate(prompt, style=style, num_scenes=scenes, panels_per_scene=panels_per_scene)
    story_file = os.path.join(output, "story.json")
    with open(story_file, "w", encoding="utf-8") as f:
        json.dump(story_obj.to_dict(), f, ensure_ascii=False, indent=2)
    click.echo(f"   -> {len(story_obj.scenes)} scenes, {sum(len(sc.panels) for sc in story_obj.scenes)} panels")

    # Step 2: Images
    click.echo("\n[2/5] 🖼️ Generating panel images...")
    panels_dir = os.path.join(output, "panels")
    prompts = story_obj.to_prompts()

    if engine == "comfyui":
        img_gen = ComfyUIGenerator()
        if not img_gen.is_available():
            click.echo("   ⚠️  ComfyUI unavailable, falling back to diffusers")
            img_gen = DiffusersGenerator()
    else:
        img_gen = DiffusersGenerator()

    panel_paths = []
    if img_gen.is_available():
        for p in prompts:
            try:
                paths = img_gen.generate(p["prompt"], output_dir=panels_dir)
                panel_paths.extend(paths)
            except Exception as e:
                click.echo(f"   ⚠️  Panel {p['scene']}-{p['panel']} failed: {e}")
    else:
        click.echo("   ⚠️  No image engine available — using placeholder panels")
        # Create placeholder images
        from PIL import Image, ImageDraw
        for p in prompts:
            img = Image.new("RGB", (512, 768), (240, 240, 240))
            draw = ImageDraw.Draw(img)
            draw.text((50, 350), f"Scene {p['scene']}-{p['panel']}\n{p['prompt'][:80]}", fill="black")
            path = os.path.join(panels_dir, f"placeholder_{p['scene']}_{p['panel']}.png")
            os.makedirs(panels_dir, exist_ok=True)
            img.save(path)
            panel_paths.append(path)

    # Step 3: Layout
    click.echo("\n[3/5] 📐 Arranging manga layout...")
    pages_dir = os.path.join(output, "pages")
    ml = MangaLayout()
    pages = ml.arrange(panel_paths, output_dir=pages_dir)

    # Step 4: TTS
    click.echo("\n[4/5] 🎙️ Generating narration...")
    audio_dir = os.path.join(output, "audio")
    tts_gen = TTSGenerator(voice=voice)
    audio_path = None
    for scene in story_obj.scenes:
        for panel in scene.panels:
            if panel.narration:
                try:
                    audio_path = tts_gen.generate(panel.narration, output_dir=audio_dir)
                except Exception as e:
                    click.echo(f"   ⚠️  TTS failed: {e}")

    # Step 5: Video
    click.echo("\n[5/5] 🎬 Assembling final video...")
    va = VideoAssembler()
    video_path = os.path.join(output, "manga_video.mp4")
    try:
        result = va.assemble(pages, audio_path=audio_path, output_path=video_path)
        click.echo(f"\n✅ Final video: {result}")
    except Exception as e:
        click.echo(f"⚠️  Video assembly failed: {e}")

    click.echo("\n" + "=" * 50)
    click.echo(f"🎉 Pipeline complete! Outputs in {output}/")
    click.echo("=" * 50)


if __name__ == "__main__":
    cli()
