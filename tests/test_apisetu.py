#!/usr/bin/env python3
"""
KalaSetu API + CLI + untested-helper regression harness.

Run:  python3 tests/test_apisetu.py

Covers:
   1. HTTP endpoints served by KalaSetu on an ephemeral port (day, month,
      range, search_city, kundali, hora, muhurta, ashtakoota, analysis,
      bodha, gochara, system_info, config, openapi.json, docs).
   2. JSON POST bodies (ashtakoota, bodha, gochara).
   3. The kalayantra-cli subprocess (day, search-city, system-info, kundali,
      gochara, bodha) with --direct (no daemon dependency).
   4. Public helpers previously only covered transitively.
"""
import os
import sys
import json
import glob
import shutil
import subprocess
import tempfile
import threading
import time
import datetime
import urllib.request
import urllib.parse
from http.server import HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "contents", "scripts")
sys.path.insert(0, SCRIPTS)

# Isolate all config writes into a throwaway HOME so the tests never touch the
# user's real ~/.config/kalayantra directory.
_TMP_HOME = tempfile.mkdtemp(prefix="kalayantra-test-home-")
os.environ["HOME"] = _TMP_HOME

import KalaChakra as KC
import KalaSetu
import KalaVartika
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


PORT = 18765
BASE = f"http://127.0.0.1:{PORT}"
SERVER = None
THREAD = None


def start_server():
    global SERVER, THREAD
    SERVER = HTTPServer(("127.0.0.1", PORT), KalaSetu.KalaSetuRequestHandler)
    THREAD = threading.Thread(target=SERVER.serve_forever, daemon=True)
    THREAD.start()
    time.sleep(0.3)


def stop_server():
    if SERVER:
        SERVER.shutdown()
        SERVER.server_close()


def get(path, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.status, r.read()


def post(path, payload):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read()


def test_http_basic():
    print("\n1. KalaSetu HTTP endpoints")
    st, body = get("/day", {"date": "12-09-2026", "tz": "5.5", "lang": "en"})
    d = json.loads(body)
    check("/day 200", st == 200 and d.get("success") is True, f"status={st}")
    for field in ("tithi", "nakshatra", "yoga", "karana", "masa", "festivals",
                  "rahu_kala", "ghadi", "date", "sunrise", "sunset"):
        check(f"day has '{field}'", field in d, f"missing {field}")

    st, body = get("/day", {"date": "12-09-2026", "tz": "5.5", "format": "csv"})
    check("/day CSV has BOM + column header", body[:3] == b"\xef\xbb\xbf" and b"tithi" in body,
          f"head={body[:40]!r}")

    st, body = get("/month", {"year": "2026", "month": "9", "tz": "5.5"})
    arr = json.loads(body)
    check("/month is a 30-day array", isinstance(arr, list) and len(arr) == 30,
          f"len={len(arr) if isinstance(arr, list) else 'not-list'}")

    st, body = get("/range", {"start": "10-09-2026", "end": "15-09-2026", "tz": "5.5"})
    arr = json.loads(body)
    check("/range returns 6 days", isinstance(arr, list) and len(arr) == 6, f"len={len(arr)}")
    check("/range dates sorted", arr[0]["date"] < arr[-1]["date"])

    st, body = get("/search_city", {"q": "Sringeri"})
    cities = json.loads(body)
    check("/search_city returns Sringeri", any(c["name"] == "Sringeri" for c in cities),
          f"got {[c['name'] for c in cities][:4]}")

    st, body = get("/system_info")
    info = json.loads(body)
    check("/system_info has platform fields",
          all(k in info for k in ("architecture", "system", "processor")))

    st, body = get("/config")
    cfg = json.loads(body)
    check("/config returns coordinates", "lat" in cfg and "tz" in cfg, f"keys={list(cfg)[:6]}")

    st, body = get("/openapi.json")
    spec = json.loads(body)
    check("/openapi.json is 3.0.3", spec.get("openapi") == "3.0.3")
    paths = set(spec.get("paths", {}))
    # dispatch table parity
    dispatch = {"'/day": None}  # placeholder
    for p in ("/day", "/month", "/range", "/search_city", "/kundali", "/hora",
              "/muhurta", "/ashtakoota", "/analysis", "/gochara", "/bodha",
              "/api/v1/bodha", "/get_custom_observances", "/save_custom_observance",
              "/delete_custom_observance", "/get_reminders", "/save_reminder",
              "/delete_reminder", "/evaluate_reminders", "/system_info", "/config",
              "/docs", "/launch_app", "/save_custom_city"):
        check(f"openapi documents {p}", p in paths, f"missing {p}")

    st, body = get("/docs")
    html = body.decode("utf-8", "replace")
    check("/docs serves HTML with /gochara row", "<code>/gochara</code>" in html)


def test_http_post():
    print("\n2. KalaSetu JSON POST endpoints")
    st, body = post("/ashtakoota", {
        "bride": {"year": 1990, "month": 6, "day": 15, "hour": 10, "minute": 30, "tz": 5.5},
        "groom": {"year": 1992, "month": 3, "day": 8, "hour": 16, "minute": 45, "tz": 5.5},
    })
    res = json.loads(body)
    check("POST /ashtakoota total in 0..36", 0 <= res.get("total", -1) <= 36,
          f"got {res.get('total')}")
    check("POST /ashtakoota verdict present", isinstance(res.get("verdict"), str))

    # moon-rashi-only input (regression for the fixed short-circuit)
    st, body = post("/ashtakoota", {
        "bride": {"moon_rashi": 5, "moon_nakshatra": 10, "moon_pada": 2},
        "groom": {"moon_rashi": 8, "moon_nakshatra": 18, "moon_pada": 3},
    })
    res = json.loads(body)
    check("POST /ashtakoota moon-rashi only succeeds", res.get("success", False) and "total" in res,
          f"got {list(res)[:6]}")

    st, body = post("/bodha", {
        "date": "15-06-1990", "hour": 10, "minute": 30,
        "lat": 13.0827, "lon": 80.2707, "tz": 5.5, "ayanamsa": "lahiri",
    })
    res = json.loads(body)
    b = res.get("bodha", {})
    check("POST /bodha has evidence+answers", "evidence" in b and "answers" in b,
          f"keys={list(b)[:6]}")

    st, body = post("/gochara", {
        "date": "15-06-1990", "hour": 10, "minute": 30,
        "transit_date": "12-09-2026", "lat": 13.0827, "lon": 80.2707, "tz": 5.5,
    })
    res = json.loads(body)
    g = res.get("gochara", {})
    check("POST /gochara returns transits", "transits" in g and len(g.get("transits", [])) == 9)

    st, body = post("/range", {"start": "01-01-2026", "end": "03-01-2026", "tz": "5.5"})
    arr = json.loads(body)
    check("POST /range returns days", isinstance(arr, list) and len(arr) == 3)


def test_chart_endpoints():
    print("\n3. Kundali-family endpoints")
    st, body = get("/kundali", {"date": "15-06-1990", "hour": "10", "minute": "30",
                                "lat": "13.0827", "lon": "80.2707", "tz": "5.5"})
    kd = json.loads(body)
    for key in ("lagna", "planets", "vargas", "houses", "dashas"):
        check(f"/kundali has '{key}'", key in kd)
    check("/kundali 9 planets", len(kd.get("planets", {})) == 9)
    check("/kundali vargas include D1..D60",
          all(f"D{n}" in kd.get("vargas", {}) for n in (1, 3, 9, 40, 60)))

    st, body = get("/kundali", {"date": "15-06-1990", "hour": "10", "minute": "30",
                                "lat": "13.0827", "lon": "80.2707", "tz": "5.5",
                                "ayanamsa": "sayana"})
    kd = json.loads(body)
    check("/kundali sayana chart_type", "Sayana" in kd.get("meta", {}).get("chart_type", ""))

    st, body = get("/analysis", {"date": "15-06-1990", "hour": "10", "minute": "30",
                                 "lat": "13.0827", "lon": "80.2707", "tz": "5.5"})
    res = json.loads(body)
    analysis = res.get("analysis", {})
    check("/analysis has highlights",
          isinstance(analysis.get("highlights"), list) and analysis["highlights"],
          f"keys={list(res)[:5]} an_keys={list(analysis)[:5]}")

    st, body = get("/hora", {"date": "12-09-2026", "tz": "5.5"})
    h = json.loads(body)
    check("/hora has 12 day horas", len(h.get("day_horas", [])) == 12)

    st, body = get("/muhurta", {"date": "12-09-2026", "tz": "5.5"})
    m = json.loads(body)
    check("/muhurta has 15 day muhurtas", len(m.get("day_muhurtas", [])) == 15)

    st, body = get("/gochara", {"date": "15-06-1990", "hour": "10", "minute": "30",
                                "transit_date": "12-09-2026", "lat": "13.0827",
                                "lon": "80.2707", "tz": "5.5"})
    res = json.loads(body)
    g = res.get("gochara", {})
    check("/gochara transits length 9", len(g.get("transits", [])) == 9)
    check("/gochara has special_yogas", "special_yogas" in g)


CLI = [sys.executable, os.path.join(SCRIPTS, "kalayantra-cli.py")]


def run_cli(subcommand, *args):
    env = dict(os.environ)
    env["HOME"] = _TMP_HOME
    p = subprocess.run(CLI + [subcommand, "--direct"] + list(args), capture_output=True,
                       text=True, timeout=120, env=env)
    return p.returncode, p.stdout, p.stderr


def test_cli():
    print("\n4. kalayantra-cli subcommand coverage")
    rc, out, err = run_cli("day", "--date", "12-09-2026", "--lang", "devanagari")
    check("cli day exits 0 and returns JSON", rc == 0 and json.loads(out).get("tithi"),
          f"rc={rc} err={err[:120]}")

    rc, out, err = run_cli("search-city", "--q", "ujjain")
    check("cli search-city returns matches", rc == 0 and json.loads(out), f"rc={rc} {err[:120]}")

    rc, out, err = run_cli("system-info")
    info = json.loads(out)
    check("cli system-info has architecture", rc == 0 and "architecture" in info)

    rc, out, err = run_cli("kundali", "--date", "15-06-1990", "--hour", "10", "--minute", "30",
                           "--lat", "13.0827", "--lon", "80.2707", "--tz", "5.5")
    kd = json.loads(out)
    check("cli kundali 9 planets", rc == 0 and len(kd.get("planets", {})) == 9)

    rc, out, err = run_cli("gochara", "--date", "15-06-1990", "--hour", "10", "--minute", "30",
                           "--transit-date", "12-09-2026", "--lat", "13.0827",
                           "--lon", "80.2707", "--tz", "5.5")
    go = json.loads(out).get("gochara", {})
    check("cli gochara transits", rc == 0 and len(go.get("transits", [])) == 9)

    rc, out, err = run_cli("bodha", "--date", "15-06-1990", "--hour", "10", "--minute", "30",
                           "--lat", "13.0827", "--lon", "80.2707", "--tz", "5.5",
                           "--sensitivity")
    b = json.loads(out).get("bodha", {})
    check("cli bodha has sense factors", rc == 0 and "evidence" in b)

    rc, out, err = run_cli("month", "--year", "2026", "--month", "1", "--tz", "5.5")
    check("cli month 31 days", rc == 0 and len(json.loads(out)) == 31)

    rc, out, err = run_cli("hora", "--date", "12-09-2026", "--tz", "5.5")
    check("cli hora 12 day horas", rc == 0 and len(json.loads(out).get("day_horas", [])) == 12)

    rc, out, err = run_cli("muhurta", "--date", "12-09-2026", "--tz", "5.5")
    check("cli muhurta 15 day muhurtas",
          rc == 0 and len(json.loads(out).get("day_muhurtas", [])) == 15)

    rc, out, err = run_cli("analysis", "--date", "15-06-1990", "--hour", "10", "--minute", "30",
                           "--lat", "13.0827", "--lon", "80.2707", "--tz", "5.5")
    check("cli analysis highlights",
          rc == 0 and json.loads(out).get("analysis", {}).get("highlights"))

    rc, out, err = run_cli("festivals", "--start", "01-10-2025", "--end", "31-10-2025",
                           "--lang", "en")
    check("cli festivals OK", rc == 0, f"rc={rc} {err[:120]}")


def test_helpers():
    print("\n5. Public helpers (previously transitively exercised)")
    check("get_ayanamsa_modes has lahiri",
          "lahiri" in KC.get_ayanamsa_modes() and "raman" in KC.get_ayanamsa_modes())
    prev = KC.get_ayanamsa_mode()
    KC.set_ayanamsa("raman")
    check("set_ayanamsa/rama roundtrip", KC.get_ayanamsa_mode() == "raman")
    KC.set_ayanamsa(prev)
    try:
        KC.set_ayanamsa("bogus")
        check("set_ayanamsa rejects unknown", False)
    except ValueError:
        check("set_ayanamsa rejects unknown", True)

    # find_transition returns a JD strictly after start where a tithi changes
    pc = KC.calculate_panchanga(2026, 9, 12, 5.5, 23.1765, 75.7885, 0, lang="en")
    t0 = pc["sunrise_jd"]

    def tithi_idx(jd):
        s, m = KC.get_sidereal_longitudes(jd)
        return int(((m - s) % 360.0) / 12.0) % 30

    def nakshatra_idx(jd):
        return int(KC.get_sidereal_longitudes(jd)[1] / KalaVartika.NAKSHATRA_SPAN) % 27

    t_end = KC.find_transition(t0, tithi_idx, max_days=1.5)
    check("find_transition returns future JD", t_end is not None and t_end > t0)
    t_nak = KC.find_transition(t0, nakshatra_idx, max_days=1.5)
    check("find_transition works for nakshatra too", t_nak is not None)

    # KalaUtsavachakra helpers
    jd = pc["jd_calc"]
    mi, adh, kr, ti, tv = KC.get_lunar_month_details(jd, "amavasyanta")
    check("get_lunar_month_details returns 5-tuple",
          isinstance(mi, int) and isinstance(adh, bool) and isinstance(ti, int))
    check("datetime_to_vaara_idx sane", 0 <= KO.datetime_to_vaara_idx("2026-09-12") <= 6)
    check("get_masa_at_jd sane", 0 <= KO.get_masa_at_jd(jd, "amavasyanta") <= 11)

    # KalaVartika pure functions
    check("rashi_index", KalaVartika.rashi_index(123.4) == 4)
    check("nakshatra_pada in 1..4", 1 <= KalaVartika.nakshatra_pada(12.3) <= 4)
    check("tithi_index in 0..29", 0 <= KalaVartika.tithi_index(20.0, 200.0) <= 29)
    check("yoga_index in 0..26", 0 <= KalaVartika.yoga_index(30.0, 100.0) <= 26)
    check("karana_index in 0..57", 0 <= KalaVartika.karana_index(50.0, 10.0) <= 57)
    check("navamsa_sign in 0..11", 0 <= KalaVartika.navamsa_sign(275.0) < 12)
    check("drekkana_sign in 0..11", 0 <= KalaVartika.drekkana_sign(153.0) < 12)
    check("shaka_year math", KalaVartika.shaka_year(2026, True) == 1948)
    check("vikram_year math", KalaVartika.vikram_year(2026, True) == 2083)
    check("kali_year math", KalaVartika.kali_year(1948) == 5128)


def main():
    start_server()
    try:
        test_http_basic()
        test_http_post()
        test_chart_endpoints()
        test_cli()
        test_helpers()
    finally:
        stop_server()
        shutil.rmtree(_TMP_HOME, ignore_errors=True)
    # clean shipped __pycache__
    for d in glob.glob(os.path.join(SCRIPTS, "__pycache__")):
        shutil.rmtree(d, ignore_errors=True)
    print(f"\n= {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())