# ad-emotion-recognition

Projekt zespołowy z Informatyki afektywnej poświęcony rozpoznawaniu emocji w krótkich fragmentach reklam wideo z YouTube.
Obejmuje sześć kategorii: radość, smutek, złość, strach, wstręt i zaskoczenie.

Projekt prowadzi przez cały proces pracy z danymi: zebranie i przygotowanie klipów, niezależną anotację przez inny zespół,
analizę zgodności ocen oraz budowę prostego klasyfikatora. Dalsza część obejmuje analizę błędów modelu,
demonstrację jego działania na nowych przykładach i prezentację wyników.

Obecnie repozytorium zawiera materiały do pierwszego etapu — przygotowania zbioru danych. Kolejne etapy będą rozwijane w ramach projektu.

- `data/clips/` — wspólny zbiór wybranych klipów MP4 do dalszej pracy.
- `data/annotations/` — końcowe anotacje, osobny plik `<indeks>.json` dla każdej osoby.
- `data/original_exports/` — oryginalne eksporty AffecTube sprzed selekcji.
- `outputs/` — pliki przygotowane do oddania prowadzącym.
- [`docs/zadanie_1.md`](docs/zadanie_1.md) — wymagania pierwszego zadania.

Każda osoba dodaje swoje wybrane klipy i anotacje do `data/`; gotowe paczki do oddania trafiają do `outputs/`.
