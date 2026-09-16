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
    check("9 planets", len(planets) == 9)
    for i in range(9):
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
    start_pos = flat["dashas.start_lord_idx"]  # cycle position (0..8)
    check("MD years sum == balance + full tail",
          almost(total, 120.0 - KalaKosha.VIMSHOTTARI_YEARS[start_pos] + flat["dashas.balance_years"], 0.06),
          f"{total:.3f}")
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
    check("gochara date recorded", go["date"] == "2026-09-12", go["date"])

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
    check("classical alias works (calculate_gocara)",
          hasattr(KC, "calculate_gocara"), f"hasattr={hasattr(KC, 'calculate_gocara')}")

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