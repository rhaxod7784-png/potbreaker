/* Archive of deployed Cloudflare patch v218. Do not deploy without live v217/v216 base.
  GitHub cloudflare/worker.js is a legacy bundle, NOT current production source.
*/
// POTBREAKER_GINKGO_SEO_20261110: preserve scenes; one semantic H1 and visible language navigation.
const __ginkgoFetchPrevious218 = worker_default.fetch;
worker_default.fetch = async function(request, env, ctx) {
  const response = await __ginkgoFetchPrevious218.call(worker_default, request, env, ctx);
  const path = new URL(request.url).pathname;
  if (request.method !== "GET" || response.status !== 200 || !/^\/ginkgo(?:\/(?:en|ja|zh))?$/.test(path) || !response.headers.get("content-type")?.includes("text/html")) return response;
  const originalHtml = await response.text();
  const heading = /<h1 data-i18n="intro_title">([\s\S]*?)<\/h1>/;
  const marker = "</nav></details>";
  if (!heading.test(originalHtml) || !originalHtml.includes(marker)) {
    return new Response(originalHtml, {status:response.status,statusText:response.statusText,headers:response.headers});
  }
  let html = originalHtml.replace(heading, '<h2 data-i18n="intro_title">$1</h2>').replaceAll(".intro-panel h1", ".intro-panel h2");
  const choices = [["/ginkgo","ko","한국어"],["/ginkgo/en","en","English"],["/ginkgo/ja","ja","日本語"],["/ginkgo/zh","zh","中文"]];
  const links = '<div class="pb-ginkgo-language-choices" aria-label="Language / 언어" style="display:flex;flex-wrap:wrap;gap:6px;padding:6px">' +
    choices.map(([href,lang,label]) => '<a href="' + href + '" lang="' + lang + '"' + (href === path ? ' aria-current="page"' : '') + ' style="color:#293b60;background:#fff;padding:4px 7px;border-radius:6px;font:inherit;text-decoration:underline">' + label + '</a>').join("") + '</div>';
  html = html.replace(marker, links + marker);
  const headers = new Headers(response.headers);
  headers.delete("content-length");
  return new Response(html,{status:response.status,statusText:response.statusText,headers});
};

