// Multi-domain redirect Worker.
// - `go.formingworlds.space/<slug>`  -> KV[<slug>], else https://formingworlds.space
// - `timlichtenberg.net/<slug>`      -> KV["tl:" + <slug>], else profile page
// - `www.timlichtenberg.net/<slug>`  -> same as apex
// Unknown host -> formingworlds.space (defensive default).

const DOMAINS = {
  "go.formingworlds.space": {
    fallback: "https://formingworlds.space",
    prefix: "",
  },
  "timlichtenberg.net": {
    fallback: "https://formingworlds.space/team/tim-lichtenberg/",
    prefix: "tl:",
  },
  "www.timlichtenberg.net": {
    fallback: "https://formingworlds.space/team/tim-lichtenberg/",
    prefix: "tl:",
  },
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const config = DOMAINS[url.hostname.toLowerCase()];

    if (!config) {
      return Response.redirect("https://formingworlds.space", 302);
    }

    const slug = url.pathname.slice(1).replace(/\/+$/, "").toLowerCase();

    if (!slug) {
      return Response.redirect(config.fallback, 302);
    }

    const target = await env.LINKS.get(config.prefix + slug);

    if (!target) {
      return Response.redirect(config.fallback, 302);
    }

    return Response.redirect(target, 302);
  },
};
