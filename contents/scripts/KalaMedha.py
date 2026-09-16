# -*- coding: utf-8 -*-
"""
KalaMedha — the offline AI reading layer over KalaBodha's evidence graph.

KalaMedha turns the structured, evidence-backed conclusions produced by
KalaBodha (conclusion → factors → rule → source) into:

    1. A deterministic rule-based **narrative** (a natural-language chart
       reading), a per-graha **strength/weakness ranking** with reasons, and
       an **intent-driven Q&A** ("Where is Shani?", "Why is Guru strong?",
       "Which yogas are present?", "What does Mangala aspect?", …).
    2. An **optional LLM hook**: a pluggable provider (a bundled Ollama HTTP
       provider is included) that can re-write the same evidence into a fluent
       reading.  The hook is always optional — if no provider is reachable the
       deterministic engine serves the reply, so KalaMedha stays fully offline
       and dependency-free by default.

Like KalaBodha, KalaMedha never invents astronomical facts: every sentence is
derived from the chart + evidence that KalaBodha computed from it.

Public API surface (used by KalaSetu, CLI, and tests):

    medha_analysis(kundali, lang='en')          → narrative + strengths +
                                                    weaknesses + answers
    answer_question(question, kundali, lang='en')
    strengths_weaknesses(kundali, lang='en')
    generate_narrative(bodha, lang='en')        → narrative dict
    generate_prediction(birth_dt..., lang='en') → this-chart read via rule engine
    # optional LLM hook
    register_provider(name, factory)
    llm_available(provider='ollama', timeout=0.5) -> bool
    query_llm(system, prompt, provider='ollama', timeout=120) -> str  (raises on failure)
"""

from __future__ import annotations

import re

import KalaKosha
import KalaBodha


# ---------------------------------------------------------------------------
#  LLM hook: pluggable, always optional
# ---------------------------------------------------------------------------

_LLM_PROVIDERS = {}


class LLMUnavailableError(RuntimeError):
    """Raised when an LLM provider is not configured or not reachable."""


def register_provider(name: str, factory):
    """Register a provider factory: ``callable() -> callable(system, prompt) -> str``."""
    _LLM_PROVIDERS[name.lower()] = factory


def llm_available(provider: str = "ollama", timeout: float = 0.5) -> bool:
    """True if the named provider is registered AND currently reachable.

    Lightweight: pings the provider endpoint (only outcomes matter, so this is
    cheap for a local Ollama instance on 127.0.0.1)."""
    factory = _LLM_PROVIDERS.get(provider.lower())
    if factory is None:
        return False
    try:
        _LLM_PROVIDERS[provider.lower()] = factory
        test = factory()
        return _provider_ok(test, timeout)
    except Exception:
        return False


def _provider_ok(provider, timeout: float) -> bool:
    try:
        import urllib.request
        req = urllib.request.Request(
            provider.ping_url,
            method="HEAD",
        )
        with urllib.request.urlopen(req, timeout=timeout) as _r:
            return True
    except Exception:
        try:
            with urllib.request.urlopen(provider.ping_url, timeout=timeout) as _r:
                return True
        except Exception:
            return False


def query_llm(system: str, prompt: str, provider: str = "ollama",
              timeout: int = 120) -> str:
    """Send *system* + *prompt* to the provider and return generated text.

    Raises :class:`LLMUnavailableError` if the provider is missing/offline, or
    the provider raises on failure.  Callers should fall back to the rule
    engine on this exception."""
    factory = _LLM_PROVIDERS.get(provider.lower())
    if factory is None:
        raise LLMUnavailableError(f"no LLM provider '{provider}' registered")
    try:
        p = factory()
    except Exception as e:
        raise LLMUnavailableError(f"could not start provider '{provider}': {e}")
    try:
        return p.generate(system, prompt, timeout=timeout)
    except Exception as e:
        raise LLMUnavailableError(f"provider '{provider}' failed: {e}")


class OllamaProvider:
    """Minimal OpenAI-compatible /api/chat client for a local Ollama server."""

    DEFAULT_MODEL = "llama3.1"

    def __init__(self, base_url="http://127.0.0.1:11434", model=None):
        self.base_url = base_url.rstrip("/")
        self.model = model or self.DEFAULT_MODEL

    @property
    def ping_url(self):
        return f"{self.base_url}/api/tags"

    def generate(self, system: str, prompt: str, timeout: int = 120) -> str:
        import json
        import urllib.request

        payload = json.dumps({
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode("utf-8"))
        return (body.get("message") or {}).get("content", "").strip()


register_provider("ollama", lambda: OllamaProvider())


# ---------------------------------------------------------------------------
#  Deterministic rule engine
# ---------------------------------------------------------------------------

_INTENT_RE = {
    "where": re.compile(r"\b(where|position|located|place(d)?|situated)\b", re.I),
    "rashi": re.compile(r"\b(rashi|rasi|sign|zodiac)\b", re.I),
    "bhava": re.compile(r"\b(bhava|house|bhav|ascendant)\b", re.I),
    "strong": re.compile(r"\b(strong|powerful|prominent|benefic|boon|good)\b", re.I),
    "weak": re.compile(r"\b(weak|debilitated|neecha|afflicted|malefic|bad|problem)\b", re.I),
    "aspect": re.compile(r"\b(aspect|drishti|dristi|see(ing)?|view)\b", re.I),
    "yoga": re.compile(r"\b(yoga|yog|combination|rajayoga|result)\b", re.I),
    "dasha": re.compile(r"\b(dasha|dasa|period|mahadasha|timing|lifespan)\b", re.I),
    "motion": re.compile(r"\b(retrograde|vakri|direct|maargi|combust|asta)\b", re.I),
    "varga": re.compile(r"\b(varga|navamsa|divisional|d9|d-?1)\b", re.I),
    "nakshatra": re.compile(r"\b(nakshatra|nakshastra|naksatra|nakshatram|star)\b", re.I),
    "lagna": re.compile(r"\b(lagna|ascendant|lagan|rising)\b", re.I),
    "describe": re.compile(r"\b(tell me about|describe|explain|about|read(ing)?|character|personality)\b", re.I),
    "karaka": re.compile(r"\b(karaka|karak|significator|natural signific)\b", re.I),
    "overview": re.compile(r"\b(overview|summary|general|chart as a whole)\b", re.I),
}

_GRAPHAS_KEYWORDS = [
    "surya", "sun",                  # 0
    "chandra", "moon", "chandra",     # 1
    "mangala", "mars", "kuja",        # 2
    "budha", "mercury",               # 3
    "guru", "jupiter", "brihaspati",  # 4
    "shukra", "venus",                # 5
    "shani", "saturn",                # 6
    "rahu", "north node", "ketu",     # 7, 8 special-cased below
]
_GRAPHAS_LOOKUP = {
    "surya": 0, "sun": 0, "aditya": 0,
    "chandra": 1, "moon": 1, "soma": 1, "candra": 1,
    "mangala": 2, "mars": 2, "kuja": 2, "mangal": 2,
    "budha": 3, "mercury": 3, "bodha": 3,
    "guru": 4, "jupiter": 4, "brihaspati": 4, "brhaspati": 4, "upiter": 4,
    "shukra": 5, "venus": 5, "sukra": 5,
    "shani": 6, "saturn": 6, "sani": 6,
    "rahu": 7, "north node": 7,
    "ketu": 8, "south node": 8,
}


def _planet_match(question: str) -> int | None:
    ql = re.sub(r"[^a-z ]", " ", question.lower())
    ql = re.sub(r"\s+", " ", ql)
    for token, idx in _GRAPHAS_LOOKUP.items():
        if re.search(rf"\b{re.escape(token)}\b", ql):
            return idx
    return None


def _dignity_score(dignity_code: str | None) -> float:
    table = {
        "exalted": 5.0,
        "moolatrikona": 4.0,
        "own sign": 4.0,
        "friendly sign": 2.0,
        "neutral sign": 0.0,
        "enemy sign": -2.0,
        "debilitated": -4.0,
        None: 0.0,
        "none": 0.0,
    }
    return table.get(str(dignity_code).lower() if dignity_code else None, 0.0)


_HOUSE_VALUE = {
    1: 4, 4: 4, 5: 4, 7: 4, 9: 3, 10: 4,   # kendra (1,4,7,10) + trikona (1,5,9) + 10th
    2: 1, 3: -1,                              # 2nd dhana mildly good, 3rd parakrama minor
    6: -2, 8: -3, 12: -2,                     # dusthana
    11: 2,                                    # labha
}


def _house_score(house: int | None) -> float:
    if house is None:
        return 0.0
    return float(_HOUSE_VALUE.get(int(house), 0))


_KARAKA = {
    0: "Aatma", 1: "Manas (mind)", 2: "Bhrātr (courage)", 3: "Vidyā (speech/wisdom)",
    4: "Dharma (fortune)", 5: "Kāma (pleasures)", 6: "Karma (discipline)",
    7: "Upāya/tantra", 8: "Moksha",
}


def _status_names(statuses: list) -> list:
    return [s.get("name", "") for s in statuses]


def strengths_weaknesses(kundali: dict, lang: str = "en") -> dict:
    """Rank the nine grahas on an explainable, rule-based strength score.

    Score = dignity + house value + kendra/trikona from Chandra + Vargottama +
    retrogression (slightly polarizing) + participation in KalaBodha yogas."""
    bodha = KalaBodha.analyze_chart(kundali, lang)
    ctx_build = _bodha_context(bodha, kundali)
    planets = {}
    for p in (kundali.get("planets", {}) or {}).values():
        idx = p.get("idx")
        if idx is not None:
            planets[int(idx)] = p

    yogas = bodha.get("yogas", [])
    moon_house_map = {}
    moon_rashi = planets.get(1, {}).get("rashi")

    scores = {}
    reasons = {}
    for idx in range(9):
        p = planets.get(idx, {})
        rashi = p.get("rashi")
        name = KalaKosha.GRAHAS[lang][idx]
        if rashi is None:
            continue
        house = p.get("house")
        score = _dignity_score(p.get("dignity_code"))
        why = []

        if p.get("is_vargottam"):
            score += 1.5
            why.append("Vargottamā (same rāśi in D1 and D9)")

        if p.get("retrograde"):
            score += 0.5
            why.append("Vakrī — retrograde (often intensifies the graha)")

        if p.get("combust"):
            score -= 1.0
            why.append("Asta — combust near the Sun")
        elif p.get("asta"):
            score -= 1.0
            why.append("Asta")

        hs = _house_score(house)
        if hs:
            score += hs
            if hs > 0:
                why.append(f"{house}th house from Lagna")
            else:
                why.append(f"{house}th house from Lagna (dusthāna)")

        if moon_rashi is not None:
            from_moon = (int(rashi) - int(moon_rashi)) % 12 + 1
            if from_moon in (1, 4, 5, 7, 9, 10):
                score += 2.0
                why.append(f"{from_moon}th from Chandra (kendra/trikona)")

        # Yogas (KalaBodha already verified them with evidence)
        for y in yogas:
            if idx in y.get("participants", []):
                w = y.get("strength", 1)
                score += min(w, 3) * 0.75
                why.append(y.get("name", ""))

        scores[idx] = round(score, 2)
        reasons[idx] = why

    ranked = sorted((i for i in scores), key=lambda i: scores[i], reverse=True)
    return {
        "rankings": [{
            "idx": i,
            "name": KalaKosha.GRAHAS[lang][i],
            "score": scores[i],
            "reasons": reasons.get(i, []),
            "house": planets.get(i, {}).get("house"),
            "rashi_name": KalaKosha.RASIS[lang][planets.get(i, {}).get("rashi")]
                          if planets.get(i, {}).get("rashi") is not None else None,
        } for i in ranked],
        "strongest": ranked[0] if ranked else None,
        "strongest_name": KalaKosha.GRAHAS[lang][ranked[0]] if ranked else None,
        "weakest": ranked[-1] if ranked else None,
        "weakest_name": KalaKosha.GRAHAS[lang][ranked[-1]] if ranked else None,
        "yoga_count": len(yogas),
        "yogas": [y.get("name") for y in yogas],
    }


def _bodha_context(bodha: dict, kundali: dict) -> dict:
    """Small context object exposing the pieces the narrative needs."""
    return {
        "bodha": bodha,
        "answers": bodha.get("answers", {}),
        "evidence": bodha.get("evidence", []),
        "yogas": bodha.get("yogas", []),
        "lagna": bodha.get("lagna", {}),
        "current_dasha": bodha.get("current_dasha", {}),
        "houses": bodha.get("houses", {}),
        "grahas": bodha.get("grahas", []),
    }


def generate_narrative(bodha: dict, kundali: dict | None = None, lang: str = "en") -> dict:
    """Build a deterministic, evidence-cited narrative from a KalaBodha dict."""
    ctx = _bodha_context(bodha, kundali)
    lang = _normalize_lang(bodha, lang)
    answers = ctx["answers"]
    yogas = ctx["yogas"]
    lagna = ctx["lagna"]
    dasha = ctx["current_dasha"]

    sections = {}

    lagna_line = None
    if lagna.get("rashi_name"):
        lagna_line = f"Lagna is {lagna['rashi_name']} (lord {lagna.get('lagnesh')})."
    else:
        lagna_line = "Lagna could not be determined."
    sections["lagna"] = lagna_line

    graha_lines = []
    for fs in ctx["grahas"]:
        name = fs.get("name", "--")
        r = fs.get("rashi", {}).get("name")
        h = fs.get("bhava", {}).get("house")
        if h is None and r is None:
            continue
        parts = [name]
        if r:
            parts.append(f"in {r}")
        if h:
            parts.append(f"({h}th house)")
        dignity = fs.get("dignity", {}).get("label")
        if dignity:
            parts.append(f"· {dignity}")
        st = fs.get("status", [])
        if st and not all(s in ("Maargi",) for s in st):
            notable = [s for s in st if s != "Maargi"]
            if notable:
                parts.append(f"· {'/'.join(notable)}")
        graha_lines.append(" ".join(parts))
    sections["grahas"] = graha_lines

    yoga_lines = []
    for y in yogas:
        line = f"{y['name']}: {y.get('interpretation', y.get('condition', ''))}"
        if y.get("source"):
            line += f" (source: {y['source']})"
        yoga_lines.append(line)
    sections["yogas"] = yoga_lines

    if dasha.get("mahadasha"):
        md = f"{dasha['mahadasha']}"
        ad = dasha.get("antardasha") or "—"
        pd = dasha.get("pratyantardasha") or "—"
        dasha_line = f"Currently running {md} Mahadasha with {ad} Antardasha and {pd} Pratyantardasha."
    else:
        dasha_line = "Dasha periods could not be derived."
    sections["dasha"] = dasha_line

    # Pull a few strong pieces of evidence into a short "notable" list
    notable = []
    seen = set()
    for e in ctx["evidence"]:
        stmt = e.get("statement", "")
        if not stmt or stmt in seen:
            continue
        seen.add(stmt)
        notable.append(stmt)
        if len(notable) >= 10:
            break
    sections["notable_evidence"] = notable

    return sections


def _normalize_lang(bodha: dict, lang: str) -> str:
    meta_lang = (bodha.get("meta", {}) or {}).get("lang")
    return lang if lang in ("en", "iast", "devanagari") else (meta_lang or "en")


def _answer_key_for(idx: int) -> str:
    return KalaKosha.GRAHAS["en"][idx]


def answer_question(question: str, kundali: dict, lang: str = "en") -> dict:
    """Route a natural-language question to a deterministic, evidence-based answer."""
    bodha = KalaBodha.analyze_chart(kundali, lang)
    answers = bodha.get("answers", {})
    planets = {}
    for p in (kundali.get("planets", {}) or {}).values():
        if p.get("idx") is not None:
            planets[int(p["idx"])] = p

    idx = _planet_match(question)
    key = _answer_key_for(idx) if idx is not None else None
    graha_name = KalaKosha.GRAHAS[lang][idx] if idx is not None else None

    intents = [k for k, rx in _INTENT_RE.items() if rx.search(question)]

    if not intents:
        intents = ["overview"]

    if "lagna" in intents and idx is None:
        return _answer_overview(bodha, answers, intents, lang, "Lagna")
    if "overview" in intents and idx is None:
        return _answer_overview(bodha, answers, intents, lang, None)

    if idx is None and "dasha" in intents:
        ans = answers.get("current dasha", {})
        return {
            "question": question,
            "intent": "dasha",
            "graha": None,
            "answer": (f"Current dasha: {ans.get('mahadasha', '—')} Mahadasha / "
                       f"{ans.get('antardasha', '—')} Antardasha / "
                       f"{ans.get('pratyantardasha', '—')} Pratyantardasha."),
            "evidence": [{"statement": "from Vimshottari mahadasha timeline",
                          "rule": "Vimśottarī", "source": "KalaChakra"}],
        }

    if idx is None:
        return {
            "question": question,
            "intent": "unknown",
            "graha": None,
            "answer": (f"I can answer about the nine grahas, lagna, yogas and the "
                       f"current dasha. Try 'Where is Shani?', 'Is Guru strong?' "
                       f"'Which yogas are present?' or 'Tell me about Mangala'."),
            "evidence": [],
        }

    fs = next((g for g in bodha.get("grahas", []) if g.get("index") == idx), None)
    p = planets.get(idx, {})
    rashi = p.get("rashi")
    house = p.get("house")

    answer_parts = []
    evidence = []

    if any(i in intents for i in ("where", "rashi", "bhava", "position")):
        if rashi is not None:
            answer_parts.append(f"{graha_name} is in {KalaKosha.RASIS[lang][rashi]}, the {house}th house.")
            evidence.append({
                "statement": f"{graha_name} in {KalaKosha.RASIS[lang][rashi]} ({house}th house)",
                "rule": "D1 placement",
                "source": "KalaChakra",
            })
        else:
            answer_parts.append(f"{graha_name} could not be placed in the chart.")
    elif "motion" in intents:
        st = _status_names(fs.get("statuses", [])) if fs else []
        motions = [s for s in st if s in ("Asta", "Vakri", "Maargi")]
        answer_parts.append(f"{graha_name} is " + (" and ".join(motions) if motions else "in normal direct motion") + ".")
        if fs and fs.get("statuses"):
            evidence.extend(fs["statuses"])
    elif "aspect" in intents:
        out = fs.get("aspects_outgoing", []) if fs else []
        targets = [o.get("rashi_name") for o in out]
        answer_parts.append(f"{graha_name} aspects " + (", ".join(targets) if targets else "no placed graha from this definition") + ".")
        evidence.append({
            "statement": f"{graha_name} aspects " + (", ".join(targets) if targets else "nothing"),
            "rule": "Parāśarī / Jaimini aspect conventions",
            "source": "KalaBodha",
        })
    elif "yoga" in intents:
        yg = fs.get("yogas", []) if fs else []
        answer_parts.append(f"{graha_name} takes part in: " + (", ".join(yg) if yg else "no yogas from the built-in set") + ".")
        evidence.extend([{"statement": yname, "rule": "KalaBodha yoga engine", "source": "KalaBodha"}
                         for yname in yg])
    elif "varga" in intents:
        vp = fs.get("varga_placements", {}) if fs else {}
        line = ", ".join(f"{k}: {v}" for k, v in vp.items()) if vp else "no divisional data"
        answer_parts.append(f"{graha_name} in the minor charts — {line}.")
    elif "nakshatra" in intents:
        ns = fs.get("nakshatra", {}) if fs else {}
        if ns.get("name"):
            answer_parts.append(f"{graha_name} occupies {ns['name']} pada {ns.get('pada', 0)}.")
        else:
            answer_parts.append(f"{graha_name} nakshatra is not available.")
    elif any(i in intents for i in ("strong", "weak")):
        sw = strengths_weaknesses(kundali, lang)
        target = next((r for r in sw["rankings"] if r["idx"] == idx), None)
        if target:
            label = "strong" if target["score"] >= 0 else "coloured by challenges"
            score = target["score"]
            answer_parts.append(
                f"{graha_name} is relatively {label} (strength score {score:+.2f}) in this chart.")
            why = target.get("reasons", [])
            if why:
                answer_parts.append("Reasons: " + "; ".join(f"- {w}" for w in why))
                evidence.extend([{"statement": f"- {w}", "rule": "rule-based strength score",
                                  "source": "KalaMedha"} for w in why])
        else:
            answer_parts.append(f"{graha_name} is not placed in the chart.")
    elif "karaka" in intents:
        answer_parts.append(f"{graha_name} is the kārakā (significator) of {_KARAKA.get(idx, '—')}.")
    elif "describe" in intents:
        sw = strengths_weaknesses(kundali, lang)
        target = next((r for r in sw["rankings"] if r["idx"] == idx), None)
        st = _status_names(fs.get("statuses", [])) if fs else []
        quality = "strong and helpful" if target and target["score"] >= 1 else ("average" if target else "variable")
        if target and target["score"] < -1:
            quality = "challenging, needs careful handling"
        answer_parts.append(
            f"{graha_name} in {KalaKosha.RASIS[lang][rashi]}, {house}th house, appears {quality} "
            f"({(' / '.join(st)) if st else 'unremarkable status'}).")
        evidence = [{"statement": f"{graha_name} in {KalaKosha.RASIS[lang][rashi]}",
                     "rule": "D1 placement", "source": "KalaChakra"}]
        if target and target.get("reasons"):
            evidence.extend({"statement": w, "rule": "rule-based strength score", "source": "KalaMedha"}
                            for w in target["reasons"])
    elif "dasha" in intents:
        ans = answers.get("current dasha", {})
        answer_parts.append(
            f"Current dasha: {ans.get('mahadasha', '—')} Mahadasha / "
            f"{ans.get('antardasha', '—')} Antardasha / {ans.get('pratyantardasha', '—')} Pratyantardasha.")
        evidence.append({"statement": "from Vimshottari mahadasha timeline", "rule": "Vimśottarī",
                         "source": "KalaChakra"})
    else:
        # fallback: dense fact dump
        answer_parts.append(f"{graha_name}: {KalaKosha.RASIS[lang][rashi]}, {house}th house, "
                            f"dignity {p.get('dignity', '—')}.")
        ans_key = f"{KalaKosha.GRAHAS['en'][idx]} rashi"
        if ans_key in answers:
            answer_parts.append(f"(KalaBodha: {answers[ans_key]})")

    dedup = {}
    for e in evidence:
        if e.get("statement") not in dedup:
            dedup[e.get("statement")] = e
    evidence = list(dedup.values())

    return {
        "question": question,
        "intent": intents[0],
        "graha": KalaKosha.GRAHAS["en"][idx],
        "answer": " ".join(answer_parts).strip(),
        "evidence": evidence,
    }


def _answer_overview(bodha: dict, answers: dict, intents: list, lang: str,
                     topic: str | None) -> dict:
    sect = generate_narrative(bodha, lang=lang)
    if topic == "Lagna":
        ans = sect.get("lagna", "")
    else:
        lines = [
            sect.get("lagna", ""),
            "Yogas: " + ("; ".join(sect.get("yogas", [])) or "none detected"),
            sect.get("dasha", ""),
        ]
        ans = " ".join(lines).strip()
    return {
        "question": "overview",
        "intent": "overview" if topic is None else "lagna",
        "graha": None,
        "answer": ans,
        "evidence": bodha.get("evidence", [])[:8],
    }


# ---------------------------------------------------------------------------
#  Main entry point
# ---------------------------------------------------------------------------

def medha_analysis(kundali: dict, lang: str = "en") -> dict:
    """Full offline analysis: narrative + strengths/weaknesses + Q&A + source
    evidence.  Deterministic, no LLM required."""
    bodha = KalaBodha.analyze_chart(kundali, lang)
    narrative = generate_narrative(bodha, kundali, lang)
    sw = strengths_weaknesses(kundali, lang)

    return {
        "meta": {
            "engine": "KalaMedha",
            "llm": False,
            "chart": (kundali.get("meta", {}) or {}),
        },
        "narrative": narrative,
        "strengths_weaknesses": sw,
        "answers": bodha.get("answers", {}),
        "evidence": bodha.get("evidence", []),
        "current_dasha": bodha.get("current_dasha", {}),
    }


def medha_with_llm(kundali: dict, lang: str = "en", provider: str = "ollama",
                   timeout: int = 120, question: str | None = None) -> dict:
    """Hybrid entry point: try the LLM provider for a fluent reading; on any
    failure fall back to the deterministic engine and report ``llm: false``."""
    base = medha_analysis(kundali, lang)
    ok = llm_available(provider, timeout=0.5)
    if not ok:
        return base

    system = (
        "You are KalaMedha, an expert Jyotiṣa assistant inside an offline "
        "Panchanga tool. Base every statement strictly on the structured "
        "evidence provided. Do not invent planetary positions. Be concise."
    )
    prompt = _llm_prompt(base, lang, question)

    try:
        text = query_llm(system, prompt, provider=provider, timeout=timeout)
    except LLMUnavailableError:
        return base

    out = dict(base)
    out["meta"] = dict(base.get("meta", {}))
    out["meta"]["llm"] = True
    out["meta"]["llm_provider"] = provider
    out["llm_reading"] = text.strip()
    return out


def _llm_prompt(base: dict, lang: str, question: str | None) -> str:
    narrative = base.get("narrative", {})
    sw = base.get("strengths_weaknesses", {})

    ctx_lines = []
    for label, value in (narrative or {}).items():
        if isinstance(value, list):
            ctx_lines.append(f"## {label}\n" + "\n".join(f"- {v}" for v in value))
        elif value:
            ctx_lines.append(f"## {label}\n{value}")

    rank_lines = []
    for r in sw.get("rankings", []):
        why = "; ".join(r.get("reasons", [])) or "—"
        rank_lines.append(f"- {r['name']} (score {r['score']:+.2f}): {why}")
    if rank_lines:
        ctx_lines.append("## strength rankings\n" + "\n".join(rank_lines))

    ctx_text = "\n\n".join(ctx_lines)

    if question:
        return f"Chart evidence:\n\n{ctx_text}\n\nQuestion: {question}\n\nAnswer:"
    return (
        f"Below is the evidence-backed structure of a Jyotiṣa chart.\n\n"
        f"{ctx_text}\n\n"
        "Write a short, clear reading (3-5 short paragraphs): 1) Lagna and "
        "general temperament, 2) yoga highlights, 3) strongest and 4) weakest "
        "graha with reasons, 5) current dasha with a practical pointer. "
        "Cite no sources not present in the evidence."
    )


# ---------------------------------------------------------------------------
#  Convenience: compute a kundali then analyze
# ---------------------------------------------------------------------------

def generate_prediction(year, month, day, hour, minute, tz, lat, lon, alt,
                        ayanamsa: str = "lahiri", lang: str = "en",
                        use_llm: bool = False, provider: str = "ollama") -> dict:
    """One-call: compute the Kundali from a birth instant and run KalaMedha.

    ``use_llm=True`` attempts the hybrid path; it always degrades gracefully to
    the deterministic engine when a provider is unavailable."""
    import KalaChakra

    kd = KalaChakra.calculate_kundali(year, month, day, hour, minute, tz, lat, lon,
                                      alt, ayanamsa=ayanamsa, lang=lang)
    if use_llm:
        return medha_with_llm(kd, lang=lang, provider=provider)
    return medha_analysis(kd, lang=lang)