"""Synthetic-data regression tests; no personal birth records or external services."""
import datetime as dt
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "solar-return/scripts/solar_return.py"
spec = importlib.util.spec_from_file_location("solar_return", SCRIPT)
sr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sr)
UTC = dt.timezone.utc
BASE = ["--birth", "1990-05-21 14:30", "--birth-tz", "Europe/Moscow",
        "--birth-lat", "55.7558", "--birth-lon", "37.6173", "--year", "2026",
        "--sr-tz", "America/New_York", "--sr-lat", "40.7128", "--sr-lon", "-74.0060",
        "--lang", "en"]


def cli(*extra):
    return subprocess.run([sys.executable, str(SCRIPT), *BASE, *extra],
                          text=True, capture_output=True, check=False)


class FormattingTests(unittest.TestCase):
    def test_sign_rollover(self):
        self.assertEqual(sr.fmt_lon(29.9999, "en"), "0°00' Taurus")

    def test_zodiac_rollover(self):
        self.assertEqual(sr.fmt_lon(359.9999, "en"), "0°00' Aries")
        self.assertEqual(sr.fmt_lon(360, "en"), "0°00' Aries")
        self.assertEqual(sr.fmt_lon(-0.0001, "en"), "0°00' Aries")

    def test_regular_longitude(self):
        self.assertEqual(sr.fmt_lon(42.5, "en"), "12°30' Taurus")
        self.assertEqual(sr.fmt_lon(42.5, "ru"), "12°30' Телец")

    def test_rounding_preserves_ambiguous_instant(self):
        ny = ZoneInfo("America/New_York")
        before_fold = dt.datetime(2021, 11, 7, 5, 59, 40, tzinfo=UTC).astimezone(ny)
        self.assertEqual(sr.rmin(before_fold).astimezone(UTC),
                         dt.datetime(2021, 11, 7, 6, tzinfo=UTC))

    def test_rounding_never_creates_spring_gap(self):
        ny = ZoneInfo("America/New_York")
        before_gap = dt.datetime(2021, 3, 14, 6, 59, 40, tzinfo=UTC).astimezone(ny)
        rounded = sr.rmin(before_gap)
        self.assertEqual(rounded.hour, 3)
        self.assertEqual(rounded.astimezone(UTC), dt.datetime(2021, 3, 14, 7, tzinfo=UTC))


class TimeZoneTests(unittest.TestCase):
    def test_gap_rejected(self):
        for fold in (None, 0, 1):
            with self.subTest(fold=fold), self.assertRaisesRegex(ValueError, "does not exist"):
                sr.localize_birth("2021-03-14 02:30", "America/New_York", fold)

    def test_ambiguous_requires_fold(self):
        with self.assertRaisesRegex(ValueError, "ambiguous.*birth-fold"):
            sr.localize_birth("2021-11-07 01:30", "America/New_York")

    def test_fold_selects_two_instants(self):
        first = sr.localize_birth("2021-11-07 01:30", "America/New_York", 0)
        second = sr.localize_birth("2021-11-07 01:30", "America/New_York", 1)
        self.assertEqual(first.astimezone(UTC), dt.datetime(2021, 11, 7, 5, 30, tzinfo=UTC))
        self.assertEqual(second.astimezone(UTC), dt.datetime(2021, 11, 7, 6, 30, tzinfo=UTC))

    def test_normal_time_and_invalid_fold(self):
        normal = sr.localize_birth("2000-01-01 12:00", "Etc/UTC")
        self.assertEqual(normal.utcoffset(), dt.timedelta(0))
        with self.assertRaisesRegex(ValueError, "fold"):
            sr.localize_birth("2000-01-01 12:00", "Etc/UTC", 9)

    def test_half_hour_gap_and_dateline_skip(self):
        for value, zone in [("2021-10-03 02:15", "Australia/Lord_Howe"),
                            ("2011-12-30 12:00", "Pacific/Apia")]:
            with self.subTest(zone=zone), self.assertRaisesRegex(ValueError, "does not exist"):
                sr.localize_birth(value, zone)


class CalendarTests(unittest.TestCase):
    def test_exact_utc_days_across_dst(self):
        for moment in (dt.datetime(2026, 3, 8, 7, 30, tzinfo=UTC),
                       dt.datetime(2026, 11, 1, 6, 30, tzinfo=UTC)):
            days = sr.day_calendar(moment, ZoneInfo("America/New_York"))
            self.assertEqual(len(days), 24)
            self.assertEqual([d["day"] for d in days], list(range(-12, 0)) + list(range(1, 13)))
            self.assertEqual([d["house"] for d in days], list(range(12, 0, -1)) + list(range(1, 13)))
            previous = None
            for d in days:
                start = dt.datetime.fromisoformat(d["start"]).astimezone(UTC)
                end = dt.datetime.fromisoformat(d["end"]).astimezone(UTC)
                self.assertEqual((end - start).total_seconds(), 86400)
                if previous is not None:
                    self.assertEqual(start, previous)
                previous = end
            self.assertEqual(dt.datetime.fromisoformat(days[12]["start"]).astimezone(UTC), moment)


class CalculationTests(unittest.TestCase):
    def test_return_invariant_and_leap_day(self):
        # Internal agreement only: this is NOT independent astronomical validation.
        for birth, year in [("1990-05-21 14:30", 2026),
                            ("2000-02-29 12:00", 2027),
                            ("1980-03-20 12:00", 2026)]:
            with self.subTest(birth=birth):
                local = sr.localize_birth(birth, "Etc/UTC")
                natal_sun = sr.swe.calc_ut(sr.julday(local), sr.swe.SUN, sr.FLAGS)[0][0]
                result = sr.solar_return_moment(natal_sun, year, local)
                result_sun = sr.swe.calc_ut(sr.julday(result), sr.swe.SUN, sr.FLAGS)[0][0]
                residual = abs((result_sun - natal_sun + 180) % 360 - 180)
                self.assertLess(residual, 0.00001)
                self.assertEqual(result.year, year)

    def test_polar_houses_never_silently_fallback(self):
        j = sr.julday(dt.datetime(2026, 5, 21, 12, tzinfo=UTC))
        with self.assertRaisesRegex(ValueError, "house.*(polar|high latitude)"):
            sr.chart(j, 78.2232, 15.6469, b"P")
        whole = sr.chart(j, 78.2232, 15.6469, b"W")
        self.assertEqual(len(whole["cusps"]), 12)

    def test_supported_house_systems(self):
        j = sr.julday(dt.datetime(2026, 5, 21, 12, tzinfo=UTC))
        for system in (b"P", b"K", b"W"):
            with self.subTest(system=system):
                self.assertEqual(len(sr.chart(j, 40.7128, -74.0060, system)["cusps"]), 12)

    def test_nonconvergence_is_error(self):
        local = dt.datetime(2000, 1, 1, tzinfo=UTC)
        with mock.patch.object(sr.swe, "calc_ut", return_value=((10, 0, 0, 1, 0, 0), 0)):
            with self.assertRaisesRegex(ValueError, "converge"):
                sr.solar_return_moment(20, 2026, local)


class CLITests(unittest.TestCase):
    def test_success_json_and_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "result.json"
            result = cli("--json", str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(data["days"]), 24)
            self.assertEqual(data["metadata"]["calculator_version"], "0.3.0")
            self.assertEqual(data["metadata"]["ephemeris"], "Moshier (Swiss Ephemeris)")
            self.assertEqual(data["metadata"]["house_system"], "P")
            self.assertIn("tzdata_package_version", data["metadata"])
            self.assertIn("timezone_sources", data["metadata"])
            self.assertIn("SOLAR RETURN MOMENT", result.stdout)
            if os.name == "posix":
                self.assertEqual(output.stat().st_mode & 0o777, 0o600)

    def test_json_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "result.json"
            output.write_text("DO NOT REPLACE", encoding="utf-8")
            result = cli("--json", str(output))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("overwrite", result.stderr)
            self.assertEqual(output.read_text(), "DO NOT REPLACE")

    def test_json_refuses_symlink(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unsupported")
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "important.txt"
            target.write_text("KEEP", encoding="utf-8")
            link = Path(temp) / "report.json"
            link.symlink_to(target)
            result = cli("--json", str(link))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_text(), "KEEP")

    def test_bad_inputs_are_actionable_without_tracebacks(self):
        cases = [("--birth-lat", "nan"), ("--sr-lon", "inf"),
                 ("--birth-lat", "90"), ("--sr-lat", "-91"),
                 ("--birth-lon", "181"), ("--year", "3000"),
                 ("--year", "1"), ("--year", "nope"),
                 ("--house-system", "G"), ("--birth-fold", "2"),
                 ("--birth", "not-a-date"), ("--birth-tz", "Invalid/Zone"),
                 ("--sr-tz", "Invalid/Zone"), ("--extra-tz", "Invalid/Zone"),
                 ("--birth", "3000-01-01 12:00")]
        for args in cases:
            with self.subTest(args=args):
                result = cli(*args)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn("error:", result.stderr)

    def test_cli_dst_gap_and_fold(self):
        gap = cli("--birth", "2021-03-14 02:30", "--birth-tz", "America/New_York")
        self.assertEqual(gap.returncode, 2)
        self.assertIn("does not exist", gap.stderr)
        ambiguous = cli("--birth", "2021-11-07 01:30", "--birth-tz", "America/New_York")
        self.assertEqual(ambiguous.returncode, 2)
        self.assertIn("--birth-fold", ambiguous.stderr)
        selected = cli("--birth", "2021-11-07 01:30", "--birth-tz", "America/New_York",
                       "--birth-fold", "1")
        self.assertEqual(selected.returncode, 0, selected.stderr)

    def test_version(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--version"],
                                text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0.3.0", result.stdout)
        self.assertEqual(sr.VERSION, (ROOT / "solar-return/VERSION").read_text().strip())


if __name__ == "__main__":
    unittest.main()
