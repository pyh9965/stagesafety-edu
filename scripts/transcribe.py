#!/usr/bin/env python3
"""
교육 영상 음성을 한국어로 전사한다.

사용법:
  python3 transcribe.py --video input.mp4 --out out.json
  python3 transcribe.py --dir vod13 --outdir txt

전제:
  ffmpeg 가 PATH 에 있거나 FFMPEG 환경변수로 지정돼 있어야 한다.
  python3 -m pip install faster-whisper numpy

주의:
  av 패키지 버전이 맞지 않으면 decode_audio 에서 metadata_errors 오류가 난다.
  그래서 ffmpeg 로 WAV 를 뽑고 wave 모듈로 직접 읽어 numpy 배열로 넘긴다.
  mlx-whisper 는 Metal 디바이스가 없는 환경에서 실패한다.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from faster_whisper import WhisperModel

FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')


def extract_wav(video, wav):
    subprocess.run(
        [FFMPEG, '-y', '-loglevel', 'error', '-i', video,
         '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', wav],
        check=True,
    )


def load_wav(path):
    with wave.open(path, 'rb') as w:
        if w.getframerate() != 16000 or w.getnchannels() != 1:
            raise ValueError('16000Hz 모노 WAV 가 아닙니다')
        buf = w.readframes(w.getnframes())
    return np.frombuffer(buf, dtype=np.int16).astype(np.float32) / 32768.0


def transcribe(model, video, out_json):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf:
        wav = tf.name
    try:
        extract_wav(video, wav)
        audio = load_wav(wav)
        segs, info = model.transcribe(audio, language='ko', vad_filter=True, beam_size=5)
        out = [{'start': round(s.start, 2), 'end': round(s.end, 2), 'text': s.text.strip()} for s in segs]
        data = {'duration': info.duration, 'segments': out}
        with open(out_json, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        return len(out)
    finally:
        if os.path.exists(wav):
            os.remove(wav)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--video')
    ap.add_argument('--out')
    ap.add_argument('--dir')
    ap.add_argument('--outdir')
    ap.add_argument('--model', default='small')
    args = ap.parse_args()

    model = WhisperModel(args.model, device='cpu', compute_type='int8')

    if args.video:
        n = transcribe(model, args.video, args.out)
        print(f'{args.out} : {n} segments')
        return

    if args.dir:
        os.makedirs(args.outdir, exist_ok=True)
        files = sorted(f for f in os.listdir(args.dir) if f.endswith('.mp4'))
        for i, name in enumerate(files, 1):
            out = os.path.join(args.outdir, name[:-4] + '.json')
            if os.path.exists(out) and os.path.getsize(out) > 10:
                continue
            n = transcribe(model, os.path.join(args.dir, name), out)
            print(f'[{i}/{len(files)}] {name} : {n} segments', flush=True)
        return

    sys.exit('--video 또는 --dir 이 필요합니다')


if __name__ == '__main__':
    main()
