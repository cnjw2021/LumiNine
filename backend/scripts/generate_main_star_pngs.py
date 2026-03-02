import argparse
import os
from typing import Iterable

import cairosvg


def iter_star_numbers() -> Iterable[int]:
    return range(1, 10)


def _normalize_svg_font_family(svg_text: str) -> str:
    # CairoSVGのフォント解決用にCJK JP系のフォント名を優先
    return (
        svg_text
        .replace("Noto Sans JP", "Noto Sans CJK JP")
        .replace("NotoSansJP", "Noto Sans CJK JP")
        .replace("Arial, sans-serif", "Noto Sans CJK JP, sans-serif")
        .replace("Arial", "Noto Sans CJK JP")
        .replace("Inter", "Noto Sans CJK JP")
    )


def convert_svg_to_png(svg_path: str, png_path: str, size: int) -> None:
    with open(svg_path, "rb") as svg_file:
        svg_text = svg_file.read().decode("utf-8")
    svg_text = _normalize_svg_font_family(svg_text)
    png_bytes = cairosvg.svg2png(bytestring=svg_text.encode("utf-8"), output_width=size, output_height=size)
    with open(png_path, "wb") as png_file:
        png_file.write(png_bytes)


def generate_pngs(base_dir: str, size: int) -> None:
    static_dir = os.path.join(base_dir, "apps", "ninestarki", "static")
    svg_root = os.path.join(static_dir, "images", "main_star")
    png_root = os.path.join(static_dir, "images", "main_star_png")

    for sub in ("", "simple"):
        svg_dir = os.path.join(svg_root, sub) if sub else svg_root
        png_dir = os.path.join(png_root, sub) if sub else png_root
        os.makedirs(png_dir, exist_ok=True)

        for star_number in iter_star_numbers():
            svg_path = os.path.join(svg_dir, f"{star_number}.svg")
            png_path = os.path.join(png_dir, f"{star_number}.png")
            if not os.path.exists(svg_path):
                raise FileNotFoundError(f"SVG not found: {svg_path}")
            convert_svg_to_png(svg_path, png_path, size)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PNGs for main star SVGs.")
    parser.add_argument("--size", type=int, default=900, help="Output PNG size in px (square).")
    args = parser.parse_args()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    generate_pngs(base_dir=base_dir, size=args.size)
    print("PNG generation completed.")


if __name__ == "__main__":
    main()
