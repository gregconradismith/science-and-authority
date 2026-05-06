#!/usr/bin/env python3
"""Download WordPress upload assets referenced by the WXR export."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlparse, urlunparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "tmp/apsc453scienceampauthority.WordPress.2026-05-06.xml"
OUT = ROOT / "docs"
UPLOAD_RE = re.compile(
    r"https?://(?:scienceauthority\.wordpress\.com|science-authority\.com)/wp-content/uploads/[^\"'<>\s)\]]+",
    re.IGNORECASE,
)


def urls_from_export() -> list[str]:
    text = EXPORT.read_text(encoding="utf-8")
    urls = {url.replace("&amp;", "&").rstrip("]") for url in UPLOAD_RE.findall(text)}
    return sorted(urls)


def target_path(url: str) -> Path:
    parsed = urlparse(url)
    path = unquote(parsed.path).lstrip("/")
    if not path.startswith("wp-content/uploads/"):
        raise ValueError(f"Not a WordPress upload URL: {url}")
    return OUT / path


def download(url: str, target: Path) -> str:
    if target.exists() and target.stat().st_size > 0:
        return "cached"
    target.parent.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(url)
    safe_url = urlunparse(parsed._replace(path=quote(unquote(parsed.path), safe="/%")))
    request = Request(safe_url, headers={"User-Agent": "Mozilla/5.0 static-site-asset-mirror"})
    with urlopen(request, timeout=45) as response:
        target.write_bytes(response.read())
    return "downloaded"


def main() -> int:
    urls = urls_from_export()
    downloaded = cached = failed = 0
    for index, url in enumerate(urls, 1):
        target = target_path(url)
        try:
            status = download(url, target)
        except Exception as exc:  # noqa: BLE001 - report every failed asset and keep going.
            failed += 1
            print(f"[{index}/{len(urls)}] failed {url}: {exc}", file=sys.stderr)
            continue
        if status == "cached":
            cached += 1
        else:
            downloaded += 1
        print(f"[{index}/{len(urls)}] {status} {target.relative_to(ROOT)}")
    print(f"Done: {downloaded} downloaded, {cached} cached, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
