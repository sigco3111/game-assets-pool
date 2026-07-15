#!/usr/bin/env python3
"""
_gen_sidecar.py — 각 추출된 에셋 옆에 YAML sidecar를 생성합니다.

sidecar 예시 (data/core/images/units/elves/swordman.png.yaml):
  source_game: wesnoth
  source_repo: ...
  copyright: "..."
  license_code: ...
  license_assets: ...
  extracted_license: ...
  extracted_at: ...
  filename: swordman.png
  size_bytes: 12345
  category: unit-sprite
  attribution_required: true
  modifications: "none (직접 추출)"
"""
import os, json, argparse, sys
from pathlib import Path
from typing import Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _game_authors import GAME_AUTHORS, CATEGORY_KEYWORDS

def categorize(path_rel: Path, game: str) -> str:
    parts = [s.lower() for s in path_rel.parts]
    kw = CATEGORY_KEYWORDS.get(game, {})
    for k, v in kw.items():
        for p in parts:
            if k in p:
                return v
    return "asset"

def file_size_safe(p: Path) -> int:
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
    out = asset_path.parent / (asset_path.name + ".yaml")
    try:
        import yaml
        out.write_text(yaml.safe_dump(obj, sort_keys=False, allow_unicode=True))
    except ImportError:
        out = asset_path.parent / (asset_path.name + ".json")
        out.write_text(json.dumps(obj, indent=2, ensure_ascii=False))
    return out

SKIP_EXT = {".yaml", ".json", ".md", ".txt", ".gitkeep", ".LICENSE", ".LICENSE.txt", ""}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--dest", required=True, type=Path)
    ap.add_argument("--license", required=True)
    ap.add_argument("--limit", type=int, default=0)
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
        size = file_size_safe(fp)
        if size < 100:
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
