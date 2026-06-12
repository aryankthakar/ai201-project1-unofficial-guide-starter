"""Milestone 3a — Acquisition.

Turns each entry in sources.py into a cleaned Markdown file at
documents/<name>.md, regardless of how it was obtained:

  - "local"  : read manually-saved HTML from documents/raw/<file>
  - "reddit" : fetch the thread's .json endpoint and flatten the comment tree
  - "scrape" : GET the URL with a browser User-Agent

All three paths funnel HTML (or assembled text) through the SAME cleaning step
(strip boilerplate tags -> markdownify -> collapse whitespace) so the corpus is
uniform downstream. Each output file starts with a small front-matter block
recording the source title and original URL for attribution.

Run:  python scrape.py
Anything that fails to fetch is reported as BLOCKED — save it manually into
documents/raw/ and switch its mode to "local" in sources.py, then re-run.
"""

import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

from sources import SOURCES

HERE = Path(__file__).parent
DOCS = HERE / "documents"
RAW = DOCS / "raw"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Tags that never carry document content — removed before conversion.
JUNK_TAGS = [
    "script", "style", "noscript", "svg", "iframe", "form", "button",
    "nav", "header", "footer", "aside", "input", "select", "option",
]


def clean_html_to_markdown(html: str) -> str:
    """Strip boilerplate tags, convert to Markdown, and collapse whitespace."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(JUNK_TAGS):
        tag.decompose()
    # Prefer a main-content container when the page exposes one; otherwise body.
    root = soup.find("main") or soup.find("article") or soup.body or soup
    markdown = md(str(root), heading_style="ATX", strip=["a", "img"])
    return _collapse(markdown)


def _collapse(text: str) -> str:
    """Drop blank-line runs and lines that are pure punctuation/whitespace."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        # Skip lines with no letters/digits (leftover separators, bullets, etc.)
        if not re.search(r"[A-Za-z0-9]", stripped):
            continue
        lines.append(stripped)
    # Collapse 3+ blank lines into one.
    out = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", out).strip()


def _reddit_comments(node, depth=0):
    """Recursively flatten a Reddit comment 'replies' listing into text blocks."""
    blocks = []
    if not isinstance(node, dict):
        return blocks
    for child in node.get("data", {}).get("children", []):
        data = child.get("data", {})
        body = data.get("body")
        if body and body not in ("[deleted]", "[removed]"):
            author = data.get("author", "user")
            blocks.append(f"{'>' * (depth + 1)} **{author}:** {body.strip()}")
        replies = data.get("replies")
        if isinstance(replies, dict):
            blocks.extend(_reddit_comments(replies, depth + 1))
    return blocks


def fetch_reddit(url: str) -> str:
    """Fetch a Reddit thread as JSON and assemble post + comments as Markdown."""
    json_url = url.rstrip("/") + "/.json"
    resp = requests.get(json_url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    listings = resp.json()
    post = listings[0]["data"]["children"][0]["data"]
    parts = [f"# {post.get('title', '').strip()}"]
    if post.get("selftext"):
        parts.append(post["selftext"].strip())
    parts.append("\n## Comments\n")
    parts.extend(_reddit_comments(listings[1]))
    return _collapse("\n\n".join(parts))


def write_doc(src: dict, body: str) -> None:
    """Write a cleaned doc with front-matter to documents/<name>.md."""
    front = f"---\nsource: {src['title']}\nurl: {src['url']}\n---\n\n"
    out = DOCS / f"{src['name']}.md"
    out.write_text(front + body, encoding="utf-8")


def acquire(src: dict) -> tuple[str, int]:
    """Return (status, char_count) for one source. status in scraped/local/reddit/BLOCKED."""
    mode = src["mode"]
    try:
        if mode == "local":
            raw_path = RAW / src["file"]
            if not raw_path.exists():
                return f"BLOCKED — missing file documents/raw/{src['file']}", 0
            body = clean_html_to_markdown(raw_path.read_text(encoding="utf-8", errors="ignore"))
        elif mode == "reddit":
            body = fetch_reddit(src["url"])
        else:  # scrape
            resp = requests.get(src["url"], headers=HEADERS, timeout=20)
            resp.raise_for_status()
            body = clean_html_to_markdown(resp.text)
    except Exception as e:  # noqa: BLE001 — report any failure, keep going
        return f"BLOCKED — {type(e).__name__}: {str(e)[:80]}", 0

    if len(body) < 100:
        return f"BLOCKED — only {len(body)} chars extracted (likely JS-rendered)", len(body)
    write_doc(src, body)
    return mode if mode != "scrape" else "scraped", len(body)


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    print(f"Acquiring {len(SOURCES)} sources -> {DOCS}/\n")
    blocked = []
    for src in SOURCES:
        status, chars = acquire(src)
        flag = "BLOCKED" in status
        mark = "✗" if flag else "✓"
        print(f"  {mark} {src['name']:<24} {status:<28} {chars:>7} chars")
        if flag:
            blocked.append((src["name"], src["url"], status))

    print(f"\nDone. {len(SOURCES) - len(blocked)}/{len(SOURCES)} written to documents/")
    if blocked:
        print("\nBLOCKED — save these manually (Save Page As -> Webpage Complete)")
        print("into documents/raw/, then set mode='local' + file=... in sources.py:")
        for name, url, why in blocked:
            print(f"  - {name}: {url}\n      ({why})")
        sys.exit(0)


if __name__ == "__main__":
    main()
