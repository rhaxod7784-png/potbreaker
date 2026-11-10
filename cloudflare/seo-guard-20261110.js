/* Deployed runtime patch for potbreaker v216 (2026-11-10).
   This is a copy of the guard appended to the live Cloudflare Worker.
   The repository cloudflare/worker.js still contains the legacy v184 bundle;
   do NOT deploy it over production until the full live bundle is synced.
*/
// POTBREAKER_SEO_GUARD_20261110: indexable HTML unchanged; internal resources stay functional.
const __seoFetchOriginal20261110 = worker_default.fetch;
worker_default.fetch = async function(request, env, ctx) {
  const requestUrl = new URL(request.url);
  const path = requestUrl.pathname;
  if (request.method === "GET" || request.method === "HEAD") {
    let normalized = null;
    if (path === "/index.html") normalized = "/";
    else if (/^\/(?:en|ja|zh)\/$/.test(path) || /^\/ginkgo(?:\/(?:en|ja|zh))?\/$/.test(path)) normalized = path.slice(0, -1);
    if (normalized !== null) {
      return Response.redirect("https://potbreaker.com" + normalized + requestUrl.search, 308);
    }
  }
  const response = await __seoFetchOriginal20261110.call(worker_default, request, env, ctx);
  if (path.startsWith("/api/") || path === "/game.py" || path === "/ginkgo/game.py" || path === "/floor" || path === "/floor/") {
    const headers = new Headers(response.headers);
    headers.set("X-Robots-Tag", "noindex");
    return new Response(response.body, {status:response.status, statusText:response.statusText, headers});
  }
  return response;
};

