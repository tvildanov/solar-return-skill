# Autonomous solar-return report — part of the "solar-return" skill.
# Copyright (C) 2026 AstroEmpathy contributors
# Licensed under the GNU Affero General Public License v3.0 (see LICENSE).
"""
Builds a Markdown report from computed chart data and the bundled knowledge
base (data/kb.<lang>.json) following the deterministic rules in
data/ALGORITHM.md. No network, no AI model: the same input gives the same text.
"""
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

DATA = Path(__file__).resolve().parent.parent / "data"
PLANET_ORDER = ["sun", "moon", "mercury", "venus", "mars", "jupiter",
                "saturn", "uranus", "neptune", "pluto", "node"]
STELLIUM_BODIES = PLANET_ORDER[:-1]          # node excluded
ANGULAR_HOUSES = (1, 4, 7, 10)
ANGULAR_WEIGHT = {"mercury": 58, "venus": 58, "mars": 60, "jupiter": 60, "saturn": 60,
                  "uranus": 55, "neptune": 55, "pluto": 55}
RETRO_KEYS = ("mercury", "venus", "mars")
FOCUS_NATAL = ("sun", "moon", "asc", "mc")
MAX_KEYS = 7


def load_kb(lang: str) -> dict:
    return json.loads((DATA / f"kb.{lang}.json").read_text(encoding="utf-8"))


def _name(kb, key):
    return kb["planets"][key]["name"] if key in kb["planets"] else kb["points"][key]["name"]


def _info(kb, key):
    return kb["planets"].get(key) or kb["points"][key]


def year_keys(kb: dict, natal: dict, solar: dict, to_natal: list) -> list:
    """Rank the factors of the year (ALGORITHM.md, section 'Keys of the year')."""
    t, houses, L = kb["templates"], kb["houses"], kb["labels"]
    bodies = solar["bodies"]
    sign = int(solar["asc"] // 30) % 12
    keys = []

    def add(weight, title, text, light, shadow, helps, src=()):
        keys.append({"weight": weight, "title": title, "text": text,
                     "light": light, "shadow": shadow, "helps": helps, "src": list(src)})

    def dedupe(a, b):
        return a if a == b else f"{a}; {b}"

    s = kb["signs"][sign]
    add(100, t["asc_key"].format(sign=s["name"]), s["asc"], s["light"], s["shadow"], s["helps"],
        src=[("sign", sign)])

    counts = {}
    for k in STELLIUM_BODIES:
        counts.setdefault(bodies[k]["house"], []).append(k)
    sun_h, moon_h = bodies["sun"]["house"], bodies["moon"]["house"]

    # Sun house; a stellium or the Moon in the same house is merged into this key.
    title, text = t["sun_key"].format(house=sun_h), kb["sun_house"][sun_h - 1]
    others = [m for m in counts[sun_h] if m != "sun"]
    if others:
        title += f" ({L['with']} " + ", ".join(_name(kb, m) for m in others) + ")"
    if len(counts[sun_h]) >= 3:
        text += " " + t["stellium_text"].format(sphere=houses[sun_h - 1]["sphere"])
    if moon_h == sun_h:
        text += " " + kb["moon_house"][moon_h - 1]
    hh = houses[sun_h - 1]
    add(95, title, text, hh["light"], hh["shadow"], hh["helps"],
        src=[("planet", "sun")] + ([("planet", "moon")] if moon_h == sun_h else []) + [("house", sun_h)])

    for house, members in sorted(counts.items()):
        if len(members) >= 3 and house != sun_h:
            hh = houses[house - 1]
            text = t["stellium_text"].format(sphere=hh["sphere"])
            if house == moon_h:
                text += " " + kb["moon_house"][moon_h - 1]
            add(90 + len(members),
                t["stellium_key"].format(house=house, planets=", ".join(_name(kb, m) for m in members)),
                text, hh["light"], hh["shadow"], hh["helps"],
                src=[("planet", m) for m in members[:2]] + [("house", house)])

    if moon_h != sun_h and len(counts[moon_h]) < 3:
        hh = houses[moon_h - 1]
        add(85, t["moon_key"].format(house=moon_h), kb["moon_house"][moon_h - 1],
            hh["light"], hh["shadow"], hh["helps"], src=[("planet", "moon"), ("house", moon_h)])

    for asp in to_natal:
        if asp["solar"] == "sun" and asp["natal"] == "sun":
            continue  # true by definition of a solar return
        if asp["solar"] in ("sun", "moon") or asp["natal"] in FOCUS_NATAL:
            a, b = _info(kb, asp["solar"]), _info(kb, asp["natal"])
            at = kb["aspects"][asp["aspect"]]
            add(80 - 10 * asp["orb"],
                t["aspect_key"].format(a=a["name"], aspect=at["name"], b=b["name"]),
                at["tone"].format(a=f'{a["name"]} ({L["sr_short"]})', b=f'{b["name"]} ({L["natal_short"]})') + ". " +
                f'{L["principles"]}: {dedupe(a["principle"], b["principle"])}.',
                dedupe(a["light"], b["light"]), dedupe(a["shadow"], b["shadow"]), at["helps"],
                src=[("aspect", asp["aspect"])] + [("planet", x) for x in (asp["solar"], asp["natal"])
                                                   if x in kb["planets"]][:2])

    sn, mn = bodies["sun"]["natal_house"], bodies["moon"]["natal_house"]
    add(70, t["natal_key"], t["natal_text"].format(
        sun=sn, sun_sphere=houses[sn - 1]["sphere"], moon=mn, moon_sphere=houses[mn - 1]["sphere"]),
        houses[sn - 1]["light"], houses[sn - 1]["shadow"], houses[sn - 1]["helps"],
        src=[("house", sn)] + ([("house", mn)] if mn != sn else []))

    for k, w in ANGULAR_WEIGHT.items():
        hh = bodies[k]["house"]
        if hh in ANGULAR_HOUSES:
            p = kb["planets"][k]
            add(w, t["angular_key"].format(planet=p["name"], house=hh),
                t["angular_text"].format(principle=p["principle"].capitalize(),
                                         sphere=houses[hh - 1]["sphere"]),
                p["light"], p["shadow"], houses[hh - 1]["helps"], src=[("planet", k), ("house", hh)])

    for k in RETRO_KEYS:
        if bodies[k]["retro"]:
            p = kb["planets"][k]
            add(50, t["retro_key"].format(planet=p["name"]),
                t["retro_text"].format(principle=p["principle"]), p["light"], p["shadow"], t["retro_helps"],
                src=[("planet", k)])

    keys.sort(key=lambda x: -x["weight"])
    return keys[:MAX_KEYS]


CHANNELS = ("body", "feel", "think", "act", "react")


def load_deep(lang: str) -> dict:
    return json.loads((DATA / f"deep.{lang}.json").read_text(encoding="utf-8"))


def _src_label(kb, src):
    kind, ref = src
    if kind == "sign":
        return f"ASC {kb['signs'][ref]['name']}"
    if kind == "planet":
        return kb["planets"][ref]["name"]
    if kind == "house":
        return f"House {ref}" if kb["lang"] == "en" else f"{ref}-й дом"
    return kb["aspects"][ref]["name"]


def _src_entry(deep, src):
    kind, ref = src
    if kind == "sign":
        return deep["signs"][ref]
    if kind == "planet":
        return deep["planets"][ref]
    if kind == "house":
        return deep["houses"][ref - 1]
    return None


def deep_block(kb, deep, srcs) -> list:
    """'How it works inside' for one key: need, mechanism, five channels, shadow root, key."""
    D = deep["labels"]
    srcs = list(dict.fromkeys(srcs))  # same planet on both sides of an aspect counts once
    entries = [(s, _src_entry(deep, s)) for s in srcs]
    entries = [(s, e) for s, e in entries if e]
    out = [f"**{D['inside']}**", ""]
    for s, e in entries:
        out.append(f"- **{_src_label(kb, s)} — {D['need'].lower()}:** {e['need']}. {e['mechanism']}")
    for s in srcs:
        if s[0] == "aspect":
            out.append(f"- **{kb['aspects'][s[1]]['name'].capitalize()}:** {deep['aspects'][s[1]]}")
    out.append("")
    for ch in CHANNELS:
        if len(entries) == 1:
            out.append(f"- **{D[ch]}.** {entries[0][1][ch]}")
        else:
            out.append(f"- **{D[ch]}**")
            out += [f"    - {_src_label(kb, s)}: {e[ch]}" for s, e in entries]
    roots = list(dict.fromkeys(e["shadow_root"] for _, e in entries if "shadow_root" in e))
    keys_ = list(dict.fromkeys(e["key"] for _, e in entries if "key" in e))
    if roots:
        out.append(f"- **{D['shadow_root']}.** " + " ".join(roots))
    if keys_:
        out.append(f"- **{D['key']}.** " + " ".join(keys_))
    return out + [""]


def recipe_section(kb, deep, solar) -> list:
    """The five layers of the year: ASC sign, Sun's house, Moon and Moon's house, angular planets."""
    D = deep["labels"]
    b = solar["bodies"]
    srcs = [("sign", int(solar["asc"] // 30) % 12), ("house", b["sun"]["house"]), ("planet", "moon")]
    if b["moon"]["house"] != b["sun"]["house"]:
        srcs.append(("house", b["moon"]["house"]))
    angular = [k for k in ANGULAR_WEIGHT if b[k]["house"] in ANGULAR_HOUSES][:2]
    srcs += [("planet", k) for k in angular]
    out = [f"## {D['recipe']}", "", D["recipe_intro"], ""]
    for ch in CHANNELS:
        out += [f"### {D[ch]}", ""]
        for s in srcs:
            out.append(f"- **{_src_label(kb, s)}:** {_src_entry(deep, s)[ch]}")
        out.append("")
    return out


def observe_section(kb, deep) -> list:
    D, L = deep["labels"], kb["labels"]
    out = [f"### {D['observe5']}", "",
           f"| {L['house']} | {D['body']} | {D['feel']} | {D['think']} | {D['act']} | {D['react']} |",
           "| --- | --- | --- | --- | --- | --- |"]
    for i, o in enumerate(deep["house_observe"], 1):
        out.append(f"| {i} | " + " | ".join(o[ch] for ch in CHANNELS) + " |")
    return out + [""]


def highlighted_houses(solar: dict) -> dict:
    occ = {}
    for k in STELLIUM_BODIES:
        occ.setdefault(solar["bodies"][k]["house"], []).append(k)
    return occ


def _point_name(kb, key):
    return kb["planets"][key]["name"] if key in kb["planets"] else kb["points"][key]["name"]


def degrees_section(kb, degrees, convention) -> list:
    L = kb["labels"]
    out = [f"## {L['degrees']}", "", L["degrees_intro"], ""]
    if not any(degrees.values()):
        out += [L["degrees_none"], ""]
    for chart_name, label in (("natal", L["degrees_natal"]), ("solar", L["degrees_solar"])):
        hits = degrees.get(chart_name, [])
        if hits:
            out += [f"**{label}**", ""]
            for h in hits:
                out.append("- " + kb["degree_text"][h["kind"]].format(
                    point=_point_name(kb, h["point"]), deg=h["degree"], sign=kb["signs"][h["sign"]]["name"]))
            out.append("")
    conv = L["conv_ordinal"] if convention == "ordinal" else L["conv_exact"]
    out += [f"*{L['degrees_convention'].format(conv=conv, src='ezoastra.com, the-day.ru')}*", ""]
    return out


def relocation_section(kb, relocation, scan, scan_lat, goal_house) -> list:
    L = kb["labels"]
    if not relocation and scan is None:
        return []
    out = [f"## {L['relocation']}", "", L["relocation_intro"], ""]
    if relocation:
        out += [f"| {L['place']} | {L['asc_sign']} | {L['mc_sign']} | {L['sun_house']} | {L['moon_house']} | "
                f"{L['on_angles']} | {L['stellium']} |", "| --- | --- | --- | --- | --- | --- | --- |"]
        for r in relocation:
            sm = r["summary"]
            ang = ", ".join(f"{_point_name(kb, x['planet'])} — {x['angle']} ({x['orb']}°)" for x in sm["on_angles"]) or "—"
            st = "; ".join(f"{h}: " + ", ".join(_point_name(kb, m) for m in ms)
                           for h, ms in sorted(sm["stelliums"].items())) or "—"
            out.append(f"| {r['name']} | {kb['signs'][sm['asc_sign']]['name']} | {kb['signs'][sm['mc_sign']]['name']} | "
                       f"{sm['sun_house']} | {sm['moon_house']} | {ang} | {st} |")
        out.append("")
    if scan is not None:
        out += [f"**{L['scan'].format(lat=scan_lat, house=goal_house)}**", ""]
        if scan:
            for r in scan:
                out.append(f"- {L['lon_range']} {r['from']:+.0f}° … {r['to']:+.0f}° — ASC: " +
                           ", ".join(kb["signs"][x]["name"] for x in r["asc_signs"]))
        else:
            out.append(L["scan_none"].format(house=goal_house))
        out.append("")
    out += [L["relocation_how"], ""]
    return out


def house_map_section(kb, house_map) -> list:
    L, houses = kb["labels"], kb["houses"]
    out = [f"## {L['year_by_area']}", "", L["year_by_area_intro"], "",
           f"| {L['sr_to_natal']} | {L['house']} ({L['sr_house']}) | {L['natal_house']} |",
           "| --- | --- | --- |"]
    for m in house_map:
        out.append(f"| {m['sr_house']} → {m['natal_house']} | {houses[m['sr_house']-1]['sphere']} | "
                   f"{houses[m['natal_house']-1]['sphere']} |")
    return out + [""]


def launch_section(kb, launch, fmt_lon, lang) -> list:
    if not launch:
        return []
    L, houses = kb["labels"], kb["houses"]
    g = launch["goal_house"]
    out = [f"## {L['launch']}", "",
           f"- {L['launch_home'].format(name=launch['home']['name'], house=launch['home_sun_house'])}",
           f"- {L['launch_goal'].format(house=g, sphere=houses[g-1]['sphere'])}"]
    pt = launch["nearest"]
    if pt and pt.get("distance_km", 0) == 0:
        out.append(f"- {L['launch_already']}")
    elif pt:
        out.append(f"- {L['launch_nearest'].format(lat=pt['lat'], lon=pt['lon'], km=round(pt['distance_km']))}")
    else:
        out.append(f"- {L['launch_none'].format(km=round(launch['radius_km']))}")
    if launch.get("boundary"):
        b = launch["boundary"]
        out.append(f"- {L['launch_boundary'].format(lon=b['lon'], km=round(b['distance_km']))}")
    if launch.get("sun_on_asc"):
        b = launch["sun_on_asc"]
        out.append(f"- {L['launch_sun_asc'].format(lon=b['lon'], km=round(b['distance_km']))}")
    if pt and launch.get("angles"):
        out.append(f"- {L['launch_angles'].format(asc=fmt_lon(launch['angles']['asc'], lang), mc=fmt_lon(launch['angles']['mc'], lang))}")
        hits = launch.get("angle_degrees") or []
        if hits:
            out.append("- " + L["launch_angles_hit"].format(hits=", ".join(
                f"{kb['points'][h['point']]['name']} — {L[h['kind']]}" for h in hits)))
        else:
            out.append(f"- {L['launch_angles_ok']}")
    out += ["", f"### {L['launch_plan']}", "", L["launch_plan_text"], "",
            f"### {L['checklist']}", ""] + [f"- [ ] {x}" for x in L["checklist_items"]] + [""]
    return out


def build_diary(*, lang, year, sr_utc, sr_tz_name, cal, moons, lunas, rmin) -> str:
    kb = load_kb(lang)
    deep = load_deep(lang)
    D = deep["labels"]
    L, houses = kb["labels"], kb["houses"]
    tz = ZoneInfo(sr_tz_name)
    hhmm = rmin(sr_utc.astimezone(tz)).strftime("%H:%M")
    moon_of = {m["day"]: m["moon_sign"] for m in moons}
    luna_of = {}
    for x in lunas:
        luna_of.setdefault(x["day"], []).append(x)
    out = [f"# {L['diary']} {year}", "", L["diary_intro"], "",
           f"- {L['diary_how_closing']}", f"- {L['diary_how_opening']}",
           f"- {L['diary_bounds'].format(time=hhmm)}", "",
           f"## {L['cheatsheet']}", ""]
    out += [f"- **{i+1}. {h['sphere']}:** {h['observe']}" for i, h in enumerate(houses)] + [""]

    def block(d):
        h = d["house"]
        start = rmin(dt.datetime.fromisoformat(d["start"]).astimezone(tz))
        num = f"{d['day']:+d}" if d["day"] > 0 else str(d["day"])
        warn = f" ⚠ {L['caution']}" if abs(d["day"]) == 8 else ""
        res = [f"### {L['day']} {num} · {start.strftime('%d.%m %H:%M')} · {L['house']} {h} — "
               f"{houses[h-1]['sphere']} · {L['moon']}: {kb['signs'][moon_of[d['day']]]['name']}{warn}", "",
               f"*{L['relate']}:* {houses[h-1]['observe']}", ""]
        for x in luna_of.get(d["day"], []):
            name = L["lunation_new"] if x["kind"] == "new" else L["lunation_full"]
            res += [f"**{name}** {rmin(x['utc'].astimezone(tz)).strftime('%d.%m %H:%M')} "
                    f"({kb['signs'][x['moon_sign']]['name']})", ""]
        if d["day"] == -1:
            res += [f"★ {L['goal_close']}", ""]
        if d["day"] == 1:
            res += [f"★ {L['goal_open']}", ""]
        close = L["f_close"] if d["phase"] == "closing" else L["f_open"]
        res += [f"**{L['f_events']}:**", "", "&nbsp;", "", "&nbsp;", ""]
        obs = deep["house_observe"][h - 1]
        for ch in CHANNELS:
            res += [f"**{D[ch]}** — *{obs[ch]}*:", "", "&nbsp;", ""]
        res += [f"**{close}:**", "", "&nbsp;", "", "&nbsp;", ""]
        return res

    out += [f"## {L['closing']}", ""]
    for d in (x for x in cal if x["phase"] == "closing"):
        out += block(d)
    out += [f"## {L['zero']}", "", L["zero_text"], ""]
    for f in (L["zero_f1"], L["zero_f2"], L["zero_f3"], L["zero_f4"]):
        out += [f"**{f}:**", "", "&nbsp;", "", "&nbsp;", ""]
    out += [f"## {L['opening']}", ""]
    for d in (x for x in cal if x["phase"] == "opening"):
        out += block(d)
    out += [f"*{kb['templates']['footer']}*", ""]
    return "\n".join(out)


def build_report(*, lang, year, sun0, natal, solar, sr_utc, sr_tz_name, extra_tz, cal,
                 to_natal, inner, house_system, fmt_lon, rmin, degrees=None,
                 degree_convention="ordinal", relocation=None, scan=None,
                 scan_lat=None, goal_house=None, house_map=None, moons=None,
                 lunas=None, launch=None) -> str:
    kb = load_kb(lang)
    deep = load_deep(lang)
    L, t, houses = kb["labels"], kb["templates"], kb["houses"]
    tz = ZoneInfo(sr_tz_name)
    local = rmin(sr_utc.astimezone(tz))
    local_s = sr_utc.astimezone(tz).strftime("%d.%m.%Y %H:%M:%S")
    out = [f"# {L['title'].format(year=year)}", ""]

    out += [f"## {L['moment']}", "",
            L["moment_text"].format(sun=fmt_lon(sun0, lang), local=local_s, tz=sr_tz_name),
            "", f"- {L['utc']}: {sr_utc.strftime('%d.%m.%Y %H:%M:%S')}"]
    for z in extra_tz:
        out.append(f"- {z}: {rmin(sr_utc.astimezone(ZoneInfo(z))).strftime('%d.%m.%Y %H:%M')}")
    if local.year != year:
        out.append(f"- {L['adjacent_year']}")
    out.append("")

    out += [f"## {L['chart']}", "",
            f"| {L['point']} | {L['position']} | {L['sr_house']} | {L['natal_house']} |",
            "| --- | --- | --- | --- |",
            f"| {L['angles']['asc']} | {fmt_lon(solar['asc'], lang)} | — | — |",
            f"| {L['angles']['mc']} | {fmt_lon(solar['mc'], lang)} | — | — |"]
    for k in PLANET_ORDER:
        b = solar["bodies"][k]
        r = f" ({L['retro']})" if b["retro"] and k != "node" else ""
        out.append(f"| {kb['planets'][k]['name']}{r} | {fmt_lon(b['lon'], lang)} | {b['house']} | {b['natal_house']} |")
    out.append("")

    out += [f"## {L['keys']}", ""]
    for i, k in enumerate(year_keys(kb, natal, solar, to_natal), 1):
        out += [f"### {i}. {k['title']}", "", k["text"], "",
                f"- **{L['light']}:** {k['light']}",
                f"- **{L['shadow']}:** {k['shadow']}",
                f"- **{L['helps']}:** {k['helps']}", ""]
        out += deep_block(kb, deep, k["src"])

    out += recipe_section(kb, deep, solar)
    if house_map:
        out += house_map_section(kb, house_map)

    out += [f"## {L['planets_in_houses']}", ""]
    for k in PLANET_ORDER[:-1]:
        b, p = solar["bodies"][k], kb["planets"][k]
        out.append(f"- **{p['name']}, {b['house']}:** " +
                   t["planet_house"].format(principle=p["principle"].capitalize(),
                                            sphere=houses[b["house"] - 1]["sphere"]))
    out.append("")

    out += [f"## {L['aspects_natal']}", ""]
    to_natal = [x for x in to_natal if not (x["solar"] == "sun" and x["natal"] == "sun")]
    if to_natal:
        for asp in to_natal:
            a, b = _info(kb, asp["solar"]), _info(kb, asp["natal"])
            at = kb["aspects"][asp["aspect"]]
            out.append(f"- **{t['aspect_key'].format(a=a['name'], aspect=at['name'], b=b['name'])}** "
                       f"({asp['orb']}°): " + at["tone"].format(a=f"{a['name']} ({L['sr_short']})", b=f"{b['name']} ({L['natal_short']})") + ".")
    else:
        out.append(L["aspects_natal_none"])
    out.append("")

    if degrees is not None:
        out += degrees_section(kb, degrees, degree_convention)
    out += relocation_section(kb, relocation or [], scan, scan_lat, goal_house)
    out += launch_section(kb, launch, fmt_lon, lang)

    occ = highlighted_houses(solar)
    moon_of = {m["day"]: m["moon_sign"] for m in (moons or [])}
    out += [f"## {L['days']}", "", L["days_intro"], ""]
    if lunas:
        out += [f"**{L['lunations']}:**", ""]
        for x in lunas:
            name = L["lunation_new"] if x["kind"] == "new" else L["lunation_full"]
            where = L["in_day"].format(day=(f"{x['day']:+d}" if x["day"] > 0 else x["day"]), house=abs(x["day"])) if x["day"] else ""
            out.append(f"- {name}: {rmin(x['utc'].astimezone(tz)).strftime('%d.%m %H:%M')}, "
                       f"{kb['signs'][x['moon_sign']]['name']}" + (f" — {where}" if where else ""))
        out.append("")
    for phase, title in (("closing", L["closing"]), ("opening", L["opening"])):
        out += [f"### {title}", "", f"| {L['day']} | {L['interval']} | {L['house']} | {L['moon']} | {L['suggestion']} |",
                "| --- | --- | --- | --- | --- |"]
        for d in (x for x in cal if x["phase"] == phase):
            s = rmin(dt.datetime.fromisoformat(d["start"]).astimezone(tz)).strftime("%d.%m %H:%M")
            e = rmin(dt.datetime.fromisoformat(d["end"]).astimezone(tz)).strftime("%d.%m %H:%M")
            h = d["house"]
            mark = abs(d["day"]) == 8 or d["day"] == 1 or h in occ
            planets = ", ".join(kb["planets"][k]["name"] for k in occ.get(h, []))
            note = f" **{L['highlight']}**" + (f" ({planets})" if planets else "") if mark else ""
            day = f"{d['day']:+d}" if d["day"] > 0 else str(d["day"])
            moon = kb["signs"][moon_of[d["day"]]]["name"] if d["day"] in moon_of else "—"
            out.append(f"| {day} | {s} → {e} | {h}: {houses[h-1]['sphere']} | {moon} | {houses[h-1][phase]}{note} |")
        out.append("")

    out += observe_section(kb, deep)
    out += [f"## {L['meeting']}", "", t["meeting"], "",
            f"## {L['journal']}", "", t["journal"], "",
            f"## {L['method']}", "", L["method_text"].format(hs=house_system), "",
            f"*{t['footer']}*", ""]
    return "\n".join(out)
