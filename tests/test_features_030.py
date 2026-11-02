"""Tests for 0.3.0 features: house systems, natal aspects, degrees, house map, lunations,
launch search, report/diary generation, rectification and web data parity."""
import datetime as dt
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "solar-return/scripts"))
import solar_return as sr  # noqa: E402
import degrees  # noqa: E402
import extras  # noqa: E402
import rectify  # noqa: E402

# Synthetic, non-personal test person.
BASE = ["--birth", "1992-04-17 10:25", "--birth-tz", "Europe/Berlin", "--birth-lat", "52.52",
        "--birth-lon", "13.405", "--year", "2026", "--sr-tz", "America/New_York",
        "--sr-lat", "40.7128", "--sr-lon", "-74.006"]


def run(args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        sr.main(args)
    return buf.getvalue()


class CalculatorFeatures(unittest.TestCase):
    def test_all_house_systems_compute(self):
        j = sr.julday(dt.datetime(2026, 4, 17, 14, 11, 17, tzinfo=dt.timezone.utc))
        for code in sr.HOUSE_SYSTEMS:
            c = sr.chart(j, 40.7128, -74.006, code.encode())
            self.assertEqual(len(c["cusps"]), 12, code)

    def test_report_contains_new_sections(self):
        out = run(BASE + ["--report", "--home", "Дом|40.7128|-74.006", "--launch-house", "10",
                          "--radius-km", "100", "--place", "Берлин|52.52|13.405"])
        for marker in ("17.04.2026 10:11:17", "Год по сферам", "Королевские и разрушительные градусы",
                       "Где встретить соляр", "Рекомендация: где встретить соляр", "| Луна |", "Чек-лист"):
            self.assertIn(marker, out)
        self.assertNotIn("Солнце (соляр) — соединение — Солнце (натал)", out)

    def test_english_report_and_diary(self):
        out = run(BASE + ["--report", "--lang", "en"])
        self.assertIn("The year by area", out)
        diary = run(BASE + ["--diary"])
        self.assertIn("Нулевой градус", diary)
        self.assertEqual(diary.count("**События дня:**"), 24)

    def test_house_map_regression(self):
        out = run(BASE + ["--report"])
        for row in ("| 1 → 12 |", "| 2 → 1 |", "| 3 → 2 |", "| 4 → 3 |", "| 5 → 4 |", "| 6 → 5 |",
                    "| 7 → 6 |", "| 8 → 7 |", "| 9 → 8 |", "| 10 → 9 |", "| 11 → 10 |", "| 12 → 11 |"):
            self.assertIn(row, out)


class Degrees(unittest.TestCase):
    def test_ordinal_and_exact(self):
        scorpio_13th = 210 + 12.5   # 12°30' Scorpio = 13th degree (ordinal)
        hits = degrees.find({"x": scorpio_13th}, "ordinal")
        self.assertEqual([(h["kind"], h["degree"]) for h in hits], [("royal", 13)])
        self.assertEqual(degrees.find({"x": scorpio_13th}, "exact"), [])
        self.assertEqual(degrees.find({"x": 210 + 13.5}, "exact")[0]["kind"], "royal")
        self.assertEqual(degrees.find({"x": 180.2}, "ordinal")[0]["kind"], "destructive")  # 1st Libra


class Extras(unittest.TestCase):
    def test_lunation_and_day(self):
        sr_utc = dt.datetime(2026, 7, 10, 0, 0, tzinfo=dt.timezone.utc)
        lun = extras.lunations(sr.swe, sr.FLAGS, sr.julday, sr.from_julday,
                               sr_utc - dt.timedelta(days=12), sr_utc + dt.timedelta(days=12))
        self.assertEqual([x["kind"] for x in lun], ["full", "new"])
        self.assertEqual(lun[1]["utc"].strftime("%Y-%m-%d %H:%M"), "2026-07-14 09:43")
        self.assertEqual(extras.day_of(lun[1]["utc"], sr_utc), 5)
        self.assertEqual(extras.day_of(lun[0]["utc"], sr_utc), -11)
        self.assertEqual(extras.day_of(sr_utc - dt.timedelta(hours=1), sr_utc), -1)
        self.assertEqual(extras.day_of(sr_utc + dt.timedelta(days=11, hours=23), sr_utc), 12)

    def test_launch_search_finds_house_one_west_of_home(self):
        j = sr.julday(dt.datetime(2026, 7, 10, 3, 50, tzinfo=dt.timezone.utc))
        res = extras.launch_search(sr.chart, j, {"name": "home", "lat": 45.0, "lon": 10.0}, 1, b"P", 150)
        self.assertEqual(res["home_sun_house"], 12)
        self.assertIsNotNone(res["nearest"])
        self.assertLess(res["nearest"]["distance_km"], 30)
        self.assertAlmostEqual(res["sun_on_asc"]["lon"], 9.708, delta=0.02)
        self.assertAlmostEqual(res["boundary"]["lon"], 9.7, delta=0.05)


class Rectification(unittest.TestCase):
    def test_sensitivity_without_events(self):
        base, rows = rectify.rectify("1985-03-12 09:40", "Europe/Moscow", 55.7558, 37.6173, 30, [])
        self.assertEqual(len(rows), 61)
        text = rectify.render(base, rows, [], 30, "en")
        self.assertIn("Sensitivity", text)
        self.assertIn("hypothesis", text)

    def test_recovers_true_minute_from_events(self):
        events = [(dt.date(2005, 4, 20), "a"), (dt.date(2008, 8, 17), "b"), (dt.date(2012, 10, 5), "c"),
                  (dt.date(2015, 5, 13), "d"), (dt.date(2006, 2, 9), "e")]
        _, rows = rectify.rectify("1985-03-12 09:40", "Europe/Moscow", 55.7558, 37.6173, 60, events)
        best = max(rows, key=lambda r: r["score"])
        self.assertEqual(best["local"].strftime("%H:%M"), "09:17")


class DeepLayer(unittest.TestCase):
    def test_deep_files_complete_and_parallel(self):
        ch = ("need", "mechanism", "body", "feel", "think", "act", "react")
        for lang in ("ru", "en"):
            d = json.loads((ROOT / f"solar-return/data/deep.{lang}.json").read_text())
            self.assertEqual(len(d["signs"]), 12)
            self.assertEqual(len(d["houses"]), 12)
            self.assertEqual(len(d["house_observe"]), 12)
            for e in list(d["planets"].values()) + d["signs"] + d["houses"]:
                for c in ch:
                    self.assertTrue(e.get(c), (lang, c))
            for e in list(d["planets"].values()) + d["signs"]:
                self.assertTrue(e.get("shadow_root") and e.get("key"))
        ru = json.loads((ROOT / "solar-return/data/deep.ru.json").read_text())
        en = json.loads((ROOT / "solar-return/data/deep.en.json").read_text())
        self.assertEqual(set(ru["labels"]), set(en["labels"]))
        self.assertEqual(set(ru["planets"]), set(en["planets"]))

    def test_report_has_five_layers(self):
        out = run(BASE + ["--report", "--lang", "en"])
        for marker in ("How it works inside", "The recipe of the year", "Reactions to the world",
                       "Where the shadow comes from", "Key to yourself", "What to observe"):
            self.assertIn(marker, out)
        diary = run(BASE + ["--diary", "--lang", "en"])
        self.assertEqual(diary.count("**Body** —"), 24)


class WebParity(unittest.TestCase):
    def test_web_data_matches_skill_data(self):
        for name in ("kb.ru.json", "kb.en.json", "deep.ru.json", "deep.en.json", "degrees.json"):
            self.assertEqual((ROOT / "docs/data" / name).read_bytes(),
                             (ROOT / "solar-return/data" / name).read_bytes(), name)

    def test_kb_languages_have_same_keys(self):
        ru = json.loads((ROOT / "solar-return/data/kb.ru.json").read_text())
        en = json.loads((ROOT / "solar-return/data/kb.en.json").read_text())
        self.assertEqual(set(ru["labels"]), set(en["labels"]))
        self.assertEqual(set(ru["templates"]), set(en["templates"]))
        self.assertEqual(len(ru["signs"]), 12)
        self.assertEqual(len(en["houses"]), 12)
        self.assertTrue(all("observe" in h for h in ru["houses"] + en["houses"]))


if __name__ == "__main__":
    unittest.main()
