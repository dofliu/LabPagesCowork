#!/usr/bin/env python3
"""Merge latest published journal articles from Google Sites into publications.json."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = (
    "https://sites.google.com/view/jui-hung-liu/"
    "%E8%91%97%E4%BD%9C%E7%99%BC%E8%A1%A8/"
    "%E6%9C%9F%E5%88%8A%E8%AB%96%E6%96%87-journal-articles"
)
SKIP_STATUSES = ("Under Review", "Submitted", "Draft", "Minor Revision")
AUTHOR_MARKERS = ("Jui-Hung Liu", "JH Liu", "劉瑞弘")


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "a":
            self.href = attrs_dict.get("href")
        if tag in {"p", "div", "li", "br", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.href = None
        if tag in {"p", "div", "li", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        if self.href and "doi" in text.lower():
            self.parts.append(f" {text} [{self.href}] ")
        else:
            self.parts.append(text)

    def lines(self) -> list[str]:
        text = "".join(self.parts).replace("\xa0", " ")
        text = html.unescape(text)
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n", text)
        return [line.strip() for line in text.splitlines() if line.strip()]


def today() -> str:
    return datetime.now(UTC).date().isoformat()


def fetch_lines(url: str) -> list[str]:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 DOF-Lab-publication-sync",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urlopen(request, timeout=30) as response:  # nosec B310: fixed HTTPS source URL
        page = response.read().decode("utf-8", errors="replace")
    parser = VisibleTextParser()
    parser.feed(page)
    return parser.lines()


def latest_published_lines(lines: list[str]) -> list[str]:
    try:
        start = next(i for i, line in enumerate(lines) if line.startswith("2022 ~2026"))
    except StopIteration as exc:
        raise ValueError("Cannot find the 2022 ~2026 published journal section.") from exc

    selected: list[str] = []
    for line in lines[start + 1:]:
        if set(line) == {"-"}:
            break
        if any(status in line for status in SKIP_STATUSES):
            continue
        if not any(marker in line for marker in AUTHOR_MARKERS):
            continue
        if not re.search(r"(?<!\d)20\d{2}(?!\d)", line):
            continue
        selected.append(line)
    if not selected:
        raise ValueError("No published journal articles were parsed from Google Sites.")
    return selected


def clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    value = value.replace("andJui-Hung", "and Jui-Hung")
    value = value.replace("Jui-Hung Liu,Nelson", "Jui-Hung Liu, Nelson")
    value = value.replace("Chenand", "Chen and")
    value = value.replace("aPin LockStructure", "a Pin Lock Structure")
    value = value.replace("forWind", "for Wind")
    value = value.replace("MaintenanceAuxiliary", "Maintenance Auxiliary")
    return value.strip(" ,.")


def clean_title(value: str) -> str:
    value = clean_text(value)
    if value.isupper():
        value = value.title()
        replacements = {
            "Rag": "RAG",
            "Scada": "SCADA",
            "Data Acquisition": "Data Acquisition",
        }
        for old, new in replacements.items():
            value = value.replace(old, new)
        for word in ("And", "For", "In", "Of", "The"):
            value = value.replace(f" {word} ", f" {word.lower()} ")
    value = re.sub(
        r"Using Supervisory Control and Data Acquisition",
        "Using SCADA",
        value,
        flags=re.IGNORECASE,
    )
    value = value.replace("Real-TimeWind", "Real-time Wind")
    value = value.replace("Real-timeWind", "Real-time Wind")
    value = value.replace("DetectionUsing", "Detection Using")
    return value


def title_from_line(line: str) -> str:
    quoted = re.search(r'["“](.+?)["”]', line)
    if quoted:
        return clean_title(quoted.group(1))

    title_end = re.search(
        r",\s*(Journal of|Applied Sciences|Sens\. Mater\.|Measurement and Control|"
        r"Engineering Failure Analysis|Scientific Reports|International Journal|"
        r"Advances in Mechanical Engineering|Cogent Engineering)",
        line,
    )
    if not title_end:
        raise ValueError(f"Cannot parse article title: {line}")
    prefix = line[: title_end.start()]
    parts = [part.strip() for part in prefix.split(",") if part.strip()]
    return clean_title(parts[-1])


def authors_from_line(line: str, title: str) -> str:
    idx = line.find(title)
    if idx < 0:
        quoted = re.search(r'["“](.+?)["”]', line)
        idx = quoted.start() if quoted else -1
    authors = line[:idx].strip(" ,") if idx >= 0 else ""
    authors = clean_text(authors)
    # doflab.cc 既有頁面用 strong 標示主要作者，保留這個視覺慣例。
    authors = authors.replace("Jui-Hung Liu*", "<strong>Jui-Hung Liu*</strong>")
    authors = authors.replace("JH Liu*", "<strong>J.H. Liu*</strong>")
    authors = authors.replace("劉瑞弘(Jui-Hung Liu)*", "<strong>劉瑞弘(Jui-Hung Liu)*</strong>")
    return authors


def remove_parenthetical_metrics(text: str) -> str:
    return re.sub(r"\([^)]*(?:SCIE|SCI|EI|IF|Q[1-4]|第一|通訊|s\d+)[^)]*\)", "", text).strip(" ,.")


def parse_metric(line: str) -> tuple[str, str]:
    if "SCIE" in line:
        index = "SCIE"
    elif re.search(r"\bSCI\b", line):
        index = "SCI"
    elif re.search(r"\bEI\b", line):
        index = "EI"
    else:
        index = ""

    metric = ""
    metric_match = re.search(r"(IF\s*:?\s*[^)\n]+|Q[1-4][^)\n]*)", line)
    if metric_match:
        metric = clean_text(metric_match.group(1))
        metric = metric.replace("IF:", "IF ").replace("IF ", "IF ")
    return index, metric


def parse_article(line: str) -> dict[str, str]:
    doi = ""
    doi_match = re.search(r"\[([a-z]+://[^\]]+)\]", line)
    if doi_match:
        doi = doi_match.group(1)
        line = line.replace(doi_match.group(0), "")
    line = clean_text(line.replace("DOI", ""))

    title = title_from_line(line)
    authors = authors_from_line(line, title)
    year = max(re.findall(r"(?<!\d)(20\d{2})(?!\d)", line), default="")
    index, metric = parse_metric(line)

    after_title = line[line.find(title) + len(title):].strip(' ",')
    after_title = remove_parenthetical_metrics(after_title)
    parts = [part.strip() for part in after_title.split(",") if part.strip()]
    venue = clean_text(parts[0]) if parts else ""
    detail = clean_text(", ".join(parts[1:])) if len(parts) > 1 else ""

    return {
        "year": year,
        "title": title,
        "authors": authors,
        "venue": venue,
        "detail": detail,
        "index": index,
        "metric": metric,
        "doi": doi,
    }


def article_key(title: str) -> str:
    title = title.lower().replace("supervisory control and data acquisition", "scada")
    return re.sub(r"[^a-z0-9]+", "", title)


def merge_journals(existing: list[dict[str, str]], latest: list[dict[str, str]]) -> tuple[list[dict[str, str]], bool]:
    latest_by_key = {article_key(item["title"]): item for item in latest}
    seen: set[str] = set()
    merged: list[dict[str, str]] = []
    changed = False

    for item in existing:
        key = article_key(str(item.get("title", "")))
        if key in latest_by_key:
            replacement = latest_by_key[key]
            if key not in seen:
                seen.add(key)
                merged.append(replacement)
                changed = changed or item != replacement
            else:
                changed = True
        else:
            merged.append(item)

    additions = [item for item in latest if article_key(item["title"]) not in seen]
    if additions:
        merged = additions + merged
        changed = True

    merged.sort(key=lambda item: (str(item.get("year", "")), str(item.get("title", ""))), reverse=True)
    return merged, changed or merged != existing


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh publications.json from Google Sites.")
    parser.add_argument("--source-url", default=SOURCE_URL)
    parser.add_argument("--output", type=Path, default=ROOT / "publications.json")
    args = parser.parse_args()

    try:
        source_lines = fetch_lines(args.source_url)
        parsed = [parse_article(line) for line in latest_published_lines(source_lines)]
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        print(f"Unable to refresh publications: {error}", file=sys.stderr)
        return 1

    with args.output.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("journal"), list):
        print("publications.json must contain a journal array.", file=sys.stderr)
        return 1

    journals, changed = merge_journals(data["journal"], parsed)
    if not changed and data.get("_source") == args.source_url:
        print("Publications are already current.")
        return 0

    # 只更新期刊陣列與來源資訊，避免 Google Sites 版面變動影響其他人工分類。
    data["journal"] = journals
    data["_source"] = args.source_url
    data["_updated"] = today()

    rendered = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    previous = args.output.read_text(encoding="utf-8")
    if rendered == previous:
        print("Publications are already current.")
        return 0

    args.output.write_text(rendered, encoding="utf-8")
    print(f"Updated {args.output.relative_to(ROOT)} ({len(parsed)} latest journal articles merged).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
