/* POTBREAKER_MOBILE_UI_20261116
 * Small forward-only overlay for the live Worker.
 * Keep the current deployed game bundle and D1 bindings; never use legacy worker.js.
 */
(() => {
  const mark = "pb-mobile-ui-20261116";
  const controlsPath = "/modules/potbreaker/controls.css";
  const originalControls = BROWSER_MODULES[controlsPath];
  if (typeof originalControls !== "string" ||
      !originalControls.includes("#gamePanel .dpad,#gamePanel .actions{display:none!important}")) {
    throw new Error("[mobile-ui] unexpected Pot Breaker control module: refusing partial patch");
  }

  const touchRules = [
    "/* Pot Breaker touch-only UI: the desktop keyboard layout remains untouched. */",
    "@media (pointer:coarse), (hover:none) and (max-width:1100px) {",
    "  #gamePanel .dpad { display:grid!important; width:clamp(252px,32cqw,328px)!important; height:clamp(252px,32cqw,328px)!important; }",
    "  #gamePanel .actions { display:flex!important; }",
    "}",
    "html.pb-mobile-ui #gamePanel .dpad { display:grid!important; width:clamp(252px,32cqw,328px)!important; height:clamp(252px,32cqw,328px)!important; }",
    "html.pb-mobile-ui #gamePanel .actions { display:flex!important; }"
  ].join("\n");
  BROWSER_MODULES[controlsPath] = originalControls + "\n" + touchRules;

  const topNavigationRules = [
    "/* Hide only the shared game switcher on mobile; keep locale, gameplay and footer independent. */",
    "@media (pointer:coarse), (hover:none) and (max-width:1100px) {",
    "  :root { --pb-tabs-height:0px!important; }",
    "  #pb-theme-tabs { display:none!important; height:0!important; }",
    "}",
    "html.pb-mobile-ui { --pb-tabs-height:0px!important; }",
    "html.pb-mobile-ui #pb-theme-tabs { display:none!important; height:0!important; }",
    touchRules
  ].join("\n");
  const deviceMarker = '<script id="pb-mobile-detection-20261116">(function(){try{var ua=navigator.userAgent||"";var mobile=/Android|iPhone|iPad|iPod|Mobile|Silk/i.test(ua)||(navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1);if(mobile||window.matchMedia("(pointer:coarse)").matches)document.documentElement.classList.add("pb-mobile-ui")}catch(_){}})();</script>';
  const headOverlay = '<style id="' + mark + '">' + topNavigationRules + '</style>' + deviceMarker;

  const pageRoutes = new Set([
    "/", "/en", "/ja", "/zh",
    "/ginkgo", "/ginkgo/en", "/ginkgo/ja", "/ginkgo/zh",
    "/floor"
  ]);
  const previousFetch = worker_default.fetch;
  worker_default.fetch = async function(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";
    const isPage = request.method === "GET" && pageRoutes.has(path);
    const isControls = request.method === "GET" && path === controlsPath;
    const response = await previousFetch.call(worker_default, request, env, ctx);
    if (response.status !== 200) return response;
    if (isControls) {
      const headers = new Headers(response.headers);
      headers.set("cache-control", "no-store, max-age=0");
      return new Response(response.body, {
        status: response.status, statusText: response.statusText, headers
      });
    }
    if (!isPage || !response.headers.get("content-type")?.includes("text/html")) return response;
    let html = await response.text();
    if (!html.includes('id="pb-theme-tabs"') || !html.includes("</head>")) {
      return new Response(html, {
        status: response.status, statusText: response.statusText, headers: response.headers
      });
    }
    if (!html.includes('id="' + mark + '"')) {
      html = html.replace("</head>", headOverlay + "</head>");
      // Bust the old mobile CSS cache for the first theme.
      html = html.replace(
        "/modules/potbreaker/controls.css?v=1.0.92",
        "/modules/potbreaker/controls.css?v=1.0.93-mobile-ui"
      );
    }
    const headers = new Headers(response.headers);
    headers.delete("content-length");
    headers.delete("etag");
    headers.set("cache-control", "no-store, max-age=0");
    return new Response(html, {
      status: response.status, statusText: response.statusText, headers
    });
  };
})();