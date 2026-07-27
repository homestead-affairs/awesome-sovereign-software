# Contributing

Thanks for helping keep this list useful. The bar is the [Sovereignty Test](README.md#the-sovereignty-test) —
read it before opening a pull request.

## Ground rules

- **One app per pull request.** Small PRs get reviewed fast; batches stall.
- **Fill in the checklist** in the PR template. Every criterion, honestly. "Mostly" is a no.
- **Alphabetical order** within each category, compared case-insensitively — so `darktable`
  sorts before `digiKam`, and `draw.io Desktop` before `Excalidraw`. The generator refuses to
  run if an entry is out of place and prints where it belongs, so you find out before a
  reviewer has to tell you.
- **No self-promotion without disclosure.** Submitting your own project is welcome — say so in
  the PR, and it will be marked in the entry like the existing disclosed entries.
- Removals and corrections are as valuable as additions. If an app added an account wall,
  went subscription-only, or shut down, open a PR (or an issue) to **delist** it — see
  [delisting an entry](#delisting-an-entry). Entries don't silently vanish, and CI enforces it.

## Where entries live

The app listings in README.md are **generated** — don't edit them by hand. Add or change
entries in [`data/apps.yaml`](data/apps.yaml), then regenerate:

```bash
pip install pyyaml          # once
python scripts/generate.py  # rewrites the generated sections of README.md
```

Commit both files. CI fails the PR if they drift apart. Everything outside the marked
sections of the README (the test, the stack, resources, papers, the badge) is hand-written —
edit those directly.

## Entry format

```yaml
- name: App Name
  url: https://homepage-or-repo
  license: MIT              # SPDX id, Source-available, or Proprietary
  badges: [plain-files]     # ordered subset: plain-files, open-db, offline, sync
  description: "One sentence: what it does and why it is sovereign."
  exit: "how you leave with your data, in one sentence."
```

Which renders in the README as:

```markdown
- [App Name](https://homepage-or-repo) `MIT` 📄 — One sentence: what it does and why it is sovereign.
  - *Exit: how you leave with your data, in one sentence.*
```

- Link to the project homepage, or the source repository if there is no homepage.
- `LICENSE` in backticks: the SPDX identifier (`MIT`, `AGPL-3.0`, …), `Source-available`, or `Proprietary`.
- Badges, in this order where they apply: 📄 plain-file data · 🗃️ open database format · 📵 fully offline · 🔁 optional user-controlled/E2EE sync.
- Description ends with a period. Keep it under ~25 words. Say what the data story is if it isn't obvious.
- **The exit line is mandatory.** Name the concrete mechanism — the file format, the export
  command, the folder you copy. "It has export" is not an exit plan; "export decks as `.apkg`
  or plain text" is. If you can't write the line honestly, the app doesn't qualify.

## Delisting an entry

An app that stops passing the [Sovereignty Test](README.md#the-sovereignty-test) moves out of
`data/apps.yaml` and into [`data/delisted.yaml`](data/delisted.yaml). It is never just deleted:
`scripts/check_removals.py` compares the roster against the base branch and fails CI on any name
that disappears without an account of why. That is what keeps "entries don't silently vanish"
an actual property of this repo rather than a good intention.

```yaml
delisted:
  - name: Example App
    delisted: 2026-01
    reason: "v5 requires an account to open existing local files — fails criterion 1."
    source: https://web.archive.org/web/2026/https://example.com/blog/v5-release-notes
```

Which renders in the README as:

```markdown
- **Example App** — delisted 2026-01: v5 requires an account to open existing local files — fails criterion 1. ([source](https://web.archive.org/web/2026/https://example.com/blog/v5-release-notes))
```

- **Name the criterion that broke.** "Got worse" is not a delisting; "requires an account to open
  local files, fails criterion 1" is.
- **The source is mandatory.** A delisting is a public claim about someone else's project, and the
  [badge](README.md#the-badge) rule makes it bite — a delisted project has to stop displaying it.
  Link the release notes, changelog, or issue that documents the change. Prefer an archived URL:
  this record is meant to outlive the project, and evidence that 404s is no evidence at all.
- **Regressions get delisted, not deleted.** Shutting down counts as a regression too.

An app that reverses the regression is re-added to `apps.yaml` **and keeps its record here** —
add `relisted` and `restored` rather than deleting anything. The history is the point.

```yaml
  - name: Example App
    delisted: 2026-01
    reason: "v5 requires an account to open existing local files — fails criterion 1."
    source: https://web.archive.org/web/2026/https://example.com/blog/v5-release-notes
    relisted: 2026-06
    restored: "v5.4 made the account optional again; local files open with no sign-in."
```

Renaming an entry is not a delisting. Record it under `renames:` in the same file so the removal
check can tell the two apart and the old name stays findable.

## What gets rejected

- Requires an account, sign-up, or activation for core features.
- Requires a server — including "just self-host it." Those belong on
  [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted).
- Core functionality behind a subscription or that stops working when payment stops.
- Data locked in an undocumented format with no real export.
- Phones home as a condition of working (license checks that brick the app offline count).
- Abandoned **and** broken. Abandoned but still working is fine — that's rather the point —
  but note it in the PR so it can be flagged if needed.

## Proprietary software

Admitted reluctantly, and only when the data format is fully open (e.g. a folder of Markdown)
and every other criterion passes. Always marked `Proprietary`. When an open-source app does the
same job as well, it is preferred and the proprietary one may be dropped.

## New categories

Open an issue first. A category needs at least three qualifying entries to exist.
