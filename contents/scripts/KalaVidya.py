#!/usr/bin/env python3
"""
KalaVidya — the informational knowledge layer of KālaYantra.

KalaVidya answers "what is this concept?" and "how is it calculated?" for every
idea used elsewhere in the engine: the five limbs of the Panchanga, the lunar
calendar, sidereal astronomy, the nine grahas, lagna and vargas, Vimshottari
dasha, gochara, compatibility, muhurtas, festival logics and the KalaBodha /
KalaMedha reasoning layers.

Each concept entry carries:
  - a trilingual title and one-line summary (en / iast / devanagari),
  - a human-level ``detail`` describing what the concept means,
  - a ``formula`` describing how KālaYantra actually computes it,
  - a self-consistent worked ``example``,
  - the classical or technical ``source`` attribution,
  - ``keywords`` for search and ``see_also`` cross references.

The module is pure data + lookup helpers (it needs no Swiss Ephemeris), so it
can be served by KalaSetu (``/vidya``), used by the `kalayantra-cli vidya`
subcommand, or imported directly by tests and QML tooling.

Usage:
    import KalaVidya
    KalaVidya.categories()                 # category slugs
    KalaVidya.concept_catalog("en")        # id/title/summary for every concept
    KalaVidya.get_concept("tithi", "en")   # full entry (or None)
    KalaVidya.search_concepts("sade sati") # ranked search across text fields
    KalaVidya.concept_count()              # total number of entries
"""
from __future__ import annotations

CATEGORIES = [
    "panchanga",      # the five daily limbs
    "time",           # lunisolar calendar, seasons, clock
    "sidereal",       # astronomy & reference frames
    "graha",          # the nine planets: placement, dignity, dynamics
    "lagna",          # the ascendant
    "varga",          # divisional charts
    "dasha",          # Vimshottari period systems
    "gochara",        # transits
    "compatibility",  # Guna Milan / Ashtakoota
    "muhurta",        # auspicious timing systems
    "festival",       # observance & festival rules
    "method",         # engine operating modes
    "reasoning",      # KalaBodha / KalaMedha layers
]

CATEGORY_TITLES = {
    "panchanga":      {"en": "Panchanga (the five limbs)",
                       "iast": "Pañchāṅga",
                       "devanagari": "पञ्चाङ्ग"},
    "time":           {"en": "Lunisolar calendar & time",
                       "iast": "Kāla",
                       "devanagari": "काल"},
    "sidereal":       {"en": "Sidereal astronomy",
                       "iast": "Siddhānta",
                       "devanagari": "सिद्धान्त"},
    "graha":          {"en": "The nine grahas",
                       "iast": "Navagraha",
                       "devanagari": "नवग्रह"},
    "lagna":          {"en": "The ascendant",
                       "iast": "Lagna",
                       "devanagari": "लग्न"},
    "varga":          {"en": "Divisional charts",
                       "iast": "Varga",
                       "devanagari": "वर्ग"},
    "dasha":          {"en": "Period systems",
                       "iast": "Daśā",
                       "devanagari": "दशा"},
    "gochara":        {"en": "Transits",
                       "iast": "Gocāra",
                       "devanagari": "गोचर"},
    "compatibility":  {"en": "Compatibility (Guna Milan)",
                       "iast": "Gūṇa Milana",
                       "devanagari": "गुण मिलन"},
    "muhurta":        {"en": "Auspicious timing",
                       "iast": "Muhūrta",
                       "devanagari": "मुहूर्त"},
    "festival":       {"en": "Festivals & observances",
                       "iast": "Utsava",
                       "devanagari": "उत्सव"},
    "method":         {"en": "Engine operating modes",
                       "iast": "Paddhati",
                       "devanagari": "पद्धति"},
    "reasoning":      {"en": "Reasoning layers",
                       "iast": "Vidyā",
                       "devanagari": "विद्या"},
}


def _L(text, lang):
    """Localize a trilingual dict or pass a plain string through."""
    if isinstance(text, dict):
        return text.get(lang) or text.get("en") or ""
    return text


# ---------------------------------------------------------------------------
# The KalaVidya knowledge base.
# Each entry: id, category, title{en,iast,devanagari}, summary{...}, detail,
# formula, example, source, keywords[list], see_also[list].
# ---------------------------------------------------------------------------
_CONCEPTS = [
    # -------------------------------------------------------------- panchanga
    {
        "id": "panchanga",
        "category": "panchanga",
        "title": {"en": "Panchanga — the five limbs of a day",
                  "iast": "Pañchāṅga",
                  "devanagari": "पञ्चाङ्ग"},
        "summary": {"en": "The five classical components that together describe a day.",
                    "iast": "The five classical components that together describe a day.",
                    "devanagari": "पंचांग — दिन के पाँच अंग"},
        "detail": ("The Pañchāṅga ('five limbs') is the traditional Hindu almanac "
                   "compressed to five daily quantities: Tithi (lunar day), Nakshatra "
                   "(constellation of the Moon), Yoga (index of combined Sun–Moon "
                   "longitude), Karana (half-tithi) and Vaara (weekday). Each is a "
                   "measurable section of an astronomical cycle, evaluated at a fixed "
                   "anchor point — by convention at sunrise (Udaya). KālaYantra reports "
                   "every element in 'at sunrise' and 'after transition' forms, marks "
                   "which one is active at dawn, and shows the exact transition clock "
                   "time in 24+ notation for events after midnight."),
        "formula": ("tithi   = floor(((Moon − Sun) mod 360°) / 12°)\n"
                    "nakshatra = floor(Moon / (360°/27)) mod 27, each with 4 pādas\n"
                    "yoga    = floor(((Sun + Moon) mod 360°) / (360°/27)) mod 27\n"
                    "karana  = floor(((Moon − Sun) mod 360°) / 6°)  (60 karaṇas)\n"
                    "vaara   = weekday of the Julian Day number, Sunday-first"),
        "example": ("KālaYantra's /day endpoint returns these five limbs with _1/_2 "
                    "(sunrise and next) forms plus _end transition times, e.g. "
                    "\"tithi_1\": \"Pratipada\", \"tithi_2\": \"Dwitiya\", "
                    "\"tithi_2_end\": \"31:09\" (next day 07:09)."),
        "source": "Classical Pañchāṅga tradition (Sūrya Siddhānta); modern Udaya-ādi convention.",
        "keywords": ["five limbs", "almanac", "panchang", "daily elements", "tithi nakshatra yoga karana vaara"],
        "see_also": ["tithi", "nakshatra", "yoga_panchanga", "karana", "vaara", "traditional_mode"],
    },
    {
        "id": "tithi",
        "category": "panchanga",
        "title": {"en": "Tithi — the lunar day",
                  "iast": "Tithi",
                  "devanagari": "तिथि"},
        "summary": {"en": "A thirtieth of the synodic (lunar) month: 12° of Moon–Sun elongation.",
                    "iast": "A thirtieth of the synodic (lunar) month: 12° of Moon–Sun elongation.",
                    "devanagari": "मास का तीसवाँ भाग — 12° चन्द्र-सूर्य वियोग"},
        "detail": ("One tithi is the time the Moon takes to gain 12° on the Sun in "
                   "elongation; thirty such steps complete the lunar month (360°/12°). "
                   "The first fifteen are the Shukla (waxing) fortnight ending in "
                   "Pūrṇimā, the second fifteen the Kṛṣṇa (waning) fortnight ending in "
                   "Amāvasyā. Because the Moon speeds up near perigee, some days may "
                   "skip a tithi (Kṣaya) or hold one across two sunrises (Vṛddhi). "
                   "KālaYantra evaluates the tithi both at sunrise and live, computes "
                   "its ending instant, and flags kṣaya days so observances are merged "
                   "correctly."),
        "formula": ("tithi_index = int(((moon_l − sun_l) mod 360.0) / 12.0) mod 30\n"
                    "0–14 → Shukla Pratipadā … Pūrṇimā; 15–29 → Kṛṣṇa Pratipadā … Amāvasyā."),
        "example": ("Elongation 12° → index 1 (Dwitīyā). For the 1990-06-15 10:30 IST "
                    "sample chart the running tithi bracket is computed the same way from "
                    "the sidereal Sun and Moon at the moment of interest."),
        "source": "Sūrya Siddhānta; Bṛhat Saṁhitā.",
        "keywords": ["lunar day", "pratipada", "purnima", "amavasya", "shukla", "krishna", "paksha"],
        "see_also": ["paksha", "karana", "kshaya_tithi", "panchanga"],
    },
    {
        "id": "nakshatra",
        "category": "panchanga",
        "title": {"en": "Nakshatra — the lunar mansion",
                  "iast": "Nakṣatra",
                  "devanagari": "नक्षत्र"},
        "summary": {"en": "One of 27 (or 28) fixed star mansions; 13°20′ of ecliptic longitude each.",
                    "iast": "One of 27 (or 28) fixed star mansions; 13°20′ of ecliptic longitude each.",
                    "devanagari": "27 नक्षत्र — प्रत्येक 13°20′"},
        "detail": ("The ecliptic is divided into 27 equal mansions of 360°/27 = "
                   "13°20′ = 800′ each, reckoned from Aśvinī. Every mansion is ruled "
                   "by one graha (the Nakṣatrādhipati) and is further split into four "
                   "pādas of 3°20′, giving 108 pādas matched to the 9 grahas × 12 "
                   "rāśis. The Moon's nakshatra anchors the Vimshottari dasha cycle; "
                   "the Sun's nakshatra is also computed by the engine so solar "
                   "transitions can be shown."),
        "formula": ("nakshatra_index = int(moon_sidereal_lon / 13.3333…) mod 27\n"
                    "pada = int((moon_sidereal_lon mod 13.3333…) / 3.3333…) + 1"),
        "example": ("Moon at 88° → 88/13.3333 = 6.6 → index 6 = Punarvasu; "
                    "88 mod 13.3333 = 8.0 → 8.0/3.3333 = 2.4 → pāda 3."),
        "source": "Sūrya Siddhānta; Bṛhat Jātaka.",
        "keywords": ["mansion", "star", "lunar asterism", "pada", "ashwini", "revati", "moon star"],
        "see_also": ["vimshottari", "panchanga", "lagna"],
    },
    {
        "id": "yoga_panchanga",
        "category": "panchanga",
        "title": {"en": "Yoga (Panchanga) — the third limb",
                  "iast": "Yoga",
                  "devanagari": "योग"},
        "summary": {"en": "One of 27 daily yogas derived from the sum of the Sun's and Moon's longitudes.",
                    "iast": "One of 27 daily yogas derived from the sum of the Sun's and Moon's longitudes.",
                    "devanagari": "सूर्य-चन्द्र योग से 27 योग"},
        "detail": ("The daily (panchanga) yoga is unrelated to the Raja/Dhana yogas of "
                   "prognostication: it is a pure time-keeping index. Sun and Moon "
                   "longitudes are summed, reduced mod 360° and divided into 27 equal "
                   "parts of 13°20′. Each index carries a lineage of meanings "
                   "(e.g. Vishkambha, Dhruva, Vaidhriti) used in muhurta selection, "
                   "with auspicious and inauspicious attributes."),
        "formula": ("yoga_index = int(((sun_l + moon_l) mod 360.0) / 13.3333…) mod 27"),
        "example": ("Sun 60° + Moon 90° = 150° → 150/13.3333 = 11.25 → index 11 = Dhruva."),
        "source": "Sūrya Siddhānta; Muhūrta (nitya-yoga) tradition.",
        "keywords": ["daily yoga", "sun moon sum", "vishkambha", "dhruva", "third limb"],
        "see_also": ["panchanga", "muhurta"],
    },
    {
        "id": "karana",
        "category": "panchanga",
        "title": {"en": "Karana — the half-tithi",
                  "iast": "Karaṇa",
                  "devanagari": "करण"},
        "summary": {"en": "Half a tithi (6° of elongation); 11 karanas in 60 recurring slots.",
                    "iast": "Half a tithi (6° of elongation); 11 karaṇas in 60 recurring slots.",
                    "devanagari": "तिथि का आधा — 60 करण"},
        "detail": ("A karana is the time in which the Moon gains 6° on the Sun — half a "
                   "tithi — so each lunar month holds 60 karanas. Seven movable karanas "
                   "(Bava, Bālava, Kaulava, Taitila, Gara, Vaṇija, Vishti) repeat 8 "
                   "times (56) plus four fixed ones (Shakuni, Chatushpāda, Nāga, "
                   "Kintughna) give the full 60. KālaYantra reports the karana at "
                   "sunrise, its transition, and the active index."),
        "formula": ("karana_index = int(((moon_l − sun_l) mod 360.0) / 6.0)\n"
                    "indices 0–55 cycle the seven chara karaṇas; 56–59 are the four stira karaṇas."),
        "example": ("Elongation of 6° → index 1 = Bālava; 60° → index 10 = Vaṇija."),
        "source": "Sūrya Siddhānta; Jyotiṣa Karaṇa literature.",
        "keywords": ["half tithi", "bava", "vishti", "chara", "stira", "60 karanas"],
        "see_also": ["tithi", "panchanga"],
    },
    {
        "id": "vaara",
        "category": "panchanga",
        "title": {"en": "Vaara — the weekday",
                  "iast": "Vāra",
                  "devanagari": "वार"},
        "summary": {"en": "The seven-day cycle named after its ruling graha.",
                    "iast": "The seven-day cycle named after its ruling graha.",
                    "devanagari": "ग्रहों के नाम पर सात वार"},
        "detail": ("Weekdays are the one wholly secular limb of the pañchāṅga, named for "
                   "the graha ruling the first hour of the day: Ravivāra (Sun), "
                   "Somavāra (Moon), Maṅgalavāra (Mars), Budhavāra (Mercury), "
                   "Guruvāra (Jupiter), Śukravāra (Venus), Śanivāra (Saturn). The "
                   "day is also classed Sthira or Chara (fixed / moving), which matters "
                   "for choosing unlucky days for certain acts."),
        "formula": ("vaara = weekday of the Julian Day number, Sun-first ordering."),
        "example": ("1990-06-15 was a Friday (Śukravāra); the engine derives it from the "
                    "Julian Day number."),
        "source": "Common jyotiṣa convention; Bṛhat Saṁhitā.",
        "keywords": ["weekday", "day of week", "ravi", "som", "mangal", "shani", "sthira", "chara"],
        "see_also": ["panchanga"],
    },

    # ------------------------------------------------------------------- time
    {
        "id": "masa",
        "category": "time",
        "title": {"en": "Masa — the lunar month",
                  "iast": "Māsa",
                  "devanagari": "मास"},
        "summary": {"en": "Lunar month named by the sankranti it contains (Chaitra … Phalguna).",
                    "iast": "Lunar month named by the sankranti it contains (Chaitra … Phalguna).",
                    "devanagari": "संक्रांति से नामित चान्द्र मास"},
        "detail": ("Twelve lunar months run from Chaitra to Phalguna. A lunar month is "
                   "named after the solar month that contains it — specifically the "
                   "synodic month in which the Sun's saṅkrānti (entry into a sign) "
                   "falls. The convention changes the boundary: amāvasyānta months end "
                   "at new moon, pūrṇimānta at full moon. Adhika (intercalary) and "
                   "Kṣaya (lost) months fall out naturally when a lunar month contains "
                   "zero or two saṅkrāntis. KālaYantra exposes both conventions via "
                   "the month_system setting and reports the Masa index and era "
                   "(Shaka/Vikrama/Kali) numbers."),
        "formula": ("Find the saṅkrānti bracketing the lunation; masa index = that "
                    "solar month index (Chaitra=0 … Phalguna=11); adjust for "
                    "amāvasyānta/pūrṇimānta and adhika/kshaya detection."),
        "example": ("The engine's get_lunar_month_details() returns, e.g., "
                    "\"Bhadrapada\" (index 5) with the era years for any date."),
        "source": "Sūrya Siddhānta; Pañchāṅga traditional astronomy.",
        "keywords": ["lunar month", "chaitra", "adhika masa", "intercalary", "amavasyanta", "purnimanta"],
        "see_also": ["paksha", "tithi", "sankranti", "samvatsara", "saura_calendar"],
    },
    {
        "id": "paksha",
        "category": "time",
        "title": {"en": "Paksha — the fortnight",
                  "iast": "Pakṣa",
                  "devanagari": "पक्ष"},
        "summary": {"en": "Shukla (waxing) or Krishna (waning) half of the lunar month.",
                    "iast": "Śukla / Kṛṣṇa pakṣa",
                    "devanagari": "शुक्ल / कृष्ण पक्ष"},
        "detail": ("Each lunar month is two fortnights: Śukla Pakṣa from Pratipadā to "
                   "Pūrṇimā (Moon waxing toward Sun opposition) and Kṛṣṇa Pakṣa to "
                   "Amāvasyā. Paksha is used by observance rules (Ekadaśī is always "
                   "Śukla or Kṛṣṇa Ekadaśī), festival logic and ashtakoota/reminder "
                   "matching."),
        "formula": ("paksha = 'Shukla' if tithi_index in 0..14 else 'Krishna'."),
        "example": ("Tithi index 9 → Shukla Navamī; index 24 → Krishna Navamī."),
        "source": "Common jyotiṣa convention.",
        "keywords": ["fortnight", "waxing", "waning", "shukla", "krishna", "purnima", "amavasya"],
        "see_also": ["tithi", "masa", "ekadashi"],
    },
    {
        "id": "ritu",
        "category": "time",
        "title": {"en": "Ritu — the season",
                  "iast": "Ṛtu",
                  "devanagari": "ऋतु"},
        "summary": {"en": "The six ritus: Vasanta, Grishma, Varsha, Sharad, Hemanta, Shishira.",
                    "iast": "The six ṛtus: Vasanta, Grīṣma, Varṣā, Śarad, Hemanta, Śiśira.",
                    "devanagari": "छह ऋतु — वसंत, ग्रीष्म, वर्षा, शरद, हेमंत, शिशिर"},
        "detail": ("The Hindu year is six two-month seasons keyed to the lunar months: "
                   "Vasanta (Chaitra–Vaishakha), Grīṣma (Jyeshtha–Ashadha), Varṣā "
                   "(Shravana–Bhadrapada), Śarad (Ashvin–Kartika), Hemanta "
                   "(Margashirsha–Pausha), Śiśira (Magha–Phalguna). KālaYantra attaches "
                   "the ritu (with hints like 'Varṣā (Monsoon)') to every day record."),
        "formula": ("ritu_index = floor(masa_index / 2) mapped to the six-season table."),
        "example": ("Bhadrapada (masa index 5) → floor(5/2)=2 → Varṣā (Monsoon)."),
        "source": "Ṛtu classification per classical calendar; Viṣṇu Purāṇa references.",
        "keywords": ["season", "vasant", "grishma", "varsha", "sharad", "hemant", "shishir"],
        "see_also": ["masa", "ayana"],
    },
    {
        "id": "ayana",
        "category": "time",
        "title": {"en": "Ayana — the tropical half-year",
                  "iast": "Ayana",
                  "devanagari": "अयन"},
        "summary": {"en": "Uttarayana (Sun northward) and Dakshinayana (Sun southward).",
                    "iast": "Uttarāyaṇa / Dakṣiṇāyana",
                    "devanagari": "उत्तरायण / दक्षिणायण"},
        "detail": ("The two ayanas mark the Sun's apparent travel in declination: "
                   "Uttarāyaṇa while the Sun moves north of its southernmost point "
                   "(sidereal roughly Makara → Mithuna), Dakṣiṇāyana the rest. The "
                   "switch day is Makara Saṅkrānti / Karka tropic, and it flavors "
                   "festival timing and muhurta."),
        "formula": ("if 0 <= sun_sidereal < 180 → Uttarāyaṇa (Sun in the first six signs)\n"
                    "else → Dakṣiṇāyana."),
        "example": ("A Sun at 300° (Makara) → Dakṣiṇāyana just ended → Uttarāyaṇa begins "
                    "at Makara Saṅkrānti."),
        "source": "Common jyotiṣa convention.",
        "keywords": ["uttarayana", "dakshinayana", "solstice", "tropic", "makara sankranti"],
        "see_also": ["sankranti", "saura_calendar"],
    },
    {
        "id": "samvatsara",
        "category": "time",
        "title": {"en": "Samvatsara — the named year cycle",
                  "iast": "Saṁvatsara",
                  "devanagari": "संवत्सर"},
        "summary": {"en": "The 60-year cycle; each year has a name (e.g. Parabhava).",
                    "iast": "The 60-year saṁvatsara cycle.",
                    "devanagari": "60 संवत्सर"},
        "detail": ("Years are counted in a repeating cycle of 60 named saṁvatsaras "
                   "(Prabhava, Vibhava, Shukla, Pramoda, … Plava, Kilaka, Sorumana, "
                   "Sadharana, Virodhakrit, Parabhava …). The same date is expressed in "
                   "several eras — Shaka (official Indian civil era, ~78 CE offset), "
                   "Vikrama (~57 BCE offset) and Kali (~3102 BCE offset). The 60-year "
                   "index is derived from the Shaka year with a Chaitra-boundary rule."),
        "formula": ("samvatsara_index ≈ (shaka_year − 50) mod 60\n"
                    "era_year: Shaka = CE − 78; Vikrama = CE + 57; Kali = CE + 3101."),
        "example": ("Shaka 1948 → (1948−50) mod 60 = 38 → Parabhava."),
        "source": "Bṛhat Saṁhitā; traditional 60-year cycle.",
        "keywords": ["year name", "60 year cycle", "shaka", "vikram", "kali", "prabhava", "parabhava"],
        "see_also": ["masa"],
    },
    {
        "id": "ghadi_vipal",
        "category": "time",
        "title": {"en": "Ghadi-Vipal — the traditional clock",
                  "iast": "Ghaṭī / Vikalā",
                  "devanagari": "घड़ी-विपल"},
        "summary": {"en": "The 60-unit day: 1 ghadi = 24 minutes, 1 vipal = 24 seconds.",
                    "iast": "The 60-unit day: 1 ghaṭī = 24 minutes, 1 vikalā = 24 seconds.",
                    "devanagari": "१ घड़ी = २४ मिनट, १ विपल = २४ सेकंड"},
        "detail": ("Indian time reckoning divides the civil day into 60 ghaṭīs of 24 "
                   "minutes each, and each ghaṭī into 60 vikalās (vipals) of 24 seconds. "
                   "Brahma-muhurta and certain muhurta boundaries are expressed in "
                   "ghaṭīs; KālaYantra's live Ghadi-Vipal clock converts the current "
                   "local time into Ghaṭī:Pal in real time."),
        "formula": ("ghadis_elapsed = minutes_since_local_midnight / 24.0\n"
                    "vipals = (ghadis_elapsed mod 1) × 60"),
        "example": ("At 06:12 local → 372 minutes / 24 = 15.5 → 15 ghaṭī 30 vipals."),
        "source": "Jyotiṣa time-keeping convention (nāḍī/vināḍī).",
        "keywords": ["ghati", "ghadi", "vipal", "nalika", "traditional clock", "time units"],
        "see_also": ["brahma_muhurta"],
    },
    {
        "id": "sunrise_sunset",
        "category": "time",
        "title": {"en": "Sunrise / Sunset computation",
                  "iast": "Udaya / Asta",
                  "devanagari": "सूर्योदय-सूर्यास्त"},
        "summary": {"en": "Rise and set instants from ephemeris geometry, refraction, and altitude.",
                    "iast": "Rise and set instants from ephemeris geometry, refraction, and altitude.",
                    "devanagari": "ज्यामिति, अपवर्तन व ऊँचाई से सूर्योदय/अस्त"},
        "detail": ("Rise/set events are computed with the Swiss Ephemeris rise/transit "
                   "routines using the astro-observation centre (location, altitude "
                   "above mean sea level) and the standard apparent horizon with a "
                   "−0.833° refraction correction. These anchor the pañchāṅga "
                   "convention (elements read at sunrise) and the daytime reckoning "
                   "for horas, muhurtas, Rāhu Kāla and Choghadiya. Moonrise/moonset "
                   "are computed the same way."),
        "formula": ("solve rise/transit(jd, centre = location, altiude-corrected) "
                    "for the moment the upper limb crosses the −0.833° horizon."),
        "example": ("For Ujjain defaults on 12-09-2026 the engine reports sunrise 06:12 "
                    "and sunset 18:34 local."),
        "source": "Swiss Ephemeris rise/transit algorithms.",
        "keywords": ["sunrise", "sunset", "rise set", "moonrise", "moonset", "udaya", "asta kala"],
        "see_also": ["swiss_ephemeris", "traditional_mode", "hora"],
    },
    {
        "id": "brahma_muhurta",
        "category": "time",
        "title": {"en": "Brahma Muhurta",
                  "iast": "Brāhma Muhūrta",
                  "devanagari": "ब्राह्म मुहूर्त"},
        "summary": {"en": "The ~96-minute auspicious span ending just before sunrise.",
                    "iast": "The ~96-minute auspicious span ending just before sunrise.",
                    "devanagari": "सूर्योदय से पूर्व ~96 मिनट"},
        "detail": ("Brahma-muhūrta is the period roughly 96 minutes before sunrise, "
                   "traditionally the finest time for meditation, study and new "
                   "beginnings. KālaYantra computes it as sunrise minus 96 minutes and "
                   "exposes it on every day record and as a reminder time-target."),
        "formula": ("brahma_muhurta_start = sunrise − 96 minutes\n"
                    "brahma_muhurta_end   = sunrise"),
        "example": ("Sunrise 06:12 → Brahma Muhurta 04:36–05:24."),
        "source": "Yoga/Āyurveda texts; common convention (two ghaṭīs before dawn).",
        "keywords": ["brahma muhurta", "brahmamuhurta", "dawn", "meditation time", "96 min"],
        "see_also": ["sunrise_sunset", "ghadi_vipal"],
    },

    # ---------------------------------------------------------------- sidereal
    {
        "id": "ayanamsa",
        "category": "sidereal",
        "title": {"en": "Ayanamsa — sidereal precession offset",
                  "iast": "Ayanāṁśa",
                  "devanagari": "अयनांश"},
        "summary": {"en": "The offset between tropical and sidereal longitudes caused by precession.",
                    "iast": "The offset between tropical and sidereal longitudes caused by precession.",
                    "devanagari": "अयनांश — विषुव चलन से अंतर"},
        "detail": ("Vedic astronomy counts the zodiac from a fixed starry frame, whereas "
                   "the 'tropical' zodiac starts at the equinox. Equinox precession "
                   "(~50.3″ per year) means the two frames drift; the difference at any "
                   "moment is the ayanāṁśa. Different schools fix the zero point "
                   "differently. KālaYantra supports lahiri (the Indian standard, "
                   "Revati/Chitrā based), raman, krishnamurti, true_citra, "
                   "fagan_bradley and deluce, plus sayana (tropical) for comparison."),
        "formula": ("swe.set_sid_mode(SIDM_…); sidereal = tropical − ayanāṁśa(jd)\n"
                    "engine API: set_ayanamsa(mode), get_ayanamsa_value(jd_ut)."),
        "example": ("The same instant yields different rāśis in lahiri vs sayana; "
                    "the /kundali endpoint returns the sayana chart when ayanamsa=sayana."),
        "source": "Sūrya Siddhānta; modern Lahiri ephemeris convention (ICAS, N.C. Lahiri).",
        "keywords": ["precession", "sidereal", "tropical", "lahiri", "raman", "krishnamurti", "true citra", "fagan", "sayana"],
        "see_also": ["sidereal_longitude", "swiss_ephemeris"],
    },
    {
        "id": "sidereal_longitude",
        "category": "sidereal",
        "title": {"en": "Sidereal longitude & rashi",
                  "iast": "Nirayana longitude; rāśi",
                  "devanagari": "निरयण देशान्तर; राशि"},
        "summary": {"en": "Position of a graha in the fixed zodiac; 30° rashi bands from Mesha.",
                    "iast": "Position of a graha in the fixed zodiac; 30° rāśi bands.",
                    "devanagari": "नक्षत्र-राशि में ग्रह स्थिति"},
        "detail": ("Every graha's sidereal longitude is its ecliptic position measured "
                   "from the ayanāṁśa-corrected zero point. The 360° belt is divided "
                   "into 12 rāśis of 30°: Mesha, Vrishabha, Mithuna, Karka, Simha, "
                   "Kanya, Tula, Vrischika, Dhanu, Makara, Kumbha, Meena. The engine "
                   "computes longitude via the Swiss Ephemeris and derives rashi, "
                   "nakshatra, pada and house from it."),
        "formula": ("sidereal = (swe.calc_ut(jd, planet, FLG_SIDEREAL)) mod 360\n"
                    "rashi = floor(sidereal / 30.0) mod 12"),
        "example": ("In the 1990-06-15 10:30 IST sample chart, Surya sits in Mithuna "
                    "(rashi 2) and Chandra in Kumbha (rashi 10)."),
        "source": "Swiss Ephemeris sidereal mode; Sūrya Siddhānta rāśi divisions.",
        "keywords": ["sidereal", "longitude", "rashi", "rasi", "mesha", "mina", "navamsha base"],
        "see_also": ["ayanamsa", "graha", "lagna"],
    },
    {
        "id": "swiss_ephemeris",
        "category": "sidereal",
        "title": {"en": "Swiss Ephemeris engine",
                  "iast": "Swiss Ephemeris",
                  "devanagari": "स्विस एफ़ेमेरिस"},
        "summary": {"en": "The high-precision astronomical library powering all geometry.",
                    "iast": "The high-precision astronomical library powering all geometry.",
                    "devanagari": "सटीक खगोलीय गणना के लिए पुस्तकालय"},
        "detail": ("KālaYantra performs all astronomical computation through the Swiss "
                   "Ephemeris (pyswisseph): planetary positions, rise/set events, "
                   "retrograde detection via the speed vector, house cusps "
                   "(swe.houses), and sidereal/tropical frames. Positions use the "
                   "pack's embedded Moshier/Swiss data, so everything runs 100% "
                   "offline and privacy-preserving."),
        "formula": ("KālaYantra wraps swe.calc_ut / rise–transit / swe.houses under "
                    "KalaChakra.get_planetary_longitudes(), get_transit(), "
                    "get_sun_moon_rise_set(), calculate_kundali() and friends."),
        "example": ("Retrograde status is read from the ephemeris speed vector: "
                    "retro = speed < 0; Rahu/Ketu are always taken as their mean node "
                    "(Ketu = Rahu + 180°)."),
        "source": "Astrodienst Swiss Ephemeris (GPL/AGPL data sets; pyswisseph).",
        "keywords": ["swiss ephemeris", "pyswisseph", "swe", "astronomy", "ephemeris", "offline"],
        "see_also": ["ayanamsa", "sidereal_longitude"],
    },

    # ------------------------------------------------------------------- graha
    {
        "id": "graha",
        "category": "graha",
        "title": {"en": "Graha — the nine planets",
                  "iast": "Graha / Navagraha",
                  "devanagari": "ग्रह / नवग्रह"},
        "summary": {"en": "Surya, Chandra, Mangala, Budha, Guru, Shukra, Shani, Rahu, Ketu.",
                    "iast": "Sūrya, Chandra, Maṅgala, Budha, Guru, Śukra, Śani, Rāhu, Ketu.",
                    "devanagari": "सूर्य, चन्द्र, मंगल, बुध, गुरु, शुक्र, शनि, राहु, केतु"},
        "detail": ("Jyotiṣa works with nine grahas: the seven classical planets plus the "
                   "two lunar nodes Rāhu and Ketu (modeled as the mean lunar nodes; Ketu "
                   "is always 180° from Rāhu). Grahas carry longitude, rāśi, nakṣatra "
                   "and pāda, plus dynamic status like dignity, combustion, retrogression "
                   "and house placement. The engine indexes them 0–8 and reports all "
                   "nine (with the Moon and lagna) in every kundali."),
        "formula": ("graha positions from swe.calc_ut in the sidereal frame; "
                    "Rahu/Ketu from the mean node with Ketu = (Rahu + 180°) mod 360."),
        "example": ("Index order in KālaYantra: 0 Surya, 1 Chandra, 2 Mangala, 3 Budha, "
                    "4 Guru, 5 Shukra, 6 Shani, 7 Rahu, 8 Ketu."),
        "source": "Classical Navagraha system; Sūrya Siddhānta; Bṛhat Jātaka.",
        "keywords": ["navagraha", "planets", "surya", "chandra", "mangala", "budha", "guru", "shukra", "shani", "rahu", "ketu"],
        "see_also": ["dignity", "combustion", "retrograde", "drishti", "graha_yuddha", "conjunction"],
    },
    {
        "id": "dignity",
        "category": "graha",
        "title": {"en": "Dignity — strength of placement",
                  "iast": "Balāvasthā / Dignity",
                  "devanagari": "बल / उच्च-नीच"},
        "summary": {"en": "Exalted, debilitated, own-sign, moolatrikona, friendly, enemy, neutral.",
                    "iast": "Uccha, Nīcha, Sva-kṣetra, Mūlatrikoṇa, Mitra, Śatru, Sama.",
                    "devanagari": "उच्च, नीच, स्वक्षेत्र, मूलत्रिकोण, मित्र, शत्रु, सम"},
        "detail": ("A graha's dignity rates how comfortably it sits in its rāśi: "
                   "Uccha (exalted), Nīcha (debilitated, the opposite sign), "
                   "Svakṣetra (own sign), Mūlatrikoṇa (its strongest own area), or "
                   "friend's/enemy's/neutral sign. The engine reads the exaltation and "
                   "ownership tables, then deterministically classifies every graha "
                   "(planets 0–6; the nodes carry no dignity). KalaBodha exposes the "
                   "dignity code on every graha fact sheet."),
        "formula": ("exaltations = {Surya: Mesha, Chandra: Vrishabha, Mangala: Makara, "
                    "Budha: Kanya, Guru: Karka, Shukra: Meena, Shani: Tula}\n"
                    "debiliation = exaltation + 6 signs; own/moolatrikona via ownership tables."),
        "example": ("Surya (index 0) is exalted in Mesha (0) and debilitated in Tula (6)."),
        "source": "Bṛhat Jātaka; Phaladīpikā.",
        "keywords": ["exalted", "debilitated", "own sign", "moolatrikona", "uccha", "neecha", "swakshetra", "dignity"],
        "see_also": ["graha", "combustion", "retrograde"],
    },
    {
        "id": "combustion",
        "category": "graha",
        "title": {"en": "Combustion (Asta)",
                  "iast": "Asta",
                  "devanagari": "अस्त (दाह)"},
        "summary": {"en": "A planet is 'burnt' when it lies within the Sun's influence orb.",
                    "iast": "A graha is asta (burnt) when too close to the Sun.",
                    "devanagari": "सूर्य के निकट ग्रह अस्त होता है"},
        "detail": ("A graha near the Sun is considered combust (asta) — weakened or "
                   "outshone — within a graha-specific orb. The engine uses the "
                   "classical elongation orbs per planet to flag combustion, which "
                   "shows up as a status marker in the kundali and KalaBodha facts. "
                   "Rāhu and Ketu are never combust; the Sun itself is the reference."),
        "formula": ("combust if elongation ≤ orb where orbs = {Chandra 12°, Mangala 17°, "
                    "Budha 14°, Guru 11°, Shukra 10°, Shani 15°}."),
        "example": ("Shukra 8° from the Sun is combust; Shukra 25° from the Sun is not."),
        "source": "Classical combustion orbs (Bṛhat Jātaka; Muhūrta literature).",
        "keywords": ["combust", "asta", "burnt", "burning", "near sun"],
        "see_also": ["graha", "dignity"],
    },
    {
        "id": "retrograde",
        "category": "graha",
        "title": {"en": "Retrograde (Vakri)",
                  "iast": "Vakrī",
                  "devanagari": "वक्री"},
        "summary": {"en": "Apparent backward motion of a graha relative to the stars.",
                    "iast": "Apparent backward motion of a graha relative to the stars.",
                    "devanagari": "ग्रह की प्रतीत प्रतिगामी गति"},
        "detail": ("From Earth a planet can appear to move backward (vakrī) against the "
                   "fixed zodiac near its station points. Jyotiṣa gives retrograde "
                   "grahas special strength and a behavior reversal. The engine detects "
                   "retrogression directly from the ephemeris speed vector; Rāhu and "
                   "Ketu (mean nodes) are always treated as moving."),
        "formula": ("retro = ephemeris speed < 0; reported on every graha and transit."),
        "example": ("Shani retrograde is a familiar slow station; the /kundali output "
                    "carries a 'retro': true flag on the graha."),
        "source": "Ephemeris apparent-motion computation; Bṛhat Jātaka treatment of vakra.",
        "keywords": ["retrograde", "vakri", "stations", "apparent motion", "backward"],
        "see_also": ["graha", "gochara"],
    },
    {
        "id": "drishti",
        "category": "graha",
        "title": {"en": "Drishti — planetary aspects",
                  "iast": "Dṛṣṭi",
                  "devanagari": "दृष्टि"},
        "summary": {"en": "The houses a graha 'looks at'; special aspects for Shani, Guru, Mangala.",
                    "iast": "The houses a graha 'looks at'; special aspects for Śani, Guru, Maṅgala.",
                    "devanagari": "ग्रहों की दृष्टियाँ"},
        "detail": ("Dṛṣṭi is how grahas interact at distance. All grahas aspect the 7th "
                   "house; Shani adds 3rd and 10th; Guru adds 5th and 9th; Mangala adds "
                   "4th and 8th; the nodes use the Jaimini system (5th/9th). KalaBodha "
                   "computes both Parashari and Jaimini drishti and the engine exposes "
                   "the house offsets each graha aspects."),
        "formula": ("full: 7th; Shani +3/+10; Guru +5/+9; Mangala +4/+8; "
                    "Jaimini for nodes: +5/+9."),
        "example": ("Guru in Mesha aspects the 5th (Simha), 7th (Tula) and 9th (Dhanu) "
                    "houses — exactly what KalaMedha reports for 'What does Guru aspect?'."),
        "source": "Parāśari system (Bṛhat Parāśara Horāśāstra); Jaimini (Rāhu/Ketu).",
        "keywords": ["aspect", "drishti", "drishti", "houses aspect", "jaimini", "parashari"],
        "see_also": ["graha", "conjunction"],
    },
    {
        "id": "graha_yuddha",
        "category": "graha",
        "title": {"en": "Graha Yuddha — planetary war",
                  "iast": "Graha Yuddha",
                  "devanagari": "ग्रह युद्ध"},
        "summary": {"en": "When two grahas occupy the same sign within 1°, the higher latitude wins.",
                    "iast": "Same-sign conjunction within 1°; the higher ecliptic latitude wins.",
                    "devanagari": "एक राशि में दो ग्रह — युद्ध"},
        "detail": ("When two grahas conjoin in the same rāśi within 1° of longitude a "
                   "'planetary war' is declared and the winner's result is delivered "
                   "while the loser's is cancelled (Bṛhat Jātaka rule). The engine "
                   "implements the classical rule with the refinements: a retrograde "
                   "combatant, a combust graha, and the Sun cannot be defeated; "
                   "otherwise the higher ecliptic latitude wins. KalaBodha emits a "
                   "dedicated yuddha record."),
        "formula": ("war if same sign and |lonA − lonB| < 1°; winner by latitude "
                    "(higher wins), with retro/combustion overrides."),
        "example": ("Two grahas at 12°20′ and 12°50′ of the same sign at 5° and 8° "
                    "latitude → the 8°-latitude graha wins."),
        "source": "Bṛhat Jātaka (Graha Yuddha); classical jyotiṣa doctrine.",
        "keywords": ["yuddha", "war", "planetary war", "battle", "1 degree orb"],
        "see_also": ["conjunction", "graha"],
    },
    {
        "id": "conjunction",
        "category": "graha",
        "title": {"en": "Conjunction (Yuti)",
                  "iast": "Yuti",
                  "devanagari": "युति"},
        "summary": {"en": "Two or more grahas in the same sign blend their results.",
                    "iast": "Two or more grahas in the same sign blend their results.",
                    "devanagari": "एक ही राशि में ग्रहों का मिलन"},
        "detail": ("Same-rāśi placement is read as a conjunction (yuti); the joined "
                   "grahas exchange results and, in the same nakṣatra, blend on the "
                   "pada level. KalaBodha groups same-sign grahas, flags those sharing "
                   "a nakṣatra, and the engine reports each graha's conjunction set in "
                   "the chart."),
        "formula": ("group by rashi index; flag same-nakshatra members."),
        "example": ("Surya and Guru both in Mithuna → a conjunction bundle;\n"
                    "KalaBodha lists them together and KalaMedha reasons over both."),
        "source": "Classical jyotiṣa conjunction doctrine.",
        "keywords": ["conjunction", "yuti", "together", "same sign", "join"],
        "see_also": ["graha", "drishti", "graha_yuddha"],
    },

    # ------------------------------------------------------------------- lagna
    {
        "id": "lagna",
        "category": "lagna",
        "title": {"en": "Lagna — the ascendant",
                  "iast": "Lagna",
                  "devanagari": "लग्न"},
        "summary": {"en": "The sign rising on the eastern horizon at the birth moment.",
                    "iast": "The sign rising on the eastern horizon at the birth moment.",
                    "devanagari": "जन्म के समय पूर्व क्षितिज पर उदित राशि"},
        "detail": ("The lagna is the rāśi rising over the eastern horizon at the moment "
                   "of interest, and the whole-sign house system then numbers houses "
                   "from it. Its lord (lagnesh) colours the entire chart. The engine "
                   "computes the house cusps with the Swiss Ephemeris, takes the "
                   "ascendant degree, applies the ayanāṁśa for the sidereal frame and "
                   "derives rashi, nakṣatra and pāda — plus lagnesh identification."),
        "formula": ("asc = ascendant degree from swe.houses(jd, lat, lon, Placidus)\n"
                    "sidereal asc = (asc − ayanāṁśa) mod 360; rashi = floor(asc/30)."),
        "example": ("For the 1990-06-15 10:30 IST Chennai sample the rising point falls "
                    "in Simha (Leo), making Surya the lagnesh."),
        "source": "Classical ascendant doctrine; Swiss Ephemeris house cusps.",
        "keywords": ["ascendant", "rising sign", "lagna", "lagnesh", "first house", "birth sign"],
        "see_also": ["graha", "sidereal_longitude", "varga"],
    },

    # ------------------------------------------------------------------- varga
    {
        "id": "varga",
        "category": "varga",
        "title": {"en": "Varga — divisional charts (D1–D60)",
                  "iast": "Varga",
                  "devanagari": "वर्ग"},
        "summary": {"en": "Sixteen harmonic charts exposing different realms of life.",
                    "iast": "Sixteen harmonic charts exposing different realms of life.",
                    "devanagari": "सोलह वर्ग — जीवन के विभिन्न क्षेत्र"},
        "detail": ("The sixteen vargas divide the zodiac into divisions: D1 "
                   "(rashi), D2–D12 and beyond each emphasise a specific life area "
                   "(D9 navāṁśa for the spouse, D10 karma, D3 siblings/Drekkana, etc.). "
                   "KālaYantra renders all 18 divisional charts D1–D60 using the "
                   "classical Parāśara allocations (as in Jagannatha Hora): D2 with "
                   "even-sign reversal, element-based D4/D8/D16/D20/D27/D45, special "
                   "D10/D12/D24/D40/D60 sign anchors, and unequal-arc D30 (trimsamsa); "
                   "only D7, D8, D11, D16, D20 and D27 coincide with a plain continuous "
                   "harmonic folding."),
        "formula": ("Per-division classical rule (see KalaVartika.varga_sign); a pure "
                    "harmonic floor( longitude × divisor / 30 ) is used only where it "
                    "matches the classical allocation (D7, D8, D11, D16, D20, D27)."),
        "example": ("A graha at 10° of a sign maps to the 1st Drekkana (0–10°) and the "
                    "4th Navāṁśa quarter (10°×9/30 → quarter 4)."),
        "source": "Bṛhat Parāśara Horāśāstra (Varga schemes).",
        "keywords": ["divisional", "varga", "harmonic", "d1", "d9", "d10", "d60", "sashtiamsa"],
        "see_also": ["navamsa", "drekkana", "lagna"],
    },
    {
        "id": "navamsa",
        "category": "varga",
        "title": {"en": "Navamsa (D9)",
                  "iast": "Navāṁśa",
                  "devanagari": "नवांश"},
        "summary": {"en": "The ninth-harmonic chart: spouse, dharma and inner strength.",
                    "iast": "The ninth-harmonic chart: spouse, dharma and inner strength.",
                    "devanagari": "नवांश — जीवनसाथी व धर्म"},
        "detail": ("Each 30° sign is split into nine 3°20′ parts; the navāṁśa sign is "
                   "counted from the sign of the same element as the natal sign "
                   "(the classical allocation: from Mesha for fire, etc.). The engine "
                   "computes D9 for every graha and lagna and flags Vargottama when a "
                   "graha occupies the same sign in D1 and D9."),
        "formula": ("navāṁśa sign = (sign_of_part + floor(deg_in_sign / 3.3333) − 1) "
                    "re-indexed within the element sequence."),
        "example": ("Kanya (6) graha at 7° → part 3 → third navāṁśa of Kanya element → "
                    "Vrishabha."),
        "source": "Bṛhat Parāśara Horāśāstra (Navāṁśa).",
        "keywords": ["navamsa", "d9", "ninth harmonic", "vargottama", "spouse chart"],
        "see_also": ["varga", "lagna"],
    },
    {
        "id": "drekkana",
        "category": "varga",
        "title": {"en": "Drekkana (D3)",
                  "iast": "Drekkāṇa",
                  "devanagari": "द्रेक्काण"},
        "summary": {"en": "The third-harmonic chart: courage, siblings and initiative.",
                    "iast": "The third-harmonic chart: courage, siblings and initiative.",
                    "devanagari": "द्रेक्काण — भाई-बहन व साहस"},
        "detail": ("Each sign divides into three 10° drekkāṇas, counted from the rashi "
                   "itself: the 1st maps to the natal sign, the 2nd to the 4th sign from "
                   "it, and the 3rd to the 8th sign from it. D3 is a classical varga for "
                   "courage and siblings. The engine reports D3 alongside D9 in every chart."),
        "formula": ("drekkāṇa sign = (natal sign + 0, +4, or +8 signs) for the "
                    "1st (0–10°), 2nd (10–20°), 3rd (20–30°) third."),
        "example": ("Karka (3) graha at 15° → second drekkāṇa → sign (3+4) = Simha (4)."),
        "source": "Bṛhat Parāśara Horāśāstra (Drekkāṇa).",
        "keywords": ["drekkana", "d3", "third harmonic", "siblings"],
        "see_also": ["varga"],
    },

    # ------------------------------------------------------------------- dasha
    {
        "id": "vimshottari",
        "category": "dasha",
        "title": {"en": "Vimshottari — the 120-year dasha cycle",
                  "iast": "Vimśottarī",
                  "devanagari": "विंशोत्तरी"},
        "summary": {"en": "The most-used period system: 120 years shared by nine grahas.",
                    "iast": "The most-used period system: 120 years shared by nine grahas.",
                    "devanagari": "120-वर्षीय महादशा चक्र"},
        "detail": ("Vimśottarī runs a fixed 120-year cycle of nine mahādashās whose "
                   "lord sequence starts from the nakṣatra occupied by the Moon at "
                   "birth: Ketu 7, Shukra 20, Surya 6, Chandra 10, Mangala 7, Rahu 18, "
                   "Guru 16, Shani 19, Budha 17 years. KālaYantra computes the "
                   "starting lord and the remaining balance from the fraction of the "
                   "Moon's nakṣatra already elapsed, then emits the full timeline with "
                   "antardashas and pratyantardashas."),
        "formula": ("order = [Ketu, Shukra, Surya, Chandra, Mangala, Rahu, Guru, Shani, Budha]\n"
                    "years = [7, 20, 6, 10, 7, 18, 16, 19, 17]\n"
                    "balance = (1 − nakṣatra_elapsed_fraction) × years[start_lord]"),
        "example": ("In the 1990-06-15 10:30 IST sample chart the Moon's nakṣatra makes "
                    "Rahu the first lord with 3.04 years remaining."),
        "source": "Bṛhat Parāśara Horāśāstra; Vimśottarī doctrine.",
        "keywords": ["vimshottari", "dasha", "mahadasha", "120 years", "balance", "period system"],
        "see_also": ["mahadasha", "nakshatra"],
    },
    {
        "id": "mahadasha",
        "category": "dasha",
        "title": {"en": "Mahadasha / Antardasha hierarchy",
                  "iast": "Mahādaśā / Antar-daśā",
                  "devanagari": "महादशा / अंतर्दशा"},
        "summary": {"en": "Sub-periods inside each mahadasha, proportionally subdivided.",
                    "iast": "Sub-periods inside each mahadasha, proportionally subdivided.",
                    "devanagari": "महादशा के भीतर उप-अवधियाँ"},
        "detail": ("Each mahādashā is further divided into antardashās whose lengths are "
                   "proportional to the mahādashā years: antardashā length = "
                   "(sub-lord years / 120) × parent years. Pratyantardashās subdivide "
                   "again the same way. The engine's dasha tree reports the current "
                   "Mahadasha / Antardasha / Pratyantardasha triad on every chart."),
        "formula": ("sub_years = parent_years × lord_years / 120  (recursed per level)."),
        "example": ("If Guru (16) mahādashā has Shukra (20) antardashā: duration = "
                    "16 × 20 / 120 = 2.67 years."),
        "source": "Vimśottarī doctrine (Bṛhat Parāśara Horāśāstra).",
        "keywords": ["antardasha", "pratyantardasha", "sub period", "dasha hierarchy", "current dasha"],
        "see_also": ["vimshottari"],
    },

    # ----------------------------------------------------------------- gochara
    {
        "id": "gochara",
        "category": "gochara",
        "title": {"en": "Gochara — current transits",
                  "iast": "Gocāra",
                  "devanagari": "गोचर"},
        "summary": {"en": "Where the grahas are now, against the natal chart.",
                    "iast": "Where the grahas are now, against the natal chart.",
                    "devanagari": "वर्तमान में ग्रहों की स्थिति"},
        "detail": ("Gocāra compares the current (transit) zodiac against a natal chart: "
                   "each transit graha's rāśi, bhāva from the natal lagna, dignity and "
                   "retrogression, plus the houses it aspects from its transit sign. "
                   "KālaYantra's /gochara endpoint and Gochara UI also track tight "
                   "1° transits crossing natal planets and the dates slow grahas enter "
                   "their next sign."),
        "formula": ("transit position from swe.calc_ut at the transit moment;\n"
                    "house = (transit_rashi − natal_lagna_rashi) mod 12."),
        "example": ("Shani travelling Tula is Ashtama Śani for a Moon in Meena "
                    "(8 houses from the natal Moon)."),
        "source": "Common transit (gocāra) practice; classical jyotiṣa.",
        "keywords": ["transit", "gochara", "current planets", "transiting", "daily movement"],
        "see_also": ["sade_sati", "guru_gochara"],
    },
    {
        "id": "sade_sati",
        "category": "gochara",
        "title": {"en": "Sade Sati — the seven-and-a-half years of Shani",
                  "iast": "Sāḍhe Sātī",
                  "devanagari": "साढ़े साती"},
        "summary": {"en": "Shani transiting the 12th, 1st and 2nd from the natal Moon ≈ 7.5 years.",
                    "iast": "Śani transiting the 12th, 1st and 2nd from the natal Moon.",
                    "devanagari": "जन्म चन्द्र से १२वें, १ वें व २वें घर में शनि"},
        "detail": ("When Śani transits the house before, on, and after the natal Moon in "
                   "sequence, the classic Sāḍhe Sātī window (~seven and a half years) "
                   "is in force. KālaYantra detects all three phases and names each, "
                   "so the Gochara view can tell exactly which part of the period is "
                   "running and when it ends."),
        "formula": ("sade sati active if transit-chandra distance ∈ {11, 0, 1} houses;\n"
                    "phases = [12th, 1st, 2nd] with per-phase boundaries from sign entry."),
        "example": ("Moon in Kumbha → Shani in Makara / Kumbha / Meena marks the three\n"
                    "consecutive Sāḍhe Sātī phases."),
        "source": "Classical Śani gochara tradition.",
        "keywords": ["sade sati", "sade saati", "shani", "seven and half", "saturn transit", "phases"],
        "see_also": ["gochara", "guru_gochara"],
    },
    {
        "id": "guru_gochara",
        "category": "gochara",
        "title": {"en": "Guru Gochara — Jupiter's transit",
                  "iast": "Guru Gocāra",
                  "devanagari": "गुरु गोचर"},
        "summary": {"en": "Guru's transit relative to its natal place and the lagna.",
                    "iast": "Guru's transit relative to its natal place and the lagna.",
                    "devanagari": "जन्म गुरु व लग्न से गुरु की स्थिति"},
        "detail": ("Guru Gocāra measures Jupiter's current sign against both the natal "
                   "Guru (its own return) and the natal lagna — the Gocara ladder of "
                   "good (5th/7th/9th), neutral and hard houses. KālaYantra's special "
                   "transit yogas include Guru's return to its natal sign and the "
                   "9th house from lagna (a highly auspicious station)."),
        "formula": ("guru_transit_house_from_lagna = (guru_now − lagna) mod 12; "
                    "guru_return = (guru_now − natal_guru) mod 12."),
        "example": ("Natal Guru in Simha → Guru transiting Dhanu is the 5th from it "
                    "(friendly) and aspects the natal chart strongly."),
        "source": "Classical Guru gochara practice.",
        "keywords": ["guru gochara", "jupiter transit", "guru return", "guru transit from lagna"],
        "see_also": ["gochara", "sade_sati"],
    },

    # ---------------------------------------------------------- compatibility
    {
        "id": "ashtakoota",
        "category": "compatibility",
        "title": {"en": "Ashtakoota — Guna Milan (36 points)",
                  "iast": "Aṣṭakūṭa",
                  "devanagari": "अष्टकूट"},
        "summary": {"en": "The eight-fold compatibility score out of 36 used in marriage matching.",
                    "iast": "The eight-fold compatibility score out of 36 used in marriage matching.",
                    "devanagari": "36 गुणों में विवाह-मिलान"},
        "detail": ("Guna Milan compares a bride and groom across eight kootas, each "
                   "carrying points that sum to 36: Varna (1), Vashya (2), Tara (3), "
                   "Yoni (4), Graha Maitri (5), Gana (6), Bhakoot (7) and Nadi (8). "
                   "KālaYantra accepts full birth data or the Moon's rashi/nakshatra "
                   "directly, computes every koota with the classical rules, totals "
                   "the score with a verdict, and flags the Nadi and Bhakoot doshas "
                   "plus their cancellation conditions."),
        "formula": ("each koota applies its matching table (ex: Bhakoot from "
                    "chandra-rashis, Nadi from nakshatra group, Yoni from species "
                    "compatibility); total = Σ points, verdict by the 36-point bands."),
        "example": ("A 32/36 score entering the 'good' band, with a Nadi dosha that "
                    "is cancelled by identical rashi — both are reported explicitly."),
        "source": "Classical Guna Milan tradition (Pañchānga / Vivāha muhūrta texts).",
        "keywords": ["ashtakoota", "guna milan", "koota", "compatibility", "match", "36 points", "nadi", "bhakoot", "yoni"],
        "see_also": ["nakshatra", "graha"],
    },

    # ----------------------------------------------------------------- muhurta
    {
        "id": "hora",
        "category": "muhurta",
        "title": {"en": "Hora — hourly lords",
                  "iast": "Horā",
                  "devanagari": "होरा"},
        "summary": {"en": "The 24 Chaldean hours ruled in turn by the seven grahas.",
                    "iast": "The 24 Chaldean hours ruled in turn by the seven grahas.",
                    "devanagari": "24 घंटों पर ग्रह स्वामित्व"},
        "detail": ("The day is divided into 12 daytime (sunrise to sunset) and 12 "
                   "nighttime horas, named in the Chaldean order. The first hour of "
                   "Sunday belongs to the Sun, Monday to the Moon, and so on; each "
                   "subsequent hour steps backward through the planetary week order. "
                   "The first hora's lord also names the weekday, which is how vāra "
                   "gets its graha. KālaYantra returns all 24 horas with their lords "
                   "and an auspiciousness grade."),
        "formula": ("hora length = daylength/12 (day) or nightlength/12 (night); "
                    "lord sequence = reverse planetary week starting from the weekday lord."),
        "example": ("Sunday sunrise hour is Surya, the next is Shukra, then Budha …"),
        "source": "Chaldean/Jyotiṣa hora doctrine.",
        "keywords": ["hora", "hour lord", "24 horas", "chaldean", "planetary hour"],
        "see_also": ["vaara", "muhurta"],
    },
    {
        "id": "muhurta",
        "category": "muhurta",
        "title": {"en": "Muhurta — the 30 auspicious timings",
                  "iast": "Muhūrta",
                  "devanagari": "मुहूर्त"},
        "summary": {"en": "Fifteen daytime and fifteen nighttime muhurtas of the day.",
                    "iast": "Fifteen daytime and fifteen nighttime muhūrtas of the day.",
                    "devanagari": "दिन-रात के 30 मुहूर्त"},
        "detail": ("Each half-day is split into fifteen muhūrtas of about 48 minutes. "
                   "Each carries a name (Rudra, Ahi, Mitra, Pitri, Vasu, …) and an "
                   "auspiciousness class. KālaYantra flags each as Abhijit / "
                   "Auspicious / Neutral / Inauspicious by overlap with Rahu Kāla, "
                   "Yamaghanta, Gulika and the auspicious Choghadiya windows."),
        "formula": ("muhurta_len = day_duration / 15; grade by overlap with the "
                    "inauspicious/auspicious spans."),
        "example": ("The midday Abhijit muhūrta (~3.5 ghaṭīs around noon) always grades "
                    "Auspicious and is recommended of all."),
        "source": "Muhūrta tradition (Bṛhat Saṁhitā; Muhūrta Chintāmaṇi).",
        "keywords": ["muhurta", "muhurt", "auspicious time", "30 muhurtas", "abhijit", "rudra"],
        "see_also": ["hora", "rahu_kala", "choghadiya", "abhijit"],
    },
    {
        "id": "rahu_kala",
        "category": "muhurta",
        "title": {"en": "Rahu Kala, Yamaghanta & Gulika",
                  "iast": "Rāhu Kāla / Yamaghānṭa / Gulikā",
                  "devanagari": "राहु काल / यमघंट / गुलिक"},
        "summary": {"en": "The daily inauspicious windows ruled by the shadow grahas.",
                    "iast": "The daily inauspicious windows ruled by the shadow grahas.",
                    "devanagari": "प्रतिदिन के अशुभ काल"},
        "detail": ("Each weekday holds fixed inauspicious spans: Rāhu Kāla (the "
                   "eighth part of the day belonging to Rāhu), Yamaghānṭa and Gulikā "
                   "(segments of the day ruled by the shadow timings). Starting "
                   "new ventures in these windows is avoided. KālaYantra computes all "
                   "three from daylight length for the date and location and marks "
                   "them in the day view."),
        "formula": ("window = eighth of the day (sunrise→sunset), shifted per weekday "
                    "to the assigned portion; e.g. Sunday Rāhu Kāla is the 8th part."),
        "example": ("For Monday at Ujjain the day view shows Rāhu Kāla, Yamaghanta and "
                    "Gulika as distinct colored spans."),
        "source": "Classical Kāla custom (Muhūrta literature).",
        "keywords": ["rahu kala", "rahu kal", "yamaghanta", "gulika", "inauspicious", "amrita kala"],
        "see_also": ["muhurta", "choghadiya", "abhijit"],
    },
    {
        "id": "choghadiya",
        "category": "muhurta",
        "title": {"en": "Choghadiya — the eight day-segments",
                  "iast": "Choghadiyā",
                  "devanagari": "चौघड़िया"},
        "summary": {"en": "Day divided into 8 segments with alternating auspiciousness.",
                    "iast": "Day divided into 8 segments with alternating auspiciousness.",
                    "devanagari": "दिन के 8 वर्ग"},
        "detail": ("Choghadiya splits the day (and separately the night) into eight "
                   "sections each ruled in turn by a graha, giving a repeating "
                   "auspicious/normal/inauspicious pattern widely used for travel and "
                   "Indian business timing. KālaYantra renders both daytime and "
                   "nighttime choghadiyā with color-coded nature."),
        "formula": ("segment = day/8; lords cycle through the planetary order; "
                    "nature per lord table."),
        "example": ("The Udveg segment is inauspicious for travel; Shubha is auspicious "
                    "— both color-coded in the day panel."),
        "source": "Popular Choghadiya panchanga usage (North/West India).",
        "keywords": ["choghadiya", "chogadia", "day segments", "auspicious", "travel time", "udveg", "shubh"],
        "see_also": ["muhurta", "rahu_kala"],
    },
    {
        "id": "abhijit",
        "category": "muhurta",
        "title": {"en": "Abhijit Muhurta",
                  "iast": "Abhijit Muhūrta",
                  "devanagari": "अभिजित मुहूर्त"},
        "summary": {"en": "The nigh-noon muhurta that is almost always auspicious.",
                    "iast": "The nigh-noon muhūrta that is almost always auspicious.",
                    "devanagari": "मध्याह्न का शुभ मुहूर्त"},
        "detail": ("Abhijit is the eighth muhūrta of the day, the ~48 minutes spanning "
                   "local midday, and is blessed — so it is exempt from most "
                   "inauspicious checks. KālaYantra reports its window on every day "
                   "record and grades it 'Auspicious' in the muhurta list."),
        "formula": ("abhijit = the middle fifteenth of daylight (daylength/15 centered "
                    "on solar noon)."),
        "example": ("Sunrise 06:12, sunset 18:34 → Abhijit ≈ 11:58–12:48."),
        "source": "Muhūrta doctrine (Muhūrta Chintāmaṇi).",
        "keywords": ["abhijit", "noon", "auspicious", "muhurta", "midday"],
        "see_also": ["muhurta"],
    },

    # ---------------------------------------------------------------- festival
    {
        "id": "ekadashi",
        "category": "festival",
        "title": {"en": "Ekadashi — Smarta vs Vaishnava rules",
                  "iast": "Ekādaśī",
                  "devanagari": "एकादशी"},
        "summary": {"en": "The 11th-tithi fast, with two observance traditions.",
                    "iast": "The 11th-tithi fast, with two observance traditions.",
                    "devanagari": "ग्यारहवीं तिथि का व्रत"},
        "detail": ("Ekādaśī is a fast kept on the 11th tithi, but the two traditions "
                   "differ on edge cases. Smārta follows the udaya-vyāpinī rule: the "
                   "day on which Ekādaśī is running at sunrise (and for a two-sunrise "
                   "Vṛddha Ekādaśī, the second day). Vaiṣṇava requires Ekādaśī to "
                   "begin before Arunodaya (96 min before sunrise); if it starts "
                   "later the day is viddha and the fast moves to Dvādaśī "
                   "(Mahādvādaśī / Atirikta). KālaYantra implements both and records "
                   "which rule matched on every festival."),
        "formula": ("smartā: fast on the tithi-present-at-sunrise day; if present two "
                    "days, the 2nd.\n"
                    "vaiṣṇava: if Ekādaśī begins after Arunodaya → fast on Dvādaśī."),
        "example": ("A viddha Ekādaśī on Tuesday pushes the Vaiṣṇava fast to Wednesday "
                    "Dvādaśī; the Smārta list keeps Tuesday."),
        "source": "Ekādaśī observance traditions (Smārta / Vaiṣṇava paddhati).",
        "keywords": ["ekadashi", "dvadashi", "fast", "vaishnava", "smarta", "viddha", "arunodaya", "twadashi"],
        "see_also": ["tithi", "festival_engine", "kshaya_tithi"],
    },
    {
        "id": "kshaya_tithi",
        "category": "festival",
        "title": {"en": "Kshaya Tithi — the lost lunar day",
                  "iast": "Kṣaya Tithi",
                  "devanagari": "क्षय तिथि"},
        "summary": {"en": "A tithi that is skipped because two successive days pass.",
                    "iast": "A tithi skipped when the Moon crosses it between sunrises.",
                    "devanagari": "छूटी हुई तिथि"},
        "detail": ("When the Moon gains more than 24° between two consecutive sunrise "
                   "readings, a whole tithi is skipped — the 'lost' (kṣaya) tithi. "
                   "Observances that fall on it are merged into the surrounding "
                   "observance logic. KālaYantra tracks kṣaya days, merges custom "
                   "observances and schedules Vaishnava Ekādaśī to Dvādaśī when the "
                   "lost day interferes."),
        "formula": ("kṣaya if tithi(elapsed) crosses an integer boundary twice in one "
                    "day; flagged as is_tithi_N_kshaya on the day record."),
        "example": ("An amāvasyā that vanishes is read as an extra-thin Krishna side; "
                    "the engine marks the kṣaya and adjusts festival merging."),
        "source": "Pañchāṅga kṣaya doctrine.",
        "keywords": ["kshaya", "kshaya tithi", "skipped tithi", "lost day", "vriddha"],
        "see_also": ["tithi", "festival_engine", "ekadashi"],
    },
    {
        "id": "sankranti",
        "category": "festival",
        "title": {"en": "Sankranti — the Sun's sign entry",
                  "iast": "Saṅkrānti",
                  "devanagari": "संक्रांति"},
        "summary": {"en": "The moment the Sun steps into the next rashi; basis of solar months.",
                    "iast": "The moment the Sun steps into the next rāśi; basis of solar months.",
                    "devanagari": "सूर्य का राशि-प्रवेश"},
        "detail": ("A saṅkrānti is the exact instant the Sun's sidereal longitude "
                   "crosses into a new 30° sign. These moments name the solar months "
                   "(Saura), trigger festivals such as Makara Saṅkrānti, and bracket "
                   "the lunar months' names. In Saura calendar mode KālaYantra "
                   "switches to solar months computed from consecutive saṅkrāntis and "
                   "native Sankranti events are shown on the calendar."),
        "formula": ("find the jd where sun_lon mod 30 crosses 0 via transition search; "
                    "solar day-of-month = floor((jd − sankranti_jd) within its month)."),
        "example": ("Makara Saṅkrānti is the moment the Sun enters Makara — the "
                    "engine reports that event with its exact local time."),
        "source": "Sūrya Siddhānta; Saura calendar doctrine.",
        "keywords": ["sankranti", "sankrant", "transit", "sun sign change", "solar month", "makara sankranti"],
        "see_also": ["masa", "saura_calendar", "ayana"],
    },
    {
        "id": "festival_engine",
        "category": "festival",
        "title": {"en": "Festival engine (KalaUtsavachakra)",
                  "iast": "Utsavachakra",
                  "devanagari": "उत्सव चक्र"},
        "summary": {"en": "The Dharmaśāstra rule engine that decides which festival a day is.",
                    "iast": "The Dharmaśāstra rule engine that decides which festival a day is.",
                    "devanagari": "त्योहारों का नियम-इंजन"},
        "detail": ("KalaUtsavachakra evaluates a library of festival definitions "
                   "against the daily pañchāṅga: fixed tithis with optional masa and "
                   "paksha, complex dates (e.g. Vaishnava Ekādaśī with the pushing "
                   "rule), nakshatra-based observations and saṅkrānti events. Each "
                   "match records its rule, a description, a color and a priority, "
                   "and days can be filtered by the Smārta or Vaiṣṇava rule set."),
        "formula": ("for each festival spec: match come/masa/paksha/tithi/nakshatra/"
                    "sankranti predicates against the day; keep the highest-priority match."),
        "example": ("The calendar dot hierarchy — Ekadashi blue, Sankranti orange, "
                    "Sankashti pink, festivals green — comes straight from the "
                    "engine's priority field."),
        "source": "Internal KalaUtsavachakra engine; Dharmaśāstra festival rules.",
        "keywords": ["festival", "utsav", "vrat", "festival rules", "dharmashastra", "observance"],
        "see_also": ["ekadashi", "sankranti", "kshaya_tithi"],
    },
    {
        "id": "saura_calendar",
        "category": "festival",
        "title": {"en": "Saura (solar) calendar",
                  "iast": "Saura māsa",
                  "devanagari": "सौर मास"},
        "summary": {"en": "Solar months from Mesha to Meena bounded by sankrantis.",
                    "iast": "Solar months from Mesha to Meena bounded by saṅkrāntis.",
                    "devanagari": "सूर्य-मास — मेष से मीन"},
        "detail": ("The Saura system counts the year by the Sun alone: each solar month "
                   "runs from one saṅkrānti to the next, named Mesha … Meena, with the "
                   "Shaka era incrementing at Mesha Saṅkrānti. In this mode pakshas are "
                   "hidden, day transitions are disabled and days count sequentially "
                   "('Solar Day 1…30/31/32') from the exact saṅkrānti moment. "
                   "KālaYantra switches the whole calendar to Saura via "
                   "calendar_system=saura."),
        "formula": ("solar month = (sun_rashi + 1) and Shaka-era step at Mesha "
                    "saṅkrānti; day = floor(jd − sankranti_jd) + 1."),
        "example": ("After Mesha Saṅkrānti, 'Solar Day 1 of Mesha' begins — with no "
                    "tithi/paksha displayed."),
        "source": "Sūrya Siddhānta; Saura tradition (Tamizh/Kerala style).",
        "keywords": ["saura", "solar calendar", "solar month", "mesha", "solar day", "sankranti based"],
        "see_also": ["sankranti", "masa"],
    },

    # ------------------------------------------------------------------ method
    {
        "id": "traditional_mode",
        "category": "method",
        "title": {"en": "Traditional vs Astronomical pañchāṅga mode",
                  "iast": "Udaya-ādi vs current",
                  "devanagari": "परम्परागत / खगोलीय मोड"},
        "summary": {"en": "Two ways to anchor which pañchāṅga element a day shows.",
                    "iast": "Two ways to anchor which pañchāṅga element a day shows.",
                    "devanagari": "दिन के पंचांग-अंग चुनने के दो तरीके"},
        "detail": ("Traditional mode reads the five elements at sunrise (udaya-ādi) and "
                   "keeps that element for the civil day; if it survives past the next "
                   "sunrise only the surviving element is shown, otherwise sunrise and "
                   "afternoon elements appear side by side. Astronomical (live) mode "
                   "tracks the current element in real time with its transition. "
                   "KālaYantra's tithi_mode=traditional|current drives both the engine "
                   "output and the panel display."),
        "formula": ("read at sunrise_jd; display logic: if element survives next "
                    "sunrise → single; else sunrise + next pair."),
        "example": ("In traditional mode a tithi changing at 10:00 still labels the "
                    "whole day by its sunrise tithi."),
        "source": "Pañchāṅga udaya-ādi convention.",
        "keywords": ["mode", "traditional", "astronomical", "udaya", "sunrise anchored", "live", "current"],
        "see_also": ["panchanga", "sunrise_sunset"],
    },

    # --------------------------------------------------------------- reasoning
    {
        "id": "evidence_graph",
        "category": "reasoning",
        "title": {"en": "KalaBodha evidence graph",
                  "iast": "Pramāṇa",
                  "devanagari": "प्रमाण"},
        "summary": {"en": "Every conclusion carries its factors, rule and source.",
                    "iast": "Every conclusion carries its factors, rule and source.",
                    "devanagari": "हर निष्कर्ष के साथ कारण व स्रोत"},
        "detail": ("KalaBodha builds a machine-readable reasoning graph over the "
                   "kundali: graha facts (dignity, status markers, conjunctions, "
                   "yuddhas), drishti maps, a curated yoga engine and the evidence set "
                   "connecting every conclusion to the factors that produced it, each "
                   "tagged with its rule and classical source. This makes each "
                   "chart assertion inspectable — why something is stated, and "
                   "according to which text."),
        "formula": ("evidence = {statement, factors, rule, source, weight} produced by "
                    "the analyzer given the kundali."),
        "example": ("'Rāhu forms Vipareeta Raja Yoga' arrives with the participating "
                    "grahas, the kendra/trikona condition and its Phaladīpikā quote."),
        "source": "Internal KalaBodha engine; Bṛhat Jātaka / Phaladīpikā sourcing.",
        "keywords": ["evidence", "reasoning", "kala bodha", "fact sheet", "source", "rule", "graph"],
        "see_also": ["dignity", "drishti", "graha_yuddha"],
    },
    {
        "id": "strengths_weaknesses",
        "category": "reasoning",
        "title": {"en": "KalaMedha strengths & answers",
                  "iast": "Bala-krama",
                  "devanagari": "बल-क्रम"},
        "summary": {"en": "Ranked graha strength with reasons, plus natural-language Q&A.",
                    "iast": "Ranked graha strength with reasons, plus natural-language Q&A.",
                    "devanagari": "ग्रह-बल क्रम व प्रश्नोत्तर"},
        "detail": ("KalaMedha turns the evidence graph into human language: a ranked, "
                   "explainable strength score for all nine grahas (based on house, "
                   "relationship to the Moon, yoga membership, dignity and status), "
                   "the strongest/weakest synthesis, and an intent-based question "
                   "answler for 'Where is Shani?', 'Is Guru strong?', 'What does Guru "
                   "aspect?', 'What is the current dasha?' and similar. An optional "
                   "local LLM hook can enrich the reading and falls back to the rule "
                   "engine automatically."),
        "formula": ("score = Σ weights over house placement, Chandra relation, "
                    "yoga membership, dignity, status; answers route question "
                    "intents onto bodha query results."),
        "example": ("'Why is Shani weak?' returns Shani's score and the exact reasons "
                    "(e.g. 8th from lagna) rather than a canned sentence."),
        "source": "Internal KalaMedha engine (rule-based + optional LLM).",
        "keywords": ["kala medha", "strength", "weakness", "question answer", "narrative", "reading", "ai", "score"],
        "see_also": ["evidence_graph", "dignity", "mahadasha"],
    },
    {
        "id": "birth_time_sensitivity",
        "category": "reasoning",
        "title": {"en": "Birth-time sensitivity",
                  "iast": "Janma-kāla sūkṣmatā",
                  "devanagari": "जन्म-समय सूक्ष्मता"},
        "summary": {"en": "How much the chart changes if the birth time is uncertain.",
                    "iast": "How much the chart changes if the birth time is uncertain.",
                    "devanagari": "जन्म-समय में त्रुटि से कुंडली में अंतर"},
        "detail": ("A birth moment recorded to the minute can be off by several "
                   "minutes, and the lagna moves about 1° every four minutes. "
                   "KālaYantra's sensitivity report re-computes the chart over a "
                   "±span window and reports which facts are stable — the lagna sign, "
                   "the running dasha lord, each graha's rashi, house and vargottama "
                   "status — as stable_factors / unstable_factors so the reading's "
                   "robustness is explicit."),
        "formula": ("for t in [−span … +span]: recompute per-graha rashi/house/status; "
                    "mark stable if unchanged across the whole window."),
        "example": ("With a ±5-minute window, Chandra is stable in Kumbha but the "
                    "lagna sign flips at the boundary — both reported."),
        "source": "Internal KalaBodha sensitivity analysis.",
        "keywords": ["sensitivity", "birth time", "uncertainty", "stable", "span", "lagna stability"],
        "see_also": ["lagna", "evidence_graph"],
    },
]


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def concept_count() -> int:
    """Number of knowledge entries in the base."""
    return len(_CONCEPTS)


def categories(lang: str = "en") -> list:
    """Category slugs with localized titles."""
    return [{"id": c, "title": _L(CATEGORY_TITLES[c], lang)} for c in CATEGORIES]


def concept_catalog(lang: str = "en", category=None) -> list:
    """Every concept as {id, category, title, summary} (optionally one category)."""
    out = []
    for c in _CONCEPTS:
        if category and c["category"] != category:
            continue
        out.append({
            "id": c["id"],
            "category": c["category"],
            "title": _L(c["title"], lang),
            "summary": _L(c["summary"], lang),
        })
    return out


def _match(ref: str, entry: dict) -> bool:
    ref = ref.strip().lower()
    if entry["id"].lower() == ref:
        return True
    for title in entry["title"].values():
        if title.strip().lower() == ref:
            return True
    return False


def get_concept(ref: str, lang: str = "en"):
    """Return the full concept entry for *ref* (id or any-language title), or None.

    The returned dict is the stored entry with ``title`` and ``summary`` localized
    to *lang* so it is JSON-friendly for the API and the CLI."""
    for c in _CONCEPTS:
        if _match(ref, c):
            out = dict(c)
            out["title"] = _L(c["title"], lang)
            out["summary"] = _L(c["summary"], lang)
            out["category_title"] = _L(CATEGORY_TITLES[c["category"]], lang)
            return out
    return None


def _search_rank(query: str, entry: dict) -> int:
    """Rank an entry for a query: exact id > keyword/title prefix > substring."""
    q = query.strip().lower()
    score = 0
    for title in entry["title"].values():
        t = title.strip().lower()
        if t == q:
            score += 100
        elif t.startswith(q) or entry["id"] == q:
            score += 60
        elif q in t:
            score += 40
    for kw in entry.get("keywords", []):
        if q in kw.lower():
            score += 30
            break
    blob = " ".join([entry["id"], _L(entry["summary"], "en"),
                     " ".join(entry.get("keywords", []))]).lower()
    if q in blob:
        score += 10
    return score


def search_concepts(query: str, lang: str = "en", limit: int = 10) -> list:
    """Ranked search across titles, summaries, ids and keywords."""
    if not query or not query.strip():
        return concept_catalog(lang)
    scored = []
    for c in _CONCEPTS:
        score = _search_rank(query, c)
        if score:
            scored.append((score, c))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    out = []
    for _, c in scored[:limit]:
        out.append({
            "id": c["id"],
            "category": c["category"],
            "title": _L(c["title"], lang),
            "summary": _L(c["summary"], lang),
            "_score": _search_rank(query, c),
        })
    # drop internal score for clean API output
    for item in out:
        item.pop("_score", None)
    return out


def validate() -> list:
    """Integrity report: returns a list of problem strings (empty = healthy)."""
    problems = []
    ids = [c["id"] for c in _CONCEPTS]
    if len(ids) != len(set(ids)):
        problems.append("duplicate concept id(s)")
    valid_categories = set(CATEGORIES)
    required = {"id", "category", "title", "summary", "detail", "formula",
                "example", "source", "keywords", "see_also"}
    for c in _CONCEPTS:
        missing = required - set(c.keys())
        if missing:
            problems.append(f"{c.get('id', '?')}: missing {sorted(missing)}")
        if c.get("category") not in valid_categories:
            problems.append(f"{c.get('id', '?')}: bad category {c.get('category')!r}")
        for lang in ("en", "iast", "devanagari"):
            if not _L(c.get("title", {}), lang):
                problems.append(f"{c.get('id', '?')}: empty {lang} title")
            if not _L(c.get("summary", {}), lang):
                problems.append(f"{c.get('id', '?')}: empty {lang} summary")
        if not (c.get("detail") and c.get("formula") and c.get("example")):
            problems.append(f"{c.get('id', '?')}: empty detail/formula/example")
        for ref in c.get("see_also", []):
            if ref not in ids:
                problems.append(f"{c.get('id', '?')}: see_also '{ref}' missing")
    return problems
