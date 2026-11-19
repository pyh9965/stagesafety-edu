# stagesafety-edu

공연안전지원센터(stagesafety.or.kr) 온라인 법정 안전교육 수강을 자동화하는 스킬.

Claude Code, Codex, Gemini CLI, Aside에서 같은 방식으로 쓴다. 원본은 이 폴더 한 곳에 있고, 각 AI의 스킬 디렉터리에서 심볼릭 링크로 가리킨다.

## 무엇을 하는가

- 진도 100% 달성 (영상 1.8배속 자동 재생 + 다음 버튼 자동 진행)
- 시험 응시 (점수 조절 가능)
- 설문 참여
- 수료증 PDF 다운로드
- 교육영상 원본 일괄 다운로드
- 음성 전사와 대본화

## 빠른 시작

```bash
# 영상만 받기
python3 scripts/download_videos.py --cntntsid 13 --pages 10 11 8 9 8 8 9 8 8 10 8 11 7 8 8 8 12 --out vod13

# 전사
python3 -m pip install faster-whisper numpy
python3 scripts/transcribe.py --dir vod13 --outdir txt
```

학습 자동화는 브라우저 자동화 도구가 필요하다. `SKILL.md`의 4장과 6장을 참고한다.

## 설치

```bash
git clone <이 저장소> ~/.agents/skills/stagesafety-edu
ln -s ~/.agents/skills/stagesafety-edu ~/.claude/skills/stagesafety-edu
ln -s ~/.agents/skills/stagesafety-edu ~/.codex/skills/stagesafety-edu
ln -s ~/.agents/skills/stagesafety-edu ~/.gemini/skills/stagesafety-edu
ln -s ~/.agents/skills/stagesafety-edu ~/.aside/u/0/skills/user/stagesafety-edu
```

## 반드시 알아야 할 함정

1. **URL로 페이지를 직접 넘기면 진도가 안 쌓인다.** 반드시 `.btn-next` 버튼을 눌러야 한다.
2. **세션이 2~3시간 사이에 만료된다.** 별도 컨트롤러 탭에서 돌려야 복구가 쉽다.
3. **컨트롤러 iframe으로 넣으면 CDN 주소가 틀어진다.** `scripts/proxy.js`의 프록시가 필요하다.
4. **시험 재응시는 1회뿐이다.** 첫 응시에 목표 점수를 맞춘다.
5. **설문 주관식 3문항을 비우면 제출이 막힌다.**

자세한 내용은 `SKILL.md`.

## 확인된 과정

| 과정 | ID | 페이지 | 재생시간 |
| --- | --- | --- | --- |
| 안전총괄책임자 안전교육 (공연장 외 공연을 하려는자)(4시간) | 22 | 81 | 192분 |
| 안전관리담당자 안전교육 (공연장 외 공연을 하려는자)(8시간) | 24 | 151 | 348분 |

## 라이선스

개인 업무용. 교육 영상의 권리는 공연안전지원센터에 있다. 이 저장소에는 코드와 절차만 담고 영상은 포함하지 않는다.
