#!/usr/bin/env python3
"""
build-index.py — 워크플로우 통합 인덱스 빌더

1) 큐레이션 5종 스캔 (~/work/game-assets/curated/)
2) Wenoth data 추출 sidecar (extracted/wesnoth/*)
3) 모두 합쳐 metadata/INDEX.json 생성
4) 카테고리·라이선스별 묶음 metadata/INDEX.md 생성
"""
import os, json, re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent  # game-assets-pool/
SRC = Path(os.path.expanduser("~/work/game-assets"))
CURATED = SRC / "curated"
EXTRACTED = REPO / "extracted"
METADATA = REPO / "metadata"
TOOLS = REPO / "tools"

METADATA.mkdir(parents=True, exist_ok=True)

# ───────────────────────────────────────────────────────────────────
# 1. 큐레이션 읽기
# ───────────────────────────────────────────────────────────────────
def parse_curation(readme: Path, source_name: str):
    """마크다운 큐레이션에서 (title, url, section) 추출"""
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
]

# -----------------------------------------------------------------
# 0-prep. auto-collected packs (free/ 디렉터리에서 fetch된 팩)
# -----------------------------------------------------------------
AUTO_PACKS_JSONL = REPO / "free" / "_curation_cc0_ccby_2026-07-15.jsonl"
auto_packs_meta = []
if AUTO_PACKS_JSONL.exists():
    try:
        for line in AUTO_PACKS_JSONL.read_text().strip().split("\n"):
            if line.strip():
                auto_packs_meta.append({
                    "title": json.loads(line)["name"],
                    "url": json.loads(line)["url"],
                    "section": f"Auto: {json.loads(line)['category']}",
                    "source": f"auto-cc0",
                })
    except Exception:
        pass
print(f"  auto-collected packs: {len(auto_packs_meta)} (free/ 디렉터리)")
all_cur = list(auto_packs_meta)  # 초기화
for name, path in curations:
    items = parse_curation(path, name)
    print(f"  {name}: {len(items)} links")
    all_cur.extend(items)

# ───────────────────────────────────────────────────────────────────
# 2. Wesnoth sidecar
# ───────────────────────────────────────────────────────────────────
def parse_sidecar(yaml_path: Path):
    try:
        import yaml
        with open(yaml_path) as f:
            return yaml.safe_load(f)
    except ImportError:
        # JSON 폴백 가능하지만 너무 자세한 정보 없으니 skip
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

# ───────────────────────────────────────────────────────────────────
# 3. 카테고리·라이선스별 집계
# ───────────────────────────────────────────────────────────────────
by_section = defaultdict(list)
for it in all_cur:
    by_section[it.get("section") or "_intro"].append(it)

by_category = defaultdict(int)
for a in wesnoth_assets:
    by_category[a.get("category", "asset")] += 1

# ───────────────────────────────────────────────────────────────────
# 4. JSON 저장
# ───────────────────────────────────────────────────────────────────
index = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "curation_total": len(all_cur),
    "wesnoth_assets_total": len(wesnoth_assets),
    "wesnoth_by_category": dict(sorted(by_category.items())),
    "by_section": {k: len(v) for k, v in by_section.items()},
    "curations": [
        {"name": n, "items": len([x for x in all_cur if x["source"] == n])}
        for n, _ in curations
    ],
    # 큐레이션 전체 (sample 200개 + section별 grouping)
    "curation_items": all_cur[:6000],
}

(METADATA / "INDEX.json").write_text(json.dumps(index, indent=2, ensure_ascii=False, default=str))
print(f"\n✅ {METADATA / 'INDEX.json'}: {len(all_cur)} 큐레이션 + {len(wesnoth_assets)} Wesnoth")

# ───────────────────────────────────────────────────────────────────
# 5. 마크다운 INDEX.md
# ───────────────────────────────────────────────────────────────────
L = []
L.append("# Game Assets Pool — Master Index\n")
L.append(f"**generated**: {index['generated_at']}")
L.append(f"**stats**: {len(all_cur):,} 큐레이션 링크 + {len(wesnoth_assets):,} Wesnoth 에셋\n")

L.append("\n## 📊 풀 스냅샷\n")
L.append("| 카테고리 | 항목 수 |")
L.append("|---|---:|")
L.append(f"| 큐레이션 유니크 링크 | {len(all_cur):,} |")
L.append(f"| Wesnoth 에셋 (sidecar) | {len(wesnoth_assets):,} |")
L.append(f"| **합계** | **{len(all_cur)+len(wesnoth_assets):,}** |")

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

# 게임 소스별 sidecar 수
L.append("\n## 🔬 게임 소스별 추출\n")
L.append("| 게임 | 라이선스 | 추출 단위 | sidecar |")
L.append("|---|---|---:|---:|")
L.append("| wesnoth | CC-BY (에셋) | units/portraits/music/sounds | {:,} |".format(len(wesnoth_assets)))
L.append("| godot-open-rts | MIT | 메타데이터 only | 0 |")
L.append("| veloren | CC-BY | 미추출 (sparse 미완) | - |")

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
L.append("\n🌐 카탈로그 사이트: [`site/index.html`](../site/index.html)")

joined = "\n".join(L)
(METADATA / "INDEX.md").write_text(joined)
print(f"✅ {METADATA / 'INDEX.md'} 생성 ({len(joined)} chars)")
