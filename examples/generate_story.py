#!/usr/bin/env python3
"""Example: Generate a short AI漫剧 from a prompt."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ai_manga.story.generator import StoryGenerator


def main():
    prompt = "一个少年在废弃城市中发现了一只会说话的猫，他们一起踏上了寻找传说中星辰之花的旅程。"

    print(f"🎬 故事梗概: {prompt[:50]}...")
    gen = StoryGenerator()
    story = gen.generate(prompt, style="manga", num_scenes=2, panels_per_scene=2)

    print(f"📖 标题: {story.title}")
    print(f"📖 场景数: {len(story.scenes)}")
    print(f"📖 分镜数: {sum(len(s.panels) for s in story.scenes)}")

    # Show first panel
    if story.scenes:
        p = story.scenes[0].panels[0]
        print(f"\n🎨 第一个分镜:")
        print(f"   镜头: {p.camera}")
        print(f"   描述: {p.description[:80]}...")
        print(f"   旁白: {p.narration}")
        if p.dialogue:
            for char, line in p.dialogue.items():
                print(f"   💬 {char}: {line}")

    # Save
    with open("story.json", "w", encoding="utf-8") as f:
        json.dump(story.to_dict(), f, ensure_ascii=False, indent=2)
    print("\n✅ Story saved to story.json")


if __name__ == "__main__":
    main()
