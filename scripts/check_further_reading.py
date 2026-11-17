"""Check the 📖 อ่านเพิ่ม (further reading) block of every ข้อ in a lesson notebook.

Usage:
    python scripts/check_further_reading.py notebooks/mock1_lesson_v2.ipynb
    python scripts/check_further_reading.py --inside-answer notebooks/mock1_lesson.ipynb

Default layout: each เฉลย (a markdown cell that is a <details> block whose
summary starts with "✅ เฉลยข้อ") is followed, as the last cell of its ข้อ, by
its own 📖 อ่านเพิ่ม cell; no อ่านเพิ่ม may appear inside a เฉลย.
--inside-answer: the older layout, where the 📖 อ่านเพิ่ม block sits inside the
เฉลย's <details> and nowhere else.

In both layouts, each ข้อ's block must:
  1. exist (exactly one per เฉลย)
  2. have 1-2 links, at least one to docs.python.org/3/
  3. have every link answer HTTP 200 with its #anchor present on the page

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


def link_problems(block):
    """Return the problems with the links in one อ่านเพิ่ม block."""
    found = []
    links = LINK.findall(block)
    if not MIN_LINKS <= len(links) <= MAX_LINKS:
        found.append(f"has {len(links)} links (expected {MIN_LINKS}-{MAX_LINKS})")
    if not any(url.startswith(DOCS_PREFIX) for url in links):
        found.append(f"no link to {DOCS_PREFIX}")
    for url in links:
        error = check_link(url)
        if error:
            found.append(f"broken link {url}: {error}")
    return found


def check_notebook_after_answer(path):
    """Default layout: the อ่านเพิ่ม is its own cell after the เฉลย, never inside it."""
    with open(path, encoding="utf-8") as f:
        notebook = json.load(f)

    problems = []
    passed = []
    waiting = None  # label of the last เฉลย still without its อ่านเพิ่ม

    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] != "markdown":
            continue
        text = "".join(cell["source"])
        summary = ANSWER_SUMMARY.search(text)

        if summary:
            if waiting:
                problems.append(f"{waiting}: no {MARKER} cell after it")
            waiting = f"เฉลยข้อ {summary.group(1)}"
            if MARKER in text:
                problems.append(f"{waiting}: {MARKER} is inside the เฉลย; it belongs in its own cell at the end of the ข้อ")
            continue

        if MARKER not in text:
            continue
        if waiting is None:
            problems.append(f"cell {index}: {MARKER} with no เฉลย before it in its ข้อ")
            continue
        section_problems = link_problems(text[text.find(MARKER):])
        if section_problems:
            problems.extend(f"{waiting}: {p}" for p in section_problems)
        else:
            passed.append(waiting)
        waiting = None

    if waiting:
        problems.append(f"{waiting}: no {MARKER} cell after it")
    return passed, problems


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

        section_problems += link_problems(block)

        if section_problems:
            problems.extend(f"{label}: {p}" for p in section_problems)
        else:
            passed.append(label)

    return passed, problems


def main(argv):
    args = argv[1:]
    inside_answer = "--inside-answer" in args
    if inside_answer:
        args.remove("--inside-answer")
    if len(args) != 1:
        print(__doc__)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")

    check = check_notebook if inside_answer else check_notebook_after_answer
    passed, problems = check(args[0])
    for label in passed:
        print(f"PASS  {label}")
    for problem in problems:
        print(f"FAIL  {problem}")
    print(f"\n{len(passed)} passed, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
