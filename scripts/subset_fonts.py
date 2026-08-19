#!/usr/bin/env python3
"""Subset official OFL fonts to common Simplified Chinese and web WOFF2.

Install the optional build dependency with:
    python -m pip install "fonttools[woff]"
"""

from __future__ import annotations

import sys
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_TOOLS = ROOT / ".codex-fonttools"
if LOCAL_TOOLS.exists():
    sys.path.insert(0, str(LOCAL_TOOLS))

from fontTools import subset  # type: ignore  # noqa: E402
from fontTools.ttLib import TTFont  # type: ignore  # noqa: E402


FONT_DIR = ROOT / "assets" / "fonts"
SOURCES = {
    "sans": "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/Variable/TTF/Subset/NotoSansSC-VF.ttf",
    "serif": "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Serif/Variable/TTF/Subset/NotoSerifSC-VF.ttf",
    "doto": "https://raw.githubusercontent.com/google/fonts/main/ofl/doto/Doto%5BROND%2Cwght%5D.ttf",
}


def common_simplified_chinese() -> str:
    chars = set(chr(code) for code in range(0x20, 0x7F))
    chars.update("，。！？；：、（）《》【】“”‘’—…·℃↑↓→←±≈≥≤％‰年月日季度单位来源同比环比目标")
    for high in range(0xA1, 0xF8):
        for low in range(0xA1, 0xFF):
            try:
                chars.update(bytes((high, low)).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    return "".join(sorted(chars))


def make_subset(source: Path, target: Path, characters: str) -> None:
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    options.name_IDs = [0, 1, 2, 3, 4, 5, 6]
    options.name_legacy = True
    options.name_languages = [0x409, 0x804]
    font = subset.load_font(str(source), options)
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text=characters)
    subsetter.subset(font)
    subset.save_font(font, str(target), options)


def to_woff2(source: Path, target: Path) -> None:
    font = TTFont(str(source))
    font.flavor = "woff2"
    font.save(str(target))


def main() -> None:
    characters = common_simplified_chinese()
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="moxing-fonts-") as directory:
        temporary = Path(directory)
        sources = {}
        for name, url in SOURCES.items():
            target = temporary / f"{name}.ttf"
            print(f"downloading {name} from official repository")
            urllib.request.urlretrieve(url, target)
            sources[name] = target
        make_subset(sources["sans"], FONT_DIR / "NotoSansSC-Variable.woff2", characters)
        make_subset(sources["serif"], FONT_DIR / "NotoSerifSC-Variable.woff2", characters)
        to_woff2(sources["doto"], FONT_DIR / "Doto-Variable.woff2")
    for path in sorted(FONT_DIR.glob("*.woff2")):
        print(f"{path.name}: {path.stat().st_size / 1024 / 1024:.2f} MiB")


if __name__ == "__main__":
    main()
