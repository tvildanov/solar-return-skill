"""Offline regressions against recorded synthetic JPL Sun cases, not all bodies."""
import datetime as dt
import json
from pathlib import Path
import unittest
from test_calculator import sr

CASES = json.loads((Path(__file__).parent / 'fixtures/jpl_sun_cases.json').read_text())['cases']


class RecordedSunReferenceTests(unittest.TestCase):
    def test_recorded_jpl_sun_cases_with_documented_timescale_tolerance(self):
        for case in CASES:
            with self.subTest(case=case['label']):
                local = sr.localize_birth(case['birth_local'], case['birth_tz'])
                natal_sun = sr.swe.calc_ut(sr.julday(local.astimezone(dt.timezone.utc)), sr.swe.SUN, sr.FLAGS)[0][0]
                result = sr.solar_return_moment(natal_sun, case['requested_year'], local)
                reference = dt.datetime.fromisoformat(case['jpl_return_interpolated_utc'])
                tolerance = {'historical': 6.0, 'future': 20.0}.get(case['label'], 2.0)
                self.assertLess(abs((result-reference).total_seconds()), tolerance)

    def test_anniversary_semantics_allow_adjacent_calendar_year(self):
        for label, actual_year in [('jan1', 2025), ('dec31', 2028)]:
            case = next(x for x in CASES if x['label'] == label)
            local = sr.localize_birth(case['birth_local'], case['birth_tz'])
            natal_sun = sr.swe.calc_ut(sr.julday(local), sr.swe.SUN, sr.FLAGS)[0][0]
            result = sr.solar_return_moment(natal_sun, case['requested_year'], local)
            self.assertEqual(result.year, actual_year)
            self.assertNotEqual(result.year, case['requested_year'])


if __name__ == '__main__':
    unittest.main()
