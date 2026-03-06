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

Dark navy theme defined in `assets/css/main.css` `@theme` block:

- **Background**: `bg-navy-950` (#060609, near-black)
- **Cards**: `bg-transparent` for team cards; `bg-navy-800 border-navy-700` for general cards
- **Text**: `text-slate-200` body, `text-white` headings
- **Links**: `text-sky-400 hover:text-sky-300` in prose
- **Buttons**: `bg-sky-600 hover:bg-sky-500` or `bg-accent-500 hover:bg-accent-600`
- **Heading font**: Jost (Google Fonts, free Futura alternative) via `--font-heading`
- **Body font**: Helvetica Neue via `--font-sans`

## Key conventions

### Data-driven content

Team members, slides, and features are stored in `data/*.json`, not in markdown front matter. Layouts iterate with `{{ range .Site.Data.team }}`. Adding a team member means editing `data/team.json` and adding a photo to `static/img/faces/`.

Team member groups: `lead`, `postdoc`, `phd`, `student`, `staff`, `alumni`. Current members are all non-alumni. Alumni render as compact cards (5-column grid, no social icons) via the `hideLinks` flag passed to the `team-card-data.html` partial.

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
