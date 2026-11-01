#!/usr/bin/env python3
"""Pobierz źródła i wytnij roboczą selekcję AffecTube, bez zmiany anotacji."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import av
import imageio_ffmpeg
import yt_dlp

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'happiness','sadness','anger','fear','disgust','surprise'}


def inspect(path, expected=None, require_audio=False):
    with av.open(str(path)) as media:
        if not media.streams.video:
            raise ValueError('brak strumienia wideo')
        stream = media.streams.video[0]
        fps = float(stream.average_rate or 25)
        audio = bool(media.streams.audio)
        frames = list(media.decode(video=0))
        if not frames:
            raise ValueError('nie można odczytać klatek')
        first = float(frames[0].pts * frames[0].time_base)
        last = float(frames[-1].pts * frames[-1].time_base)
        duration = last - first + 1 / fps
        if expected is not None and abs(duration - float(expected)) > 1 / fps + 0.025:
            raise ValueError(f'długość wideo {duration:.4f} s zamiast {expected} s')
        if require_audio and not audio:
            raise ValueError('brak dźwięku obecnego w źródle')
        result = {'video_duration': round(duration,6), 'frames':len(frames),
                  'fps':round(fps,6),'width':stream.width,'height':stream.height,'audio':audio,
                  'size_bytes':path.stat().st_size}
    if audio:
        with av.open(str(path)) as media:
            if next(media.decode(audio=0),None) is None:
                raise ValueError('nie można odczytać dźwięku')
    return result


class Logger:
    def debug(self,message): pass
    def info(self,message): pass
    def warning(self,message):
        if 'ffprobe' not in message:
            print('UWAGA:',message,flush=True)
    def error(self,message):
        print('BŁĄD POBIERANIA:',message,flush=True)


def process(video, entries, node):
    ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe())
    bindir = ROOT / '.venv/bin'
    link = bindir / 'ffmpeg'
    if not link.exists(): link.symlink_to(ffmpeg)
    raw = ROOT / 'data/raw'
    clips = ROOT / 'data/clips'
    source = raw / f'{video}.mp4'
    if not source.exists():
        print(f'Pobieranie: {video}',flush=True)
        options = {
            'format':'bv[ext=mp4][vcodec^=avc1][height<=720]+ba[ext=m4a]/b[ext=mp4][height<=720]/b[height<=720]',
            'merge_output_format':'mp4', 'outtmpl':str(raw/'%(id)s.%(ext)s'),
            'ffmpeg_location':str(bindir),'noplaylist':True,'quiet':True,'noprogress':True,
            'socket_timeout':25,'retries':2,'fragment_retries':2,'logger':Logger(),
        }
        if node: options['js_runtimes']={'node':{'path':node}}
        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([f'https://www.youtube.com/watch?v={video}'])
        if not source.exists():
            alternatives=[p for p in raw.glob(f'{video}.*') if p.suffix in ('.webm','.mkv','.mp4') and '.f' not in p.stem]
            if len(alternatives)!=1: raise ValueError('nie znaleziono pobranego źródła')
            source=alternatives[0]
    with av.open(str(source)) as media:
        require_audio=bool(media.streams.audio)
        if not media.streams.video:raise ValueError('źródło nie zawiera wideo')
        source_duration=float(media.duration/av.time_base) if media.duration else None
    output=[]
    for key,entry in entries:
        start,end=Decimal(entry['startTime']),Decimal(entry['endTime'])
        if source_duration is not None and float(end)>source_duration+0.05:
            raise ValueError(f'koniec {end} poza źródłem {source_duration}')
        name=f'{video}_{start:.2f}-{end:.2f}.mp4'
        target=clips/name
        if target.exists():
            details=inspect(target,end-start,require_audio)
        else:
            tmp=clips/(target.stem+'.partial.mp4')
            command=[str(ffmpeg),'-hide_banner','-loglevel','error','-nostdin','-y',
                     '-ss',str(start),'-i',str(source),'-t',str(end-start),
                     '-map','0:v:0','-map','0:a:0?','-c:v','libx264','-preset','medium',
                     '-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k',
                     '-movflags','+faststart',str(tmp)]
            result=subprocess.run(command,capture_output=True,text=True)
            if result.returncode:
                raise RuntimeError(result.stderr[-1000:])
            details=inspect(tmp,end-start,require_audio)
            tmp.replace(target)
        output.append({'filename':name,'videoURL':video,'source_entry':key,**entry,
                       'expected_duration':str(end-start),**details,
                       'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    print(f'Gotowe: {video} — {len(output)} klipów',flush=True)
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node',default=shutil.which('node'))
    parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args()
    if not 1<=args.workers<=4:parser.error('--workers: od 1 do 4')
    selected=ROOT/'data/metadata/affectube_selected.json'
    digest=hashlib.sha256(selected.read_bytes()).hexdigest()
    objects=json.loads(selected.read_text())
    jobs={};counts=Counter();names=set()
    for obj in objects:
        video=obj['videoURL'];entries=[]
        for key,x in obj.items():
            if not isinstance(x,dict) or 'label' not in x:continue
            a,b=Decimal(x['startTime']),Decimal(x['endTime'])
            assert x['label'] in LABELS and a>=0 and b>a
            assert a==a.quantize(Decimal('.01')) and b==b.quantize(Decimal('.01'))
            name=f'{video}_{a:.2f}-{b:.2f}.mp4';assert name not in names;names.add(name)
            counts[x['label']]+=1;entries.append((key,x))
        intervals=sorted((Decimal(x['startTime']),Decimal(x['endTime'])) for _,x in entries)
        assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:]))
        if entries:
            assert video not in jobs;jobs[video]=entries
    assert counts==Counter({label:10 for label in LABELS}),counts
    for folder in ('data/raw','data/clips'):(ROOT/folder).mkdir(parents=True,exist_ok=True)
    results=[];errors=[]
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures={executor.submit(process,v,e,args.node):v for v,e in jobs.items()}
        for future in as_completed(futures):
            try:results.extend(future.result())
            except Exception as exc:
                video=futures[future]
                errors.append({'videoURL':video,'error':str(exc)[:1000]})
                print(f'Niepowodzenie: {video}: {exc}',flush=True)
    assert hashlib.sha256(selected.read_bytes()).hexdigest()==digest
    report={'selection_sha256':digest,'expected_clips':60,'created_clips':len(results),
            'complete':len(results)==60 and not errors,'errors':errors,
            'clips':sorted(results,key=lambda x:x['filename'])}
    (ROOT/'data/metadata/clip_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'Wynik: {len(results)}/60 zweryfikowanych klipów; błędy: {len(errors)}',flush=True)
    return 0 if report['complete'] else 1

if __name__=='__main__':sys.exit(main())
