"""Build four crawlable, self-contained game guide pages for the Worker."""
from html import escape
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'web' / 'site-guides'))
from content import CONTENT  # noqa: E402

STYLE = """
:root{font-family:system-ui,'Malgun Gothic',sans-serif;color:#29365c;background:#d9efff}
*{box-sizing:border-box}body{margin:0;line-height:1.65;background:linear-gradient(145deg,#d3edff,#fff8e7 60%,#e5f4ff)}
a{color:#27518d}a:focus-visible,summary:focus-visible{outline:3px solid #cb7930;outline-offset:3px}
.top{display:flex;flex-wrap:wrap;align-items:center;gap:12px;justify-content:space-between;padding:12px clamp(12px,4vw,40px);background:#fffaf0;border-bottom:3px solid #405879}
.brand{font-weight:950;text-decoration:none;color:#243b65;letter-spacing:.04em}.top nav,.languages{display:flex;flex-wrap:wrap;gap:8px}.top nav a,.languages a{padding:5px 10px;border-radius:10px;background:#e8f3ff;text-decoration:none;font-size:.9rem;font-weight:800}.languages a[aria-current]{background:#ffd875}
main{max-width:1020px;margin:auto;padding:24px clamp(14px,4vw,32px) 60px}.intro{padding:clamp(20px,5vw,42px);border:3px solid #405b8b;border-radius:22px;background:#fffaf0;box-shadow:0 7px 0 #8a9fbd}.eyebrow{font-size:.8rem;font-weight:950;letter-spacing:.16em;color:#a34d4f}
h1{font-size:clamp(2rem,5vw,3.2rem);line-height:1.15;margin:.1em 0 .35em}h2{font-size:clamp(1.5rem,3vw,2rem);line-height:1.25;margin:0}h3{margin:1.2em 0 .35em;font-size:1.12rem}p{margin:.5em 0 1em}.intro p:last-child{font-size:1.1rem;max-width:760px}
.jump{display:flex;flex-wrap:wrap;gap:9px;margin:22px 0}.jump a{padding:9px 15px;background:#fff;border:2px solid #5476aa;border-radius:99px;text-decoration:none;font-weight:850}
.guide{scroll-margin-top:18px;margin:22px 0;padding:clamp(18px,4vw,32px);background:#fffdf8;border:2px solid #8da8cd;border-radius:20px;box-shadow:0 5px 0 #9db5d455}.section-head{display:flex;align-items:center;gap:14px;padding-bottom:12px;border-bottom:2px solid #d9e4f1}.section-head p{margin:.3em 0 0;color:#435477}.num{display:grid;place-items:center;flex:none;width:44px;height:44px;border-radius:12px;background:#ffdb7b;border:2px solid #415482;font-weight:950}
.two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.two>div{padding:2px 15px;border-radius:13px;background:#f0f6ff}.two h3{margin-top:.6em}ol,ul{padding-left:1.4em}li{margin:.38em 0}.note{padding:11px 14px;border-left:5px solid #d9a857;background:#fff2d3}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:540px}th,td{padding:10px 12px;border:1px solid #afc3da;text-align:left;vertical-align:top}thead{background:#dcecff}tbody th{background:#f2f7ff;white-space:nowrap}.play{display:inline-block;margin-top:10px;padding:11px 17px;border:2px solid #4b5d83;border-radius:13px;background:#ffd879;box-shadow:0 3px 0 #8295b2;color:#213456;text-decoration:none;font-weight:950}
details{padding:10px 0;border-bottom:1px solid #d4dfec}summary{cursor:pointer;font-weight:850}details p{padding-left:14px}footer{padding:22px;text-align:center;background:#c4e4fa;color:#31466e}
@media(max-width:700px){.two{grid-template-columns:1fr}.top{align-items:flex-start}.top nav{width:100%}.top nav a{padding:4px 8px}.guide{padding:17px}.section-head{align-items:flex-start}}
"""

pages = {}
for lang, copy in CONTENT.items():
    path = '/about' if lang == 'ko' else f'/{lang}/about'
    privacy = '/privacy' if lang == 'ko' else f'/{lang}/privacy'
    game = '/' if lang == 'ko' else f'/{lang}'
    nav_game, nav_guide, nav_privacy = copy['nav']
    alternates = ''.join(
        f'<link rel="alternate" hreflang="{other}" href="https://potbreaker.com{("/about" if other == "ko" else f"/{other}/about")}">'
        for other in ('ko', 'en', 'ja', 'zh')
    )
    languages = ' '.join(
        f'<a href="{("/about" if other == "ko" else f"/{other}/about")}"'
        + (' aria-current="page"' if other == lang else '')
        + f' lang="{other}">{label}</a>'
        for other, label in [('ko', '한국어'), ('en', 'English'), ('ja', '日本語'), ('zh', '中文')]
    )
    html = f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{escape(copy['description'], quote=True)}"><link rel="canonical" href="https://potbreaker.com{path}">{alternates}<title>{escape(copy['title'])} | CBZP POT BREAKER</title><style>{STYLE}</style></head><body><div class="top"><a class="brand" href="{game}">♟ CBZP · POT BREAKER</a><nav aria-label="Site"><a href="{game}">{escape(nav_game)}</a><a href="{path}" aria-current="page">{escape(nav_guide)}</a><a href="{privacy}">{escape(nav_privacy)}</a></nav><div class="languages" aria-label="Languages">{languages}</div></div><main>{copy['body']}</main><footer>CBZP · POT BREAKER · <a href="{privacy}">{escape(nav_privacy)}</a></footer></body></html>'''
    out = ROOT / 'web' / 'site-guides' / f'about-{lang}.html'
    out.write_text(html, encoding='utf-8')
    pages[lang] = html
    print(f'{out.relative_to(ROOT)}: {len(html):,} characters')

patch = '''// PB_AD_QUALITY_20261112
const PB_GUIDES=''' + json.dumps(pages, ensure_ascii=False) + ''';
for(const [lang,html] of Object.entries(PB_GUIDES)) INFO_PAGES[lang].about=html;
const __pbGuideFetch=worker_default.fetch;
worker_default.fetch=async function(request,env,ctx){
  const response=await __pbGuideFetch(request,env,ctx);
  const path=new URL(request.url).pathname;
  if(request.method!=="GET"||response.status!==200||!(["/sitemap.xml","/sitemap.txt"].includes(path)))return response;
  let body=await response.text();
  if(path==="/sitemap.xml"&&!body.includes("<loc>https://potbreaker.com/floor</loc>"))body=body.replace("</urlset>","<url><loc>https://potbreaker.com/floor</loc></url></urlset>");
  if(path==="/sitemap.txt"&&!body.includes("https://potbreaker.com/floor"))body+="https://potbreaker.com/floor\\n";
  const headers=new Headers(response.headers);headers.delete("content-length");headers.delete("etag");
  return new Response(body,{status:response.status,statusText:response.statusText,headers});
};
'''
patch_out = ROOT / 'web' / 'site-guides' / 'worker-patch.js'
patch_out.write_text(patch, encoding='utf-8')
print(f'{patch_out.relative_to(ROOT)}: {len(patch):,} characters')
