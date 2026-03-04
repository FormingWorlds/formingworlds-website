# Forming Worlds Website

Group website for the [Forming Worlds Lab](https://formingworlds.space) at the Kapteyn Astronomical Institute, University of Groningen.

Built with [Hugo](https://gohugo.io/) and [Tailwind CSS v4](https://tailwindcss.com/).

## Local Development

```bash
# Install dependencies
npm install

# Run development server
hugo server

# Build for production
hugo --minify
```

## Adding Team Members

```bash
hugo new content team/<firstname-lastname>.md
```

Then edit the front matter — see `archetypes/team.md` for the template.

## Project Structure

```
content/         # Markdown content pages
layouts/         # Hugo templates
assets/css/      # Tailwind CSS source
static/img/      # Images (faces, brand, illustrations)
data/            # Structured data (features, etc.)
```

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions on push to `main`.
