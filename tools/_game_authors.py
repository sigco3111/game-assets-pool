#!/usr/bin/env python3
"""
_game_authors.py

shared game authors metadata for sidecar generators + extract scripts.
"""
GAME_AUTHORS = {
    "wesnoth": {
        "copyright": "Copyright © 2003-2026 The Battle for Wesnoth contributors",
        "license_code": "GPL-2.0-only",
        "license_assets": "CC-BY-4.0",
        "source_repo": "https://github.com/wesnoth/wesnoth",
        "extracted_license": "CC-BY-4.0 (에셋만 추출, 코드 GPL 분리)",
    },
    "veloren": {
        "copyright": "Copyright © Veloren contributors",
        "license_code": "MPL-2.0",
        "license_assets": "CC-BY-4.0",
        "source_repo": "https://gitlab.com/veloren/veloren",
        "extracted_license": "CC-BY-4.0",
    },
    "freeciv": {
        "copyright": "Copyright © Freeciv contributors",
        "license_code": "GPL-2.0-or-later",
        "license_assets": "GPL-2.0-only",
        "source_repo": "https://github.com/freeciv/freeciv",
        "extracted_license": "GPL-2.0 (그림도 GPL)",
    },
    "openttd": {
        "copyright": "Copyright © OpenTTD contributors / Transport Tycoon original by Chris Sawyer",
        "license_code": "GPL-2.0-only",
        "license_assets": "GPL-2.0-only",
        "source_repo": "https://github.com/OpenTTD/OpenTTD",
        "extracted_license": "GPL-2.0 (원본 픽셀 저작권 별도 표기)",
    },
    "warzone": {
        "copyright": "Copyright © Warzone 2100 contributors / Pumpkin Studios original",
        "license_code": "GPL-2.0-only",
        "license_assets": "CC-BY-SA-2.0 (제한적 상업적 재사용 가능)",
        "source_repo": "https://github.com/Warzone2100/warzone2100",
        "extracted_license": "CC-BY-SA-2.0 (에셋만)",
    },
    "godot-open-rts": {
        "copyright": "Copyright © lampe-games contributors",
        "license_code": "MIT",
        "license_assets": "MIT",
        "source_repo": "https://github.com/lampe-games/godot-open-rts",
        "extracted_license": "MIT",
    },
}

CATEGORY_KEYWORDS = {
    "wesnoth": {
        "units": "unit-sprite", "portraits": "portrait",
        "music": "background-music", "sounds": "sfx",
        "terrain": "terrain-tile", "items": "item-icon",
    },
    "veloren": {
        "voxel": "voxel-model", "item": "item-icon", "world": "world-asset",
        "figure": "character-figure",
    },
    "freeciv": {
        "flags": "country-flag", "terrain": "terrain-tile",
        "units": "unit-sprite", "icons": "ui-icon", "city": "city-image",
        "misc": "misc-asset",
    },
    "openttd": {
        "vehicles": "vehicle-sprite", "terrain": "terrain-tile",
        "buildings": "building-sprite", "gui": "ui-element", "music": "background-music",
        "sounds": "sfx",
    },
    "warzone": {
        "units": "unit-3d", "structures": "structure-3d",
        "terrain": "terrain-texture", "features": "feature-mesh",
        "weapons": "weapon-model", "effects": "vfx",
        "interface": "ui-element",
    },
    "godot-open-rts": {
        "unit": "unit-model", "building": "building",
        "terrain": "terrain-texture", "ui": "ui-element",
    },
}
