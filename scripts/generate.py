#!/usr/bin/env python3
"""Generate the app sections of README.md from data/apps.yaml and data/delisted.yaml.

The README's category table-of-contents, app listings, and delisting record live
between marker comments and are overwritten by this script; everything outside the
markers is hand-written and left alone.

Entries must be alphabetical within their category. That is checked in both modes
and is a hard error, so the ordering rule in CONTRIBUTING.md cannot quietly drift
out of true again.

The companion check — that no entry leaves apps.yaml without a delisting record —
lives in check_removals.py, because it needs to compare against another revision.

Usage:
    python scripts/generate.py           # rewrite README.md in place
    python scripts/generate.py --check   # exit 1 if README.md is out of sync (CI)
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
DATA = ROOT / "data" / "apps.yaml"
DELISTED = ROOT / "data" / "delisted.yaml"

BADGES = {"plain-files": "📄", "open-db": "🗃️", "offline": "📵", "sync": "🔁"}
TOC_START, TOC_END = "<!-- TOC:APPS:START -->", "<!-- TOC:APPS:END -->"
APPS_START, APPS_END = "<!-- APPS:START -->", "<!-- APPS:END -->"
DELISTED_START, DELISTED_END = "<!-- DELISTED:START -->", "<!-- DELISTED:END -->"

EMPTY_DELISTED = "*Nothing yet. When it happens, it will be recorded here.*"


def slug(name: str) -> str:
    """GitHub heading anchor: lowercase, strip punctuation, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", name.lower()).replace(" ", "-")


def render_toc(cats: list) -> str:
    return "\n".join(f"- [{c['name']}](#{slug(c['name'])})" for c in cats)


def render_apps(cats: list) -> str:
    lines = []
    for c in cats:
        lines.append(f"## {c['name']}")
        lines.append("")
        if c.get("intro"):
            lines.append(c["intro"].strip())
            lines.append("")
        for a in c["apps"]:
            head = f"- [{a['name']}]({a['url']})"
            if a.get("suffix"):
                head += f" {a['suffix']}"
            if a.get("license"):
                head += f" `{a['license']}`"
            badges = " ".join(BADGES[b] for b in a.get("badges", []))
            if badges:
                head += f" {badges}"
            head += f" — {a['description']}"
            if a.get("disclosure"):
                head += f" *Disclosure: {a['disclosure']}*"
            lines.append(head)
            lines.append(f"  - *Exit: {a['exit']}*")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_delisted(records: list) -> str:
    """Render the delisting record, newest first.

    A relisted app keeps its entry rather than being deleted — the history is the
    whole point of the section, so a reversal is appended, never a removal.
    """
    if not records:
        return EMPTY_DELISTED

    lines = []
    for d in sorted(records, key=lambda r: str(r["delisted"]), reverse=True):
        line = f"- **{d['name']}** — delisted {d['delisted']}: {d['reason']}"
        if d.get("source"):
            line += f" ([source]({d['source']}))"
        if d.get("relisted"):
            line += f" **Relisted {d['relisted']}:** {d['restored']}"
        lines.append(line)
    return "\n".join(lines)


def check_delisted(records: list) -> None:
    """Reject records that cannot carry their own weight.

    A delisting is a public claim about someone else's project, and the badge rule
    makes it consequential, so the fields that make it checkable are mandatory.
    """
    problems = []
    for i, d in enumerate(records):
        where = d.get("name") or f"entry {i + 1}"
        for field in ("name", "delisted", "reason", "source"):
            if not d.get(field):
                problems.append(f"{where}: missing required field '{field}'")
        if d.get("delisted") and not re.fullmatch(r"\d{4}-\d{2}", str(d["delisted"])):
            problems.append(f"{where}: 'delisted' must be YYYY-MM, got {d['delisted']!r}")
        if d.get("relisted"):
            if not re.fullmatch(r"\d{4}-\d{2}", str(d["relisted"])):
                problems.append(f"{where}: 'relisted' must be YYYY-MM, got {d['relisted']!r}")
            if not d.get("restored"):
                problems.append(f"{where}: 'relisted' requires 'restored' saying what changed")

    if problems:
        for p in problems:
            print(f"error: {p}", file=sys.stderr)
        sys.exit("delisting records are incomplete — see CONTRIBUTING.md")


def check_order(cats: list) -> None:
    """Exit with a diff-style report if any category is not alphabetical.

    Sorting is case-insensitive so that lowercase-styled names (darktable,
    restic, draw.io) sort by spelling rather than by capitalisation.
    """
    problems = []
    for c in cats:
        names = [a["name"] for a in c["apps"]]
        expected = sorted(names, key=str.lower)
        if names != expected:
            problems.append((c["name"], names, expected))

    if problems:
        for name, got, want in problems:
            print(f"error: {name} is not in alphabetical order", file=sys.stderr)
            print(f"           is: {', '.join(got)}", file=sys.stderr)
            print(f"       should: {', '.join(want)}", file=sys.stderr)
        sys.exit("entries must be alphabetical within their category — see CONTRIBUTING.md")


def splice(text: str, start: str, end: str, payload: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        sys.exit(f"error: markers {start} … {end} not found in README.md")
    return pattern.sub(lambda _: f"{start}\n{payload}\n{end}", text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if README.md is out of sync with data/apps.yaml")
    args = parser.parse_args()

    cats = yaml.safe_load(DATA.read_text(encoding="utf-8"))["categories"]
    check_order(cats)
    records = yaml.safe_load(DELISTED.read_text(encoding="utf-8"))["delisted"] or []
    check_delisted(records)

    text = README.read_text(encoding="utf-8")
    new = splice(text, TOC_START, TOC_END, render_toc(cats))
    new = splice(new, APPS_START, APPS_END, render_apps(cats))
    new = splice(new, DELISTED_START, DELISTED_END, render_delisted(records))

    if args.check:
        if new != text:
            sys.exit("README.md is out of sync with the data files — run: python scripts/generate.py")
        print("README.md is in sync.")
    else:
        README.write_text(new, encoding="utf-8")
        n_apps = sum(len(c["apps"]) for c in cats)
        print(f"README.md regenerated: {len(cats)} categories, {n_apps} apps, "
              f"{len(records)} delisted.")


if __name__ == "__main__":
    main()
