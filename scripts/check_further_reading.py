"""Check the 📖 อ่านเพิ่ม (further reading) block in every เฉลย of a lesson notebook.

Usage:
    python scripts/check_further_reading.py notebooks/mock1_lesson.ipynb

For each เฉลย (a markdown cell that is a <details> block whose summary starts
with "✅ เฉลยข้อ"), checks that:
  1. it contains a 📖 อ่านเพิ่ม block inside <details>
  2. the block has 1-2 links, at least one to docs.python.org/3/
  3. every link answers HTTP 200 and its #anchor exists on the page
It also checks that no 📖 อ่านเพิ่ม appears outside a เฉลย's <details>.

Exits 0 when everything passes, 1 otherwise. Needs internet access.
Standard library only.
"""

import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser

MARKER = "📖 อ่านเพิ่ม"
ANSWER_SUMMARY = re.compile(r"<summary>\s*✅\s*เฉลยข้อ\s*([^(<]+?)\s*(?:\(|</summary>)")
LINK = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
DOCS_PREFIX = "https://docs.python.org/3/"
MIN_LINKS, MAX_LINKS = 1, 2
USER_AGENT = "hkico-lessons-link-check/1.0"


class _AnchorCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id" or (tag == "a" and name == "name"):
                if value:
                    self.anchors.add(value)


_page_cache = {}


def fetch_anchors(page_url):
    """Return (anchors, error) for a page; error is None when the page loaded."""
    if page_url not in _page_cache:
        request = urllib.request.Request(page_url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status != 200:
                    _page_cache[page_url] = (set(), f"HTTP {response.status}")
                else:
                    body = response.read().decode("utf-8", errors="replace")
                    collector = _AnchorCollector()
                    collector.feed(body)
                    _page_cache[page_url] = (collector.anchors, None)
        except urllib.error.HTTPError as e:
            _page_cache[page_url] = (set(), f"HTTP {e.code}")
        except (urllib.error.URLError, TimeoutError) as e:
            _page_cache[page_url] = (set(), f"cannot open ({e})")
    return _page_cache[page_url]


def check_link(url):
    """Return an error message for a broken link, or None if it is fine."""
    page_url, _, anchor = url.partition("#")
    anchors, error = fetch_anchors(page_url)
    if error:
        return error
    if anchor and anchor not in anchors:
        return f"anchor #{anchor} not found on page"
    return None


def further_reading_block(answer_text):
    """Return the text of the อ่านเพิ่ม block inside an answer, or None."""
    details_end = answer_text.rfind("</details>")
    inside = answer_text[:details_end] if details_end != -1 else answer_text
    start = inside.find(MARKER)
    return None if start == -1 else inside[start:]


def check_notebook(path):
    with open(path, encoding="utf-8") as f:
        notebook = json.load(f)

    problems = []
    passed = []

    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "markdown":
            continue
        text = "".join(cell["source"])
        summary = ANSWER_SUMMARY.search(text)

        if not summary:
            if MARKER in text:
                problems.append(f"cell {index}: {MARKER} is outside a เฉลย <details>")
            continue

        label = f"เฉลยข้อ {summary.group(1)}"
        section_problems = []
        details_end = text.rfind("</details>")
        if details_end != -1 and MARKER in text[details_end:]:
            section_problems.append(f"{MARKER} is after </details>, so students see it before opening the answer")

        block = further_reading_block(text)
        if block is None:
            problems.extend(f"{label}: {p}" for p in section_problems + [f"no {MARKER}"])
            continue

        links = LINK.findall(block)
        if not MIN_LINKS <= len(links) <= MAX_LINKS:
            section_problems.append(f"has {len(links)} links (expected {MIN_LINKS}-{MAX_LINKS})")
        if not any(url.startswith(DOCS_PREFIX) for url in links):
            section_problems.append(f"no link to {DOCS_PREFIX}")
        for url in links:
            error = check_link(url)
            if error:
                section_problems.append(f"broken link {url}: {error}")

        if section_problems:
            problems.extend(f"{label}: {p}" for p in section_problems)
        else:
            passed.append(label)

    return passed, problems


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")

    passed, problems = check_notebook(argv[1])
    for label in passed:
        print(f"PASS  {label}")
    for problem in problems:
        print(f"FAIL  {problem}")
    print(f"\n{len(passed)} passed, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
