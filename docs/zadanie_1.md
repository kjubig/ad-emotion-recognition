# Zadanie 1 — przygotowanie zbioru

Temat grupy: reklamy. Zespół ma 4 osoby; każdy oddaje swoją część osobno.
Moja część: indeks **193178**, nickname **kjubig**.

## Co przygotowano

60 fragmentów z 13 filmów YouTube: po 10 `happiness`, `sadness`, `anger`, `fear`, `disgust` i `surprise`.
Źródła zostały uzgodnione z grupą. Fragmenty tego samego filmu nie nakładają się.
Zachowano zatwierdzone klipy bez zmian. Wskazówka „zwykle 1–5 s” ma cztery wyjątki: 0,40 s, 0,82 s, 0,92 s i 5,37 s.

## Pliki do oddania

- `outputs/193178_affectube.json` — tablica 13 obiektów w formacie AffecTube, zawierająca końcowe 60 anotacji.
- `outputs/193178_klipy.zip` — dokładnie 60 odpowiadających im plików MP4, bez podfolderów i pełnych filmów.

Nazwy klipów: `<videoID>_<start>-<end>.mp4`, z czasami do dwóch miejsc po kropce, bez etykiety emocji i bez dodatkowego marginesu.

Sprawdzono liczbę i etykiety, czasy, brak duplikatów i nakładania, nazwy plików, odczyt obrazu i dźwięku,
długości z dokładnością do klatek oraz zgodność zawartości ZIP z JSON-em i lokalnymi MP4.

## Oddanie

Na eNauczaniu oddaj oba pliki z `outputs/`. W komentarzu podaj **numer zespołu**.
Jeśli ZIP przekroczy limit platformy, umieść go w chmurze i oddaj link z dostępem do odczytu.

`data/annotations/` zawiera oryginalne eksporty sprzed selekcji (82 propozycje); nie są plikami do oddania.
`data/clips/` zawiera lokalne MP4. Komplet klipów jest też w archiwum ZIP.
