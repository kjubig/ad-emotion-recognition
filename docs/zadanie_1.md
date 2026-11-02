# Zadanie 1 — przygotowanie zbioru do zaetykietowania

Celem jest przygotowanie krótkich klipów z YouTube, które w kolejnym zadaniu zostaną przekazane innemu zespołowi do anotacji.

## Wymagania

- Każda osoba przygotowuje **60 fragmentów**: po 10 `happiness`, `sadness`, `anger`, `fear`, `disgust` i `surprise`.
- Materiały muszą pasować do tematu wybranego przez grupę. Uzgodnijcie różne filmy źródłowe dla każdej osoby i unikajcie powtórzonych scen.
- Oznaczaj fragmenty we wtyczce AffecTube, zawsze z tym samym, jednoznacznym `nickname`. Zachowaj eksport JSON z każdego filmu; nie edytuj ręcznie struktury eksportów.
- Fragment powinien obejmować widoczną emocję i być krótki, zwykle 1–5 s. Fragmenty tego samego filmu nie mogą się nakładać.

## Pliki do oddania

1. **`nrindeksu_affectube.json`** — poprawny JSON w UTF-8: tablica obiektów z eksportów AffecTube, po jednym na film. Obiekty przenieś bez zmian. Łącznie muszą zawierać 60 fragmentów, po 10 każdej emocji.
2. **`nrindeksu_klipy.zip`** — dokładnie odpowiadające anotacjom klipy MP4, bez podfolderów i pełnych filmów źródłowych.

Nazwa każdego klipu: `<videoURL>_<startTime>-<endTime>.mp4`, np. `rGhOuA3rr1k_5.16-6.28.mp4`.
`videoURL` oznacza identyfikator filmu YouTube. Czasy muszą odpowiadać anotacjom, mieć dwa miejsca po kropce i nie zawierać dodatkowego marginesu. Nazwa nie zawiera etykiety emocji.

Przed oddaniem sprawdź liczbę i etykiety fragmentów, brak duplikatów i nakładania, zgodność JSON-u z nazwami MP4 oraz odtwórz kilka klipów.

## Oddanie

Każdy student oddaje swoją część **indywidualnie na eNauczaniu**. Zastąp `nrindeksu` swoim numerem indeksu i w komentarzu podaj **numer zespołu**.
Jeżeli ZIP przekracza limit platformy, umieść go w chmurze i oddaj link z dostępem do odczytu.

Opis opracowano na podstawie instrukcji prowadzących „Zadanie 1. Przygotowanie zbioru do zaetykietowania”.
