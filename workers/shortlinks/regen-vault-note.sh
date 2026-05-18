#!/usr/bin/env bash
# Regenerate the Obsidian "Shortlinks.md" note from the live Cloudflare KV.
#
# Usage:
#   ./regen-vault-note.sh                   # writes to $HOME/git/notes/Shortlinks.md
#   VAULT_NOTE=/path/to/Shortlinks.md ./regen-vault-note.sh
#
# Requires: wrangler (npx wrangler), an authenticated session (`wrangler login`
# or CLOUDFLARE_API_TOKEN), and run from this directory.

set -euo pipefail

cd "$(dirname "$0")"

NAMESPACE_ID="c72549669e824027a45762e9462f2262"
VAULT_NOTE="${VAULT_NOTE:-$HOME/git/notes/Shortlinks.md}"
TODAY="$(date +%Y-%m-%d)"

echo "Listing KV keys..." >&2
KEYS=$(npx wrangler kv key list --namespace-id="$NAMESPACE_ID" --remote 2>/dev/null \
       | python3 -c "import json,sys; [print(k['name']) for k in sorted(json.load(sys.stdin), key=lambda x: (':' in x['name'], x['name']))]")

GO_ROWS=""
TL_ROWS=""

while IFS= read -r key; do
  [ -z "$key" ] && continue
  echo "  fetching $key..." >&2
  value=$(npx wrangler kv key get "$key" --namespace-id="$NAMESPACE_ID" --remote 2>/dev/null)
  if [[ "$key" == tl:* ]]; then
    slug="${key#tl:}"
    TL_ROWS+="| \`$slug\` | [go.tl/$slug](https://timlichtenberg.net/$slug) | $value |"$'\n'
  else
    GO_ROWS+="| \`$key\` | [go.fw/$key](https://go.formingworlds.space/$key) | $value |"$'\n'
  fi
done <<< "$KEYS"

mkdir -p "$(dirname "$VAULT_NOTE")"
cat > "$VAULT_NOTE" <<EOF
# Shortlinks

Live targets for the URL shortener Worker (\`workers/shortlinks/\` in the formingworlds-website repo). KV is the source of truth; this note is auto-generated.

Regenerate with \`./regen-vault-note.sh\` in \`workers/shortlinks/\`. To add, change, or delete a slug, see \`workers/shortlinks/README.md\`.

Last regenerated: $TODAY

## go.formingworlds.space

Bare slug keys. Unmatched slugs fall back to https://formingworlds.space.

| Slug | Short URL | Destination |
|---|---|---|
$GO_ROWS

## timlichtenberg.net

Slugs prefixed \`tl:\` in KV. Unmatched slugs fall back to https://formingworlds.space/team/tim-lichtenberg/.

| Slug | Short URL | Destination |
|---|---|---|
$TL_ROWS
EOF

echo "Wrote $VAULT_NOTE" >&2
