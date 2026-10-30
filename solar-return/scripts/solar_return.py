#!/usr/bin/env python3
# Solar Return calculator — part of the "solar-return" skill.
# Copyright (C) 2026 AstroEmpathy contributors
# Licensed under the GNU Affero General Public License v3.0 (see LICENSE).
# Uses the Swiss Ephemeris via pyswisseph (AGPL), (c) Astrodienst AG.
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
import argparse, datetime as dt, json, sys
from zoneinfo import ZoneInfo

try:
    import swisseph as swe
except ImportError:
    sys.exit("pyswisseph is not installed. Run:  pip install pyswisseph\n"
             "(add --break-system-packages if pip refuses)")

FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED   # built-in Moshier ephemeris, no data files needed

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
    """Round to the nearest minute for display."""
    return (t + dt.timedelta(seconds=30)).replace(second=0, microsecond=0)


def fmt_lon(lon: float, lang: str) -> str:
    s = int(lon // 30) % 12
    deg = lon - 30 * s
    d = int(deg)
    m = int(round((deg - d) * 60))
    if m == 60:
        d, m = d + 1, 0
    return f"{d}°{m:02d}' {SIGNS[lang][s]}"


def house_of(lon: float, cusps) -> int:
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360 < (b - a) % 360:
            return i + 1
    return 12


def chart(j: float, lat: float, lon: float, hsys: bytes = b"P") -> dict:
    cusps, ascmc = swe.houses(j, lat, lon, hsys)
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
        j += diff / s[3]
        if abs(diff) < 1e-9:
            break
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


def main():
    p = argparse.ArgumentParser(description="Solar return calculator (Swiss Ephemeris)")
    p.add_argument("--birth", required=True, help='local birth time "YYYY-MM-DD HH:MM"')
    p.add_argument("--birth-tz", required=True, help="IANA time zone of the birthplace")
    p.add_argument("--birth-lat", type=float, required=True)
    p.add_argument("--birth-lon", type=float, required=True)
    p.add_argument("--year", type=int, required=True, help="year of the solar return")
    p.add_argument("--sr-tz", required=True, help="IANA time zone where the return is met")
    p.add_argument("--sr-lat", type=float, required=True)
    p.add_argument("--sr-lon", type=float, required=True)
    p.add_argument("--extra-tz", action="append", default=[],
                   help="extra time zones to show the moment in (repeatable)")
    p.add_argument("--house-system", default="P", help="P=Placidus (default), K=Koch, W=Whole sign ...")
    p.add_argument("--lang", choices=["ru", "en"], default="ru")
    p.add_argument("--json", help="write full results to this JSON file")
    a = p.parse_args()

    L = a.lang
    hsys = a.house_system.encode()
    birth_local = dt.datetime.strptime(a.birth, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(a.birth_tz))
    birth_utc = birth_local.astimezone(dt.timezone.utc)
    natal = chart(julday(birth_utc), a.birth_lat, a.birth_lon, hsys)
    sun0 = natal["bodies"]["sun"]["lon"]

    sr_utc = solar_return_moment(sun0, a.year, birth_local)
    j = julday(sr_utc)
    solar = chart(j, a.sr_lat, a.sr_lon, hsys)
    for key, b in solar["bodies"].items():
        b["natal_house"] = house_of(b["lon"], natal["cusps"])
    sr_tz = ZoneInfo(a.sr_tz)
    names = {k: (ru if L == "ru" else en) for k, _, ru, en in BODIES}

    T = (lambda ru, en: ru if L == "ru" else en)
    print(T("=== НАТАЛЬНАЯ КАРТА ===", "=== NATAL CHART ==="))
    print(T("Рождение (UTC):", "Birth (UTC):"), birth_utc.strftime("%Y-%m-%d %H:%M"))
    print("ASC", fmt_lon(natal["asc"], L), "| MC", fmt_lon(natal["mc"], L))
    for k, b in natal["bodies"].items():
        print(f"  {names[k]:12s} {fmt_lon(b['lon'], L):22s} {T('дом','house')} {b['house']}{'  R' if b['retro'] else ''}")

    print("\n" + T("=== МОМЕНТ СОЛЯРА ===", "=== SOLAR RETURN MOMENT ==="))
    print(T("Солнце возвращается в", "Sun returns to"), fmt_lon(sun0, L))
    print("  UTC:", sr_utc.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"  {a.sr_tz}:", rmin(sr_utc.astimezone(sr_tz)).strftime("%Y-%m-%d %H:%M"))
    for tz in a.extra_tz:
        print(f"  {tz}:", rmin(sr_utc.astimezone(ZoneInfo(tz))).strftime("%Y-%m-%d %H:%M"))

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

    cal = day_calendar(sr_utc, sr_tz)
    print("\n" + T("=== 24 СУТОК ===", "=== 24-DAY CALENDAR ==="))
    for d in cal:
        s = rmin(dt.datetime.fromisoformat(d["start"])).strftime("%d.%m %H:%M")
        e = rmin(dt.datetime.fromisoformat(d["end"])).strftime("%d.%m %H:%M")
        print(f"  {d['day']:>3} | {s} → {e} | {T('дом','house')} {d['house']}")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"input": vars(a), "birth_utc": birth_utc.isoformat(), "natal": natal,
                       "solar_return_utc": sr_utc.isoformat(),
                       "solar_return_local": sr_utc.astimezone(sr_tz).isoformat(),
                       "solar": solar, "aspects": aspects(solar["bodies"]), "days": cal},
                      f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
