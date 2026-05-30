"""Story & script generation module.

Uses LLM (via Hermes or direct API) to generate:
- Story synopsis
- Scene-by-scene script
- Panel descriptions (camera angle, characters, background, text)
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Panel:
    """A single manga panel/cell."""
    scene_index: int
    panel_index: int
    description: str  # Visual description for image gen
    narration: str = ""  # Narration text (voiceover)
    dialogue: dict[str, str] = field(default_factory=dict)  # character -> line
    camera: str = "medium shot"  # close-up, medium, wide
    background: str = ""


@dataclass
class Scene:
    """A scene composed of multiple panels."""
    index: int
    title: str
    setting: str
    panels: list[Panel] = field(default_factory=list)


@dataclass
class Story:
    """Complete story structure."""
    title: str
    synopsis: str
    characters: list[dict] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)
    style: str = "manga"  # manga, comic, anime

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Story":
        scenes = []
        for sd in d.get("scenes", []):
            scene_idx = sd.get("index", 0)
            panels = []
            for pd in sd.get("panels", []):
                pd["scene_index"] = pd.get("scene_index", scene_idx)
                panels.append(Panel(**pd))
            scene_data = {k: v for k, v in sd.items() if k != "panels"}
            scenes.append(Scene(**scene_data, panels=panels))
        story_data = {k: v for k, v in d.items() if k != "scenes"}
        return cls(**story_data, scenes=scenes)

    def to_prompts(self) -> list[dict[str, str]]:
        """Convert each panel to an image generation prompt."""
        prompts = []
        for scene in self.scenes:
            for panel in scene.panels:
                prompt = (
                    f"Manga style. {panel.camera}. "
                    f"{panel.description}. "
                    f"Background: {panel.background}"
                )
                prompts.append({
                    "prompt": prompt,
                    "scene": scene.index,
                    "panel": panel.panel_index,
                    "narration": panel.narration,
                    "dialogue": panel.dialogue,
                })
        return prompts


class StoryGenerator:
    """Generate story structures from a prompt.
    
    Uses local LLM API or Hermes Agent to produce structured stories.
    """

    def __init__(self, api_base: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.api_base = api_base
        self.model = model

    def generate(self, prompt: str, style: str = "manga", num_scenes: int = 4, panels_per_scene: int = 3) -> Story:
        """Generate a complete story from a text prompt."""
        sys_prompt = f"""你是一个漫剧编剧。根据用户提供的梗概，生成一个{style}风格的剧本。

输出JSON格式:
{{
  "title": "作品标题",
  "synopsis": "完整故事简介",
  "characters": [{{"name": "角色名", "role": "角色描述", "voice": "声线描述"}}],
  "scenes": [
    {{
      "index": 1,
      "title": "场景标题",
      "setting": "场景设定描述",
      "panels": [
        {{
          "panel_index": 1,
          "camera": "wide shot/medium shot/close-up",
          "description": "画面描述(用于AI生图，英文)",
          "background": "背景描述(英文)",
          "narration": "旁白文字",
          "dialogue": {{"角色名": "台词"}}
        }}
      ]
    }}
  ]
}}

画面描述用英文(适配stable diffusion)，其他字段用中文。
每个场景{panels_per_scene}个分镜，共{num_scenes}个场景。"""

        # Try OpenAI-compatible API first
        try:
            import requests
            resp = requests.post(
                f"{self.api_base}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.8,
                    "response_format": {"type": "json_object"},
                },
                timeout=60
            )
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            story_dict = json.loads(content)
        except Exception:
            # Fallback: return a template story
            story_dict = self._template_story(prompt, style, num_scenes, panels_per_scene)

        story_dict["style"] = style
        return Story.from_dict(story_dict)

    def _template_story(self, prompt: str, style: str, num_scenes: int, panels_per_scene: int) -> dict:
        """Template fallback when LLM is unavailable."""
        return {
            "title": prompt[:30],
            "synopsis": f"{prompt} — 一个由AI生成的{style}风格漫剧故事。",
            "characters": [{"name": "主角", "role": "主要角色", "voice": "中性"}],
            "scenes": [
                {
                    "index": i + 1,
                    "title": f"第{i+1}幕",
                    "setting": f"场景{i+1}的设定",
                    "panels": [
                        {
                            "panel_index": j + 1,
                            "camera": ["wide shot", "medium shot", "close-up"][j % 3],
                            "description": f"A manga style scene: {prompt[:50]}, part {i+1}-{j+1}",
                            "background": f"Scene background {i+1}",
                            "narration": f"旁白：故事进入了第{i+1}幕。",
                            "dialogue": {}
                        }
                        for j in range(panels_per_scene)
                    ]
                }
                for i in range(num_scenes)
            ]
        }
