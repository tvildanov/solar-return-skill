# Solar-return relocation comparison — part of the "solar-return" skill.
# Copyright (C) 2026 AstroEmpathy contributors
# Licensed under the GNU Affero General Public License v3.0 (see LICENSE).
"""
Where to meet the solar return: the moment is the same everywhere, but houses
and angles depend on the place. This module recasts the solar-return chart for
several places (or scans longitudes along one latitude) and summarises the
factors listed in data/ALGORITHM.md, section "Relocation".
"""
ANGLE_ORB = 5.0
PERSONAL = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
            "uranus", "neptune", "pluto")


def _sep(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def summarize(chart: dict) -> dict:
    """Key placement facts for one location (no value judgement)."""
    b = chart["bodies"]
    asc, mc = chart["asc"], chart["mc"]
    angles = {"ASC": asc, "MC": mc, "DSC": (asc + 180) % 360, "IC": (mc + 180) % 360}
    on_angles = []
    for k in PERSONAL:
        for name, lon in angles.items():
            orb = _sep(b[k]["lon"], lon)
            if orb <= ANGLE_ORB:
                on_angles.append({"planet": k, "angle": name, "orb": round(orb, 1)})
    counts = {}
    for k in PERSONAL:
        counts.setdefault(b[k]["house"], []).append(k)
    return {
        "asc_sign": int(asc // 30) % 12, "mc_sign": int(mc // 30) % 12,
        "sun_house": b["sun"]["house"], "moon_house": b["moon"]["house"],
        "on_angles": on_angles,
        "stelliums": {h: m for h, m in counts.items() if len(m) >= 3},
        "houses": {k: b[k]["house"] for k in PERSONAL},
    }


def compare(chart_fn, j: float, places: list, hsys: bytes) -> list:
    """places: [{"name", "lat", "lon"}] -> [{place..., summary}]."""
    out = []
    for p in places:
        c = chart_fn(j, p["lat"], p["lon"], hsys)
        out.append(dict(p, summary=summarize(c), asc=c["asc"], mc=c["mc"]))
    return out


def scan_longitudes(chart_fn, j: float, lat: float, hsys: bytes, goal_house: int, step: float = 1.0) -> list:
    """Longitude ranges along one latitude where the SR Sun falls in goal_house."""
    ranges, start, prev, asc_signs = [], None, None, set()
    n = int(360 / step)
    for i in range(n + 1):
        lon = -180 + i * step
        c = chart_fn(j, lat, min(lon, 180), hsys)
        hit = c["bodies"]["sun"]["house"] == goal_house
        if hit:
            if start is None:
                start, asc_signs = lon, set()
            asc_signs.add(int(c["asc"] // 30) % 12)
            prev = lon
        elif start is not None:
            ranges.append({"from": start, "to": prev, "asc_signs": sorted(asc_signs)})
            start = None
    if start is not None:
        ranges.append({"from": start, "to": prev, "asc_signs": sorted(asc_signs)})
    return ranges
