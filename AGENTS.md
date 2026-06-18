# Agent Instructions

This repository contains editable Markdown source for the APSC 453 Science &
Authority course site.

Main paths:

- `docs/_materials/` contains course pages.
- `docs/_posts/` contains course updates.
- `docs/index.md`, `docs/pages.md`, and `docs/posts.md` are top-level editable
  pages.
- `docs/assets/` contains site assets.
- `docs/wp-content/uploads/` contains local WordPress media copies where
  practical.
- `.github/workflows/pages.yml` builds and deploys the Jekyll site from `docs/`
  on pushes to `main`.

Prefer editing Markdown source under `docs/`; do not hand-edit generated HTML.
Do not run local Jekyll/Bundler unless Greg explicitly asks. The normal
publication path is GitHub Actions after pushing to `main`.

Useful lightweight checks:

```bash
git status --short --branch
git diff --check
```

Avoid committing `_site/`, Bundler artifacts, local caches, or regenerated
export clutter unless explicitly requested.
