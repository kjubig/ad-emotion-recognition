#!/usr/bin/env python3
"""Waliduje plik z metadanymi klipów i pobiera wskazane fragmenty z YouTube.

Użycie:
    python3 scripts/fetch_clips.py data/metadata/clips_lukasz.csv            # walidacja + pobieranie
    python3 scripts/fetch_clips.py data/metadata/clips_lukasz.csv --check    # tylko walidacja
"""
import argparse
import csv
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

REQUIRED = ["clip_id", "collector", "youtube_url", "brand", "target_emotion"]  # start/end opcjonalne
CLIPS_PER_EMOTION = 10
N_EMOTIONS = 6
MIN_LEN, MAX_LEN = 2, 15  # sekundy – poza tym zakresem tylko ostrzeżenie
YT = re.compile(r"^https?://(www\.|m\.)?(youtube\.com/(watch\?v=|shorts/)|youtu\.be/)([\w-]{11})")
WATCH = re.compile(r"^https?://(www\.)?youtube\.com/watch\?v=[\w-]{11}")
TIME = re.compile(r"^(\d{1,2}:)?\d{1,2}:\d{2}(\.\d+)?$")


def to_sec(t: str) -> float:
    parts = [float(p) for p in t.split(":")]
    return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))


def validate(rows):
    errors, warnings = [], []
    ids = Counter(r["clip_id"] for r in rows)
    for cid, n in ids.items():
        if n > 1:
            errors.append(f"powtórzony clip_id: {cid} ({n}x)")
    seen, seen_vid = {}, {}
    for i, r in enumerate(rows, start=2):
        tag = f"wiersz {i} ({r.get('clip_id') or '?'})"
        for col in REQUIRED:
            if not (r.get(col) or "").strip():
                errors.append(f"{tag}: puste pole '{col}'")
        url = r.get("youtube_url", "")
        m = YT.match(url) if url else None
        if url and not m:
            errors.append(f"{tag}: niepoprawny link YouTube")
        elif m and not WATCH.match(url):
            errors.append(f"{tag}: AffecTube działa tylko z linkami youtube.com/watch?v=… "
                          f"(użyj https://www.youtube.com/watch?v={m.group(4)})")
        if m:
            vid = m.group(4)
            if vid in seen_vid:
                warnings.append(f"{tag}: ten sam film co {seen_vid[vid]}")
            seen_vid.setdefault(vid, r.get("clip_id"))
        s, e = r.get("start", ""), r.get("end", "")
        if bool(s) != bool(e):
            errors.append(f"{tag}: podaj oba pola start i end albo żadne")
        if s and e:
            if not (TIME.match(s) and TIME.match(e)):
                errors.append(f"{tag}: zły format czasu (MM:SS lub HH:MM:SS)")
            else:
                d = to_sec(e) - to_sec(s)
                if d <= 0:
                    errors.append(f"{tag}: end <= start")
                elif not MIN_LEN <= d <= MAX_LEN:
                    warnings.append(f"{tag}: długość {d:.1f} s (zalecane {MIN_LEN}-{MAX_LEN} s)")
                key = (url, s, e)
                if key in seen:
                    warnings.append(f"{tag}: ten sam fragment co {seen[key]}")
                seen[key] = r["clip_id"]
    counts = Counter(r["target_emotion"] for r in rows if r.get("target_emotion"))
    if len(counts) != N_EMOTIONS:
        warnings.append(f"liczba emocji: {len(counts)} (oczekiwane {N_EMOTIONS})")
    for emo, n in sorted(counts.items()):
        if n != CLIPS_PER_EMOTION:
            warnings.append(f"emocja '{emo}': {n} klipów (oczekiwane {CLIPS_PER_EMOTION})")
    return errors, warnings, counts


def fetch(row, out_dir: Path):
    if not (row.get("start") and row.get("end")):
        return "pominięto (brak start/end)"
    out = out_dir / f"{row['clip_id']}.mp4"
    if out.exists():
        return "pominięto (istnieje)"
    cmd = [
        "yt-dlp", "-q", "--no-warnings", "--no-playlist",
        "-f", "bv*[ext=mp4][height<=720]+ba[ext=m4a]/b[ext=mp4]/b",
        "--merge-output-format", "mp4",
        "--download-sections", f"*{row['start']}-{row['end']}",
        "--force-keyframes-at-cuts",
        "-o", str(out_dir / f"{row['clip_id']}.%(ext)s"),
        row["youtube_url"],
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return "OK" if r.returncode == 0 else f"BŁĄD: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path)
    ap.add_argument("--out", type=Path, default=Path("data/raw"))
    ap.add_argument("--check", action="store_true", help="tylko walidacja, bez pobierania")
    a = ap.parse_args()

    with a.csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"Brak kolumn: {', '.join(missing)}")
        rows = [r for r in reader if any((v or "").strip() for v in r.values())]

    errors, warnings, counts = validate(rows)
    print(f"Klipów: {len(rows)}  |  " + ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    for w in warnings:
        print("  [UWAGA]", w)
    for e in errors:
        print("  [BŁĄD] ", e)
    if errors:
        sys.exit("Popraw błędy przed pobieraniem.")
    if a.check:
        return
    if not shutil.which("yt-dlp") or not shutil.which("ffmpeg"):
        sys.exit("Brak yt-dlp lub ffmpeg – uruchom scripts/check_tools.sh")

    a.out.mkdir(parents=True, exist_ok=True)
    for i, r in enumerate(rows, 1):
        print(f"[{i}/{len(rows)}] {r['clip_id']}: {fetch(r, a.out)}")


if __name__ == "__main__":
    main()
