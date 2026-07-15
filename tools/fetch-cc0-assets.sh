#!/usr/bin/env bash
# fetch-cc0-assets.sh — _curation_cc0_ccby_*.jsonl 의 ZIP URL을 다운로드해서
# 라이선스별·카테고리별 디렉터리로 자동 분류.
# 사용: ./fetch-cc0-assets.sh [jsonl_file]
set -euo pipefail

JSONL="${1:-$HOME/work/game-assets-pool/free/_curation_cc0_ccby_2026-07-15.jsonl}"
REPO="$HOME/work/game-assets-pool"
FREE="$REPO/free"
TMP="$REPO/.cache/downloads"
mkdir -p "$TMP"

if [ ! -f "$JSONL" ]; then
  echo "❌ JSONL 없음: $JSONL"
  exit 1
fi

# 현재 라이선스·카테고리 분류 디렉토리 만들어 두기
mkdir -p "$FREE/3D/CC0" "$FREE/2D/CC0" "$FREE/UI/CC0" "$FREE/Audio/CC0" "$FREE/Voxel/CC0"
mkdir -p "$FREE/CC-BY-SA"  # mixed (VoxelAssets는 CC-BY/CC0 혼재라 별도)

total=$(wc -l < "$JSONL" | tr -d ' ')
echo "📥 $total assets to download"
echo ""

ok=0
fail=0
size_added=0

while IFS= read -r line; do
  # JSONL 한 줄 파싱 — 필드 추출 (jq 없이)
  name=$(echo "$line" | python3 -c "import sys,json;print(json.loads(sys.stdin.read())['name'])")
  url=$(echo "$line" | python3 -c "import sys,json;print(json.loads(sys.stdin.read())['url'])")
  license=$(echo "$line" | python3 -c "import sys,json;print(json.loads(sys.stdin.read())['license'])")
  category=$(echo "$line" | python3 -c "import sys,json;print(json.loads(sys.stdin.read())['category'])")
  size_mb=$(echo "$line" | python3 -c "import sys,json;print(json.loads(sys.stdin.read())['size_estimate_mb'])")

  # 안전 파일명 (특수문자 제거)
  safe_name=$(echo "$name" | tr ' ' '_' | tr -cd 'A-Za-z0-9._-')
  zip_path="$TMP/${safe_name}.zip"

  # 분류 결정
  # 1) 라이선스가 CC-BY/CC-BY-SA 혼재면 CC-BY-SA 디렉터리
  # 2) 카테고리 prefix로 매핑
  case "$category" in
    2D*) target_dir="$FREE/2D/CC0" ;;
    3D*) target_dir="$FREE/3D/CC0" ;;
    UI*) target_dir="$FREE/UI/CC0" ;;
    Audio*) target_dir="$FREE/Audio/CC0" ;;
    Voxel*) target_dir="$FREE/Voxel/CC0" ;;
    Catalog|Catalog/*) target_dir="$FREE/Catalog/CC0" ;;
    *) target_dir="$FREE/_misc/CC0" ;;
  esac

  # mixed 라이선스는 CC-BY-SA 또는 별도 보존
  if [[ "$license" == CC-BY* ]] || [[ "$license" == *CC-BY* ]]; then
    if [[ "$license" == CC0-1.0*CC-BY* ]]; then
      # mixed: 안전하게 CC0 디렉터리 진입 후 별도 NOTICE 동봉
      target_dir="$FREE/Voxel/CC0_with_CC-BY"
      safe_name="${safe_name}_NOTICE"
    fi
  fi

  if [ -d "$target_dir/$safe_name" ]; then
    echo "  ⏩ already exists: $safe_name"
    ok=$((ok+1))
    continue
  fi

  echo "  📥 [$category/$license] $name ($size_mb MB)"
  echo "     → $target_dir/$safe_name/"
  if [ ! -f "$zip_path" ]; then
    curl -fsL --max-time 120 "$url" -o "$zip_path" 2>/dev/null || {
      echo "     ❌ download failed"
      fail=$((fail+1))
      continue
    }
  fi

  mkdir -p "$target_dir/$safe_name"
  unzip -q -o "$zip_path" -d "$target_dir/$safe_name" 2>&1 || {
    # 일부 zip은 첫 디렉터리 prefix 갖음 — 한 단계 들어가고 다시 시도
    inner=$(ls "$target_dir/$safe_name" | head -1)
    if [ -d "$target_dir/$safe_name/$inner" ]; then
      mv "$target_dir/$safe_name/$inner"/* "$target_dir/$safe_name/" 2>/dev/null || true
      rmdir "$target_dir/$safe_name/$inner" 2>/dev/null || true
    fi
  }

  # NOTICE/LICENSE 동봉
  cat > "$target_dir/$safe_name/SOURCE.md" <<NOTICE
# $name

- **출처**: $url
- **다운로드 일**: $(date -I)
- **라이선스**: $license
- **카테고리**: $category
- **메모(원본)**: $(echo "$line" | python3 -c "import sys,json;print(json.loads(sys.stdin.read()).get('notes_kr',''))")

라이선스 표기:
\`\`\`
$(cat <<EOF
$name
© $(date +%Y) 원본 저작자 (라이선스 $license)
Source: $url
\`\`\`
EOF
)
\`\`\`
NOTICE

  # 어느 디렉터리에서 발견되면 그쪽으로 메타데이터 sidecar도 생성 (간소화)
  ok=$((ok+1))
  size_added=$((size_added + size_mb))
done < "$JSONL"

echo ""
echo "=========================================="
echo "  완료: $ok / $total · 추정 ${size_added}MB 누적"
echo "  실패: $fail"
echo "=========================================="
echo ""
echo "📂 트리:"
find "$FREE" -mindepth 1 -maxdepth 2 -type d | sort | head -30
