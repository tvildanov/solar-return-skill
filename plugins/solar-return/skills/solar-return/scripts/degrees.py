# Royal / destructive degree check — part of the "solar-return" skill.
# Copyright (C) 2026 AstroEmpathy contributors
# Licensed under the GNU Affero General Public License v3.0 (see LICENSE).
"""Find chart points that fall on royal or destructive degrees (data/degrees.json)."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
SIGN_KEYS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
             "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]


def load_table() -> dict:
    return json.loads((DATA / "degrees.json").read_text(encoding="utf-8"))


def degree_number(lon: float, convention: str = "ordinal") -> tuple:
    """Return (sign index, degree number 1–30) for a longitude.

    ordinal: 0°00'–0°59' of a sign is its 1st degree, 12°00'–12°59' its 13th (default).
    exact:   the whole degree as written, 13°00'–13°59' is "13"; 0°xx' is 0 and never matches.
    """
    lon %= 360
    sign = int(lon // 30)
    within = lon - 30 * sign
    if convention == "ordinal":
        return sign, int(within) + 1
    if convention == "exact":
        return sign, int(within)
    raise ValueError("degree convention must be 'ordinal' or 'exact'")


def find(points: dict, convention: str = "ordinal") -> list:
    """points: {key: longitude}. Returns [{point, kind, sign, degree}]."""
    table = load_table()
    hits = []
    for key, lon in points.items():
        sign, deg = degree_number(lon, convention)
        for kind in ("royal", "destructive"):
            if table[kind].get(SIGN_KEYS[sign]) == deg:
                hits.append({"point": key, "kind": kind, "sign": sign, "degree": deg, "lon": lon})
    return hits


def chart_points(chart: dict, cusps: bool = True) -> dict:
    """Bodies, ASC, MC and (by default) the other ten house cusps: keys cusp2 … cusp12."""
    pts = {k: v["lon"] for k, v in chart["bodies"].items()}
    pts.update({"asc": chart["asc"], "mc": chart["mc"]})
    if cusps:
        for i, lon in enumerate(chart["cusps"], 1):
            if i not in (1, 10):
                pts[f"cusp{i}"] = lon
    return pts


def activations(natal_hits: list, to_natal: list) -> list:
    """Natal points on special degrees that a solar-return body aspects this year."""
    by_point = {h["point"]: h for h in natal_hits}
    return [dict(by_point[a["natal"]], solar=a["solar"], aspect=a["aspect"], orb=a["orb"])
            for a in to_natal if a["natal"] in by_point]
