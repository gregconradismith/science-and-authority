# Codex Handoff

Date: 2026-06-21

Repo: `science-and-authority`

Branch: `main`

Current Git status after the 2026-06-21 announcement review:

```bash
## main...origin/main
 M docs/_layouts/home.html
 M docs/_layouts/listing.html
 D docs/_posts/2026-01-21-welcome-to-science-authority.md
 D docs/_posts/2026-01-28-transitioning-from-snow-days-to-our-second-class-meeting.md
 D docs/_posts/2026-02-03-biology-seminar-that-may-be-of-interest.md
 D docs/_posts/2026-03-03-thursday-defending-second-hand-smoke.md
 D docs/_posts/2026-03-16-assignment-for-tuesday-march-17.md
 D docs/_posts/2026-03-18-assignment-for-thursday-march-19.md
 D docs/_posts/2026-03-23-midterm-projects-and-assignment-for-tuesday-march-24.md
 D docs/_posts/2026-03-25-thursday-march-24-the-universal-solvent.md
 D docs/_posts/2026-04-04-what-is-scientism.md
 D docs/_posts/2026-04-07-assignment-for-class-on-thursday.md
 D docs/_posts/2026-04-12-assignment-email-me-a-description-of-your-final-project.md
 D docs/_posts/2026-04-27-final-projects.md
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
- Public site: https://gregconradismith.github.io/science-and-authority/
- Recent design work aligned the site with the
  `cellular-biophysics-and-modeling` course-site style:
  - landing page uses a full-width image banner;
  - landing page menu uses large centered buttons;
  - home page recent announcements use a centered dated list;
  - `/posts/` Announcements uses a centered dated list rather than card panels;
  - archive/export framing was removed from public-facing pages.
- The latest pushed commit at this handoff is `43cc79b` (`Remove announcements
  subtitle`). If local state differs, inspect `git log --oneline -5`.
- On 2026-06-21, Greg reviewed Science & Authority announcement posts one by
  one. Eight posts remain in `docs/_posts/`; twelve announcement posts were
  deleted. `git diff --check` passed after the review. The layout edits to
  `docs/_layouts/home.html` and `docs/_layouts/listing.html` were already
  present before this announcement cleanup and should be treated as separate
  work unless Greg says otherwise.
- Later on 2026-06-21, the remaining announcement posts were scrubbed of
  visible date, semester, and scheduling language while preserving Jekyll
  frontmatter dates, filenames, and required asset paths.

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
- Preserve the CBM-inspired live-course-portal feel. Avoid reverting to
  generic WordPress-export card grids for the landing page or Announcements.
- Avoid committing generated `_site/`, Bundler artifacts, or export noise.
- After adding or updating `AGENTS.md` / `CODEX-HANDOFF.md`, commit the scoped
  change and push it to `main`.
