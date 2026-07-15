#!/usr/bin/env python3
"""
build-index.py — 워크플로우 통합 인덱스 빌더

1) 큐레이션 14종 README 스캔 (repo submodule + auto-curated)
2) Wenoth sidecar (extracted/wesnoth 안) 스캔
3) 모두 합쳐 metadata/INDEX.json 생성
4) 카테고리·라이선스별 묶음 metadata/INDEX.md 생성

모든 데이터는 REPO 내부에서 가져옴 (외부 의존 0)
   - 큐레이션 = curated/<name>/README.md
   - sidecar = extracted/<game>/*.yaml
   - 자동수집 팩 = free/_curation_cc0_ccby_*.jsonl
"""
import os, json, re, shutil
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent  # game-assets-pool/
CURATED = REPO / "curated"
EXTRACTED = REPO / "extracted"
METADATA = REPO / "metadata"
TOOLS = REPO / "tools"

METADATA.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────
# 1. 큐레이션 README 파싱
# ──────────────────────────────────────────────────────────────────────
def parse_curation(readme: Path, source_name: str):
    if not readme.exists():
        return []
    text = readme.read_text(errors="ignore")
    parts = re.split(r'^#{2,4}\s+', text, flags=re.M)
    cur = "(_intro)"
    items = []
    for chunk in parts:
        nl = chunk.find('\n')
        if nl > 0 and nl < 100:
            cur = chunk[:nl].strip()
        for m in re.finditer(r'\[([^\]]+)\]\(([^\)]+)\)', chunk):
            title, url = m.group(1).strip(), m.group(2).strip()
            if not (url.startswith('http') or url.startswith('/')):
                continue
            items.append({"title": title, "url": url, "section": cur, "source": source_name})
    return items

curations = [
    ("3d-resources", CURATED / "3d-resources" / "README.md"),
    ("awesome-game-engine-dev", CURATED / "awesome-game-engine-dev" / "README.md"),
    ("awesome-opensource-unity", CURATED / "awesome-opensource-unity" / "README.md"),
    ("VoxelAssets", CURATED / "VoxelAssets" / "README.md"),
    ("spritecook-free-game-assets", CURATED / "spritecook-free-game-assets" / "README.md"),
    # 새로 추가된 9종
    ("magictools", CURATED / "magictools" / "README.md"),
    ("GameDev-Resources", CURATED / "GameDev-Resources" / "README.md"),
    ("awesome-unity", CURATED / "awesome-unity" / "README.md"),
    ("awesome-love2d", CURATED / "awesome-love2d" / "README.md"),
    ("awesome-PICO-8", CURATED / "awesome-PICO-8" / "README.md"),
    ("awesome-gamedev", CURATED / "awesome-gamedev" / "README.md"),
    ("awesome-learn-gamedev", CURATED / "awesome-learn-gamedev" / "README.md"),
    ("anything_about_game", CURATED / "anything_about_game" / "README.md"),
    ("awesome-playdate", CURATED / "awesome-playdate" / "README.md"),
]

# ──────────────────────────────────────────────────────────────────────
# 0-prep. auto-collected packs (free/ JSONL)
# ──────────────────────────────────────────────────────────────────────
AUTO_PACKS_JSONL = REPO / "free" / "_curation_cc0_ccby_2026-07-15.jsonl"
auto_packs_meta = []
auto_packs_full = []
if AUTO_PACKS_JSONL.exists():
    try:
        for line in AUTO_PACKS_JSONL.read_text().strip().split("\n"):
            if line.strip():
                e = json.loads(line)
                auto_packs_full.append(e)
                auto_packs_meta.append({
                    "title": e["name"],
                    "url": e["url"],
                    "section": f"Auto: {e['category']}",
                    "source": "auto-cc0",
                })
    except Exception:
        pass
print(f"  auto-collected packs: {len(auto_packs_meta)} (free/ 디렉터리)")

all_cur = list(auto_packs_meta)
for name, path in curations:
    items = parse_curation(path, name)
    print(f"  {name}: {len(items)} links")
    all_cur.extend(items)

# ──────────────────────────────────────────────────────────────────────
# 2. Wesnoth sidecar
# ──────────────────────────────────────────────────────────────────────
def parse_sidecar(yaml_path: Path):
    try:
        import yaml
        with open(yaml_path) as f:
            return yaml.safe_load(f)
    except ImportError:
        return None
    except Exception:
        return None

wesnoth_assets = []
if (EXTRACTED / "wesnoth").exists():
    for yp in (EXTRACTED / "wesnoth").rglob("*.yaml"):
        data = parse_sidecar(yp)
        if data:
            data["_src"] = str(yp.relative_to(EXTRACTED))
            wesnoth_assets.append(data)
print(f"  wesnoth sidecars: {len(wesnoth_assets)}")

# ──────────────────────────────────────────────────────────────────────
# 3. 카테고리·라이선스별 집계
# ──────────────────────────────────────────────────────────────────────
by_section = defaultdict(list)
for it in all_cur:
    by_section[it.get("section") or "_intro"].append(it)

by_category = defaultdict(int)
for a in wesnoth_assets:
    by_category[a.get("category", "asset")] += 1

# ──────────────────────────────────────────────────────────────────────
# 4. JSON 출력
# ──────────────────────────────────────────────────────────────────────
index = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "curation_total": len(all_cur),
    "wesnoth_assets_total": len(wesnoth_assets),
    "wesnoth_by_category": dict(sorted(by_category.items())),
    "by_section": {k: len(v) for k, v in by_section.items()},
    "auto_collected_packs": auto_packs_full,
    "auto_collected_total": len(auto_packs_full),
    "by_license": dict(Counter(it.get("license", "?") for it in all_cur).most_common()),
    "by_source": dict(Counter(it.get("source", "?") for it in all_cur).most_common()),
    "curations": [
        {"name": n, "items": len([x for x in all_cur if x["source"] == n])}
        for n, _ in curations
    ],
    # 전체 큐레이션 (필터링 없이)
    "curation_items": all_cur,
}

(METADATA / "INDEX.json").write_text(json.dumps(index, indent=2, ensure_ascii=False, default=str))
print(f"\n✅ {METADATA / 'INDEX.json'}: {len(all_cur)} 큐레이션 + {len(wesnoth_assets)} Wesnoth")

# ──────────────────────────────────────────────────────────────────────
# 5. 마크다운 INDEX.md
# ──────────────────────────────────────────────────────────────────────
L = []
L.append("# Game Assets Pool — Master Index\n")
L.append(f"**generated**: {index['generated_at']}")
L.append(f"**stats**: {len(all_cur):,} 큐레이션 링크 + {len(wesnoth_assets):,} Wesnoth 에셋 + {len(auto_packs_full)} 자동수집 팩\n")

L.append("\n## 📊 풀 스냅샷\n")
L.append("| 카테고리 | 항목 수 |")
L.append("|---|---:|")
L.append(f"| 큐레이션 유니크 링크 | {len(all_cur):,} |")
L.append(f"| 자동수집 팩 | {len(auto_packs_full):,} |")
L.append(f"| Wesnoth 에셋 (sidecar) | {len(wesnoth_assets):,} |")
total = len(all_cur) + len(wesnoth_assets) + len(auto_packs_full)
L.append(f"| **합계** | **{total:,}** |")

L.append("\n## 🎮 Wesnoth 카테고리별 분포\n")
L.append("| 카테고리 | 수 |")
L.append("|---|---:|")
for k, v in sorted(by_category.items(), key=lambda x: -x[1]):
    L.append(f"| {k} | {v:,} |")

# 큐레이션 상위 섹션
sec_count = Counter(it.get("section", "_") for it in all_cur)
L.append("\n## 📚 큐레이션 섹션 TOP 20\n")
L.append("| 섹션 | 항목 수 |")
L.append("|---|---:|")
for sec, n in sec_count.most_common(20):
    L.append(f"| {sec[:60]} | {n:,} |")

L.append("\n## 🏷 라이선스 표기 정책\n")
L.append("""
| 자원 | 라이선스 | 표기 |
|---|---|---|
| Wesnoth 에셋 | CC-BY-4.0 | 저작자 + 라이선스 + 변경 |
| Veloren | CC-BY-4.0 | 동일 |
| godot-open-rts | MIT | 저작권 고지 |
| 큐레이션 본체 | CC0-1.0 | 표기 선택 |
| 3d-resources 항목들 | UNKNOWN | 사용 전 URL에서 재확인 |

자세한 표기 템플릿: [`docs/CREDIT-TEMPLATES.md`](../docs/CREDIT-TEMPLATES.md)
""")

# 카탈로그 사이트
L.append("\n🌐 카탈로그 사이트: [`site/INDEX.md`](../site/index.html)")

(METADATA / "INDEX.md").write_text("\n".join(L))
joined = "\n".join(L)
print(f"✅ {METADATA / 'INDEX.md'} 생성 ({len(joined)} chars)")
