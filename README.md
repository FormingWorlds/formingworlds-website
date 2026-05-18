# Forming Worlds Website

Source for [formingworlds.space](https://formingworlds.space), the group website of the [Forming Worlds Lab](https://formingworlds.space) at the Kapteyn Astronomical Institute, University of Groningen.

The site is a dark-themed Hugo static site (the "Field Station" design language) hosted on GitHub Pages, with a small Cloudflare Worker for URL shortening on `go.formingworlds.space` and `timlichtenberg.net`.

## Stack

- **Hugo 0.147+** (extended), static site generator
- **Tailwind CSS v4** via the native `css.TailwindCSS` Hugo pipe (no PostCSS, no `tailwind.config.js`)
- **GitHub Actions** for CI/CD to GitHub Pages on push to `main`
- **Formspree** as the contact form backend
- **Cloudflare Workers + KV** for the `go.formingworlds.space` shortlinks (separate deploy path, see `workers/shortlinks/`)

## Local development

```bash
npm install           # Tailwind v4 CLI + tailwindcss
hugo server           # dev server, usually http://localhost:1313
hugo --minify         # production build into ./public
```

Hugo picks an alternative port if 1313 is busy. Check with `lsof -i :1313`.

After adding a new section-specific layout directory, restart the dev server with `--disableFastRender` once so Hugo notices it.

## Adding a team member

Team data lives in `data/team.json` (a flat array), not in markdown front matter.

1. Add a profile photo to `static/img/faces/<slug>.avif`. Convert from JPG/PNG with:
   ```bash
   sips -s format avif -s formatOptions 45 input.jpg --out static/img/faces/<slug>.avif
   ```
   Target under 100 KB. Make sure both pixel dimensions are even (Safari's AVIF decoder rejects odd dimensions silently).
2. Append a new entry to `data/team.json` at the end of the current-members section (above the alumni block). New members go last in chronological join order; do not sort by role or group.
3. If the member needs a profile page, set `page: true` and add `content/team/<slug>.md`.

Each entry looks like:

```json
{
  "name": "Firstname Lastname",
  "slug": "firstname-lastname",
  "role": "PhD student",
  "group": "phd",
  "image": "/img/faces/firstname-lastname.avif",
  "topics": ["topic 1", "topic 2"],
  "page": true,
  "links": { "email": "...", "github": "...", "orcid": "..." }
}
```

Groups: `lead`, `postdoc`, `phd`, `student`, `staff`, `alumni`. Alumni render in a compact 5-column grid without social icons.

## Project structure

```
content/              Markdown pages (each section has _index.md)
  contact/              two-column contact page + getting-to-kapteyn sub-page
  join/                 position cards (PhD, postdoc, student, code of conduct)
  publications/         year-divided publication list
  research/             goals and prose
  team/                 team intro page (members come from data/team.json)
  kapteyn-groningen/    Groningen city + institute page

layouts/
  _default/             baseof, list, single (list supports banner_image hero)
  index.html            homepage slideshow + about section
  partials/             header, footer, head, team-card-data
  <section>/            section-specific list and single templates

assets/css/main.css   Tailwind v4 CSS-first config (@theme + component classes)
data/                 team.json, slides.json, group_photos.json, research_topics.json, groningen_gallery.json
static/img/           faces/, brand/, research/, illustrations/, logos/, groningen/
static/CNAME          custom-domain marker for GitHub Pages

workers/shortlinks/   Cloudflare Worker for go.formingworlds.space + timlichtenberg.net
.github/workflows/    deploy.yml builds Hugo and publishes to GitHub Pages
hugo.toml             site config, menus, params (analytics, formspree, social links)
```

## Design system

The authoritative reference is the comment block at the top of `assets/css/main.css`. The short version:

- Three color tokens: **ink** (cool neutral ramp), **signal** (brand blue, links and primary CTAs), **magma** (warm accent for callouts and the `.btn-warm` variant). All defined in `@theme` so the palette has a single source of truth.
- Heading font is Geist. Section headings are sentence-case and end with a period ("Our team.", "Publications.", "Research.").
- Long-form text uses `.prose-content`; small section labels use `text-xs uppercase tracking-wider text-ink-400`.
- Component primitives in `main.css`: `.container-site`, `.btn-primary` / `.btn-ghost` / `.btn-warm`, `.team-card`, `.alumni-grid`, `.prose-content`, `.year-divider`, `.gallery-masonry`.

Anti-patterns to avoid:

- New tokens outside the ink / signal / magma vocabulary. Extend if you must, otherwise reuse.
- Raw hex codes in component CSS. Always reference `var(--color-*)`.
- Arbitrary-value Tailwind utilities in layout templates (`gap-3`, `py-32`, `grid-cols-[24px_1fr]`, etc.). Hugo's TW4 pipe does not reliably emit them. Use inline `style=""` for one-offs or define a class in `main.css`.
- Em-dashes and en-dashes in user-facing copy. Use commas, semicolons, colons, or parentheses.

The `navy-*`, `sky-*`, and `accent-*` tokens from the original Wix port still exist as aliases in `@theme` but should not be used for new work.

## Publications

`content/publications/_index.md` is the canonical list, edited by hand. Lab members are bolded in author lists. Entries follow:

```
AuthorA X, **T Lichtenberg**, AuthorB Y. [Title.](scix_arxiv-stable_URL) *Journal* vol, page (year). [pdf](arxiv_pdf_url)
```

The list is split by year via `.year-divider` headings (most recent first, with everything up to and including 2022 collapsed under "≤ 2022"). The sidebar links (ADS, SciX, arXiv, Google Scholar) are defined in `layouts/publications/list.html` and duplicated for the mobile pill nav.

## Deployment

Push to `main` triggers `.github/workflows/deploy.yml`, which:

1. Installs Hugo extended 0.147 and Node 22, runs `npm ci`.
2. Calls `actions/configure-pages` (this auto-detects the custom domain and passes the correct `--baseURL`).
3. Runs `hugo --minify`.
4. Publishes `./public` to GitHub Pages.

Custom domain `formingworlds.space` (plus `www`, `ips`, `aes` subdomains) is served via Cloudflare DNS pointing at GitHub Pages IPs. The `static/CNAME` file is what tells GitHub Pages to expect that domain.

If you change the custom domain in GitHub Pages settings, re-trigger a deploy: the configure-pages action caches the previous base URL otherwise and asset paths break.

## URL shortener

`https://go.formingworlds.space/<slug>` 302-redirects to a target URL stored in Cloudflare KV. The same Worker also serves `timlichtenberg.net/<slug>` (slugs prefixed `tl:` in KV, fall through to `/team/tim-lichtenberg/`).

Implementation lives in `workers/shortlinks/`; see `workers/shortlinks/README.md` for the add/update/delete workflow and where the Cloudflare API token is stored. The Worker deploys via `wrangler` and is independent of the Hugo build.

## Repo conventions

- Branch naming for non-trivial work: `tl/<short-description>`.
- Direct pushes to `main` are allowed for small content updates (publications, team data, copy fixes). Larger structural changes should go through a feature branch.
- Generated images and screenshots from local sessions stay out of the repo. The root-level globs in `.gitignore` (`/*.png`, `/*.jpg`, `/*.webp`, etc.) catch the common cases.
- `CLAUDE.md` carries project-specific instructions for AI-assisted edits; treat it as part of the codebase.
