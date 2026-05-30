#!/usr/bin/env python3
"""Create visually appealing manga-style placeholder panel images.
Uses PIL to create artistic gradient backgrounds with scene text.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math
import os
from pathlib import Path

FONT_PATH = "/System/Library/Fonts/PingFang.ttc"
PANELS_DIR = Path("/Users/alex/ai-manga-comic/outputs/panels")
PANELS_DIR.mkdir(parents=True, exist_ok=True)

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def create_gradient(w, h, color1, color2):
    """Create a vertical gradient image."""
    base = Image.new("RGB", (w, h), color1)
    top = Image.new("RGB", (w, h), color2)
    mask = Image.new("L", (w, h))
    for y in range(h):
        for x in range(w):
            mask.putpixel((x, y), int(255 * (1 - y / h)))
    return Image.composite(base, top, mask)

def draw_acrylic_overlay(draw, w, h, alpha=80):
    """Draw a semi-transparent overlay for text readability."""
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle([20, h-120, w-20, h-20], radius=12, fill=(0, 0, 0, alpha))
    return overlay

def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within max_width."""
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for char in paragraph:
            test = current + char
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width:
                lines.append(current)
                current = char
            else:
                current = test
        if current:
            lines.append(current)
    return lines

def create_panel(filename, title, subtitle, colors, mood_icon="", width=1024, height=576):
    """Create a stylized panel image with gradient background."""
    # Create gradient background
    img = create_gradient(width, height, colors[0], colors[1])
    
    # Add some artistic elements
    draw = ImageDraw.Draw(img)
    
    # Draw decorative elements
    # Horizontal lines at top
    for i in range(3):
        y = 30 + i * 8
        draw.line([40, y, 200, y], fill=(255, 255, 255, 60), width=2)
    
    # Draw scene number badge
    badge_color = colors[2] if len(colors) > 2 else "#FF6B6B"
    draw.rounded_rectangle([30, 50, 160, 110], radius=20, fill=badge_color)
    title_font = get_font(28)
    draw.text((50, 62), title, fill="white", font=title_font)
    
    # Draw subtitle (scene description)
    subtitle_font = get_font(20)
    lines = wrap_text(draw, subtitle, subtitle_font, width - 100)
    y_start = 140
    for i, line in enumerate(lines[:4]):
        draw.text((40, y_start + i * 32), line, fill=(255, 255, 255, 200), font=subtitle_font)
    
    # Draw decorative elements - circles/dots
    draw.ellipse([width-100, 50, width-50, 100], fill=None, outline=(255, 255, 255, 40), width=2)
    draw.ellipse([width-130, 80, width-20, 150], fill=None, outline=(255, 255, 255, 20), width=1)
    
    # Draw bottom overlay with mood
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle([20, height-90, width-20, height-20], radius=12, fill=(0, 0, 0, 160))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    # Draw mood/atmosphere text at bottom
    mood_font = get_font(18)
    lines_bottom = wrap_text(draw, mood_icon, mood_font, width - 80)
    for i, line in enumerate(lines_bottom[:2]):
        draw.text((40, height - 70 + i * 26), line, fill=(255, 255, 255, 180), font=mood_font)
    
    # Save
    out_path = PANELS_DIR / filename
    img.save(out_path, "PNG")
    print(f"  ✅ {filename}")

print("🎨 Creating 12 stylized manga panel images...")
print()

# Scene 1: Classroom - warm yellow tones
create_panel("scene_1_1.png", "场景 1 · 放学前", "1998年夏天的教室。窗外乌云密布，同学们收拾书包准备放学。", 
             ["#F5E6CA", "#D4A574", "#E8A040"], 
             "🌤️ 教室 · 午后的闷热 · 暗涌的心情")

create_panel("scene_1_2.png", "场景 1 · 林小北", "林小北悄悄看向教室另一边的那个背影，心跳加速。", 
             ["#E8D5B7", "#C49A6C", "#7EB6B5"],
             "👦 暗恋 · 偷偷一瞥 · 不敢靠近")

create_panel("scene_1_3.png", "场景 1 · 苏雨晴", "苏雨晴望着窗外——要下雨了。她没带伞。", 
             ["#C9D6E8", "#8FA8C9", "#5B7FA5"],
             "🌧️ 担忧 · 忘记带伞 · 夏天的雨")

# Scene 2: Shelter - cool blue rainy tones
create_panel("scene_2_1.png", "场景 2 · 屋檐下", "雨越下越大。苏雨晴站在教学楼门口，看着雨帘发愁。", 
             ["#6B8FA3", "#3A5A6F", "#4A6FA5"],
             "🌧️ 大雨 · 屋檐 · 躲雨")

create_panel("scene_2_2.png", "场景 2 · 相遇", "林小北鼓起勇气，默默站到了她旁边。空气里只有雨声。", 
             ["#7A9BAE", "#4A6B80", "#6B8F7A"],
             "☔ 并肩 · 雨声 · 心跳")

create_panel("scene_2_3.png", "场景 2 · 犹豫", "雨飘进来打湿了她的肩膀。他想说什么，却开不了口。", 
             ["#5A7A8F", "#3A5A6F", "#8F6B5A"],
             "💧 犹豫 · 关心 · 说不出口的话")

# Scene 3: Getting closer - warm romantic tones
create_panel("scene_3_1.png", "场景 3 · 靠近", "林小北鼓起勇气，把课本举在两人头顶。距离突然变得很近。", 
             ["#D4A574", "#B88A4A", "#C96B6B"],
             "📚 一把伞 · 靠近 · 勇气")

create_panel("scene_3_2.png", "场景 3 · 对视", "近距离的瞬间，四目相对。他闻到了她发梢淡淡的香味。", 
             ["#E8C49A", "#C9A57A", "#D47A7A"],
             "👀 对视 · 心跳加速 · 青春")

create_panel("scene_3_3.png", "场景 3 · 雨停", "雨渐渐小了。一道彩虹挂在天边。她对他笑了。", 
             ["#F5E6CA", "#D4C47A", "#7AB58A"],
             "🌈 雨过天晴 · 彩虹 · 微笑")

# Scene 4: Walking together - golden warm tones
create_panel("scene_4_1.png", "场景 4 · 同行", "两人并肩走在雨后湿漉漉的校园小路上，夕阳洒在肩头。", 
             ["#F0D5A5", "#D4A040", "#C97A4A"],
             "🌅 雨后 · 夕阳 · 并肩而行")

create_panel("scene_4_2.png", "场景 4 · 秘密", "她打开速写本——里面画着梧桐树下看书的他。", 
             ["#F5E0C0", "#D4B080", "#A5B07A"],
             "🎨 速写本 · 秘密 · 被看见")

create_panel("scene_4_3.png", "场景 4 · 约定", "「明天还会下雨吗？」 「下雨的话，我在这等你。」", 
             ["#E8C47A", "#C99A4A", "#D47A4A"],
             "💛 约定 · 青春 · 故事的开始")

print(f"\n✅ All 12 panels created in {PANELS_DIR}")
