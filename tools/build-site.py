"""
build-site.py — placeholder, see site/index.html
(Vercel-catalog UI moved directly into site/index.html via build_cards.py → cards.json + thumbnails/)
"""
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"

# Quick: rebuild HTML with current build-cards.py output + Vercel-style cards
INDEX_HTML = (REPO / "vercel-catalog" / "public" / "index.html").read_text() if (REPO / "vercel-catalog" / "public" / "index.html").exists() else ""

print("⚠️  이 build-site.py는 deprecated. build-cards.py가 cards.json 생성하며")
print("   site/index.html (Vercel 디자인)은 직접 수동 유지합니다.")
print("   빌드 명령: python3 tools/build-cards.py")
print("   git:  cd ~/work/game-assets-pool && git add site/ && git commit -m '...'")
