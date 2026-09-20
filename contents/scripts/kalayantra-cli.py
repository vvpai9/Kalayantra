#!/usr/bin/env python3
"""
kalayantra-cli - Command-line interface for the Kālayantra Panchanga engine.

Queries the local KalaSetu daemon (http://127.0.0.1:8642) when it is running and
otherwise falls back to computing values directly. Output is human-readable text
by default; use --format json or --format csv for machine-readable output.

Examples:
    kalayantra-cli.py day  --date 28-08-2026
    kalayantra-cli.py day  28-08-2026 --lang devanagari
    kalayantra-cli.py day  28-08-2026 --format json
    kalayantra-cli.py range --start 01-01-2026 --end 31-12-2026 --format csv --output year.csv
    kalayantra-cli.py festivals --start 01-01-2026 --days 365 --festival-rule vaishnava --format csv
    kalayantra-cli.py search-city Sringeri
    kalayantra-cli.py gochara --date 15-06-1990 --hour 10 --minute 30 --transit-date 12-09-2026 --lat 13.0827 --lon 80.2707 --tz 5.5 --direct
    kalayantra-cli.py medha --date 15-06-1990 --hour 10 --minute 30 --lat 13.0827 --lon 80.2707 --tz 5.5 --question "Why is Guru strong?" --direct
"""
import sys
import os
import json
import datetime
import argparse
import urllib.request
import urllib.parse
import urllib.error
import platform

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Locate the directory containing the engine modules (KalaChakra.py etc.).
_SCRIPT_CANDIDATES = [
    SCRIPT_DIR,
    os.path.expanduser(os.path.join("~", ".local", "share", "kalayantra", "contents", "scripts")),
    os.path.join(os.path.dirname(SCRIPT_DIR), "contents", "scripts"),
]
for _cand in _SCRIPT_CANDIDATES:
    if os.path.isfile(os.path.join(_cand, "KalaChakra.py")):
        if _cand not in sys.path:
            sys.path.insert(0, _cand)
        break

import KalaChakra
import KalaUtsavachakra
import KalaKosha
from KalaSetu import json_rows_to_csv

DEFAULT_PORT = 8642
DATE_FORMAT = "%d-%m-%Y"

WEEKDAY_MAP = {
    "Saumya": "Wednesday", "Shourya": "Tuesday", "Saumya (Budha)": "Wednesday",
    "Mangalya": "Saturday", "Ashubha": "Monday", "Ravivara": "Sunday", "Jeeva": "Thursday",
}
SEASON_LABELS = {
    "Shishira": "Shishira (Late winter)", "Vasanta": "Vasanta (Spring)",
    "Grishma": "Grishma (Summer)", "Varsha": "Varsha (Monsoon)",
    "Sharad": "Sharad (Autumn)", "Hemanta": "Hemanta (Pre-winter)",
}
GUNA_CANONICAL = ["varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi"]
GUNA_LABELS = {"varna": "Varna", "vashya": "Vashya", "tara": "Tara", "yoni": "Yoni",
               "graha_maitri": "Graha Maitri", "gana": "Gana", "bhakoot": "Bhakoot", "nadi": "Nadi"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _deg(v):
    if v is None:
        return "--"
    d = int(v)
    m = int(round((v - d) * 60))
    if m == 60:
        m = 0; d += 1
    return "{}\u00b0{:02d}'".format(d, m)


def _line(title, body):
    if body:
        return "{}: {}".format(title, body)
    return None


def _sec(title):
    return "\n{}\n{}".format(title, "\u2500" * max(20, len(title) + 2))


def _safe(d, k, fmt=str):
    v = d.get(k)
    return fmt(v) if v is not None else "--"


def _ymd_text(dur):
    """Render a {years, months, days} duration dict without decimals."""
    if not dur:
        return ""
    parts = []
    if dur.get("years"):
        parts.append("{}y".format(dur["years"]))
    if dur.get("months"):
        parts.append("{}m".format(dur["months"]))
    if dur.get("days"):
        parts.append("{}d".format(dur["days"]))
    return " ".join(parts) if parts else "0y"


def _wrap(text, width=78):
    import textwrap
    return "\n".join(textwrap.wrap(text, width))


def _iter_data(data):
    """Yield each entry whether data is a dict, list, or wrapper dict."""
    if isinstance(data, dict):
        if "days" in data:
            yield from data["days"]
            return
        yield data
    else:
        yield from (data or [])


# ── Text formatters ──────────────────────────────────────────────────────────

def _fmt_day(astro, include_festivals=True):
    """Full panchanga text block for a single day."""
    out = []
    d = astro.get("date", "--")
    v = astro.get("vaara", "")
    m = astro.get("masa", "")
    ritu_raw = astro.get("ritu", "")
    ayana = astro.get("ayana", "")
    samvat = astro.get("samvatsara", "")
    era_name = astro.get("era_name", "")
    shaka = astro.get("shaka_year", "")
    vikram = astro.get("vikram_year", "")
    kali = astro.get("kali_year", "")
    cal = astro.get("calendar_system", "")
    cal_display = {"shaka": "Shaka", "amavasyanta": "Amāvāsyānta", "purnimanta": "Pūrṇimānta"}.get(cal, cal)
    pkg = "Shukla" if not astro.get("is_krishna_paksha") else "Krishna"

    out.append(_sec("Kālayantra Panchanga"))
    out.append("Date: {} ({})".format(d, v))
    if era_name or shaka or vikram or kali:
        eras = []
        if shaka: eras.append("Shaka {}".format(shaka))
        if vikram: eras.append("Vikrama Saṁvat {}".format(vikram))
        if kali: eras.append("Kali {}".format(kali))
        out.append("Eras: {}".format(" \u00b7 ".join(eras)))
    if m:
        season = SEASON_LABELS.get(ritu_raw, ritu_raw)
        parts = ["Masa: {}".format(m)]
        if cal_display: parts.append("({})".format(cal_display))
        if season or ayana or samvat:
            extras = [x for x in [season, ayana, samvat] if x]
            parts.append("\u2014 {}".format(", ".join(extras)))
        out.append(" ".join(parts))

    rise = _safe(astro, "sunrise")
    set_ = _safe(astro, "sunset")
    mrise = _safe(astro, "moonrise")
    mset = _safe(astro, "moonset")
    dl = _safe(astro, "day_length_min", "{:.0f}")
    nl = _safe(astro, "night_length_min", "{:.0f}")
    out.append("Sunrise {} \u00b7 Sunset {}".format(rise, set_))
    if mrise != "--" or mset != "--":
        out.append("Moonrise {} \u00b7 Moonset {}".format(mrise, mset))
    if dl != "--" and nl != "--":
        out.append("Day {} min \u00b7 Night {} min".format(dl, nl))

    t1 = astro.get("tithi", "--")
    t1e = astro.get("tithi_1_end", "")
    t2 = astro.get("tithi_2")
    t2e = astro.get("tithi_2_end", "")
    paksha = pkg
    thParts = ["Tithi: {} ({}, {})".format(t1, paksha, t1e)]
    if t2:
        thParts.append("second tithi: {} (until {})".format(t2, t2e))
    out.append(_line("Paksha " + paksha, thParts[0]))
    if t2: out.append("  {}".format(thParts[1]))

    nak = astro.get("nakshatra", "--")
    naka = astro.get("nakshatra_adhipati", "")
    nakp = astro.get("nakshatra_pada", "")
    nak2 = astro.get("nakshatra_2")
    nak2e = astro.get("nakshatra_2_end", "")
    nak1e = astro.get("nakshatra_1_end", "")
    nakParts = ["Nakshatra: {} (Pada {}, lord {} until {})".format(nak, nakp, naka, nak1e)]
    if nak2:
        nakParts.append("Second: {} (until {})".format(nak2, nak2e))
    out.append(nakParts[0])
    if nak2: out.append("  {}".format(nakParts[1]))

    yog1 = astro.get("yoga", "--")
    yog2 = astro.get("yoga_2")
    yog2e = astro.get("yoga_2_end", "")
    out.append("Yoga: {}".format(yog1))
    if yog2: out.append("  Second: {} (until {})".format(yog2, yog2e))

    out.append("Karana: {}".format(astro.get("karana", "--")))
    mr = astro.get("moon_rashi", "--")
    mra = astro.get("moon_rashi_adhipati", "")
    out.append("Moon in {} (lord {})".format(mr, mra))
    la = astro.get("lagna", "--")
    laa = astro.get("lagna_adhipati", "")
    if la and la != "--":
        out.append("Lagna: {} (lord {})".format(la, laa))
    surya_nak = astro.get("surya_nakshatra")
    if surya_nak: out.append("Surya Nakshatra: {}".format(surya_nak))

    rk = astro.get("rahu_kala")
    yam = astro.get("yamaghanta")
    gul = astro.get("gulika")
    abh = astro.get("abhijit_muhurta")
    brahma = astro.get("brahma_muhurta")
    ghadi = astro.get("ghadi")
    special = []
    if rk: special.append("Rahu Kala: {}".format(rk))
    if yam: special.append("Yamaghanta: {}".format(yam))
    if gul: special.append("Gulika: {}".format(gul))
    if abh: special.append("Abhijit: {}".format(abh))
    if brahma: special.append("Brahma Muhurta: {}".format(brahma))
    if ghadi: special.append("Ghadi: {}".format(ghadi))
    if special:
        out.append(_sec("Special Periods"))
        out.extend(special)

    day_gh = astro.get("day_choghadiya")
    night_gh = astro.get("night_choghadiya")
    if day_gh or night_gh:
        out.append(_sec("Choghadiya"))
        if day_gh:
            out.append("Day:")
            for h in day_gh:
                out.append("  {} {}--{} ({})".format(h.get("name","?"), h.get("start","?"), h.get("end","?"), h.get("nature","")))
        if night_gh:
            out.append("Night:")
            for h in night_gh:
                out.append("  {} {}--{} ({})".format(h.get("name","?"), h.get("start","?"), h.get("end","?"), h.get("nature","")))

    if include_festivals:
        fests = astro.get("festivals") or []
        if fests:
            out.append(_sec("Festivals"))
            for f in fests:
                out.append("  - {} ({}, priority {})".format(f.get("name","?"), f.get("type","?"), f.get("priority","?")))
                if f.get("description"):
                    out.append("    {}".format(_wrap(f["description"], 74)))

    return "\n".join(out)


def _fmt_range_compact(data, cmd="range"):
    """Compact per-day text for range / month."""
    out = []
    if cmd == "month":
        out.append("Monthly Panchanga ({} days)".format(len(data)))
    else:
        out.append("Date Range ({} days)".format(len(data)))
    out.append("Date       Vara      Tithi (Paksha)           Nakshatra       Yoga       Moon")
    out.append("-" * 100)
    for d in data:
        date_s = d.get("date", "--")[:10]
        vaara = d.get("vaara", "")[:8]
        tithi = d.get("tithi", "--")
        paksha = "Shukla" if not d.get("is_krishna_paksha") else "Krishna"
        tithi_s = "{} ({})".format(tithi, paksha)[:24]
        nak = d.get("nakshatra", "--")[:14]
        yoga = d.get("yoga", "--")[:10]
        moon = d.get("moon_rashi", "--")[:12]
        fests = d.get("festivals") or []
        fest_s = " ".join([f.get("name", "")[:20] for f in fests])
        out.append("{} {:<9} {:<24} {:<15} {:<11} {:<13} {}".format(
            date_s, vaara, tithi_s, nak, yoga, moon, fest_s))
    return "\n".join(out)


def _fmt_festivals(data):
    """Text list of festival days."""
    out = []
    days = list(_iter_data(data)) if not isinstance(data, dict) else (data.get("days") or [])
    if not days:
        return "No festivals found in the given range."
    out.append("Festivals ({} days with observances)".format(len(days)))
    out.append("-" * 60)
    for d in days:
        date_s = d.get("date", "--")
        fests = d.get("festivals") or []
        names = [f.get("name", "?") for f in fests]
        out.append("{}  {}".format(date_s, ", ".join(names)))
        for f in fests:
            if f.get("description"):
                out.append("              {}".format(f["description"]))
            rule = f.get("rule")
            if rule:
                out.append("              Rule: {}".format(rule))
    return "\n".join(out)


def _fmt_search_city(results, query):
    """Text display of city search results."""
    out = []
    if not results:
        return "No cities found for '{}'.".format(query)
    out.append("City search results for '{}' ({} found):".format(query, len(results)))
    out.append("-" * 60)
    for c in results:
        name = c.get("name", "?")
        state = c.get("state", "")
        country = c.get("country", "")
        loc = ", ".join(filter(None, [state, country]))
        out.append("{}{}".format(name, " ({})".format(loc) if loc else ""))
        out.append("  Lat: {}  Lon: {}  Alt: {} m  TZ: {}".format(
            c.get("lat", "?"), c.get("lon", "?"), c.get("alt", 0), c.get("tz", "?")))
    return "\n".join(out)


def _fmt_kundali(kd):
    """Kundali text: lagna, planet table, dashas."""
    out = []
    meta = kd.get("meta", {})
    out.append(_sec("Kundali (Natal Chart)"))
    out.append("Date: {}  Timezone: UTC{:+g}".format(
        meta.get("date", "--"), meta.get("timezone_hours", 0)))
    lat = meta.get("lat", "?")
    lon = meta.get("lon", "?")
    out.append("Place: lat {} \u00b0 lon {} \u00b0  Ayanamsa: {} {:.5f}\u00b0".format(
        lat, lon, meta.get("ayanamsa", "?"), meta.get("ayanamsa_value", 0)))
    out.append("Type: {}".format(meta.get("chart_type", "?")))

    la = kd.get("lagna", {})
    out.append(_sec("Lagna"))
    out.append("{} (lord {}) -- {} {}".format(
        la.get("rashi_name", "?"), la.get("lord", "?"),
        la.get("nakshatra_name", "?"), la.get("nakshatra_pada", "")))
    out.append("Longitude: {:.2f}\u00b0".format(la.get("longitude", 0)))

    planets = kd.get("planets", {})
    if planets:
        out.append(_sec("Grahas"))
        header = "{:<10} {:<14} {:>9} {:>6} {:<16} {:>4}".format(
            "Graha", "Rashi", "Degree", "House", "Dignity", "")
        out.append(header)
        out.append("-" * 60)
        for idx in range(9):
            for nm, p in planets.items():
                if p.get("idx") != idx:
                    continue
                ret = "R" if p.get("retrograde") else ""
                ast = "\u2666" if p.get("combust") else ""
                vig = "V" if p.get("is_vargottam") else ""
                flags = "/".join(filter(None, [ret, ast, vig]))
                out.append("{:<10} {:<14} {:>9} {:>6} {:<16} {:>4}".format(
                    p.get("name", "?")[:10],
                    p.get("rashi_name", "?")[:14],
                    _deg(p.get("degree_in_sign")),
                    p.get("house", "?"),
                    p.get("dignity", "")[:16],
                    flags))
        out.append("  (R = Vakri/Retrograde  \u2666 = Asta/Combust  V = Vargottam)")

    karakas = kd.get("karakas")
    if karakas:
        out.append(_sec("Chara Karakas"))
        note = karakas.get("note", "")
        if note:
            out.append(note)
        for scheme in ("eight", "seven"):
            rows = karakas.get(scheme)
            if not rows:
                continue
            out.append("{} ({} signif.):".format(
                "8-Karaka" if scheme == "eight" else "7-Karaka",
                len(rows)))
            for r in rows:
                rahu_tag = " \u2190Rahu (reversed)" if r.get("via_rahu") else ""
                out.append("  {:<2} {:<14} {:<9} {:>8}\u00b0 {:<12} H{:<3}{}".format(
                    r.get("rank"), r.get("karaka", "?")[:14],
                    r.get("planet", "?")[:9], r.get("degree_in_sign", 0),
                    r.get("rashi_name", "?"), r.get("house", "?"), rahu_tag))

    ghat = kd.get("ghatak")
    if ghat:
        out.append(_sec("Ghatak Chakra"))
        out.append("Janma (Moon) rashi: {}".format(ghat.get("janma_rashi", "?")))
        out.append("Ghat Month: {}    Ghat Tithi: {}  / {}".format(
            ghat.get("ghat_maas", "?"),
            ", ".join(map(str, ghat.get("ghat_tithis", []))),
            ", ".join(map(str, ghat.get("ghat_tithis_full", [])))))
        out.append("Ghat Day: {}    Ghat Nakshatra: {}    Ghat Yoga: {}    Ghat Karana: {}".format(
            ghat.get("ghat_vaara", "?"), ghat.get("ghat_nakshatra", "?"),
            ghat.get("ghat_yoga", "?"), ghat.get("ghat_karana", "?")))
        out.append("Ghat Prahar: {}".format(ghat.get("prahar", "?")))
        cm = ghat.get("ghat_chandra_male", {})
        cf = ghat.get("ghat_chandra_female", {})
        out.append("Ghat Chandra (male): {} ({} from sign)    Ghat Chandra (female): {} ({} from sign)".format(
            cm.get("rashi", "?"), cm.get("position", "?"),
            cf.get("rashi", "?"), cf.get("position", "?")))

    dashas = kd.get("dashas")
    if dashas:
        out.append(_sec("Vimshottari Dasha"))
        out.append("Balance: {} Mahadasha ({})".format(
            dashas.get("start_lord", "?"), _ymd_text(dashas.get("balance_duration"))))
        el = dashas.get("elapsed_duration")
        tot = dashas.get("total_years")
        if el is not None: out.append("Elapsed: {}".format(_ymd_text(el)))
        if tot is not None: out.append("Total cycle: {}".format(_ymd_text(KalaChakra.years_to_ymd(tot))))
        mds = dashas.get("mahadashas", [])
        if mds:
            cur = next((m for m in mds if m.get("cur")), mds[0])
            out.append("Currently: {} Mahadasha (running since {})".format(
                cur.get("lord"), cur.get("start_date", "?")))
            out.append("")
            out.append("{:<12} {:<12} {:<12} {:<8}".format(
                "Mahadasha", "Start", "End", ""))
            out.append("-" * 50)
            for m in mds[:9]:
                marker = " <-- now" if m.get("cur") else ""
                out.append("{:<12} {:<12} {:<12}{}".format(
                    m.get("lord", "?"), m.get("start_date", "?"),
                    m.get("end_date", "?"), marker))
            if len(mds) > 9:
                out.append("  ... ({} more)".format(len(mds) - 9))

    vargas = kd.get("vargas")
    if vargas:
        keys = list(vargas.keys())
        out.append(_sec("Vargas ({})".format(", ".join(keys[:8]) + ("..." if len(keys) > 8 else ""))))
        for vk in keys[:6]:
            vd = vargas[vk]
            la2 = vd.get("lagna", {})
            out.append("  {}: Lagna {}".format(vk, la2.get("rashi_name", "?")))

    return "\n".join(out)


def _fmt_analysis(data):
    """Analysis text (highlights + lagna + moon)."""
    out = []
    kd = data.get("kundali", {})
    meta = kd.get("meta", {})
    la = kd.get("lagna", {})
    out.append(_sec("Kundali Analysis"))
    out.append("Date: {} \u00b7 Ayanamsa: {}".format(meta.get("date", "?"), meta.get("ayanamsa", "?")))
    out.append("Lagna: {} (lord {})".format(la.get("rashi_name", "?"), la.get("lord", "?")))

    highlights = (data.get("analysis") or {}).get("highlights") or data.get("highlights") or []
    if highlights:
        out.append(_sec("Highlights"))
        for h in highlights:
            out.append("  \u2022 {}".format(h))
    return "\n".join(out)


def _fmt_bodha(data):
    """Bodha structured reasoning text."""
    out = []
    kd = data.get("kundali", {})
    bodha = data.get("bodha", {})
    meta = kd.get("meta", {})
    la = kd.get("lagna", {})
    out.append(_sec("KalaBodha \u2014 Structured Reasoning"))
    out.append("Date: {} \u00b7 Ayanamsa: {}".format(meta.get("date", "?"), meta.get("ayanamsa", "?")))
    out.append("Lagna: {} (lord {})".format(la.get("rashi_name", "?"), la.get("lord", "?")))

    cd = bodha.get("current_dasha", {})
    if cd:
        out.append("Current Dasha: {} Mahadasha / {} Antardasha / {} Pratyantardasha".format(
            cd.get("mahadasha", "?"), cd.get("antardasha", "?"), cd.get("pratyantardasha", "?")))

    yogas = bodha.get("yogas") or []
    if yogas:
        out.append(_sec("Yogas"))
        for y in yogas:
            name = y.get("name", "?")
            strength = y.get("strength", 0)
            interp = y.get("interpretation", "")
            src = y.get("source", "")
            line = "  \u2022 {} (strength {})".format(name, strength)
            if interp: line += ": {}".format(interp)
            if src: line += " [{}]".format(src)
            out.append(line)

    concs = bodha.get("conjunctions") or []
    if concs:
        out.append(_sec("Conjunctions"))
        for c in concs:
            rname = c.get("rashi_name", "?")
            gn = [KalaKosha.GRAHAS.get("en", {}).get(i, str(i)) if isinstance(KalaKosha.GRAHAS.get("en"), dict) else str(i) for i in c.get("grahas", [])]
            out.append("  {} in {}: {}".format(", ".join(gn), rname,
                       "(same nakshatra)" if c.get("same_nakshatra") else ""))

    evidence = bodha.get("evidence") or []
    if evidence:
        out.append(_sec("Evidence Chain"))
        for e in evidence:
            out.append("  \u2014 {}".format(e.get("statement", "?")))
            for ev in e.get("evidence", []):
                out.append("      Evidence: {}".format(ev))

    answers = bodha.get("answers") or {}
    if answers:
        out.append(_sec("Quick Answers"))
        for k, v in answers.items():
            if k.startswith("_") or isinstance(v, (dict, list)):
                continue
            out.append("  {}: {}".format(k, v))

    sensitivity = data.get("sensitivity")
    if sensitivity:
        out.append(_sec("Birth Time Sensitivity"))
        sens = sensitivity if isinstance(sensitivity, list) else sensitivity.get("checks", [])
        for ch in sens:
            if isinstance(ch, dict):
                out.append("  {} -- {} ({})".format(
                    ch.get("check", "?"), ch.get("verdict", "?"), ch.get("rule", "")))
            else:
                out.append("  {}".format(ch))
    return "\n".join(out)


def _fmt_medha(data):
    """Medha natural-language narrative."""
    out = []
    kd = data.get("kundali", {})
    medha = data.get("medha", {})
    meta = kd.get("meta", {})
    narr = medha.get("narrative", {})
    out.append(_sec("KalaMedha \u2014 AI Reading"))
    out.append("Date: {} \u00b7 Ayanamsa: {}".format(meta.get("date", "?"), meta.get("ayanamsa", "?")))
    out.append("Engine: {} | LLM: {}".format(medha.get("meta", {}).get("engine", "?"),
                                             "yes" if medha.get("meta", {}).get("llm") else "no"))

    lagna = narr.get("lagna", "")
    if lagna:
        out.append(_sec("Lagna"))
        out.append("  {}".format(lagna))

    grahas = narr.get("grahas") or []
    if grahas:
        out.append(_sec("Grahas"))
        for g in grahas:
            out.append("  \u2022 {}".format(g))

    yogas = narr.get("yogas") or []
    if yogas:
        out.append(_sec("Yogas"))
        for y in yogas:
            out.append("  \u2022 {}".format(y))

    dasha = narr.get("dasha", "")
    if dasha:
        out.append(_sec("Dasha"))
        out.append("  {}".format(dasha))

    notes = narr.get("notable_evidence") or []
    if notes:
        out.append(_sec("Notable Evidence"))
        for n in notes:
            out.append("  \u2022 {}".format(n))

    answer = data.get("answer")
    if answer:
        out.append(_sec("Answer"))
        out.append("  {}".format(answer))
    return "\n".join(out)


def _fmt_vidya(data):
    """Vidya concept display."""
    out = []
    if "search" in data:
        results = data["search"]
        q = data.get("query", "")
        count = data.get("count", len(results))
        out.append(_sec("KalaVidya Search"))
        out.append("Query: '{}' ({} results)".format(q, count))
        out.append("-" * 60)
        for r in results:
            out.append("  {} -- {}".format(r.get("id", "?"), r.get("title", "?")))
            if r.get("summary"):
                out.append("    {}".format(_wrap(r["summary"], 72)))
        return "\n".join(out)

    if "catalog" in data:
        cat = data["catalog"]
        cats = data.get("categories", [])
        cat_filter = data.get("category")
        out.append(_sec("KalaVidya Catalog"))
        if cats:
            out.append("Categories: {}".format(", ".join(c.get("id", c) if isinstance(c, dict) else c for c in cats)))
        out.append("Concepts ({}):\n".format(data.get("count", len(cat))))
        for c in cat:
            out.append("  {} -- {}".format(c.get("id", "?"), c.get("title", "?")))
            if c.get("summary"):
                out.append("    {}".format(_wrap(c["summary"], 72)))
        return "\n".join(out)

    entry = data.get("concept", {})
    found = data.get("found", True)
    if not found or not entry:
        return "Concept not found."
    out.append(_sec("KalaVidya \u2014 {}".format(entry.get("title", "?"))))
    out.append("Category: {}".format(entry.get("category_title", entry.get("category", ""))))
    if entry.get("summary"):
        out.append("\n{}".format(_wrap(entry["summary"], 78)))
    if entry.get("detail"):
        out.append("\n{}".format(_wrap(entry["detail"], 78)))
    if entry.get("formula"):
        out.append(_sec("Formula"))
        out.append(entry["formula"])
    if entry.get("example"):
        out.append(_sec("Example"))
        out.append(_wrap(entry["example"], 78))
    if entry.get("source"):
        out.append(_sec("Source"))
        out.append(entry["source"])
    see_also = entry.get("see_also") or []
    if see_also:
        out.append("See also: {}".format(", ".join(see_also)))
    return "\n".join(out)


def _fmt_gochara(data):
    """Gochara transit display."""
    out = []
    kd = data.get("kundali", {})
    gc = data.get("gochara", {})
    meta = kd.get("meta", {})
    out.append(_sec("Gochara \u2014 Planetary Transits"))
    out.append("Transit date: {}".format(gc.get("date", "?")))
    out.append("Natal chart: {} (Lagna {})".format(meta.get("date", "?"),
                                                  kd.get("lagna", {}).get("rashi_name", "?")))
    out.append("Ayanamsa: {}".format(gc.get("ayanamsa", "?")))

    transits = gc.get("transits") or []
    if transits:
        out.append(_sec("Transit Positions"))
        out.append("{:<10} {:<14} {:>9} {:>6} {:<16}".format(
            "Graha", "Rashi", "Degree", "House", "Dignity"))
        out.append("-" * 55)
        for t in transits:
            ret = "R" if t.get("retrograde") else ""
            out.append("{:<10} {:<14} {:>9} {:>6} {:<16} {}".format(
                t.get("name", "?")[:10],
                t.get("rashi_name", "?")[:14],
                _deg(t.get("degree_in_sign")),
                t.get("house", "?"),
                t.get("dignity", "")[:16],
                ret))

    yogas = gc.get("special_yogas") or []
    if yogas:
        out.append(_sec("Special Gochara Yogas"))
        for y in yogas:
            sev = y.get("severity", "low")
            out.append("  \u2022 {} [{}]: {}".format(y.get("name", "?"), sev, y.get("description", "")))

    sign_changes = gc.get("next_sign_changes") or []
    if sign_changes:
        out.append(_sec("Upcoming Sign Changes"))
        for sc in sign_changes:
            out.append("  {} : {} -> {}  on {}".format(
                sc.get("graha", "?"), sc.get("from_rashi", "?"),
                sc.get("to_rashi", "?"), sc.get("date", "?")))

    conj = gc.get("transit_conjunctions") or []
    if conj:
        out.append(_sec("Transit Conjunctions"))
        for c in conj:
            out.append("  {} in {}".format(
                ", ".join(c.get("grahas", [])), c.get("rashi_name", "?")))
    return "\n".join(out)


def _fmt_hora_muhurta(data, cmd="hora"):
    """Hora or muhurta text."""
    out = []
    if cmd == "hora":
        out.append(_sec("Dina Horas"))
    else:
        out.append(_sec("Muhurtas"))
    if cmd == "hora":
        out.append("Sunrise {} \u00b7 Sunset {}".format(
            data.get("sunrise", "?"), data.get("sunset", "?")))
    dl = data.get("day_length_min")
    nl = data.get("night_length_min")
    if dl and nl:
        out.append("Day {} min \u00b7 Night {} min".format(dl, nl))

    if cmd == "hora":
        horas = data.get("day_horas", [])
        n_horas = data.get("night_horas", [])
        out.append("\nDay Horas ({}):".format(len(horas)))
        for h in horas:
            out.append("  {:<8} {}--{}  {}  ({})".format(
                h.get("lord", "?"), h.get("start", "?"), h.get("end", "?"),
                h.get("period", ""), h.get("nature", "")))
        out.append("\nNight Horas ({}):".format(len(n_horas)))
        for h in n_horas:
            out.append("  {:<8} {}--{}  {}  ({})".format(
                h.get("lord", "?"), h.get("start", "?"), h.get("end", "?"),
                h.get("period", ""), h.get("nature", "")))
    else:
        ab = data.get("abhijit", {})
        if ab:
            out.append("Abhijit Muhurta: {}--{}".format(ab.get("start", "?"), ab.get("end", "?")))
        rk = data.get("rahu_kala")
        if rk: out.append("Rahu Kala: {}".format(rk))
        yam = data.get("yamaghanta")
        if yam: out.append("Yamaghanta: {}".format(yam))
        gul = data.get("gulika")
        if gul: out.append("Gulika: {}".format(gul))

        day_m = data.get("day_muhurtas", [])
        night_m = data.get("night_muhurtas", [])
        if day_m:
            out.append("\nDay Muhurtas ({}):".format(len(day_m)))
            for m in day_m:
                out.append("  {:<12} {}--{}  ({})".format(
                    m.get("name", "?"), m.get("start", "?"), m.get("end", "?"),
                    m.get("status", "")))
        if night_m:
            out.append("\nNight Muhurtas ({}):".format(len(night_m)))
            for m in night_m:
                out.append("  {:<12} {}--{}  ({})".format(
                    m.get("name", "?"), m.get("start", "?"), m.get("end", "?"),
                    m.get("status", "")))
    return "\n".join(out)


def _fmt_ashtakoota(data, args):
    """Ashtakoota compatibility text."""
    out = []
    out.append(_sec("Ashtakoota (Guna Milan)"))

    def _party_name(label, d):
        raw = {
            "bride": ("Bride", "bride"),
            "groom": ("Groom", "groom"),
        }
        try:
            yy = int(getattr(args, label + "_year", 0))
            mo = int(getattr(args, label + "_month", 0))
            dd = int(getattr(args, label + "_day", 0))
        except (TypeError, ValueError):
            yy = mo = dd = 0
        if yy:
            bd = "{:02d}-{:02d}-{:04d}".format(dd, mo, yy)
        else:
            bd = None
        rashi = d.get("rashi")
        nak = d.get("nak")
        pada = d.get("pada")
        parts = []
        if rashi is not None and 0 <= rashi < 12:
            parts.append(KalaKosha.RASIS["en"][rashi])
        if nak is not None and 0 <= nak < 27:
            parts.append("{} {}".format(KalaKosha.NAKSHATRAS["en"][nak], pada if pada is not None else ""))
        return ("{}:  {}".format(raw[label][0], " \u00b7 ".join(filter(None, [
            bd, ", ".join(parts) if parts else ""]))))

    out.append(_party_name("bride", data.get("bride", {})))
    out.append(_party_name("groom", data.get("groom", {})))
    scores = data.get("scores", {})
    out.append(_sec("Scores"))
    parts = []
    for k in GUNA_CANONICAL:
        label = GUNA_LABELS.get(k, k)
        parts.append("{} {}".format(label, scores.get(k, 0)))
    out.append("  ".join(parts))

    total = data.get("total", 0)
    verdict = data.get("verdict", "?")
    out.append(_sec("Result"))
    out.append("Total: {} / 36 \u2014 {}".format(total, verdict))
    nd = data.get("nadi_dosha", False)
    ndc = data.get("nadi_dosha_cancelled", False)
    bd = data.get("bhakoot_dosha", False)
    bdc = data.get("bhakoot_dosha_cancelled", False)
    out.append("Nadi Dosha: {} (cancelled: {})".format("yes" if nd else "no", "yes" if ndc else "no"))
    out.append("Bhakoot Dosha: {} (cancelled: {})".format("yes" if bd else "no", "yes" if bdc else "no"))
    return "\n".join(out)


def _fmt_system_info(data):
    """System info text."""
    return "System: {} | Architecture: {} | Processor: {}".format(
        data.get("system", "?"), data.get("architecture", "?"), data.get("processor", "?"))


def format_text(command, data, args):
    """Dispatch to the appropriate text formatter based on command."""
    if command in ("day",):
        return _fmt_day(data, include_festivals=True)
    if command in ("month", "range"):
        return _fmt_range_compact(data if isinstance(data, list) else [data], cmd=command)
    if command == "festivals":
        return _fmt_festivals(data)
    if command == "search-city":
        return _fmt_search_city(data, getattr(args, "q", getattr(args, "query", "?")))
    if command == "kundali":
        return _fmt_kundali(data)
    if command == "analysis":
        return _fmt_analysis(data)
    if command == "bodha":
        return _fmt_bodha(data)
    if command == "medha":
        return _fmt_medha(data)
    if command == "vidya":
        return _fmt_vidya(data)
    if command == "gochara":
        return _fmt_gochara(data)
    if command in ("hora", "muhurta"):
        return _fmt_hora_muhurta(data, cmd=command)
    if command == "ashtakoota":
        return _fmt_ashtakoota(data, args)
    if command == "system-info":
        return _fmt_system_info(data)
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── Engine helpers ───────────────────────────────────────────────────────────

def build_opts(args):
    return {
        "tithi_mode": args.tithi_mode,
        "calendar_system": args.calendar_system,
        "month_system": args.month_system,
        "festival_rule": args.festival_rule,
        "lang": args.lang,
    }


def query_server(port, path, params):
    qs = urllib.parse.urlencode(params)
    url = "http://127.0.0.1:{}{}?{}".format(port, path, qs)
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read()


def compute_day(date_obj, args):
    opts = build_opts(args)
    astro = KalaChakra.calculate_panchanga(
        date_obj.year, date_obj.month, date_obj.day, args.tz, args.lat, args.lon, args.alt,
        opts["tithi_mode"], opts["calendar_system"], opts["month_system"], opts["lang"],
    )
    festivals = KalaUtsavachakra.calculate_festivals(
        astro, args.tz, None, opts["festival_rule"], opts["lang"]
    )
    astro["festivals"] = festivals
    return astro


def compute_range(start, end, args):
    days_data = []
    day = start
    while day <= end:
        days_data.append(compute_day(day, args))
        day += datetime.timedelta(days=1)
    return days_data


def emit(data, args):
    cmd = getattr(args, "command", "")
    if args.format == "text":
        text = format_text(cmd, data, args)
    elif args.format == "csv":
        text = json_rows_to_csv(data if isinstance(data, list) else [data])
    else:
        text = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("Wrote {} to {}".format(args.format.upper(), args.output))
    else:
        sys.stdout.write(text + "\n")


def _norm_date(args, positional_attr, flag_attr):
    """Resolve positional-or-flag date arguments: prefer positional, fall back to flag."""
    pos = getattr(args, positional_attr, None)
    flag = getattr(args, flag_attr, None)
    if pos and not flag:
        setattr(args, flag_attr, pos)
    elif flag and not pos:
        pass  # flag already set
    elif pos and flag:
        if pos != flag:
            print("Warning: {} positional '{}' differs from --{} '{}'; using positional.".format(
                positional_attr, pos, flag_attr, flag), file=sys.stderr)
            setattr(args, flag_attr, pos)


# ── Subcommand handlers ─────────────────────────────────────────────────────

def cmd_day(args):
    _norm_date(args, "pos_date", "date")
    if not args.date:
        print("Error: date is required. Usage: kalayantra-cli day DD-MM-YYYY", file=sys.stderr)
        return 1
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT)}
            params.update(build_opts(args))
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, "/day", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", "replace")
            print("Server error {}: {}".format(e.code, err), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    emit(compute_day(date_obj, args), args)
    return 0


def cmd_month(args):
    if getattr(args, "pos_year", None):
        args.year = args.pos_year
    if getattr(args, "pos_month", None):
        args.month = args.pos_month
    start = datetime.date(args.year, args.month, 1)
    if args.month == 12:
        end = datetime.date(args.year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end = datetime.date(args.year, args.month + 1, 1) - datetime.timedelta(days=1)
    if not args.direct:
        try:
            params = {"year": str(args.year), "month": str(args.month)}
            params.update(build_opts(args))
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, "/month", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    emit(compute_range(start, end, args), args)
    return 0


def cmd_range(args):
    _norm_date(args, "pos_start", "start")
    if not args.start:
        print("Error: --start is required. Usage: kalayantra-cli range --start DD-MM-YYYY", file=sys.stderr)
        return 1
    start = datetime.datetime.strptime(args.start, DATE_FORMAT).date()
    if args.end:
        end = datetime.datetime.strptime(args.end, DATE_FORMAT).date()
    else:
        end = start + datetime.timedelta(days=args.days - 1)
    if end < start:
        start, end = end, start
    if (end - start).days + 1 > 372:
        print("Range limited to 372 days at a time.", file=sys.stderr)
        return 1
    if not args.direct:
        try:
            params = {"start": start.strftime(DATE_FORMAT), "end": end.strftime(DATE_FORMAT)}
            params.update(build_opts(args))
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            payload = query_server(args.port, "/range", params)
            emit(json.loads(payload), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    emit(compute_range(start, end, args), args)
    return 0


def cmd_festivals(args):
    _norm_date(args, "pos_start", "start")
    if not args.start:
        args.start = datetime.date.today().strftime(DATE_FORMAT)
    start = datetime.datetime.strptime(args.start, DATE_FORMAT).date()
    if args.end:
        end = datetime.datetime.strptime(args.end, DATE_FORMAT).date()
    else:
        end = start + datetime.timedelta(days=args.days - 1)
    rows = compute_range(start, end, args)
    festival_days = [row for row in rows if row.get("festivals")]
    if args.format == "csv":
        emit(festival_days, args)
    elif args.format == "text":
        emit({"days": festival_days, "count": len(festival_days)}, args)
    else:
        emit([{"date": row["date"], "festivals": [f["name"] for f in row["festivals"]]} for row in festival_days], args)
    return 0


def cmd_search_city(args):
    _norm_date(args, "pos_q", "q")
    q = args.q
    if not q:
        print("Error: --q is required. Usage: kalayantra-cli search-city <city>", file=sys.stderr)
        return 1
    if not args.direct:
        try:
            emit(json.loads(query_server(args.port, "/search_city", {"q": args.q})), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    results = [c for c in KalaKosha.BUILTIN_CITIES if q.lower() in c["name"].lower()]
    emit(results[:15], args)
    return 0


def cmd_system_info(args):
    info = {
        "architecture": platform.machine(),
        "system": platform.system(),
        "processor": platform.processor(),
    }
    emit(info, args)
    return 0


def cmd_bodha(args):
    _norm_date(args, "pos_date", "date")
    if not args.date:
        print("Error: date is required.", file=sys.stderr)
        return 1
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT), "hour": str(args.hour), "minute": str(args.minute),
                      "ayanamsa": args.ayanamsa, "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            if getattr(args, "sensitivity", False):
                params["sensitivity"] = "true"
            emit(json.loads(query_server(args.port, "/bodha", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    kd = KalaChakra.calculate_kundali(
        date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
        args.tz, args.lat, args.lon, args.alt, ayanamsa=args.ayanamsa, lang=args.lang,
    )
    import KalaBodha
    bodha = KalaBodha.analyze_chart(kd, lang=args.lang)
    response = {"kundali": kd, "bodha": bodha}
    if getattr(args, "sensitivity", False):
        response["sensitivity"] = KalaBodha.birth_time_sensitivity(
            date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
            args.tz, args.lat, args.lon, args.alt,
            ayanamsa=args.ayanamsa, lang=args.lang)
    emit(response, args)
    return 0


def cmd_medha(args):
    _norm_date(args, "pos_date", "date")
    if not args.date:
        print("Error: date is required.", file=sys.stderr)
        return 1
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT), "hour": str(args.hour),
                      "minute": str(args.minute), "ayanamsa": args.ayanamsa, "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            if getattr(args, "question", None):
                params["question"] = args.question
            if getattr(args, "llm", False):
                params["llm"] = "true"
            emit(json.loads(query_server(args.port, "/medha", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")),
                  file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    kd = KalaChakra.calculate_kundali(
        date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
        args.tz, args.lat, args.lon, args.alt, ayanamsa=args.ayanamsa, lang=args.lang,
    )
    import KalaMedha
    response = {"kundali": kd}
    if getattr(args, "llm", False):
        response["medha"] = KalaMedha.medha_with_llm(kd, lang=args.lang)
    else:
        response["medha"] = KalaMedha.medha_analysis(kd, lang=args.lang)
    if getattr(args, "question", None):
        response["answer"] = KalaMedha.answer_question(args.question, kd, lang=args.lang)
    emit(response, args)
    return 0


def cmd_vidya(args):
    import KalaVidya
    if not args.direct:
        try:
            params = {"lang": args.lang}
            if getattr(args, "concept", None):
                params["concept"] = args.concept
            if getattr(args, "category", None):
                params["category"] = args.category
            if getattr(args, "search", None):
                params["q"] = args.search
            emit(json.loads(query_server(args.port, "/vidya", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")),
                  file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    lang = args.lang
    if getattr(args, "concept", None):
        entry = KalaVidya.get_concept(args.concept, lang)
        emit({"concept": entry, "found": entry is not None,
              "categories": KalaVidya.categories(lang)}, args)
    elif getattr(args, "search", None):
        results = KalaVidya.search_concepts(args.search, lang)
        emit({"search": results, "count": len(results), "query": args.search,
              "categories": KalaVidya.categories(lang)}, args)
    else:
        catalog = KalaVidya.concept_catalog(lang, category=getattr(args, "category", None))
        resp = {"catalog": catalog, "count": len(catalog),
                "categories": KalaVidya.categories(lang)}
        if getattr(args, "category", None):
            resp["category"] = args.category
        emit(resp, args)
    return 0


def cmd_kundali(args):
    _norm_date(args, "pos_date", "date")
    if not args.date:
        print("Error: date is required.", file=sys.stderr)
        return 1
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT), "hour": str(args.hour), "minute": str(args.minute),
                      "ayanamsa": args.ayanamsa, "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, "/kundali", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    kd = KalaChakra.calculate_kundali(
        date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
        args.tz, args.lat, args.lon, args.alt, ayanamsa=args.ayanamsa, lang=args.lang,
    )
    emit(kd, args)
    return 0


def cmd_analysis(args):
    _norm_date(args, "pos_date", "date")
    if not args.date:
        print("Error: date is required.", file=sys.stderr)
        return 1
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT), "hour": str(args.hour), "minute": str(args.minute),
                      "ayanamsa": args.ayanamsa, "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, "/analysis", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    kd = KalaChakra.calculate_kundali(
        date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
        args.tz, args.lat, args.lon, args.alt, ayanamsa=args.ayanamsa, lang=args.lang,
    )
    emit({"kundali": kd, "analysis": KalaChakra.generate_analysis(kd, lang=args.lang)}, args)
    return 0


def cmd_day_hora_muhurta(args):
    _norm_date(args, "pos_date", "date")
    if not args.date:
        print("Error: date is required.", file=sys.stderr)
        return 1
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    endpoint = "/hora" if args.command == "hora" else "/muhurta"
    func = KalaChakra.calculate_dina_horas if args.command == "hora" else KalaChakra.calculate_muhurtas
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT), "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, endpoint, params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    data = func(date_obj.year, date_obj.month, date_obj.day,
                args.tz, args.lat, args.lon, args.alt, lang=args.lang)
    emit(data, args)
    return 0


def cmd_ashtakoota(args):
    bride = {"year": args.bride_year, "month": args.bride_month, "day": args.bride_day,
             "hour": args.bride_hour, "minute": args.bride_minute, "tz": args.bride_tz}
    groom = {"year": args.groom_year, "month": args.groom_month, "day": args.groom_day,
             "hour": args.groom_hour, "minute": args.groom_minute, "tz": args.groom_tz}
    if not args.direct:
        try:
            payload = json.dumps({"bride": bride, "groom": groom,
                                  "ayanamsa": args.ayanamsa, "lang": args.lang}).encode()
            req = urllib.request.Request("http://127.0.0.1:{}/ashtakoota".format(args.port),
                                         data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                text = resp.read()
            emit(json.loads(text), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    result = KalaChakra.calculate_ashtakoota(bride, groom, ayanamsa=args.ayanamsa, lang=args.lang)
    emit(result, args)
    return 0


def cmd_gochara(args):
    _norm_date(args, "pos_date", "date")
    if not args.date:
        print("Error: date is required.", file=sys.stderr)
        return 1
    date_obj = datetime.datetime.strptime(args.date, DATE_FORMAT).date()
    if args.transit_date:
        t_obj = datetime.datetime.strptime(args.transit_date, DATE_FORMAT).date()
    else:
        t_obj = date_obj
    if not args.direct:
        try:
            params = {"date": date_obj.strftime(DATE_FORMAT),
                      "hour": str(args.hour), "minute": str(args.minute),
                      "transit_date": t_obj.strftime(DATE_FORMAT),
                      "transit_hour": str(args.transit_hour),
                      "transit_minute": str(args.transit_minute),
                      "ayanamsa": args.ayanamsa, "lang": args.lang}
            for k in ("lat", "lon", "alt", "tz"):
                params[k] = str(getattr(args, k))
            emit(json.loads(query_server(args.port, "/gochara", params)), args)
            return 0
        except urllib.error.HTTPError as e:
            print("Server error {}: {}".format(e.code, e.read().decode("utf-8", "replace")), file=sys.stderr)
            return 1
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
    kd = KalaChakra.calculate_kundali(
        date_obj.year, date_obj.month, date_obj.day, args.hour, args.minute,
        args.tz, args.lat, args.lon, args.alt, ayanamsa=args.ayanamsa, lang=args.lang,
    )
    gochara = KalaChakra.calculate_gochara(
        kd, t_obj.year, t_obj.month, t_obj.day, args.transit_hour, args.transit_minute,
        args.tz, args.lat, args.lon, lang=args.lang, ayanamsa=args.ayanamsa,
    )
    emit({"kundali": kd, "gochara": gochara}, args)
    return 0


# ── Argument parsing ─────────────────────────────────────────────────────────

def add_common(parser):
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="KalaSetu port (default 8642)")
    parser.add_argument("--direct", action="store_true", help="Compute directly instead of querying the daemon")
    parser.add_argument("--lat", type=float, default=23.1765)
    parser.add_argument("--lon", type=float, default=75.7885)
    parser.add_argument("--alt", type=float, default=0.0)
    parser.add_argument("--tz", type=float, default=5.5)
    parser.add_argument("--tithi-mode", default="traditional")
    parser.add_argument("--calendar-system", default="shaka")
    parser.add_argument("--month-system", default="amavasyanta")
    parser.add_argument("--festival-rule", default="vaishnava")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--dasha-depth", type=int, default=3, choices=[3, 4, 5],
                        help="Vimshottari tree depth: 3 MD/AD/PD, 4 +Sukshma, 5 +Prana")
    parser.add_argument("--format", choices=["json", "csv", "text"], default="text",
                        help="Output format: text (default), json, csv")
    parser.add_argument("--output", help="Write to file instead of stdout")


def build_parser():
    p = argparse.ArgumentParser(prog="kalayantra-cli", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_common(p)

    common = argparse.ArgumentParser(add_help=False)
    add_common(common)

    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("day", parents=[common], help="Single day panchanga")
    d.add_argument("pos_date", nargs="?", metavar="DATE", help="DD-MM-YYYY (positional)")
    d.add_argument("--date", help="DD-MM-YYYY")
    d.set_defaults(func=cmd_day)

    m = sub.add_parser("month", parents=[common], help="Whole month panchanga")
    m.add_argument("pos_year", nargs="?", type=int, metavar="YEAR", help="Year (positional)")
    m.add_argument("pos_month", nargs="?", type=int, metavar="MONTH", help="Month 1-12 (positional)")
    m.add_argument("--year", type=int, default=datetime.date.today().year)
    m.add_argument("--month", type=int, default=datetime.date.today().month)
    m.set_defaults(func=cmd_month)

    r = sub.add_parser("range", parents=[common], help="Date range panchanga (up to 372 days)")
    r.add_argument("pos_start", nargs="?", metavar="START", help="Start DD-MM-YYYY (positional)")
    r.add_argument("--start", help="Start DD-MM-YYYY")
    r.add_argument("--end", help="DD-MM-YYYY")
    r.add_argument("--days", type=int, default=1)
    r.set_defaults(func=cmd_range)

    f = sub.add_parser("festivals", parents=[common], help="Only days that have festivals in a range")
    f.add_argument("pos_start", nargs="?", metavar="START", help="Start DD-MM-YYYY (positional)")
    f.add_argument("--start", help="Start DD-MM-YYYY")
    f.add_argument("--end", help="DD-MM-YYYY")
    f.add_argument("--days", type=int, default=365)
    f.set_defaults(func=cmd_festivals)

    c = sub.add_parser("search-city", parents=[common], help="Find a built-in/custom city")
    c.add_argument("pos_q", nargs="?", metavar="CITY", help="City name (positional)")
    c.add_argument("--q", help="City name")
    c.set_defaults(func=cmd_search_city)

    s = sub.add_parser("system-info", parents=[common], help="Runtime system information")
    s.set_defaults(func=cmd_system_info)

    k = sub.add_parser("kundali", parents=[common], help="Natal chart (D1/D3/D9 + vargas + dashas)")
    k.add_argument("pos_date", nargs="?", metavar="DATE", help="Birth date DD-MM-YYYY (positional)")
    k.add_argument("--date", help="Birth date DD-MM-YYYY")
    k.add_argument("--hour", type=float, default=12.0, help="Birth hour (0-23)")
    k.add_argument("--minute", type=float, default=0.0, help="Birth minute")
    k.add_argument("--ayanamsa", default="lahiri",
                   help="lahiri | raman | krishnamurti | true_citra | fagan_bradley | deluce | sayana")
    k.set_defaults(func=cmd_kundali)

    an = sub.add_parser("analysis", parents=[common], help="Offline rule-based chart analysis")
    an.add_argument("pos_date", nargs="?", metavar="DATE", help="Birth date DD-MM-YYYY (positional)")
    an.add_argument("--date", help="Birth date DD-MM-YYYY")
    an.add_argument("--hour", type=float, default=12.0)
    an.add_argument("--minute", type=float, default=0.0)
    an.add_argument("--ayanamsa", default="lahiri")
    an.set_defaults(func=cmd_analysis)

    bo = sub.add_parser("bodha", parents=[common],
                        help="Structured Jyotisa reasoning (KalaBodha)")
    bo.add_argument("pos_date", nargs="?", metavar="DATE", help="Birth date DD-MM-YYYY (positional)")
    bo.add_argument("--date", help="Birth date DD-MM-YYYY")
    bo.add_argument("--hour", type=float, default=12.0)
    bo.add_argument("--minute", type=float, default=0.0)
    bo.add_argument("--ayanamsa", default="lahiri")
    bo.add_argument("--sensitivity", action="store_true",
                    help="Include the birth-time sensitivity report")
    bo.set_defaults(func=cmd_bodha)

    me = sub.add_parser("medha", parents=[common],
                        help="Offline AI reading (KalaMedha) over the evidence graph")
    me.add_argument("pos_date", nargs="?", metavar="DATE", help="Birth date DD-MM-YYYY (positional)")
    me.add_argument("--date", help="Birth date DD-MM-YYYY")
    me.add_argument("--hour", type=float, default=12.0)
    me.add_argument("--minute", type=float, default=0.0)
    me.add_argument("--ayanamsa", default="lahiri")
    me.add_argument("--question", help="Optional natural-language question about the chart")
    me.add_argument("--llm", action="store_true",
                    help="Try the optional local LLM hook (falls back to rules)")
    me.set_defaults(func=cmd_medha)

    vd = sub.add_parser("vidya", parents=[common],
                        help="KalaVidya informational layer -- concepts, formulas and examples")
    vd.add_argument("concept", nargs="?", help="Concept id or title to fetch in full (e.g. tithi)")
    vd.add_argument("--category", help="Filter the catalog by category slug (e.g. panchanga)")
    vd.add_argument("--search", help="Keyword search across titles/summaries")
    vd.set_defaults(func=cmd_vidya)

    gc = sub.add_parser("gochara", parents=[common],
                        help="Gochara -- planetary transits against a natal chart")
    gc.add_argument("pos_date", nargs="?", metavar="DATE", help="Birth date DD-MM-YYYY (positional)")
    gc.add_argument("--date", help="Birth date DD-MM-YYYY")
    gc.add_argument("--hour", type=float, default=12.0, help="Birth hour (0-23)")
    gc.add_argument("--minute", type=float, default=0.0, help="Birth minute")
    gc.add_argument("--transit-date", help="Transit moment DD-MM-YYYY (defaults to birth date)")
    gc.add_argument("--transit-hour", type=float, default=12.0, help="Transit hour (0-23)")
    gc.add_argument("--transit-minute", type=float, default=0.0, help="Transit minute")
    gc.add_argument("--ayanamsa", default="lahiri",
                    help="lahiri | raman | krishnamurti | true_citra | fagan_bradley | deluce | sayana")
    gc.set_defaults(func=cmd_gochara)

    ho = sub.add_parser("hora", parents=[common], help="24 Chaldean dina horas of a day")
    ho.add_argument("pos_date", nargs="?", metavar="DATE", help="DD-MM-YYYY (positional)")
    ho.add_argument("--date", help="DD-MM-YYYY")
    ho.set_defaults(func=cmd_day_hora_muhurta, command="hora")

    mu = sub.add_parser("muhurta", parents=[common], help="30 day/night muhurtas of a day")
    mu.add_argument("pos_date", nargs="?", metavar="DATE", help="DD-MM-YYYY (positional)")
    mu.add_argument("--date", help="DD-MM-YYYY")
    mu.set_defaults(func=cmd_day_hora_muhurta, command="muhurta")

    ak = sub.add_parser("ashtakoota", parents=[common], help="Ashtakoota (Guna Milan) compatibility")
    ak.add_argument("--bride-year", type=int, required=True)
    ak.add_argument("--bride-month", type=int, required=True)
    ak.add_argument("--bride-day", type=int, required=True)
    ak.add_argument("--bride-hour", type=int, default=12, help="Bride birth hour (0-23)")
    ak.add_argument("--bride-minute", type=int, default=0)
    ak.add_argument("--bride-tz", type=float, default=5.5)
    ak.add_argument("--groom-year", type=int, required=True)
    ak.add_argument("--groom-month", type=int, required=True)
    ak.add_argument("--groom-day", type=int, required=True)
    ak.add_argument("--groom-hour", type=int, default=12)
    ak.add_argument("--groom-minute", type=int, default=0)
    ak.add_argument("--groom-tz", type=float, default=5.5)
    ak.add_argument("--ayanamsa", default="lahiri")
    ak.set_defaults(func=cmd_ashtakoota)

    return p


def main():
    args = build_parser().parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
