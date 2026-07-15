# 📜 게임 에셋 라이선스 표기 템플릿

> 게임 배포 시 **반드시** 표시해야 하는 라이선스 표기 표준.
> 각 에셋을 게임 디렉터리에 넣을 때, **이 표준에 맞춰 만든 `CREDITS.md`** 를 게임에 같이 동봉합니다.

---

## ▶ 라이선스별 표준 표기

### 1) CC0-1.0 / Public Domain _(Kenney 등)_

표기는 **선택**(권장). 표시할 때:

```
Asset: [Resource Name]
Source: https://[URL]
License: CC0-1.0 (Public Domain Dedication)
Author: [Author]
```

### 2) CC-BY-4.0 _(Wesnoth 에셋, Veloren 등)_

**필수** 표기 — 다음 4가지 정보 모두 표시:

```
[Resource Name] © [Author] [Year]
Licensed under CC-BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
Source: [URL]
Modifications: [Yes/No — 무엇을 바꿨는지]
```

게임 내 "설정 → 크레딧" 페이지에 동일 형식 적용.

### 3) CC-BY-SA-4.0 _(Flare 등)_ 

**CC-BY와 같지만 + 동일 라이선스 의무** — 게임이 이를 따라야 할 수도 있음:

```
[Resource Name] © [Author] [Year]
Licensed under CC-BY-SA-4.0 (https://creativecommons.org/licenses/by-sa/4.0/)
Source: [URL]
Modifications: Yes — [brief description]
```

> ⚠️ 게임 전체에 SA 적용해야 하면 상업 배포가 어려워질 수 있음. SA 자원만 따로 분리해서 사용 권장.

### 4) GPL-2.0 / GPL-3.0 _(Wesnoth/Freeciv/Warzone 코드)_

코드를 게임에 **링크**하면 게임도 GPL 공개 의무 — 에셋만 쓸 것.

```
This game uses artwork extracted from [Game Name], © [Authors].
Artwork licensed GPL-2.0 / CC-BY (mixed — see COPYING).
Game source code: unaffected by artwork usage.
```

### 5) MIT / BSD / Apache-2.0

```
[Resource Name] © [Copyright Holder]
Licensed under [MIT|BSD-3-Clause|Apache-2.0]
License text: see third_party_licenses/[name].LICENSE.txt
```

LICENSE 원문 파일을 게임 `third_party_licenses/` 폴더에 동봉.

---

## ▶ 게임별 자동 CREDIT 메타 정보

### Wesnoth (data/)
- **저작권**: Copyright © 2003-2026 Wesnoth development team
- **코드**: GPL-2.0 (`COPYING.txt`)
- **에셋**: CC-BY ("The Battle for Wesnoth" 로고 + mainline art)
- **저작자표시 의무**: 있음 — 게임 내 표시 필요
- **상업 이용**: 가능

### Veloren
- **저작권**: Veloren contributors
- **에셋**: CC-BY
- **상업 이용**: 가능, 저작자 표기 권장

### godot-open-rts (lampe-games)
- **저작권**: lampe-games
- **전체**: MIT → 에셋 자유 사용 가능, 저작권 고지만 표시

---

## ▶ 자동 생성 스크립트

`index/build_index.py` 와 함께 사용:

```bash
python3 index/build_index.py              # INDEX.md / INDEX.json 재생성
python3 index/build_credits.py            # credits/CREDITS.md 생성 (게임 디렉터리 동봉용)
python3 index/build_credits.py --out ../../my-game/CREDITS.md
```

`build_credits.py` 는 `sources/` 와 `curated/` 의 COPYING/LICENSE 를 자동으로 스캔해서
**per-source CREDITS 섹션**을 만들어 줍니다.

---

## ▶ 검증 절차

1. 게임 빌드 후 `CREDITS.md` 반드시 동봉 (`.zip`/`.dmg`/AppImage 패키지 모두)
2. 게임 내 "크레딧" 또는 "정보" 화면에 동일 텍스트 노출
3. 상업 배포일수록 **공식 라이선스 URL** + **저작자 + 변경 사항** 표시

> 가이드 출처: [Creative Commons License Chooser](https://chooser-beta.creativecommons.org/?lang=ko),
> [GPL FAQ](https://www.gnu.org/licenses/gpl-faq.html)
