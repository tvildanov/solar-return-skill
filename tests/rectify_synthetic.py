#!/usr/bin/env python3
"""Synthetic check: events built from a known 'true' minute must lead rectify.py back to it."""
import datetime as dt
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "solar-return/scripts"))
import rectify as rc  # noqa: E402
import solar_return as sr  # noqa: E402

swe = sr.swe


def exact_dates(true_local, lat, lon, start_year, end_year, limit=8):
    """Dates (local) when slow planets transit the true angles, or solar arc hits them."""
    tz = true_local.tzinfo
    utc = true_local.astimezone(dt.timezone.utc)
    ang = rc.angles_at(sr.julday(utc), lat, lon)
    natal, _ = rc.prepare_events([], utc, tz)
    jb = sr.julday(utc)
    sun0 = swe.calc_ut(jb, swe.SUN, sr.FLAGS)[0][0]
    found = []
    day = dt.date(start_year, 1, 1)
    prev = {}
    while day.year < end_year and len(found) < limit:
        noon = dt.datetime.combine(day, dt.time(12), tzinfo=tz).astimezone(dt.timezone.utc)
        je = sr.julday(noon)
        for k, pid, _ in rc.SLOW[1:]:   # Saturn..Pluto
            lonp = swe.calc_ut(je, pid, sr.FLAGS)[0][0]
            for a_name in ("ASC", "MC"):
                for asp in (0, 90, 180):
                    d = rc.sep(lonp, ang[a_name]) - asp
                    key = (k, a_name, asp)
                    if key in prev and prev[key] * d < 0 and abs(d) < 0.5:
                        found.append((day, f"{k}-{asp}-{a_name}"))
                    prev[key] = d
        age = (noon - utc).total_seconds() / 86400 / rc.TROPICAL_YEAR
        arc = (swe.calc_ut(jb + age, swe.SUN, sr.FLAGS)[0][0] - sun0) % 360
        for k, lonn in natal.items():
            d = rc.sep((ang["MC"] + arc) % 360, lonn)
            key = ("arc", k)
            if key in prev and prev[key] * d < 0 and abs(d) < 0.5:
                found.append((day, f"arcMC-{k}"))
            prev[key] = d if d < 2 else 99
        day += dt.timedelta(days=5)
    return found


def main():
    tz = ZoneInfo("Europe/Moscow")
    true_local = dt.datetime(1985, 3, 12, 9, 17, tzinfo=tz)
    lat, lon = 55.7558, 37.6173
    events = exact_dates(true_local, lat, lon, 2003, 2026)
    print("events:", events)
    stated = (true_local + dt.timedelta(minutes=23)).strftime("%Y-%m-%d %H:%M")
    base, rows = rc.rectify(stated, "Europe/Moscow", lat, lon, 60, events)
    best = max(rows, key=lambda r: r["score"])
    err = (best["local"] - true_local).total_seconds() / 60
    print("true 09:17, stated", stated[-5:], "→ best", best["local"].strftime("%H:%M"), f"(error {err:+.0f} min)")
    ok = len(events) >= 4 and abs(err) <= 3
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
