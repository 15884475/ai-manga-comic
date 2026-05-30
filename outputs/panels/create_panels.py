#!/usr/bin/env python3
"""Create manga-style placeholder panels in portrait (512x768) format."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

FONT_PATH = "/System/Library/Fonts/PingFang.ttc"
PANELS_DIR = Path("/Users/alex/ai-manga-comic/outputs/panels")
PANELS_DIR.mkdir(parents=True, exist_ok=True)

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def create_gradient(w, h, c1, c2):
    base = Image.new("RGB", (w, h), c1)
    top = Image.new("RGB", (w, h), c2)
    mask = Image.new("L", (w, h))
    for y in range(h):
        for x in range(w):
            mask.putpixel((x, y), int(255 * (1 - y / h)))
    return Image.composite(base, top, mask)

def wrap_text(draw, text, font, max_w):
    lines = []
    for ch in text:
        if not lines:
            lines.append(ch)
        else:
            test = lines[-1] + ch
            if draw.textbbox((0, 0), test, font=font)[2] > max_w:
                lines.append(ch)
            else:
                lines[-1] = test
    return lines

def make_panel(fn, scene_label, title, desc, colors, mood, w=512, h=768):
    img = create_gradient(w, h, colors[0], colors[1])
    draw = ImageDraw.Draw(img)
    
    # Scene badge
    badge_c = colors[2] if len(colors) > 2 else "#FF6B6B"
    draw.rounded_rectangle([20, 30, 170, 75], radius=16, fill=badge_c)
    draw.text((32, 40), scene_label, fill="white", font=get_font(24))
    
    # Title
    t_font = get_font(22)
    tw = draw.textbbox((0, 0), title, font=t_font)[2]
    tx = (w - tw) // 2
    draw.text((tx, 100), title, fill=(255, 255, 255, 220), font=t_font)
    
    # Description (centered)
    d_font = get_font(16)
    lines = wrap_text(draw, desc, d_font, w - 60)
    y = 170
    for line in lines[:8]:
        lw = draw.textbbox((0, 0), line, font=d_font)[2]
        lx = (w - lw) // 2
        draw.text((lx, y), line, fill=(255, 255, 255, 180), font=d_font)
        y += 28
    
    # Decorative circles
    draw.ellipse([w-60, 30, w-20, 70], fill=None, outline=(255,255,255,40), width=2)
    draw.ellipse([w-80, 55, w-10, 120], fill=None, outline=(255,255,255,20), width=1)
    
    # Bottom mood
    overlay = Image.new("RGBA", (w, h), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([15, h-70, w-15, h-15], radius=10, fill=(0,0,0,140))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    m_lines = wrap_text(draw, mood, get_font(15), w-50)
    for i, line in enumerate(m_lines[:2]):
        draw.text((25, h-58+i*22), line, fill=(255,255,255,170), font=get_font(15))
    
    img.save(PANELS_DIR / fn, "PNG")
    print(f"  ✅ {fn}")

print("🎨 Creating 12 panels (portrait 512x768)...")

# Scene 1
make_panel("scene_1_1.png", "场景 1", "放学前", "教室。乌云密布，同学们收拾书包准备放学。", ["#F5E6CA", "#D4A574", "#E8A040"], "午后的教室 · 闷热 · 暗涌的心情")
make_panel("scene_1_2.png", "场景 1", "偷偷一瞥", "林小北悄悄看向那个熟悉的背影，心跳加速。", ["#E8D5B7", "#C49A6C", "#7EB6B5"], "暗恋 · 不敢靠近")
make_panel("scene_1_3.png", "场景 1", "忘记带伞", "苏雨晴望着窗外，要下雨了，可是没带伞。", ["#C9D6E8", "#8FA8C9", "#5B7FA5"], "担忧 · 夏天的雨")

# Scene 2
make_panel("scene_2_1.png", "场景 2", "屋檐下", "大雨倾盆。苏雨晴站在屋檐下躲雨，看着雨帘发愁。", ["#6B8FA3", "#3A5A6F", "#4A6FA5"], "大雨 · 躲雨")
make_panel("scene_2_2.png", "场景 2", "并肩", "林小北默默站到她身旁。雨声中，两人无言。", ["#7A9BAE", "#4A6B80", "#6B8F7A"], "并肩 · 雨声 · 心跳")
make_panel("scene_2_3.png", "场景 2", "犹豫", "雨飘进来，打湿了她的肩膀。他欲言又止。", ["#5A7A8F", "#3A5A6F", "#8F6B5A"], "犹豫 · 说不出口")

# Scene 3
make_panel("scene_3_1.png", "场景 3", "靠近", "林小北把课本举在两人头顶挡雨，距离突然拉近。", ["#D4A574", "#B88A4A", "#C96B6B"], "一把「伞」· 靠近 · 勇气")
make_panel("scene_3_2.png", "场景 3", "对视", "四目相对。近到能听到彼此的心跳声和呼吸。", ["#E8C49A", "#C9A57A", "#D47A7A"], "对视 · 青春的心跳")
make_panel("scene_3_3.png", "场景 3", "雨过天晴", "雨渐小，天边挂起一道彩虹。她对他笑了。", ["#F5E6CA", "#D4C47A", "#7AB58A"], "雨过天晴 · 彩虹 · 微笑")

# Scene 4
make_panel("scene_4_1.png", "场景 4", "同行", "两人并肩走在雨后湿漉漉的校园小路上。夕阳洒肩。", ["#F0D5A5", "#D4A040", "#C97A4A"], "雨后 · 夕阳 · 并肩")
make_panel("scene_4_2.png", "场景 4", "秘密", "她打开速写本——里面是他在梧桐树下看书的模样。", ["#F5E0C0", "#D4B080", "#A5B07A"], "速写里的秘密 · 原来你也在这里")
make_panel("scene_4_3.png", "场景 4", "约定", "「明天还会下雨吗？」「下雨的话，我在这等你。」", ["#E8C47A", "#C99A4A", "#D47A4A"], "约定 · 故事的开始")

print(f"\n✅ Done. All panels in {PANELS_DIR}")
