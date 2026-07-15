#!/usr/bin/env python3
"""
build_cards.py — metadata/INDEX.json + thumbnails/ 를 머지해서 vercel-catalog/public/data/cards.json 생성.

cards.json:
  {
    "assets": [
      {
        "id": "kaykit-adventurers",
        "title": "KayKit Adventurers",
        "category": "3D/Characters",
        "license": "CC0-1.0",
        "thumbnail": "/thumbnails/kaykit/adventurers.png",
        "description": "...",
        "url": "https://github.com/KayKit-Game-Assets/...",
        "tags": ["low-poly", "characters", "animation"],
        "size_estimate_mb": 24
      },
      ...
    ],
    "stats": { total: N, licensed: M, with_thumbnail: T }
  }
"""
import json, re
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

WORK = Path(__file__).resolve().parent.parent  # game-assets-pool/
THUMB = WORK / "site" / "thumbnails"
OUT = WORK / "site" / "data" / "cards.json"
INDEX = json.loads((WORK / "metadata" / "INDEX.json").read_text())

# 1. 자동 수집 팩 JSONL 읽기 (자세한 메타)
auto_packs = []
jsonl = WORK / "free" / "_curation_cc0_ccby_2026-07-15.jsonl"
if jsonl.exists():
    for line in jsonl.read_text().strip().split("\n"):
        if line.strip():
            e = json.loads(line)
            auto_packs.append(e)

# 2. thumbnail 매핑: 어떤 src_name이 어떤 thumbnail 가지고 있는가
#    id 에서 썸네일 매칭은 단순히 src_name 키 이름으로 검색
THUMB_MAP = {
    # src_name keyword → thumbnail path
    "Adventurers":        "kaykit/adventurers.png",
    "Skeletons":          "kaykit/skeletons.png",
    "City Builder":       "kaykit/city.png",
    "Dungeon Remastered": "kaykit-dungeon/dungeon.png",
    "Medieval Hexagon":   "kaykit/hexagon.png",
    "Prototype Bits":     "kaykit/prototype.png",
    "Restaurant":         "kaykit-restaurant/restaurant.png",
    "Nieobie":            "nieobie/sword.svg",
    "PHI-LABS":           "others/phi-objects.png",
    "Sparklinlabs":       "phaser/superpowers.png",
    "gmgeo":              "others/osmic.svg",
    "mr-breakfast":       "others/prompts.png",
    "tstamborski":        "others/pixel-icons.png",
    "Phyronnaz":          "others/voxel.png",
    "devanshutak25":      "others/3d-resources.png",
    "felladrin":          None,  # README only
    "Kimbatt":            None,
    "Toxsam":             None,
}

# 3. 카드 빌드
cards = []
for p in auto_packs:
    name = p["name"]
    # ID: lowercase + hyphen
    id_ = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

    # 썸네일 매칭
    thumbnail = None
    for keyword, t in THUMB_MAP.items():
        if keyword.lower() in name.lower():
            if t and (THUMB / t).exists():
                thumbnail = f"/thumbnails/{t}"
            break

    # 카테고리 정제 (POD에 어울리는 한국어)
    cat_raw = p["category"]
    cat_pretty = {
        "2D/Pixel-sprites": "2D 스프라이트",
        "2D/Pixel-icons": "2D 아이콘",
        "2D/Prompt-pack": "2D 프롬프트",
        "2D/SVG-icons": "2D SVG 아이콘",
        "2D+3D/Multi": "2D+3D 멀티",
        "3D/Characters": "3D 캐릭터",
        "3D/Props": "3D 소품",
        "3D/Tilesets": "3D 타일셋",
        "3D/Environments": "3D 환경",
        "3D/Catalog": "3D 카탈로그",
        "3D/Objects": "3D 오브젝트",
        "3D/PBR-textures": "3D PBR 텍스처",
        "Audio/Samples": "오디오 샘플",
        "UI/Icons": "UI 아이콘",
        "Voxel": "Voxel",
        "Catalog/Meta-list": "큐레이션 리스트",
    }.get(cat_raw, cat_raw)

    # 태그 (이름에서 추출)
    tags = []
    if "kaykit" in name.lower(): tags.append("KayKit")
    if "td" in cat_raw.lower(): tags.append("Top-Down")
    if "voxel" in cat_raw.lower(): tags.append("Voxel")
    if "png" in (thumbnail or ''): tags.append("Textured")
    if "svg" in (thumbnail or ''): tags.append("Vector")

    cards.append({
        "id": id_,
        "title": name,
        "category": cat_pretty,
        "category_raw": cat_raw,
        "license": p["license"],
        "thumbnail": thumbnail,
        "description": p["notes_kr"],
        "url": p["url"],
        "tags": tags,
        "size_mb": p["size_estimate_mb"],
        "available": thumbnail is not None,
    })

# 4. 큐레이션 인덱스에서 모든 카드 빌드 (11,306 풀 표시)
curation_cards = []
curations = INDEX.get("curation_items", [])
for idx, it in enumerate(curations):
    title = it["title"][:80]
    sec = it.get("section") or "Other"
    sec_short = sec[:60]
    # 카테고리 정제 (이전 build-site.py 키워드)
    title_l = title.lower()
    category = "Other"
    for cat, kws in [
        ("3D", ["3d","model","blender","obj","fbx","gltf","glb","vox"]),
        ("2D", ["2d","sprite","pixel","tile","ui","font","icon"]),
        ("Voxel", ["voxel","magicavoxel"]),
        ("Audio", ["music","sound","sfx","audio","ogg","wav"]),
        ("Game Engine", ["engine","godot","unity","unreal","framework"]),
        ("AI", ["ai","neural","ml","gpt","diffusion"]),
        ("Networking", ["network","multiplayer","server"]),
    ]:
        if any(k in title_l for k in kws):
            category = cat
            break
    curation_cards.append({
        "id": re.sub(r'[^a-z0-9]+', '-', f"link-{title[:50]}-{idx}".lower()).strip('-')[:80],
        "title": title,
        "category": category,
        "category_raw": sec_short,
        "license": "UNKNOWN",
        "thumbnail": None,
        "description": f"{it.get('source','?')} — {sec_short}",
        "url": it["url"],
        "tags": [it.get("source","link")] if it.get("source") else ["link"],
        "size_mb": 0,
        "available": False,
        "is_link_only": True,
    })

# 5. 통계
stats = {
    "total": len(cards) + len(curation_cards),
    "with_thumbnail": sum(1 for c in cards if c["thumbnail"]),
    "linked_resources": len(curation_cards),
    "auto_packs": len(cards),
    "by_category": dict(Counter(c["category"] for c in cards).most_common()),
    "by_license": dict(Counter(c["license"] for c in cards).most_common()),
    "generated_at": datetime.utcnow().isoformat() + "Z",
}

# 6. 출력
out = {
    "stats": stats,
    "assets": cards,
    "links": curation_cards[:1500],  # 풀 큐레이션 11,306에서 상위 1,500 (사이트 부담 균형)
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False))

print(f"✅ cards.json: {len(cards)} assets + {len(curation_cards)} links")
print(f"   thumbnails: {stats['with_thumbnail']}/{stats['auto_packs']}")
print(f"   by_category: {stats['by_category']}")
print(f"   output: {OUT}")
