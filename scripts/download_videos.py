#!/usr/bin/env python3
"""
공연안전지원센터 온라인 교육 영상 일괄 다운로드.

사용법:
  python3 download_videos.py --cntntsid 13 --pages 10 11 8 9 8 8 9 8 8 10 8 11 7 8 8 8 12 --out vod13
  python3 download_videos.py --cntntsid 13 --chapters 17 --out vod13   # 페이지 수를 모를 때

--pages 는 장별 페이지 수를 순서대로 준다. --chapters 와 함께 쓰지 않는다.
--chapters 모드에서는 1~12 페이지까지 시도하고 200이 아닌 것은 건너뛴다.
"""
import argparse
import os
import sys
import time
import urllib.request

BASE = 'https://vod.kbrainc.com/kbrain/ktlSafety/prod/{sid}/{ch:02d}_{pg:02d}.mp4'


def is_mp4(path):
    try:
        with open(path, 'rb') as f:
            head = f.read(12)
        return b'ftyp' in head
    except OSError:
        return False


def fetch(url, dest, timeout=120):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    if len(data) < 1000:
        return False
    with open(dest, 'wb') as f:
        f.write(data)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cntntsid', required=True, help='콘텐츠 ID (예: 12, 13)')
    ap.add_argument('--pages', nargs='*', type=int, help='장별 페이지 수')
    ap.add_argument('--chapters', type=int, help='장 개수 (페이지 수 모를 때)')
    ap.add_argument('--max-per-chapter', type=int, default=14)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    if args.pages:
        plan = list(enumerate(args.pages, start=1))
    elif args.chapters:
        plan = [(c, args.max_per_chapter) for c in range(1, args.chapters + 1)]
    else:
        sys.exit('--pages 또는 --chapters 중 하나가 필요합니다.')

    total = ok = skip = fail = 0
    for ch, count in plan:
        for pg in range(1, count + 1):
            total += 1
            dest = os.path.join(args.out, f'{ch:02d}_{pg:02d}.mp4')
            if os.path.exists(dest) and os.path.getsize(dest) > 1000 and is_mp4(dest):
                ok += 1
                continue
            url = BASE.format(sid=args.cntntsid, ch=ch, pg=pg)
            try:
                if fetch(url, dest):
                    if is_mp4(dest):
                        ok += 1
                        print(f'ok   {ch:02d}_{pg:02d}', flush=True)
                    else:
                        os.remove(dest)
                        skip += 1
                        print(f'bad  {ch:02d}_{pg:02d} (mp4 아님)', flush=True)
                else:
                    skip += 1
                    if os.path.exists(dest):
                        os.remove(dest)
                    print(f'skip {ch:02d}_{pg:02d} (작음)', flush=True)
            except Exception as e:
                fail += 1
                if os.path.exists(dest):
                    os.remove(dest)
                print(f'fail {ch:02d}_{pg:02d} {e}', flush=True)
                time.sleep(1)

    print(f'\n총 {total}개 시도 / 성공 {ok} / 건너뜀 {skip} / 실패 {fail}')


if __name__ == '__main__':
    main()
