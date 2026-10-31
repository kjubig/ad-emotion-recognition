"""Syntetyczne testy wyłącznie w usuwanych katalogach tymczasowych."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import przygotuj as p


class PrzygotowanieTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="test affectube ")
        self.root = Path(self.tmp.name)
        for katalog in ("data/annotations", "data/clips", "outputs"):
            (self.root / katalog).mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def eksport(self, nazwa="film.json", video="video_-1234", fragmenty=None, nickname="Jan K"):
        obiekt = dict(fragmenty if fragmenty is not None else {"3": {"startTime": "0", "endTime": "1.5", "label": "happiness"}})
        obiekt.update(videoURL=video, nickname=nickname)
        plik = self.root / "data" / "annotations" / nazwa
        plik.write_text(json.dumps(obiekt, ensure_ascii=False, indent=2), encoding="utf-8")
        return plik

    def komplet(self):
        for numer, label in enumerate(p.LABELS):
            fragmenty = {str(2 * n): {"startTime": f"{3*n}.1000", "endTime": f"{3*n+1}.10", "label": label} for n in range(10)}
            self.eksport(f"{numer}.json", video=f"AbCdEfGh_{numer:02}", fragmenty=fragmenty)
        stan = p.sprawdz(self.root)
        for nazwa in stan.klipy:
            (self.root / "data" / "clips" / nazwa).write_bytes(b"syntetyczna zawartosc testowa")

    def test_pusty_i_czesciowy_zbior(self):
        self.assertFalse(p.sprawdz(self.root).gotowy)
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(p.main(["sprawdz"], root=self.root), 0)
        self.assertIn("happiness: 0/10", out.getvalue())
        self.eksport()
        stan = p.sprawdz(self.root)
        self.assertEqual(stan.fragmenty, 1)
        self.assertEqual(stan.brakujace_klipy, ["video_-1234_0.00-1.50.mp4"])
        self.assertFalse(stan.gotowy)

    def test_pakowanie_niezmiennosc_i_plaski_zip(self):
        self.komplet()
        przed = {plik: plik.read_bytes() for plik in (self.root / "data" / "annotations").iterdir()}
        (self.root / "data" / "clips" / "AbCdEfGh_00.mp4").write_bytes(b"pelny film")
        (self.root / "data" / "clips" / "niepotrzebny.mp4").write_bytes(b"inny klip")
        stan = p.sprawdz(self.root)
        self.assertTrue(stan.gotowy, stan.bledy)
        json_path, zip_path = p.spakuj(self.root, stan, "123456")
        scalony = json_path.read_text(encoding="utf-8")
        self.assertEqual(len(json.loads(scalony)), 6)
        for plik, dane in przed.items():
            self.assertEqual(plik.read_bytes(), dane)
            self.assertIn(dane.decode().strip(), scalony)
        with zipfile.ZipFile(zip_path) as archiwum:
            self.assertEqual(set(archiwum.namelist()), set(stan.klipy))
            self.assertEqual(len(archiwum.namelist()), 60)
            self.assertTrue(all("/" not in nazwa for nazwa in archiwum.namelist()))
        with self.assertRaisesRegex(ValueError, "już istnieją"):
            p.spakuj(self.root, stan, "123456")
        p.spakuj(self.root, stan, "123456", zastap=True)
        self.assertEqual(len(list((self.root / "outputs").iterdir())), 2)

    def test_niepoprawny_json_duplikaty_kluczy_i_tablica(self):
        for tresc in ('{', '{"nickname":"A", "nickname":"B"}', '[]', '{"x":NaN}'):
            with self.subTest(tresc=tresc):
                (self.root / "data" / "annotations" / "bad.json").write_text(tresc)
                self.assertTrue(p.sprawdz(self.root).bledy)

    def test_bledne_etykiety_liczby_i_nickname(self):
        self.komplet()
        plik = self.root / "data" / "annotations" / "0.json"
        dane = json.loads(plik.read_text())
        dane["0"]["label"] = "joy"
        dane["nickname"] = "Inny"
        plik.write_text(json.dumps(dane))
        stan = p.sprawdz(self.root)
        self.assertFalse(stan.gotowy)
        self.assertEqual(stan.liczby["happiness"], 9)
        self.assertTrue(any("etykieta" in blad for blad in stan.bledy))
        self.assertTrue(any("nickname" in blad for blad in stan.bledy))
        with self.assertRaises(ValueError):
            p.spakuj(self.root, stan, "123")
        self.assertFalse(list((self.root / "outputs").iterdir()))

    def test_nakladanie_takze_miedzy_eksportami(self):
        self.eksport(fragmenty={"1": {"startTime": "1", "endTime": "3", "label": "happiness"}, "9": {"startTime": "2", "endTime": "4", "label": "fear"}})
        self.eksport("drugi.json", fragmenty={"0": {"startTime": "3.5", "endTime": "5", "label": "anger"}})
        stan = p.sprawdz(self.root)
        self.assertEqual(sum("Nakładanie" in blad for blad in stan.bledy), 2)
        self.assertTrue(any("aktualny eksport" in blad for blad in stan.bledy))

    def test_stykajace_sie_fragmenty_do_zaakceptowania(self):
        self.eksport(fragmenty={"0": {"startTime": "0", "endTime": "1", "label": "fear"}, "8": {"startTime": "1", "endTime": "2", "label": "anger"}})
        self.assertFalse(p.sprawdz(self.root).bledy)

    def test_czasy_i_nazwy_bez_zaokraglania(self):
        from decimal import Decimal
        self.assertEqual(p.nazwa_klipu("video_-1234", p.czas("5.100"), p.czas("6")), "video_-1234_5.10-6.00.mp4")
        for wartosc in ("1.234", "NaN", "Infinity", "-1", True, None, Decimal("0.001")):
            with self.subTest(wartosc=wartosc), self.assertRaises(ValueError):
                p.czas(wartosc)
        self.eksport(fragmenty={"0": {"startTime": "5", "endTime": "5", "label": "anger"}})
        self.assertTrue(any("większe" in blad for blad in p.sprawdz(self.root).bledy))

    def test_dlugosc_tylko_ostrzezenie_i_puste_pliki(self):
        self.eksport(fragmenty={"4": {"startTime": "0", "endTime": "8", "label": "anger"}})
        stan = p.sprawdz(self.root)
        self.assertFalse(stan.bledy)
        self.assertTrue(stan.ostrzezenia)
        (self.root / "data" / "clips" / stan.klipy[0]).touch()
        self.assertEqual(len(p.sprawdz(self.root).brakujace_klipy), 1)

    def test_inne_pliki_i_niebezpieczny_identifikator(self):
        (self.root / "data" / "annotations" / "README.md").write_text("tekst")
        self.eksport(video="../film.mp4")
        stan = p.sprawdz(self.root)
        self.assertTrue(any("README" in blad for blad in stan.bledy))
        self.assertTrue(any("videoURL" in blad for blad in stan.bledy))
        self.assertEqual(stan.klipy, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
