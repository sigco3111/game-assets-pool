# Game Assets Pool 🎮

> 게임 개발용 오픈소스 에셋 통합 풀. 라이선스별로 정리되어 있고, **git submodule로 게임 프로젝트에 바로 끌어다 쓸 수 있는** 구조.

> 🚧 **초기 베타**: 현재 큐레이션 인덱스 + Wesnoth sparse-checkout 기반. Kenney 클린 라인업 추가는 진행 중.

## 🚀 빠른 시작

```bash
# submodule로 추가 (특정 라이선스 라인업만)
git submodule add https://github.com/sigco3111/game-assets-pool.git assets
ln -s assets/free/2D/CC0 assets-2d-cc0
ln -s assets/free/3D/CC0 assets-3d-cc0
```

## 📁 디렉터리 구조

```
game-assets-pool/
├── free/                  즉시 사용 가능 (수집된 풀 라이브러리)
│   ├── 2D/{CC0,CC-BY,CC-BY-SA}
│   ├── 3D/{CC0,CC-BY}
│   ├── Audio/             음악 + SFX
│   ├── Tilesets/          타일셋
│   ├── Sprites/
│   ├── UI/
│   ├── Fonts/
│   ├── Voxel/
│   ├── Effects/
│   └── Animations/
├── extracted/             게임 소스에서 추출
│   ├── wesnoth/           Battle for Wesnoth (CC-BY assets / GPL-2.0 code)
│   ├── veloren/
│   └── godot-open-rts/
├── curated/               메타 큐레이션 본문 (인덱싱용)
├── metadata/
│   ├── sidecars/          자동 생성된 에셋별 YAML 메타데이터
│   ├── INDEX.json         전체 인덱스 (6k+ 항목)
│   └── INDEX.md           사람이 보는 인덱스
├── tools/                 인덱스 빌더 + 추출 스크립트
├── site/                  카탈로그 사이트 (정적)
└── docs/                  추가 문서
```

## 🏷 라이선스 표기 정책

| 폴더 | 라이선스 | 표기 |
|---|---|---|
| `free/**/CC0` | CC0-1.0 | 표기 선택 |
| `free/**/CC-BY` | CC-BY-4.0 | 저작자 + 라이선스 + 변경 |
| `free/**/CC-BY-SA` | CC-BY-SA-4.0 | 동일 + 동일 라이선스 |
| `extracted/wesnoth` | GPL-2.0 (코드) / CC-BY (에셋) | 둘 다 분리 표기 |
| `extracted/veloren` | CC-BY | 저작자·라이선스 |
| `extracted/godot-open-rts` | MIT | 저작권 고지 |

자세한 표기 템플릿: [`docs/CREDIT-TEMPLATES.md`](docs/CREDIT-TEMPLATES.md)

## 🎮 용도

- **신속한 게임 프로토타이핑** — CC0 라인업만 골라 상용 게임에서 표기 없이 사용 가능
- **정책/전략 톤 게임** — Wesnoth·Veloren 양식화된 일러스트
- **2D 픽셀 아트** — 게임잼·SDL/Pygame/Godot 즉시 import

## 📊 현재 풀 규모

- 큐레이션 5종 → 6,158개 유니크 링크
- **자동 수집 CC0 팩 20종** (KayKit 8종, Nieobie, Pixelicons, VoxelAssets 등)
- **Wesnoth 22,827개 자산 (sparse-checkout) → 10,327개 symlink + 1,088 sidecar YAML**
- 추출·정리된 실제 에셋은 `metadata/INDEX.md` 참조

## ⚡ Quick fetch

```bash
# 검증된 CC0/CC-BY 무료 팩 20개 자동 다운로드 + 카테고리별 분류
bash tools/fetch-cc0-assets.sh
# 캐시: .cache/downloads/*.zip (~1.2GB)
```

## 🔄 인덱스 재생성

```bash
python3 tools/build-index.py     # 전체 인덱스 JSON + Markdown
python3 tools/build-credits.py   # CREDITS.md 자동 생성
```

## 📜 라이선스

이 저장소 자체의 코드·도구·문서는 **CC0-1.0**. 포함된 third-party 에셋은 각자 라이선스 따름.
