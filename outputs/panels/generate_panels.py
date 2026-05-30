#!/usr/bin/env python3
"""Generate manga panel images via SiliconFlow API."""

import os
import sys
import json
import time
from pathlib import Path

# Load API key from .env
env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get("CUSTOM_PROVIDER_API_SILICONFLOW_CN_KEY", "")
if not API_KEY:
    print("ERROR: No API key found")
    sys.exit(1)

# Strip any prefix if needed
if API_KEY.startswith("sk-"):
    API_KEY = API_KEY

API_URL = "https://api.siliconflow.cn/v1/images/generations"

PANELS_DIR = Path("/Users/alex/ai-manga-comic/outputs/panels")
PANELS_DIR.mkdir(parents=True, exist_ok=True)

# All 12 panel prompts
panels = [
    # Scene 1: 放学前
    ("scene_1_1", "Realistic 1990s Chinese high school classroom, old wooden desks arranged in rows, chalkboard with chalk writings, ceiling fan, dark clouds visible through window, students in blue/white uniforms packing schoolbags, warm nostalgic summer afternoon light, Kodak film photography style, cinematic"),
    ("scene_1_2", "Medium shot of a shy teenage boy in 1990s Chinese blue-white school uniform, wearing round glasses, packing his canvas schoolbag, glancing nervously across classroom, soft natural lighting, realistic film photography, nostalgic 90s aesthetic, cinematic portrait"),
    ("scene_1_3", "Close-up of a pretty Chinese teenage girl with ponytail in 1990s school uniform, looking out window with worried expression, holding a sketchbook, dark clouds visible through glass, soft window light illuminating her face, realistic photography, nostalgic 90s film look"),
    # Scene 2: 屋檐下
    ("scene_2_1", "Wide shot of old Chinese school building entrance with traditional grey-tiled eaves, heavy rain pouring down like a curtain, two students in blue-white uniforms standing under narrow roof shelter, wet concrete ground with puddles, 1990s Chinese campus architecture, rainy atmosphere, realistic photography, film grain"),
    ("scene_2_2", "Medium shot of two Chinese high school students standing side by side under narrow eaves, rain splashing near their feet, awkward distance between shy boy and girl in blue-white uniforms, grey rainy sky, wet atmosphere, soft natural light, 1990s campus, realistic photography"),
    ("scene_2_3", "Extreme close-up of rain droplets on a girl's shoulder, blue-white school uniform fabric getting wet, a boy's hand visible holding a notebook hesitating to offer it, shallow depth of field, rainy day soft lighting, artistic film photography"),
    # Scene 3: 靠近
    ("scene_3_1", "Medium shot of two Chinese teenagers huddled close under a textbook held over their heads as makeshift rain shelter, shoulders almost touching, blue-white school uniforms getting wet, rain pouring around them, intimate atmosphere, 1990s campus, realistic film photography, cinematic lighting"),
    ("scene_3_2", "Close-up portrait of a teenage boy and girl looking at each other, faces very close, rain droplets on boy's round glasses, girl's eyes showing shyness and warmth, blurred rain background with bokeh lights, cinematic shallow depth of field, nostalgic 90s film aesthetic"),
    ("scene_3_3", "Medium shot as rain lightens, warm sunlight breaking through grey clouds, a teenage girl smiling at boy, boy looking relieved and hopeful, faint rainbow visible in distance, wet reflective ground, golden hour lighting breaking through storm, hopeful atmosphere, realistic photography"),
    # Scene 4: 同行
    ("scene_4_1", "Wide shot of a tree-lined path on a Chinese campus after rain, wet ground reflecting golden sunlight, two teenagers in school uniforms walking side by side with canvas schoolbags, summer greenery, beautiful golden hour lighting, nostalgic 1990s campus scene, realistic film photography"),
    ("scene_4_2", "Close-up of an open sketchbook revealing a pencil drawing of a boy reading under a tree, a girl's slender hand holding the sketchbook, soft afternoon light filtering through leaves, artistic shallow depth of field, warm nostalgic tones, detailed pencil art visible"),
    ("scene_4_3", "Golden sunset silhouette shot, two teenagers standing at a campus crossroad, warm golden light surrounding them, beautiful post-rain glow, long shadows on wet ground, cinematic composition, young love atmosphere, nostalgic 1990s film photography style, happy ending feel")
]

def generate_image(filename, prompt, retries=2):
    """Generate image via SiliconFlow API."""
    import requests
    
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell",
        "prompt": prompt,
        "image_size": "1024x576",  # 16:9 landscape
        "num_inference_steps": 4,
        "seed": int(time.time()) % 1000000,
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    for attempt in range(retries + 1):
        try:
            resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
            if resp.status_code != 200:
                print(f"  HTTP {resp.status_code}: {resp.text[:200]}")
                if "insufficient_quota" in resp.text.lower():
                    # Try cheaper model
                    payload["model"] = "stabilityai/stable-diffusion-3.5-large-turbo"
                    payload["image_size"] = "1024x576"
                    resp = requests.post(API_URL, json=payload, headers=headers, timeout=60)
                    if resp.status_code != 200:
                        print(f"  Fallback also failed: {resp.status_code}")
                        return False
                else:
                    continue
            
            data = resp.json()
            images = data.get("images", [])
            if not images:
                images = [img["url"] for img in data.get("data", [])]
            
            if images:
                url = images[0] if isinstance(images[0], str) else images[0].get("url", "")
                if url:
                    img_resp = requests.get(url, timeout=30)
                    if img_resp.status_code == 200:
                        out_path = PANELS_DIR / f"{filename}.png"
                        with open(out_path, "wb") as f:
                            f.write(img_resp.content)
                        print(f"  ✅ Saved {filename}.png ({len(img_resp.content)} bytes)")
                        return True
            
            print(f"  ⚠️ No image in response: {json.dumps(data)[:200]}")
        except Exception as e:
            print(f"  ⚠️ Attempt {attempt+1} failed: {e}")
            time.sleep(3)
    
    return False

print("🎨 Generating 12 manga panel images via SiliconFlow...")
print(f"   API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
print()

success = 0
for filename, prompt in panels:
    print(f"[{filename}] Generating...")
    if generate_image(filename, prompt):
        success += 1
    else:
        print(f"  ❌ Failed to generate {filename}")
    print()

print(f"\n📊 Results: {success}/{len(panels)} images generated")
print(f"📁 Output: {PANELS_DIR}")

if success == 0:
    print("\n⚠️  No images were generated. The SiliconFlow key may not have image gen quota.")
    print("   Alternative: Set FAL_KEY environment variable and use the built-in image_generate tool.")
    sys.exit(1)
