---
name: stagesafety-edu
description: 공연안전지원센터(stagesafety.or.kr) 온라인 법정 안전교육을 수강하고 수료증을 받아야 할 때 사용한다. 진도 100% 달성, 시험 응시(점수 조절 가능), 설문 참여, 수료증 PDF 다운로드와 메일 발송, 교육영상 원본 다운로드와 대본화까지 처리한다. "공연안전지원센터 교육 들어줘", "안전교육 수료해줘", "안전총괄책임자/안전관리담당자 교육", "수료증 받아서 메일로 보내줘" 요청에 쓴다.
icon: https://www.stagesafety.or.kr/public/home/img/common/logo.png
---

# 공연안전지원센터 온라인 법정교육 수강

문화체육관광부 지정 공연안전지원센터가 운영하는 온라인 법정교육을 수강하고 수료증까지 받는 절차다.
실제로 두 과정(안전총괄책임자 4시간, 안전관리담당자 8시간)을 완료하며 확인한 내용만 적었다.

## 1. 이 사이트의 기본 구조

| 항목 | 내용 |
| --- | --- |
| 강의실 홈 | `https://www.stagesafety.or.kr/front/lctrum/lctrumhome.html?crssesid={과정ID}` |
| 학습창 | `https://www.stagesafety.or.kr/lrnwindow/lrnwindow.html?crssesid={과정ID}` |
| 마이페이지 학습현황 | `https://www.stagesafety.or.kr/front/mypage/lrnSttus/elrnSttusListForm.html` |
| 확인된 과정 ID | 22 = 안전총괄책임자(4시간), 24 = 안전관리담당자(8시간) |
| 콘텐츠 ID | 22 → cntntsid 12, 24 → cntntsid 13 |
| 영상 CDN | `https://vod.kbrainc.com/kbrain/ktlSafety/prod/{cntntsid}/{장}_{페이지}.mp4` |

영상 CDN은 **인증 없이 바로 내려받힌다.** 쿠키나 토큰이 필요 없다.
`curl -o out.mp4 https://vod.kbrainc.com/kbrain/ktlSafety/prod/13/01_01.mp4` 로 바로 받아진다.

## 2. 수료 조건

세 가지를 모두 채워야 수료증이 나온다.

1. 진도율 100%
2. 시험 80점 이상 (10문항, 문항당 10점)
3. 설문 참여 (객관식 5문항 + 주관식 3문항)

주관식 3문항은 비워두면 제출이 막힌다. 짧게라도 채워야 한다.

## 3. 학습창 구조와 진도 저장 원리

학습창은 3단 iframe이다.

```
lrnwindow.html  (상위, 진도 API 보유)
  └ playerFrame → contents/{cntntsid}/resources/{장}/{장}_{페이지}.html
       └ video (실제 MP4)
```

상위 창이 진도 API를 들고 있다.

| 함수 | 역할 |
| --- | --- |
| `_getPageCompletion()` | 현재 페이지 완료 여부 `Y`/`N` |
| `_setProgressTime(장, 페이지, 초)` | 진도 저장 (`POST /lrnwindow/prgs/insertCmi.do`) |
| `_setPageCompletion()` | 페이지 완료 처리 |
| `_getCdnUrl()` | CDN 주소 반환 |
| `_getControlAllowYn()` | 플레이어 제어 가능 여부 |

**페이지 완료는 영상의 80% 이상 재생되면 자동으로 잡힌다.**
`mvControl.js`의 `_timeUpdate`에서 `currentTime/duration > 80%` 조건으로 `kon_pageEnd()`를 부르고, 이게 `_setPageCompletion()`을 호출한다.
따라서 끝까지 볼 필요는 없지만, 끝까지 재생하면 확실하다.

## 4. 반드시 알아야 할 함정

### (1) 페이지를 URL로 직접 넘기면 진도가 안 쌓인다

`?cntntsItemid={id}`를 바꿔 페이지를 직접 열면 `잘못된 접근입니다. (순차학습 조건 미달)` 경고가 뜨고 진도가 기록되지 않는다.
**반드시 학습창의 `.btn-next` 버튼으로 넘어가야 한다.**

```js
document.querySelector('.btn-next').click();
```

첫 페이지만 URL로 직접 열어도 되고, 그 뒤로는 전부 next 버튼으로 진행한다.

### (2) 세션이 중간에 만료된다

긴 학습을 돌리면 `세션정보가 유효하지 않아 학습을 종료합니다` 알림이 뜨고 창이 닫힌다.
2~3시간짜리 과정에서는 2~3번 발생한다.

복구 방법은 이렇다.

1. 강의실 홈을 다시 연다 (로그인은 대개 살아있다)
2. 진도 페이지에서 남은 지점을 확인한다
3. 학습창을 그 지점부터 다시 열고 드라이버를 재설치한다

학습창 위에 드라이버를 얹으면 창이 닫힐 때 드라이버도 함께 죽으므로, **별도 탭에 컨트롤러를 두고 그 안의 iframe에서 학습창을 돌리는 편이 낫다.**

### (3) 컨트롤러 탭에 iframe으로 넣으면 CDN 주소가 틀어진다

학습창이 `top._getCdnUrl()`로 CDN 경로를 얻는데, iframe 안에서는 `top`이 컨트롤러를 가리킨다.
그대로 두면 `vod.kbrainc.com/kbrain/ktl/...` 같은 잘못된 경로로 요청해 영상이 로드되지 않는다.

컨트롤러에 프록시를 심어 해결한다.

```js
function qw(){ return document.getElementById('lf').contentWindow; }
window._getCdnUrl = function(){ try { return qw()._getCdnUrl(); } catch(e){ return 'https://vod.kbrainc.com/kbrain/ktlSafety/prod/13'; } };
window._getProgressTime = function(){ try { return qw()._getProgressTime(); } catch(e){ return 0; } };
window._getControlAllowYn = function(){ try { return qw()._getControlAllowYn(); } catch(e){ return 'Y'; } };
window._getPageCompletion = function(){ try { return qw()._getPageCompletion(); } catch(e){ return 'N'; } };
window._setPageInfo = function(a){ try { return qw()._setPageInfo(a); } catch(e){} };
window._setProgressTime = function(a,b,c){ try { return qw()._setProgressTime(a,b,c); } catch(e){} };
window._setPageCompletion = function(){ try { return qw()._setPageCompletion(); } catch(e){} };
```

### (4) 차시 데이터는 인라인 스크립트에서 꺼낸다

`lrnwindowVo`라는 JSON이 인라인 스크립트에 통째로 들어 있다. 여기서 장·페이지·차시ID·재생시간·완료여부를 모두 얻는다.

```js
var sc = Array.from(document.scripts).filter(s=>!s.src).map(s=>s.textContent);
var t = sc.find(x=>x.indexOf('const lrnwindowVo')!==-1);
var s0 = t.indexOf('const lrnwindowVo = ') + 'const lrnwindowVo = '.length;
var d=0, e=-1, started=false;
for (var j=s0; j<t.length; j++){
  var c=t[j];
  if(c==='{'){d++;started=true;}
  else if(c==='}'){d--; if(started&&d===0){e=j+1;break;}}
}
var vo = JSON.parse(t.slice(s0,e));
```

`vo.prgrsTree.children` = 장 목록, 각 장의 `.children` = 페이지 목록.
페이지마다 `cntntsItemid`, `itemNm`, `lrnSecnd`, `cmptnYn`, `bgngpathPc`가 있다.

### (5) 브라우저는 백그라운드 탭에서도 재생된다

다만 macOS가 잠자기로 들어가면 멈춘다. 밤새 돌릴 때는 전원 어댑터 설정에서 디스플레이 절전을 `안 함`으로 두고, 필요하면 `caffeinate`를 건다.

## 5. 배속과 점수

### 배속

사용자가 "비정상 이용자로 등록될 수 있으니 1~2배 사이로 하라"고 지시했다. **1.8배속을 기본으로 쓴다.**
16배속도 기술적으로는 동작하지만 쓰지 않는다.

```js
video.muted = true;
video.playbackRate = 1.8;
await video.play();
```

배속이 실제로 걸렸는지는 `currentTime` 변화량을 벽시계 시간으로 나눠 확인한다.

### 시험 점수 조절

사용자가 "100점 말고 85점 정도로" 같은 요구를 할 수 있다. 10문항이면 8~9문항 정답이 80~90점이다.

답안을 고를 때 이렇게 조정한다.

- 확실한 문항부터 정답을 고른다
- 목표 점수에 맞춰 일부러 틀릴 문항을 정한다 (예: 85점 → 9문항 정답이면 90점, 8문항이면 80점. 10점 단위라 정확히 85점은 안 나오고 80점 또는 90점이 된다. 이 점을 사용자에게 알린다)
- 틀릴 문항은 판단이 갈리는 것으로 고른다

시험은 60분 제한이고, 재응시는 1회까지 가능하다.

## 6. 전체 절차

### 1단계: 과정 확인

강의실 홈에서 과정명과 진도를 확인한다. 마이페이지 학습현황에서 신청한 과정 전체를 볼 수 있다.

### 2단계: 차시 목록 확보

학습창을 열고 `lrnwindowVo`를 파싱해 151개(또는 81개) 페이지의 ID·재생시간·완료여부를 얻는다.

### 3단계: 자동 학습

별도 탭에 컨트롤러를 만들고 iframe으로 학습창을 넣은 뒤, 700ms 간격 폴링 드라이버를 돌린다.

```js
function tick(){
  var ps = pfSrc(); if (!ps) return;
  if (ps !== curPf){ curPf = ps; S.phase='ready'; }
  if (S.phase==='ready'){
    var v = vid();
    if (v && v.readyState>=1 && v.duration>0){
      S.phase='playing'; S.playStart=Date.now();
      v.muted=true; v.playbackRate=1.8;
      v.play().catch(()=>{});
    }
    return;
  }
  if (S.phase==='playing'){
    var v2 = vid(); if (!v2) return;
    if (comp()==='Y' || v2.ended){ S.phase='advance'; S.advStart=Date.now(); return; }
    if (v2.playbackRate!==1.8) v2.playbackRate=1.8;
    if (!v2.muted) v2.muted=true;
    if (v2.paused) v2.play().catch(()=>{});
    if (Date.now()-S.playStart > Math.ceil((v2.duration||10)/1.8*1000)+120000){
      S.phase='advance'; S.advStart=Date.now();
    }
    return;
  }
  if (S.phase==='advance'){
    if (Date.now()-S.advStart<1500) return;
    clickNext(); S.pages++;
    S.phase='loading';
    setTimeout(()=>{ if(S.phase==='loading') S.phase='ready'; }, 4000);
  }
}
setInterval(tick, 700);
```

장이 바뀔 때 `해당 차시 학습이 종료되었습니다. 다음 차시로 이동 하시겠습니까?` 확인창이 뜬다. Playwright의 `page.on('dialog', d => d.accept())`로 자동 수락한다.

### 4단계: 진도 확인

학습창을 새로 열어 `lrnwindowVo`의 `cmptnYn`을 세면 남은 페이지를 알 수 있다.
강의실 홈의 진도 퍼센트는 페이지 로드 시점 값이라 갱신이 늦다. 새로고침해서 본다.

### 5단계: 시험

`시험 페이지 이동` → `응시하기` → 시험정보 팝업의 `#takeExamBtn` → 문항 응답 → `제출하기`.

라디오 버튼은 `input[type=radio]`이고 name이 문항별로 다르다. 40개(10문항×4지선다) 중 10개를 고른다.
제출 전에 문항별로 정확히 1개씩 선택됐는지 확인한다.

```js
const groups = {};
document.querySelectorAll('input[type=radio]').forEach(r=>{
  groups[r.name] = groups[r.name] || [];
  groups[r.name].push(r.checked);
});
// 각 그룹마다 picked === 1 인지 확인
```

제출 후 `결과확인`을 누르면 문항별 정오와 정답, 해설을 볼 수 있다.

### 6단계: 설문

`설문 참여하기` → `참여하기` → 객관식 5문항 + 주관식 3문항 → `제출하기`.
주관식을 비우면 `(6번 문항) 응답하지 않은 문항이 있습니다`로 막힌다.

### 7단계: 수료증

강의실 홈의 `수료증 출력` 링크를 누르면 PDF가 자동 다운로드된다.
파일명은 `수료증_{이름}_{날짜}-{구분}-{번호}.pdf` 형식이다 (예: `수료증_박용호_2026-1119-E-0571.pdf`).
브라우저 기본 다운로드 폴더(`~/Downloads`)에 저장된다.

수료증에는 성명·생년월일·소속·과정명·수료일자·교육시간·수료번호가 들어간다.

### 8단계: 영상 원본 수집

`prod/{cntntsid}/{장}_{페이지}.mp4` 규칙으로 전부 받는다. 페이지 수만큼 반복한다.
이미 받은 파일은 크기로 확인해 건너뛴다.

```bash
CH=(0 10 11 8 9 8 8 9 8 8 10 8 11 7 8 8 8 12)   # 장별 페이지 수
for ch in $(seq 1 17); do
  for p in $(seq 1 ${CH[$ch]}); do
    c=$(printf "%02d" $ch); q=$(printf "%02d" $p)
    curl -s -o "vod/${c}_${q}.mp4" "https://vod.kbrainc.com/kbrain/ktlSafety/prod/13/${c}_${q}.mp4"
  done
done
```

무결성은 MP4 시그니처(`ftyp` = `66747970`)로 확인한다.

```bash
head -c 12 file.mp4 | xxd -p | grep -q 66747970
```

### 9단계: 대본화 (필요할 때)

`ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le out.wav` 로 음성만 뽑고 전사한다.
`faster-whisper`가 이 환경에서 동작한다. `mlx-whisper`는 Metal 디바이스가 없어 실패했다.

```python
from faster_whisper import WhisperModel
import wave, numpy as np

with wave.open(path,'rb') as w:
    audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)/32768.0

m = WhisperModel('small', device='cpu', compute_type='int8')
segs, info = m.transcribe(audio, language='ko', vad_filter=True)
```

`av` 패키지 버전이 맞지 않으면 `decode_audio`에서 `metadata_errors` 오류가 난다. WAV를 직접 읽어 numpy 배열로 넘기면 우회된다.

자동 전사는 고유명사·숫자가 틀린다. 법령 조문·금액·비율은 원음이나 원문으로 다시 확인해야 한다.

## 7. 시험 답안 근거 (참고)

시험은 강의 내용에서 나온다. 대본을 확보했다면 grep으로 근거를 찾을 수 있다.

```bash
python3 -c "
import json,glob
for f in sorted(glob.glob('txt/*.json')):
    d=json.load(open(f)); t=' '.join(s['text'] for s in d['segments'])
    if '키워드' in t: print(f); print(t[:800])
"
```

실제로 나온 문항 유형은 이렇다.

- 사고 후 자체 조사 절차에서 관계없는 것
- 관객 추락사고의 주된 요인
- 공연 전 확인사항과 거리가 먼 것
- 야외 콘서트 준비 내용과 무관한 것
- 안전사고 예방 대책과 거리가 먼 것
- 철수·반출 단계 안전유의사항과 거리가 먼 것
- 위험성 감소 대책과 거리가 먼 것
- 재해 대응 체계에서 올바르지 않은 것
- 공연 반입 단계 안전사항과 거리가 먼 것
- 비상연락망의 필요성과 거리가 먼 것

"~와 거리가 먼 것", "올바르지 않은 것" 형태가 많다. 부정형 문제이므로 지문을 끝까지 읽어야 한다.

## 8. 걸린 시간 (실측)

| 과정 | 페이지 | 총 재생 | 1.8배속 실측 | 세션 만료 |
| --- | --- | --- | --- | --- |
| 안전총괄책임자 4시간 | 81 | 192분 | 약 2시간 20분 | 3회 |
| 안전관리담당자 8시간 | 151 | 348분 | 약 3시간 30분 | 진행 중 |

세션 만료 복구에 건당 3~5분이 더 걸린다.

## 9. 결과물 보관

드라이브 규칙(`~/내 드라이브/AGENTS.md`)에 따라 `10_더희/11_회사운영/` 아래에 둔다.

```
10_공연안전교육_공연안전지원센터/
├── 영상원본/{장번호}_{장이름}/{장}-{페이지}_{제목}.mp4
├── 수료증/수료증_{이름}_{번호}.pdf
└── 교육자료분석/{전체대본.md, 교육자료_활용안내.md, 장별대본/*.txt}
```

수료증은 사용자가 지정한 주소로 메일 발송한다. 이 사용자는 `pyh9965@naver.com`, `thehee7@naver.com` 두 곳을 지정했다.

## 10. 하지 말 것

- URL로 페이지를 직접 넘기지 않는다 (진도가 안 쌓인다)
- 16배속 같은 과한 배속을 쓰지 않는다 (비정상 이용자 등록 위험)
- 시험 재응시는 1회뿐이므로 첫 응시에 목표 점수를 맞춘다
- 영상은 교육 목적 사용과 외부 재배포를 구분한다. 외부 배포 전에 센터에 이용 조건을 확인한다
