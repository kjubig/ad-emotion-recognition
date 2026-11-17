# ad-emotion-recognition

Projekt zespołowy z Informatyki afektywnej poświęcony rozpoznawaniu emocji w krótkich fragmentach reklam wideo z YouTube.
W Zadaniu 1 wybrano klipy dla sześciu emocji: radości, smutku, złości, strachu, wstrętu i zaskoczenia.
W Zadaniu 2 do listy etykiet dodano `neutral`.

Projekt prowadzi przez cały proces pracy z danymi: zebranie i przygotowanie klipów, niezależną anotację przez inny zespół,
analizę zgodności ocen oraz budowę prostego klasyfikatora. Dalsza część obejmuje analizę błędów modelu,
demonstrację jego działania na nowych przykładach i prezentację wyników.

## Zadanie 1 – przygotowanie klipów zespołu C

- `data/clips/` zawiera klipy MP4 wybrane przez zespół.
- `data/annotations/` zawiera końcowe anotacje, po jednym pliku JSON na osobę.
- `data/original_exports/` zawiera pierwotne eksporty AffecTube.
- `done/` zawiera paczki do oddania w Zadaniu 1.
- [Instrukcja Zadania 1](docs/zadanie_1.md) opisuje wymagania i format plików.

## Zadanie 2 – etykietowanie klipów zespołu B

- [Opis Zadania 2](docs/zadanie_2.md) wyjaśnia strukturę danych i podaje pliki wymagane do oddania na kursie.
