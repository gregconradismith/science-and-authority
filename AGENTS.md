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

Design and site-structure preferences:

- Use `cellular-biophysics-and-modeling` as the main style guide for this
  course site.
- The site should feel like a current course portal, not a WordPress export or
  archive.
- The landing page should use the CBM-style full-width image banner, large
  centered menu buttons, and a centered list of recent Announcements.
- The primary menu should focus on student-facing course affordances such as
  About, Syllabus, Calendar, Readings, Projects, and Announcements.
- The Announcements page (`docs/posts.md`, rendered through
  `docs/_layouts/listing.html`) should be a centered dated list, not a grid of
  square cards. Materials listings may remain searchable card grids.
- Avoid visible wording such as "from the export" on public-facing course
  pages.

Useful lightweight checks:

```bash
git status --short --branch
git diff --check
```

Avoid committing `_site/`, Bundler artifacts, local caches, or regenerated
export clutter unless explicitly requested.
