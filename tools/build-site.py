#!/usr/bin/env python3
"""
build-site.py — metadata/INDEX.json 을 읽어 정적 카탈로그 사이트 site/ 생성.
- site/index.html : 카드 그리드 + 라이선스 배지 + 검색/필터
- Pure HTML+CSS+JS, GitHub Pages 배포 가능
"""
import json, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
METADATA = REPO / "metadata"
SITE = REPO / "site"

INDEX_JSON = METADATA / "INDEX.json"

data = json.loads(INDEX_JSON.read_text())
curations = data["curation_items"][:6000]

# 카테고리 키워드 → 카탈로그 카테고리 매핑
CATEGORY_KEYWORDS = {
    "2D":            ["2d", "sprite", "pixel", "tile", "spritesheet", "ui", "font", "icon"],
    "3D":            ["3d", "model", "blender", "obj", "fbx", "gltf", "glb", "vox"],
    "Voxel":         ["voxel", "magicavoxel", "magica"],
    "Audio":         ["music", "sound", "sfx", "audio", "ogg", "wav"],
    "Game Engine":   ["engine", "godot", "unity", "unreal", "framework"],
    "Tutorial":      ["tutorial", "course", "book", "learning", "guide"],
    "Tools":         ["tool", "editor", "plugin"],
    "AI":            ["ai", "neural", "ml", "gpt", "diffusion"],
    "Physics":       ["physics", "rigid", "collision"],
    "Networking":    ["network", "multiplayer", "server"],
    "Templates":     ["template", "starter", "boilerplate"],
}

def categorize(title: str) -> str:
    title = title.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        for k in kws:
            if k in title:
                return cat
    return "Other"

# 수집
records = []
for it in curations:
    records.append({
        "title": it["title"][:120],
        "url": it["url"],
        "section": it.get("section", "")[:80],
        "source": it.get("source", ""),
        "category": categorize(it["title"]),
        "license": "UNKNOWN",  # 대부분 라이선스 정보가 마크다운에 없음
    })

# 게임 소스 메타
WESNOTH_COUNT = data["wesnoth_assets_total"]
EXTRA_STATS = {
    "wesnoth_count": WESNOTH_COUNT,
    "wesnoth_by_cat": data["wesnoth_by_category"],
    "curation_total": data["curation_total"],
}

# HTML
HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Game Assets Pool · 카탈로그</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; background: #0f1419; color: #e6e8eb; line-height: 1.5; }
header { background: linear-gradient(135deg, #1e3a5f 0%, #0a1929 100%); padding: 2.5rem 2rem; border-bottom: 2px solid #2a3f5f; }
header h1 { font-size: 2.4rem; margin-bottom: 0.5rem; color: #fff; }
header p { color: #8aa2c0; font-size: 1.05rem; max-width: 800px; }
.container { max-width: 1400px; margin: 0 auto; padding: 1.5rem; }
.controls { background: #1a2332; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; display: grid; grid-template-columns: 1fr auto auto auto; gap: 0.75rem; align-items: center; }
.controls input[type=search], .controls select { background: #0f1a2b; border: 1px solid #2a3f5f; color: #e6e8eb; padding: 0.5rem 0.8rem; border-radius: 6px; font-size: 0.95rem; }
.controls input[type=search] { width: 100%; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { background: linear-gradient(180deg, #1a2332, #15202b); padding: 1rem 1.2rem; border-radius: 8px; border-left: 3px solid #4a90e2; }
.stat-card .num { font-size: 1.8rem; font-weight: 700; color: #fff; }
.stat-card .label { color: #8aa2c0; font-size: 0.85rem; margin-top: 0.25rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 0.9rem; }
.card { background: #1a2332; border: 1px solid #2a3f5f; border-radius: 8px; padding: 0.85rem; transition: all 0.18s; }
.card:hover { border-color: #4a90e2; transform: translateY(-2px); box-shadow: 0 4px 16px rgba(74,144,226,0.18); }
.card-title { color: #e6e8eb; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.5rem; word-break: break-word; line-height: 1.35; }
.card a.card-title-link { color: inherit; text-decoration: none; }
.card a.card-title-link:hover { color: #4a90e2; }
.card-meta { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.6rem; font-size: 0.75rem; }
.badge { padding: 0.18rem 0.45rem; border-radius: 4px; font-size: 0.72rem; font-weight: 600; }
.badge-cat { background: #2a3f5f; color: #8aa2c0; }
.badge-license { background: #1f4e3a; color: #6ce5b3; }
.badge-source { background: #4a3520; color: #f4b884; }
.badge-unknown { background: #4a2020; color: #f48484; }
.wesnoth-section { background: #142028; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }
.wesnoth-section h2 { color: #6ce5b3; margin-bottom: 1rem; }
.wesnoth-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 0.5rem; }
.wesnoth-grid div { background: #1a2332; padding: 0.5rem 0.8rem; border-radius: 6px; text-align: center; }
.wesnoth-grid .num { color: #f4b884; font-size: 1.3rem; font-weight: 700; }
.wesnoth-grid .label { color: #8aa2c0; font-size: 0.8rem; }
.pagination { display: flex; justify-content: center; gap: 0.5rem; margin-top: 1.5rem; }
.pagination button { background: #1a2332; border: 1px solid #2a3f5f; color: #e6e8eb; padding: 0.45rem 0.9rem; border-radius: 6px; cursor: pointer; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
footer { text-align: center; padding: 2.5rem 1rem; color: #5a6b80; font-size: 0.85rem; border-top: 1px solid #2a3f5f; margin-top: 3rem; }
footer a { color: #8aa2c0; text-decoration: none; }
</style>
</head>
<body>
<header>
  <div class="container">
    <h1>🎮 Game Assets Pool</h1>
    <p>오픈소스 게임 에셋 통합 풀. <strong>%CURATION_TOTAL%개 큐레이션 링크</strong> + <strong>%WESNOTH_COUNT%개 Battle for Wesnoth 에셋</strong>이 정리되어 있어요. 게임 프로젝트의 git submodule로 끌어다 쓰세요.</p>
  </div>
</header>

<div class="container">
  <div class="stats">
    <div class="stat-card"><div class="num">%CURATION_TOTAL%</div><div class="label">큐레이션 링크</div></div>
    <div class="stat-card"><div class="num">%WESNOTH_COUNT%</div><div class="label">Wesnoth 에셋 (CC-BY)</div></div>
    <div class="stat-card"><div class="num">6</div><div class="label">추출된 게임</div></div>
    <div class="stat-card"><div class="num">CC0/CC-BY/MIT</div><div class="label">지원 라이선스</div></div>
  </div>

  <div class="wesnoth-section">
    <h2>🐉 Battle for Wesnoth — 카테고리별 분포</h2>
    <div class="wesnoth-grid">
      %WESNOTH_CATS%
    </div>
  </div>

  <div class="controls">
    <input type="search" id="q" placeholder="🔍 제목, URL, 카테고리 검색…">
    <select id="cat">
      <option value="">전체 카테고리</option>
      %CAT_OPTIONS%
    </select>
    <select id="src">
      <option value="">전체 큐레이션</option>
      <option value="3d-resources">3d-resources</option>
      <option value="awesome-game-engine-dev">awesome-game-engine-dev</option>
      <option value="awesome-opensource-unity">awesome-opensource-unity</option>
      <option value="spritecook-free-game-assets">spritecook</option>
      <option value="VoxelAssets">VoxelAssets</option>
    </select>
    <button onclick="reset()" style="background:#2a3f5f;border:none;color:#e6e8eb;padding:0.5rem 1rem;border-radius:6px;cursor:pointer;">초기화</button>
  </div>

  <div class="grid" id="grid"></div>
  <div class="pagination">
    <button id="prev" onclick="prevPage()">‹ 이전</button>
    <span id="pinfo" style="padding:0.5rem 1rem;color:#8aa2c0;"></span>
    <button id="next" onclick="nextPage()">다음 ›</button>
  </div>
</div>

<footer>
  <p><a href="../README.md">README</a> · <a href="../docs/CREDIT-TEMPLATES.md">라이선스 표기 템플릿</a> · <a href="https://github.com/sigco3111/game-assets-pool">GitHub</a></p>
  <p style="margin-top:0.8rem;">이 카탈로그는 자동 생성 — <code>python3 tools/build-site.py</code>로 갱신</p>
</footer>

<script>
const RECORDS = %JSON_DATA%;
const PAGE_SIZE = 60;
let page = 0;

function escapeHtml(s) {
  return (s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function filtered() {
  const q = document.getElementById('q').value.toLowerCase();
  const cat = document.getElementById('cat').value;
  const src = document.getElementById('src').value;
  return RECORDS.filter(r => {
    if (cat && r.category !== cat) return false;
    if (src && r.source !== src) return false;
    if (q) {
      const hay = (r.title + ' ' + r.url + ' ' + (r.section||'')).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
}

function render() {
  const list = filtered();
  const total = list.length;
  const start = page * PAGE_SIZE;
  const end = Math.min(start + PAGE_SIZE, total);
  const slice = list.slice(start, end);

  const grid = document.getElementById('grid');
  if (slice.length === 0) {
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;color:#5a6b80;padding:2rem;">🔍 매치 없음</div>';
  } else {
    grid.innerHTML = slice.map(r => `
      <div class="card">
        <a href="${escapeHtml(r.url)}" target="_blank" class="card-title-link">
          <div class="card-title">${escapeHtml(r.title)}</div>
        </a>
        <div class="card-meta">
          <span class="badge badge-cat">${escapeHtml(r.category)}</span>
          <span class="badge badge-source">${escapeHtml(r.source)}</span>
          <span class="badge badge-unknown">${escapeHtml(r.license)}</span>
        </div>
      </div>
    `).join('');
  }
  document.getElementById('pinfo').textContent = `${(start+1).toLocaleString()}–${end.toLocaleString()} / ${total.toLocaleString()}`;
  document.getElementById('prev').disabled = page === 0;
  document.getElementById('next').disabled = end >= total;
  // 데이터가 끝나면 page=0으로 리셋
  if (start >= total && page > 0) { page = 0; render(); }
}

function prevPage() { if (page > 0) { page--; render(); } }
function nextPage() { page++; render(); }
function reset() { document.getElementById('q').value=''; document.getElementById('cat').value=''; document.getElementById('src').value=''; page=0; render(); }

document.getElementById('q').addEventListener('input', () => { page=0; render(); });
document.getElementById('cat').addEventListener('change', () => { page=0; render(); });
document.getElementById('src').addEventListener('change', () => { page=0; render(); });

render();
</script>
</body>
</html>
"""

# Wesnoth 카테고리
cats_html = ""
for k, v in sorted(EXTRA_STATS["wesnoth_by_cat"].items(), key=lambda x: -x[1]):
    cats_html += f'<div><div class="num">{v:,}</div><div class="label">{k}</div></div>'

# 카테고리 옵션
unique_cats = sorted(set(r["category"] for r in records))
cat_opts = "\n".join(f'<option value="{c}">{c}</option>' for c in unique_cats)

# JSON 데이터 — 너무 크면 페이지가 무거워지니 6000개로 캡
HTML = (HTML
    .replace("%CURATION_TOTAL%", f"{EXTRA_STATS['curation_total']:,}")
    .replace("%WESNOTH_COUNT%", f"{EXTRA_STATS['wesnoth_count']:,}")
    .replace("%WESNOTH_CATS%", cats_html)
    .replace("%CAT_OPTIONS%", cat_opts)
    .replace("%JSON_DATA%", json.dumps(records[:1500], ensure_ascii=False))
)

(SITE / "index.html").write_text(HTML)
print(f"✅ {SITE}/index.html ({len(HTML):,} chars)")
print(f"   카테고리: {len(unique_cats)}개, 카드: {len(records):,}개")
