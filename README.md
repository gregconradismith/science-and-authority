# Science & Authority

This repository contains editable Markdown source files for the APSC 453
Science & Authority course site, plus the original WordPress export used to
create the first static version.

## Editing the site

Edit course pages in `docs/_materials/` and course updates in `docs/_posts/`.
The top-level editable pages are:

- `docs/index.md`
- `docs/pages.md`
- `docs/posts.md`

Assets live in `docs/assets/` and uploaded media lives in
`docs/wp-content/uploads/`.

## Publishing

When changes are committed to `main`, the GitHub Pages workflow builds the HTML
site from the Markdown files with Jekyll and deploys the generated `_site`
artifact.

The source site includes:

- A course landing page generated from `docs/index.md`
- Static course pages generated from `docs/_materials/*.md`
- Course updates generated from `docs/_posts/*.md`
- Local copies of the WordPress media export where practical
- Lightweight filtering on the page and post index views

One oversized audio file is intentionally left as an external WordPress link
because it exceeds GitHub's normal 100 MB file limit.

## Original export

The original WordPress export is preserved at
`tmp/apsc453scienceampauthority.WordPress.2026-05-06.xml`.
