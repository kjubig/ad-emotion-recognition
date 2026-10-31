# Przygotowanie własnych 60 fragmentów

Stan na 28.10.2026: 13 eksportów, 82 propozycje; wszystkie emocje mają co najmniej 10 przykładów.
Anotacje znajdują się w `data/annotations/`, ich połączona kopia w `data/metadata/affectube_all.json`.

## Co dalej

1. Obejrzyj zebrane fragmenty i wybierz 10 na każdą emocję: happiness, sadness, anger, fear, disgust, surprise.
   Nie zmieniaj etykiet tylko po to, żeby wyrównać liczby. Sprawdź szczególnie krótkie i długie reakcje.
2. Końcową selekcję zapisz przez AffecTubeLocal i wyeksportuj ponownie, zachowując kopię pełnego zbioru.
   Wtyczka zapisuje dane przez **Save to file**. Nickname przez cały projekt: `kjubig`.
   Nie edytuj ręcznie struktury oryginalnych plików JSON.
3. Porównaj identyfikatory źródłowych filmów z grupą, aby uniknąć wspólnych nagrań.
4. Pobierz filmy i wytnij fragmenty dokładnie według anotacji, bez dodatkowego marginesu.
   Przy użyciu DatasetCreator ustaw `-n 0`; wejściem jest folder pojedynczych JSON-ów, nie scalona tablica.
5. Umieść wycięte MP4 w `data/clips/`. Nazwa: `<videoID>_<start:.2f>-<end:.2f>.mp4`,
   np. `rGhOuA3rr1k_5.16-6.28.mp4`. Nazwa nie zawiera etykiety emocji.
6. Uruchom `python3 scripts/przygotuj.py sprawdz`, obejrzyj wynikowe klipy i przygotuj paczkę.

Przed podmianą eksportów do końcowej selekcji zachowaj pełne 82 propozycje w historii Git lub kopii roboczej.
Obecne narzędzie sprawdza cały folder `data/annotations/`; przy 82 fragmentach celowo nie pozwala spakować oddania.

## Pliki do oddania

```bash
python3 scripts/przygotuj.py spakuj --indeks TWOJ_NUMER_INDEKSU
```

Zastąp oznaczenie swoim numerem indeksu. Powstaną:

- `outputs/<indeks>_affectube.json` — tablica oryginalnych obiektów eksportów, bez zmiany ich struktury;
- `outputs/<indeks>_klipy.zip` — 60 wyciętych MP4 bez podfolderów i bez pełnych filmów.

Każdy student oddaje swoją część indywidualnie. W komentarzu na eNauczaniu podaj numer zespołu.
Wymagania prowadzących są w `zadanie_1.txt` i `instrukcja_studenta.pdf`.
Wskazówki organizacji folderów i przeglądu są ustaleniami roboczymi projektu.
