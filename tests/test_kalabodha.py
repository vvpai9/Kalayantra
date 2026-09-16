#!/usr/bin/env python3
"""
KalaBodha (Phase 10) regression harness.

Run:  python3 tests/test_kalabodha.py

Covers:
  1. Semantic chart structure + machine-readable fact sheets.
  2. Golden regression of the SAMPLE chart (1990-06-15 Chennai, Lahiri).
  3. Graha Drishti convention (Parashari + Jaimini nodes).
  4. Conjunctions and Graha Yuddha (Brihat Jataka), incl. the retrograde
     exception and the 1-degree orb rule.
  5. The structured yoga engine (13-yoga curated set).
  6. Programmatic query answers and full (non-abbreviated) nomenclature.
  7. Birth-time uncertainty report (#42).
  8. Language independence (iast).
"""
import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "contents", "scripts"))

import KalaChakra as KC
import KalaKosha
import KalaBodha as KB

PASS = 0
FAIL = 0

FULL_NAMES = {"Surya", "Chandra", "Mangala", "Budha", "Guru",
              "Shukra", "Shani", "Rahu", "Ketu"}


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {detail}")


# ---------------------------------------------------------------------------
# Known birth chart (Chennai, 1990-06-15 10:30 IST, Lahiri) — same lock-points
# as tests/test_calibrated.py.
# ---------------------------------------------------------------------------
SAMPLE = dict(year=1990, month=6, day=15, hour=10, minute=30,
              tz=5.5, lat=13.0827, lon=80.2707, alt=6.0,
              ayanamsa="lahiri", lang="en")

# Real documented Budha–Shukra yuddha: 2000-03-15, within 1 degree in Kumbha.
YUDDHA = dict(year=2000, month=3, day=15, hour=12, minute=0,
              tz=5.5, lat=23.1765, lon=75.7885, alt=216.0,
              ayanamsa="lahiri", lang="en")


def sample_ctx():
    kd = KC.calculate_kundali(**SAMPLE)
    return kd, KB.analyze_chart(kd, "en")


def test_structure():
    print("\n1. Semantic chart structure + fact sheets")
    kd, b = sample_ctx()
    for key in ("lagna", "grahas", "yogas", "conjunctions", "graha_yuddhas",
                "evidence", "answers", "current_dasha", "meta"):
        check(f"analyze_chart has '{key}'", key in b, f"keys: {list(b)}")

    check("lagna object", all(k in b["lagna"] for k in ("rashi", "rashi_name", "lagnesh")),
          f"{b['lagna']}")
    check("9 graha sheets", len(b["grahas"]) == 9, f"{len(b['grahas'])}")

    sheet_keys = {"index", "name", "longitude_deg", "rashi", "nakshatra",
                  "bhava", "dignity", "status", "statuses", "aspects_outgoing",
                  "aspects_incoming", "conjunction_with", "graha_yuddha",
                  "yogas", "varga_placements"}
    for i, sheet in enumerate(b["grahas"]):
        check(f"sheet#{i} has all keys", sheet_keys <= set(sheet), f"missing {sheet_keys - set(sheet)}")
        check(f"sheet#{i} full name", sheet["name"] in FULL_NAMES, f"{sheet['name']}")
        check(f"sheet#{i} rashi object", all(k in sheet["rashi"] for k in ("code", "name")))
        check(f"sheet#{i} dignity object", all(k in sheet["dignity"] for k in ("code", "label")))

    st = {s["name"] for s in b["grahas"][1]["statuses"]}
    check("every graha is Maargi or Vakri", st & {"Maargi", "Vakri"} == st, f"{st}")
    for s in b["grahas"][1]["statuses"]:
        check(f"status '{s['name']}' has rule+evidence",
              all(k in s for k in ("name", "rule", "evidence")), f"{s}")

    for i, item in enumerate(b["evidence"]):
        check(f"evidence#{i} has conclusion->factors->rule->source",
              all(k in item for k in ("statement", "evidence", "rule", "source", "weight")),
              f"{item}")
        check(f"evidence#{i} factors non-empty", isinstance(item["evidence"], list) and item["evidence"])
        check(f"evidence#{i} weight int", isinstance(item["weight"], int) and item["weight"] >= 1)

    vp = b["grahas"][6]["varga_placements"]
    check("varga placements has D1..D60", "D1" in vp and "D9" in vp and "D60" in vp,
          f"sample keys {list(vp)[:4]}")


def test_golden_chart():
    print("\n2. Golden chart facts (SAMPLE, Lahiri, Chennai 1990)")
    kd, b = sample_ctx()
    check("lagna rashi Simha (4)", b["lagna"]["rashi"] == 4 and b["lagna"]["rashi_name"] == "Simha",
          f"{b['lagna']}")
    check("lagnesh Surya", b["lagna"]["lagnesh"] == "Surya", f"{b['lagna']['lagnesh']}")

    def g(idx):
        return b["grahas"][idx]

    check("Surya: Mithuna rashi", g(0)["rashi"]["name"] == "Mithuna",
          f"{(g(0)['rashi']['code'], g(0)['rashi']['name'])}")
    check("Surya: 11th house", g(0)["bhava"]["house"] == 11, f"{g(0)['bhava']}")
    check("Chandra: Kumbha, 7th house", g(1)["rashi"]["name"] == "Kumbha" and g(1)["bhava"]["house"] == 7,
          f"{(g(1)['rashi']['name'], g(1)['bhava']['house'])}")
    check("Shani: Makara, 6th house", g(6)["rashi"]["name"] == "Makara" and g(6)["bhava"]["house"] == 6,
          f"{(g(6)['rashi']['name'], g(6)['bhava']['house'])}")

    shani_status = [s["name"] for s in g(6)["statuses"]]
    check("Shani status: Vakri + Moolatrikona + Vargottama",
          shani_status == ["Vakri", "Moolatrikona", "Vargottama"], f"{shani_status}")
    check("Shani dignity code moolatrikona", g(6)["dignity"]["code"] == "moolatrikona",
          f"{g(6)['dignity']}")

    check("Rahu conjunct Shani in Makara", g(7)["rashi"]["name"] == "Makara",
          f"{g(7)['rashi']['name']}")


def test_drishti():
    print("\n3. Graha Drishti convention")
    kd, b = sample_ctx()
    en = KalaKosha.RASIS["en"]

    moon_rashi = b["grahas"][1]["rashi"]["code"]
    sun_rashi = b["grahas"][0]["rashi"]["code"]
    check("7th aspect always present for the seven grahas",
          all(6 in {a["offset"] for a in b["grahas"][i]["aspects_outgoing"]} for i in range(7)),
          f"expect offset value 6 (= 7th aspect)")
    check("Rahu/Ketu carry only the Jaimini 5th/9th aspects",
          all(a["offset"] in {4, 8} for i in (7, 8) for a in b["grahas"][i]["aspects_outgoing"]),
          f"{(b['grahas'][7]['aspects_outgoing'], b['grahas'][8]['aspects_outgoing'])}")

    # Golden spot-checks (classical inclusive-count convention:
    # target rashi = (source rashi + aspect - 1) mod 12).
    def targets(i):
        return {a["rashi"] for a in b["grahas"][i]["aspects_outgoing"]}

    check("Shani (Makara) aspects 3rd Meena, 7th Karka, 10th Tula",
          targets(6) == {(9 + o - 1) % 12 for o in (3, 7, 10)}, f"{targets(6)}")
    check("Guru (Mithuna) aspects 5th, 7th, 9th",
          targets(4) == {(2 + o - 1) % 12 for o in (5, 7, 9)}, f"{targets(4)}")
    check("Mangala (Meena) aspects 4th, 7th, 8th",
          targets(2) == {(11 + o - 1) % 12 for o in (4, 7, 8)}, f"{targets(2)}")
    check("Rahu (Makara) Jaimini 5th/9th",
          targets(7) == {(9 + o - 1) % 12 for o in (5, 9)}, f"{targets(7)}")
    check("Surya (Mithuna) 7th only == Dhanu",
          targets(0) == {(2 + 7 - 1) % 12}, f"{targets(0)}")

    # Incoming aspects mirror outgoing (closed under the same occupancy).
    for i in range(9):
        outgoing = {a["rashi"] for a in b["grahas"][i]["aspects_outgoing"]}
        for j in range(9):
            if j != i and b["grahas"][j]["rashi"]["code"] in outgoing:
                check(f"aspect reciprocity {i}->{j}",
                      KalaKosha.GRAHAS["en"][i] in b["grahas"][j]["aspects_incoming"],
                      f"got {b['grahas'][j]['aspects_incoming']}")

    a0 = b["answers"]["Chandra aspects"]
    check("Chandra aspects Simha (7th from Kumbha)", a0 == "Simha", f"{a0}")


def test_conjunctions():
    print("\n4. Conjunctions (yuuti)")
    kd, b = sample_ctx()
    groups = {(c["rashi_name"], tuple(c["grahas"])) for c in b["conjunctions"]}
    check("conjunctions = Mithuna(Surya,Guru) + Makara(Shani,Rahu)",
          groups == {("Mithuna", (0, 4)), ("Makara", (6, 7))}, f"{groups}")
    check("same_nakshatra False for both", not any(c["same_nakshatra"] for c in b["conjunctions"]))
    check("Surya sheet conjunction_with == [Guru]",
          b["grahas"][0]["conjunction_with"] == ["Guru"], f"{b['grahas'][0]['conjunction_with']}")


def test_yuddha():
    print("\n5. Graha Yuddha (Brihat Jataka)")
    kd = KC.calculate_kundali(**YUDDHA)
    b = KB.analyze_chart(kd, "en")
    check("exactly one yuddha on 2000-03-15", len(b["graha_yuddhas"]) == 1,
          f"{len(b['graha_yuddhas'])}")
    w = b["graha_yuddhas"][0]
    check("yuddha involves Budha + Shukra", {w["graha_a"], w["graha_b"]} == {3, 5},
          f"{w}")
    check("yuddha in Kumbha within 1 deg", w["rashi_name"] == "Kumbha" and w["separation_deg"] <= 1.0)
    check("winner/loser form the pair", {w["winner"], w["loser"]} == {3, 5}, f"{w}")
    check("yuddha rule documented", "1°" in w["rule"] or "1 degree" in w["rule"], w["rule"])

    ev = [e for e in b["evidence"] if "Yuddha" in e["statement"]]
    check("yuddha evidence recorded", len(ev) >= 1, f"{[e['statement'] for e in ev]}")
    role = b["grahas"][3]["graha_yuddha"]
    check("Budha sheet yuddha role set", role and role["role"] in ("winner", "loser"), f"{role}")

    # No yuddha in a chart without same-rashi pairs within 1° (SAMPLE).
    kd0, b0 = sample_ctx()
    check("no yuddha in SAMPLE chart", b0["graha_yuddhas"] == [], f"{b0['graha_yuddhas']}")

    # Retrograde exception: Budha (higher latitude) wins when direct; flipping
    # its retrograde flag must hand the win to Shukra.
    ctx = KB._build_context(kd, "en")
    y1 = KB.compute_yuddhas(ctx)
    check("synthetic: Budha wins when direct", y1 and y1[0]["winner"] == 3, f"{y1}")
    ctx2 = copy.deepcopy(ctx)
    ctx2["planets"][3]["retrograde"] = True
    y2 = KB.compute_yuddhas(ctx2)
    check("retrograde exception: loser flips, Shukra wins", y2 and y2[0]["winner"] == 5,
          f"{y2}")
    check("separation identical across flag flip",
          abs(y1[0]["separation_deg"] - y2[0]["separation_deg"]) < 1e-9)


def test_yogas():
    print("\n6. Structured yoga engine")
    kd, b = sample_ctx()
    by_id = {y["id"]: y for y in b["yogas"]}
    check("all curated yogas have structured record",
          all(set(y) >= {"id", "name", "strength", "participants",
                         "source", "tradition", "condition", "exception",
                         "interpretation", "evidence"} for y in b["yogas"]))

    golden = {
        "sunapha": [2], "anapha": [6, 7], "durudhara": [2, 6, 7],
        "vipareeta": [6], "raja_yoga": [0, 4], "dhana_yoga": [3],
    }
    check(f"golden yoga set == {sorted(golden)}",
          sorted(by_id) == sorted(golden), f"got {sorted(by_id)}")
    for yid, parts in golden.items():
        check(f"{yid} participants {parts}",
              sorted(by_id[yid]["participants"]) == sorted(parts),
              f"{by_id[yid]['participants']}")

    check("sunapha strength 1", by_id["sunapha"]["strength"] == 1)
    check("durudhara strength 2", by_id["durudhara"]["strength"] == 2)
    check("dhana participants deduped (Budha owns 2nd & 11th)",
          sorted(by_id["dhana_yoga"]["participants"]) == [3],
          f"{by_id['dhana_yoga']['participants']}")
    check("dhana evidence per unique lord",
          len(by_id["dhana_yoga"]["evidence"]) == 1,
          f"{by_id['dhana_yoga']['evidence']}")

    names = [y["name"] for y in b["yogas"]]
    check("full-name yoga display", all(len(n) > 3 for n in names), f"{names}")


def test_answers():
    print("\n7. Programmatic query API (#104)")
    kd, b = sample_ctx()
    a = b["answers"]
    check("82 answers (9 grahas x 9 + current dasha)", len(a) == 82,
          f"got {len(a)}")
    check("Surya rashi == Mithuna", a["Surya rashi"] == "Mithuna", f"{a['Surya rashi']}")
    check("Shani dignity == moolatrikona", a["Shani dignity"] == "moolatrikona",
          f"{a['Shani dignity']}")
    check("is Shani Asta/Vakri == Vakri", a["is Shani Asta/Vakri"] == "Vakri",
          f"{a['is Shani Asta/Vakri']}")
    check("Shani aspects == Karka, Tula, Meena", a["Shani aspects"] == "Karka, Tula, Meena",
          f"{a['Shani aspects']}")
    check("Shani varga placements D1 == Makara", a["Shani varga placements"]["D1"] == "Makara",
          f"{a['Shani varga placements'].get('D1')}")
    check("current dasha present", "mahadasha" in a["current dasha"], f"{a['current dasha']}")
    check("current dasha mahadasha in full set",
          a["current dasha"]["mahadasha"] in FULL_NAMES,
          f"{a['current dasha']}")

    # No cryptic abbreviations anywhere in the answers surface.
    bad = [k for k in a if not k.startswith("is ") and k != "current dasha"
           and k.split(" ")[0] not in FULL_NAMES]
    check("no abbreviated graha keys", bad == [], f"bad keys: {bad}")


def test_sensitivity():
    print("\n8. Birth-time uncertainty report (#42)")
    kd, b = sample_ctx()
    s = KB.birth_time_sensitivity(1990, 6, 15, 10, 30, 5.5, 13.0827, 80.2707, 6.0,
                                  lang="en", span_minutes=15, step=5)
    for key in ("input", "lagna_rashi_values", "lagna_stable",
                "current_mahadasha_values", "mahadasha_stable",
                "rashi_by_graha", "house_by_graha", "vargottam_by_graha",
                "stable_factors", "unstable_factors"):
        check(f"sensitivity has '{key}'", key in s, f"keys: {list(s)}")
    check("SAMPLE lagna stable (Simha)", s["lagna_stable"] and set(s["lagna_rashi_values"]) == {4},
          f"{s['lagna_rashi_values']}")
    check("stable factors non-empty", bool(s["stable_factors"]), f"{s['stable_factors']}")
    check("factor strings human-readable (reasons, not codes)",
          all(len(f) > 8 and "(" in f for f in s["stable_factors"]),
          f"{s['stable_factors'][:3]}")
    golden = KB.birth_time_sensitivity(1990, 6, 15, 10, 30, 5.5, 13.0827, 80.2707, 6.0,
                                       lang="en", span_minutes=15, step=5)
    check("deterministic across runs", s["stable_factors"] == golden["stable_factors"])


def test_languages():
    print("\n9. Language independence")
    kd_en = KC.calculate_kundali(**SAMPLE)
    b_en = KB.analyze_chart(kd_en, "en")
    kd_ia = KC.calculate_kundali(year=SAMPLE["year"], month=SAMPLE["month"],
                                 day=SAMPLE["day"], hour=SAMPLE["hour"],
                                 minute=SAMPLE["minute"], tz=SAMPLE["tz"],
                                 lat=SAMPLE["lat"], lon=SAMPLE["lon"],
                                 alt=SAMPLE["alt"], ayanamsa="lahiri", lang="iast")
    b_ia = KB.analyze_chart(kd_ia, "iast")
    check("iast graha names used", b_ia["grahas"][0]["name"] == "Sūrya",
          f"{b_ia['grahas'][0]['name']}")
    check("iast lagnesh localized", b_ia["lagna"]["lagnesh"] == "Sūrya",
          f"{b_ia['lagna']['lagnesh']}")
    check("same structure both languages", len(b_en["grahas"]) == len(b_ia["grahas"]))
    check("same yoga ids both languages",
          {y["id"] for y in b_en["yogas"]} == {y["id"] for y in b_ia["yogas"]})
    check("sensitivity localized", "(" in KB.birth_time_sensitivity(
        1990, 6, 15, 10, 30, 5.5, 13.0827, 80.2707, 6.0,
        lang="iast", span_minutes=15, step=5)["stable_factors"][0])


    test_track_a_multiwindow()
    test_track_a_stability_score()
def main():
    test_structure()
    test_golden_chart()
    test_drishti()
    test_conjunctions()
    test_yuddha()
    test_yogas()
    test_answers()
    test_sensitivity()
    test_languages()
    print(f"\n= {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0

    test_track_a_multiwindow()
    test_track_a_stability_score()

