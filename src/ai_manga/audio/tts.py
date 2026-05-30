"""TTS & audio mixing module."""

import asyncio
import os
from pathlib import Path
from typing import Optional


class TTSGenerator:
    """Text-to-speech using edge-tts."""

    def __init__(self, voice: str = "zh-CN-XiaoxiaoNeural"):
        self.voice = voice

    async def _generate(self, text: str, output_path: str) -> str:
        import edge_tts
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
        return output_path

    def generate(self, text: str, output_dir: str = "./outputs/audio") -> str:
        """Generate TTS audio file. Returns path."""
        os.makedirs(output_dir, exist_ok=True)
        ts = str(int(__import__("time").time()))
        out_path = os.path.join(output_dir, f"narration_{ts}.mp3")
        return asyncio.run(self._generate(text, out_path))


class AudioMixer:
    """Mix multiple audio tracks (narration + bgm)."""

    def __init__(self, ffmpeg_path: str = "./bin/ffmpeg"):
        self.ffmpeg = ffmpeg_path

    def mix(self, narration_path: str, bgm_path: Optional[str] = None,
            output_path: str = "./outputs/audio/final.mp3") -> str:
        """Mix narration with optional background music."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if bgm_path and os.path.exists(bgm_path):
            import subprocess
            cmd = [
                self.ffmpeg, "-y",
                "-i", narration_path,
                "-i", bgm_path,
                "-filter_complex",
                "[1:a]volume=0.15[a1];[0:a][a1]amix=inputs=2:duration=first",
                output_path
            ]
            subprocess.run(cmd, capture_output=True)
        else:
            import shutil
            shutil.copy2(narration_path, output_path)

        return output_path
