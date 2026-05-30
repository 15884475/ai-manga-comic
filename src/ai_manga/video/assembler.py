"""Video assembly module.

Combines manga pages with transitions, narration audio,
and optional subtitles into a final MP4 video.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional


class VideoAssembler:
    """Assemble manga pages + audio into video."""

    FFMPEG_URL = "https://github.com/eugeneware/ffmpeg-static/releases/download/b6.0/ffmpeg-darwin-arm64"

    def __init__(self, ffmpeg_path: Optional[str] = None, fps: int = 30,
                 duration_per_page: float = 5.0):
        self.fps = fps
        self.duration_per_page = duration_per_page

        if ffmpeg_path is None:
            local_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "bin", "ffmpeg")
            if os.path.exists(local_path):
                self.ffmpeg = local_path
            else:
                self.ffmpeg = self._ensure_ffmpeg()
        else:
            self.ffmpeg = ffmpeg_path

    def _ensure_ffmpeg(self) -> str:
        """Download ffmpeg if not present."""
        import stat
        cache_dir = os.path.expanduser("~/.cache/ai-manga")
        os.makedirs(cache_dir, exist_ok=True)
        exe = os.path.join(cache_dir, "ffmpeg")
        if not os.path.exists(exe):
            import urllib.request
            print(f"Downloading ffmpeg to {exe}...")
            urllib.request.urlretrieve(self.FFMPEG_URL, exe)
            st = os.stat(exe)
            os.chmod(exe, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        return exe

    def assemble(self, page_paths: list[str], audio_path: Optional[str] = None,
                 output_path: str = "./outputs/manga_video.mp4") -> str:
        """Assemble pages into video with audio."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if not page_paths:
            raise ValueError("No page images to assemble")

        # Create concat file for ffmpeg (image sequence)
        concat_lines = []
        for p in page_paths:
            abs_p = os.path.abspath(p)
            concat_lines.append(f"file '{abs_p}'")
            concat_lines.append(f"duration {self.duration_per_page}")

        # Last frame needs extra entry for correct duration
        concat_lines.append(f"file '{os.path.abspath(page_paths[-1])}'")

        concat_path = "/tmp/manga_concat.txt"
        with open(concat_path, "w") as f:
            f.write("\n".join(concat_lines))

        cmd = [
            self.ffmpeg, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_path,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", str(self.fps),
        ]

        if audio_path and os.path.exists(audio_path):
            cmd.extend(["-i", audio_path])
            cmd.extend(["-c:a", "aac", "-shortest"])
        else:
            cmd.extend(["-an"])

        cmd.append(output_path)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        return output_path

    def add_subtitles(self, video_path: str, subtitles: list[dict],
                      output_path: str) -> str:
        """Add subtitle SRT to video."""
        srt_lines = []
        for i, sub in enumerate(subtitles, 1):
            start = sub.get("start", 0)
            end = sub.get("end", start + 3)
            text = sub.get("text", "")

            def to_srt(seconds):
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                s = int(seconds % 60)
                ms = int((seconds - int(seconds)) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            srt_lines.append(str(i))
            srt_lines.append(f"{to_srt(start)} --> {to_srt(end)}")
            srt_lines.append(text)
            srt_lines.append("")

        srt_path = "/tmp/manga_subs.srt"
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines))

        cmd = [
            self.ffmpeg, "-y",
            "-i", video_path,
            "-i", srt_path,
            "-c", "copy",
            "-c:s", "mov_text",
            output_path
        ]
        subprocess.run(cmd, capture_output=True)
        return output_path
