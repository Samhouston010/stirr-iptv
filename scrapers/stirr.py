#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stirr TV IPTV Generator
این اسکریپت لیست کانال‌های Stirr را با لینک‌های m3u8 جمع می‌کند
و یک فایل M3U می‌سازد.
"""
import requests
import sys
import os
import re
from datetime import datetime, timezone

OUTPUT_FILE = "playlists/stirr.m3u"
TEST_TIMEOUT = 15

# منبع پایه: لیست کانال‌های Stirr که در iptv-org نگه‌داری می‌شود
SOURCE_URL = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/us_stirr.m3u"


def fetch_source():
    print(f"Fetching channel list from iptv-org...")
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()
    return r.text


def parse_m3u(content):
    """تجزیه فایل M3U به لیست (نام، tvg-id، URL)"""
    channels = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            # استخراج tvg-id و نام
            tvg_id_match = re.search(r'tvg-id="([^"]*)"', line)
            tvg_id = tvg_id_match.group(1) if tvg_id_match else ""
            name = line.split(",", 1)[1] if "," in line else "Unknown"
            # خط بعدی URL است
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url.startswith("http"):
                    channels.append((tvg_id, name, url))
        i += 1
    return channels


def test_stream(url):
    """تست سریع آیا URL کار می‌کند"""
    try:
        r = requests.head(url, timeout=TEST_TIMEOUT, allow_redirects=True)
        return r.status_code == 200
    except Exception:
        return False


def generate():
    print("Starting Stirr TV playlist generation")
    print("=" * 60)

    content = fetch_source()
    all_channels = parse_m3u(content)
    print(f"Found {len(all_channels)} channels in source")

    output_lines = ["#EXTM3U"]
    working = 0
    broken = 0

    for tvg_id, name, url in all_channels:
        print(f"  Testing {name[:40]} ", end="", flush=True)
        if test_stream(url):
            print("OK")
            extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="Stirr TV",{name}'
            output_lines.append(extinf)
            output_lines.append(url)
            working += 1
        else:
            print("FAILED")
            broken += 1

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines) + "\n")

    print("=" * 60)
    print(f"Working: {working}")
    print(f"Broken: {broken}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    return working


if __name__ == "__main__":
    count = generate()
    sys.exit(0)
