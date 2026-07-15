# Game Assets Pool 🎮

> 게임 개발용 오픈소스 에셋 통합 풀. 라이선스별로 정리되어 있고, **git submodule로 게임 프로젝트에 바로 끌어다 쓸 수 있는** 구조.

<div align="center">

🎯 **[라이브 카탈로그 · GitHub Pages](https://sigco3111.github.io/game-assets-pool/)**

</div>

<div align="center">

![Stars](https://img.shields.io/github/stars/sigco3111/game-assets-pool?style=for-the-badge)
![License](https://img.shields.io/github/license/sigco3111/game-assets-pool?style=for-the-badge)
![CC0](https://img.shields.io/badge/code%20license-CC0--1.0-blue?style=for-the-badge)
![Pages](https://img.shields.io/badge/hosting-GitHub%20Pages-blue?style=for-the-badge&logo=github)

</div>

---

## 🌐 라이브 사이트

| | |
|---|---|
| **GitHub Pages 카탈로그** | [sigco3111.github.io/game-assets-pool](https://sigco3111.github.io/game-assets-pool/) |

GitHub Actions의 `pages.yml` 워크플로우가 main 브랜치 push 시 사이트를 자동 빌드 + 배포합니다. **새 CC0 팩을 추가하거나 sidecar를 갱신해도 push만 하면 자동으로 사이트가 갱신됩니다.**

---

## 🚀 빠른 시작

```bash
# 게임 프로젝트에 submodule로 추가
git submodule add https://github.com/sigco3111/game-assets-pool.git assets

# 원하면 특정 카테고리만 symlink
ln -s assets/free/2D/CC0 assets-2d-cc0
ln -s assets/free/3D/CC0 assets-3d-cc0
ln -s assets/extracted/wesnoth/units assets-wesnoth-units
```

게임 빌드 시 `assets/CREDITS.md` + 게임 내 "Credits" 화면에 라이선스 동봉 ([표기 템플릿](docs/CREDIT-TEMPLATES.md)).

---

## 📁 디렉터리 구조

```
game-assets-pool/
├── free/                  자동 다운로드 CC0/CC-BY 무료 팩 19종 (SOURCE.md만 추적, .cache에서 fetch)
│   ├── 2D/{CC0}
│   ├── 3D/CC0              KayKit 7종, PHI-LABS, Kimbatt, devanshutak25 등
│   ├── Audio/CC-BY
│   ├── UI/CC0              Nieobie game-icon-pack
│   ├── Voxel/CC-BY         Phyronnaz VoxelAssets
│   └── Catalog/CC0
├── extracted/             게임 소스에서 추출 (symlink + sidecar YAML)
│   ├── wesnoth/           Battle for Wesnoth (CC-BY assets / GPL-2.0 code) — 1,088 sidecar
│   ├── freeciv/           FreeCiv (GPL-2.0) — 2,988 sidecar
│   ├── warzone/           Warzone 2100 (CC-BY-SA 2.0) — 730 sidecar
│   ├── openttd/           OpenTTD (GPL-2.0) — 19 sidecar
│   ├── veloren/           Veloren (CC-BY, sparse) — 55 sidecar
│   └── godot-open-rts/    (MIT) 메타만
├── curated/               메타 큐레이션 (clone + submodule 3종)
│   ├── 3d-resources, magictools, GameDev-Resources, ...
├── metadata/
│   ├── INDEX.json         11,306 링크 + 4,528 sidecar 통합 인덱스
│   └── INDEX.md           사람이 읽는 인덱스
├── tools/                 자동화 도구 8종 (인덱스빌더, 사이트생성, 추출, 엔진 import)
├── site/                  GitHub Pages 카탈로그 (단일 HTML 295KB, Actions 자동 빌드+배포)
├── docs/CREDIT-TEMPLATES.md  라이선스 표기 표준
└── .github/workflows/pages.yml  Pages 자동 배포 (push trigger)
```

---

## 🏷 라이선스 표기 정책

| 폴더 | 라이선스 | 표기 의무 |
|---|---|---|
| `free/**/CC0` | CC0-1.0 | 표기 선택 |
| `free/**/CC-BY` | CC-BY-4.0 | 저작자 + 라이선스 + 변경 |
| `free/**/CC-BY-SA` | CC-BY-SA-4.0 | 동일 + 동일 라이선스 |
| `extracted/wesnoth` | GPL-2.0 (코드) / CC-BY (에셋) | **둘 다 분리 표기** |
| `extracted/freeciv` | GPL-2.0-only | LICENSE 소스 공개 |
| `extracted/warzone` | CC-BY-SA-2.0 (에셋) | 동일 라이선스 |
| `extracted/veloren` | CC-BY | 저작자·라이선스 |
| `extracted/openttd` | GPL-2.0-only | LICENSE + 사운드 별도 |
| `extracted/godot-open-rts` | MIT | 저작권 고지 |

자세한 표기 템플릿: [`docs/CREDIT-TEMPLATES.md`](docs/CREDIT-TEMPLATES.md)

---

## 📊 풀 규모 (2026-07-15 기준)

| 메트릭 | 수치 |
|---|---:|
| 큐레이션 메타리스트 | **14개** |
| 유니크 링크 | **11,306개** |
| 자동 수집 CC0/CC-BY 팩 | **19개** (KayKit 7, Nieobie, PHI-LABS, Kimbatt, Phyronnaz Voxel 등) |
| 추출 게임 소스 | **5종** (Wesnoth, FreeCiv, Warzone 2100, Veloren, OpenTTD) |
| 에셋 sidecar YAML 메타 | **4,528개** |
| 자동화 도구 | **8종** |
| 라이브 카탈로그 사이트 | **1개** (GitHub Pages) |

**캐시 디스크 사용** (gitignored, 재생성 가능):
- `free/*/` 실제 에셋: ~1GB (KayKit 7종 + Nieobie + 나머지)
- `extracted/wesnoth/data` sparse-checkout: 1.1GB
- `.cache/downloads/` ZIP 캐시: ~1.2GB

---

## ⚡ 빠른 사용법

### A) CC0 팩만 즉시 사용 (가장 간단)
```bash
bash tools/fetch-cc0-assets.sh   # 20개 ZIP 다운로드 + 카테고리별 분류
```

### B) 게임 소스 추출 (대용량)
```bash
bash tools/extract-with-metadata.sh wesnoth       # Battle for Wesnoth
bash tools/extract-with-metadata.sh freeciv       # FreeCiv flags/icons
bash tools/extract-with-metadata.sh warzone       # Warzone 2100 units
bash tools/extract-with-metadata.sh veloren       # Veloren voxel
bash tools/extract-with-metadata.sh openttd       # OpenTTD
```

### C) 게임 엔진 import (PNG → Godot/Bevy/PixelArt)
```bash
python3 tools/convert-to-godot.py \
  --src extracted/wesnoth/units \
  --out godot-assets/wesnoth-units \
  --limit 1000           # PNG → .import + .tscn

python3 tools/convert-to-bevy.py \
  --src extracted/wesnoth/units --limit 500

python3 tools/convert-to-pixelart.py \
  --src extracted/wesnoth/units \
  --out godot-assets/wesnoth-pixels \
  --sizes 32,64,128      # nearest-neighbor 리사이즈
```

---

## 🔄 인덱스 & 카탈로그 재생성

```bash
# 1. 메타 큐레이션 + sidecar 통합 인덱스
python3 tools/build-index.py            # metadata/INDEX.{json,md}

# 2. GitHub Pages 카탈로그 사이트
python3 tools/build-site.py             # site/index.html

# 3. 라이선스 자동 표기
python3 tools/build-credits.py          # CREDITS.md (게임 배포 동봉용)
```

GitHub Actions의 `pages.yml`이 main 브랜치 push 시 자동으로 사이트를 빌드 + Pages에 배포합니다.

---

## 🎮 풀 사용 사례

- **신속한 게임 프로토타이핑** — CC0 라인업만 골라 상용 게임에서 표기 없이 사용 가능
- **저전 fantasy / 정치 / 전략 톤 게임** — Wesnoth·Veloren 양식화된 일러스트
- **2D 픽셀 아트** — game jam · Pygame · SDL · Godot 4 즉시 import
- **Godot/Bevy 게임** — `convert-to-*.py`로 자동 변환 후 `addons/godot_assets/`

---

## 📜 라이선스

이 저장소 자체의 **코드·도구·문서는 CC0-1.0** ([LICENSE](LICENSE)).
포함된 **third-party 에셋은 각자 라이선스 따름** — 각 자산 폴더의 `LICENSE` 파일 또는 `SOURCE.md` 참조.

게임 상업 배포 시: 사용한 자원의 라이선스를 빌드에 동봉하고, 게임 내 "Credits" 화면에 표기.

---

<div align="center">

<sub>
생성/갱신 도구: <code>tools/build-index.py</code> · <code>tools/build-site.py</code> · GitHub Actions 자동 페이지 빌드<br>
<sub>
</sub></sub>

</div>
