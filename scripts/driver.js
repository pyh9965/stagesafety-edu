/**
 * 공연안전지원센터 학습창에 넣는 자동 진행 드라이버.
 *
 * 전제: 별도 컨트롤러 탭에 iframe id="lf" 가 있고, 그 안에 lrnwindow.html 이 로드돼 있다.
 *       컨트롤러에는 아래 proxySnippet.js 의 프록시가 먼저 설치돼 있어야 한다.
 *
 * 사용:
 *   const drv = await ctl.evaluate(DRIVER_SRC, { rate: 1.8 });
 *   // 진행 확인
 *   await ctl.evaluate(() => ({ phase: window.__S.phase, pages: window.__S.pages }));
 */
function installDriver(opts) {
  var RATE = (opts && opts.rate) || 1.8;
  var lf = document.getElementById('lf');
  if (!lf) throw new Error('iframe#lf 가 없습니다');
  if (window.__DRV) { try { window.__DRV.stop(); } catch (e) {} }

  var LOG = [];
  var stop = { v: false, timer: null };
  var S = { phase: 'ready', pages: 0, errors: 0, timeouts: 0 };
  window.__S = S;
  window.__LOGLIVE = LOG;
  var curPf = null;

  function lw() { try { return lf.contentWindow; } catch (e) { return null; } }
  function comp() {
    try {
      var w = lw();
      return (w && typeof w._getPageCompletion === 'function') ? w._getPageCompletion() : null;
    } catch (e) { return null; }
  }
  function pfSrc() {
    try {
      var w = lw();
      var pf = w.document.getElementById('playerFrame');
      return pf ? pf.src : null;
    } catch (e) { return null; }
  }
  function vid() {
    try {
      var w = lw();
      var pf = w.document.getElementById('playerFrame');
      if (!pf) return null;
      return pf.contentWindow.document.querySelector('video');
    } catch (e) { return null; }
  }
  function clickNext() {
    try {
      var w = lw();
      var b = w.document.querySelector('.btn-next');
      if (b) { b.click(); return true; }
      return false;
    } catch (e) { return false; }
  }

  function tick() {
    if (stop.v) return;
    var ps = pfSrc();
    if (!ps) return;
    if (ps !== curPf) { curPf = ps; S.phase = 'ready'; }

    if (S.phase === 'ready') {
      var v = vid();
      if (v && v.readyState >= 1 && v.duration > 0) {
        S.phase = 'playing';
        S.playStart = Date.now();
        v.muted = true;
        v.playbackRate = RATE;
        try { v.play().catch(function () {}); } catch (e) {}
      }
      return;
    }

    if (S.phase === 'playing') {
      var v2 = vid();
      if (!v2) return;
      if (comp() === 'Y' || v2.ended) { S.phase = 'advance'; S.advStart = Date.now(); return; }
      if (v2.playbackRate !== RATE) v2.playbackRate = RATE;
      if (!v2.muted) v2.muted = true;
      if (v2.paused) { try { v2.play().catch(function () {}); } catch (e) {} }
      var budget = Math.ceil((v2.duration || 10) / RATE * 1000) + 120000;
      if (Date.now() - S.playStart > budget) {
        S.phase = 'advance';
        S.advStart = Date.now();
        S.timeouts++;
        LOG.push({ pf: ps.split('/resources/')[1], why: 'timeout', t: Math.round(v2.currentTime || 0) });
      }
      return;
    }

    if (S.phase === 'advance') {
      if (Date.now() - S.advStart < 1500) return;
      var ok = clickNext();
      S.pages++;
      if (!ok) S.errors++;
      LOG.push({ n: S.pages, from: ps.split('/resources/')[1], ok: ok });
      window.__LOGLIVE = LOG;
      S.phase = 'loading';
      setTimeout(function () { if (!stop.v && S.phase === 'loading') S.phase = 'ready'; }, 4000);
    }
  }

  window.__DRV = { stop: function () { stop.v = true; if (stop.timer) clearInterval(stop.timer); } };
  stop.timer = setInterval(tick, 700);
  return 'driver installed (rate ' + RATE + ')';
}

installDriver(arguments[0]);
