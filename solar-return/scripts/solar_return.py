#!/usr/bin/env python3
# Solar Return calculator — part of the "solar-return" skill.
# Copyright (C) 2026 AstroEmpathy contributors
# Licensed under the GNU Affero General Public License v3.0 (see LICENSE).
# Uses the Swiss Ephemeris via pyswisseph (AGPL), (c) Astrodienst AG.
# Modified 2026-10-30 for distribution version 0.2.1: input/DST validation,
# safe report creation, rounding fixes, explicit errors and provenance metadata.
# Version metadata updated 2026-10-31 for 0.2.2.
# Modified 2026-11-01 for 0.3.0: all Swiss Ephemeris house systems, solar-to-natal
# aspects, autonomous Markdown report from the bundled knowledge base.
# Upstream: https://github.com/tvildanov/solar-return-skill
"""
Calculate a solar return (the exact moment the Sun returns to its natal
longitude), the solar-return chart for the place where it is met, and the
24-day calendar (12 days closing the old year + 12 days opening the new one).

Example:
  python3 solar_return.py \
    --birth "1990-05-21 14:30" --birth-tz Europe/Moscow \
    --birth-lat 55.7558 --birth-lon 37.6173 \
    --year 2026 \
    --sr-tz America/New_York --sr-lat 40.7128 --sr-lon -74.0060 \
    --lang ru --json out.json

Latitude: north positive. Longitude: east positive, west negative.
Time zones are IANA names (Europe/Moscow, America/Cancun, Asia/Tashkent ...);
historical daylight-saving rules are applied automatically.
"""
import argparse
import datetime as dt
from importlib import metadata as import_metadata
import json
import math
import os
from pathlib import Path
import platform
import sys
import zoneinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    import swisseph as swe
except ImportError:
    sys.exit("pyswisseph is not installed. Create a virtual environment, then run\n"
             "python -m pip install -r requirements.txt inside it. See INSTALL.md.")

FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED   # built-in Moshier ephemeris, no data files needed
VERSION = "0.4.0"
MIN_YEAR, MAX_YEAR = 2, 2999
HOUSE_SYSTEMS = {
    "P": "Placidus", "K": "Koch", "O": "Porphyry", "R": "Regiomontanus", "C": "Campanus",
    "E": "Equal (Ascendant)", "D": "Equal (MC)", "W": "Whole Sign", "N": "Equal (0° Aries)",
    "B": "Alcabitius", "M": "Morinus", "T": "Polich/Page (Topocentric)", "V": "Vehlow equal",
    "X": "Axial rotation / Meridian", "H": "Horizon / Azimuthal", "S": "Sripati",
}
NATAL_POINTS = ("asc", "mc")


def load_time_zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"Unknown or unavailable IANA time zone {name!r}; "
                         "check its spelling and install the pinned tzdata dependency.") from exc


def localize_birth(value: str, zone_name: str, fold=None) -> dt.datetime:
    """Validate a wall time by roundtripping each possible fold through UTC."""
    if fold not in (None, 0, 1):
        raise ValueError("birth fold must be 0 or 1")
    try:
        naive = dt.datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise ValueError('Birth date must be a valid date/time in "YYYY-MM-DD HH:MM" format.') from exc
    if not MIN_YEAR <= naive.year <= MAX_YEAR:
        raise ValueError(f"Birth year must be between {MIN_YEAR} and {MAX_YEAR}.")
    zone = load_time_zone(zone_name)
    valid = {}
    for candidate_fold in (0, 1):
        candidate = naive.replace(tzinfo=zone, fold=candidate_fold)
        restored = candidate.astimezone(dt.timezone.utc).astimezone(zone)
        if restored.replace(tzinfo=None) == naive:
            valid[candidate_fold] = candidate
    if not valid:
        raise ValueError(f"Birth time {value} does not exist in {zone_name} because of "
                         "a clock transition. Check the recorded local time; it was not shifted automatically.")
    ambiguous = len({x.utcoffset() for x in valid.values()}) > 1
    if ambiguous and fold is None:
        raise ValueError(f"Birth time {value} is ambiguous in {zone_name}; specify "
                         "--birth-fold 0 for the earlier occurrence or --birth-fold 1 for the later one.")
    return valid[fold if fold is not None else 0]


def coordinate(value: str, *, latitude: bool) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("coordinate must be a number") from exc
    limit = 90 if latitude else 180
    valid = (-limit < number < limit) if latitude else (-limit <= number <= limit)
    if not math.isfinite(number) or not valid:
        domain = "strictly between -90 and 90 (exact poles unsupported)" if latitude else "between -180 and 180"
        raise argparse.ArgumentTypeError(f"coordinate must be finite and {domain}")
    return number


def supported_year(value: str) -> int:
    try:
        year = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("year must be an integer") from exc
    if not MIN_YEAR <= year <= MAX_YEAR:
        raise argparse.ArgumentTypeError(f"year must be between {MIN_YEAR} and {MAX_YEAR}")
    return year


def package_version(name: str) -> str:
    try:
        return import_metadata.version(name)
    except import_metadata.PackageNotFoundError:
        return "not installed / unavailable"


def provenance(args) -> dict:
    sources = {}
    for key in dict.fromkeys([args.birth_tz, args.sr_tz, *args.extra_tz]):
        # ZoneInfo has already validated the keys. Its documented search order
        # checks system TZPATH first, then the separately installed tzdata package.
        sources[key] = "tzdata package"
        for root in zoneinfo.TZPATH:
            if (Path(root) / key).is_file():
                sources[key] = "system IANA database (version not determined)"
                break
    return {
        "calculator_version": VERSION,
        "python_version": platform.python_version(),
        "pyswisseph_version": package_version("pyswisseph"),
        "swiss_ephemeris_version": str(swe.version),
        "ephemeris": "Moshier (Swiss Ephemeris)",
        "ephemeris_flags": FLAGS,
        "coordinate_frame": "geocentric tropical ecliptic longitude",
        "house_system": args.house_system,
        "house_assignment": "longitude relative to house cusps; latitude ignored",
        "tzdata_package_version": package_version("tzdata"),
        "timezone_sources": sources,
        "timezone_source_note": "System TZPATH takes precedence when available. PYTHONTZPATH='' selects installed tzdata.",
        "calendar_interval_seconds": 86400,
        "solar_return_time_rounding": "nearest second; human local display nearest minute",
        "supported_years": [MIN_YEAR, MAX_YEAR],
        "year_semantics": "birthday anniversary year; nearest return may occur in adjacent calendar year",
        "calendar": "proleptic Gregorian",
        "time_scale_note": "UTC is approximated as UT1 for calc_ut; no explicit DUT1 correction. Historical/future time-scale uncertainty applies.",
        "interpretation": "Astrological reflection, not scientifically validated prediction.",
    }


def write_json_exclusive(filename: str, data: dict) -> None:
    """Create a private report only; never follow or replace an existing path."""
    try:
        fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError(f"Refusing to overwrite existing JSON path {filename!r}; choose a new filename.") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        json.dump(data, output, ensure_ascii=False, indent=2, allow_nan=False)
        output.write("\n")

SIGNS = {
    "ru": ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы",
           "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"],
    "en": ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
           "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
}
BODIES = [
    ("sun", swe.SUN, "Солнце", "Sun"), ("moon", swe.MOON, "Луна", "Moon"),
    ("mercury", swe.MERCURY, "Меркурий", "Mercury"), ("venus", swe.VENUS, "Венера", "Venus"),
    ("mars", swe.MARS, "Марс", "Mars"), ("jupiter", swe.JUPITER, "Юпитер", "Jupiter"),
    ("saturn", swe.SATURN, "Сатурн", "Saturn"), ("uranus", swe.URANUS, "Уран", "Uranus"),
    ("neptune", swe.NEPTUNE, "Нептун", "Neptune"), ("pluto", swe.PLUTO, "Плутон", "Pluto"),
    ("node", swe.TRUE_NODE, "Сев. узел", "North Node"),
]
ASPECTS = [(0, "conjunction", "соединение", 8), (60, "sextile", "секстиль", 5),
           (90, "square", "квадрат", 7), (120, "trine", "трин", 7),
           (180, "opposition", "оппозиция", 8)]


def julday(utc: dt.datetime) -> float:
    return swe.julday(utc.year, utc.month, utc.day,
                      utc.hour + utc.minute / 60 + utc.second / 3600)


def from_julday(j: float) -> dt.datetime:
    y, m, d, h = swe.revjul(j)
    return dt.datetime(y, m, d, tzinfo=dt.timezone.utc) + dt.timedelta(seconds=round(h * 3600))


def rmin(t: dt.datetime) -> dt.datetime:
    """Round the instant, not a local wall clock that may cross a DST gap/fold."""
    zone = t.tzinfo
    base = t.astimezone(dt.timezone.utc) if zone is not None else t
    rounded = (base + dt.timedelta(seconds=30)).replace(second=0, microsecond=0)
    return rounded.astimezone(zone) if zone is not None else rounded


def fmt_lon(lon: float, lang: str) -> str:
    if not math.isfinite(lon):
        raise ValueError("longitude must be finite")
    # Round the entire circle before splitting into sign/degree/minute, so
    # rounding 29°59'59\" correctly advances to 0°00' of the following sign.
    arcminutes = int(math.floor((lon % 360) * 60 + 0.5)) % (360 * 60)
    s, remainder = divmod(arcminutes, 30 * 60)
    d, m = divmod(remainder, 60)
    return f"{d}°{m:02d}' {SIGNS[lang][s]}"


def house_of(lon: float, cusps) -> int:
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360 < (b - a) % 360:
            return i + 1
    return 12


def chart(j: float, lat: float, lon: float, hsys: bytes = b"P") -> dict:
    if hsys not in tuple(x.encode("ascii") for x in HOUSE_SYSTEMS):
        raise ValueError("Unsupported house system; choose one of: " + ", ".join(HOUSE_SYSTEMS))
    try:
        cusps, ascmc = swe.houses(j, lat, lon, hsys)
    except swe.Error as exc:
        raise ValueError(f"Cannot calculate {HOUSE_SYSTEMS[hsys.decode()]} houses at this location/time. "
                         "Placidus/Koch can fail at high latitude or polar locations. "
                         "No alternative was substituted; explicitly choose --house-system W if appropriate.") from exc
    out = {"asc": ascmc[0], "mc": ascmc[1], "cusps": list(cusps), "bodies": {}}
    for key, pid, _, _ in BODIES:
        r = swe.calc_ut(j, pid, FLAGS)[0]
        out["bodies"][key] = {"lon": r[0], "speed": r[3], "retro": r[3] < 0,
                              "house": house_of(r[0], cusps)}
    return out


def aspects(bodies: dict) -> list:
    keys = [k for k in bodies if k != "node"]
    res = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            d = abs(bodies[a]["lon"] - bodies[b]["lon"]) % 360
            d = min(d, 360 - d)
            for ang, en, ru, orb in ASPECTS:
                o = orb if ("sun" in (a, b) or "moon" in (a, b)) else orb - 2
                if abs(d - ang) <= o:
                    res.append({"a": a, "b": b, "aspect": en, "aspect_ru": ru,
                                "orb": round(abs(d - ang), 2)})
    return sorted(res, key=lambda x: x["orb"])


def natal_aspects(solar_bodies: dict, natal: dict, orb: float) -> list:
    """Aspects from solar-return bodies to natal bodies and natal ASC/MC within one orb."""
    targets = {k: v["lon"] for k, v in natal["bodies"].items() if k != "node"}
    targets.update({"asc": natal["asc"], "mc": natal["mc"]})
    res = []
    for a, body in solar_bodies.items():
        if a == "node":
            continue
        for b, lon in targets.items():
            d = abs(body["lon"] - lon) % 360
            d = min(d, 360 - d)
            for ang, en, ru, _ in ASPECTS:
                if abs(d - ang) <= orb:
                    res.append({"solar": a, "natal": b, "aspect": en, "aspect_ru": ru,
                                "orb": round(abs(d - ang), 2)})
    return sorted(res, key=lambda x: x["orb"])


def solar_return_moment(natal_sun: float, year: int, birth_local: dt.datetime) -> dt.datetime:
    # Start near the birthday in the requested year and refine with Newton's method.
    try:
        guess = dt.datetime(year, birth_local.month, birth_local.day, 12, tzinfo=dt.timezone.utc)
    except ValueError:  # Feb 29 in a non-leap year
        guess = dt.datetime(year, 3, 1, 12, tzinfo=dt.timezone.utc)
    j = julday(guess)
    for _ in range(50):
        s = swe.calc_ut(j, swe.SUN, FLAGS)[0]
        diff = ((natal_sun - s[0] + 180) % 360) - 180
        if not math.isfinite(diff) or not math.isfinite(s[3]) or abs(s[3]) < 1e-12:
            raise ValueError("Solar-return solver received invalid longitude/speed.")
        j += diff / s[3]
        if abs(diff) < 1e-9:
            break
    else:
        raise ValueError("Solar-return calculation did not converge; no result was reported.")
    return from_julday(j)


def day_calendar(sr_utc: dt.datetime, tz: ZoneInfo) -> list:
    days = []
    for k in range(12, 0, -1):
        start = sr_utc - dt.timedelta(days=k)
        days.append({"day": -k, "house": k, "phase": "closing",
                     "start": start.astimezone(tz).isoformat(),
                     "end": (start + dt.timedelta(days=1)).astimezone(tz).isoformat()})
    for k in range(1, 13):
        start = sr_utc + dt.timedelta(days=k - 1)
        days.append({"day": k, "house": k, "phase": "opening",
                     "start": start.astimezone(tz).isoformat(),
                     "end": (start + dt.timedelta(days=1)).astimezone(tz).isoformat()})
    return days


def main(argv=None):
    p = argparse.ArgumentParser(description="Solar return calculator (Swiss Ephemeris)")
    p.add_argument("--version", action="version", version=f"solar-return {VERSION}")
    p.add_argument("--birth", required=True, help='local birth time "YYYY-MM-DD HH:MM"')
    p.add_argument("--birth-tz", required=True, help="IANA time zone of the birthplace")
    p.add_argument("--birth-fold", type=int, choices=(0, 1),
                   help="required only for repeated local times: 0=earlier occurrence, 1=later")
    p.add_argument("--birth-lat", type=lambda x: coordinate(x, latitude=True), required=True)
    p.add_argument("--birth-lon", type=lambda x: coordinate(x, latitude=False), required=True)
    p.add_argument("--year", type=supported_year, required=True,
                   help=f"birthday anniversary year ({MIN_YEAR}–{MAX_YEAR}); return may fall in adjacent calendar year")
    p.add_argument("--sr-tz", required=True, help="IANA time zone where the return is met")
    p.add_argument("--sr-lat", type=lambda x: coordinate(x, latitude=True), required=True)
    p.add_argument("--sr-lon", type=lambda x: coordinate(x, latitude=False), required=True)
    p.add_argument("--extra-tz", action="append", default=[],
                   help="extra time zones to show the moment in (repeatable)")
    p.add_argument("--house-system", default="P", choices=tuple(HOUSE_SYSTEMS),
                   help="P=Placidus (default), K=Koch, W=Whole Sign, E=Equal, R=Regiomontanus, "
                        "C=Campanus, O=Porphyry ... (see HOUSE_SYSTEMS); no automatic fallback")
    p.add_argument("--natal-orb", type=float, default=1.0,
                   help="orb in degrees for solar-return-to-natal aspects (default 1.0)")
    p.add_argument("--report", action="store_true",
                   help="print a full Markdown report built from the bundled knowledge base instead of tables")
    p.add_argument("--degree-convention", choices=("ordinal", "exact"), default="ordinal",
                   help="how royal/destructive degree numbers map to longitude (default ordinal)")
    p.add_argument("--place", action="append", default=[], metavar="NAME|LAT|LON",
                   help="compare the solar-return chart at another place (repeatable)")
    p.add_argument("--scan-lat", type=lambda x: coordinate(x, latitude=True),
                   help="scan longitudes along this latitude (use with --goal-house)")
    p.add_argument("--goal-house", type=int, choices=range(1, 13),
                   help="house wanted for the solar-return Sun when scanning longitudes")
    p.add_argument("--home", metavar="NAME|LAT|LON",
                   help="home point for the launch recommendation (nearest place meeting --launch-house)")
    p.add_argument("--launch-house", type=int, choices=range(1, 13), default=1,
                   help="house wanted for the SR Sun in the launch recommendation (default 1)")
    p.add_argument("--radius-km", type=float, default=300.0,
                   help="search radius around --home in km (default 300)")
    p.add_argument("--diary", action="store_true",
                   help="print a printable Markdown observation diary for the 24 days")
    p.add_argument("--lang", choices=["ru", "en"], default="ru")
    p.add_argument("--json", help="create a new private JSON file containing birth/location inputs; never overwrite")
    a = p.parse_args(argv)

    try:
        run(a)
    except (ValueError, OSError, OverflowError, swe.Error) as exc:
        p.error(str(exc))


def run(a):

    L = a.lang
    hsys = a.house_system.encode()
    birth_local = localize_birth(a.birth, a.birth_tz, a.birth_fold)
    sr_tz = load_time_zone(a.sr_tz)
    extra_zones = {name: load_time_zone(name) for name in a.extra_tz}
    birth_utc = birth_local.astimezone(dt.timezone.utc)
    natal = chart(julday(birth_utc), a.birth_lat, a.birth_lon, hsys)
    sun0 = natal["bodies"]["sun"]["lon"]

    sr_utc = solar_return_moment(sun0, a.year, birth_local)
    j = julday(sr_utc)
    solar = chart(j, a.sr_lat, a.sr_lon, hsys)
    for key, b in solar["bodies"].items():
        b["natal_house"] = house_of(b["lon"], natal["cusps"])
    if not 0 <= a.natal_orb <= 5:
        raise ValueError("--natal-orb must be between 0 and 5 degrees")
    names = {k: (ru if L == "ru" else en) for k, _, ru, en in BODIES}
    cal = day_calendar(sr_utc, sr_tz)
    to_natal = natal_aspects(solar["bodies"], natal, a.natal_orb)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import degrees as deg_mod
    import relocation as rel_mod
    deg_hits = {"natal": deg_mod.find(deg_mod.chart_points(natal), a.degree_convention),
                "solar": deg_mod.find(deg_mod.chart_points(solar), a.degree_convention)}
    places = [{"name": ("Место встречи" if L == "ru" else "Return location") + f" ({a.sr_tz})",
               "lat": a.sr_lat, "lon": a.sr_lon}]
    for item in a.place:
        try:
            name, lat, lon = item.rsplit("|", 2)
            places.append({"name": name, "lat": coordinate(lat, latitude=True),
                           "lon": coordinate(lon, latitude=False)})
        except (ValueError, argparse.ArgumentTypeError) as exc:
            raise ValueError(f'--place must look like "City|lat|lon": {item!r}') from exc
    reloc = rel_mod.compare(chart, j, places, hsys) if a.place else []
    import extras
    hmap = extras.house_map(solar, natal)
    moons = extras.day_moons(swe, FLAGS, julday, cal)
    lunas = extras.lunations(swe, FLAGS, julday, from_julday,
                             sr_utc - dt.timedelta(days=12), sr_utc + dt.timedelta(days=12))
    for x in lunas:
        x["day"] = extras.day_of(x["utc"], sr_utc)
    launch = None
    if a.home:
        try:
            hname, hlat, hlon = a.home.rsplit("|", 2)
            home = {"name": hname, "lat": coordinate(hlat, latitude=True),
                    "lon": coordinate(hlon, latitude=False)}
        except (ValueError, argparse.ArgumentTypeError) as exc:
            raise ValueError(f'--home must look like "Name|lat|lon": {a.home!r}') from exc
        if not 0 < a.radius_km <= 2000:
            raise ValueError("--radius-km must be between 0 and 2000")
        launch = extras.launch_search(chart, j, home, a.launch_house, hsys, a.radius_km)
        pt = launch["nearest"]
        if pt:
            pc = chart(j, pt["lat"], pt["lon"], hsys)
            launch["angles"] = {"asc": pc["asc"], "mc": pc["mc"]}
            launch["angle_degrees"] = deg_mod.find({"asc": pc["asc"], "mc": pc["mc"]}, a.degree_convention)
    if (a.scan_lat is None) != (a.goal_house is None):
        raise ValueError("--scan-lat and --goal-house must be used together")
    scan = (rel_mod.scan_longitudes(chart, j, a.scan_lat, hsys, a.goal_house)
            if a.scan_lat is not None else None)
    if a.json:
        write_json_exclusive(a.json, {
            "metadata": provenance(a), "input": vars(a),
            "birth_utc": birth_utc.isoformat(), "natal": natal,
            "solar_return_utc": sr_utc.isoformat(),
            "solar_return_local": sr_utc.astimezone(sr_tz).isoformat(),
            "solar": solar, "aspects": aspects(solar["bodies"]),
            "natal_aspects": to_natal, "days": cal, "degrees": deg_hits,
            "relocation": reloc, "scan": scan, "house_map": hmap, "day_moons": moons,
            "lunations": [dict(x, utc=x["utc"].isoformat()) for x in lunas], "launch": launch,
        })

    extra = dict(house_map=hmap, moons=moons, lunas=lunas, launch=launch)
    if a.diary:
        from report import build_diary
        print(build_diary(lang=L, year=a.year, sr_utc=sr_utc, sr_tz_name=a.sr_tz, cal=cal,
                          moons=moons, lunas=lunas, rmin=rmin))
        return
    if a.report:
        from report import build_report
        print(build_report(lang=L, year=a.year, sun0=sun0, natal=natal, solar=solar,
                           sr_utc=sr_utc, sr_tz_name=a.sr_tz, extra_tz=a.extra_tz,
                           cal=cal, to_natal=to_natal, inner=aspects(solar["bodies"]),
                           house_system=HOUSE_SYSTEMS[a.house_system],
                           fmt_lon=fmt_lon, rmin=rmin, degrees=deg_hits,
                           degree_convention=a.degree_convention, relocation=reloc,
                           scan=scan, scan_lat=a.scan_lat, goal_house=a.goal_house, **extra))
        return

    T = (lambda ru, en: ru if L == "ru" else en)
    print(T("=== НАТАЛЬНАЯ КАРТА ===", "=== NATAL CHART ==="))
    print(T("Рождение (UTC):", "Birth (UTC):"), birth_utc.strftime("%Y-%m-%d %H:%M"))
    print("ASC", fmt_lon(natal["asc"], L), "| MC", fmt_lon(natal["mc"], L))
    for k, b in natal["bodies"].items():
        print(f"  {names[k]:12s} {fmt_lon(b['lon'], L):22s} {T('дом','house')} {b['house']}{'  R' if b['retro'] else ''}")

    print("\n" + T("=== МОМЕНТ СОЛЯРА ===", "=== SOLAR RETURN MOMENT ==="))
    print(T("Солнце возвращается в", "Sun returns to"), fmt_lon(sun0, L))
    print(T("Год годовщины:", "Birthday anniversary year:"), a.year)
    if sr_utc.year != a.year or sr_utc.astimezone(sr_tz).year != a.year:
        print(T("Примечание: ближайший возврат попал в соседний календарный год.",
                "Note: the nearest return falls in an adjacent calendar year."))
    print("  UTC:", sr_utc.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"  {a.sr_tz}:", rmin(sr_utc.astimezone(sr_tz)).strftime("%Y-%m-%d %H:%M %z"))
    for tz, zone in extra_zones.items():
        print(f"  {tz}:", rmin(sr_utc.astimezone(zone)).strftime("%Y-%m-%d %H:%M %z"))

    print("\n" + T("=== КАРТА СОЛЯРА ===", "=== SOLAR RETURN CHART ==="))
    print("ASC", fmt_lon(solar["asc"], L), "| MC", fmt_lon(solar["mc"], L))
    for i, c in enumerate(solar["cusps"]):
        print(f"  {T('куспид','cusp')} {i+1:2d}: {fmt_lon(c, L)}")
    for k, b in solar["bodies"].items():
        print(f"  {names[k]:12s} {fmt_lon(b['lon'], L):22s} {T('дом соляра','SR house')} {b['house']:2d}"
              f" | {T('натальный дом','natal house')} {b['natal_house']:2d}{'  R' if b['retro'] else ''}")
    print(T("Аспекты:", "Aspects:"))
    for x in aspects(solar["bodies"]):
        print(f"  {names[x['a']]} {x['aspect_ru'] if L=='ru' else x['aspect']} {names[x['b']]} ({x['orb']}°)")
    print(T(f"Аспекты соляра к наталу (орбис {a.natal_orb}°):",
            f"Solar-return to natal aspects (orb {a.natal_orb}°):"))
    pnames = dict(names, asc="ASC", mc="MC")
    for x in to_natal:
        print(f"  {T('соляр','SR')} {names[x['solar']]} {x['aspect_ru'] if L=='ru' else x['aspect']} "
              f"{T('натал','natal')} {pnames[x['natal']]} ({x['orb']}°)")

    print("\n" + T("=== КОРОЛЕВСКИЕ И РАЗРУШИТЕЛЬНЫЕ ГРАДУСЫ ===", "=== ROYAL AND DESTRUCTIVE DEGREES ==="),
          f"({a.degree_convention})")
    for chart_name, hits in deg_hits.items():
        for h in hits:
            print(f"  {T('натал','natal') if chart_name == 'natal' else T('соляр','SR')}: {pnames[h['point']]} "
                  f"{fmt_lon(h['lon'], L)} — {T('королевский','royal') if h['kind'] == 'royal' else T('разрушительный','destructive')}")
    if not any(deg_hits.values()):
        print(T("  нет", "  none"))

    if reloc:
        print("\n" + T("=== СРАВНЕНИЕ МЕСТ ===", "=== PLACE COMPARISON ==="))
        for r in reloc:
            sm = r["summary"]
            ang = ", ".join(f"{names[x['planet']]}@{x['angle']}" for x in sm["on_angles"]) or "—"
            print(f"  {r['name']}: ASC {SIGNS[L][sm['asc_sign']]}, MC {SIGNS[L][sm['mc_sign']]}, "
                  f"{T('Солнце','Sun')} {sm['sun_house']}, {T('Луна','Moon')} {sm['moon_house']}, {ang}")
    if scan is not None:
        print("\n" + T(f"=== ДОЛГОТЫ НА ШИРОТЕ {a.scan_lat}°: СОЛНЦЕ В {a.goal_house}-М ДОМЕ ===",
                        f"=== LONGITUDES AT LAT {a.scan_lat}°: SUN IN HOUSE {a.goal_house} ==="))
        for r in scan:
            print(f"  {r['from']:+.0f}° … {r['to']:+.0f}°  ASC: " + ", ".join(SIGNS[L][x] for x in r["asc_signs"]))
        if not scan:
            print(T("  нет", "  none"))

    print("\n" + T("=== 24 СУТОК ===", "=== 24-DAY CALENDAR ==="))
    for d in cal:
        s = rmin(dt.datetime.fromisoformat(d["start"]).astimezone(sr_tz)).strftime("%d.%m %H:%M %z")
        e = rmin(dt.datetime.fromisoformat(d["end"]).astimezone(sr_tz)).strftime("%d.%m %H:%M %z")
        print(f"  {d['day']:>3} | {s} → {e} | {T('дом','house')} {d['house']}")


if __name__ == "__main__":
    main()
