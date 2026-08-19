#!/usr/bin/env python3
"""moxing-studio PNG 导出：优先 Playwright，缺失时回退到系统 Chrome/Edge。"""
from pathlib import Path
import os
import shutil
import struct
import subprocess
import sys
import tempfile


def png_size(path):
    """用 PNG 文件头读取尺寸，避免引入 Pillow。"""
    with open(path, "rb") as image:
        header = image.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("导出文件不是有效 PNG")
    return struct.unpack(">II", header[16:24])


def find_browser():
    configured = os.environ.get("MOXING_BROWSER_EXECUTABLE")
    candidates = [
        configured,
        shutil.which("chrome"),
        shutil.which("msedge"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    return next((item for item in candidates if item and Path(item).is_file()), None)


def export_with_browser(html_path, png_path):
    browser = find_browser()
    if not browser:
        return False
    profile = tempfile.mkdtemp(
        prefix=".moxing-export-",
        dir=str(Path(png_path).resolve().parent),
    )
    try:
        command = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--no-first-run",
            f"--user-data-dir={profile}",
            "--window-size=1280,720",
            "--force-device-scale-factor=2",
            f"--screenshot={Path(png_path).resolve()}",
            Path(html_path).resolve().as_uri(),
        ]
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
        return result.returncode == 0 and Path(png_path).is_file()
    finally:
        shutil.rmtree(profile, ignore_errors=True)

def main():
    if len(sys.argv) < 3:
        print("用法: python export.py <input.html> <output.png>")
        sys.exit(1)
    html_path, png_path = sys.argv[1], sys.argv[2]
    Path(png_path).resolve().parent.mkdir(parents=True, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        exported = export_with_browser(html_path, png_path)
        engine = "系统浏览器"
    else:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 720},
                                    device_scale_factor=2)
            page.goto(Path(html_path).resolve().as_uri())
            page.wait_for_timeout(500)
            page.screenshot(path=png_path)
            browser.close()
        exported = True
        engine = "Playwright"

    if not exported:
        print("未安装 Playwright，且未找到可用的 Chrome/Edge。")
        print("可安装 playwright，或用浏览器全屏打开 HTML 后手动截图。")
        sys.exit(2)

    size = png_size(png_path)
    if size != (2560, 1440):
        print(f"导出尺寸异常：{size[0]}×{size[1]}，预期 2560×1440")
        sys.exit(3)
    print(f"已通过{engine}导出 {png_path}（2560×1440）")

if __name__ == "__main__":
    main()
