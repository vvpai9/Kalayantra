#!/usr/bin/env python3
"""
KalaVidya — informational knowledge layer regression harness.

Run:  python3 tests/test_kalavidya.py

Covers:
   1. Catalog integrity: unique ids, valid categories, trilingual titles and
      summaries, complete detail/formula/example/source fields, and valid
      cross-references (see_also) — via the validate() report.
   2. Lookup helpers: concept_count, categories, concept_catalog (with and
      without a category filter), get_concept by id and by any-language title,
      missing-concept behaviour.
   3. Search: exact id, keyword ranking, IAST and Devanagari input.
   4. HTTP /vidya + /api/v1/vidya and the openapi.json contract (ephemeral
      daemon).
   5. vidya CLI: --direct catalog, --category, concept fetch, --search.
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

_TMP_HOME = tempfile.mkdtemp(prefix="kalayantra-test-vidya-")
os.environ["HOME"] = _TMP_HOME

import KalaVidya as KV

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


def test_validate():
    print("\n1. Catalog integrity")
    problems = KV.validate()
    check("validate() reports no problems", problems == [], "; ".join(problems[:4]))

    ids = [c["id"] for c in KV._CONCEPTS]
    check("concept ids are unique", len(ids) == len(set(ids)))
    check("every concept has keywords", all(c.get("keywords") for c in KV._CONCEPTS))
    check("every see_also target exists", all(
        all(r in ids for r in c.get("see_also", [])) for c in KV._CONCEPTS))


def test_catalog_helpers():
    print("\n2. Catalog + lookup helpers")
    n = KV.concept_count()
    check("concept_count >= 40", n >= 40, f"got {n}")
    cats = KV.categories("en")
    check("13 categories with titles", len(cats) == 13 and all(c["title"] for c in cats))
    cats_de = KV.categories("devanagari")
    by_id = {c["id"]: c["title"] for c in cats}
    check("devanagari category titles differ from English",
          all(by_id[c["id"]] != c["title"] for c in cats_de))

    full = KV.concept_catalog("en")
    check("catalog has one entry per concept", len(full) == n)
    pan = KV.concept_catalog("en", category="panchanga")
    check("category filter works", len(pan) > 0 and pan and all(
        c["category"] == "panchanga" for c in pan))

    t = KV.get_concept("tithi", "en")
    check("get_concept by id", t and t["id"] == "tithi")
    check("full entry fields", t and all(k in t for k in ("title", "summary", "detail",
                                                          "formula", "example", "source",
                                                          "keywords", "see_also")))
    check("formula explains the engine rule", t and "360" in t["formula"],
          t and t["formula"][:80])
    what_tithi = KV.get_concept(t["title"].upper(), "en")
    check("title lookup is case-insensitive on title",
          what_tithi and what_tithi["id"] == "tithi")
    dev = KV.get_concept("तिथि", "devanagari")
    check("get_concept by Devanagari title", dev and dev["id"] == "tithi")
    check("localized title returned", dev and dev["title"] != t["title"])
    check("unknown concept -> None", KV.get_concept("zzz-nope") is None)

    na = KV.get_concept("nakshatra", "en")
    check("nakshatra section present", na is not None)


def test_search():
    print("\n3. Search")
    s = KV.search_concepts("sade sati", "en")
    check("'sade sati' -> sade_sati first", s and s[0]["id"] == "sade_sati", str(s[:2]))
    s2 = KV.search_concepts("ekadashi", "iast")
    check("'ekadashi' (IAST) hits ekadashi", s2 and s2[0]["id"] == "ekadashi")
    s3 = KV.search_concepts("दशा", "en")
    check("Devanagari query finds dasha concepts", s3 and any(
        x["id"] in ("mahadasha", "antardasha", "vimshottari") for x in s3), str(s3[:3]))
    s4 = KV.search_concepts("", "en")
    check("empty query -> full catalog", len(s4) == KV.concept_count())
    check("results carry expected keys", bool(s) and set(s[0]) == {"id", "category",
                                                                   "title", "summary"})


class _ImportKalaSetuLazy:
    def __init__(self):
        self._mod = None

    def __getattr__(self, item):
        if self._mod is None:
            import KalaSetu
            self._mod = KalaSetu
        return getattr(self._mod, item)


PORT = 18770
BASE = f"http://127.0.0.1:{PORT}"


def test_http_and_cli():
    print("\n4. HTTP endpoint + CLI")
    srv = HTTPServer(("127.0.0.1", PORT), _ImportKalaSetuLazy().KalaSetuRequestHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.3)
    try:
        with urllib.request.urlopen(f"{BASE}/vidya", timeout=60) as r:
            d = json.loads(r.read())
        check("HTTP /vidya returns catalog + count + categories",
              "catalog" in d and d["count"] == KV.concept_count() and len(d["categories"]) == 13)

        q = urllib.parse.urlencode({"concept": "tithi"})
        with urllib.request.urlopen(f"{BASE}/vidya?{q}", timeout=60) as r:
            d = json.loads(r.read())
        check("HTTP /vidya concept fetch", d["found"] and
              d["concept"]["id"] == "tithi" and "example" in d["concept"])

        q = urllib.parse.urlencode({"q": "sade sati"})
        with urllib.request.urlopen(f"{BASE}/vidya?{q}", timeout=60) as r:
            d = json.loads(r.read())
        check("HTTP /vidya search", d["count"] >= 1 and d["search"][0]["id"] == "sade_sati")

        q = urllib.parse.urlencode({"category": "panchanga"})
        with urllib.request.urlopen(f"{BASE}/api/v1/vidya?{q}", timeout=60) as r:
            d = json.loads(r.read())
        check("HTTP /api/v1/vidya category filter",
              d["category"] == "panchanga" and d["count"] > 0 and
              all(c["category"] == "panchanga" for c in d["catalog"]))

        with urllib.request.urlopen(f"{BASE}/openapi.json", timeout=30) as r:
            spec = json.loads(r.read())
        check("openapi documents /vidya + alias",
              "/vidya" in spec["paths"] and "/api/v1/vidya" in spec["paths"])

        env = dict(os.environ)
        env["HOME"] = _TMP_HOME
        cli = os.path.join(SCRIPTS, "kalayantra-cli.py")
        p = subprocess.run([sys.executable, cli, "vidya", "--direct", "--format", "json"],
                           capture_output=True, text=True, timeout=120, env=env)
        out = json.loads(p.stdout)
        check("CLI vidya catalog", p.returncode == 0 and "catalog" in out
              and out["count"] == KV.concept_count(), f"rc={p.returncode} {p.stderr[:200]}")

        p = subprocess.run([sys.executable, cli, "vidya", "--direct", "tithi", "--format", "json"],
                           capture_output=True, text=True, timeout=120, env=env)
        out = json.loads(p.stdout)
        check("CLI vidya concept fetch", out["found"] and out["concept"]["id"] == "tithi")

        p = subprocess.run([sys.executable, cli, "vidya", "--direct",
                            "--category", "muhurta", "--format", "json"],
                           capture_output=True, text=True, timeout=120, env=env)
        out = json.loads(p.stdout)
        check("CLI vidya category filter", out["category"] == "muhurta" and out["count"] >= 5)

        p = subprocess.run([sys.executable, cli, "vidya", "--direct",
                            "--search", "brahma", "--format", "json"],
                           capture_output=True, text=True, timeout=120, env=env)
        out = json.loads(p.stdout)
        check("CLI vidya search", out["count"] >= 1, str(out.get("count")))
    finally:
        srv.shutdown()
        srv.server_close()


def main():
    test_validate()
    test_catalog_helpers()
    test_search()
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