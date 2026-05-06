#!/usr/bin/env python3
"""Build a static, presentable site from the WordPress WXR export."""

from __future__ import annotations

import html
import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "tmp/apsc453scienceampauthority.WordPress.2026-05-06.xml"
OUT = ROOT / "docs"
MEDIA_EXPORT = ROOT / "tmp/media-export-203120012-from-0-to-7589"
SITE_HOSTS = {"scienceauthority.wordpress.com", "science-authority.com"}
NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    "wp": "http://wordpress.org/export/1.2/",
}

UPLOAD_ALIASES = {
    "wp-content/uploads/2022/08/71yflt5uvul.jpg": "wp-content/uploads/2022/08/71yflt5uvul-1.jpg",
}

EXTERNAL_UPLOADS = {
    "wp-content/uploads/2022/09/lecture-1-introduction-and-the-distinction-between-power-and-authority-online-audio-converter.com_.mp3",
    "wp-content/uploads/2022/09/lecture-2-professional-authority.mp3",
    "wp-content/uploads/2022/09/lecture-3-falsification-and-scientific-authority.mp3",
    "wp-content/uploads/2022/09/lecture-4-religious-authority-in-a-differentiated-world.mp3",
    "wp-content/uploads/2022/09/lecture-5-kafka-and-ambivalence-towards-authority.mp3",
    "wp-content/uploads/2022/09/lecture-6-modernity-and-authority-in-the-work-of-max-weber.mp3",
    "wp-content/uploads/2022/10/1995-01-29_gilfronsdal_clingingtoviewsandopinions.mp3",
}


@dataclass(frozen=True)
class Entry:
    id: str
    kind: str
    title: str
    slug: str
    date: str
    modified: str
    author: str
    content: str
    excerpt: str
    categories: tuple[str, ...]
    order: int

    @property
    def sort_date(self) -> str:
        return self.date or self.modified or "0000-00-00 00:00:00"

    @property
    def year(self) -> str:
        return self.sort_date[:4] if self.sort_date[:4].isdigit() else ""


def text(node: ET.Element, path: str, default: str = "") -> str:
    value = node.findtext(path, default=default, namespaces=NS)
    return html.unescape(value or "").strip()


def parse_export() -> tuple[dict[str, str], list[Entry], list[dict[str, str]]]:
    tree = ET.parse(EXPORT)
    channel = tree.getroot().find("channel")
    if channel is None:
        raise ValueError("No channel found in export")

    metadata = {
        "title": text(channel, "title"),
        "description": text(channel, "description"),
        "link": text(channel, "link"),
        "exported": text(channel, "pubDate"),
    }

    entries: list[Entry] = []
    attachments: list[dict[str, str]] = []
    for item in channel.findall("item"):
        kind = text(item, "wp:post_type")
        status = text(item, "wp:status")
        if kind == "attachment":
            url = text(item, "wp:attachment_url")
            if url:
                attachments.append(
                    {
                        "title": text(item, "title") or Path(urlparse(url).path).name,
                        "url": url,
                        "date": text(item, "wp:post_date"),
                    }
                )
            continue

        if kind not in {"page", "post"} or status != "publish":
            continue

        slug = text(item, "wp:post_name") or slugify(text(item, "title"))
        entries.append(
            Entry(
                id=text(item, "wp:post_id"),
                kind=kind,
                title=text(item, "title") or "Untitled",
                slug=slug,
                date=text(item, "wp:post_date"),
                modified=text(item, "wp:post_modified"),
                author=text(item, "dc:creator"),
                content=item.findtext("content:encoded", default="", namespaces=NS) or "",
                excerpt=item.findtext("excerpt:encoded", default="", namespaces=NS) or "",
                categories=tuple(
                    html.unescape(cat.text or "").strip()
                    for cat in item.findall("category")
                    if (cat.text or "").strip()
                ),
                order=int(text(item, "wp:menu_order") or "0"),
            )
        )
    return metadata, entries, attachments


def slugify(value: str) -> str:
    value = html.unescape(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "untitled"


def strip_tags(value: str) -> str:
    value = re.sub(r"(?is)<script.*?</script>", " ", value)
    value = re.sub(r"(?is)<style.*?</style>", " ", value)
    value = re.sub(r"(?s)<!--.*?-->", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def excerpt(entry: Entry, words: int = 30) -> str:
    source = strip_tags(entry.excerpt or entry.content)
    parts = source.split()
    return " ".join(parts[:words]) + ("..." if len(parts) > words else "")


def date_label(value: str) -> str:
    if not value:
        return ""
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").strftime("%b %-d, %Y")
    except ValueError:
        return value[:10]


def output_path(entry: Entry) -> str:
    return f"{'posts' if entry.kind == 'post' else 'pages'}/{entry.slug}/"


def relative_url(from_dir: str, target: str) -> str:
    target = target or "."
    rel = os.path.relpath(target, start=from_dir or ".")
    if rel == ".":
        return "./"
    rel = rel.replace(os.sep, "/")
    if Path(target).suffix or rel.endswith("/"):
        return rel
    return rel + "/"


def rewrite_links(content: str, from_dir: str, by_slug: dict[str, Entry]) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, url, suffix = match.groups()
        parsed = urlparse(html.unescape(url))
        if parsed.netloc and parsed.netloc not in SITE_HOSTS:
            return match.group(0)
        path = parsed.path.strip("/")
        if path.startswith("wp-content/uploads/"):
            if path in EXTERNAL_UPLOADS:
                return match.group(0)
            path = UPLOAD_ALIASES.get(path, path)
            local = relative_url(from_dir, path)
            return f"{prefix}{local}{suffix}"
        if not path:
            return match.group(0)
        slug = path.split("/")[0]
        entry = by_slug.get(slug)
        if not entry:
            return match.group(0)
        local = relative_url(from_dir, output_path(entry))
        return f"{prefix}{local}{suffix}"

    host_pattern = "|".join(re.escape(host) for host in SITE_HOSTS)
    return re.sub(rf"""((?:href|src|data)=["'])(https?://(?:{host_pattern})/[^"']+)(["'])""", repl, content)


def normalize_content(entry: Entry, from_dir: str, by_slug: dict[str, Entry]) -> str:
    content = rewrite_links(entry.content, from_dir, by_slug).strip()
    content = content.replace('href="http://[glossary] [dictionary]"', 'href="#"')
    if not content:
        return '<p class="empty-note">No body content was included in the WordPress export for this page.</p>'
    if re.search(r"(?is)<!doctype\s+html|<html[\s>]", content):
        return (
            '<iframe class="embedded-page" title="Embedded interactive content" '
            f'srcdoc="{html.escape(content, quote=True)}"></iframe>'
        )
    return content


def page_shell(title: str, body: str, from_dir: str, metadata: dict[str, str]) -> str:
    css = relative_url(from_dir, "assets/site.css").rstrip("/")
    js = relative_url(from_dir, "assets/site.js").rstrip("/")
    home = relative_url(from_dir, "").rstrip("/") or "."
    pages = relative_url(from_dir, "pages/").rstrip("/")
    posts = relative_url(from_dir, "posts/").rstrip("/")
    syllabus = relative_url(from_dir, "pages/syllabus/").rstrip("/")
    foundations = relative_url(from_dir, "pages/foundations/").rstrip("/")
    resources = relative_url(from_dir, "pages/resources/").rstrip("/")
    calendar = relative_url(from_dir, "pages/spring-2026-calendar/").rstrip("/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} | {html.escape(metadata["title"])}</title>
  <link rel="stylesheet" href="{css}">
  <script src="{js}" defer></script>
</head>
<body>
  <header class="site-header">
    <a class="brand" href="{home}">
      <span class="brand-mark">S&amp;A</span>
      <span><strong>{html.escape(metadata["title"])}</strong><em>{html.escape(metadata["description"])}</em></span>
    </a>
    <nav aria-label="Primary navigation">
      <a href="{calendar}">Calendar</a>
      <a href="{syllabus}">Syllabus</a>
      <a href="{foundations}">Foundations</a>
      <a href="{pages}">Materials</a>
      <a href="{resources}">Resources</a>
      <a href="{posts}">Updates</a>
    </nav>
  </header>
  <main>
{body}
  </main>
  <footer class="site-footer">
    <span>Static version generated from the WordPress export dated {html.escape(metadata["exported"])}.</span>
    <a href="{html.escape(metadata["link"])}">Original site</a>
  </footer>
</body>
</html>
"""


def card(entry: Entry, from_dir: str, extra: str = "") -> str:
    href = relative_url(from_dir, output_path(entry)).rstrip("/")
    meta = date_label(entry.date) if entry.kind == "post" else "Course material"
    return f"""<article class="card {extra}">
  <p class="eyebrow">{html.escape(meta)}</p>
  <h3><a href="{href}">{html.escape(entry.title)}</a></h3>
  <p>{html.escape(excerpt(entry, 24))}</p>
</article>"""


def render_entry(entry: Entry, metadata: dict[str, str], by_slug: dict[str, Entry]) -> None:
    out_dir = OUT / output_path(entry)
    out_dir.mkdir(parents=True, exist_ok=True)
    from_dir = output_path(entry)
    body = f"""    <article class="content-page">
      <div class="page-kicker">{html.escape(entry.kind.title())}{' · ' + html.escape(date_label(entry.date)) if entry.kind == 'post' else ''}</div>
      <h1>{html.escape(entry.title)}</h1>
      <div class="wp-content">
{normalize_content(entry, from_dir, by_slug)}
      </div>
    </article>"""
    (out_dir / "index.html").write_text(page_shell(entry.title, body, from_dir, metadata), encoding="utf-8")


def render_home(metadata: dict[str, str], entries: list[Entry]) -> None:
    pages = [e for e in entries if e.kind == "page"]
    posts = sorted((e for e in entries if e.kind == "post"), key=lambda e: e.sort_date, reverse=True)
    course_arc_slugs = [
        "introduction-to-science-and-authority",
        "what-is-authority-2",
        "professional-authority",
        "falsification",
        "the-new-atlantis",
        "looking-up-the-truth",
        "modernity-and-authority-in-max-weber",
        "diagnosis-mercury-money-politics-and-poison",
        "an-enemy-of-the-people",
        "manufactured-uncertainty-and-product-defense",
        "the-panic-virus",
        "evidence-not-authority",
        "scientism-2",
        "surveillance-capitalism",
        "data-ism",
        "why-how-when-trust-science",
    ]
    course_arc = [e for slug in course_arc_slugs for e in pages if e.slug == slug]
    featured_slugs = [
        "spring-2026-calendar",
        "syllabus",
        "readings",
        "foundations",
        "projects-3",
        "fall-2025-final-project-description",
        "resources",
        "flyer",
    ]
    featured = [e for slug in featured_slugs for e in pages if e.slug == slug]
    body = f"""    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">William & Mary COLL 400 capstone</p>
        <h1>{html.escape(metadata["title"])}</h1>
        <p>{html.escape(metadata["description"])}. A static, browsable edition of the course site exported from WordPress.</p>
        <div class="hero-actions">
          <a class="button primary" href="pages/spring-2026-calendar/">View calendar</a>
          <a class="button" href="pages/">Browse materials</a>
        </div>
      </div>
      <img src="wp-content/uploads/2024/08/cool-graphic-reflecting-modern-science-and-totalitarian-society-with-young-2.png" alt="Science and Authority course artwork">
    </section>

    <section class="section">
      <div class="section-heading">
        <p class="eyebrow">Core course pages</p>
        <h2>Start here</h2>
      </div>
      <div class="card-grid">
        {''.join(card(e, '', 'feature') for e in featured)}
      </div>
    </section>

    <section class="section two-column">
      <div>
        <div class="section-heading">
          <p class="eyebrow">{len(course_arc)} selected pages</p>
          <h2>Course arc</h2>
        </div>
        <ol class="link-list">
          {''.join(f'<li><a href="{relative_url("", output_path(e)).rstrip("/")}">{html.escape(e.title)}</a><span>{html.escape(excerpt(e, 14))}</span></li>' for e in course_arc)}
        </ol>
      </div>
      <aside class="updates-panel">
        <div class="section-heading">
          <p class="eyebrow">Recent posts</p>
          <h2>Course updates</h2>
        </div>
        {''.join(card(e, '') for e in posts[:6])}
      </aside>
    </section>"""
    (OUT / "index.html").write_text(page_shell(metadata["title"], body, "", metadata), encoding="utf-8")


def lecture_key(entry: Entry) -> tuple[int, str]:
    m = re.search(r"lecture-(\d+)", entry.slug)
    if m:
        return (int(m.group(1)), entry.slug)
    return (999, entry.slug)


def render_index(metadata: dict[str, str], entries: Iterable[Entry], kind: str) -> None:
    entries = list(entries)
    out_dir = OUT / ("posts" if kind == "post" else "pages")
    out_dir.mkdir(parents=True, exist_ok=True)
    from_dir = "posts/" if kind == "post" else "pages/"
    if kind == "post":
        ordered = sorted(entries, key=lambda e: e.sort_date, reverse=True)
        title = "Course Updates"
        subtitle = "Announcements and course blog posts from the export."
    else:
        ordered = sorted(entries, key=lambda e: (0 if e.slug in {"spring-2026-calendar", "syllabus", "readings", "foundations"} else 1, e.title.lower()))
        title = "Course Materials"
        subtitle = "Pages, calendars, readings, case studies, project descriptions, and helper resources."
    body = f"""    <section class="listing">
      <div class="section-heading">
        <p class="eyebrow">{len(ordered)} items</p>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <label class="search-box">
        <span>Filter</span>
        <input type="search" data-filter-input placeholder="Search title or text">
      </label>
      <div class="card-grid" data-filter-list>
        {''.join(card(e, from_dir) for e in ordered)}
      </div>
    </section>"""
    (out_dir / "index.html").write_text(page_shell(title, body, from_dir, metadata), encoding="utf-8")


def render_assets(entries: list[Entry], attachments: list[dict[str, str]]) -> None:
    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "site.css").write_text(CSS, encoding="utf-8")
    (assets / "site.js").write_text(JS, encoding="utf-8")
    search = [
        {
            "title": entry.title,
            "kind": entry.kind,
            "url": output_path(entry),
            "date": entry.date[:10],
            "text": strip_tags(entry.content)[:800],
        }
        for entry in entries
    ]
    (assets / "search-index.json").write_text(json.dumps(search, indent=2), encoding="utf-8")
    (assets / "attachments.json").write_text(json.dumps(attachments, indent=2), encoding="utf-8")


def sync_media_export() -> None:
    if not MEDIA_EXPORT.exists():
        return
    dest_root = OUT / "wp-content/uploads"
    for source in MEDIA_EXPORT.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(MEDIA_EXPORT)
        if f"wp-content/uploads/{relative.as_posix()}" in EXTERNAL_UPLOADS:
            dest = dest_root / relative
            if dest.exists():
                dest.unlink()
            continue
        dest = dest_root / relative
        if dest.exists() and dest.stat().st_size == source.stat().st_size:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)


CSS = r"""
:root {
  --bg: #f6f5f1;
  --surface: #ffffff;
  --ink: #17191c;
  --muted: #646b73;
  --line: #ddd8cd;
  --accent: #006b6b;
  --accent-2: #9a3d20;
  --soft: #e7efed;
  --shadow: 0 16px 45px rgba(28, 31, 34, .10);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 17px/1.65 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
a { color: var(--accent); text-decoration-thickness: .08em; text-underline-offset: .18em; }
img, iframe, object { max-width: 100%; }
.site-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 14px clamp(18px, 4vw, 56px);
  background: rgba(246, 245, 241, .94);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(14px);
}
.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--ink);
  text-decoration: none;
}
.brand strong, .brand em { display: block; line-height: 1.2; }
.brand em { color: var(--muted); font-size: 13px; font-style: normal; }
.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border: 1px solid var(--accent);
  background: var(--accent);
  color: white;
  font-weight: 800;
  letter-spacing: .04em;
}
nav { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
nav a {
  color: var(--ink);
  padding: 8px 10px;
  text-decoration: none;
  border-bottom: 2px solid transparent;
}
nav a:hover { border-color: var(--accent); }
main { min-height: 70vh; }
.hero {
  min-height: 72vh;
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(300px, .9fr);
  align-items: center;
  gap: clamp(28px, 6vw, 72px);
  padding: clamp(38px, 7vw, 88px) clamp(18px, 4vw, 56px) 44px;
  border-bottom: 1px solid var(--line);
}
.hero h1 {
  max-width: 950px;
  margin: 0 0 18px;
  font-size: clamp(42px, 7vw, 90px);
  line-height: .98;
  letter-spacing: 0;
}
.hero p { max-width: 720px; color: #3e454c; font-size: 20px; }
.hero img {
  width: 100%;
  aspect-ratio: 1.3;
  object-fit: cover;
  border: 1px solid var(--line);
  box-shadow: var(--shadow);
}
.hero-actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 30px; }
.button {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  border: 1px solid var(--accent);
  color: var(--accent);
  text-decoration: none;
  font-weight: 700;
}
.button.primary { background: var(--accent); color: white; }
.section, .listing {
  padding: clamp(34px, 6vw, 70px) clamp(18px, 4vw, 56px);
}
.section-heading { margin-bottom: 22px; }
.section-heading h1, .section-heading h2 {
  margin: 0;
  font-size: clamp(30px, 4vw, 52px);
  line-height: 1.08;
}
.section-heading p:not(.eyebrow) { max-width: 780px; color: var(--muted); }
.eyebrow {
  margin: 0 0 8px;
  color: var(--accent-2);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .12em;
  text-transform: uppercase;
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(260px, 100%), 1fr));
  gap: 16px;
}
.card {
  min-height: 190px;
  padding: 20px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 8px 22px rgba(28, 31, 34, .05);
}
.card h3 { margin: 0 0 10px; font-size: 21px; line-height: 1.2; }
.card h3 a { color: var(--ink); text-decoration: none; }
.card p { color: var(--muted); margin: 0; }
.feature { background: linear-gradient(180deg, #ffffff, var(--soft)); }
.two-column {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(300px, .75fr);
  gap: clamp(24px, 4vw, 48px);
  align-items: start;
}
.updates-panel {
  background: #efede6;
  border-left: 4px solid var(--accent);
  padding: 20px;
}
.updates-panel .card { margin-bottom: 14px; min-height: 0; }
.link-list {
  display: grid;
  gap: 10px;
  padding: 0;
  list-style: none;
  counter-reset: links;
}
.link-list li {
  counter-increment: links;
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid var(--line);
}
.link-list li::before {
  content: counter(links, decimal-leading-zero);
  color: var(--accent-2);
  font-weight: 800;
}
.link-list a { color: var(--ink); font-weight: 800; text-decoration: none; }
.link-list span { grid-column: 2; color: var(--muted); font-size: 15px; }
.content-page {
  width: min(940px, calc(100% - 36px));
  margin: 0 auto;
  padding: clamp(34px, 6vw, 76px) 0;
}
.content-page h1 {
  margin: 0 0 26px;
  font-size: clamp(34px, 5vw, 64px);
  line-height: 1.05;
}
.page-kicker {
  color: var(--accent-2);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .12em;
  font-size: 12px;
  margin-bottom: 10px;
}
.wp-content {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: clamp(20px, 4vw, 44px);
  box-shadow: var(--shadow);
}
.wp-content h1, .wp-content h2, .wp-content h3 { line-height: 1.15; margin-top: 1.5em; }
.wp-content h1:first-child, .wp-content h2:first-child, .wp-content h3:first-child { margin-top: 0; }
.wp-content p, .wp-content li { max-width: 78ch; }
.wp-content figure { margin: 26px 0; }
.wp-content img {
  height: auto;
  border: 1px solid var(--line);
}
.wp-content iframe, .wp-content object {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 8px;
}
.wp-content object { min-height: 560px; }
.wp-content .wp-block-file {
  margin: 22px 0;
  padding: 14px;
  background: #f8f7f3;
  border: 1px solid var(--line);
}
.wp-block-file__button, .wp-element-button {
  display: inline-flex;
  margin-left: 10px;
  padding: 6px 10px;
  background: var(--accent);
  color: white;
  text-decoration: none;
}
.embedded-page {
  display: block;
  width: 100%;
  min-height: 860px;
  background: white;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 520px;
  margin: 0 0 24px;
  padding: 10px 12px;
  background: var(--surface);
  border: 1px solid var(--line);
}
.search-box span { color: var(--muted); font-weight: 800; }
.search-box input {
  width: 100%;
  border: 0;
  outline: 0;
  font: inherit;
  background: transparent;
}
.empty-note { color: var(--muted); font-style: italic; }
.site-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 24px clamp(18px, 4vw, 56px);
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 14px;
}
@media (max-width: 820px) {
  .site-header { position: static; align-items: flex-start; flex-direction: column; }
  nav { justify-content: flex-start; }
  .hero, .two-column { grid-template-columns: 1fr; }
  .hero { min-height: 0; }
  .hero img { order: -1; max-height: 340px; }
  .site-footer { flex-direction: column; }
}
"""


JS = r"""
document.addEventListener("input", (event) => {
  const input = event.target.closest("[data-filter-input]");
  if (!input) return;
  const list = document.querySelector("[data-filter-list]");
  const query = input.value.trim().toLowerCase();
  for (const item of list.querySelectorAll(".card")) {
    item.hidden = query && !item.textContent.toLowerCase().includes(query);
  }
});
"""


def main() -> None:
    if OUT.exists():
        for path in OUT.iterdir():
            if path.name == "wp-content":
                continue
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    OUT.mkdir(exist_ok=True)
    sync_media_export()
    metadata, entries, attachments = parse_export()
    by_slug = {entry.slug: entry for entry in entries}
    render_assets(entries, attachments)
    for entry in entries:
        render_entry(entry, metadata, by_slug)
    render_home(metadata, entries)
    render_index(metadata, [e for e in entries if e.kind == "page"], "page")
    render_index(metadata, [e for e in entries if e.kind == "post"], "post")
    print(f"Generated {len(entries)} pages/posts and {len(attachments)} attachment references in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
