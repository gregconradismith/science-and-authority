# Science & Authority

This repository contains a WordPress export and a generated static version of
the APSC 453 Science & Authority course site.

## Static site

Open `docs/index.html` in a browser to browse the generated site locally. For
GitHub Pages, configure the repository to serve from the `main` branch and the
`/docs` folder.

The generated site includes:

- A course landing page
- Static pages for the syllabus, calendars, readings, foundations, case studies,
  project descriptions, and resources
- A course updates archive generated from published WordPress posts
- Local copies of the WordPress media export where practical
- Lightweight filtering on the page and post index views

One oversized audio file is intentionally left as an external WordPress link
because it exceeds GitHub's normal 100 MB file limit.

## Regenerate

```sh
sage -python tools/build_static_site.py
```

The generator reads `tmp/apsc453scienceampauthority.WordPress.2026-05-06.xml`,
copies media from `tmp/media-export-203120012-from-0-to-7589`, and rewrites
`docs/`.

If a media file is referenced in the XML but missing from the local media export,
you can attempt a direct download from WordPress with:

```sh
sage -python tools/download_wordpress_uploads.py
```
