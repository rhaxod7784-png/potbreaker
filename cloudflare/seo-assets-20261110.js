/* Archive of the exact deployed Cloudflare SEO asset extraction patch (v217).
  IMPORTANT: cloudflare/worker.js remains a prior version; do not redeploy it as production source.
  v217 keeps live game logic and replaces duplicated base64 images in HTML with WebP routes.
*/
// POTBREAKER_SEO_ASSETS_20261110: preserve gameplay; offload duplicated inline WebP data to same-origin immutable files.
const __seoAssetRegex217 = /data:image\/(webp|png|jpeg|gif);base64,([A-Za-z0-9+/=]+)/gi;
let __seoAssetMap217 = null;
let __seoAssetItems217 = null;
function __seoInitAssets217() {
  if (__seoAssetMap217) return;
  const map = new Map(), items = [];
  for (const match of PAGE.matchAll(__seoAssetRegex217)) {
    if (!map.has(match[0])) {
      map.set(match[0], items.length);
      items.push({mime: match[1].toLowerCase(), base64: match[2]});
    }
  }
  __seoAssetMap217 = map;
  __seoAssetItems217 = items;
}
const __seoFetchPrevious217 = worker_default.fetch;
worker_default.fetch = async function(request, env, ctx) {
  const url = new URL(request.url);
  const resource = /^\/_pb_inline\/v217\/([0-9]+)\.(webp|png|jpeg|gif)$/.exec(url.pathname);
  if (resource) {
    __seoInitAssets217();
    const asset = __seoAssetItems217[Number(resource[1])];
    if (!asset || asset.mime !== resource[2]) {
      return new Response("Not Found", {status: 404, headers: {"X-Robots-Tag":"noindex"}});
    }
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method Not Allowed", {status: 405, headers: {"Allow":"GET, HEAD","X-Robots-Tag":"noindex"}});
    }
    const decoded = request.method === "HEAD" ? null : Uint8Array.from(atob(asset.base64), value => value.charCodeAt(0));
    return new Response(decoded, {status: 200, headers: {"Content-Type":"image/" + asset.mime,"Cache-Control":"public, max-age=31536000, immutable","X-Robots-Tag":"noindex","X-Content-Type-Options":"nosniff"}});
  }
  const response = await __seoFetchPrevious217.call(worker_default, request, env, ctx);
  if (request.method !== "GET" || response.status !== 200 || !["/", "/en", "/ja", "/zh"].includes(url.pathname) || !response.headers.get("content-type")?.includes("text/html")) return response;
  __seoInitAssets217();
  const originalHtml = await response.text();
  const rewritten = originalHtml.replace(__seoAssetRegex217, source => {
    const id = __seoAssetMap217.get(source);
    if (id === undefined) return source;
    return "/_pb_inline/v217/" + id + "." + __seoAssetItems217[id].mime;
  });
  const headers = new Headers(response.headers);
  headers.delete("content-length");
  return new Response(rewritten, {status:response.status, statusText:response.statusText, headers});
};

