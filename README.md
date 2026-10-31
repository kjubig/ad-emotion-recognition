# ad-emotion-recognition

Projekt z Informatyki afektywnej: rozpoznawanie emocji w reklamach z YouTube.
Zespół 4-osobowy, docelowo po 60 fragmentów na osobę (10 dla każdej z sześciu emocji).
Repozytorium zawiera obecnie część oznaczoną przez `kjubig` oraz materiały do dalszych etapów projektu.

## Aktualny stan — 28.10.2026

Zebrano **82 fragmenty z 13 filmów**. Oryginalne eksporty pozostają niezmienione.

| Emocja | Zebrano | Do oddania |
|---|---:|---:|
| happiness | 19 | 10 |
| sadness | 11 | 10 |
| anger | 17 | 10 |
| fear | 14 | 10 |
| disgust | 10 | 10 |
| surprise | 11 | 10 |

Każda kategoria ma wymaganą liczbę przykładów. Pozostaje wybór końcowych 60 i przygotowanie klipów MP4.
Kontrola wykazała poprawną strukturę, wspólny nickname, dozwolone etykiety oraz brak duplikatów i nakładania czasów.
21 fragmentów ma długość poza zwykłym zakresem 1–5 s; wymaga to przeglądu, nie oznacza automatycznego odrzucenia.
Nie sprawdzono tu wizualnie poprawności wszystkich etykiet. Klipy MP4 nie zostały jeszcze pobrane ani wycięte.

## Gdzie są pliki

| Ścieżka | Zawartość |
|---|---|
| `data/annotations/` | 13 oryginalnych eksportów AffecTubeLocal, wyłącznie pliki JSON |
| `data/metadata/affectube_all.json` | Wszystkie eksporty połączone w tablicę: 13 obiektów, 82 fragmenty |
| `data/metadata/clips_*.csv` | Wcześniejszy szablon i pusta lista robocza; źródłem aktualnych anotacji są JSON-y |
| `data/clips/` | Miejsce na wycięte MP4 (media pomijane przez Git) |
| `data/raw/` | Miejsce na pełne filmy robocze (pomijane przez Git) |
| `docs/zadanie_1.txt` | Szczegółowe wymagania zadania 1 |
| `docs/instrukcja_studenta.pdf` | Ogólna instrukcja projektu |
| `docs/START.md` | Dalszy przebieg pracy i wymagania oddania |
| `docs/lista_filmow.md` | Pierwotna lista kandydatów, nie wykaz zebranych anotacji |
| `docs/lista_zrodel_kjubig.md` | Aktualna lista 13 oznaczonych źródeł do porównania w grupie |
| `scripts/przygotuj.py` | Kontrola JSON-ów i pakowanie kompletu do oddania |
| `tests/` | Testy narzędzia kontroli i pakowania |
| `outputs/` | Docelowe pliki do oddania |
| `annotation/`, `analysis/`, `model/`, `presentation/` | Miejsce na kolejne etapy projektu |

`affectube_all.json` obejmuje wszystkie 82 propozycje, więc nie jest jeszcze ostatecznym plikiem 60 fragmentów do oddania.
Weryfikacja grupowych duplikatów wymaga porównania identyfikatorów filmów z pozostałymi trzema osobami.

## Kontrola danych

Uruchom z głównego folderu repozytorium:

```bash
python3 scripts/przygotuj.py sprawdz
python3 -m unittest discover -s tests -v
```

Kontrola działa także na nadmiarowym zbiorze. Pakowanie jest dostępne dopiero przy dokładnie 60 fragmentach,
po 10 każdej emocji, i obecności wszystkich odpowiadających im plików MP4:

```bash
python3 scripts/przygotuj.py spakuj --indeks TWOJ_NUMER_INDEKSU
```

Wynik: `outputs/<indeks>_affectube.json` oraz `outputs/<indeks>_klipy.zip`.
Narzędzie nie zmienia eksportów i nie pobiera filmów.

## Narzędzia i dalsza praca

Do oznaczania używamy [AffecTubeLocal](https://github.com/AffectiveSE/AffecTubeLocal),
zapisującego JSON lokalnie przyciskiem **Save to file**. Używamy tylko etykiet wymienionych powyżej, bez `confusion`.
Do pobierania i cięcia można użyć [DatasetCreator](https://github.com/AffecTube/DatasetCreator), z marginesem `-n 0`.
Dokładne wymagania są w `docs/zadanie_1.txt`.

Wcześniejsze `scripts/fetch_clips.py` i `scripts/check_tools.sh` zachowano.
Skrypt CSV jest wcześniejszym narzędziem roboczym: nadaje nazwy na podstawie `clip_id`, więc sam nie przygotowuje
wymaganych w zadaniu nazw `<videoID>_<start>-<end>.mp4`. Dalsze przygotowanie oprzyj na eksportach JSON.

Repozytorium GitHub (prywatne): [kjubig/ad-emotion-recognition](https://github.com/kjubig/ad-emotion-recognition).
