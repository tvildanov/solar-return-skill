#!/usr/bin/env python3
"""Independent cross-check of the calculator against Astropy/ERFA (no Swiss Ephemeris).

Optional: requires `pip install astropy`. Compares, for several test charts:
- the solar-return instant (independent root finding on the Sun's apparent longitude);
- the solar-return Ascendant and MC (formula from apparent sidereal time and true obliquity);
- Sun and Moon apparent longitudes at the solar-return instant.
Run:  python3 tests/independent_check.py
"""
import datetime as dt
import math
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import astropy.units as u
from astropy.coordinates import GeocentricTrueEcliptic, get_body
from astropy.time import Time
import erfa

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "solar-return/scripts"))
import solar_return as sr  # noqa: E402

CASES = [  # birth local, birth zone, birth lat/lon, year, return lat/lon
    ("1992-04-17 10:25", "Europe/Berlin", 52.5200, 13.4050, 2026, 40.7128, -74.0060),
    ("1990-05-21 14:30", "Europe/Moscow", 55.7558, 37.6173, 2026, 40.7128, -74.0060),
    ("1984-02-29 08:00", "Europe/Berlin", 52.5200, 13.4050, 2027, -33.8688, 151.2093),
    ("2001-07-04 23:45", "America/Los_Angeles", 34.0522, -118.2437, 2026, 35.6762, 139.6503),
    ("1975-12-31 00:10", "Asia/Tashkent", 41.2995, 69.2401, 2025, 51.5072, -0.1276),
]


def sun_lon(t: Time) -> float:
    return get_body("sun", t).transform_to(GeocentricTrueEcliptic(equinox=t)).lon.deg


def moon_lon(t: Time) -> float:
    return get_body("moon", t).transform_to(GeocentricTrueEcliptic(equinox=t)).lon.deg


def angles(t: Time, lat: float, lon: float):
    gast = t.sidereal_time("apparent", longitude=0 * u.deg).deg
    ramc = math.radians((gast + lon) % 360)
    eps = erfa.obl06(t.tt.jd1, t.tt.jd2) + erfa.nut06a(t.tt.jd1, t.tt.jd2)[1]
    phi = math.radians(lat)
    mc = math.degrees(math.atan2(math.sin(ramc), math.cos(ramc) * math.cos(eps))) % 360
    asc = math.degrees(math.atan2(math.cos(ramc),
                                  -(math.sin(ramc) * math.cos(eps) + math.tan(phi) * math.sin(eps)))) % 360
    return asc, mc


def wrap(d: float) -> float:
    return (d + 180) % 360 - 180


def main():
    worst = {"time_s": 0, "asc_arcmin": 0, "mc_arcmin": 0, "moon_arcmin": 0}
    for birth, zone, blat, blon, year, rlat, rlon in CASES:
        b_local = dt.datetime.strptime(birth, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(zone))
        b_utc = b_local.astimezone(dt.timezone.utc)
        target = sun_lon(Time(b_utc))
        # independent solar return: Newton on Astropy Sun (≈0.9856°/day)
        t = Time(dt.datetime(year, b_local.month, min(b_local.day, 28), 12, tzinfo=dt.timezone.utc))
        for _ in range(20):
            d = wrap(target - sun_lon(t))
            t = t + (d / 0.98565) * u.day
            if abs(d) < 1e-7:
                break
        ours_natal = sr.chart(sr.julday(b_utc), blat, blon)
        ours_t = sr.solar_return_moment(ours_natal["bodies"]["sun"]["lon"], year, b_local)
        ours = sr.chart(sr.julday(ours_t), rlat, rlon)
        dt_s = (ours_t - t.to_datetime(timezone=dt.timezone.utc)).total_seconds()
        a_asc, a_mc = angles(Time(ours_t), rlat, rlon)
        res = {"time_s": abs(dt_s),
               "asc_arcmin": abs(wrap(ours["asc"] - a_asc)) * 60,
               "mc_arcmin": abs(wrap(ours["mc"] - a_mc)) * 60,
               "moon_arcmin": abs(wrap(ours["bodies"]["moon"]["lon"] - moon_lon(Time(ours_t)))) * 60}
        for k, v in res.items():
            worst[k] = max(worst[k], v)
        print(f"{birth} {zone} → {year}: Δt={dt_s:+.1f}s  ΔASC={res['asc_arcmin']:.2f}′  "
              f"ΔMC={res['mc_arcmin']:.2f}′  ΔMoon={res['moon_arcmin']:.2f}′")
    print("worst:", {k: round(v, 2) for k, v in worst.items()})
    ok = worst["time_s"] < 60 and worst["asc_arcmin"] < 2 and worst["mc_arcmin"] < 2 and worst["moon_arcmin"] < 2
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
