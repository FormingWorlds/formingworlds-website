# fw-shortlinks

Cloudflare Worker that serves 302 redirects on several custom domains:

- `https://go.formingworlds.space/<slug>` → KV[`<slug>`], else `https://formingworlds.space`
- `https://timlichtenberg.net/<slug>` (and `www.`) → KV[`tl:<slug>`], else `https://formingworlds.space/team/tim-lichtenberg/`
- `https://go.interra-project.org/<slug>` → KV[`ip:<slug>`], else `https://interra-project.org`

The Worker branches on `request.url.hostname`, namespaces the KV lookup with a per-domain prefix, and picks a per-domain fallback URL.

## Architecture

- **Worker**: `src/index.js` — reads hostname + slug, looks up `env.LINKS.get(prefix + slug)`, returns 302.
- **KV namespace**: `LINKS`, id `c72549669e824027a45762e9462f2262`. Keys: bare `<slug>` for go.formingworlds.space, `tl:<slug>` for timlichtenberg.net, `ip:<slug>` for go.interra-project.org.
- **Custom domains**: `go.formingworlds.space`, `timlichtenberg.net`, `www.timlichtenberg.net`, `go.interra-project.org` — all declared in `wrangler.toml` `routes`. Cloudflare auto-creates each DNS record and provisions TLS. The interra apex and `www` stay on GitHub Pages; only the `go.` subdomain is bound to this Worker.

## Authentication

The recommended path is the interactive OAuth flow:

```bash
npx wrangler login
```

This opens a browser, authenticates against the Cloudflare account, and caches the session in `~/.config/.wrangler/` on this Mac. Every subsequent `wrangler` invocation from this machine picks it up automatically, no env vars needed. Re-run `wrangler login` after switching machines or if the session expires.

If you prefer a non-interactive token (useful for CI or for a machine without browser access), set `CLOUDFLARE_API_TOKEN`:

```bash
CLOUDFLARE_API_TOKEN=<token> npx wrangler <command>
```

Required token scope: "Edit Cloudflare Workers" template, **zones**: `formingworlds.space`, `timlichtenberg.net`, AND `interra-project.org` (or simply "All zones from an account" for the account that owns all three). The zone resources must cover every domain the Worker binds, because attaching a custom domain is a per-zone `Workers Routes:Edit` operation; a token missing a zone deploys the script but fails to register that zone's route. Tokens are managed at https://dash.cloudflare.com/profile/api-tokens.

> Wrangler 4 defaults to **local** KV for `kv key list` / `kv key get` / `kv key put`. Always pass `--remote` to act on the deployed namespace.

## Adding a slug

`go.formingworlds.space` slug (bare key):

```bash
cd workers/shortlinks
npx wrangler kv key put --binding=LINKS --remote <slug> "<target_url>"
```

`timlichtenberg.net` slug (prefix with `tl:`):

```bash
npx wrangler kv key put --binding=LINKS --remote "tl:<slug>" "<target_url>"
```

`go.interra-project.org` slug (prefix with `ip:`):

```bash
npx wrangler kv key put --binding=LINKS --remote "ip:<slug>" "<target_url>"
```

KV is eventually consistent globally; new keys are live within ~60s.

After any add/update/delete, regenerate the Obsidian reference note:

```bash
./regen-vault-note.sh
```

## Updating a slug

Same command as adding. The key is overwritten.

## Deleting a slug

```bash
npx wrangler kv key delete --binding=LINKS --remote <slug>
```

## Listing all slugs

```bash
npx wrangler kv key list --binding=LINKS --remote
```

## Deploying code changes

If `src/index.js` or `wrangler.toml` changes:

```bash
npx wrangler deploy
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
- **`Unauthenticated` error from wrangler**: cached OAuth session expired (run `wrangler login` again), or the `CLOUDFLARE_API_TOKEN` env var is unset/invalid.
- **`kv key list` returns `[]` despite live slugs**: missing `--remote` flag. Wrangler 4 reads local KV by default.
