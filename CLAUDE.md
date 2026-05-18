# Forming Worlds Website

Group website for the [Forming Worlds Lab](https://formingworlds.space) at the Kapteyn Astronomical Institute, University of Groningen. Replaces a previous Wix site. The design is a dark-themed, single-page-per-section static site that faithfully reproduces the original Wix visual style.

## Stack

- **Hugo 0.157+** — static site generator
- **Tailwind CSS v4** — via native Hugo `css.TailwindCSS` pipe (no PostCSS config needed)
- **GitHub Actions** — CI/CD to GitHub Pages on push to `main`
- **Formspree** — contact form backend

## Project structure

```
content/             Markdown content pages (each section has _index.md)
layouts/
  _default/          Base templates (baseof, list, single); list supports banner_image hero
  index.html         Homepage slideshow (full-viewport carousel)
  team/              Team grid (list.html) + profile pages (single.html)
  join/              Position cards (list.html) + detail pages (single.html)
  publications/      Sidebar + scrolling content (list.html)
  research/          Goals + prose (list.html)
  contact/           Two-column: info + form (list.html)
  partials/          header, footer, head, team-card-data
assets/css/main.css  Tailwind v4 CSS-first config (@theme block + component classes)
data/
  team.json          Team members: {name, slug, role, group, image, topics, page, links}
  slides.json        Homepage carousel: {image, question, credit}
  features.json      Homepage feature cards: {icon, title, description}
  research_topics.json  Research section topics
static/img/
  faces/             Team profile photos (AVIF, ~20-50KB each)
  research/          Research topic and slideshow backgrounds
  brand/             Logos
  illustrations/     Group photos, page illustrations
hugo.toml            Site config, menus, params
```

## Design system

Authoritative reference: the comment block at the top of `assets/css/main.css`. Summary of the current Field Station design language:

**Palette** (three-token system, defined in `@theme`):
- **Ink** — cool neutral ramp, ink-50 (near-white) through ink-980 (near-black). Page background is ink-950; body text ink-100/200; muted body ink-300/400; section borders ink-700/800.
- **Signal** — brand blue, seeded by the logo (#0072A1 at signal-500). Used for links (signal-300, hover signal-400) and primary CTAs (.btn-primary fills signal-500/400).
- **Magma** — warm planet-formation accent. Used for important callouts and the .btn-warm CTA variant. Patterns: full callout box (background + left border + magma-300 text, see join/single.html deadline alert) or left-border sidenote (border + magma-300 text only).

**Typography**:
- Display/heading font: Geist (via Google Fonts).
- Section headings use **sentence-case ending in a period**: "Our team.", "Publications.", "Research.". The period is the design's tic; never drop it.
- Small section labels (sidebar h3s, year dividers): `text-xs uppercase tracking-wider text-ink-400`.
- Long-form text via `.prose-content` (line-height 1.65, ink-200, signal-300 links, h2/h3/h4 spacing built in).

**Component primitives** (all defined in `assets/css/main.css`):
`.container-site`, `.btn-primary` / `.btn-ghost` / `.btn-warm` (+ `.btn-sm` / `.btn-lg`), `.team-card`, `.alumni-grid`, `.prose-content`, `.year-divider`, `.gallery-masonry`.

**Layout primitives**:
- Container max-width: `var(--container-max)` = 1280px.
- Navbar: 120px tall, items vertically centered, no internal padding (height does the spacing).
- Hero section padding-top: **6rem** across all top-level pages (matches the navbar bump).
- Hero intro paragraphs widen to **2/3 container** via `style="max-width: calc(var(--container-max) * 2 / 3)"` (~853px at the widest viewport).
- Section vertical padding: typically `padding: 4rem 0 5rem`.

**Design anti-patterns to avoid**:
- New color/font tokens outside the ink / signal / magma vocabulary. Extend if absolutely necessary; otherwise reuse.
- Raw hex codes in component CSS. Always reference `var(--color-*)` so `@theme` stays the single source of truth.
- Arbitrary-value Tailwind utilities in layouts (`gap-3`, `py-32`, `grid-cols-[24px_1fr]`, etc.). Hugo's TW4 pipe doesn't reliably emit them; use inline `style=""` or define a class in `main.css`.
- Em-dashes / en-dashes in user-facing copy. Use commas, semicolons, colons, or parentheses.
- Orphan data files (data/*.json without a layout that consumes them).

Background context: `navy-*` / `sky-*` / `accent-*` tokens from the original Wix port still exist as aliases in `@theme` and are mapped to the current ink/signal/magma values. Don't author new work against those names.

## Key conventions

### Data-driven content

Team members, slides, and features are stored in `data/*.json`, not in markdown front matter. Layouts iterate with `{{ range .Site.Data.team }}`. Adding a team member means editing `data/team.json` and adding a photo to `static/img/faces/`.

Team member groups: `lead`, `postdoc`, `phd`, `student`, `staff`, `alumni`. Current members are all non-alumni. Alumni render as compact cards (5-column grid, no social icons) via the `hideLinks` flag passed to the `team-card-data.html` partial. New members are always appended at the end of the current members list (before alumni), strictly in chronological join order. Do not sort by role or group.

### Images

- Profile photos: AVIF format, quality 45, target <100KB. Convert with: `sips -s format avif -s formatOptions 45 input.jpg --out output.avif`
- All images go in `static/img/` subdirectories, not in `content/`

### Publications

`content/publications/_index.md` contains the full publication list as markdown. Lab members are **bolded** in author lists. Format:

```
AuthorA X, **T Lichtenberg**, AuthorB Y. [Title.](ADS_URL) *Journal* vol, page (year). [pdf](arxiv_pdf_url)
```

Sidebar links (ADS, SciX, arXiv, Google Scholar) are in `layouts/publications/list.html`, duplicated for mobile and desktop views.

### Navbar

Transparent, absolutely positioned over page content. CSS-only hover dropdowns using Tailwind `group`/`group-hover:block`. Active page highlighted with `text-sky-400`. Uses URL comparison (`eq $.RelPermalink`) for active state.

### Sub-page hero banners

`banner_image` in front matter triggers a full-width image (~50vh) with gradient overlay and title. Used on join sub-pages and Kapteyn & Groningen.

## Development

```bash
npm install          # Install Tailwind dependencies
hugo server          # Dev server at localhost:1313
hugo --minify        # Production build
```

Hugo may grab alternative ports if 1313 is busy — check with `lsof -i :1313`.

## Tailwind v4 gotchas

- Config is CSS-first via `@theme` blocks in `assets/css/main.css` — no `tailwind.config.js`.
- `@apply` cannot reference custom classes defined in the same CSS file. Component classes must inline Tailwind utilities directly.
- Hugo's native `css.TailwindCSS` pipe handles everything — no PostCSS config needed.

## URL shortener

`https://go.formingworlds.space/<slug>` 302-redirects to a target URL stored in a Cloudflare KV namespace. Implementation lives in `workers/shortlinks/`; see `workers/shortlinks/README.md` for the slug add/update/delete workflow and the Cloudflare API token location.

DNS and TLS are handled by Cloudflare (zone is on `kareem.ns.cloudflare.com` / `nena.ns.cloudflare.com`). The Worker code is independent of the Hugo build — Hugo deploys via GitHub Pages, the Worker deploys via `wrangler`.
