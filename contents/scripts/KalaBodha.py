# -*- coding: utf-8 -*-
"""
KalaBodha — the structured Jyotiṣa reasoning layer.

KalaBodha transforms a KalaChakra Kundali dict into a machine-readable semantic
representation and an evidence graph.  Every conclusion it produces carries:

    conclusion → chart factors → rule → source/tradition

It never invents astronomical facts: it only reasons over the chart supplied
by KalaChakra.  This is the data layer that KalaMedha (offline AI) and the
desktop tools consume for evidence-backed analysis.

Coverage
--------
    Graha Drishti (Parāśarī 7th-house aspect + special Mangala/Guru/Shani
        aspects; Rāhu/Ketu use the Jaimini 5th/9th convention, labelled as such)
    Graha conjunctions (same-rāśi on D1)
    Graha Yuddha (Bṛhat Jātaka rule, 1° orb, latitude tie-break)
    Graha status markers (Uccha, Neecha, Svakshetra, Moolatrikona, Asta,
        Maargi, Vakri, Vargottama, Digbala)
    Structured Yoga engine (initial curated set, extensible)
    Evidence graph   (statement → factors → rule → source)
    Programmatic query API   (milestone: "Where is Shani?", "Is Shani Asta?",
        "What does Shani aspect?", "What Vargas contain Shani?", ...)
    Birth-time sensitivity (#42): stable vs unstable factors over ± minutes

Public API surface (used by KalaSetu, CLI, and tests):
    analyze_chart(kundali, lang='en')
    graha_fact_sheet(idx, kundali, lang='en')
    query_chart(kundali, lang='en')        → answers dict
    birth_time_sensitivity(year, month, day, hour, minute, tz, lat, lon, alt,
                           ayanamsa='lahiri', lang='en',
                           span_minutes=15, step=5)
"""

from __future__ import annotations

import math

import KalaKosha

# ---------------------------------------------------------------------------
#  Classical rule tables (data only; the reasoning lives below)
# ---------------------------------------------------------------------------

# Graha Drishti — the 7th house (6 signs forward) is aspected by every graha.
# Mangala extra: 4th, 8th.  Guru extra: 5th, 9th.  Shani extra: 3rd, 10th.
# Rāhu/Ketu: Jaimini convention — 5th and 9th (labelled separately).
_ASPECT_OFFSETS = {
    0: {7},          # Surya
    1: {7},          # Chandra
    2: {4, 7, 8},    # Mangala
    3: {7},          # Budha
    4: {5, 7, 9},    # Guru
    5: {7},          # Shukra
    6: {3, 7, 10},   # Shani
    7: {5, 9},       # Rahu (Jaimini)
    8: {5, 9},       # Ketu (Jaimini)
}
_ASPECT_SOURCES = {
    0: "Parāśarī Hora Śāstra: 7th aspect",
    1: "Parāśarī Hora Śāstra: 7th aspect",
    2: "Parāśarī Hora Śāstra: full then 4th, 7th, 8th aspects",
    3: "Parāśarī Hora Śāstra: 7th aspect",
    4: "Parāśarī Hora Śāstra: 5th, 7th, 9th aspects",
    5: "Parāśarī Hora Śāstra: 7th aspect",
    6: "Parāśarī Hora Śāstra: 3rd, 7th, 10th aspects",
    7: "Jaimini convention: 5th and 9th aspects",
    8: "Jaimini convention: 5th and 9th aspects",
}

# Graha Yuddha — Bṛhat Jātaka: only these five grahas wage war.
_YUDDHA_PARTICIPANTS = {2, 3, 4, 5, 6}
_YUDDHA_ORB_DEG = 1.0

# Directional strength (Digbala) — the house in which each graha is strongest.
_DIGBALA_HOUSE = {0: 10, 1: 4, 2: 10, 3: 1, 4: 1, 5: 4, 6: 7}

_KENDRA = {1, 4, 7, 10}
_TRIKONA = {1, 5, 9}
_DUSTHANA = {6, 8, 12}

# Pancha Mahapurusha pairing.
_PANCHA_MAHAPURUSHA = {
    2: "Ruchaka",   # Mangala
    3: "Bhadra",    # Budha
    4: "Hamsa",     # Guru
    5: "Malavya",   # Shukra
    6: "Sasa",      # Shani
}

# ---------------------------------------------------------------------------
#  Chart context
# ---------------------------------------------------------------------------

def _normalize_planets(kundali: dict) -> dict:
    """Return {idx: planet_dict} preserving every field, language-independent."""
    result = {}
    for name, p in kundali.get("planets", {}).items():
        idx = p.get("idx")
        if idx is not None:
            result[int(idx)] = dict(p)
    for idx in range(9):
        if idx not in result:
            result[idx] = {
                "idx": idx,
                "name": KalaKosha.GRAHAS["en"][idx],
                "rashi": None, "house": None, "longitude": None,
                "retrograde": False, "combust": False, "is_vargottam": False,
            }
    return result


def _build_context(kundali: dict, lang: str = "en") -> dict:
    """Normalize a Kundali dict into the KalaBodha working context."""
    planets = _normalize_planets(kundali)
    lagna = kundali.get("lagna", {}) or {}
    houses = {}
    for h, hd in (kundali.get("houses", {}) or {}).items():
        houses[int(h)] = hd

    lord_of_house = {int(h): hd.get("lord_idx") for h, hd in houses.items()}

    varga = {}
    for vk, vdata in (kundali.get("vargas", {}) or {}).items():
        vplanets = {}
        for name, vp in (vdata or {}).get("planets", {}).items():
            idx = None
            if name == "Lagna":
                idx = "Lagna"
            else:
                for i in range(9):
                    if KalaKosha.GRAHAS["en"][i] == name:
                        idx = i
                        break
                if idx is None:
                    for i in range(9):
                        if KalaKosha.GRAHAS[lang][i] == name:
                            idx = i
                            break
            if idx is not None:
                vplanets[idx] = vp.get("rashi")
        if vdata and vdata.get("lagna") is not None:
            vplanets["Lagna"] = vdata["lagna"].get("rashi")
        if vplanets:
            varga[vk] = vplanets

    md = None
    ad = None
    pd = None
    for m in (kundali.get("dashas", {}) or {}).get("mahadashas", []):
        if m.get("is_current"):
            md = m
            for a in m.get("antardashas", []):
                if a.get("is_current"):
                    ad = a
                    for p in a.get("pratyantardashas", []):
                        if p.get("is_current"):
                            pd = p
                            break
                    break
            break

    return {
        "lang": lang,
        "kundali": kundali,
        "planets": planets,
        "lagna_rashi": lagna.get("rashi"),
        "lagna_lord": lagna.get("lord_idx"),
        "houses": houses,
        "lord_of_house": lord_of_house,
        "varga": varga,
        "current_dasha": {
            "mahadasha": md.get("lord_idx") if md else None,
            "antardasha": ad.get("lord_idx") if ad else None,
            "pratyantardasha": pd.get("lord_idx") if pd else None,
        },
    }


def _house_from_lagna(rashi: int, lagna_rashi: int) -> int | None:
    if rashi is None or lagna_rashi is None:
        return None
    return (int(rashi) - int(lagna_rashi)) % 12 + 1


def _moon_relative_house(rashi: int, moon_rashi: int) -> int | None:
    if rashi is None or moon_rashi is None:
        return None
    return (int(rashi) - int(moon_rashi)) % 12 + 1


def _rashi_lord(rashi: int) -> int:
    return KalaKosha.RASHI_LORD[rashi % 12]


def _debilitated_sign(idx: int) -> int | None:
    ex = KalaKosha.EXALTATION_SIGN[idx]
    if ex is None:
        return None
    return (ex + 6) % 12


# ---------------------------------------------------------------------------
#  Graha Drishti
# ---------------------------------------------------------------------------

def _aspect_offsets(idx: int) -> set:
    return set(_ASPECT_OFFSETS.get(idx, {7}))


def _aspect_target_rashis(rashi: int, offsets: set) -> list:
    if rashi is None:
        return []
    return sorted((int(rashi) + off - 1) % 12 for off in offsets)


def _with_source(idx: int) -> str:
    return _ASPECT_SOURCES.get(idx, "Parāśarī Hora Śāstra")


def compute_drishti(ctx: dict) -> dict:
    """Return {'outgoing': {idx: [...], 'incoming': {idx: [...]}} and the
    per-rāśi aspect map used for evidence."""
    planets = ctx["planets"]
    outgoing = {}
    incoming = {i: [] for i in range(9)}
    for idx in range(9):
        rashi = planets[idx].get("rashi")
        if rashi is None:
            outgoing[idx] = []
            continue
        targets = _aspect_target_rashis(rashi, _aspect_offsets(idx))
        outgoing[idx] = targets
        for t in targets:
            for j in range(9):
                if j == idx:
                    continue
                if planets[j].get("rashi") == t:
                    incoming[j].append(idx)
    for idx in range(9):
        incoming[idx] = sorted(set(incoming[idx]))
    return {"outgoing": outgoing, "incoming": incoming}


# ---------------------------------------------------------------------------
#  Conjunctions (same-rāśi on D1)
# ---------------------------------------------------------------------------

def compute_conjunctions(ctx: dict) -> list:
    planets = ctx["planets"]
    groups = {}
    for idx in range(9):
        rashi = planets[idx].get("rashi")
        if rashi is None:
            continue
        groups.setdefault(rashi, []).append(idx)
    result = []
    for rashi in sorted(groups):
        members = groups[rashi]
        if len(members) >= 2:
            nakshatra_union = {planets[i].get("nakshatra") for i in members}
            result.append({
                "rashi": rashi,
                "rashi_name": KalaKosha.RASIS[ctx["lang"]][rashi],
                "grahas": members,
                "same_nakshatra": len(nakshatra_union) == 1,
            })
    return result


# ---------------------------------------------------------------------------
#  Graha Yuddha (Bṛhat Jātaka)
# ---------------------------------------------------------------------------

def _ecliptic_latitude(idx: int, jd_ut: float) -> float:
    """Ecliptic latitude of a graha at jd_ut (Swiss Ephemeris)."""
    import swisseph as swe
    ids = {0: swe.SUN, 1: swe.MOON, 2: swe.MARS, 3: swe.MERCURY,
           4: swe.JUPITER, 5: swe.VENUS, 6: swe.SATURN, 7: swe.MEAN_NODE}
    if idx == 8:
        res = swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SWIEPH)
        return -res[0][1]
    res = swe.calc_ut(jd_ut, ids[idx], swe.FLG_SWIEPH)
    return res[0][1]


def compute_yuddhas(ctx: dict) -> list:
    """Graha Yuddha between the five yuddha-participating grahas.

    Rule (Bṛhat Jātaka, Muhūrta): if two of them occupy the same rāśi and are
    within 1° of each other, war occurs. The graha with the higher (more
    northern) ecliptic latitude wins — unless that graha is retrograde, in
    which case the other graha wins.
    """
    planets = ctx["planets"]
    jd_ut = (ctx["kundali"].get("meta", {}) or {}).get("jd_ut")
    result = []
    members = sorted(i for i in _YUDDHA_PARTICIPANTS
                     if planets[i].get("longitude") is not None)
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            a, b = members[i], members[j]
            if planets[a].get("rashi") != planets[b].get("rashi"):
                continue
            sep = abs(planets[a]["longitude"] - planets[b]["longitude"])
            sep = min(sep, 360.0 - sep)
            if sep > _YUDDHA_ORB_DEG:
                continue
            lat_a = lat_b = 0.0
            if jd_ut:
                lat_a = _ecliptic_latitude(a, jd_ut)
                lat_b = _ecliptic_latitude(b, jd_ut)
            winner = None
            loser = None
            if abs(lat_a - lat_b) < 1e-9 and not jd_ut:
                winner, loser = None, None
            else:
                if lat_a > lat_b:
                    candidate, other = a, b
                else:
                    candidate, other = b, a
                if planets[candidate].get("retrograde"):
                    winner, loser = other, candidate
                else:
                    winner, loser = candidate, other
            result.append({
                "graha_a": a,
                "graha_b": b,
                "name_a": KalaKosha.GRAHAS[ctx["lang"]][a],
                "name_b": KalaKosha.GRAHAS[ctx["lang"]][b],
                "rashi": planets[a]["rashi"],
                "rashi_name": KalaKosha.RASIS[ctx["lang"]][planets[a]["rashi"]],
                "separation_deg": round(sep, 4),
                "latitude_a": round(lat_a, 4),
                "latitude_b": round(lat_b, 4),
                "rule": "Bṛhat Jātaka: same-rāśi occupants within 1°; higher "
                        "ecliptic latitude wins unless it is retrograde",
                "winner": winner,
                "loser": loser,
                "winner_name": KalaKosha.GRAHAS[ctx["lang"]][winner] if winner is not None else None,
                "loser_name": KalaKosha.GRAHAS[ctx["lang"]][loser] if loser is not None else None,
            })
    return result


# ---------------------------------------------------------------------------
#  Graha status markers (Uccha / Neecha / Svakshetra / ... / Digbala)
# ---------------------------------------------------------------------------

def _sign_ownership(idx: int, rashi: int, lang: str) -> str | None:
    """Return one of moolatrikona / svakshetra / shatrukshetra / mitrakshetra /
    neutral, or None for nodes."""
    if idx >= 7:
        return None
    mt = KalaKosha.MOOLATRIKONA_SIGN.get(idx)
    own = KalaKosha.OWN_SIGNS.get(idx, [])
    if rashi in own:
        return "moolatrikona" if rashi == mt else "svakshetra"
    friend_planets = KalaKosha.GRAHA_FRIENDS.get(idx, set())
    for f in friend_planets:
        if rashi in KalaKosha.OWN_SIGNS.get(f, []):
            return "mitrakshetra"
    enemy_planets = KalaKosha.GRAHA_ENEMIES.get(idx, set())
    for e in enemy_planets:
        if rashi in KalaKosha.OWN_SIGNS.get(e, []):
            return "shatrukshetra"
    return "neutral"


def compute_graha_status(ctx: dict) -> dict:
    """Per-graha list of classical status markers with evidence."""
    planets = ctx["planets"]
    lang = ctx["lang"]
    result = {}
    for idx in range(9):
        p = planets[idx]
        rashi = p.get("rashi")
        statuses = []
        if rashi is None:
            result[idx] = statuses
            continue

        if p.get("combust") or p.get("asta"):
            statuses.append({"name": "Asta", "rule": "Within the Sun's combustion orb",
                             "evidence": f"{KalaKosha.GRAHAS[lang][idx]} within combustion orb of Surya"})
        if p.get("retrograde"):
            statuses.append({"name": "Vakri", "rule": "Apparent retrograde motion (negative daily speed)",
                             "evidence": f"{KalaKosha.GRAHAS[lang][idx]} is retrograde"})
        else:
            statuses.append({"name": "Maargi", "rule": "Apparent direct motion",
                             "evidence": f"{KalaKosha.GRAHAS[lang][idx]} is direct"})

        if idx < 7:
            if _debilitated_sign(idx) == rashi:
                statuses.append({"name": "Neecha", "rule": "Graha in the sign of its debilitation",
                                 "evidence": f"{KalaKosha.GRAHAS[lang][idx]} in {KalaKosha.RASIS[lang][rashi]}, the sign of debilitation"})
            else:
                ex = KalaKosha.EXALTATION_SIGN[idx]
                if ex == rashi:
                    statuses.append({"name": "Uccha", "rule": "Graha in its sign of exaltation",
                                     "evidence": f"{KalaKosha.GRAHAS[lang][idx]} exalted in {KalaKosha.RASIS[lang][rashi]}"})
                ownership = _sign_ownership(idx, rashi, lang)
                if ownership == "moolatrikona":
                    statuses.append({"name": "Moolatrikona", "rule": "Graha in its moolatrikona sign",
                                     "evidence": f"{KalaKosha.GRAHAS[lang][idx]} in its moolatrikona {KalaKosha.RASIS[lang][rashi]}"})
                elif ownership == "svakshetra":
                    statuses.append({"name": "Svakshetra", "rule": "Graha in its own sign",
                                     "evidence": f"{KalaKosha.GRAHAS[lang][idx]} in own sign {KalaKosha.RASIS[lang][rashi]}"})

        if p.get("is_vargottam"):
            statuses.append({"name": "Vargottama", "rule": "Same rāśi in D1 and D9",
                             "evidence": f"{KalaKosha.GRAHAS[lang][idx]} occupies {KalaKosha.RASIS[lang][rashi]} in both D1 and D9"})

        house = p.get("house")
        if idx in _DIGBALA_HOUSE and house == _DIGBALA_HOUSE[idx]:
            statuses.append({"name": "Digbala", "rule": "Graha in its directional-strength house",
                             "evidence": f"{KalaKosha.GRAHAS[lang][idx]} in the {_DIGBALA_HOUSE[idx]}th house of directional strength"})

        result[idx] = statuses
    return result


# ---------------------------------------------------------------------------
#  Varga summary (which rāśi a graha occupies in every varga)
# ---------------------------------------------------------------------------

def _varga_rashi_name(vk: str, rashi: int, lang: str) -> str:
    if rashi is None:
        return "--"
    return KalaKosha.RASIS[lang][rashi % 12]


# ---------------------------------------------------------------------------
#  Structured Yoga engine
# ---------------------------------------------------------------------------

def _evaluate_pancha_mahapurusha(ctx) -> list:
    planets = ctx["planets"]
    out = []
    for idx, name in _PANCHA_MAHAPURUSHA.items():
        p = planets[idx]
        rashi = p.get("rashi")
        if rashi is None:
            continue
        ownership = _sign_ownership(idx, rashi, ctx["lang"]) if idx < 7 else None
        dignified = ownership in ("moolatrikona", "svakshetra") or \
            KalaKosha.EXALTATION_SIGN[idx] == rashi
        if dignified and p.get("house") in _KENDRA:
            out.append({
                "id": "pancha_mahapurusha",
                "name": f"{name} Yoga",
                "strength": 3,
                "participants": [idx],
                "source": "Phaladīpikā",
                "tradition": "Parāśarī",
                "condition": (f"{KalaKosha.GRAHAS[ctx['lang']][idx]} in own/exalted/moolatrikona"
                              f" {KalaKosha.RASIS[ctx['lang']][rashi]} placed in a kendra"),
                "exception": "",
                "interpretation": "One of the five Mahāpuruṣa Yogas conferring a strong, self-made personality through the dispositor of its planet.",
                "evidence": [f"{KalaKosha.GRAHAS[ctx['lang']][idx]} in {KalaKosha.RASIS[ctx['lang']][rashi]}, "
                             f"{p.get('house')}th house"],
            })
    return out


def _moon_house(ctx, idx) -> int | None:
    return _moon_relative_house(ctx["planets"][idx].get("rashi"),
                                ctx["planets"][1].get("rashi"))


def _planet_at_house(ctx, house_set, relative_to="lagna") -> list:
    """All grahas whose house (from lagna or from Chandra) falls in house_set."""
    planets = ctx["planets"]
    out = []
    for idx in range(1, 9):
        if relative_to == "moon":
            h = _moon_house(ctx, idx)
        else:
            h = planets[idx].get("house")
        if h in house_set:
            out.append(idx)
    return out


def _evaluate_gajakesari(ctx) -> list:
    guru_house_moon = _moon_house(ctx, 4)
    if guru_house_moon in _KENDRA:
        return [{
            "id": "gajakesari", "name": "Gajakesari Yoga", "strength": 3,
            "participants": [4, 1],
            "source": "Phaladīpikā", "tradition": "Parāśarī",
            "condition": "Guru placed in a kendra (1/4/7/10) from Chandra",
            "exception": "Result is tempered if Guru is combust or in a dusthāna from Lagna",
            "interpretation": "Elephant's mount: dignity, renown, intelligence and leadership.",
            "evidence": [f"Guru in {KalaKosha.RASIS[ctx['lang']][ctx['planets'][4].get('rashi')]}, "
                         f"{guru_house_moon}th from Chandra"],
        }]
    return []


def _evaluate_budhaditya(ctx) -> list:
    if ctx["planets"][3].get("rashi") == ctx["planets"][0].get("rashi") and \
            ctx["planets"][3].get("rashi") is not None:
        r = ctx["planets"][3]["rashi"]
        return [{
            "id": "budhaditya", "name": "Budhāditya Yoga", "strength": 2,
            "participants": [3, 0],
            "source": "Bṛhat Jātaka", "tradition": "Parāśarī",
            "condition": "Budha in the same rāśi as Surya",
            "exception": "",
            "interpretation": "Sharp intellect, eloquence and administrative success.",
            "evidence": [f"Budha and Surya together in {KalaKosha.RASIS[ctx['lang']][r]}"],
        }]
    return []


def _evaluate_chandramangala(ctx) -> list:
    m = ctx["planets"][1].get("rashi")
    k = ctx["planets"][2].get("rashi")
    if m is None or k is None:
        return []
    same = m == k
    opposite = (m - k) % 12 == 6
    if same or opposite:
        return [{
            "id": "chandra_mangala", "name": "Chandra–Mangala Yoga", "strength": 2,
            "participants": [1, 2],
            "source": "Sarāvalī", "tradition": "Parāśarī",
            "condition": "Chandra and Mangala in the same rāśi or in mutual opposition",
            "exception": "",
            "interpretation": "Bold, energetic temperament; material gains with courage.",
            "evidence": [f"Chandra in {KalaKosha.RASIS[ctx['lang']][m]}, "
                         f"Mangala in {KalaKosha.RASIS[ctx['lang']][k]}"],
        }]
    return []


def _evaluate_adhi(ctx) -> list:
    occupants = _planet_at_house(ctx, {6, 7, 8}, relative_to="moon")
    benefics = [i for i in occupants if i in (3, 4, 5)]
    if benefics:
        return [{
            "id": "adhi_yoga", "name": "Adhi Yoga", "strength": 3,
            "participants": benefics,
            "source": "Phaladīpikā", "tradition": "Parāśarī",
            "condition": "Natural benefics (Budha/Guru/Shukra) in 6th, 7th or 8th from Chandra",
            "exception": "",
            "interpretation": "Wealth, health, influence and freedom from disease.",
            "evidence": [f"{KalaKosha.GRAHAS[ctx['lang']][i]} in the "
                         f"{_moon_house(ctx, i)}th from Chandra" for i in benefics],
        }]
    return []


def _evaluate_moon_yogas(ctx) -> list:
    """Sunaphā / Anaphā / Durudhara / Kemadruma — combined."""
    planets = ctx["planets"]
    two_from_moon = [i for i in range(9) if i != 1 and _moon_house(ctx, i) == 2]
    twelve_from_moon = [i for i in range(9) if i != 1 and _moon_house(ctx, i) == 12]
    kendra_from_moon = [i for i in range(9) if i != 1 and _moon_house(ctx, i) in _KENDRA]

    out = []
    if two_from_moon:
        out.append({
            "id": "sunapha", "name": "Sunaphā Yoga", "strength": 1,
            "participants": two_from_moon, "source": "Bṛhat Jātaka",
            "tradition": "Parāśarī",
            "condition": "A graha in the 2nd from Chandra",
            "exception": "", "interpretation": "Intelligence, wealth and self-effort.",
            "evidence": [f"{KalaKosha.GRAHAS[ctx['lang']][i]} in 2nd from Chandra"
                         for i in two_from_moon],
        })
    if twelve_from_moon:
        out.append({
            "id": "anapha", "name": "Anaphā Yoga", "strength": 1,
            "participants": twelve_from_moon, "source": "Bṛhat Jātaka",
            "tradition": "Parāśarī",
            "condition": "A graha in the 12th from Chandra",
            "exception": "", "interpretation": "Self-restraint, contentment and steady gains.",
            "evidence": [f"{KalaKosha.GRAHAS[ctx['lang']][i]} in 12th from Chandra"
                         for i in twelve_from_moon],
        })
    if two_from_moon and twelve_from_moon:
        out.append({
            "id": "durudhara", "name": "Duruḍharā Yoga", "strength": 2,
            "participants": two_from_moon + twelve_from_moon,
            "source": "Bṛhat Jātaka", "tradition": "Parāśarī",
            "condition": "Grahas in both the 2nd and the 12th from Chandra",
            "exception": "", "interpretation": "Prosperity and enduring reputation.",
            "evidence": [f"{KalaKosha.GRAHAS[ctx['lang']][i]} in 2nd from Chandra" for i in two_from_moon]
                        + [f"{KalaKosha.GRAHAS[ctx['lang']][i]} in 12th from Chandra" for i in twelve_from_moon],
        })
    if not two_from_moon and not twelve_from_moon and not kendra_from_moon:
        out.append({
            "id": "kemadruma", "name": "Kemadruma Yoga", "strength": 1,
            "participants": [1], "source": "Bṛhat Jātaka", "tradition": "Parāśarī",
            "condition": "No graha in a kendra from Chandra and none in the 2nd from Chandra",
            "exception": "Neutralised if Chandra is dignified or aspected by a benefic",
            "interpretation": "Austerity, solitude and fluctuating fortune (tempered by noble conduct).",
            "evidence": ["No graha in a kendra or 2nd house from Chandra"],
        })
    return out


def _evaluate_neecha_bhanga(ctx) -> list:
    planets = ctx["planets"]
    out = []
    for idx in range(7):
        rashi = planets[idx].get("rashi")
        if rashi is None or _debilitated_sign(idx) != rashi:
            continue
        dispositor = _rashi_lord(rashi)
        dis_rashi = planets[dispositor].get("rashi")
        dis_house = planets[dispositor].get("house")
        dis_exalted = KalaKosha.EXALTATION_SIGN[dispositor] == dis_rashi if dispositor < 7 else False
        conds = []
        if dis_house in _KENDRA:
            conds.append("dispositor in a kendra from Lagna")
        if dis_exalted:
            conds.append("dispositor exalted")
        if _moon_house(ctx, idx) in _KENDRA:
            conds.append("graha in a kendra from Chandra")
        if conds:
            out.append({
                "id": "neecha_bhanga", "name": "Neecha Bhanga Raja Yoga", "strength": 3 if len(conds) >= 2 else 2,
                "participants": [idx, dispositor],
                "source": "Jātaka Pārījāta", "tradition": "Parāśarī",
                "condition": "; ".join(conds),
                "exception": "",
                "interpretation": "Cancellation of debilitation — the graha operates instead like a benefic lord.",
                "evidence": [f"{KalaKosha.GRAHAS[ctx['lang']][idx]} debilitated in "
                             f"{KalaKosha.RASIS[ctx['lang']][rashi]}; dispositor "
                             f"{KalaKosha.GRAHAS[ctx['lang']][dispositor]} "
                             f"{KalaKosha.RASIS[ctx['lang']][dis_rashi] if dis_rashi is not None else '--'}"] +
                            [f"condition: {c}" for c in conds],
            })
    return out


def _evaluate_vipareeta(ctx) -> list:
    lord_of = ctx["lord_of_house"]
    involved = [h for h in (6, 8, 12) if lord_of.get(h) is not None]
    occupants = [lord_of[h] for h in involved
                 if lord_of.get(h) in _planet_at_house(ctx, _DUSTHANA)]
    if occupants:
        return [{
            "id": "vipareeta", "name": "Vipareeta Raja Yoga", "strength": 2 if len(occupants) <= 2 else 3,
            "participants": occupants,
            "source": "Phaladīpikā", "tradition": "Parāśarī",
            "condition": "Lords of the dusthānas (6/8/12) placed in the dusthānas",
            "exception": "",
            "interpretation": "Adversity is converted into success; gains after struggle.",
            "evidence": [f"{KalaKosha.GRAHAS[ctx['lang']][x]} is a dusthāna lord placed in a dusthāna"
                         for x in occupants],
        }]
    return []


def _mutual_aspect(a: int, b: int, drishti: dict) -> bool:
    return b in drishti["incoming"].get(a, []) and a in drishti["incoming"].get(b, [])


def _evaluate_raja_yoga(ctx) -> list:
    lord_of = ctx["lord_of_house"]
    kendra_lords = {lord_of[h] for h in (1, 4, 7, 10) if lord_of.get(h) is not None}
    trikona_lords = {lord_of[h] for h in (1, 5, 9) if lord_of.get(h) is not None}
    planets = ctx["planets"]
    drishti = ctx["_drishti"]
    out = []
    for k in kendra_lords:
        for t in trikona_lords:
            if k == t:
                continue
            same_sign = (planets[k].get("rashi") is not None
                         and planets[k].get("rashi") == planets[t].get("rashi"))
            parivartana = (planets[k].get("rashi") in KalaKosha.OWN_SIGNS.get(t, [])
                           and planets[t].get("rashi") in KalaKosha.OWN_SIGNS.get(k, []))
            if same_sign or parivartana or _mutual_aspect(k, t, drishti):
                ra = planets[k].get("rashi")
                out.append({
                    "id": "raja_yoga", "name": "Raja Yoga (kendra–trikona)", "strength": 2,
                    "participants": [k, t],
                    "source": "Bṛhat Jātaka", "tradition": "Parāśarī",
                    "condition": "A kendra lord and a trikona lord conjunct, exchange signs, or mutually aspect",
                    "exception": "",
                    "interpretation": "Authority, status and success through rulership qualities.",
                    "evidence": [f"{KalaKosha.GRAHAS[ctx['lang']][k]} (kendra lord) and "
                                 f"{KalaKosha.GRAHAS[ctx['lang']][t]} (trikona lord) "
                                 f"{'conjunct' if same_sign else 'in exchange/mutual aspect'} "
                                 f"{'in ' + KalaKosha.RASIS[ctx['lang']][ra] if ra is not None else ''}"],
                })
                break
    return out


def _evaluate_dhana(ctx) -> list:
    lord_of = ctx["lord_of_house"]
    planets = ctx["planets"]
    by_lord = {}
    for h in (2, 9, 11):
        lord = lord_of.get(h)
        if lord is not None and planets[lord].get("house") in (_KENDRA | _TRIKONA):
            by_lord.setdefault(lord, []).append(h)
    if by_lord:
        lords = sorted(by_lord)
        return [{
            "id": "dhana_yoga", "name": "Dhana Yoga", "strength": 2,
            "participants": lords,
            "source": "Bṛhat Jātaka", "tradition": "Parāśarī",
            "condition": "Lord of the 2nd, 9th or 11th house in a kendra or trikona from Lagna",
            "exception": "",
            "interpretation": "Wealth and stable finances through the houses involved.",
            "evidence": [f"{KalaKosha.GRAHAS[ctx['lang']][l]} — lord of the "
                         f"{', '.join(f'{h}th' for h in by_lord[l])} — in the "
                         f"{planets[l].get('house')}th house" for l in lords],
        }]
    return []


def compute_yogas(ctx: dict, drishti: dict) -> list:
    ctx["_drishti"] = drishti
    evaluators = [
        _evaluate_pancha_mahapurusha,
        _evaluate_gajakesari,
        _evaluate_budhaditya,
        _evaluate_chandramangala,
        _evaluate_adhi,
        _evaluate_moon_yogas,
        _evaluate_neecha_bhanga,
        _evaluate_vipareeta,
        _evaluate_raja_yoga,
        _evaluate_dhana,
    ]
    result = []
    for fn in evaluators:
        result.extend(fn(ctx))
    return result


# ---------------------------------------------------------------------------
#  Per-graha semantic fact sheet  (#33, #104)
# ---------------------------------------------------------------------------

def graha_fact_sheet(idx: int, ctx: dict, drishti: dict | None = None,
                     conjunctions: list | None = None,
                     yogas: list | None = None,
                     yuddhas: list | None = None,
                     varga: dict | None = None) -> dict:
    """Machine-readable representation of every axis / status of one graha."""
    lang = ctx["lang"]
    planets = ctx["planets"]
    p = planets[idx]
    rashi = p.get("rashi")
    house = p.get("house")
    statuses = compute_graha_status(ctx).get(idx, [])

    if drishti is None:
        drishti = compute_drishti(ctx)
    aspects_out = []
    for t in drishti["outgoing"].get(idx, []):
        aspects_out.append({
            "rashi": t,
            "rashi_name": KalaKosha.RASIS[lang][t],
            "offset": (t - rashi) % 12 if rashi is not None else None,
        })
    aspects_in = [KalaKosha.GRAHAS[lang][j] for j in drishti["incoming"].get(idx, [])]

    conj = []
    for group in (conjunctions or []):
        if idx in group["grahas"]:
            conj = [KalaKosha.GRAHAS[lang][x] for x in group["grahas"] if x != idx]
            break

    yuddha = None
    for w in (yuddhas or []):
        if idx in (w["graha_a"], w["graha_b"]):
            yuddha = {
                "with": w["name_b"] if w["graha_a"] == idx else w["name_a"],
                "separation_deg": w["separation_deg"],
                "role": "winner" if w["winner"] == idx else ("loser" if w["loser"] == idx else "undecided"),
                "rule": w["rule"],
            }
            break

    yogas_of = [y["name"] for y in (yogas or []) if idx in y["participants"]]

    varga_placements = {}
    for vk, vplanets in (varga or ctx["varga"]).items():
        varga_placements[vk] = _varga_rashi_name(vk, vplanets.get(idx), lang)

    sheet = {
        "index": idx,
        "name": KalaKosha.GRAHAS[lang][idx],
        "longitude_deg": p.get("longitude"),
        "degree_in_sign_deg": p.get("degree_in_sign"),
        "speed_deg_per_day": p.get("speed"),
        "rashi": {
            "code": rashi,
            "name": KalaKosha.RASIS[lang][rashi] if rashi is not None else None,
        },
        "nakshatra": {
            "code": p.get("nakshatra"),
            "name": KalaKosha.NAKSHATRAS[lang][p.get("nakshatra")] if p.get("nakshatra") is not None else None,
            "pada": p.get("nakshatra_pada"),
        },
        "bhava": {
            "house": house,
            "house_rashi": KalaKosha.RASIS[lang][ctx["houses"].get(house, {}).get("rashi")] if house else None,
            "bhavesha": KalaKosha.GRAHAS[lang][ctx["houses"].get(house, {}).get("lord_idx")] if house else None,
        },
        "dignity": {
            "code": p.get("dignity_code"),
            "label": p.get("dignity"),
        },
        "status": [s["name"] for s in statuses],
        "statuses": statuses,
        "aspects_outgoing": aspects_out,
        "aspects_incoming": aspects_in,
        "conjunction_with": conj,
        "graha_yuddha": yuddha,
        "yogas": yogas_of,
        "varga_placements": varga_placements,
    }
    return sheet


# ---------------------------------------------------------------------------
#  Evidence graph  (conclusion → factors → rule → source)
# ---------------------------------------------------------------------------

def _evidence_items(ctx: dict, drishti: dict, conjunctions: list,
                    yuddhas: list, yogas: list) -> list:
    lang = ctx["lang"]
    planets = ctx["planets"]
    evidence = []

    for y in yogas:
        evidence.append({
            "statement": f"{y['name']} is formed",
            "evidence": y.get("evidence", []),
            "rule": y.get("condition", ""),
            "source": y.get("source", ""),
            "weight": y.get("strength", 0),
        })

    for idx in range(9):
        rashi = planets[idx].get("rashi")
        if rashi is None:
            continue
        g = KalaKosha.GRAHAS[lang][idx]
        for s in compute_graha_status(ctx).get(idx, []):
            evidence.append({
                "statement": f"{g} carries the status {s['name']}",
                "evidence": [s.get("evidence", "")],
                "rule": s.get("rule", ""),
                "source": "Parāśarī Hora Śāstra",
                "weight": 1,
            })

    for group in conjunctions:
        members = [KalaKosha.GRAHAS[lang][i] for i in group["grahas"]]
        evidence.append({
            "statement": f"Conjunction (yuti) in {group['rashi_name']}",
            "evidence": [f"{', '.join(members)} occupy {group['rashi_name']}"],
            "rule": "Same-rāśi occupancy on D1",
            "source": "Parāśarī Hora Śāstra",
            "weight": 1,
        })

    for w in yuddhas:
        evidence.append({
            "statement": f"Graha Yuddha between {w['name_a']} and {w['name_b']}",
            "evidence": [f"Separation {w['separation_deg']}° in {w['rashi_name']}",
                         f"Latitudes: {w['name_a']} {w['latitude_a']}°, {w['name_b']} {w['latitude_b']}°"],
            "rule": w["rule"],
            "source": "Bṛhat Jātaka",
            "weight": 2,
        })

    for idx in range(9):
        for t in drishti["outgoing"].get(idx, []):
            targets = [n for n in range(9) if planets[n].get("rashi") == t and n != idx]
            if targets:
                evidence.append({
                    "statement": f"{KalaKosha.GRAHAS[lang][idx]} aspects "
                                 f"{KalaKosha.RASIS[lang][t]}",
                    "evidence": [f"Aspects {', '.join(KalaKosha.GRAHAS[lang][x] for x in targets)}"],
                    "rule": _with_source(idx),
                    "source": "Parāśarī Hora Śāstra" if idx < 7 else "Jaimini convention",
                    "weight": 1,
                })

    return evidence


# ---------------------------------------------------------------------------
#  Programmatic query API (#104)
# ---------------------------------------------------------------------------

def _answers_dict(ctx: dict, fact_sheets: dict,
                  drishti: dict, conjunctions: list,
                  yogas: list, yuddhas: list) -> dict:
    lang = ctx["lang"]
    planets = ctx["planets"]
    answers = {}
    for idx in range(9):
        name = KalaKosha.GRAHAS[lang][idx]
        p = planets[idx]
        rashi = p.get("rashi")
        if rashi is None:
            answers[f"{name} position"] = "Below the horizon / not placed (degenerate chart)"
            continue
        answers[f"{name} rashi"] = KalaKosha.RASIS[lang][rashi]
        answers[f"{name} bhava"] = f"{p.get('house')}th house"
        answers[f"{name} nakshatra"] = \
            f"{KalaKosha.NAKSHATRAS[lang][p['nakshatra']]} pada {p['nakshatra_pada']}" \
            if p.get("nakshatra") is not None else "--"
        st = [s["name"] for s in compute_graha_status(ctx).get(idx, [])]
        answers[f"is {name} Asta/Vakri"] = "/".join(
            [x for x in ("Asta", "Vakri", "Maargi") if x in st]) or "none"
        answers[f"{name} dignity"] = p.get("dignity_code") or "--"
        answers[f"{name} aspects"] = ", ".join(
            KalaKosha.RASIS[lang][t] for t in drishti["outgoing"].get(idx, []))
        answers[f"{name} conjunct"] = ", ".join(
            fact_sheets[idx]["conjunction_with"]) or "none"
        placements = fact_sheets[idx]["varga_placements"]
        answers[f"{name} varga placements"] = {vk: vp for vk, vp in placements.items()}
        yg = fact_sheets[idx]["yogas"]
        answers[f"{name} yogas"] = ", ".join(yg) or "none"
    answers["current dasha"] = {
        "mahadasha": KalaKosha.GRAHAS[lang][ctx["current_dasha"]["mahadasha"]]
        if ctx["current_dasha"]["mahadasha"] is not None else None,
        "antardasha": KalaKosha.GRAHAS[lang][ctx["current_dasha"]["antardasha"]]
        if ctx["current_dasha"]["antardasha"] is not None else None,
        "pratyantardasha": KalaKosha.GRAHAS[lang][ctx["current_dasha"]["pratyantardasha"]]
        if ctx["current_dasha"]["pratyantardasha"] is not None else None,
    }
    return answers


# ---------------------------------------------------------------------------
#  Main entry: analyze a chart
# ---------------------------------------------------------------------------

def analyze_chart(kundali: dict, lang: str = "en") -> dict:
    ctx = _build_context(kundali, lang)
    drishti = compute_drishti(ctx)
    conjunctions = compute_conjunctions(ctx)
    yuddhas = compute_yuddhas(ctx)
    yogas = compute_yogas(ctx, drishti)
    fact_sheets = {idx: graha_fact_sheet(idx, ctx, drishti, conjunctions, yogas, yuddhas)
                   for idx in range(9)}
    evidence = _evidence_items(ctx, drishti, conjunctions, yuddhas, yogas)
    answers = _answers_dict(ctx, fact_sheets, drishti, conjunctions, yogas, yuddhas)

    return {
        "meta": {
            "engine": "KalaBodha",
            "chart": (kundali.get("meta", {}) or {}),
        },
        "lagna": {
            "rashi": ctx["lagna_rashi"],
            "rashi_name": KalaKosha.RASIS[lang][ctx["lagna_rashi"]] if ctx["lagna_rashi"] is not None else None,
            "lagnesh": KalaKosha.GRAHAS[lang][ctx["lagna_lord"]] if ctx["lagna_lord"] is not None else None,
        },
        "grahas": [fact_sheets[i] for i in range(9)],
        "houses": {h: {
            "rashi": v.get("rashi"),
            "rashi_name": KalaKosha.RASIS[lang][v.get("rashi")] if v.get("rashi") is not None else None,
            "lord": KalaKosha.GRAHAS[lang][v.get("lord_idx")] if v.get("lord_idx") is not None else None,
        } for h, v in sorted(ctx["houses"].items())},
        "aspects": drishti,
        "conjunctions": conjunctions,
        "graha_yuddhas": yuddhas,
        "yogas": yogas,
        "evidence": evidence,
        "answers": answers,
        "current_dasha": _answers_dict(ctx, fact_sheets, drishti, conjunctions, yogas, yuddhas)["current dasha"],
    }


# ---------------------------------------------------------------------------
#  Query convenience (#104): structured lookups on a chart dict
# ---------------------------------------------------------------------------

def query_chart(kundali: dict, lang: str = "en") -> dict:
    """Return the programmatic Q&A answers for a Kundali (no AI involved)."""
    return analyze_chart(kundali, lang)["answers"]


# ---------------------------------------------------------------------------
#  Birth-time sensitivity (#42): stable vs unstable factors over ± minutes
# ---------------------------------------------------------------------------

def birth_time_sensitivity(year: int, month: int, day: int,
                           hour: int, minute: int, tz: float,
                           lat: float, lon: float, alt: float,
                           ayanamsa: str = "lahiri", lang: str = "en",
                           span_minutes: int = 15, step: int = 5) -> dict:
    """Recompute the chart across [minute−span, minute+span] and report which
    factors are robust and which depend on the exact birth minute."""
    import KalaChakra as _KC

    offsets = sorted(set(range(-span_minutes, span_minutes + 1, step)))
    if span_minutes not in offsets:
        offsets.append(span_minutes)
        offsets.sort()

    birth_total = hour * 60 + minute
    samples = {}
    for m in offsets:
        total = birth_total + m
        if total < 0 or total >= 24 * 60:
            continue
        h2, m2 = divmod(total, 60)
        kd = _KC.calculate_kundali(year, month, day, h2, m2, tz, lat, lon, alt,
                                   ayanamsa=ayanamsa, lang="en")
        bp = {p["idx"]: p for p in kd["planets"].values()}
        current_md = None
        for mdd in kd["dashas"]["mahadashas"]:
            if mdd["is_current"]:
                current_md = mdd["lord_idx"]
                break
        samples[m] = {
            "lagna_rashi": kd["lagna"]["rashi"],
            "current_md": current_md,
            "rashi": {i: bp[i]["rashi"] for i in range(9)},
            "house": {i: bp[i]["house"] for i in range(9)},
            "vargottam": {i: bool(bp[i]["is_vargottam"]) for i in range(9)},
        }

    def collect(scalar):
        return [samples[m][scalar] for m in samples]

    def per_graha(field):
        stable, unstable = {}, {}
        for i in range(9):
            values = [samples[m][field][i] for m in samples]
            unique = set(values)
            if len(unique) == 1:
                stable[i] = next(iter(unique))
            else:
                unstable[i] = sorted(unique)
        return stable, unstable

    lagna_values = collect("lagna_rashi")
    md_values = collect("current_md")
    rashi_stable, rashi_unstable = per_graha("rashi")
    house_stable, house_unstable = per_graha("house")
    vargottam_stable, vargottam_unstable = per_graha("vargottam")

    sens = {
        "input": {"year": year, "month": month, "day": day, "hour": hour,
                  "minute": minute, "tz": tz, "lat": lat, "lon": lon,
                  "alt": alt, "ayanamsa": ayanamsa,
                  "span_minutes": span_minutes, "step": step},
        "lagna_rashi_values": lagna_values,
        "lagna_stable": len(set(lagna_values)) == 1,
        "current_mahadasha_values": md_values,
        "mahadasha_stable": len(set(md_values)) == 1,
        "rashi_by_graha": {i: {"stable": i in rashi_stable,
                               "values": rashi_stable.get(i, rashi_unstable.get(i))}
                           for i in range(9)},
        "house_by_graha": {"stable": house_stable, "unstable": house_unstable},
        "vargottam_by_graha": {"stable": vargottam_stable, "unstable": vargottam_unstable},
        "stable_factors": [],
        "unstable_factors": [],
    }

    stable, unstable = [], []
    if sens["lagna_stable"] and lagna_values:
        stable.append(f"Lagna ({KalaKosha.RASIS[lang][lagna_values[0]]})")
    else:
        unstable.append("Lagna — changes with birth minute: " +
                        ", ".join(KalaKosha.RASIS[lang][r] for r in sorted(set(lagna_values)) if r is not None))
    if sens["mahadasha_stable"] and md_values:
        stable.append(f"Current Mahadasha ({KalaKosha.GRAHAS[lang][md_values[0]]})")
    else:
        unstable.append("Current Mahadasha — changes with birth minute")
    for i in range(9):
        g = KalaKosha.GRAHAS[lang][i]
        if i in rashi_stable:
            stable.append(f"{g} rāśi ({KalaKosha.RASIS[lang][rashi_stable[i]]})")
        elif i in rashi_unstable:
            vals = sorted(set(v for v in rashi_unstable[i] if v is not None))
            unstable.append(f"{g} rāśi — changes: " + ", ".join(KalaKosha.RASIS[lang][v] for v in vals))
        if i in house_stable and house_stable[i] is not None:
            stable.append(f"{g} bhava ({house_stable[i]}th house)")
        elif i in house_unstable:
            vals = sorted(set(v for v in house_unstable[i] if v is not None))
            unstable.append(f"{g} bhava — changes: " + ", ".join(f"{v}th house" for v in vals))
    sens["stable_factors"] = stable
    sens["unstable_factors"] = unstable
    return sens

# ---------------------------------------------------------------------------
# Phase 16 · Track A — birth-time sensitivity, expanded (multi-window tiers,
# per-factor stability score 0-100, remedy tiering).  Everything here is
# ADDITIVE over the byte-golden single-window birth_time_sensitivity(): the
# original function above is untouched and its default span_minutes=15 output
# remains byte-identical.  These layers are only computed when explicitly
# requested with sensitivity=true, so goldens never see them.
# ---------------------------------------------------------------------------

_SENS_WINDOWS = (5, 10, 15)          # default half-spans tested per tier
_SENS_STEPS = (1, 2, 5)              # matching step widths per window

def multi_window_sensitivity(year, month, day, hour, minute, tz,
                             lat, lon, alt, ayanamsa="lahiri", lang="en"):
    """Compose several sensitivity windows (few minutes vs wide) into one
    stability profile.  Returns, per factor, a 0-100 *latestability score*
    (100 = stable at every tested offset) plus a *verdict* tier:
    ``reliable`` (>=90), ``watch`` (75-89), ``fragile`` (50-74),
    ``unusable`` (<50).  Also reports, per window, how many factors jumped
    (moved lagna_rashi / changed current_mahadasha / graha rashi or house),
    and builds a *remedy tier* list keyed to the most unstable factors.
    Purely deterministic; no LLM; language-aware like the rest of KalaBodha.
    """
    import KalaChakra as _KC

    per_window = {}
    scores = {}
    for w, st in zip(_SENS_WINDOWS, _SENS_STEPS):
        res = birth_time_sensitivity(year, month, day, hour, minute, tz,
                                     lat, lon, alt, ayanamsa=ayanamsa,
                                     lang=lang, span_minutes=w, step=st)
        per_window[w] = res
        n_stable = len(res.get("stable_factors", []))
        n_unstable = len(res.get("unstable_factors", []))
        scores[w] = {"stable": n_stable, "unstable": n_unstable,
                     "jumps": n_unstable}

    # Per-factor score: fraction of windows that keep the factor stable.
    window_keys = set()
    for w in _SENS_WINDOWS:
        for f in per_window[w].get("stable_factors", []):
            window_keys.add(f)
        for f in per_window[w].get("unstable_factors", []):
            window_keys.add(f)
    per_factor = {}
    for factor in sorted(window_keys, key=lambda x: x.lower()[:3]):
        stable_w = sum(1 for w in _SENS_WINDOWS
                       if factor in per_window[w].get("stable_factors", []))
        score = int(round(100.0 * stable_w / len(_SENS_WINDOWS)))
        if score >= 90:
            verdict = "reliable"
        elif score >= 75:
            verdict = "watch"
        elif score >= 50:
            verdict = "fragile"
        else:
            verdict = "unusable"
        per_factor[factor] = {"score": score, "stable_windows": stable_w,
                              "total_windows": len(_SENS_WINDOWS),
                              "verdict": verdict}

    # Remedy tiering — deterministic, sourced: unstable birth-time factors
    # get chart-safe, non-destructive countermeasures keyed by verdict.
    remedies = {"reliable": [], "watch": [], "fragile": [], "unusable": []}
    fragment_groups = {"watch": [], "fragile": [], "unusable": []}
    for factor, info in per_factor.items():
        v = info["verdict"]
        base = "verify the recorded birth minute against the hospital/astrological record first"
        if v == "reliable":
            remedies["reliable"].append({"factor": factor, "score": info["score"]})
        else:
            remedies[v].append({"factor": factor, "score": info["score"],
                                "suggested": _remedy_hint(factor, v, lang)})
            fragment_groups[v].append(factor.split(" ")[0])

    return {
        "windows": [{"span_minutes": w, "stable": scores[w]["stable"],
                     "unstable": scores[w]["unstable"], "jumps": scores[w]["jumps"]}
                    for w in _SENS_WINDOWS],
        "per_factor": per_factor,
        "overall": {
            "stable_factors": [f for f in per_factor
                               if per_factor[f]["verdict"] == "reliable"],
            "unstable_factors": [f for f in per_factor
                                 if per_factor[f]["verdict"] != "reliable"],
            "reliable_ratio": round(
                sum(1 for f in per_factor if per_factor[f]["verdict"] == "reliable")
                / max(1, len(per_factor)) * 100),
        },
        "remedies": remedies,
    }


def _remedy_hint(factor, verdict, lang="en"):
    """A short, sourced, non-invasive remedy hint per unstable factor."""
    f = factor.lower()
    if "lagna" in f:
        hint = _("remedy.lagna_verify")
    elif "mahadasha" in f or "current mahadasha" in f:
        hint = _("remedy.md_verify")
    elif "rashi" in f or "bhava" in f or "house" in f:
        hint = _("remedy.graha_verify")
    else:
        hint = _("remedy.chart_verify")
    if verdict in ("fragile", "unusable"):
        hint += "  " + _("remedy.narla_deepen")
    return hint

