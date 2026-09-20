#!/usr/bin/env python3
"""
KalaYantra accuracy / regression harness.

Run:  python3 tests/test_calibrated.py

Two kinds of checks:
  1. Internal consistency + structural invariants of the engine.
  2. Golden regression snapshots of a known birth chart (Lahiri, Chennai).

To calibrate against the reference "Hindu Calendar" app (Alok Mandavgane),
compute the same birth chart there and fill the GET_APP_BASELINE dict below;
when non-empty the harness compares against it and prints a diff.
"""
import os
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "contents", "scripts"))

import KalaChakra as KC
import KalaKosha
import KalaUtsavachakra as KO

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


def almost(a, b, tol=0.011):
    try:
        if isinstance(a, str) or isinstance(b, str):
            return a == b
        return abs(a - b) <= tol
    except TypeError:
        return a == b


# ---------------------------------------------------------------------------
# Known birth chart (Chennai, 1990-06-15 10:30 IST, Lahiri).
# These are regression lock-points; change them only after verifying the
# reference app confirms a genuine calculation change.
# ---------------------------------------------------------------------------
SAMPLE = dict(year=1990, month=6, day=15, hour=10, minute=30,
              tz=5.5, lat=13.0827, lon=80.2707, alt=6.0, ayanamsa="lahiri", lang="en")

GOLDEN = {
    "meta.lon": 80.2707,
    "lagna.rashi": 4,          # Simha
    "lagna.rashi_name": "Simha",
    "planets.Surya.rashi": 2,  # Mithuna
    "planets.Chandra.rashi": 10,  # Kumbha
    "dashas.start_lord": "Rahu",
    "dashas.balance_years": 3.04,
}

# Optional reference-app cross-check.  Fill these from the "Hindu Calendar"
# app's Kundali screen for the SAMPLE birth data, then re-run:
#   "lagna.rashi_name": "...", "planets.Chandra.rashi_name": "...", ...
GET_APP_BASELINE = {}


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out


def main():
    print("= KalaYantra accuracy / regression harness\n")
    print("1. Golden regression lock (Chennai birth chart, Lahiri)")
    kd = KC.calculate_kundali(**SAMPLE)
    flat = flatten(kd)
    for key, expected in GOLDEN.items():
        check(f"{key} == {expected}", almost(flat.get(key), expected), f"got {flat.get(key)}")

    print("\n2. Structural invariants")
    planets = {p["idx"]: p for p in kd["planets"].values()}
    check("13 planets (9 grahas + Uranus/Neptune/Pluto/Maandi)", len(planets) == 13)
    for i in range(13):
        check(f"planet {i} index key present", planets[i]["idx"] == i)
        check(f"planet {i} has speed", isinstance(planets[i].get("speed"), (int, float)))
        check(f"planet {i} prograde xor retrograde",
              planets[i]["prograde"] != planets[i]["retrograde"])
        check(f"planet {i} asta == combust",
              planets[i]["asta"] == planets[i]["combust"])
        check(f"planet {i} degree in [0,30)",
              0.0 <= planets[i]["degree"] < 30.0,
              f"degree={planets[i]['degree']}")

    # meta passes location through (regression: lon was clobbered by Ketu)
    check("meta.lat == SAMPLE lat", almost(flat["meta.lat"], SAMPLE["lat"]))
    check("meta.lon == SAMPLE lon", almost(flat["meta.lon"], SAMPLE["lon"]))

    # Vimshottari tree
    d = kd["dashas"]
    mds = d["mahadashas"]
    check("9 mahadashas", len(mds) == 9)
    total = sum(m["years"] for m in mds)
    # All nine full Vimshottari lords materialise (120-year cycle); the natal
    # lord's mahadasha *contains* birth, so `balance_years` is the part that
    # remains after birth, not a shortened first entry.
    check("MD years sum == 120.0", almost(total, 120.0, 0.06), f"{total:.3f}")
    check("exactly one current MD", sum(1 for m in mds if m["is_current"]) == 1)
    for m in mds:
        ads = m["antardashas"]
        check(f"MD {m['lord']}: 9 antardashas", len(ads) == 9)
        check(f"MD {m['lord']}: AD sum == MD years",
              almost(sum(a["years"] for a in ads), m["years"], 0.05),
              f"{sum(a['years'] for a in ads):.3f} vs {m['years']:.3f}")
        check(f"MD {m['lord']}: AD continuity",
              ads[0]["start_date"] == m["start_date"] and ads[-1]["end_date"] == m["end_date"])
        for a in ads:
            pts = a["pratyantardashas"]
            check(f"AD {m['lord']}-{a['lord']}: 9 pratyantardashas", len(pts) == 9)
            check(f"AD {m['lord']}-{a['lord']}: PD sum == AD years",
                  almost(sum(p["years"] for p in pts), a["years"], 0.06),
                  f"{sum(p['years'] for p in pts):.3f} vs {a['years']:.3f}")
            check(f"AD {m['lord']}-{a['lord']}: PD continuity",
                  pts[0]["start_date"] == a["start_date"] and pts[-1]["end_date"] == a["end_date"])
    check("exactly one current AD", sum(1 for m in mds for a in m["antardashas"] if a["is_current"]) == 1)
    check("exactly one current PD",
          sum(1 for m in mds for a in m["antardashas"] for p in a["pratyantardashas"] if p["is_current"]) == 1)

    # Non-decimal durations: every node carries a Y/M/D breakdown that rounds
    # back to its decimal `years`.
    def _ymd_int(dur):
        return (dur.get("years"), dur.get("months"), dur.get("days"))

    def _ymd_years(dur, ymd):
        return ymd[0] + ymd[1] / 12.0 + ymd[2] / 365.2425
    for m in mds:
        check(f"MD {m['lord']} duration present",
              all(isinstance(x, int) for x in _ymd_int(m["duration"])),
              f"{m['duration']}")
        check(f"MD {m['lord']} duration ≈ years",
              almost(_ymd_years(m["years"], _ymd_int(m["duration"])), m["years"], 0.02),
              f"{m['duration']} vs {m['years']}")
        for a in m["antardashas"]:
            check(f"AD {m['lord']}-{a['lord']} duration present",
                  all(isinstance(x, int) for x in _ymd_int(a["duration"])),
                  f"{a['duration']}")
            for p in a["pratyantardashas"]:
                check(f"PD {m['lord']}-{a['lord']}-{p['lord']} duration present",
                      all(isinstance(x, int) for x in _ymd_int(p["duration"])),
                      f"{p['duration']}")
    check("balance duration present",
          all(isinstance(x, int) for x in _ymd_int(d["balance_duration"])),
          f"{d['balance_duration']}")
    check("balance duration ≈ balance years",
          almost(_ymd_years(d["balance_years"], _ymd_int(d["balance_duration"])),
                 d["balance_years"], 0.02),
          f"{d['balance_duration']} vs {d['balance_years']}")

    # Vargottam consistency: D1 rashi == D9 rashi  <=>  is_vargottam
    print("\n3. Varga / vargottam consistency")
    for i in range(9):
        nm = planets[i]["name"]
        d1 = kd["vargas"]["D1"]["planets"][nm]["rashi"]
        d9 = kd["vargas"]["D9"]["planets"][nm]["rashi"]
        check(f"{nm} vargottam matches D1==D9", planets[i]["is_vargottam"] == (d1 == d9),
              f"flag={planets[i]['is_vargottam']} D1={d1} D9={d9}")
        check(f"{nm} D1 placement matches natal", d1 == planets[i]["rashi"])
        dd = kd["vargas"]["D9"]["planets"][nm]["degree"]
        check(f"{nm} D9 degree within [0,30)", 0.0 <= dd < 30.0, f"degree={dd}")

    print("\n4. Panchanga additions (adhipatis / lagna / initials)")
    pc = KC.calculate_panchanga(2026, 9, 12, 5.5, SAMPLE["lat"], SAMPLE["lon"], 6.0, lang="en")
    check("lagna present", 0 <= pc["lagna_idx"] <= 11)
    check("lagna adhipati consistent", pc["lagna_adhipati"] == KalaKosha.GRAHAS["en"][KalaKosha.RASHI_LORD[pc["lagna_idx"]]])
    check("moon rashi consistent", pc["moon_rashi"] == KalaKosha.RASIS["en"][pc["moon_rashi_idx"]])
    nak = pc["nakshatra"]
    check("nakshatra adhipati consistent",
          pc["nakshatra_adhipati"] == KalaKosha.GRAHAS["en"][KalaKosha.NAKSHATRA_LORD[KalaKosha.NAKSHATRAS["en"].index(nak)]]
          if isinstance(nak, str) and nak in KalaKosha.NAKSHATRAS["en"] else True)
    check("nakshatra pada in 1..4", 1 <= pc["nakshatra_pada"] <= 4)
    check("nakshatra initial non-empty", bool(pc["nakshatra_initial"]))
    check("initials table size", len(KalaKosha.NAKSHATRA_INITIALS["en"]) == 108
          and len(KalaKosha.NAKSHATRA_INITIALS["devanagari"]) == 108)

    # --- Festival engine regression lock (Delhi, Ujjain-ish reference). ---
    print("\n4b. Festival engine regression (2025, Delhi)")
    F_TEST = [
        # (month, day, expected festival name, lang)
        (1, 14, "Makara Sankranti"),
        (2, 26, "Mahashivaratri"),
        (3, 30, "Gudi Padwa"),
        (4, 6, "Rama Navami"),
        (7, 10, "Guru Purnima"),
        (8, 9, "Raksha Bandhan"),
        (8, 27, "Ganesh Chaturthi"),
        (10, 2, "Vijayadashami"),
        (10, 20, "Deepavali"),
    ]
    for m, d, fest in F_TEST:
        lang = "en"
        pc_f = KC.calculate_panchanga(2025, m, d, 5.5, 28.6139, 77.2090, 216.0, lang=lang)
        names = [x["name"] for x in KO.calculate_festivals(pc_f, 5.5, None, "vaishnava", lang)]
        check(f"{fest} on 2025-{m:02d}-{d:02d} ({lang})", fest in names, f"got {names}")

    # Ekadashi names resolve across all three languages.
    pc_ek = KC.calculate_panchanga(2025, 10, 3, 5.5, 28.6139, 77.2090, 216.0, lang="devanagari")
    ek_names = [x["name"] for x in KO.calculate_festivals(pc_ek, 5.5, None, "vaishnava", "devanagari")]
    check("Ekadashi devanagari name", any("एकादशी" in n for n in ek_names), f"got {ek_names}")

    # evaluate_reminders matches tithi, festival and sankranti types.
    rem = [
        {"enabled": True, "type": "festival", "params": {"festival_name": "Vijayadashami"}},
        {"enabled": True, "type": "tithi", "params": {"tithi": "Dashami"}},
        {"enabled": True, "type": "sankranti", "params": {}},
        {"enabled": False, "type": "tithi", "params": {"tithi": "Purnima"}},
    ]
    pc_f = KC.calculate_panchanga(2025, 10, 2, 5.5, 28.6139, 77.2090, 216.0, lang="en")
    fest_day = KO.calculate_festivals(pc_f, 5.5, None, "vaishnava", "en")
    matched = KO.evaluate_reminders(pc_f, fest_day, rem, "en")
    check("reminder tithi match", any(r["type"] == "tithi" for r in matched))
    check("reminder festival match", any(r["type"] == "festival" for r in matched))
    check("reminder disabled ignored", any(r["type"] == "tithi" and not r["enabled"] for r in matched) is False)

    print("\n4c. Multi-year festival + adhika masa regression (Delhi)")
    F_YEARS = [
        (2023, 3, 30, "Rama Navami"),
        (2023, 12, 16, "Dhanu Sankranti"),
        (2024, 4, 17, "Rama Navami"),
        (2024, 11, 12, "Devutthana Ekadashi"),
        (2026, 2, 15, "Mahashivaratri"),
        (2026, 3, 26, "Rama Navami"),
    ]
    for yr, m, d, fest in F_YEARS:
        pc_y = KC.calculate_panchanga(yr, m, d, 5.5, 28.6139, 77.2090, 216.0, lang="en")
        names = [x["name"] for x in KO.calculate_festivals(pc_y, 5.5, None, "vaishnava", "en")]
        check(f"{fest} on {yr}-{m:02d}-{d:02d}", fest in names, f"got {names}")

    # Adhika (intercalary) masa: 2023 had Adhika Shravana.
    pc_adh = KC.calculate_panchanga(2023, 7, 29, 5.5, 28.6139, 77.2090, 216.0, lang="en")
    check("2023 adhika masa flagged", pc_adh.get("is_adhika"), f"{pc_adh.get('masa')}")
    check("adhika masa name", pc_adh.get("masa") == "Adhika Shravana", f"{pc_adh.get('masa')}")
    n_adh = [x["name"] for x in KO.calculate_festivals(pc_adh, 5.5, None, "vaishnava", "en")
             if x.get("type") == "Ekadashi"]
    check("Padmini Ekadashi in Adhika Shravana", "Padmini Ekadashi" in n_adh, f"got {n_adh}")
    pc_adh2 = KC.calculate_panchanga(2023, 8, 12, 5.5, 28.6139, 77.2090, 216.0, lang="en")
    n_adh2 = [x["name"] for x in KO.calculate_festivals(pc_adh2, 5.5, None, "vaishnava", "en")
              if x.get("type") == "Ekadashi"]
    check("Parama Ekadashi in Adhika Shravana", "Parama Ekadashi" in n_adh2, f"got {n_adh2}")

    check("2026 Adhika Jyeshtha flagged",
          KC.calculate_panchanga(2026, 5, 19, 5.5, 28.6139, 77.2090, 216.0, lang="en").get("is_adhika"),
          "expected adhika Jyeshtha 2026")

    print("\n4d. Gochara (transit) engine")
    go = KC.calculate_gochara(kd, 2026, 9, 12, 12, 0, 5.5, SAMPLE["lat"], SAMPLE["lon"],
                              lang="en", ayanamsa="lahiri")
    for key in ("transits", "special_yogas", "next_sign_changes", "date", "ayanamsa"):
        check(f"gochara has '{key}'", key in go, f"keys: {list(go)}")
    tlist = {t["idx"]: t for t in go["transits"]}
    check("gochara covers all 9 grahas", set(tlist) == set(range(9)), f"got {set(tlist)}")
    check("transit rashi range", all(0 <= t["rashi"] <= 11 for t in go["transits"]))
    check("transit degree range", all(0.0 <= t["degree_in_sign"] < 30.0 for t in go["transits"]))
    check("all 9 dignity codes", all(isinstance(t["dignity_code"], str) for t in go["transits"]))
    # transit house should be relative to natal lagna (Simha = rashi 4, house 1)
    check("Surya transits natal 1st house (Simha)", tlist[0]["house"] == 1, f"{tlist[0]['house']}")
    check("gochara date recorded", go["date"] == "12-09-2026", go["date"])

    # Special yogas should be structurally valid (name, severity, description)
    for y in go["special_yogas"]:
        check(f"yoga '{y['name']}' has keys",
              all(k in y for k in ("name", "severity", "description")))
    check(">=3 special transits expected for SAMPLE", len(go["special_yogas"]) >= 3,
          f"{len(go['special_yogas'])}")
    check("next sign changes non-empty", go["next_sign_changes"], f"got {go['next_sign_changes']}")
    for e in go["next_sign_changes"]:
        check(f"sign change '{e['graha']}' has keys",
              all(k in e for k in ("graha", "from_rashi", "to_rashi", "date")) and
              e["from_rashi"] != e["to_rashi"])

    def _edge_ymd(date_str):
        dmy = date_str.split()[0].split("-")
        d, m, y = int(dmy[0]), int(dmy[1]), int(dmy[2])
        return y * 10000 + m * 100 + d

    edge_dates = [e["date"] for e in go["next_sign_changes"]]
    check("sign changes listed chronologically",
          edge_dates == sorted(edge_dates, key=_edge_ymd), f"{edge_dates}")
    check("Budha sign change reported",
          any(budha_e["graha"] == "Budha" for budha_e in go["next_sign_changes"]),
          f"{go['next_sign_changes']}")
    check("Surya sign change reported",
          any(surya_e["graha"] == "Surya" for surya_e in go["next_sign_changes"]),
          f"{[e['graha'] for e in go['next_sign_changes']]}")

    # Budha-Aditya Yoga: Budha within 12° of Surya. Take the 2026-01-07 close
    # Sun–Mercury conjunction (~8.6°) and require the yoga to be reported.
    go_ba = KC.calculate_gochara(kd, 2026, 1, 7, 12, 0, 5.5, SAMPLE["lat"], SAMPLE["lon"],
                                 lang="en", ayanamsa="lahiri")
    ba = [y for y in go_ba["special_yogas"] if "Budha-Aditya" in y["name"]]
    check("Budha-Aditya Yoga detected during close conjunction",
          len(ba) == 1 and all(k in ba[0] for k in ("name", "severity", "description")),
          f"got {ba}")
    check("classical alias works (calculate_gocara)",
          hasattr(KC, "calculate_gocara"), f"hasattr={hasattr(KC, 'calculate_gocara')}")

    print("\n4e. Saura (solar) calendar regression")
    saura_days = []
    for d in range(8, 28):
        ps = KC.calculate_panchanga(2026, 9, d, 5.5, 28.6139, 77.2090, 216.0,
                                    lang="en", calendar_system="saura")
        saura_days.append(ps)
    # masa name is a saura (rashi) name, not a lunar 'Bhadrapada'.
    check("saura masa is rashi name",
          all(p["masa"] in KalaKosha.SAURA_MASAS["en"] for p in saura_days),
          f"got {[p['masa'] for p in saura_days[:3]]}")
    check("saura has no paksha", all(p["paksha"] == "" for p in saura_days))
    check("solar_day in 1..31", all(1 <= p["solar_day"] <= 31 for p in saura_days),
          f"got {[p['solar_day'] for p in saura_days[:3]]}")
    # solar day resets to 1 exactly when the saura (rashi) month flips.
    resets = [i for i in range(1, len(saura_days))
              if saura_days[i]["solar_day"] == 1]
    check("solar day resets exactly once", len(resets) == 1, f"resets at {resets}")
    if resets:
        i = resets[0]
        check("reset coincides with rashi change",
              saura_days[i]["masa"] != saura_days[i - 1]["masa"],
              f"{saura_days[i-1]['masa']} -> {saura_days[i]['masa']}")
    # Between two days within the same saura month the day number advances by 1.
    for a, b in zip(saura_days, saura_days[1:]):
        if a["masa"] == b["masa"]:
            check(f"solar day +1 within {a['masa']}", b["solar_day"] - a["solar_day"] == 1,
                  f"{a['solar_day']} -> {b['solar_day']}")

    print("\n4f. Chara Karakas + Ghatak Chakra")
    kar = kd["karakas"]
    check("karakas: seven + eight present",
          len(kar["seven"]) == 7 and len(kar["eight"]) == 8)
    d7 = [r["degree_in_sign"] for r in kar["seven"]]
    d8 = [r["degree_in_sign"] for r in kar["eight"]]
    check("karakas: seven ranked descending", d7 == sorted(d7, reverse=True), f"{d7}")
    check("karakas: eight ranked descending", d8 == sorted(d8, reverse=True), f"{d8}")
    check("karakas: Atmakaraka highest", kar["eight"][0]["karaka_idx"] == 0)
    check("karakas: Darakaraka lowest",
          kar["eight"][-1]["karaka_idx"] == 7, f"{kar['eight'][-1]['karaka_idx']}")
    rahu_ef = next((r for r in kar["eight"] if r["idx"] == 7), None)
    check("karakas: Rahu in eight only",
          rahu_ef is not None and all(r["idx"] != 7 for r in kar["seven"]))
    if rahu_ef:
        natal = kd["planets"]["Rahu"]["degree_in_sign"]
        check("karakas: Rahu counted backward",
              almost(rahu_ef["degree_in_sign"], round(30.0 - natal, 4), 1e-3))
        check("karakas: Rahu flagged via_rahu", bool(rahu_ef["via_rahu"]))
    check("karakas: meaning table complete",
          all(len(KalaKosha.KARAKAS[ln]) == 8 for ln in ("en", "iast", "devanagari")))
    check("karakas: meaning strings non-empty",
          all(r["meaning"] for r in kar["eight"]))
    check("karakas: note present", bool(kar.get("note")))

    # Ghataka Chakra supplies exactly the row for the natal Moon rashi.
    gh = kd["ghatak"]
    moon_rashi = kd["planets"]["Chandra"]["rashi"]
    row = KalaKosha.GHATA_CHAKRA[moon_rashi]
    check("ghatak: matches GHATA_CHAKRA maas",
          kd["meta"] and gh["ghat_maas"] == KalaKosha.MASAS["en"][row["maas"]])
    check("ghatak: tithis from table", gh["ghat_tithis"] == list(row["tithis"]))
    check("ghatak: full tithis = group + Krishna",
          gh["ghat_tithis_full"] == sorted(set(row["tithis"] + [t + 15 for t in row["tithis"]])))
    check("ghatak: vaara/nakshatra/yoga/karana from table",
          gh["ghat_vaara"] == KalaKosha.VAARAS["en"][row["vaara"]]
          and gh["ghat_nakshatra"] == KalaKosha.NAKSHATRAS["en"][row["nakshatra"]]
          and gh["ghat_yoga"] == KalaKosha.YOGAS["en"][row["yoga"]]
          and gh["ghat_karana"] == KalaKosha.KARANAS["en"][row["karana"]])
    check("ghatak: prahar in 1..4", 1 <= gh["prahar"] <= 4)
    cm = gh["ghat_chandra_male"]
    cf = gh["ghat_chandra_female"]
    check("ghatak: chandra positions counted from birth rashi",
          cm["rashi"] == KalaKosha.RASIS["en"][(moon_rashi + cm["position"] - 1) % 12]
          and cf["rashi"] == KalaKosha.RASIS["en"][(moon_rashi + cf["position"] - 1) % 12])
    # Known lock: SAMPLE Moon = Kumbha -> Chaitra / [3,8,13] / Guru / Ardra / Ganda / Kimstughna.
    if KalaKosha.RASIS["en"][moon_rashi] == "Kumbha":
        check("ghatak: Kumbha lock maas==",
              gh["ghat_maas"] == "Chaitra", f"{gh['ghat_maas']}")
        check("ghatak: Kumbha lock tithis==", gh["ghat_tithis"] == [3, 8, 13])
        check("ghatak: Kumbha lock vaara==", gh["ghat_vaara"] == "Guru")
        check("ghatak: Kumbha lock nakshatra==", gh["ghat_nakshatra"] == "Ardra")
        check("ghatak: Kumbha lock yoga==", gh["ghat_yoga"] == "Ganda")
        check("ghatak: Kumbha lock karana==", gh["ghat_karana"] == "Kimstughna")
    for i, r in enumerate(KalaKosha.GHATA_CHAKRA):
        check(f"ghata table row {i} sane",
              0 <= r["maas"] < 12 and 0 <= r["vaara"] < 7
              and 0 <= r["nakshatra"] < 27 and 0 <= r["yoga"] < 27
              and 0 <= r["karana"] < 11 and 1 <= r["prahar"] <= 4
              and len(r["tithis"]) == 3 and all(1 <= t <= 15 for t in r["tithis"])
              and 1 <= r["c_male"] <= 12 and 1 <= r["c_female"] <= 12)

    if GET_APP_BASELINE:
        print("\n5. Cross-check vs reference app baseline")
        for key, expected in GET_APP_BASELINE.items():
            check(f"{key} == app value", almost(flat.get(key), expected), f"got {flat.get(key)}")
    else:
        print("\n5. (skipped)  Reference app cross-check — fill")
        print("   GET_APP_BASELINE in tests/test_calibrated.py with values from the")
        print("   'Hindu Calendar' app's Kundali screen for the SAMPLE birth chart.")

    print(f"\n= {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())