#!/usr/bin/env python3
"""Fail if an entry left data/apps.yaml without a record in data/delisted.yaml.

The README promises that entries "move here with a date and a reason instead of
silently vanishing". Nothing enforced that: deleting an app from apps.yaml and
regenerating leaves both the sync check and the link check perfectly happy, and
the entry is simply gone. This closes that hole.

Removals are legitimate — apps regress, and delisting them is the point. What is
not legitimate is a removal with no record, so this compares the app roster
against a base revision and demands an account of every name that disappeared.

Usage:
    python scripts/check_removals.py --base origin/main
    python scripts/check_removals.py --base <sha>
"""
import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_REL = "data/apps.yaml"
DELISTED = ROOT / "data" / "delisted.yaml"


def names_from(text: str) -> set:
    cats = yaml.safe_load(text)["categories"]
    return {a["name"] for c in cats for a in c["apps"]}


def base_names(ref: str) -> set:
    """The app roster as of `ref`, or an empty set if the file did not exist yet."""
    try:
        out = subprocess.run(
            ["git", "show", f"{ref}:{DATA_REL}"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        if "does not exist" in stderr or "exists on disk, but not in" in stderr:
            return set()
        sys.exit(f"error: could not read {DATA_REL} at {ref}: {stderr}")
    return names_from(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True,
                        help="git ref to compare against (e.g. origin/main, or the PR base sha)")
    args = parser.parse_args()

    before = base_names(args.base)
    after = names_from((ROOT / DATA_REL).read_text(encoding="utf-8"))

    doc = yaml.safe_load(DELISTED.read_text(encoding="utf-8"))
    accounted = {d["name"] for d in (doc.get("delisted") or [])}
    renamed = {r["from"] for r in (doc.get("renames") or [])}

    unexplained = sorted(before - after - accounted - renamed, key=str.lower)
    if unexplained:
        for name in unexplained:
            print(f"error: {name} was removed from {DATA_REL} with no record of why",
                  file=sys.stderr)
        print("", file=sys.stderr)
        print("Entries do not silently vanish from this list. Either:", file=sys.stderr)
        print("  - it regressed      → add a delisting record to data/delisted.yaml", file=sys.stderr)
        print("  - it was renamed    → add it to the `renames:` list there", file=sys.stderr)
        print("See CONTRIBUTING.md#delisting-an-entry.", file=sys.stderr)
        sys.exit(1)

    removed = len(before - after)
    print(f"Removal check passed against {args.base}: "
          f"{len(after)} entries, {removed} removed and accounted for.")


if __name__ == "__main__":
    main()
