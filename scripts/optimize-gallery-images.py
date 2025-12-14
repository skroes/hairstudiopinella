#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Toolchain:
    sips: str
    cwebp: str
    avifenc: str


def _which(name: str) -> str | None:
    return shutil.which(name)


def require_toolchain() -> Toolchain:
    sips = _which("sips")
    cwebp = _which("cwebp")
    avifenc = _which("avifenc")

    missing = [name for name, path in (("sips", sips), ("cwebp", cwebp), ("avifenc", avifenc)) if not path]
    if missing:
        missing_str = ", ".join(missing)
        raise SystemExit(
            f"Missing required tools: {missing_str}\n"
            "- macOS ships with `sips`\n"
            "- Install WebP: `brew install webp`\n"
            "- Install AVIF: `brew install libavif`"
        )

    return Toolchain(sips=sips, cwebp=cwebp, avifenc=avifenc)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate responsive AVIF/WebP/JPEG variants for gallery images.\n"
            "Defaults are tailored to this repo: images/inner_images -> images/inner_images_opt."
        )
    )
    parser.add_argument(
        "--input",
        default="images/inner_images",
        help="Input directory (relative to repo root unless absolute).",
    )
    parser.add_argument(
        "--output",
        default="images/inner_images_opt",
        help="Output directory (relative to repo root unless absolute).",
    )
    parser.add_argument(
        "--widths",
        default="320,640,960,1600",
        help="Comma-separated target widths (px). Example: 320,640,960,1600",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=72,
        help="JPEG quality (sips formatOptions, 0-100).",
    )
    parser.add_argument(
        "--webp-quality",
        type=int,
        default=75,
        help="WebP quality (cwebp -q, 0-100).",
    )
    parser.add_argument(
        "--avif-quality",
        type=int,
        default=45,
        help="AVIF quality (avifenc -q, 0-100; lower = smaller).",
    )
    parser.add_argument(
        "--avif-speed",
        type=int,
        default=6,
        help="AVIF speed (avifenc --speed, 0=slowest..10=fastest).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate even if outputs are up-to-date.",
    )
    return parser.parse_args(argv)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return repo_root() / path


def parse_widths(widths_str: str) -> list[int]:
    widths: list[int] = []
    for part in widths_str.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            widths.append(int(part))
        except ValueError as exc:
            raise SystemExit(f"Invalid --widths value: {widths_str}") from exc

    widths = sorted({w for w in widths if w > 0})
    if not widths:
        raise SystemExit("No valid widths provided.")
    return widths


def sips_get_pixel_width(sips: str, image_path: Path) -> int:
    proc = subprocess.run(
        [sips, "-g", "pixelWidth", str(image_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("pixelWidth:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError(f"Could not parse pixelWidth for {image_path}")


def target_widths(original_width: int, requested: list[int]) -> list[int]:
    max_requested = max(requested)
    widths = [w for w in requested if w < original_width]
    widths.append(original_width if original_width <= max_requested else max_requested)
    return sorted(set(widths))


def up_to_date(source: Path, outputs: Iterable[Path]) -> bool:
    source_mtime = source.stat().st_mtime
    for out in outputs:
        if not out.exists():
            return False
        if out.stat().st_mtime < source_mtime:
            return False
    return True


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def optimize_one(
    tools: Toolchain,
    source: Path,
    output_dir: Path,
    requested_widths: list[int],
    *,
    jpeg_quality: int,
    webp_quality: int,
    avif_quality: int,
    avif_speed: int,
    overwrite: bool,
) -> tuple[int, int]:
    original_width = sips_get_pixel_width(tools.sips, source)
    widths = target_widths(original_width, requested_widths)

    generated = 0
    skipped = 0

    for w in widths:
        stem = source.stem
        out_jpg = output_dir / f"{stem}-{w}.jpg"
        out_webp = output_dir / f"{stem}-{w}.webp"
        out_avif = output_dir / f"{stem}-{w}.avif"

        if not overwrite and up_to_date(source, (out_jpg, out_webp, out_avif)):
            skipped += 1
            continue

        # JPEG (resized/compressed)
        if overwrite or (not out_jpg.exists()) or out_jpg.stat().st_mtime < source.stat().st_mtime:
            run(
                [
                    tools.sips,
                    "--resampleWidth",
                    str(w),
                    "-s",
                    "formatOptions",
                    str(jpeg_quality),
                    str(source),
                    "--out",
                    str(out_jpg),
                ]
            )

        # WebP (from resized JPEG)
        if overwrite or (not out_webp.exists()) or out_webp.stat().st_mtime < out_jpg.stat().st_mtime:
            run(
                [
                    tools.cwebp,
                    "-quiet",
                    "-q",
                    str(webp_quality),
                    "-metadata",
                    "none",
                    str(out_jpg),
                    "-o",
                    str(out_webp),
                ]
            )

        # AVIF (from resized JPEG)
        if overwrite or (not out_avif.exists()) or out_avif.stat().st_mtime < out_jpg.stat().st_mtime:
            run(
                [
                    tools.avifenc,
                    "--jobs",
                    "all",
                    "--speed",
                    str(avif_speed),
                    "-q",
                    str(avif_quality),
                    "--ignore-exif",
                    "--ignore-xmp",
                    "--ignore-icc",
                    str(out_jpg),
                    str(out_avif),
                ]
            )

        generated += 1

    return generated, skipped


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    tools = require_toolchain()

    input_dir = resolve_path(args.input)
    output_dir = resolve_path(args.output)
    requested_widths = parse_widths(args.widths)

    ensure_dir(output_dir)

    sources = sorted(
        [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    )
    if not sources:
        raise SystemExit(f"No images found in {input_dir}")

    total_generated = 0
    total_skipped = 0

    for src in sources:
        generated, skipped = optimize_one(
            tools,
            src,
            output_dir,
            requested_widths,
            jpeg_quality=args.jpeg_quality,
            webp_quality=args.webp_quality,
            avif_quality=args.avif_quality,
            avif_speed=args.avif_speed,
            overwrite=args.overwrite,
        )
        total_generated += generated
        total_skipped += skipped

    print(f"Done. Generated: {total_generated}, skipped (up-to-date): {total_skipped}")
    print(f"Output directory: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
