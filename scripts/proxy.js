/**
 * 컨트롤러 탭에 설치하는 프록시.
 * 학습창을 iframe으로 넣었을 때 top._getCdnUrl() 이 컨트롤러를 가리켜
 * CDN 경로가 틀어지는 문제를 막는다.
 *
 * 컨트롤러 탭(같은 오리진)에서 실행:
 *   await ctl.evaluate(PROXY_SRC, { cntntsid: 13 });
 */
function installProxy(opts) {
  var sid = (opts && opts.cntntsid) || 12;
  var FALLBACK = 'https://vod.kbrainc.com/kbrain/ktlSafety/prod/' + sid;

  function qw() {
    var lf = document.getElementById('lf');
    return lf ? lf.contentWindow : null;
  }

  window._getCdnUrl = function () {
    try { return qw()._getCdnUrl(); } catch (e) { return FALLBACK; }
  };
  window._getProgressTime = function () {
    try { return qw()._getProgressTime(); } catch (e) { return 0; }
  };
  window._getControlAllowYn = function () {
    try { return qw()._getControlAllowYn(); } catch (e) { return 'Y'; }
  };
  window._getPageCompletion = function () {
    try { return qw()._getPageCompletion(); } catch (e) { return 'N'; }
  };
  window._setPageInfo = function (a) {
    try { return qw()._setPageInfo(a); } catch (e) {}
  };
  window._setProgressTime = function (a, b, c) {
    try { return qw()._setProgressTime(a, b, c); } catch (e) {}
  };
  window._setPageCompletion = function () {
    try { return qw()._setPageCompletion(); } catch (e) {}
  };

  return 'proxy installed (cntntsid ' + sid + ')';
}

installProxy(arguments[0]);
