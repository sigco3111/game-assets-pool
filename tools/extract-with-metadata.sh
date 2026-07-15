#!/usr/bin/env bash
# extract-with-metadata.sh — 게임별 추출 + sidecar 생성
# 사용: ./extract-with-metadata.sh <game-name> [source-root] [dest-root]
set -euo pipefail

GAME="${1:-wesnoth}"

GAMEROOT="${HOME}/work/game-assets"
DEST_BASE="${HOME}/work/game-assets-pool/extracted"

# src 디렉토리 전체를 dest 아래로 symlink 트리 복사
symlink_tree() {
  local src="$1"
  local dest="$2"
  if [ ! -d "$src" ]; then return 0; fi
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
    echo "🎯 Battle for Wesnoth (assets: CC-BY)"
    WES_DATA="$SRC_ROOT/data"
    mkdir -p "$DEST_ROOT"/{units,portraits,music,sounds,maps}
    if [ -d "$WES_DATA/core/images/units" ]; then
      symlink_tree "$WES_DATA/core/images/units" "$DEST_ROOT/units"
    fi
    for cd in "$WES_DATA"/campaigns/*/images/units; do
      [ -d "$cd" ] || continue
      campaign=$(basename $(dirname $(dirname "$cd")))
      symlink_tree "$cd" "$DEST_ROOT/units/campaigns/$campaign"
    done
    if [ -d "$WES_DATA/core/images/portraits" ]; then
      symlink_tree "$WES_DATA/core/images/portraits" "$DEST_ROOT/portraits"
    fi
    if [ -d "$WES_DATA" ]; then
      find "$WES_DATA" -type d -name 'music' -not -path '*/.git/*' 2>/dev/null | while IFS= read -r md; do
        rel="${md#${WES_DATA}/}"
        if [[ "$rel" == core/* ]]; then
          target_dir="$DEST_ROOT/music/core/$(basename $md)"
        else
          camp=$(echo "$rel" | cut -d/ -f1)
          target_dir="$DEST_ROOT/music/$camp"
        fi
        mkdir -p "$target_dir"
        find "$md" -maxdepth 2 -type f \( -name '*.ogg' -o -name '*.opus' -o -name '*.wav' \) -size +1k 2>/dev/null | while IFS= read -r f; do
          fname="$(basename "$f")"
          [ ! -e "$target_dir/$fname" ] && [ ! -L "$target_dir/$fname" ] && ln -s "$f" "$target_dir/$fname"
        done
      done
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
          [ ! -e "$target_dir/$fname" ] && [ ! -L "$target_dir/$fname" ] && ln -s "$f" "$target_dir/$fname"
        done
      done
    fi
    python3 "${DEST_BASE%extracted}tools/_gen_sidecar.py" \
      --game wesnoth --license "$LICENSE_LABEL" --dest "$DEST_ROOT"
    ;;

  veloren)
    SRC_ROOT="${2:-${GAMEROOT}/sources/veloren}"
    DEST_ROOT="${3:-${DEST_BASE}/veloren}"
    LICENSE_LABEL="CC-BY-4.0"
    echo "🎯 Veloren (CC-BY)"
    mkdir -p "$DEST_ROOT"/{voxels,items,figures,faces,animations,elements,frames}
    # Veloren 데이터: assets/voxygen/{voxel/*, element/*, face/*, anim/*, figure/*, item/*}
    [ -d "$SRC_ROOT/assets/voxygen/voxel" ] && symlink_tree "$SRC_ROOT/assets/voxygen/voxel" "$DEST_ROOT/voxels"
    [ -d "$SRC_ROOT/assets/voxygen/element" ] && symlink_tree "$SRC_ROOT/assets/voxygen/element" "$DEST_ROOT/elements"
    [ -d "$SRC_ROOT/assets/voxygen/figure" ] && symlink_tree "$SRC_ROOT/assets/voxygen/figure" "$DEST_ROOT/figures"
    if [ -d "$SRC_ROOT/assets/voxygen/face" ]; then
      for inner in "$SRC_ROOT/assets/voxygen/face"/*/; do
        [ -d "$inner" ] || continue
        inner_name="$(basename "$inner")"
        symlink_tree "$inner" "$DEST_ROOT/faces/$inner_name"
      done
    fi
    [ -d "$SRC_ROOT/assets/voxygen/anim" ] && symlink_tree "$SRC_ROOT/assets/voxygen/anim" "$DEST_ROOT/animations"
    [ -d "$SRC_ROOT/assets/voxygen/item" ] && symlink_tree "$SRC_ROOT/assets/voxygen/item" "$DEST_ROOT/items"
    python3 "${DEST_BASE%extracted}tools/_gen_sidecar.py" --game veloren --license "$LICENSE_LABEL" --dest "$DEST_ROOT"
    ;;

  freeciv)
    SRC_ROOT="${2:-${GAMEROOT}/sources/freeciv}"
    DEST_ROOT="${3:-${DEST_BASE}/freeciv}"
    LICENSE_LABEL="GPL-2.0-only"
    echo "🎯 FreeCiv (GPL-2.0)"
    mkdir -p "$DEST_ROOT"/{flags,icons,units,terrain,city,misc,sounds,music,buildings,nations,wonders}
    if [ -d "$SRC_ROOT/data" ]; then
      for sub in flags icons misc terrain improvements units nations wonders rules cities; do
        [ -d "$SRC_ROOT/data/$sub" ] && symlink_tree "$SRC_ROOT/data/$sub" "$DEST_ROOT/$sub"
      done
    fi
    if [ -d "$SRC_ROOT/freeciv/data" ]; then
      [ -d "$SRC_ROOT/freeciv/data/music" ] && symlink_tree "$SRC_ROOT/freeciv/data/music" "$DEST_ROOT/music"
      [ -d "$SRC_ROOT/freeciv/data/sounds" ] && symlink_tree "$SRC_ROOT/freeciv/data/sounds" "$DEST_ROOT/sounds"
    fi
    python3 "${DEST_BASE%extracted}tools/_gen_sidecar.py" --game freeciv --license "$LICENSE_LABEL" --dest "$DEST_ROOT"
    ;;

  openttd)
    SRC_ROOT="${2:-${GAMEROOT}/sources/openttd}"
    DEST_ROOT="${3:-${DEST_BASE}/openttd}"
    LICENSE_LABEL="GPL-2.0-only"
    echo "🎯 OpenTTD (GPL-2.0)"

    mkdir -p "$DEST_ROOT"/{terrain,buildings,vehicles,gui,sounds,music,sprites}
    # OpenTTD assets live in media/baseset/{orig_extra,tren*,}/...
    # PNG 풀 + GRF/OBS file split
    if [ -d "$SRC_ROOT/media/baseset" ]; then
      for inner in "$SRC_ROOT/media/baseset"/*/; do
        [ -d "$inner" ] || continue
        inner_name="$(basename "$inner")"
        case "$inner_name" in
          orig_extra|tren*) symlink_tree "$inner" "$DEST_ROOT/sprites/$inner_name" ;;
          *) ;;
        esac
      done
      # Top level PNG files (아이콘)
      for png in "$SRC_ROOT/media"/openttd.*.png; do
        [ -f "$png" ] && ln -sf "$png" "$DEST_ROOT/gui/$(basename $png)"
      done
    fi
    # 사운드/음악은 별도 디렉터리가 없는 경우가 대부분 — .obs (오디오 ObSet) 처리는 별도 도구 필요
    python3 "${DEST_BASE%extracted}tools/_gen_sidecar.py" --game openttd --license "$LICENSE_LABEL" --dest "$DEST_ROOT"
    ;;

  warzone)
    SRC_ROOT="${2:-${GAMEROOT}/sources/warzone}"
    DEST_ROOT="${3:-${DEST_BASE}/warzone}"
    LICENSE_LABEL="CC-BY-SA-2.0"
    echo "🎯 Warzone 2100 (assets: CC-BY-SA 2.0)"
    mkdir -p "$DEST_ROOT"/{units,structures,terrain,features,weapons,effects,interface,sounds,music}

    # Warzone image 디렉터리는 data/base/images 안에 카테고리별:
    #   units/, structures/, terrain/, features/, weapons/, effects/, frontend/, intfac/, replay/
    if [ -d "$SRC_ROOT/data/base/images" ]; then
      for inner in "$SRC_ROOT/data/base/images"/*/; do
        [ -d "$inner" ] || continue
        inner_name="$(basename "$inner")"
        case "$inner_name" in
          structure*) symlink_tree "$inner" "$DEST_ROOT/structures" ;;
          terrain*) symlink_tree "$inner" "$DEST_ROOT/terrain" ;;
          feature*) symlink_tree "$inner" "$DEST_ROOT/features" ;;
          unit*) symlink_tree "$inner" "$DEST_ROOT/units" ;;
          weapon*) symlink_tree "$inner" "$DEST_ROOT/weapons" ;;
          effect*) symlink_tree "$inner" "$DEST_ROOT/effects" ;;
          frontend|intfac) symlink_tree "$inner" "$DEST_ROOT/interface/$inner_name" ;;
          *) symlink_tree "$inner" "$DEST_ROOT/$inner_name" ;;
        esac
      done
    fi
    [ -d "$SRC_ROOT/data/base/audio" ] && symlink_tree "$SRC_ROOT/data/base/audio" "$DEST_ROOT/sounds"
    [ -d "$SRC_ROOT/data/music" ] && symlink_tree "$SRC_ROOT/data/music" "$DEST_ROOT/music"

    python3 "${DEST_BASE%extracted}tools/_gen_sidecar.py" --game warzone --license "$LICENSE_LABEL" --dest "$DEST_ROOT"
    ;;

  godot-open-rts)
    SRC_ROOT="${2:-${GAMEROOT}/sources/godot-open-rts}"
    DEST_ROOT="${3:-${DEST_BASE}/godot-open-rts}"
    LICENSE_LABEL="MIT"
    echo "🎯 godot-open-rts (MIT)"
    if [ ! -d "$SRC_ROOT" ]; then
      cd "${GAMEROOT}/sources"
      git clone --depth 1 https://github.com/lampe-games/godot-open-rts.git 2>&1 | tail -2
    fi
    mkdir -p "$DEST_ROOT"/{units,buildings,terrain,ui}
    if [ -d "$SRC_ROOT/assets" ]; then
      symlink_tree "$SRC_ROOT/assets" "$DEST_ROOT/assets"
    fi
    python3 "${DEST_BASE%extracted}tools/_gen_sidecar.py" --game godot-open-rts --license "$LICENSE_LABEL" --dest "$DEST_ROOT"
    ;;

  *)
    echo "❌ 알 수 없는 게임: $GAME"
    echo "지원: wesnoth | veloren | freeciv | openttd | warzone | godot-open-rts"
    exit 1
    ;;
esac

echo ""
echo "📊 추출 리포트: ${DEST_ROOT}"
du -sh "$DEST_ROOT" 2>/dev/null
for cat in units portraits music sounds voxels figures faces animations flags icons buildings vehicles terrain structures features weapons effects interface; do
  if [ -d "$DEST_ROOT/$cat" ]; then
    n=$(find "$DEST_ROOT/$cat" -type l 2>/dev/null | wc -l)
    [ "$n" -gt 0 ] && echo "  $cat: $n entries"
  fi
done
n_sides=$(find "$DEST_ROOT" \( -name "*.yaml" -o -name "*.json" \) 2>/dev/null | wc -l)
echo ""
echo "📝 sidecar: $n_sides files"
