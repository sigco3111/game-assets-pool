#!/usr/bin/env bash
# extract-with-metadata.sh — 게임별 추출 + sidecar 생성
# 사용: ./extract-with-metadata.sh <game-name> [source-root] [dest-root]
set -euo pipefail

GAME="${1:-wesnoth}"

# 기본 경로
GAMEROOT="${HOME}/work/game-assets"
DEST_BASE="${HOME}/work/game-assets-pool/extracted"

# 함수: src 디렉토리 전체를 dest 아래로 symlink 트리 복사
# 인자: $1=src, $2=dest
symlink_tree() {
  local src="$1"
  local dest="$2"
  if [ ! -d "$src" ]; then
    echo "⚠️  src 없음: $src"
    return 1
  fi
  find "$src" -mindepth 1 \( -type d -o -type f \) -print0 | while IFS= read -r -d $'\0' entry; do
    rel="${entry#$src/}"
    target="$dest/$rel"
    if [ ! -e "$target" ] && [ ! -L "$target" ]; then
      mkdir -p "$(dirname "$target")"
      ln -s "$entry" "$target"
    fi
  done
}

case "$GAME" in
  wesnoth)
    SRC_ROOT="${2:-${GAMEROOT}/sources/wesnoth}"
    DEST_ROOT="${3:-${DEST_BASE}/wesnoth}"
    LICENSE_LABEL="CC-BY-4.0"
    echo "🎯 Battle for Wesnoth"
    echo "   src:  $SRC_ROOT"
    echo "   dest: $DEST_ROOT"
    echo "   license (assets): $LICENSE_LABEL"
    WES_DATA="$SRC_ROOT/data"

    mkdir -p "$DEST_ROOT"/{units,portraits,music,sounds,maps}

    # 1. 메인라인 유닛
    echo "📸 유닛 (depth 1만 — campaigns는 너무 깊음)"
    if [ -d "$WES_DATA/core/images/units" ]; then
      symlink_tree "$WES_DATA/core/images/units" "$DEST_ROOT/units"
    fi
    # 각 캠페인별 유닛 (간단히 depth 1 한정)
    echo "📸 캠페인 유닛"
    for cd in "$WES_DATA"/campaigns/*/images/units; do
      [ -d "$cd" ] || continue
      campaign=$(basename $(dirname $(dirname "$cd")))
      symlink_tree "$cd" "$DEST_ROOT/units/campaigns/$campaign"
    done

    # 2. 포터레이트
    echo "🎭 포터레이트"
    if [ -d "$WES_DATA/core/images/portraits" ]; then
      symlink_tree "$WES_DATA/core/images/portraits" "$DEST_ROOT/portraits"
    fi

    # 3. 음악
    echo "🎵 음악"
    if [ -d "$WES_DATA" ]; then
      find "$WES_DATA" -type d -name 'music' -not -path '*/.git/*' 2>/dev/null | while IFS= read -r md; do
        # 첫 ancestor 캠페인 이름 가져오기
        rel="${md#${WES_DATA}/}"
        # 핵심 + 캠페인 디렉토리 prefix 매핑
        if [[ "$rel" == core/* ]]; then
          target_dir="$DEST_ROOT/music/core/$(basename $md)"
        else
          camp=$(echo "$rel" | cut -d/ -f1)
          target_dir="$DEST_ROOT/music/$camp"
        fi
        mkdir -p "$target_dir"
        find "$md" -maxdepth 2 -type f \( -name '*.ogg' -o -name '*.opus' -o -name '*.wav' \) -size +1k 2>/dev/null | while IFS= read -r f; do
          fname="$(basename "$f")"
          if [ ! -e "$target_dir/$fname" ] && [ ! -L "$target_dir/$fname" ]; then
            ln -s "$f" "$target_dir/$fname"
          fi
        done
      done
    fi

    # 4. 사운드
    echo "🔊 사운드"
    if [ -d "$WES_DATA" ]; then
      find "$WES_DATA" -type d -name 'sounds' -not -path '*/.git/*' 2>/dev/null | while IFS= read -r sd; do
        rel="${sd#${WES_DATA}/}"
        if [[ "$rel" == core/* ]]; then
          target_dir="$DEST_ROOT/sounds/core"
        else
          camp=$(echo "$rel" | cut -d/ -f1)
          target_dir="$DEST_ROOT/sounds/$camp"
        fi
        mkdir -p "$target_dir"
        find "$sd" -maxdepth 4 -type f \( -name '*.ogg' -o -name '*.wav' -o -name '*.opus' \) -size +1k 2>/dev/null | while IFS= read -r f; do
          fname="$(basename "$f")"
          if [ ! -e "$target_dir/$fname" ] && [ ! -L "$target_dir/$fname" ]; then
            ln -s "$f" "$target_dir/$fname"
          fi
        done
      done
    fi

    # 5. 메타데이터
    echo "📝 sidecar 생성"
    python3 "${DEST_BASE%extracted}tools/_gen_sidecar.py" \
      --game wesnoth --license "$LICENSE_LABEL" \
      --dest "$DEST_ROOT"
    ;;

  godot-open-rts)
    SRC_ROOT="${2:-${GAMEROOT}/sources/godot-open-rts}"
    DEST_ROOT="${3:-${DEST_BASE}/godot-open-rts}"
    LICENSE_LABEL="MIT"
    echo "🎯 godot-open-rts (MIT)"
    if [ ! -d "$SRC_ROOT" ]; then
      cd "${GAMEROOT}/sources"
      git clone --depth 1 https://github.com/lampe-games/godot-open-rts.git 2>&1 | tail -2
      cd - > /dev/null
    fi
    mkdir -p "$DEST_ROOT"/{units,buildings,terrain,ui}
    if [ -d "$SRC_ROOT/assets" ]; then
      symlink_tree "$SRC_ROOT/assets" "$DEST_ROOT/assets"
    fi
    python3 "${DEST_BASE%extracted}tools/_gen_sidecar.py" --game godot-open-rts --license "$LICENSE_LABEL" --dest "$DEST_ROOT"
    ;;

  *)
    echo "❌ 알 수 없는 게임: $GAME"
    echo "지원: wesnoth | godot-open-rts"
    exit 1
    ;;
esac

# 결과
echo ""
echo "📊 추출 리포트:"
du -sh "$DEST_ROOT"/* 2>/dev/null

# 카운트
for cat in units portraits music sounds; do
  if [ -d "$DEST_ROOT/$cat" ]; then
    n=$(find "$DEST_ROOT/$cat" -type l 2>/dev/null | wc -l)
    echo "  $cat: $n entries"
  fi
done

# 사이드카 카운트
n_sides=$(find "$DEST_ROOT" -name "*.yaml" -o -name "*.json" | wc -l)
echo ""
echo "📝 sidecar: $n_sides files"
