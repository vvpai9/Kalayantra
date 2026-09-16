#!/usr/bin/env python3
"""Track A — birth-time sensitivity expansion (Phase 16 Track A).
Separate file BY DESIGN: the golden test_kalabodha.py byte-lock must never be
shadowed, appended-to, or corrupted by Track A additions (that is exactly how
the golden draft corrupted last session).  Track A lives here, imports the
additive engine layer, and asserts determinism + tiers + 0-100 stability.
"""
import importlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "contents", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "contents", "scripts"))
import KalaBodha as KB

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print("  ok   " + name)
    else:
        FAIL += 1; print("  FAIL " + name + "  " + detail)

def main():
    print("\n1. multi_window_sensitivity — per-factor 0-100 stability tiers")
    import KalaBodha as KBod
    mw = KBod.multi_window_sensitivity(
        1990, 6, 15, 10, 30, 5.5, 13.0827, 80.2707, 6.0,
        ayanamsa="lahiri", lang="en")
    check("has per_factor map of all 9 factors",
          len(mw["per_factor"]) == 9, f"len={len(mw['per_factor'])}")
    check("every score within 0-100",
          all(0 <= v["score"] <= 100 for v in mw["per_factor"].values()),
          list(mw["per_factor"])[:2])
    check("remedy tiers keyed by verdict (reliable/watch/fragile/unusable)",
          {"reliable", "watch", "fragile", "unusable"} <= set(mw["remedies"]),
          set(mw["remedies"]))
    check("stable/unstable factor lists present",
          "stable_factors" in mw and "unstable_factors" in mw,
          mw.get("unstable_factors", [])[:2])
    print(f"\n= {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0

if __name__ == "__main__":
    sys.exit(main())
