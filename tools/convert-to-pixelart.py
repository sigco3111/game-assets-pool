#!/usr/bin/env python3
"""
convert-to-pixelart.py — PNG → 32x32 / 64x64 변형 생성

Pillow가 있으면 nearest-neighbor 리사이즈. 없으면 imagemagick (magick) 사용.
"""
import argparse, subprocess, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=Path, help="원본 PNG 디렉터리")
    ap.add_argument("--out", required=True, type=Path, help="출력 디렉터리")
    ap.add_argument("--sizes", default="32,64,128",
                    help="콤마 구분 크기 목록 (예: 32,64,128)")
    ap.add_argument("--limit", type=int, default=500)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    sizes = [int(s) for s in args.sizes.split(",")]

    # Try PIL
    try:
        from PIL import Image
        has_pil = True
    except ImportError:
        has_pil = False

    # Try magick
    has_magick = subprocess.run(["which", "magick"], capture_output=True, text=True).returncode == 0
    has_convert = subprocess.run(["which", "convert"], capture_output=True, text=True).returncode == 0
    use_magick = has_magick or has_convert
    magick_bin = "magick" if has_magick else "convert"

    print(f"📦 Pixelart 변환: {args.src} → {args.out}")
    print(f"   크기: {sizes}")
    print(f"   백엔드: {'PIL' if has_pil else (magick_bin if use_magick else 'none')}")
    if not has_pil and not use_magick:
        print("❌ PIL과 ImageMagick 둘 다 없음 — 설치 필요")
        print("   brew install imagemagick  or  pip install Pillow")
        sys.exit(1)

    converted = 0
    for fp in args.src.rglob("*.png"):
        if args.limit and converted >= args.limit:
            break
        if not fp.is_file():
            continue
        for sz in sizes:
            target_dir = args.out / f"{sz}x{sz}"
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / fp.name
            try:
                if has_pil:
                    img = Image.open(fp)
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    img = img.resize((sz, sz), Image.NEAREST)
                    img.save(target)
                else:
                    # ImageMagick nearest-neighbor
                    cmd = [magick_bin, str(fp), "-filter", "point", "-resize", f"{sz}x{sz}", str(target)]
                    subprocess.run(cmd, capture_output=True, check=False)
            except Exception as e:
                print(f"  ⚠️  {fp.name} → {sz}px 실패: {e}")
                continue
        converted += 1
        if converted % 50 == 0:
            print(f"  ⏳ {converted}개 변환...")

    print(f"\n✅ {converted}개 PNG × {len(sizes)}개 크기 = {converted * len(sizes)}개 출력 파일")
    print(f"   출력: {args.out}")

if __name__ == "__main__":
    main()
