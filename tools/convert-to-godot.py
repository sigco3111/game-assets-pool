#!/usr/bin/env python3
"""
convert-to-godot.py — Wesnoth / Veloren / FreeCiv / OpenTTD / Warzone 에셋을
Godot 4 프로젝트로 import할 .tres (Texture/Resource) 및 .import 파일 생성.

출력: godot-import/<game>/<path>.png.import + .tres
- PNG 원본은 그대로 두고 .import/.tres 만 자동 생성
- 게임 프로젝트의 addons/godot_assets/ 폴더에 복사하면 즉시 사용

사용:
    python3 tools/convert-to-godot.py wesnoth \
        --src extracted/wesnoth/units \
        --out godot-import/wesnoth-units \
        --scene godot-instances
    python3 tools/convert-to-godot.py wop --game warzone --src extracted/warzone/data
"""
import os
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime

# Godot import template — PNG/WebP/JPG/svg generator
GODOT_IMPORT_TEMPLATE_PNG = """[remap]

importer="texture"
type="CompressedTexture2D"
uid="uid://{uid}"
path="res://.godot/imported/{filename}-{hash}.ctex"
metadata={{
"vram_texture": false
}}

[deps]

source_file="res://{relpath}"
dest_files=["res://.godot/imported/{filename}-{hash}.ctex"]

[params]

compress/mode=0
compress/high_quality=false
compress/lossy_quality=0.7
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=true
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=0.0
process/size_limit=0
detect_3d/compress_to=1
"""

GODOT_RESOURCE_2D_TEMPLATE = """[gd_resource type="Texture2D" load_steps=2 format=3]

[ext_resource type="Texture2D" path="res://{relpath}" id="1_texture"]

[resource]
resource_local_to_scene = false
resource_name = "{name}"
_data = {
"diffuse_textures": PackedStringArray("{relpath}"),
"normal_enabled": false,
"roughness_enabled": false,
"rifft_enabled": false,
}

[node name="Sprite2D" type="Sprite2D"]
texture = ExtResource("1_texture")
"""

GODOT_SCENE_TEMPLATE = """[gd_scene load_steps=2 format=3]

[ext_resource type="PackedScene" uid="uid://abc" path="res://{relpath}" id="1"]

[node name="Root" type="Node2D"]
"""


def make_uid(seed: str) -> str:
    """고유 UID 생성 (16바이트 hex)"""
    import hashlib
    h = hashlib.sha1(seed.encode()).hexdigest()[:16]
    # Godot UID 형식: uid://<hex>
    return h + "1234"


def make_hash(content: bytes) -> str:
    import hashlib
    return hashlib.sha256(content).hexdigest()[:8]


def safe_filename(name: str) -> str:
    """Godot-safe 파일명"""
    return ''.join(c if c.isalnum() or c in ('_', '-', '.') else '_' for c in name)


def process_png(src_png: Path, dest_dir: Path, base_path: Path) -> dict:
    """PNG → .import + .tres + .tscn (Sprite2D 씬)"""
    rel = src_png.relative_to(base_path)
    dest_path = dest_dir / rel

    # 안전 파일명 (공백·한글 → ASCII)
    safe_rel = Path(*[safe_filename(p) for p in rel.parts])
    dest_path = dest_dir / safe_rel

    # PNG 위치 계산 — .import 파일은 같은 디렉터리에
    dest_dir.mkdir(parents=True, exist_ok=True)

    # PNG 원본 cp
    target_png = dest_path.with_suffix('.png')
    target_png.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_png, target_png)

    # .import 파일
    import_file = target_png.with_suffix('.png.import')
    relpath = str(safe_rel.with_suffix('.png'))
    uid = make_uid(str(src_png.absolute()))
    with open(import_file, 'w', encoding='utf-8') as f:
        f.write(GODOT_IMPORT_TEMPLATE_PNG.format(
            uid=uid,
            filename=target_png.stem,
            hash=make_hash(str(src_png).encode()),
            relpath=relpath,
        ))

    # Sprite2D 씬
    scene_file = dest_path.with_suffix('.tscn')
    relpath_no_ext = str(safe_rel.with_suffix(''))
    with open(scene_file, 'w', encoding='utf-8') as f:
        f.write(GODOT_SCENE_TEMPLATE.format(relpath=relpath_no_ext + '.tscn'))

    return {
        "src": str(src_png),
        "dst": str(target_png),
        "import": str(import_file),
        "scene": str(scene_file),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=Path, help="원본 에셋 디렉터리")
    ap.add_argument("--out", required=True, type=Path, help="출력 Godot 디렉터리")
    ap.add_argument("--limit", type=int, default=500, help="변환 최대 파일 수")
    ap.add_argument("--skip-frames", action="store_true",
                    help="애니메이션 프레임 (_0.png, _1.png 등) 건너뜀")
    args = ap.parse_args()

    if not args.src.exists():
        print(f"❌ src 디렉터리 없음: {args.src}")
        sys.exit(1)

    print(f"📦 Godot 4 import 변환: {args.src} → {args.out}")
    args.out.mkdir(parents=True, exist_ok=True)

    converted = 0
    skipped = 0

    image_exts = {".png", ".webp", ".jpg", ".jpeg", ".svg"}
    for fp in args.src.rglob("*"):
        if not fp.is_file():
            continue
        ext = fp.suffix.lower()
        if ext not in image_exts:
            continue
        if args.skip_frames and any(s in fp.stem for s in ('_0', '_1', '_2', '_3', '_4', '_5', '_attack-', '_run-', '_idle-')):
            skipped += 1
            continue
        if args.limit and converted >= args.limit:
            print(f"⏹  limit {args.limit} 도달 — 중단")
            break
        result = process_png(fp, args.out, args.src)
        converted += 1
        if converted % 50 == 0:
            print(f"  ⏳ {converted}개 변환...")

    print(f"\n✅ 변환 완료: {converted}개 (스킵: {skipped})")
    print(f"   출력: {args.out}")
    print(f"   다음: 이 디렉터리를 Godot 프로젝트의 root에 cp/sc -r로 복사")


if __name__ == "__main__":
    main()
