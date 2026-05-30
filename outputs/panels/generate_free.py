#!/usr/bin/env python3
"""Generate manga panel images via Pollinations.ai (free, no API key)."""

import requests
import urllib.parse
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PANELS_DIR = Path("/Users/alex/ai-manga-comic/outputs/panels")
PANELS_DIR.mkdir(parents=True, exist_ok=True)

# All 12 panel prompts (URL-safe, no API key needed)
panels = [
    ("scene_1_1", "1990s Chinese high school classroom wooden desks chalkboard ceiling fan dark clouds outside window students blue white uniforms packing bags nostalgic summer afternoon realistic film photography"),
    ("scene_1_2", "shy teenage boy 1990s Chinese blue white school uniform round glasses glancing nervously across classroom canvas bag soft lighting nostalgic realistic portrait"),
    ("scene_1_3", "pretty Chinese teenage girl ponytail 1990s school uniform looking out window worried holding sketchbook dark clouds outside soft window light realistic film portrait"),
    ("scene_2_1", "old Chinese school building entrance grey tiled eaves heavy rain curtain two students blue white uniforms under narrow roof wet concrete puddles 1990s campus rainy realistic"),
    ("scene_2_2", "two Chinese high school students standing side by side under eaves rain splashing near feet awkward distance boy girl school uniforms grey sky wet atmosphere realistic"),
    ("scene_2_3", "extreme close up rain droplets girls shoulder school uniform getting wet boys hand holding notebook hesitating shallow depth field rainy artistic photography"),
    ("scene_3_1", "two Chinese teenagers huddled close under textbook over heads rain shelter shoulders almost touching blue school uniforms wet pouring rain intimate cinematic"),
    ("scene_3_2", "close up teenage boy and girl looking each other faces very close rain on boys round glasses girls eyes showing shyness blurred rain bokeh background cinematic"),
    ("scene_3_3", "rain lightening warm sunlight breaking through grey clouds teenage girl smiling boy hopeful rainbow distant wet reflective ground golden hour hopeful atmosphere"),
    ("scene_4_1", "tree lined path Chinese campus after rain wet ground reflecting golden sunlight two teenagers walking schoolbags summer greenery golden hour nostalgic campus realistic"),
    ("scene_4_2", "close up open sketchbook pencil drawing boy reading under tree girls hand holding sketchbook soft afternoon light through leaves artistic warm"),
    ("scene_4_3", "golden sunset silhouette two teenagers campus crossroad warm golden light surrounding beautiful post rain glow long shadows cinematic young love atmosphere")
]

def generate_one(filename, prompt, timeout=60):
    """Generate one image via Pollinations.ai."""
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
    params = {"width": 1024, "height": 576, "nologo": True, "seed": int(time.time() * 1000) % 10000000}
    
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        if resp.status_code == 200 and len(resp.content) > 1000:
            out_path = PANELS_DIR / f"{filename}.png"
            with open(out_path, "wb") as f:
                f.write(resp.content)
            size_kb = len(resp.content) // 1024
            return (True, filename, f"{size_kb}KB")
        else:
            return (False, filename, f"HTTP {resp.status_code} size {len(resp.content)}")
    except Exception as e:
        return (False, filename, str(e))

print("🎨 Generating 12 manga panel images via Pollinations.ai (free)...")
print()

success = 0
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = {executor.submit(generate_one, fn, prompt): (fn, prompt) for fn, prompt in panels}
    for future in as_completed(futures):
        ok, fn, info = future.result()
        if ok:
            print(f"  ✅ {fn}.png ({info})")
            success += 1
        else:
            print(f"  ❌ {fn}.png - {info}")

print(f"\n📊 Results: {success}/{len(panels)} images generated")
print(f"📁 Output: {PANELS_DIR}")
