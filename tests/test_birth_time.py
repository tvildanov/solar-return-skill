"""Synthetic regression tests for birth-time uncertainty, not validation of astrology."""
import datetime as dt
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "solar-return/scripts"))
import rectify

UTC = dt.timezone.utc


class BirthTimeTests(unittest.TestCase):
    def test_spring_window_has_no_nonexistent_wall_times_or_duplicate_instants(self):
        _, rows = rectify.rectify("2021-03-14 01:50", "America/New_York", 40.7, -74, 30, [])
        instants = [r["local"].astimezone(UTC) for r in rows]
        self.assertTrue(all(b - a == dt.timedelta(minutes=1) for a, b in zip(instants, instants[1:])))
        self.assertFalse(any(r["local"].hour == 2 for r in rows))

    def test_fall_window_preserves_chosen_fold(self):
        for fold in (0, 1):
            base, rows = rectify.rectify("2021-11-07 01:30", "America/New_York", 40.7, -74, 40, [], fold=fold)
            center = next(r for r in rows if r["offset"] == 0)
            self.assertEqual(center["local"].astimezone(UTC), base.astimezone(UTC))
            self.assertEqual(center["local"].fold, fold)
            instants = [r["local"].astimezone(UTC) for r in rows]
            self.assertTrue(all(b - a == dt.timedelta(minutes=1) for a, b in zip(instants, instants[1:])))

    def test_duplicate_event_dates_rejected(self):
        events = [(dt.date(2010, 1, 1), "A"), (dt.date(2010, 1, 1), "B")]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            rectify.rectify("1990-01-01 12:00", "UTC", 40.7, -74, 30, events)

    def test_event_before_birth_rejected(self):
        with self.assertRaisesRegex(ValueError, "after"):
            rectify.rectify("1990-01-01 12:00", "UTC", 40.7, -74, 30,
                            [(dt.date(1989, 12, 31), "A")])

    def test_zero_scores_do_not_select_an_arbitrary_minute(self):
        base, rows = rectify.rectify("1990-01-01 12:00", "UTC", 40.7, -74, 1, [])
        for lang, marker in (("en", "No candidate is supported"), ("ru", "Ни один вариант не выделен")):
            text = rectify.render(base, rows, [(dt.date(2010, 1, 1), "A")], 1, lang)
            self.assertIn(marker, text)
            self.assertNotIn("Most likely", text)
            self.assertNotIn("Наиболее вероятное", text)

    def test_report_disclaims_probability_and_shows_offset(self):
        base, rows = rectify.rectify("2021-11-07 01:30", "America/New_York", 40.7, -74, 40, [], fold=1)
        text = rectify.render(base, rows, [], 40, "en")
        self.assertIn("not a probability", text)
        self.assertIn("-0500", text)

    def test_positive_tie_does_not_select_a_unique_time(self):
        base, rows = rectify.rectify("1990-01-01 12:00", "UTC", 40.7, -74, 1, [])
        for row in rows:
            row["score"] = 1.0
        text = rectify.render(base, rows, [(dt.date(2010, 1, 1), "A")], 1, "en")
        self.assertIn("close or tied", text)
        self.assertNotIn("**Top score", text)

    def test_invalid_windows_fail_in_api(self):
        for window in (-1, 0, 721, 1.5, True):
            with self.subTest(window=window), self.assertRaisesRegex(ValueError, "window"):
                rectify.rectify("1990-01-01 12:00", "UTC", 40.7, -74, window, [])

    def test_skipped_event_date_is_not_silently_shifted(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            rectify.rectify("1990-01-01 12:00", "Pacific/Apia", -13.8, -171.8, 10,
                            [(dt.date(2011, 12, 30), "A")])

    def test_event_outside_supported_range_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Event year"):
            rectify.rectify("1990-01-01 12:00", "UTC", 40.7, -74, 10,
                            [(dt.date(3000, 1, 1), "A")])


if __name__ == "__main__":
    unittest.main()
