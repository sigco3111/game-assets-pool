#!/usr/bin/env python3
"""
_gen_sidecar.py — 각 추출된 에셋 옆에 YAML sidecar를 생성합니다.

sidecar 예시 (data/core/images/units/elves/swordman.png.yaml):
  source_game: wesnoth
  source_repo: https://github.com/wesnoth/wesnoth
  copyright: "Copyright © 2003-2026 The Battle for Wesnoth contributors"
  license_code: GPL-2.0-only
  license_assets: CC-BY-4.0
  extracted_license: CC-BY-4.0
  extracted_at: "2026-07-15T..."
  filename: swordman.png
  size_bytes: 12345
  category: unit-sprite
  attribution_required: true
  modifications: "none (직접 추출)"
"""
import os, json, argparse, hashlib, sys
from pathlib import Path
from typing import Optional
from datetime import datetime

GAME_AUTHORS = {
    "wesnoth": {
        "copyright": "Copyright © 2003-2026 The Battle for Wesnoth contributors",
        "license_code": "GPL-2.0-only",
        "license_assets": "CC-BY-4.0",
        "source_repo": "https://github.com/wesnoth/wesnoth",
        "extracted_license": "CC-BY-4.0 (에셋만 추출, 코드 GPL 분리)",
    },
    "veloren": {
        "copyright": "Copyright © Veloren contributors",
        "license_code": "MPL-2.0",
        "license_assets": "CC-BY-4.0",
        "source_repo": "https://gitlab.com/veloren/veloren",
        "extracted_license": "CC-BY-4.0",
    },
    "godot-open-rts": {
        "copyright": "Copyright © lampe-games contributors",
        "license_code": "MIT",
        "license_assets": "MIT",
        "source_repo": "https://github.com/lampe-games/godot-open-rts",
        "extracted_license": "MIT",
    },
}

CATEGORY_KEYWORDS = {
    "wesnoth": {
        "units": "unit-sprite",
        "portraits": "portrait",
        "music": "background-music",
        "sounds": "sfx",
        "terrain": "terrain-tile",
        "items": "item-icon",
    },
    "veloren": {
        "voxel": "voxel-model",
        "item": "item-icon",
        "world": "world-asset",
    },
    "godot-open-rts": {
        "unit": "unit-model",
        "building": "building",
        "terrain": "terrain-texture",
        "ui": "ui-element",
    },
}

def categorize(path_rel: Path, game: str) -> str:
    parts = [s.lower() for s in path_rel.parts]
    kw = CATEGORY_KEYWORDS.get(game, {})
    for k, v in kw.items():
        for p in parts:
            if k in p:
                return v
    return "asset"

def file_size_safe(p: Path) -> int:
    """symlink 따라가서 실제 파일 크기 계산"""
    try:
        if p.is_symlink():
            target = Path(os.path.realpath(p))
            if target.exists():
                return target.stat().st_size
        return p.stat().st_size
    except (OSError, FileNotFoundError):
        return 0

def make_sidecar(asset_path: Path, dest_root: Path, game: str, info: dict) -> Optional[Path]:
    rel = asset_path.relative_to(dest_root)
    cat = categorize(rel, game)
    obj = {
        "source_game": game,
        "source_repo": info["source_repo"],
        "copyright": info["copyright"],
        "license_code": info["license_code"],
        "license_assets": info["license_assets"],
        "extracted_license": info["extracted_license"],
        "extracted_at": datetime.utcnow().isoformat() + "Z",
        "filename": str(asset_path.name),
        "rel_path": str(rel),
        "size_bytes": file_size_safe(asset_path),
        "category": cat,
        "attribution_required": info["license_assets"] not in ("CC0-1.0",),
        "modifications": "none (symlinked from upstream sparse-checkout)",
    }
    # YAML로 우선, 라이브러리 없으면 JSON
    out = asset_path.parent / (asset_path.name + ".yaml")
    try:
        import yaml
        out.write_text(yaml.safe_dump(obj, sort_keys=False, allow_unicode=True))
    except ImportError:
        out = asset_path.parent / (asset_path.name + ".json")
        out.write_text(json.dumps(obj, indent=2, ensure_ascii=False))
    return out

SKIP_EXT = {".yaml", ".json", ".md", ".txt", ".gitkeep", ".LICENSE", ".LICENSE.txt"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--dest", required=True, type=Path)
    ap.add_argument("--license", required=True)
    ap.add_argument("--limit", type=int, default=0, help="sidecar 생성 갯수 상한 (0=무제한)")
    args = ap.parse_args()

    info = GAME_AUTHORS[args.game]
    print(f"📝 {args.game} sidecar 생성 중 → {args.dest}")
    
    sidecars = 0
    skipped = 0
    for fp in args.dest.rglob("*"):
        if fp.is_dir():
            continue
        ext = fp.suffix.lower()
        if ext in SKIP_EXT or fp.name.startswith("."):
            continue
        # 사이즈 확인 (symlink 따라가기)
        size = file_size_safe(fp)
        if size < 100:  # 너무 작음
            skipped += 1
            continue
        out = make_sidecar(fp, args.dest, args.game, info)
        if out:
            sidecars += 1
            if args.limit and sidecars >= args.limit:
                break

    print(f"✅ {sidecars} sidecar 생성 ({skipped} 건너뜀)")

if __name__ == "__main__":
    main()
