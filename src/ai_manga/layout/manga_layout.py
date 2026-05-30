"""Manga layout engine.

Arranges generated panels into manga-style page layouts
and adds speech bubbles / text overlays.
"""

import math
import os
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


# Manga reading direction: right-to-left, top-to-bottom
LAYOUTS = {
    "4panel": ["2x2", None],
    "6panel": ["3x2", None],
    "cinematic": ["1x3", None],
}


class MangaLayout:
    """Arrange panels into manga-style pages."""

    def __init__(self, page_width: int = 1080, page_height: int = 1920, direction: str = "rtl"):
        self.page_width = page_width
        self.page_height = page_height
        self.direction = direction  # rtl = right-to-left (manga), ltr = left-to-right (comic)

    def arrange(self, panel_paths: list[str], layout: str = "auto",
                gap: int = 8, output_dir: str = "./outputs") -> list[str]:
        """Arrange panels into manga pages. Returns page image paths."""
        os.makedirs(output_dir, exist_ok=True)

        if not panel_paths:
            return []

        # Determine grid
        if layout == "auto":
            n = len(panel_paths)
            cols = 2
            rows = math.ceil(n / cols)
        elif "x" in layout:
            parts = layout.split("x")
            cols, rows = int(parts[0]), int(parts[1])
        else:
            cols, rows = 2, 2

        panels_per_page = cols * rows
        pages = []

        for page_idx in range(0, len(panel_paths), panels_per_page):
            page_panels = panel_paths[page_idx:page_idx + panels_per_page]
            page_img = self._compose_page(page_panels, cols, rows, gap)
            out_path = os.path.join(output_dir, f"page_{page_idx // panels_per_page:03d}.png")
            page_img.save(out_path)
            pages.append(out_path)

        return pages

    def _compose_page(self, panel_paths: list[str], cols: int, rows: int, gap: int) -> Image.Image:
        """Compose a single manga page."""
        panel_w = (self.page_width - gap * (cols + 1)) // cols
        panel_h = (self.page_height - gap * (rows + 1)) // rows

        page = Image.new("RGB", (self.page_width, self.page_height), "white")

        positions = []
        if self.direction == "rtl":
            # Manga: right-to-left, top-to-bottom
            for row in range(rows):
                for col in range(cols - 1, -1, -1):  # rightmost first
                    x = gap + col * (panel_w + gap)
                    y = gap + row * (panel_h + gap)
                    positions.append((x, y))
        else:
            for row in range(rows):
                for col in range(cols):
                    x = gap + col * (panel_w + gap)
                    y = gap + row * (panel_h + gap)
                    positions.append((x, y))

        for idx, path in enumerate(panel_paths):
            if idx >= len(positions):
                break
            try:
                img = Image.open(path).convert("RGB")
                img = img.resize((panel_w, panel_h), Image.LANCZOS)
                page.paste(img, positions[idx])
            except Exception as e:
                print(f"Warning: could not load {path}: {e}")

        # Draw panel borders
        draw = ImageDraw.Draw(page)
        for x, y in positions[:len(panel_paths)]:
            draw.rectangle([x, y, x + panel_w, y + panel_h], outline="black", width=3)

        return page


class TextBubble:
    """Add speech bubbles and text to panels."""

    def __init__(self, font_path: Optional[str] = None):
        self.font_path = font_path
        self._font = None

    def _get_font(self, size: int = 28) -> ImageFont.FreeTypeFont:
        if self._font is None:
            try:
                self._font = ImageFont.truetype(self.font_path or "/System/Library/Fonts/PingFang.ttc", size)
            except (IOError, OSError):
                self._font = ImageFont.load_default()
        return self._font

    def add_bubble(self, image: Image.Image, text: str, position: str = "bottom",
                   max_width: int = 400) -> Image.Image:
        """Add a speech bubble to an image."""
        draw = ImageDraw.Draw(image)
        font = self._get_font()

        # Wrap text
        words = text
        lines = []
        line = ""
        for char in text:
            test_line = line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width:
                lines.append(line)
                line = char
            else:
                line = test_line
        if line:
            lines.append(line)

        # Calculate bubble size
        line_height = draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]
        bubble_h = line_height * len(lines) + 30
        bubble_w = max(draw.textbbox((0, 0), l, font=font)[2] - draw.textbbox((0, 0), l, font=font)[0] for l in lines) + 30

        img_w, img_h = image.size

        if position == "bottom":
            bx = (img_w - bubble_w) // 2
            by = img_h - bubble_h - 20
        elif position == "top":
            bx = (img_w - bubble_w) // 2
            by = 20
        elif position == "left":
            bx = 20
            by = (img_h - bubble_h) // 2
        else:  # right
            bx = img_w - bubble_w - 20
            by = (img_h - bubble_h) // 2

        # Draw bubble background (white rounded rect)
        draw.rounded_rectangle(
            [bx, by, bx + bubble_w, by + bubble_h],
            radius=12, fill="white", outline="black", width=2
        )

        # Draw text
        for i, line in enumerate(lines):
            tx = bx + 15
            ty = by + 15 + i * line_height
            draw.text((tx, ty), line, fill="black", font=font)

        return image
