#!/usr/bin/env python3
"""Sprawdzanie i pakowanie własnych eksportów AffecTube, bez zmiany źródeł."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parent.parent
LABELS = ("happiness", "sadness", "anger", "fear", "disgust", "surprise")


@dataclass
class Wynik:
    obiekty: list = field(default_factory=list)
    surowe: list = field(default_factory=list)
    liczby: Counter = field(default_factory=Counter)
    fragmenty: int = 0
    klipy: list = field(default_factory=list)
    bledy: list = field(default_factory=list)
    ostrzezenia: list = field(default_factory=list)
    brakujace_klipy: list = field(default_factory=list)
    nickname: str | None = None

    @property
    def gotowy(self):
        return (not self.bledy and not self.brakujace_klipy
                and self.fragmenty == 60
                and all(self.liczby[label] == 10 for label in LABELS)
                and self.nickname is not None)


def bez_duplikatow(pary):
    wynik = {}
    for klucz, wartosc in pary:
        if klucz in wynik:
            raise ValueError(f"powtórzony klucz JSON: {klucz!r}")
        wynik[klucz] = wartosc
    return wynik


def odrzuc_stala(wartosc):
    raise ValueError(f"niedozwolona wartość JSON: {wartosc}")


def czas(wartosc):
    if isinstance(wartosc, bool) or not isinstance(wartosc, (str, int, Decimal)):
        raise ValueError("czas musi być liczbą albo tekstem reprezentującym liczbę")
    try:
        liczba = Decimal(wartosc)
    except (InvalidOperation, ValueError):
        raise ValueError(f"nieprawidłowy czas: {wartosc!r}") from None
    if not liczba.is_finite() or liczba < 0:
        raise ValueError(f"czas musi być skończony i nieujemny: {wartosc!r}")
    _, cyfry, wykladnik = liczba.as_tuple()
    nadmiar = max(0, -wykladnik - 2)
    if nadmiar and any(cyfry[-nadmiar:]):
        raise ValueError(f"czas {wartosc!r} wymaga zaokrąglenia; popraw eksport we wtyczce")
    return liczba


def nazwa_klipu(video, start, end):
    # Zera ze znakiem mają tę samą nazwę co zwykłe zero. Nie zmieniamy JSON-u.
    return f"{video}_{abs(start) if start == 0 else start:.2f}-{abs(end) if end == 0 else end:.2f}.mp4"


def sprawdz(root=ROOT):
    wynik = Wynik()
    anotacje = root / "data" / "annotations"
    filmy = {}
    przedzialy = defaultdict(list)
    nazwy = set()
    if not anotacje.is_dir():
        wynik.ostrzezenia.append("Brak katalogu data/annotations/. Utwórz go i zapisuj w nim eksporty AffecTube.")
        return wynik
    for plik in sorted(anotacje.iterdir()):
        if not plik.is_file() or plik.suffix.lower() != ".json":
            wynik.bledy.append(f"{plik.name}: w data/annotations/ mogą być tylko oryginalne pliki JSON; przenieś pozostałe elementy.")
            continue
        try:
            surowy = plik.read_text(encoding="utf-8")
            obiekt = json.loads(surowy, object_pairs_hook=bez_duplikatow,
                                parse_float=Decimal, parse_constant=odrzuc_stala)
        except (OSError, UnicodeError, ValueError) as exc:
            wynik.bledy.append(f"{plik.name}: nie można wczytać JSON-u: {exc}")
            continue
        if not isinstance(obiekt, dict):
            wynik.bledy.append(f"{plik.name}: oczekiwany jeden oryginalny obiekt AffecTube, a nie tablica.")
            continue
        wynik.obiekty.append(obiekt)
        wynik.surowe.append(surowy.strip())
        video = obiekt.get("videoURL")
        poprawny_video = isinstance(video, str) and re.fullmatch(r"[A-Za-z0-9_-]{11}", video)
        if not poprawny_video:
            wynik.bledy.append(f"{plik.name}: videoURL musi być 11-znakowym identyfikatorem YouTube (litery, cyfry, _ i -).")
        else:
            if video in filmy:
                wynik.bledy.append(f"{plik.name}: film {video} jest już w {filmy[video]}; pozostaw tylko aktualny eksport tego filmu.")
            filmy[video] = plik.name
        nickname = obiekt.get("nickname")
        if not isinstance(nickname, str) or not nickname.strip():
            wynik.bledy.append(f"{plik.name}: nickname musi być niepustym tekstem.")
        elif wynik.nickname is None:
            wynik.nickname = nickname
        elif nickname != wynik.nickname:
            wynik.bledy.append(f"{plik.name}: nickname {nickname!r} różni się od {wynik.nickname!r}; używaj jednego oznaczenia.")
        ile = 0
        for indeks, fragment in obiekt.items():
            if indeks in ("videoURL", "nickname"):
                continue
            opis = f"{plik.name}, fragment {indeks}"
            if not re.fullmatch(r"[0-9]+", indeks):
                wynik.bledy.append(f"{opis}: nieznane pole; klucze fragmentów muszą być liczbowe.")
                continue
            ile += 1
            wynik.fragmenty += 1
            if not isinstance(fragment, dict):
                wynik.bledy.append(f"{opis}: fragment musi być obiektem.")
                continue
            label = fragment.get("label")
            if not isinstance(label, str) or label not in LABELS:
                wynik.bledy.append(f"{opis}: nieprawidłowa etykieta {label!r}; dozwolone: {', '.join(LABELS)}.")
            else:
                wynik.liczby[label] += 1
            try:
                start = czas(fragment.get("startTime"))
                end = czas(fragment.get("endTime"))
                if end <= start:
                    raise ValueError("endTime musi być większe niż startTime")
            except ValueError as exc:
                wynik.bledy.append(f"{opis}: {exc}.")
                continue
            if end - start < 1 or end - start > 5:
                wynik.ostrzezenia.append(f"{opis}: długość {end - start} s jest poza zwykłym zakresem 1–5 s; sprawdź, czy fragment obejmuje jedną reakcję.")
            if poprawny_video:
                przedzialy[video].append((start, end, opis))
                nazwa = nazwa_klipu(video, start, end)
                if nazwa in nazwy:
                    wynik.bledy.append(f"{opis}: powtórzony fragment i nazwa pliku {nazwa}.")
                else:
                    nazwy.add(nazwa)
                    wynik.klipy.append(nazwa)
        if ile == 0:
            wynik.bledy.append(f"{plik.name}: brak oznaczonych fragmentów.")
    for video, fragmenty in przedzialy.items():
        najdalszy_end = None
        poprzedni = None
        for start, end, opis in sorted(fragmenty):
            if najdalszy_end is not None and start < najdalszy_end:
                wynik.bledy.append(f"Nakładanie w filmie {video}: {poprzedni} oraz {opis}.")
            if najdalszy_end is None or end > najdalszy_end:
                najdalszy_end, poprzedni = end, opis
    for nazwa in wynik.klipy:
        klip = root / "data" / "clips" / nazwa
        try:
            istnieje = klip.is_file() and klip.stat().st_size > 0
        except OSError:
            istnieje = False
        if not istnieje:
            wynik.brakujace_klipy.append(nazwa)
    return wynik


def pokaz(wynik):
    print(f"Eksporty JSON: {len(wynik.obiekty)} | fragmenty: {wynik.fragmenty}/60")
    print(f"Nickname: {wynik.nickname or 'jeszcze nie ustalony w eksportach'}")
    for label in LABELS:
        ile = wynik.liczby[label]
        dopisek = f"brakuje {10 - ile}" if ile < 10 else f"nadmiar {ile - 10}" if ile > 10 else "komplet"
        print(f"  {label}: {ile}/10 ({dopisek})")
    for blad in wynik.bledy:
        print(f"BŁĄD: {blad}")
    for ostrzezenie in wynik.ostrzezenia:
        print(f"UWAGA: {ostrzezenie}")
    if wynik.brakujace_klipy:
        print(f"Brakuje {len(wynik.brakujace_klipy)} niepustych plików w data/clips/:")
        for nazwa in wynik.brakujace_klipy:
            print(f"  {nazwa}")
    print("Zbiór gotowy do spakowania." if wynik.gotowy else "Zbiór nie jest jeszcze gotowy do spakowania.")
    print("Sprawdzam anotacje, nazwy i obecność niepustych plików. Nie sprawdzam zawartości ani faktycznej długości mediów; obejrzyj klipy.")


def spakuj(root, wynik, indeks, zastap=False):
    if not re.fullmatch(r"[0-9]+", indeks):
        raise ValueError("Numer indeksu może zawierać wyłącznie cyfry.")
    if not wynik.gotowy:
        raise ValueError("Pakowanie wymaga poprawnych anotacji: 60 fragmentów, po 10 każdej emocji, jeden nickname i wszystkie klipy.")
    katalog = root / "outputs"
    katalog.mkdir(parents=True, exist_ok=True)
    json_path = katalog / f"{indeks}_affectube.json"
    zip_path = katalog / f"{indeks}_klipy.zip"
    if not zastap and (json_path.exists() or zip_path.exists()):
        raise ValueError("Pliki wynikowe już istnieją. Jeśli chcesz je zastąpić, dodaj --zastap.")
    # Zachowujemy treść każdego oryginalnego obiektu, także zapis liczb i tekstów.
    polaczony = "[\n" + ",\n".join(wynik.surowe) + "\n]\n"
    with tempfile.TemporaryDirectory(prefix="affectube_", dir=katalog) as tymczasowy:
        tmp = Path(tymczasowy)
        (tmp / "anotacje.json").write_text(polaczony, encoding="utf-8")
        with zipfile.ZipFile(tmp / "klipy.zip", "w", compression=zipfile.ZIP_STORED) as archiwum:
            for nazwa in wynik.klipy:
                archiwum.write(root / "data" / "clips" / nazwa, arcname=nazwa)
        (tmp / "anotacje.json").replace(json_path)
        (tmp / "klipy.zip").replace(zip_path)
    return json_path, zip_path


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    komendy = parser.add_subparsers(dest="komenda", required=True)
    komendy.add_parser("sprawdz", help="Pokaż stan zbioru, także na początku zbierania.")
    pakowanie = komendy.add_parser("spakuj", help="Przygotuj dwa pliki do oddania z kompletnych danych.")
    pakowanie.add_argument("--indeks", required=True, help="Twój numer indeksu, złożony z cyfr.")
    pakowanie.add_argument("--zastap", action="store_true", help="Jawnie zezwól na zastąpienie istniejących wyników.")
    args = parser.parse_args(argv)
    wynik = sprawdz(root)
    pokaz(wynik)
    if args.komenda == "sprawdz":
        # Niepełny zbiór jest normalny podczas pracy; wadliwe wejścia to błąd.
        return 1 if wynik.bledy else 0
    try:
        json_path, zip_path = spakuj(root, wynik, args.indeks, args.zastap)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"BŁĄD: {exc}")
        return 1
    print(f"Utworzono: {json_path}\nUtworzono: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
