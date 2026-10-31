#!/usr/bin/env bash
# Sprawdza, czy są zainstalowane narzędzia potrzebne do zbierania klipów.
ok=0
check() {
  local name="$1" hint="$2"
  if command -v "$name" >/dev/null 2>&1; then
    printf "  [OK]   %-8s %s\n" "$name" "$("$name" --version 2>&1 | head -1)"
  else
    printf "  [BRAK] %-8s -> %s\n" "$name" "$hint"; ok=1
  fi
}
echo "Narzędzia:"
check yt-dlp  "brew install yt-dlp"
check ffmpeg  "brew install ffmpeg"
check ffprobe "brew install ffmpeg"
check python3 "brew install python"
check git     "xcode-select --install"

if command -v python3 >/dev/null 2>&1; then
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' \
    || { echo "  [UWAGA] python3 < 3.10"; ok=1; }
fi

if command -v yt-dlp >/dev/null 2>&1; then
  echo "Test pobierania (5 s z YouTube, bez zapisu na stałe)..."
  tmp=$(mktemp -d)
  if yt-dlp -q --no-warnings -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" \
       --download-sections "*00:00-00:05" -o "$tmp/t.%(ext)s" \
       "https://www.youtube.com/watch?v=jNQXAC9IVRw" >/dev/null 2>&1 && ls "$tmp"/t.* >/dev/null 2>&1; then
    echo "  [OK]   pobieranie fragmentu działa"
  else
    echo "  [BŁĄD] nie udało się pobrać fragmentu – zaktualizuj: brew upgrade yt-dlp"; ok=1
  fi
  rm -rf "$tmp"
fi

[ $ok -eq 0 ] && echo "Wszystko gotowe." || echo "Uzupełnij brakujące elementy powyżej."
exit $ok
