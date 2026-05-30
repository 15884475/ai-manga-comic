"""Image generation module.

Generates manga-style images using:
- ComfyUI (recommended, via REST API)
- Diffusers (fallback, local)
"""

import json
import os
import time
from pathlib import Path
from typing import Optional

import requests
from PIL import Image


class ComfyUIGenerator:
    """Generate images via ComfyUI REST API."""

    def __init__(self, server_url: str = "http://127.0.0.1:8188", workflow_path: Optional[str] = None):
        self.server_url = server_url.rstrip("/")
        self.workflow_path = workflow_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "workflows", "manga_txt2img.json"
        )

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.server_url}/system_stats", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, negative_prompt: str = "", output_dir: str = "./outputs") -> list[str]:
        """Generate image(s) from prompt via ComfyUI.
        Returns list of output file paths.
        """
        # Load workflow
        with open(self.workflow_path) as f:
            workflow = json.load(f)

        # Inject prompt — find the CLIPTextEncode node
        for node_id, node in workflow.items():
            if isinstance(node, dict):
                class_type = node.get("class_type", "")
                if "CLIPTextEncode" in class_type:
                    inputs = node.get("inputs", {})
                    text = inputs.get("text", "")
                    if negative_prompt not in text and len(text) < 200:
                        node["inputs"]["text"] = prompt
                        break

        # Submit
        payload = {"prompt": workflow}
        resp = requests.post(f"{self.server_url}/prompt", json=payload, timeout=30)
        result = resp.json()
        prompt_id = result.get("prompt_id")

        if not prompt_id:
            raise RuntimeError(f"ComfyUI submit failed: {result}")

        # Wait for completion
        for _ in range(120):
            time.sleep(2)
            status = requests.get(f"{self.server_url}/history/{prompt_id}", timeout=10)
            if status.status_code == 200:
                history = status.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    saved = []
                    os.makedirs(output_dir, exist_ok=True)
                    for node_id, node_outputs in outputs.items():
                        for img_data in node_outputs.get("images", []):
                            img_url = f"{self.server_url}/view?filename={img_data['filename']}&subfolder={img_data.get('subfolder','')}&type={img_data.get('type','output')}"
                            img_resp = requests.get(img_url, timeout=30)
                            out_path = os.path.join(output_dir, f"{prompt_id[:8]}_{img_data['filename']}")
                            with open(out_path, "wb") as f:
                                f.write(img_resp.content)
                            saved.append(out_path)
                    return saved

        raise TimeoutError("ComfyUI generation timed out")


class DiffusersGenerator:
    """Lightweight local generation using 🤗 Diffusers.
    Falls back if ComfyUI is unavailable.
    """

    def __init__(self, model_id: str = "hakurei/waifu-diffusion", device: str = "auto"):
        self.model_id = model_id
        self.device = device
        self._pipeline = None

    def is_available(self) -> bool:
        try:
            import torch
            return True
        except ImportError:
            return False

    def _load_pipeline(self):
        if self._pipeline is not None:
            return
        from diffusers import DiffusionPipeline
        import torch

        device = self.device
        if device == "auto":
            device = "mps" if torch.backends.mps.is_available() else "cpu"

        self._pipeline = DiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if device == "mps" else torch.float32,
            safety_checker=None,
        )
        self._pipeline.to(device)

    def generate(self, prompt: str, negative_prompt: str = "",
                 width: int = 512, height: int = 768,
                 num_inference_steps: int = 25,
                 output_dir: str = "./outputs") -> list[str]:
        self._load_pipeline()
        os.makedirs(output_dir, exist_ok=True)

        result = self._pipeline(
            prompt=[prompt],
            negative_prompt=[negative_prompt] if negative_prompt else None,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
        )

        saved = []
        for i, img in enumerate(result.images):
            ts = int(time.time())
            out_path = os.path.join(output_dir, f"panel_{ts}_{i}.png")
            img.save(out_path)
            saved.append(out_path)

        return saved
