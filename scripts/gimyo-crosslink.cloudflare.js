// Run through Cloudflare execute after setting WRITE to true. This patches the
// currently deployed Worker bundle, since repository main predates production.
async () => {
  const WRITE = false;
  const expectedVersion = 'd9ae9d96-4818-49b1-8666-8ea4815dd9f7'; // production v207
  const path = `/accounts/${accountId}/workers/scripts/potbreaker`;
  const deployments = await cloudflare.request({ method: 'GET', path: `${path}/deployments` });
  const current = deployments.result?.deployments?.[0]?.versions;
  if (current?.length !== 1 || current[0].version_id !== expectedVersion || current[0].percentage !== 100) {
    throw new Error('Production Worker changed; review the new version before patching.');
  }

  const multipart = await cloudflare.request({ method: 'GET', path: `${path}/content/v2` });
  const delimiter = multipart.slice(0, multipart.indexOf('\r\n'));
  const begin = multipart.indexOf('\r\n\r\n') + 4;
  const end = multipart.lastIndexOf(`\r\n${delimiter}--`);
  if (!delimiter.startsWith('--') || begin < 4 || end < begin || !multipart.includes('name="worker.js"')) {
    throw new Error('Unexpected Worker source format.');
  }
  let source = multipart.slice(begin, end);
  if (source.includes('gimyo-crosslink-20261107')) throw new Error('Cross-link already present.');

  const homeLink = '<a href="https://djgimyo.com/home.html" target="_blank" rel="noopener noreferrer" aria-label="대전의 기묘한 여행, 새 창"><span class="info-ko">🐈 기묘의 대전 여행</span><span class="info-en">🐈 Gimyo in Daejeon</span><span class="info-zh">🐈 奇妙的大田旅行</span><span class="info-ja">🐈 キミョの大田旅</span></a>';
  const titleNav = source.lastIndexOf('<nav class="site-info-links"');
  const titleNavEnd = source.indexOf('</nav>', titleNav);
  if (titleNav < 0 || titleNavEnd < 0 || !source.slice(titleNav, titleNavEnd).includes('href="/about"')) {
    throw new Error('POT BREAKER title navigation not found.');
  }
  source = source.slice(0, titleNavEnd) + homeLink + source.slice(titleNavEnd);

  const endSection = source.indexOf('<section class="screen end hidden" id="end">', titleNavEnd);
  const endActions = source.indexOf('<div class="end-btns">', endSection);
  const endActionsClose = source.indexOf('</div>', endActions);
  if (endSection < 0 || endActions < 0 || endActionsClose < 0 ||
      !source.slice(endActions, endActionsClose).includes('id="registerScore"')) {
    throw new Error('POT BREAKER result controls not found.');
  }
  const resultLink = '<p class="gimyo-travel-note"><a href="https://djgimyo.com/home.html" target="_blank" rel="noopener noreferrer" aria-label="대전의 기묘한 여행, 새 창"><span class="travel-ko">사무실 밖 기묘 만나기 ↗</span><span class="travel-en">Meet Gimyo outside the office ↗</span><span class="travel-zh">去见办公室外的奇妙 ↗</span><span class="travel-ja">オフィスの外のキミョに会う ↗</span></a></p>';
  const afterActions = endActionsClose + '</div>'.length;
  source = source.slice(0, afterActions) + resultLink + source.slice(afterActions);

  const css = '\n/* gimyo-crosslink-20261107 */\n.gimyo-travel-note{margin:10px 0 0!important;text-align:center}.gimyo-travel-note a{display:inline-flex;align-items:center;justify-content:center;min-height:36px;padding:5px 14px;border:1px solid #fff;border-radius:999px;background:#fffdf0e8;color:#35456d;font-size:clamp(11px,1.15cqw,15px);font-weight:900;text-decoration:none}.gimyo-travel-note a:hover,.site-info-links a:hover{background:#ffe8bb}.gimyo-travel-note [class^="travel-"]{display:none}html[lang="ko"] .gimyo-travel-note .travel-ko,html[lang="en"] .gimyo-travel-note .travel-en,html[lang="zh"] .gimyo-travel-note .travel-zh,html[lang="ja"] .gimyo-travel-note .travel-ja{display:inline}\n';
  const styleClose = source.lastIndexOf('</style>', titleNav);
  if (styleClose < 0 || titleNav - styleClose > 800000) throw new Error('POT BREAKER stylesheet not found.');
  source = source.slice(0, styleClose) + css + source.slice(styleClose);

  const report = {
    baseVersion: expectedVersion,
    sourceBytes: source.length,
    titleLinks: source.split('https://djgimyo.com/home.html').length - 1,
    markerCount: source.split('gimyo-crosslink-20261107').length - 1,
    resultLinkPresent: source.includes('사무실 밖 기묘 만나기'),
  };
  if (report.titleLinks !== 2 || report.markerCount !== 1 || !report.resultLinkPresent) {
    throw new Error(`Patch verification failed: ${JSON.stringify(report)}`);
  }
  if (!WRITE) return { dryRun: true, ...report };

  const form = new FormData();
  form.append('metadata', new Blob([JSON.stringify({
    main_module: 'worker.js',
    compatibility_date: '2026-10-27',
    bindings: [{ type: 'd1', name: 'POTBREAKER_DB', database_id: 'bfc89eda-b76b-44f0-9653-bbda3b7c6806' }],
    annotations: { 'workers/message': 'Link Gimyo travel and POT BREAKER without changing game logic' },
  })], { type: 'application/json' }));
  form.append('worker.js', new Blob([source], { type: 'application/javascript+module' }), 'worker.js');
  const uploaded = await cloudflare.request({ method: 'POST', path: `${path}/versions`, body: form });
  return { dryRun: false, ...report, uploadedVersion: uploaded.result?.id, upload: uploaded.result };
}
