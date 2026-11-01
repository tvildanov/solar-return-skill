#!/usr/bin/env python3
# Birth-time rectification helper — part of the "solar-return" skill.
# Copyright (C) 2026 AstroEmpathy contributors
# Licensed under the GNU Affero General Public License v3.0 (see LICENSE).
"""
Rectification to the minute: test every minute of a time window and rank them by how
well dated life events coincide with (a) transits of Jupiter–Pluto to the angles and
(b) solar-arc directions between the angles and natal planets. Without events it
prints a sensitivity table only. The result is a hypothesis for an astrologer to
confirm, never a certainty.

Example:
  python3 rectify.py --birth "1990-05-21 14:30" --birth-tz Europe/Moscow \
    --birth-lat 55.7558 --birth-lon 37.6173 --window 60 \
    --event "2012-08-18|свадьба" --event "2015-03-02|рождение ребёнка" --lang ru
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import solar_return as sr  # noqa: E402

swe = sr.swe
FLAGS = sr.FLAGS
SLOW = [("jupiter", swe.JUPITER, 0.6), ("saturn", swe.SATURN, 0.9), ("uranus", swe.URANUS, 1.0),
        ("neptune", swe.NEPTUNE, 0.8), ("pluto", swe.PLUTO, 1.0)]
NATAL = [("sun", swe.SUN), ("moon", swe.MOON), ("mercury", swe.MERCURY), ("venus", swe.VENUS),
         ("mars", swe.MARS), ("jupiter", swe.JUPITER), ("saturn", swe.SATURN),
         ("uranus", swe.URANUS), ("neptune", swe.NEPTUNE), ("pluto", swe.PLUTO)]
ASPECT_W = {0: 1.0, 180: 0.9, 90: 0.8, 120: 0.35}
TRANSIT_ORB = 1.0      # degrees, transit to angle
ARC_ORB = 0.5          # degrees (~6 months of solar arc)
TROPICAL_YEAR = 365.24219

T = {
    "ru": {"title": "Уточнение времени рождения", "given": "Заявленное время", "window": "Окно поиска",
           "min": "мин", "sens": "Чувствительность", "time": "Время", "asc": "Асцендент", "mc": "MC",
           "changes": "Смена знака Асцендента в окне", "none": "нет",
           "ranking": "Лучшие варианты по событиям", "score": "Баллы", "hits": "Совпадения",
           "best": "Наиболее вероятное время (гипотеза)", "events": "События",
           "detail": "Совпадения для лучшего варианта", "transit": "транзит", "arc": "дирекция",
           "to": "к", "noevents": "Событий не задано: показана только чувствительность. Добавьте 5–10 датированных событий (--event \"ГГГГ-ММ-ДД|описание\"), чтобы ранжировать минуты.",
           "warn": "Это гипотеза для проверки, а не точный ответ. Чем больше точно датированных событий, тем надёжнее результат. Сильные события: свадьба, развод, рождение детей, переезд, смена работы, смерть близких, тяжёлые болезни или аварии.",
           "flat": "Разница между лучшими вариантами мала: событий недостаточно, чтобы уверенно выбрать минуту."},
    "en": {"title": "Birth-time rectification", "given": "Stated time", "window": "Search window",
           "min": "min", "sens": "Sensitivity", "time": "Time", "asc": "Ascendant", "mc": "MC",
           "changes": "Ascendant sign changes in the window", "none": "none",
           "ranking": "Best candidates by events", "score": "Score", "hits": "Hits",
           "best": "Most likely time (hypothesis)", "events": "Events",
           "detail": "Hits for the best candidate", "transit": "transit", "arc": "direction",
           "to": "to", "noevents": "No events given: sensitivity only. Add 5–10 dated events (--event \"YYYY-MM-DD|label\") to rank minutes.",
           "warn": "This is a hypothesis to verify, not an exact answer. More precisely dated events give a more reliable result. Strong events: marriage, divorce, birth of children, relocation, job change, death of loved ones, serious illness or accidents.",
           "flat": "The best candidates are close: not enough events to pick one minute with confidence."},
}
NAMES = {"ru": {"sun": "Солнце", "moon": "Луна", "mercury": "Меркурий", "venus": "Венера", "mars": "Марс",
                "jupiter": "Юпитер", "saturn": "Сатурн", "uranus": "Уран", "neptune": "Нептун",
                "pluto": "Плутон", "ASC": "ASC", "MC": "MC", "DSC": "DSC", "IC": "IC"},
         "en": {k: k.capitalize() for k in ("sun", "moon", "mercury", "venus", "mars", "jupiter",
                                            "saturn", "uranus", "neptune", "pluto")}}
NAMES["en"].update({"ASC": "ASC", "MC": "MC", "DSC": "DSC", "IC": "IC"})


def sep(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def angles_at(j, lat, lon, hsys=b"P"):
    _, ascmc = swe.houses(j, lat, lon, hsys)
    asc, mc = ascmc[0], ascmc[1]
    return {"ASC": asc, "MC": mc, "DSC": (asc + 180) % 360, "IC": (mc + 180) % 360}


def prepare_events(events, birth_utc, tz):
    """Positions that do not depend on the exact birth minute."""
    jb = sr.julday(birth_utc)
    sun0 = swe.calc_ut(jb, swe.SUN, FLAGS)[0][0]
    natal = {k: swe.calc_ut(jb, pid, FLAGS)[0][0] for k, pid in NATAL}
    out = []
    for date, label in events:
        noon = dt.datetime.combine(date, dt.time(12, 0), tzinfo=tz).astimezone(dt.timezone.utc)
        je = sr.julday(noon)
        age_days = (noon - birth_utc).total_seconds() / 86400 / TROPICAL_YEAR   # 1 day = 1 year
        prog_sun = swe.calc_ut(jb + age_days, swe.SUN, FLAGS)[0][0]
        arc = (prog_sun - sun0) % 360
        out.append({"date": date, "label": label, "arc": arc,
                    "transits": {k: (swe.calc_ut(je, pid, FLAGS)[0][0], w) for k, pid, w in SLOW}})
    return natal, out


def score_candidate(ang, natal, events):
    total, hits = 0.0, []
    for ev in events:
        for k, (lon, w) in ev["transits"].items():
            for a_name in ("ASC", "MC"):   # DSC/IC are covered by the opposition/conjunction
                a_lon = ang[a_name]
                d = sep(lon, a_lon)
                for asp, aw in ASPECT_W.items():
                    orb = abs(d - asp)
                    if orb <= TRANSIT_ORB:
                        s = w * aw * (1 - orb / TRANSIT_ORB)
                        total += s
                        hits.append((ev, "transit", k, asp, a_name, round(orb, 2), s))
        for a_name in ("ASC", "MC"):
            directed = (ang[a_name] + ev["arc"]) % 360
            for k, lon in natal.items():
                d = sep(directed, lon)
                for asp in (0, 90, 180):
                    orb = abs(d - asp)
                    if orb <= ARC_ORB:
                        s = ASPECT_W[asp] * (1 - orb / ARC_ORB)
                        total += s
                        hits.append((ev, "arc", a_name, asp, k, round(orb, 2), s))
        for k, lon in natal.items():   # directed planets to natal angles
            directed = (lon + ev["arc"]) % 360
            for a_name in ("ASC", "MC"):
                d = sep(directed, ang[a_name])
                for asp in (0, 90, 180):
                    orb = abs(d - asp)
                    if orb <= ARC_ORB:
                        s = 0.8 * ASPECT_W[asp] * (1 - orb / ARC_ORB)
                        total += s
                        hits.append((ev, "arc", k, asp, a_name, round(orb, 2), s))
    return total, hits


def parse_event(text):
    try:
        date_s, label = (text.split("|", 1) + [""])[:2]
        return dt.date.fromisoformat(date_s.strip()), label.strip()
    except ValueError as exc:
        raise argparse.ArgumentTypeError('event must look like "YYYY-MM-DD|label"') from exc


def rectify(birth, tz_name, lat, lon, window, events, hsys=b"P", fold=None):
    base = sr.localize_birth(birth, tz_name, fold)
    tz = sr.load_time_zone(tz_name)
    natal, evs = prepare_events(events, base.astimezone(dt.timezone.utc), tz) if events else ({}, [])
    rows = []
    for m in range(-window, window + 1):
        t = base + dt.timedelta(minutes=m)
        ang = angles_at(sr.julday(t.astimezone(dt.timezone.utc)), lat, lon, hsys)
        score, hits = score_candidate(ang, natal, evs) if evs else (0.0, [])
        rows.append({"offset": m, "local": t, "ang": ang, "score": score, "hits": hits})
    return base, rows


def render(base, rows, events, window, lang):
    L, N = T[lang], NAMES[lang]
    fmt = lambda x: sr.fmt_lon(x, lang)
    out = [f"# {L['title']}", "", f"- {L['given']}: {base.strftime('%Y-%m-%d %H:%M %Z')}",
           f"- {L['window']}: ±{window} {L['min']}", ""]
    out += [f"## {L['sens']}", "", f"| {L['time']} | {L['asc']} | {L['mc']} |", "| --- | --- | --- |"]
    marks = sorted({0, -window, window, *range(-window, window + 1, max(5, window // 6))})
    by = {r["offset"]: r for r in rows}
    for m in marks:
        r = by[m]
        out.append(f"| {r['local'].strftime('%H:%M')} ({m:+d}) | {fmt(r['ang']['ASC'])} | {fmt(r['ang']['MC'])} |")
    changes = [r for prev, r in zip(rows, rows[1:]) if int(prev["ang"]["ASC"] // 30) != int(r["ang"]["ASC"] // 30)]
    out += ["", f"**{L['changes']}:** " + (", ".join(f"{r['local'].strftime('%H:%M')} → "
                                                       f"{sr.SIGNS[lang][int(r['ang']['ASC'] // 30)]}"
                                                       for r in changes) or L["none"]), ""]
    if not events:
        return "\n".join(out + [L["noevents"], "", f"*{L['warn']}*", ""])
    ranked = sorted(rows, key=lambda r: -r["score"])
    out += [f"## {L['events']}", ""] + [f"- {d.isoformat()} — {lbl}" for d, lbl in events] + [""]
    out += [f"## {L['ranking']}", "", f"| {L['time']} | {L['asc']} | {L['mc']} | {L['score']} | {L['hits']} |",
            "| --- | --- | --- | --- | --- |"]
    for r in ranked[:7]:
        out.append(f"| {r['local'].strftime('%H:%M')} ({r['offset']:+d}) | {fmt(r['ang']['ASC'])} | "
                   f"{fmt(r['ang']['MC'])} | {r['score']:.2f} | {len(r['hits'])} |")
    best = ranked[0]
    out += ["", f"**{L['best']}: {best['local'].strftime('%H:%M')}** ({best['offset']:+d} {L['min']})", ""]
    if len(ranked) > 1 and ranked[1]["score"] > 0 and best["score"] - ranked[1]["score"] < 0.05 * max(best["score"], 1e-9):
        out += [f"*{L['flat']}*", ""]
    out += [f"### {L['detail']}", ""]
    for ev, kind, a, asp, b, orb, s in sorted(best["hits"], key=lambda h: -h[6])[:15]:
        label = L["transit"] if kind == "transit" else L["arc"]
        out.append(f"- {ev['date'].isoformat()} {ev['label']}: {label} {N.get(a, a)} {asp}° {L['to']} {N.get(b, b)} (орб {orb}°)"
                   if lang == "ru" else
                   f"- {ev['date'].isoformat()} {ev['label']}: {label} {N.get(a, a)} {asp}° {L['to']} {N.get(b, b)} (orb {orb}°)")
    return "\n".join(out + ["", f"*{L['warn']}*", ""])


def main(argv=None):
    p = argparse.ArgumentParser(description="Birth-time rectification to the minute (hypothesis)")
    p.add_argument("--birth", required=True, help='approximate local birth time "YYYY-MM-DD HH:MM"')
    p.add_argument("--birth-tz", required=True)
    p.add_argument("--birth-fold", type=int, choices=(0, 1))
    p.add_argument("--birth-lat", type=lambda x: sr.coordinate(x, latitude=True), required=True)
    p.add_argument("--birth-lon", type=lambda x: sr.coordinate(x, latitude=False), required=True)
    p.add_argument("--window", type=int, default=60, help="minutes either side to test (1–720, default 60)")
    p.add_argument("--event", action="append", default=[], type=parse_event,
                   help='dated life event "YYYY-MM-DD|label" (repeatable)')
    p.add_argument("--house-system", default="P", choices=tuple(sr.HOUSE_SYSTEMS))
    p.add_argument("--lang", choices=["ru", "en"], default="ru")
    a = p.parse_args(argv)
    if not 1 <= a.window <= 720:
        p.error("--window must be between 1 and 720 minutes")
    try:
        base, rows = rectify(a.birth, a.birth_tz, a.birth_lat, a.birth_lon, a.window, a.event,
                             a.house_system.encode(), a.birth_fold)
    except (ValueError, swe.Error) as exc:
        p.error(str(exc))
    print(render(base, rows, a.event, a.window, a.lang))


if __name__ == "__main__":
    main()
