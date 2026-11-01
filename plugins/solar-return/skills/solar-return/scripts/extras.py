# Extra solar-return mechanics — part of the "solar-return" skill.
# Copyright (C) 2026 AstroEmpathy contributors
# Licensed under the GNU Affero General Public License v3.0 (see LICENSE).
"""
- house_map: which natal house each solar-return house cusp falls into ("year by area");
- day_moons: Moon sign at the start of each of the 24 days;
- lunations: new and full moons inside the 24-day window;
- launch_search: nearest place to a home point where the SR Sun falls in a goal house,
  plus the "Sun on Ascendant" longitude and the zone boundary along the home latitude.
"""
import datetime as dt
import math

EARTH_KM = 6371.0


def house_of(lon, cusps):
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360 < (b - a) % 360:
            return i + 1
    return 12


def house_map(solar: dict, natal: dict) -> list:
    """[{sr_house, natal_house, cusp_lon}] for SR cusps 1..12."""
    return [{"sr_house": i + 1, "natal_house": house_of(c, natal["cusps"]), "cusp_lon": c}
            for i, c in enumerate(solar["cusps"])]


def day_moons(swe, flags, julday, cal: list) -> list:
    out = []
    for d in cal:
        start = dt.datetime.fromisoformat(d["start"]).astimezone(dt.timezone.utc)
        lon = swe.calc_ut(julday(start), swe.MOON, flags)[0][0]
        out.append({"day": d["day"], "moon_lon": lon, "moon_sign": int(lon // 30) % 12})
    return out


def lunations(swe, flags, julday, from_julday, start_utc, end_utc) -> list:
    """New (0°) and full (180°) moons between start and end, refined to ~1 s."""
    def elong(j):
        s = swe.calc_ut(j, swe.SUN, flags)[0][0]
        m = swe.calc_ut(j, swe.MOON, flags)[0][0]
        return (m - s) % 360

    j0, j1 = julday(start_utc), julday(end_utc)
    res, step = [], 0.25
    j = j0
    prev = elong(j)
    while j < j1:
        jn = min(j + step, j1)
        cur = elong(jn)
        for target, kind in ((0.0, "new"), (180.0, "full")):
            a = (prev - target + 180) % 360 - 180
            b = (cur - target + 180) % 360 - 180
            if a < 0 <= b:
                lo, hi = j, jn
                for _ in range(40):
                    mid = (lo + hi) / 2
                    if ((elong(mid) - target + 180) % 360 - 180) < 0:
                        lo = mid
                    else:
                        hi = mid
                t = from_julday((lo + hi) / 2)
                mlon = swe.calc_ut((lo + hi) / 2, swe.MOON, flags)[0][0]
                res.append({"kind": kind, "utc": t, "moon_sign": int(mlon // 30) % 12, "lon": mlon})
        prev, j = cur, jn
    return res


def day_of(instant_utc, sr_utc) -> int:
    """Number of the solar day (−12..−1, 1..12) containing an instant, or 0 if outside."""
    days = (instant_utc - sr_utc).total_seconds() / 86400
    if -12 <= days < 0:
        return -math.ceil(-days) if days != int(days) else int(days)
    if 0 <= days < 12:
        return int(days) + 1
    return 0


def distance_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(a))


def _wrap(x):
    return (x + 180) % 360 - 180


def launch_search(chart_fn, j, home: dict, goal_house: int, hsys: bytes,
                  radius_km: float = 300.0, step_km: float = 5.0) -> dict:
    """Nearest point to home (within radius) where the SR Sun is in goal_house."""
    home_chart = chart_fn(j, home["lat"], home["lon"], hsys)
    result = {"home": home, "home_sun_house": home_chart["bodies"]["sun"]["house"],
              "goal_house": goal_house, "radius_km": radius_km, "nearest": None,
              "sun_on_asc": None, "boundary": None}
    if result["home_sun_house"] == goal_house:
        result["nearest"] = dict(home, distance_km=0.0, lat=home["lat"], lon=home["lon"])
    else:
        best = None
        n = int(radius_km // step_km)
        dlat = step_km / 111.2
        dlon = step_km / (111.2 * max(math.cos(math.radians(home["lat"])), 0.05))
        for i in range(-n, n + 1):
            for k in range(-n, n + 1):
                lat, lon = home["lat"] + i * dlat, _wrap(home["lon"] + k * dlon)
                if not -89 < lat < 89:
                    continue
                dist = distance_km(home["lat"], home["lon"], lat, lon)
                if dist > radius_km or (best and dist >= best["distance_km"]):
                    continue
                try:
                    c = chart_fn(j, lat, lon, hsys)
                except ValueError:
                    continue
                if c["bodies"]["sun"]["house"] == goal_house:
                    best = {"lat": round(lat, 3), "lon": round(lon, 3), "distance_km": round(dist, 1)}
        result["nearest"] = best

    # Along the home latitude: longitude where the Sun sits exactly on the ASC (house-1 cusp),
    # and the boundary where the Sun enters the goal house.
    sun = home_chart["bodies"]["sun"]["lon"]
    prev = None
    lo = home["lon"]
    for direction in (1, -1):
        for s in range(1, 1801):
            lon = _wrap(home["lon"] + direction * s * 0.1)
            try:
                c = chart_fn(j, home["lat"], lon, hsys)
            except ValueError:
                break
            if result["boundary"] is None and c["bodies"]["sun"]["house"] == goal_house and \
                    result["home_sun_house"] != goal_house:
                result["boundary"] = {"lat": home["lat"], "lon": round(lon, 3),
                                      "distance_km": round(distance_km(home["lat"], home["lon"], home["lat"], lon), 1)}
            d = _wrap(c["asc"] - sun)
            if prev is not None and prev[0] * d < 0 and abs(prev[0] - d) < 30 and result["sun_on_asc"] is None:
                # linear interpolation between prev lon and this lon
                f = prev[0] / (prev[0] - d)
                at = _wrap(prev[1] + f * _wrap(lon - prev[1]))
                result["sun_on_asc"] = {"lat": home["lat"], "lon": round(at, 3),
                                        "distance_km": round(distance_km(home["lat"], home["lon"], home["lat"], at), 1)}
            prev = (d, lon)
            if result["sun_on_asc"] and (result["boundary"] or result["home_sun_house"] == goal_house):
                break
        prev = None
        if result["sun_on_asc"] and (result["boundary"] or result["home_sun_house"] == goal_house):
            break
    return result
