#!/usr/bin/env python3
"""
KalaMedha — offline AI reading layer regression harness.

Run:  python3 tests/test_kalamedha.py

Covers:
   1. Deterministic narrative (lagna / grahas / yogas / dasha sections).
   2. Explainable per-graha strength/weakness rankings (9 grahas, sorted,
      strongest/weakest present, reasons non-empty).
   3. Intent-driven Q&A: where / strong / weak / aspect / yoga / describe /
      dasha / motion / varga / nakshatra / lagna / overview / unknown.
   4. Evidence is never invented: statements all derive from the chart.
   5. LLM hook: graceful degradation — with no provider reachable, llm_available
      is False, query_llm raises LLMUnavailableError, medha_with_llm falls back
      deterministically, and a fake registered provider is actually used.
   6. medha CLI + /medha HTTP endpoint (ephemeral daemon).
"""
import os
import sys
import json
import shutil
import tempfile
import threading
import time
import subprocess
import urllib.request
import urllib.parse
from http.server import HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "contents", "scripts")
sys.path.insert(0, SCRIPTS)

_TMP_HOME = tempfile.mkdtemp(prefix="kalayantra-test-medha-")
os.environ["HOME"] = _TMP_HOME

import KalaChakra as KC
import KalaBodha
import KalaMedha as KM

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


SAMPLE = dict(year=1990, month=6, day=15, hour=10, minute=30,
              tz=5.5, lat=13.0827, lon=80.2707, alt=6.0, ayanamsa="lahiri", lang="en")


def sample_kundali(lang="en"):
    return KC.calculate_kundali(SAMPLE["year"], SAMPLE["month"], SAMPLE["day"],
                                SAMPLE["hour"], SAMPLE["minute"], SAMPLE["tz"],
                                SAMPLE["lat"], SAMPLE["lon"], SAMPLE["alt"],
                                ayanamsa=SAMPLE["ayanamsa"], lang=lang)


def test_narrative():
    print("\n1. Deterministic narrative")
    kd = sample_kundali()
    m = KM.medha_analysis(kd, lang="en")
    check("meta engine = KalaMedha, llm = False",
          m["meta"]["engine"] == "KalaMedha" and m["meta"]["llm"] is False)
    nar = m["narrative"]
    check("narrative has 5 sections",
          all(k in nar for k in ("lagna", "grahas", "yogas", "dasha", "notable_evidence")))
    check("lagna mentions Simha", "Simha" in nar["lagna"], nar["lagna"])
    check("grahas has 9 entries", isinstance(nar["grahas"], list) and len(nar["grahas"]) == 9,
          f"len={len(nar['grahas'])}")
    check("dasha names a mahadasha", len(nar["dasha"]) > 8, nar["dasha"])

    bodha = KalaBodha.analyze_chart(kd, "en")
    sect = KM.generate_narrative(bodha, kd, "en")
    check("generate_narrative standalone works", sect["grahas"] == nar["grahas"])


def test_strengths():
    print("\n2. Strengths / weaknesses rankings")
    kd = sample_kundali()
    sw = KM.strengths_weaknesses(kd, lang="en")
    ranks = sw["rankings"]
    check("9 ranked grahas", len(ranks) == 9, f"len={len(ranks)}")
    check("sorted descending by score",
          all(ranks[i]["score"] >= ranks[i + 1]["score"] for i in range(len(ranks) - 1)),
          [r["score"] for r in ranks])
    check("indices 0..8 present", sorted(r["idx"] for r in ranks) == list(range(9)))
    check("strongest/weakest names present",
          sw["strongest_name"] == ranks[0]["name"] and sw["weakest_name"] == ranks[-1]["name"])
    check("each ranking bilingual name", all(KM.KalaKosha.GRAHAS["en"][r["idx"]] == r["name"]
                                             for r in ranks))
    check("reasons non-empty for all",
          all(r["reasons"] for r in ranks), "reasons missing for some graha")

    kd_dev = sample_kundali(lang="devanagari")
    swd = KM.strengths_weaknesses(kd_dev, lang="devanagari")
    check("devanagari rankings", swd["rankings"][0]["name"] in
          [KM.KalaKosha.GRAHAS["devanagari"][i] for i in range(9)])


def test_questions():
    print("\n3. Intent-driven Q&A")
    kd = sample_kundali()
    p = {pl["idx"]: pl for pl in kd["planets"].values()}

    a = KM.answer_question("Where is Shani?", kd, "en")
    check("where intent", a["intent"] == "where" and a["graha"] == "Shani",
          f"{a['intent']} {a['graha']}")
    # answer must reference Shani's actual placement
    shani_rashi = KM.KalaKosha.RASIS["en"][p[6]["rashi"]]
    check("answer matches actual placement", shani_rashi in a["answer"],
          f"{a['answer']} vs {shani_rashi}")

    a = KM.answer_question("Is Guru strong?", kd, "en")
    check("strong intent", a["intent"] == "strong" and a["graha"] == "Guru",
          f"{a['intent']} {a['graha']}")
    check("strength answer has reasons", "Reasons:" in a["answer"])

    a = KM.answer_question("Why is Surya weak?", kd, "en")
    check("weak intent resolves to Surya", a["graha"] == "Surya")

    a = KM.answer_question("What does Guru aspect?", kd, "en")
    check("aspect intent", a["intent"] == "aspect" and a["graha"] == "Guru")
    targets = {o["rashi_name"] for o in
               next(g for g in KalaBodha.analyze_chart(kd, "en")["grahas"]
                    if g["index"] == 4)["aspects_outgoing"]}
    check("aspect answer cites rashi names",
          any(t in a["answer"] for t in targets) if targets else len(a["answer"]) > 0)

    a = KM.answer_question("What is the current dasha?", kd, "en")
    check("dasha intent with no graha", a["intent"] == "dasha" and "Mahadasha" in a["answer"],
          a["answer"])
    a = KM.answer_question("Tell me about Mangala", kd, "en")
    check("describe intent", a["intent"] == "describe" and a["graha"] == "Mangala")

    a = KM.answer_question("Is Shani vakri or asta?", kd, "en")
    check("motion intent", a["intent"] == "motion" and a["graha"] == "Shani",
          f"{a['intent']} {a['graha']}")

    a = KM.answer_question("Show me Guru in navamsa", kd, "en")
    check("varga intent", a["intent"] == "varga" and a["graha"] == "Guru")

    a = KM.answer_question("Which nakshatra is the Moon in?", kd, "en")
    check("nakshatra intent", a["intent"] == "nakshatra" and a["graha"] == "Chandra",
          f"{a['intent']} {a['graha']}")

    a = KM.answer_question("Lagna?", kd, "en")
    check("lagna intent", a["intent"] == "lagna" and "Lagna" in a["answer"])

    a = KM.answer_question("Overview of this chart", kd, "en")
    check("overview intent", a["intent"] == "overview" and len(a["answer"]) > 20)

    a = KM.answer_question("banana hobby?", kd, "en")
    check("gibberish falls back to overview", a["intent"] == "overview" and len(a["answer"]) > 20,
          f"{a['intent']}")


def test_evidence_says_true():
    print("\n4. Evidence honesty (nothing invented)")
    kd = sample_kundali()
    m = KM.medha_analysis(kd, lang="en")
    seen_grahas = []
    for line in m["narrative"]["grahas"]:
        name = line.split()[0]
        seen_grahas.append(name)
    check("every narrated graha exists in chart",
          all(g in kd["planets"] for g in seen_grahas),
          [g for g in seen_grahas if g not in kd["planets"]])
    check("dasha narrative echoes computed dasha",
          KalaBodha.analyze_chart(kd, "en")["current_dasha"]["mahadasha"] in m["narrative"]["dasha"])


def test_llm_hook():
    print("\n5. LLM hook (graceful + pluggable)")
    kd = sample_kundali()
    check("llm_available('ollama') False offline", KM.llm_available("ollama", timeout=0.3) is False)
    try:
        KM.query_llm("sys", "prompt", provider="ollama", timeout=2)
        check("query_llm raises when offline", False)
    except KM.LLMUnavailableError:
        check("query_llm raises when offline", True)

    # absent provider name
    try:
        KM.query_llm("sys", "prompt", provider="nonexistent", timeout=2)
        check("unknown provider raises", False)
    except KM.LLMUnavailableError:
        check("unknown provider raises", True)

    # medha_with_llm must fall back deterministically
    m = KM.medha_with_llm(kd, lang="en")
    check("medha_with_llm falls back (llm False)", m["meta"]["llm"] is False)
    check("fallback still has narrative", "narrative" in m)

    # fake provider that responds
    class FakeProvider:
        ping_url = "http://127.0.0.1:1/unreachable"
        def generate(self, system, prompt, timeout=120):
            return "Fake LLM reading of the evidence."

    KM.register_provider("fake", lambda: FakeProvider())
    m2 = KM.medha_with_llm(kd, lang="en", provider="fake")
    check("fake provider unreachable -> fallback", m2["meta"]["llm"] is False)

    class ReachableProvider(FakeProvider):
        ping_url = "http://127.0.0.1:18767/probe"
        def generate(self, system, prompt, timeout=120):
            return "Fake LLM reading of the evidence."

    # make the ping succeed, then generate must be used
    ping_ok = {"v": True}
    class PingOk(ReachableProvider):
        @property
        def ping_url(self):
            return "http://127.0.0.1:18767/probe" if ping_ok["v"] else "http://127.0.0.1:1/off"
    KM.register_provider("fakeok", lambda: PingOk())
    with HTTPServer(("127.0.0.1", 18767), _ProbeHandler) as prober:
        threading.Thread(target=prober.serve_forever, daemon=True).start()
        time.sleep(0.2)
        m3 = KM.medha_with_llm(kd, lang="en", provider="fakeok")
        prober.shutdown()
    check("reachable provider used (llm True)", m3["meta"]["llm"] is True
          and m3["meta"]["llm_provider"] == "fakeok")
    check("llm_reading returned", "Fake LLM reading" in m3.get("llm_reading", ""))

    del KM._LLM_PROVIDERS["fake"]
    del KM._LLM_PROVIDERS["fakeok"]


class _ProbeHandler:
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.handle()

    def handle(self):
        self.request.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok")
        self.request.close()


PORT = 18768
BASE = f"http://127.0.0.1:{PORT}"


def test_http_and_cli():
    print("\n6. HTTP endpoint + CLI")
    srv = HTTPServer(("127.0.0.1", PORT), _import_KalaSetu().KalaSetuRequestHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.3)
    try:
        q = urllib.parse.urlencode({
            "date": "15-06-1990", "hour": "10", "minute": "30",
            "lat": "13.0827", "lon": "80.2707", "tz": "5.5",
            "question": "Where is Shani?"})
        with urllib.request.urlopen(f"{BASE}/medha?{q}", timeout=120) as r:
            d = json.loads(r.read())
        check("HTTP /medha returns medha+answer",
              "medha" in d and d["answer"]["graha"] == "Shani")
        check("HTTP /medha llm flag off", d["medha"]["meta"]["llm"] is False)

        with urllib.request.urlopen(f"{BASE}/openapi.json", timeout=30) as r:
            spec = json.loads(r.read())
        check("openapi documents /medha + alias",
              "/medha" in spec["paths"] and "/api/v1/medha" in spec["paths"])

        # cli --direct
        env = dict(os.environ)
        env["HOME"] = _TMP_HOME
        p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "kalayantra-cli.py"),
                            "medha", "--direct",
                            "--date", "15-06-1990", "--hour", "10", "--minute", "30",
                            "--lat", "13.0827", "--lon", "80.2707", "--tz", "5.5",
                            "--question", "Why is Shani strong?"],
                           capture_output=True, text=True, timeout=120, env=env)
        out = json.loads(p.stdout)
        check("CLI medha returns medha+answer", p.returncode == 0
              and "medha" in out and out["answer"]["graha"] == "Shani",
              f"rc={p.returncode} {p.stderr[:200]}")
    finally:
        srv.shutdown()
        srv.server_close()


def _import_KalaSetu():
    import KalaSetu
    return KalaSetu


def main():
    test_narrative()
    test_strengths()
    test_questions()
    test_evidence_says_true()
    test_llm_hook()
    test_http_and_cli()
    for d in (SCRIPTS, os.path.dirname(os.path.abspath(__file__))):
        import glob
        for c in glob.glob(os.path.join(d, "__pycache__")):
            shutil.rmtree(c, ignore_errors=True)
    shutil.rmtree(_TMP_HOME, ignore_errors=True)
    print(f"\n= {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())