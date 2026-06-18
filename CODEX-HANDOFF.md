# Codex Handoff

Date: 2026-06-18

Repo: `science-and-authority`

Branch: `main`

Current Git status at handoff creation:

```bash
## main...origin/main
```

## Repository Role

This repository publishes the APSC 453 Science & Authority course site from
editable Markdown source in `docs/`.

## High-Value Context

- Read `AGENTS.md` before editing.
- Source pages live in `docs/_materials/`.
- Source posts live in `docs/_posts/`.
- GitHub Actions builds Jekyll from `docs/` and deploys Pages.
- The original WordPress export is preserved under `tmp/`.
- One oversized audio file is intentionally left as an external WordPress link
  because it exceeds GitHub's normal 100 MB file limit.

## Useful Commands

Check Git state:

```bash
git status --short --branch
git diff --check
```

Inspect the Pages workflow:

```bash
sed -n '1,220p' .github/workflows/pages.yml
```

## Notes For The Next Codex

- Do not run local Jekyll/Bundler unless Greg explicitly asks.
- Keep source edits in Markdown and shared layouts/assets.
- Avoid committing generated `_site/`, Bundler artifacts, or export noise.
- After adding or updating `AGENTS.md` / `CODEX-HANDOFF.md`, commit the scoped
  change and push it to `main`.
