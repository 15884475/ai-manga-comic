#!/usr/bin/env python3
"""Direct video assembly bypassing the pipeline's VideoAssembler."""
import subprocess, os, sys

FFMPEG = os.path.expanduser("~/.cache/ai-manga/ffmpeg")
PAGES_DIR = "/Users/alex/ai-manga-comic/outputs/pages"
AUDIO_DIR = "/Users/alex/ai-manga-comic/outputs/audio"
OUTPUT = "/Users/alex/ai-manga-comic/outputs/manga_video.mp4"
DURATION = 5.0

def main():
    pages = sorted([f for f in os.listdir(PAGES_DIR) if f.startswith("page_")])
    
    # 1. Create concat file
    concat = "/tmp/manga_concat.txt"
    with open(concat, "w") as f:
        for p in pages:
            f.write(f"file '{os.path.join(PAGES_DIR, p)}'\n")
            f.write(f"duration {DURATION}\n")
    
    # 2. Mix audio clips into one
    mixed_audio = "/tmp/mixed_audio.mp3"
    clips = sorted([f for f in os.listdir(AUDIO_DIR) if f.startswith("clip_")])
    
    if clips:
        audio_concat = "/tmp/audio_concat.txt"
        with open(audio_concat, "w") as f:
            for c in clips:
                f.write(f"file '{os.path.join(AUDIO_DIR, c)}'\n")
        
        print(f"📢 Mixing {len(clips)} audio clips...")
        cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", 
               "-i", audio_concat, "-c", "copy", mixed_audio]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"⚠️ Audio mix failed: {r.stderr[:200]}")
            mixed_audio = None
        else:
            print("✅ Audio mixed")
    else:
        mixed_audio = None
    
    # 3. Assemble video
    print(f"🎬 Assembling {len(pages)} pages...")
    
    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat,
           "-c:v", "h264_videotoolbox", "-b:v", "5M", "-pix_fmt", "yuv420p",
           "-r", "30"]
    
    if mixed_audio and os.path.exists(mixed_audio):
        cmd.extend(["-i", mixed_audio, "-c:a", "aac", "-b:a", "128k", "-shortest"])
    
    cmd.append(OUTPUT)
    
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if r.returncode != 0:
        # Fallback: try libx264
        print(f"⚠️ Videotoolbox failed, trying libx264...")
        cmd[10] = "libx264"
        cmd[11] = "23"
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if r.returncode != 0:
        print(f"❌ FFmpeg failed:\n{r.stderr[-500:]}")
        sys.exit(1)
    
    print(f"✅ Video saved to {OUTPUT}")
    
    info = subprocess.run([FFMPEG, "-i", OUTPUT], capture_output=True, text=True)
    for line in info.stderr.split("\n"):
        if "Duration" in line:
            print(f"⏱️ {line.strip()}")

if __name__ == "__main__":
    mainmpeg failed:\\n{r.stderr[-500:]}\")\n        sys.exit(1)\n    \n    print(f\"\u2705 Video saved to {OUTPUT}\")\n    \n    info = subprocess.run([FFMPEG, \"-i\", OUTPUT], capture_output=True, text=True)\n    for line in info.stderr.split(\"\\n\"):\n        if \"Duration\" in line:\n            print(f\"\u23f1\ufe0f {line.strip()}\")\n\nif __name__ == \"__main__\":\n    main()"