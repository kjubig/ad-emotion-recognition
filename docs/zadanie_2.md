# Zadanie 2 – niezależne etykietowanie klipów

Zespół C ocenił zbiór przygotowany przez zespół B. Cztery osoby niezależnie przypisały każdemu z 240 klipów po jednej etykiecie emocji. Zbiór zawiera 960 ocen.

## Dane do analizy zgodności

[Plik etykiety_C.csv](../data/zadanie_2/etykiety_C.csv) zawiera jeden wiersz na klip. Kolumna `plik_klipu` odpowiada nazwie MP4 w paczce zespołu B. Kolumny `anotator_1`–`anotator_4` zawierają indywidualne etykiety pod stałymi oznaczeniami. Wartości pochodzą bezpośrednio z arkusza zbiorczego. Plik jest zapisany w UTF-8 i używa przecinków jako separatorów.

Dozwolone etykiety to `anger`, `disgust`, `fear`, `happiness`, `neutral`, `sadness` i `surprise`. Podczas analizy należy zachować cztery oceny każdego klipu.

## Pliki do oddania na kursie

Na kursie zespół oddaje `zbiorczy_etykiety_C.xlsx` i krótki raport. Pełny arkusz zawiera także indeksy, opcjonalne typy próbek i uwagi.

Lokalnie arkusz do oddania znajduje się w `C/do_oddania/`, arkusze poszczególnych osób w `C/arkusze_indywidualne/`, a roboczy raport w `C/raport/`. Klipy zespołu B pochodzą z paczki udostępnionej uczestnikom kursu.
