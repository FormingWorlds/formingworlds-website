# fw-shortlinks

Cloudflare Worker that serves 302 redirects on two custom domains:

- `https://go.formingworlds.space/<slug>` → KV[`<slug>`], else `https://formingworlds.space`
- `https://timlichtenberg.net/<slug>` (and `www.`) → KV[`tl:<slug>`], else `https://formingworlds.space/team/tim-lichtenberg/`

The Worker branches on `request.url.hostname`, namespaces the KV lookup with a per-domain prefix, and picks a per-domain fallback URL.

## Architecture

- **Worker**: `src/index.js` — reads hostname + slug, looks up `env.LINKS.get(prefix + slug)`, returns 302.
- **KV namespace**: `LINKS`, id `c72549669e824027a45762e9462f2262`. Keys: bare `<slug>` for go.formingworlds.space, `tl:<slug>` for timlichtenberg.net.
- **Custom domains**: `go.formingworlds.space`, `timlichtenberg.net`, `www.timlichtenberg.net` — all declared in `wrangler.toml` `routes`. Cloudflare auto-creates each DNS record and provisions TLS.

## Authentication

`wrangler` reads a Cloudflare API token from `CLOUDFLARE_API_TOKEN`. The token lives at `~/.cloudflare-fw-token` (mode 600, never committed). Every wrangler invocation in this repo should be prefixed:

```bash
CLOUDFLARE_API_TOKEN=$(cat ~/.cloudflare-fw-token | tr -d '\n\r') npx wrangler <command>
```

Required token scope: "Edit Cloudflare Workers" template, **zones**: `formingworlds.space` AND `timlichtenberg.net`. To rotate or expand scope, edit the token at https://dash.cloudflare.com/profile/api-tokens, overwrite the file, revoke the old token.

## Adding a slug

`go.formingworlds.space` slug (bare key):

```bash
cd workers/shortlinks
CLOUDFLARE_API_TOKEN=$(cat ~/.cloudflare-fw-token | tr -d '\n\r') npx wrangler kv key put --binding=LINKS <slug> "<target_url>"
```

`timlichtenberg.net` slug (prefix with `tl:`):

```bash
CLOUDFLARE_API_TOKEN=$(cat ~/.cloudflare-fw-token | tr -d '\n\r') npx wrangler kv key put --binding=LINKS "tl:<slug>" "<target_url>"
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
