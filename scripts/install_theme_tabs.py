"""Install the shared three-game tab bar in the deployed Worker bundle.

The Worker already serves several independently embedded HTML pages. This
response wrapper applies one shared tab template to Theme 1 and Theme 2;
Floor Breaker bundles that same template in its own standalone page.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MARKER = '// PB_THEME_TABS_20261110'


def wrapper() -> str:
    css = (ROOT / 'web/theme-tabs.css').read_text(encoding='utf-8')
    controls_css = (ROOT / 'web/pot-touch-controls.css').read_text(encoding='utf-8')
    html = (ROOT / 'web/theme-tabs.html').read_text(encoding='utf-8')
    return (MARKER + '\n'
            + 'const PB_THEME_CSS=' + json.dumps(css, ensure_ascii=False) + ';\n'
            + 'const PB_TOUCH_CSS=' + json.dumps(controls_css, ensure_ascii=False) + ';\n'
            + 'const PB_THEME_HTML=' + json.dumps(html, ensure_ascii=False) + ';\n'
            + r'''const __pbThemeFetch=worker_default.fetch;
worker_default.fetch=async function(request,env,ctx){
  const response=await __pbThemeFetch(request,env,ctx);
  const path=new URL(request.url).pathname;
  const isPot=/^\/(?:index\.html|en|ja|zh)?\/?$/.test(path);
  const isGinkgo=/^\/ginkgo(?:\/(?:en|ja|zh))?\/?$/.test(path);
  if(request.method!=="GET"||response.status!==200||(!isPot&&!isGinkgo)||!(response.headers.get("content-type")||"").includes("text/html"))return response;
  let page=await response.text();
  const current=isPot?"pot":"ginkgo";
  const tabs=PB_THEME_HTML.replace("{{ACTIVE_POT}}",current==="pot"?'aria-current="page"':"").replace("{{ACTIVE_GINKGO}}",current==="ginkgo"?'aria-current="page"':"").replace("{{ACTIVE_FLOOR}}","");
  page=page.replace(/<details id="pb-game-mode">[\s\S]*?<\/details>/,"");
  page=page.replace("<body>","<body>"+tabs);
  page=page.replace("</head>","<style>"+PB_THEME_CSS+(isPot?PB_TOUCH_CSS:"")+"</style></head>");
  const headers=new Headers(response.headers);headers.delete("content-length");headers.delete("etag");
  return new Response(page,{status:response.status,statusText:response.statusText,headers});
};
''' )


def install(source: str) -> str:
    if MARKER in source:
        raise ValueError('Theme tab wrapper already installed')
    anchor = '\nexport {\n'
    if source.count(anchor) != 1:
        raise ValueError('Expected one final Worker export')
    return source.replace(anchor, '\n' + wrapper() + anchor, 1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: install_theme_tabs.py input-worker.js output-worker.js')
    source = Path(sys.argv[1]).read_text(encoding='utf-8')
    Path(sys.argv[2]).write_text(install(source), encoding='utf-8')
