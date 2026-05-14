# fw-shortlinks

Cloudflare Worker that serves `https://go.formingworlds.space/<slug>` → 302 redirect to a URL stored in a Cloudflare KV namespace. Unknown or empty slugs fall back to `https://formingworlds.space/`.

## Architecture

- **Worker**: `src/index.js` — 20 lines, reads slug from path, looks up `env.LINKS.get(slug)`, returns 302.
- **KV namespace**: `LINKS`, id `c72549669e824027a45762e9462f2262`. Slugs are keys, target URLs are values.
- **Custom domain**: `go.formingworlds.space`, bound via `routes = [{ pattern = "go.formingworlds.space", custom_domain = true }]` in `wrangler.toml`. Cloudflare manages the DNS record and TLS cert.

## Authentication

`wrangler` reads a Cloudflare API token from `CLOUDFLARE_API_TOKEN`. The token lives at `~/.cloudflare-fw-token` (mode 600, never committed). Every wrangler invocation in this repo should be prefixed:

```bash
CLOUDFLARE_API_TOKEN=$(cat ~/.cloudflare-fw-token | tr -d '\n\r') npx wrangler <command>
```

To rotate the token: create a new one at https://dash.cloudflare.com/profile/api-tokens (template "Edit Cloudflare Workers", zone scoped to `formingworlds.space`), overwrite the file, revoke the old token.

## Adding a slug

```bash
cd workers/shortlinks
CLOUDFLARE_API_TOKEN=$(cat ~/.cloudflare-fw-token | tr -d '\n\r') npx wrangler kv key put --binding=LINKS <slug> "<target_url>"
```

KV is eventually consistent globally; new keys are live within ~60s.

## Updating a slug

Same command as adding. The key is overwritten.

## Deleting a slug

```bash
CLOUDFLARE_API_TOKEN=$(cat ~/.cloudflare-fw-token | tr -d '\n\r') npx wrangler kv key delete --binding=LINKS <slug>
```

## Listing all slugs

```bash
CLOUDFLARE_API_TOKEN=$(cat ~/.cloudflare-fw-token | tr -d '\n\r') npx wrangler kv key list --binding=LINKS
```

## Deploying code changes

If `src/index.js` or `wrangler.toml` changes:

```bash
CLOUDFLARE_API_TOKEN=$(cat ~/.cloudflare-fw-token | tr -d '\n\r') npx wrangler deploy
```

## Slug conventions

- All slugs are lowercased by the Worker before lookup (`/Test` and `/test` both hit the `test` key).
- Trailing slashes are stripped (`/zoom/` resolves the same as `/zoom`).
- Slugs should be short, memorable, and URL-safe. Prefer single English words (`zoom`, `handbook`, `cv`) over `talk-2026-04-groningen-v2`.
- Reserved slugs to avoid (collide with site paths): `team`, `research`, `publications`, `join`, `contact`.

## Live slugs

Use the listing command above for the current state. Smoke-test slugs:

- `test` → research page (intentional, used to verify the Worker is alive)

## Failure modes

- **404 on custom domain**: TLS cert hasn't provisioned. Wait 5 min after first `wrangler deploy`. After that, cert auto-renews indefinitely.
- **302 to apex for a slug that should resolve**: KV propagation lag (<60s after write), or slug typo (case-insensitive but otherwise exact match).
- **`Unauthenticated` error from wrangler**: token expired or revoked, or `~/.cloudflare-fw-token` is missing/unreadable.
