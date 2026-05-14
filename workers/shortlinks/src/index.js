const FALLBACK_URL = "https://formingworlds.space";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const slug = url.pathname.slice(1).replace(/\/+$/, "").toLowerCase();

    if (!slug) {
      return Response.redirect(FALLBACK_URL, 302);
    }

    const target = await env.LINKS.get(slug);

    if (!target) {
      return Response.redirect(FALLBACK_URL, 302);
    }

    return Response.redirect(target, 302);
  },
};
