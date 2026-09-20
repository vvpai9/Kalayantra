# -*- coding: utf-8 -*-
"""
KalaChakra — the core astronomical calculation engine.

Depends on pyswisseph (Swiss Ephemeris) for planetary positions and rise/set
computations, and on KalaVartika + KalaKosha for pure-math helpers and
static data respectively.

Public API surface (called by KalaSetu, CLI, and tests):
    get_ayanamsa_modes / set_ayanamsa / get_ayanamsa_mode
    get_ayanamsa_value
    get_planetary_longitudes / get_transit / get_sidereal_longitudes
    get_rashi / get_nakshatra / get_nakshatra_pada / get_rashi_longitude
    varga_sign / _drekkana_sign / _navamsa_sign
    get_sun_moon_rise_set
    find_transition / find_previous_conjunction / find_next_conjunction
    get_lunar_month_details / get_chaitra_pratipada_jd / get_kartika_pratipada_jd
    get_prev_sankranti_jd / get_solar_day_of_month
    get_karana_name_from_idx
    calculate_panchanga / calculate_detailed_panchanga
    calculate_dina_horas / calculate_muhurtas
    calculate_vimshottari_tree
    calculate_kundali
    calculate_ashtakoota
    generate_analysis
    calculate_gochara / calculate_gocara (transits)
"""

from __future__ import annotations

import math
import datetime as _dt

import swisseph as swe

import KalaKosha
import KalaVartika

_YEAR_DAYS = 365.2425

# ---------------------------------------------------------------------------
# Ayanamsa table
# ---------------------------------------------------------------------------
_AYANAMSA_TABLE = {
    "lahiri":       swe.SIDM_LAHIRI,
    "raman":        swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "true_citra":   swe.SIDM_TRUE_CITRA,
    "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
    "deluce":       swe.SIDM_DELUCE,
}
_AYANAMSA_MODE = "lahiri"

# Swiss Ephemeris planet mapping (0–7); Ketu is Rahu+180°; 9–11 are the
# modern outer planets.  Maandi (12) is a time-derived upagraha (not in the
# ephemeris) and is computed separately in calculate_kundali.
_PLANET_SWE_IDS = {
    0: swe.SUN, 1: swe.MOON, 2: swe.MARS,
    3: swe.MERCURY, 4: swe.JUPITER, 5: swe.VENUS,
    6: swe.SATURN, 7: swe.MEAN_NODE,
    9: swe.URANUS, 10: swe.NEPTUNE, 11: swe.PLUTO,
}
_MAANDI_IDX = 12

# ---------------------------------------------------------------------------
# Ayanamsa management
# ---------------------------------------------------------------------------

def get_ayanamsa_modes() -> list[str]:
    return sorted(_AYANAMSA_TABLE.keys())


def set_ayanamsa(mode: str) -> None:
    global _AYANAMSA_MODE
    if mode not in _AYANAMSA_TABLE:
        raise ValueError(f"Unknown ayanamsa mode: {mode!r}")
    _AYANAMSA_MODE = mode


def get_ayanamsa_mode() -> str:
    return _AYANAMSA_MODE


def _get_sid_mode() -> int:
    return _AYANAMSA_TABLE.get(_AYANAMSA_MODE, swe.SIDM_LAHIRI)


def get_ayanamsa_value(jd_ut: float) -> float:
    """Sidereal ayanamsa in degrees for a Julian Day (UTC).

    Raises if Swiss Ephemeris fails — silently returning a constant would
    corrupt every sidereal position downstream.
    """
    swe.set_sid_mode(_get_sid_mode())
    return swe.get_ayanamsa_ut(jd_ut)


# ---------------------------------------------------------------------------
# Planet positions
# ---------------------------------------------------------------------------

def get_planetary_longitudes(jd_ut: float, tropical: bool = False) -> dict[int, float]:
    """Sidereal (or tropical) longitude of each graha (0–8)."""
    result = {}
    flags = swe.FLG_SWIEPH
    if not tropical:
        swe.set_sid_mode(_get_sid_mode())
        flags |= swe.FLG_SIDEREAL
    for idx in range(8):
        res = swe.calc_ut(jd_ut, _PLANET_SWE_IDS[idx], flags)
        result[idx] = res[0][0] % 360.0
    # Ketu = Rahu + 180°
    result[8] = (result[7] + 180.0) % 360.0
    return result


def get_transit(planet_idx: int, jd_ut: float) -> tuple[float, bool]:
    """(sidereal_lon, retro_flag) for a single planet."""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    swe.set_sid_mode(_get_sid_mode())
    res = swe.calc_ut(jd_ut, _PLANET_SWE_IDS[planet_idx], flags)
    lon = res[0][0] % 360.0
    retro = res[0][3] < 0
    if planet_idx == 7:
        retro = False
    return lon, retro


def get_sidereal_longitudes(jd_ut: float) -> tuple[float, float]:
    """(Sun_longitude, Moon_longitude) sidereal at jd_ut."""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    swe.set_sid_mode(_get_sid_mode())
    sun = swe.calc_ut(jd_ut, swe.SUN, flags)
    moon = swe.calc_ut(jd_ut, swe.MOON, flags)
    return (sun[0][0] % 360.0, moon[0][0] % 360.0)


# ---------------------------------------------------------------------------
# Rashi / Nakshatra / Pada helpers (delegate to KalaVartika)
# ---------------------------------------------------------------------------

def get_rashi(longitude: float) -> int:
    return KalaVartika.rashi_index(longitude)

def get_nakshatra(longitude: float) -> int:
    return KalaVartika.nakshatra_index(longitude)

def get_nakshatra_pada(longitude: float) -> int:
    return KalaVartika.nakshatra_pada(longitude)

def get_rashi_longitude(longitude: float) -> float:
    return KalaVartika.rashi_longitude(longitude)


# ---------------------------------------------------------------------------
# Varga helpers
# ---------------------------------------------------------------------------

def _harmonic_varga_sign(longitude: float, divisor: int) -> int:
    return KalaVartika._harmonic_varga_sign(longitude, divisor)

def _drekkana_sign(longitude: float) -> int:
    return KalaVartika.drekkana_sign(longitude)

def navamsa_sign(longitude: float) -> int:
    return KalaVartika.navamsa_sign(longitude)

def varga_sign(longitude: float, divisor: int) -> int:
    return KalaVartika.varga_sign(longitude, divisor)

def _varga_degree(longitude: float, divisor: int) -> float:
    return KalaVartika.varga_degree(longitude, divisor)


# ---------------------------------------------------------------------------
# Search / bisection utilities
# ---------------------------------------------------------------------------

def find_transition(jd_start: float, get_index_func, max_days: float = 1.2,
                    step_days: float = 0.05) -> float | None:
    """Bisection search for next JD where *get_index_func* changes value."""
    idx0 = get_index_func(jd_start)
    scan_jd = jd_start + step_days
    while scan_jd < jd_start + max_days:
        if get_index_func(scan_jd) != idx0:
            lo, hi = scan_jd - step_days, scan_jd
            for _ in range(20):
                mid = (lo + hi) / 2.0
                if get_index_func(mid) == idx0:
                    lo = mid
                else:
                    hi = mid
            return hi
        scan_jd += step_days
    return None


def find_previous_conjunction(jd_ut: float) -> float:
    """Locate the preceding Sun-Moon conjunction (amavasya) JD."""
    t = jd_ut
    _, m_l = get_sidereal_longitudes(t)
    diff = (m_l - get_sidereal_longitudes(t)[0]) % 360.0

    prev_t = t
    prev_diff = diff
    for _ in range(20):
        t -= 2.0
        curr_diff = (get_sidereal_longitudes(t)[1] - get_sidereal_longitudes(t)[0]) % 360.0
        if curr_diff > prev_diff:
            lo, hi = t, prev_t
            for _ in range(30):
                mid = (lo + hi) / 2.0
                d = (get_sidereal_longitudes(mid)[1] - get_sidereal_longitudes(mid)[0]) % 360.0
                if d > 180.0:
                    lo = mid
                else:
                    hi = mid
            return (lo + hi) / 2.0
        prev_t = t
        prev_diff = curr_diff
    return jd_ut - 29.53


def find_next_conjunction(jd_ut: float) -> float:
    """Locate the next Sun-Moon conjunction JD."""
    t = jd_ut
    _, m_l = get_sidereal_longitudes(t)
    diff = (m_l - get_sidereal_longitudes(t)[0]) % 360.0

    prev_t = t
    prev_diff = diff
    for _ in range(20):
        t += 2.0
        curr_diff = (get_sidereal_longitudes(t)[1] - get_sidereal_longitudes(t)[0]) % 360.0
        if curr_diff < prev_diff:
            lo, hi = prev_t, t
            for _ in range(30):
                mid = (lo + hi) / 2.0
                d = (get_sidereal_longitudes(mid)[1] - get_sidereal_longitudes(mid)[0]) % 360.0
                if d > 180.0:
                    lo = mid
                else:
                    hi = mid
            return (lo + hi) / 2.0
        prev_t = t
        prev_diff = curr_diff
    return jd_ut + 29.53


# ---------------------------------------------------------------------------
# Lunar month details
# ---------------------------------------------------------------------------

def get_lunar_month_details(jd_ut: float,
                            month_system: str = "amavasyanta") -> tuple:
    """Return (masa_idx, is_adhika, is_krishna, tithi_idx, tithi_val).

    month_system: 'amavasyanta' or 'purnimanta'
    """
    prev_jd = find_previous_conjunction(jd_ut)
    next_jd = find_next_conjunction(jd_ut)

    sun_l_prev, _ = get_sidereal_longitudes(prev_jd)
    rashi_prev = int(sun_l_prev / 30.0)

    sun_l_next, _ = get_sidereal_longitudes(next_jd)
    rashi_next = int(sun_l_next / 30.0)

    is_adhika = (rashi_prev == rashi_next)
    masa_idx = (rashi_prev + 1) % 12

    sun_l, moon_l = get_sidereal_longitudes(jd_ut)
    tithi_val = ((moon_l - sun_l) % 360.0) / 12.0
    tithi_idx = int(tithi_val) % 30
    is_krishna = tithi_idx >= 15

    actual_masa_idx = masa_idx
    if month_system == "purnimanta" and not is_adhika and is_krishna:
        actual_masa_idx = (masa_idx + 1) % 12

    return (actual_masa_idx, is_adhika, is_krishna, tithi_idx, tithi_val)


# ---------------------------------------------------------------------------
# Chaitra / Kartika Pratipada
# ---------------------------------------------------------------------------

def get_chaitra_pratipada_jd(year: int) -> float:
    """JD of Chaitra Pratipada: first new-moon after Mar 1 with Sun in Mesha."""
    jd_start = swe.julday(year, 3, 1, 0.0)
    for day in range(40):
        jd = jd_start + day
        next_jd = find_next_conjunction(jd)
        s_l, _ = get_sidereal_longitudes(next_jd)
        rashi = int(s_l / 30.0) % 12
        if rashi == 0:
            return next_jd
    return jd_start + 30.0


def get_kartika_pratipada_jd(year: int) -> float:
    """JD of Kartika Pratipada: first new-moon after Oct 1 with Sun in Kanya."""
    jd_start = swe.julday(year, 10, 1, 0.0)
    for day in range(40):
        jd = jd_start + day
        next_jd = find_next_conjunction(jd)
        s_l, _ = get_sidereal_longitudes(next_jd)
        rashi = int(s_l / 30.0) % 12
        if rashi == 5:
            return next_jd
    return jd_start + 30.0


# ---------------------------------------------------------------------------
# Sankranti (solar ingress)
# ---------------------------------------------------------------------------

def get_prev_sankranti_jd(jd_calc: float) -> float:
    """JD of the previous solar sign change relative to jd_calc."""
    s_l, _ = get_sidereal_longitudes(jd_calc)
    prev_sign = int(s_l / 30.0) % 12
    jd = jd_calc
    for _ in range(40):
        s, _ = get_sidereal_longitudes(jd)
        if int(s / 30.0) % 12 != prev_sign:
            lo, hi = jd, jd + 1.0
            for _ in range(32):
                mid = (lo + hi) / 2.0
                sm, _ = get_sidereal_longitudes(mid)
                if int(sm / 30.0) % 12 == prev_sign:
                    hi = mid
                else:
                    lo = mid
            return hi
        jd -= 1.0
    return jd_calc - 30.0


def get_solar_day_of_month(jd_calc: float, lat: float, lon: float, alt: float,
                           tz: float, jd_ut_start: float) -> int:
    """Day number within the solar (saura) month (≥1)."""
    prev_jd = get_prev_sankranti_jd(jd_calc)
    return int(math.floor(jd_calc - prev_jd)) + 1


def _get_planetary_longitude_at(jd_ut: float) -> float:
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    swe.set_sid_mode(_get_sid_mode())
    res = swe.calc_ut(jd_ut, swe.SUN, flags)
    return res[0][0] % 360.0


# ---------------------------------------------------------------------------
# Rise / Set
# ---------------------------------------------------------------------------

def get_sun_moon_rise_set(jd_ut_day_start: float, lat: float, lon: float,
                          alt: float) -> tuple:
    """Return (sunrise_jd, sunset_jd, moonrise_jd|None, moonset_jd|None)."""
    geopos = (lon, lat, alt)
    flags = swe.FLG_MOSEPH

    sunrise_result = swe.rise_trans_true_hor(
        jd_ut_day_start, swe.SUN, swe.CALC_RISE, geopos,
        1013.25, 15.0, 0.0, flags)
    sunrise_jd = sunrise_result[1][0] if isinstance(sunrise_result, tuple) and isinstance(sunrise_result[1], tuple) else (sunrise_result[0] if isinstance(sunrise_result, tuple) else sunrise_result)

    sunset_result = swe.rise_trans_true_hor(
        sunrise_jd, swe.SUN, swe.CALC_SET, geopos,
        1013.25, 15.0, 0.0, flags)
    sunset_jd = sunset_result[1][0] if isinstance(sunset_result, tuple) and isinstance(sunset_result[1], tuple) else (sunset_result[0] if isinstance(sunset_result, tuple) else sunset_result)

    moonrise_jd = None
    moonset_jd = None
    try:
        mr = swe.rise_trans_true_hor(
            sunrise_jd, swe.MOON, swe.CALC_RISE, geopos,
            1013.25, 15.0, 0.0, flags)
        moonrise_jd = mr[1][0] if isinstance(mr, tuple) and isinstance(mr[1], tuple) else (mr[0] if isinstance(mr, tuple) else mr)
    except Exception:
        pass
    try:
        ms = swe.rise_trans_true_hor(
            sunrise_jd, swe.MOON, swe.CALC_SET, geopos,
            1013.25, 15.0, 0.0, flags)
        moonset_jd = ms[1][0] if isinstance(ms, tuple) and isinstance(ms[1], tuple) else (ms[0] if isinstance(ms, tuple) else ms)
    except Exception:
        pass

    return (sunrise_jd, sunset_jd, moonrise_jd, moonset_jd)


# ---------------------------------------------------------------------------
# Karana name helper
# ---------------------------------------------------------------------------

def get_karana_name_from_idx(k_idx: int, lang: str = "en") -> str:
    """Resolve karana index (0–59) to its name.

    The first 56 slots are the seven movable karanas cycling 8 times; the
    final four slots are the fixed karanas in classical order: 56=Shakuni,
    57=Chatushpada, 58=Naga, 59=Kimstughna.
    """
    names = KalaKosha.KARANAS[lang]
    if 0 <= k_idx < 56:
        return names[k_idx % 7]
    fixed_map = {56: names[7], 57: names[8], 58: names[9], 59: names[10]}
    return fixed_map.get(k_idx, names[6])


# ---------------------------------------------------------------------------
# Panchanga (daily almanac)
# ---------------------------------------------------------------------------

def calculate_panchanga(year: int, month: int, day: int, tz: float,
                        lat: float, lon: float, alt: float,
                        tithi_mode: str = "traditional",
                        calendar_system: str = "shaka",
                        month_system: str = "amavasyanta",
                        lang: str = "en") -> dict:
    """Compute full daily panchanga record."""

    jd_ut_start = swe.julday(year, month, day, -tz)
    tomorrow_jd_ut = jd_ut_start + 1.0

    sunrise_jd, sunset_jd, moonrise_jd, moonset_jd = get_sun_moon_rise_set(
        jd_ut_start, lat, lon, alt)
    _, tomorrow_sunset, _, _ = get_sun_moon_rise_set(
        tomorrow_jd_ut, lat, lon, alt)
    _tsr = swe.rise_trans_true_hor(
        tomorrow_jd_ut, swe.SUN, swe.CALC_RISE, (lon, lat, alt),
        1013.25, 15.0, 0.0, swe.FLG_MOSEPH)
    tomorrow_sunrise = _tsr[1][0] if isinstance(_tsr, tuple) and isinstance(_tsr[1], tuple) else (_tsr[0] if isinstance(_tsr, tuple) else _tsr)

    jd_calc = sunrise_jd if tithi_mode == "traditional" else (sunrise_jd + sunset_jd) / 2.0
    sun_l, moon_l = get_sidereal_longitudes(jd_calc)

    # --- Tithi / Paksha / Masa ---
    masa_idx, is_adhika, is_krishna, tithi_idx_now, tithi_val = \
        get_lunar_month_details(jd_calc, month_system)

    # Saura mode override
    sun_rashi = int(sun_l / 30.0) % 12
    if calendar_system == "saura":
        masa_idx = sun_rashi
        is_krishna = False
        solar_day = get_solar_day_of_month(jd_calc, lat, lon, alt, tz, jd_ut_start)
    else:
        solar_day = None

    t_idx = masa_idx  # tithi group index within the month
    tithi_num = (tithi_idx_now % 15) + 1
    paksha_idx = 1 if is_krishna else 0

    if calendar_system == "saura":
        masa_name = KalaKosha.SAURA_MASAS[lang][masa_idx]
    else:
        masa_name = KalaKosha.MASAS[lang][masa_idx]
    if is_adhika:
        masa_name = (_ADHIKA_PREFIX[lang] + " ") + masa_name
    paksha_name = KalaKosha.PAKSHAS[lang][paksha_idx] if calendar_system != "saura" else ""

    # --- Nakshatra ---
    nak_idx = int(moon_l / KalaVartika.NAKSHATRA_SPAN) % 27
    nak_name = KalaKosha.NAKSHATRAS[lang][nak_idx]
    nak_lord_idx = KalaKosha.NAKSHATRA_LORD[nak_idx]
    nak_adhipati = KalaKosha.GRAHAS[lang][nak_lord_idx]
    nak_pada = KalaVartika.nakshatra_pada(moon_l)
    nak_initials = KalaKosha.NAKSHATRA_INITIALS[lang]
    nak_initial_idx = nak_idx * 4 + (nak_pada - 1)
    nak_initial = nak_initials[nak_initial_idx] if nak_initial_idx < len(nak_initials) else ""

    # --- Moon rashi ---
    moon_rashi_idx = int(moon_l / 30.0) % 12
    moon_rashi = KalaKosha.RASIS[lang][moon_rashi_idx]

    # --- Lagna at sunrise ---
    lagna_lon, _ = swe.houses(sunrise_jd, lat, lon, b"P")
    ayan_val = get_ayanamsa_value(sunrise_jd)
    lagna_sidereal = (lagna_lon[0] % 360.0) - ayan_val
    if lagna_sidereal < 0:
        lagna_sidereal += 360.0
    lagna_idx = int(lagna_sidereal / 30.0) % 12
    lagna_adhipati = KalaKosha.GRAHAS[lang][KalaKosha.RASHI_LORD[lagna_idx]]

    # --- Yoga ---
    diff_sum = (moon_l + sun_l) % 360.0
    yoga_idx = int(diff_sum / KalaVartika.YOGA_SPAN) % 27
    yoga_name = KalaKosha.YOGAS[lang][yoga_idx]

    # --- Karana ---
    diff_l = (moon_l - sun_l) % 360.0
    k_idx = int(diff_l / 6.0)
    karana_name = get_karana_name_from_idx(k_idx, lang)

    # --- Vaara ---
    date_obj = _dt.date(year, month, day)
    vaara_idx = date_obj.weekday()  # Monday=0
    vaara_name = KalaKosha.VAARAS[lang][vaara_idx]

    # --- Ritu / Ayana ---
    if calendar_system == "saura":
        ritu_idx = KalaVartika.ritu_from_rashi(sun_rashi)
    else:
        ritu_idx = KalaVartika.ritu_from_tithi_idx(t_idx)
    ritu_name = KalaKosha.RITUS[lang][ritu_idx]
    ayana_idx = KalaVartika.ayana_from_rashi(sun_rashi)
    ayana_name = KalaKosha.AYANAS[lang][ayana_idx]

    # --- Era calculations ---
    year_calc = year
    is_after_chaitra_prat = jd_calc >= get_chaitra_pratipada_jd(year_calc)

    if calendar_system == "saura":
        shaka_year_val = year_calc - 78 if sun_rashi < 9 else year_calc - 79
        vikram_year_val = year_calc + 57 if sun_rashi < 9 else year_calc + 56
        era_year = shaka_year_val
        era_name = "Solar Shaka" if lang == "en" else "सौर शक"
    else:
        shaka_year_val = KalaVartika.shaka_year(year_calc, is_after_chaitra_prat)
        if calendar_system == "kartak":
            is_after_kartika_prat = jd_calc >= get_kartika_pratipada_jd(year_calc)
            vikram_year_val = KalaVartika.vikram_year(year_calc, is_after_kartika_prat)
        else:
            vikram_year_val = KalaVartika.vikram_year(year_calc, is_after_chaitra_prat)
        era_year = shaka_year_val if calendar_system in ("shaka",) else vikram_year_val
        era_name = "Shaka" if calendar_system == "shaka" else \
                   ("Vikram" if calendar_system == "vikram" else "Kartak")

    kali_year_val = KalaVartika.kali_year(shaka_year_val)

    if calendar_system in ("vikram", "kartak"):
        samvatsara_idx = KalaVartika.samvatsara_idx_vikram(vikram_year_val)
    else:
        samvatsara_idx = KalaVartika.samvatsara_idx_shaka(shaka_year_val)
    samvatsara_name = KalaKosha.SAMVATSARAS[lang][samvatsara_idx]

    # --- Rahu / Yama / Gulika ---
    day_duration = (sunset_jd - sunrise_jd) * 24.0
    part_duration = day_duration / 8.0
    vaara = vaara_idx
    rahu_parts = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}
    yama_parts = {0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6, 6: 5}
    gulika_parts = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 7}

    def _part_str(part_num):
        start = sunrise_jd + (part_num - 1) * part_duration / 24.0
        end = sunrise_jd + part_num * part_duration / 24.0
        s_str = KalaVartika.format_time_hhmm(start, tz, jd_ut_start)
        e_str = KalaVartika.format_time_hhmm(end, tz, jd_ut_start)
        return f"{s_str} - {e_str}"

    rahu_kala = _part_str(rahu_parts[vaara])
    yamaghanta = _part_str(yama_parts[vaara])
    gulika_str = _part_str(gulika_parts[vaara])

    # --- Abhijit Muhurta ---
    muhurta_dur = day_duration / 15.0
    abhijit_start = sunrise_jd + 7 * muhurta_dur / 24.0
    abhijit_end = sunrise_jd + 8 * muhurta_dur / 24.0
    abhijit_str = f"{KalaVartika.format_time_hhmm(abhijit_start, tz, jd_ut_start)} - {KalaVartika.format_time_hhmm(abhijit_end, tz, jd_ut_start)}"

    # --- Ghadi (live value for "today"; deterministic for any other date) ---
    now_jd = _now_jd_ut()
    if now_jd < sunrise_jd or now_jd >= tomorrow_sunrise:
        mins_since_sunrise = 0.0 if now_jd < sunrise_jd else (tomorrow_sunrise - sunrise_jd) * 1440.0
    else:
        mins_since_sunrise = (now_jd - sunrise_jd) * 1440.0
    ghadi = mins_since_sunrise / 24.0
    ghadi_g = int(ghadi)
    ghadi_v = int((ghadi - ghadi_g) * 60)
    ghadi_str = f"{ghadi_g}:{ghadi_v:02d}" if ghadi_g < 1440 else "0:00"

    # --- Brahma Muhurta ---
    bm_end = sunrise_jd - 48.0 / 1440.0
    bm_start = bm_end - 96.0 / 1440.0
    brahma_str = f"{KalaVartika.format_time_hhmm(bm_start, tz, jd_ut_start)} - {KalaVartika.format_time_hhmm(bm_end, tz, jd_ut_start)}"

    # --- Tithi transitions ---
    def get_tithi_idx(jd):
        s, m = get_sidereal_longitudes(jd)
        return int(((m - s) % 360.0) / 12.0) % 30

    def get_nakshatra_idx(jd):
        _, m = get_sidereal_longitudes(jd)
        return int(m / KalaVartika.NAKSHATRA_SPAN) % 27

    def get_yoga_idx(jd):
        s, m = get_sidereal_longitudes(jd)
        return int(((m + s) % 360.0) / KalaVartika.YOGA_SPAN) % 27

    def get_karana_idx(jd):
        s, m = get_sidereal_longitudes(jd)
        return int(((m - s) % 360.0) / 6.0)

    tithi_end_jd = find_transition(sunrise_jd, get_tithi_idx)
    nak_end_jd = find_transition(sunrise_jd, get_nakshatra_idx)
    yoga_end_jd = find_transition(sunrise_jd, get_yoga_idx)
    karana_end_jd = find_transition(sunrise_jd, get_karana_idx)

    tithi_2_end = None
    nakshatra_2_end = None

    # second nakshatra at sunrise
    nakshatra_2_name = "--"
    if nak_end_jd is not None and nak_end_jd < tomorrow_sunrise:
        nak_2_idx = get_nakshatra_idx(nak_end_jd + 0.02)
        nakshatra_2_name = KalaKosha.NAKSHATRAS[lang][nak_2_idx]
        nak_2_end_jd = find_transition(nak_end_jd + 0.02, get_nakshatra_idx)
        if nak_2_end_jd is not None:
            nakshatra_2_end = KalaVartika.format_time_hhmm(nak_2_end_jd, tz, jd_ut_start)

    nakshatra_1_end = None
    if nak_end_jd is not None:
        nakshatra_1_end = KalaVartika.format_time_hhmm(nak_end_jd, tz, jd_ut_start)
    nakshatra_survives = (nak_end_jd is None) or (nak_end_jd > tomorrow_sunrise)
    nakshatra_active_idx = 2 if (not nakshatra_survives and nak_end_jd is not None) else 1

    # second tithi at sunrise
    tithi_1 = KalaKosha.TITHIS[lang][get_tithi_idx(sunrise_jd)]
    tithi_2 = None
    tithi_2_idx = None
    if tithi_end_jd is not None:
        tithi_2_idx = get_tithi_idx(tithi_end_jd + 0.001)
        tithi_2 = KalaKosha.TITHIS[lang][tithi_2_idx]
        tithi_2_end = None
        tithi_2_end_jd = find_transition(tithi_end_jd + 0.001, get_tithi_idx)
        if tithi_2_end_jd is not None:
            tithi_2_end = KalaVartika.format_time_hhmm(tithi_2_end_jd, tz, jd_ut_start)

    tithi_end_str = None
    if tithi_end_jd is not None:
        tithi_end_str = KalaVartika.format_time_hhmm(tithi_end_jd, tz, jd_ut_start)

    tithi_survives = False
    if tithi_end_jd is not None:
        tithi_survives = tithi_end_jd > tomorrow_sunrise

    active_tithi = 1
    if tithi_survives:
        active_tithi = 1
    elif tithi_end_jd is not None:
        active_tithi = 2

    is_tithi_2_kshaya = False
    if tithi_2 is not None:
        next_idx = get_tithi_idx(tithi_end_jd + 0.01)
        expected_next = (get_tithi_idx(sunrise_jd) + 1) % 30
        if next_idx != expected_next:
            is_tithi_2_kshaya = True

    # --- Kshaya tithi detection (Traditional, sunrise basis) ---
    # If the tithi at tomorrow's sunrise skips the one that should follow
    # today's sunrise tithi (e.g. Saptami today -> Navami tomorrow), the
    # skipped tithi (Ashtami) is kshaya and is attributed to today.
    tithi_kshaya_idx = None
    tithi_kshaya = None
    tithi_kshaya_num = None
    if tithi_mode == "traditional" and tomorrow_sunrise:
        today_sr_idx = get_tithi_idx(sunrise_jd)
        tomorrow_sr_idx = get_tithi_idx(tomorrow_sunrise)
        if (tomorrow_sr_idx - today_sr_idx) % 30 == 2:
            tithi_kshaya_idx = (today_sr_idx + 1) % 30
            tithi_kshaya = KalaKosha.TITHIS[lang][tithi_kshaya_idx]
            tithi_kshaya_num = (tithi_kshaya_idx % 15) + 1

    # --- Surya Nakshatra ---
    surya_nak_idx = int(sun_l / KalaVartika.NAKSHATRA_SPAN) % 27
    surya_nak_name = KalaKosha.NAKSHATRAS[lang][surya_nak_idx]

    def get_surya_nakshatra_idx(jd):
        s, _ = get_sidereal_longitudes(jd)
        return int(s / KalaVartika.NAKSHATRA_SPAN) % 27

    surya_nak_end_jd = find_transition(sunrise_jd, get_surya_nakshatra_idx)
    surya_nakshatra_1_end = None
    if surya_nak_end_jd is not None:
        surya_nakshatra_1_end = KalaVartika.format_time_hhmm(surya_nak_end_jd, tz, jd_ut_start)
    surya_nakshatra_2 = None
    surya_nakshatra_2_end = None
    if surya_nak_end_jd is not None and surya_nak_end_jd < tomorrow_sunrise:
        s2_idx = get_surya_nakshatra_idx(surya_nak_end_jd + 0.02)
        surya_nakshatra_2 = KalaKosha.NAKSHATRAS[lang][s2_idx]
        s2_end_jd = find_transition(surya_nak_end_jd + 0.02, get_surya_nakshatra_idx)
        if s2_end_jd is not None:
            surya_nakshatra_2_end = KalaVartika.format_time_hhmm(s2_end_jd, tz, jd_ut_start)
    surya_nakshatra_survives = (surya_nak_end_jd is None) or (surya_nak_end_jd > tomorrow_sunrise)
    surya_nakshatra_active_idx = 2 if (not surya_nakshatra_survives and surya_nak_end_jd is not None) else 1

    # --- Yoga transitions ---
    yoga_1 = yoga_name
    yoga_2 = None
    yoga_1_end = None
    yoga_2_end = None
    if yoga_end_jd is not None:
        yoga_1_end = KalaVartika.format_time_hhmm(yoga_end_jd, tz, jd_ut_start)
        if yoga_end_jd < tomorrow_sunrise:
            y2_idx = get_yoga_idx(yoga_end_jd + 0.02)
            yoga_2 = KalaKosha.YOGAS[lang][y2_idx]
            y2_end_jd = find_transition(yoga_end_jd + 0.02, get_yoga_idx)
            if y2_end_jd is not None:
                yoga_2_end = KalaVartika.format_time_hhmm(y2_end_jd, tz, jd_ut_start)
    yoga_survives = (yoga_end_jd is None) or (yoga_end_jd > tomorrow_sunrise)
    yoga_active_idx = 2 if (not yoga_survives and yoga_end_jd is not None) else 1

    # --- Karana transitions ---
    karana_1 = karana_name
    karana_2 = None
    karana_1_end = None
    karana_2_end = None
    if karana_end_jd is not None:
        karana_1_end = KalaVartika.format_time_hhmm(karana_end_jd, tz, jd_ut_start)
        if karana_end_jd < tomorrow_sunrise:
            k2_idx = get_karana_idx(karana_end_jd + 0.02)
            karana_2 = get_karana_name_from_idx(k2_idx, lang)
            k2_end_jd = find_transition(karana_end_jd + 0.02, get_karana_idx)
            if k2_end_jd is not None:
                karana_2_end = KalaVartika.format_time_hhmm(k2_end_jd, tz, jd_ut_start)
    karana_survives = (karana_end_jd is None) or (karana_end_jd > tomorrow_sunrise)
    karana_active_idx = 2 if (not karana_survives and karana_end_jd is not None) else 1

    # --- Choghadiya ---
    ch_day = []
    ch_night = []
    day_dur = (sunset_jd - sunrise_jd) * 24.0 * 60.0
    night_dur = (tomorrow_sunrise - sunset_jd) * 24.0 * 60.0
    ch_dur_day = day_dur / 8.0
    ch_dur_night = night_dur / 8.0

    day_start_idx = KalaKosha.CHOGHADIYA_DAY_START.get(vaara, 0)
    night_start_idx = KalaKosha.CHOGHADIYA_NIGHT_START.get(vaara, 0)

    ch_names = KalaKosha.CHOGHADIYAS[lang]
    ch_nats = KalaKosha.CHOGHADIYA_NATURES.get(lang, {})

    for i in range(8):
        s = sunrise_jd + (i * ch_dur_day / 1440.0)
        e = sunrise_jd + ((i + 1) * ch_dur_day / 1440.0)
        ch_idx = (day_start_idx + i) % 7
        ch_name = ch_names[ch_idx]
        ch_nat = ch_nats.get(ch_name, "Neutral")
        ch_day.append({
            "name": ch_name,
            "start": KalaVartika.format_time_hhmm(s, tz, jd_ut_start),
            "end": KalaVartika.format_time_hhmm(e, tz, jd_ut_start),
            "nature": ch_nat,
        })

    for i in range(8):
        s = sunset_jd + (i * ch_dur_night / 1440.0)
        e = sunset_jd + ((i + 1) * ch_dur_night / 1440.0)
        ch_idx = (night_start_idx + i) % 7
        ch_name = ch_names[ch_idx]
        ch_nat = ch_nats.get(ch_name, "Neutral")
        ch_night.append({
            "name": ch_name,
            "start": KalaVartika.format_time_hhmm(s, tz, jd_ut_start),
            "end": KalaVartika.format_time_hhmm(e, tz, jd_ut_start),
            "nature": ch_nat,
        })

    date_str = f"{day:02d}-{month:02d}-{year:04d}"

    return {
        "date": date_str,
        "vaara": vaara_name,
        "tithi": KalaKosha.TITHIS[lang][get_tithi_idx(sunrise_jd)],
        "tithi_1": tithi_1,
        "tithi_1_end": tithi_end_str,
        "tithi_2": tithi_2,
        "tithi_2_end": tithi_2_end,
        "active_tithi": active_tithi,
        "tithi_active_idx": active_tithi,
        "tithi_survives": tithi_survives,
        "is_tithi_2_kshaya": is_tithi_2_kshaya,
        "tithi_kshaya": tithi_kshaya,
        "tithi_kshaya_idx": tithi_kshaya_idx,
        "tithi_kshaya_num": tithi_kshaya_num,
        "paksha": paksha_name,
        "is_krishna_paksha": is_krishna,
        "masa": masa_name,
        "masa_idx": masa_idx,
        "nakshatra": nak_name,
        "nakshatra_1": nak_name,
        "nakshatra_2": nakshatra_2_name,
        "nakshatra_end": nakshatra_1_end,
        "nakshatra_1_end": nakshatra_1_end,
        "nakshatra_2_end": nakshatra_2_end,
        "nakshatra_active_idx": nakshatra_active_idx,
        "nakshatra_survives": nakshatra_survives,
        "nakshatra_pada": nak_pada,
        "nakshatra_adhipati": nak_adhipati,
        "nakshatra_initial": nak_initial,
        "moon_rashi": moon_rashi,
        "moon_rashi_idx": moon_rashi_idx,
        "moon_rashi_adhipati": KalaKosha.GRAHAS[lang][KalaKosha.RASHI_LORD[moon_rashi_idx]],
        "lagna": KalaKosha.RASIS[lang][lagna_idx],
        "lagna_idx": lagna_idx,
        "lagna_adhipati": lagna_adhipati,
        "yoga": yoga_name,
        "yoga_1": yoga_1,
        "yoga_1_end": yoga_1_end,
        "yoga_2": yoga_2,
        "yoga_2_end": yoga_2_end,
        "yoga_active_idx": yoga_active_idx,
        "yoga_survives": yoga_survives,
        "karana": karana_name,
        "karana_1": karana_1,
        "karana_1_end": karana_1_end,
        "karana_2": karana_2,
        "karana_2_end": karana_2_end,
        "karana_active_idx": karana_active_idx,
        "karana_survives": karana_survives,
        "ritu": ritu_name,
        "ayana": ayana_name,
        "samvatsara": samvatsara_name,
        "era_name": era_name,
        "era_year": era_year,
        "shaka_year": shaka_year_val,
        "vikram_year": vikram_year_val,
        "kali_year": kali_year_val,
        "sunrise": KalaVartika.format_time_hhmm(sunrise_jd, tz, jd_ut_start),
        "sunset": KalaVartika.format_time_hhmm(sunset_jd, tz, jd_ut_start),
        "moonrise": KalaVartika.format_time_hhmm(moonrise_jd, tz, jd_ut_start) if moonrise_jd else None,
        "moonset": KalaVartika.format_time_hhmm(moonset_jd, tz, jd_ut_start) if moonset_jd else None,
        "rahu_kala": rahu_kala,
        "yamaghanta": yamaghanta,
        "gulika": gulika_str,
        "abhijit_muhurta": abhijit_str,
        "ghadi": ghadi_str,
        "brahma_muhurta": brahma_str,
        "day_choghadiya": ch_day,
        "night_choghadiya": ch_night,
        "tithi_num": tithi_num,
        "tithi_idx": get_tithi_idx(sunrise_jd),
        "surya_nakshatra": surya_nak_name,
        "surya_nakshatra_1": surya_nak_name,
        "surya_nakshatra_1_end": surya_nakshatra_1_end,
        "surya_nakshatra_2": surya_nakshatra_2,
        "surya_nakshatra_2_end": surya_nakshatra_2_end,
        "surya_nakshatra_active_idx": surya_nakshatra_active_idx,
        "surya_nakshatra_survives": surya_nakshatra_survives,
        "sunrise_jd": sunrise_jd,
        "sunset_jd": sunset_jd,
        "moonrise_jd": moonrise_jd,
        "moonset_jd": moonset_jd,
        "tomorrow_sunrise_jd": tomorrow_sunrise,
        "jd_calc": jd_calc,
        "jd_ut_start": jd_ut_start,
        "is_adhika": is_adhika,
        "tithi_2_idx": tithi_2_idx,
        "lat": lat,
        "lon": lon,
        "alt": alt,
        "solar_day": solar_day,
        "calendar_system": calendar_system,
    }


# ---------------------------------------------------------------------------
# Time formatting helpers (for internal use and external compatibility)
# ---------------------------------------------------------------------------

def _time_str(jd: float, tz: float, jd_ut_start: float) -> str:
    return KalaVartika.format_time_hhmm(jd, tz, jd_ut_start)


def _jd_to_datetime_str(jd: float, tz: float) -> str:
    return KalaVartika.format_datetime(jd, tz)


def _now_jd_ut() -> float:
    now = _dt.datetime.utcnow()
    return swe.julday(now.year, now.month, now.day,
                      now.hour + now.minute / 60.0 + now.second / 3600.0)


# ---------------------------------------------------------------------------
# Dina Horas (Chaldean hourly lords)
# ---------------------------------------------------------------------------

_HORA_AUSPICIOUS = {4, 5}
_HORA_INAUSPICIOUS = {2, 6}


def calculate_dina_horas(year: int, month: int, day: int, tz: float,
                         lat: float, lon: float, alt: float,
                         lang: str = "en") -> dict:
    """Compute 24 Chaldean horas (12 day + 12 night)."""
    jd_ut_start = swe.julday(year, month, day, -tz)
    sunrise_jd, sunset_jd, _, _ = get_sun_moon_rise_set(jd_ut_start, lat, lon, alt)
    tomorrow_jd_ut = jd_ut_start + 1.0
    _tsr = swe.rise_trans_true_hor(
        tomorrow_jd_ut, swe.SUN, swe.CALC_RISE, (lon, lat, alt),
        1013.25, 15.0, 0.0, swe.FLG_MOSEPH)
    tomorrow_sunrise = _tsr[1][0] if isinstance(_tsr, tuple) and isinstance(_tsr[1], tuple) else (_tsr[0] if isinstance(_tsr, tuple) else _tsr)

    date_obj = _dt.date(year, month, day)
    vaara_idx = date_obj.weekday()

    day_dur = (sunset_jd - sunrise_jd) * 24.0 * 60.0
    night_dur = (tomorrow_sunrise - sunset_jd) * 24.0 * 60.0

    start_lord_pos = KalaKosha.HORA_ORDER.index(KalaKosha.WEEKDAY_LORD[vaara_idx])

    def hora_entry(idx, is_day):
        dur = day_dur if is_day else night_dur
        if is_day:
            step_days = dur / 1440.0 / 12.0
            start_jd = sunrise_jd + (idx * step_days)
            end_jd = sunrise_jd + ((idx + 1) * step_days)
        else:
            step_days = dur / 1440.0 / 12.0
            start_jd = sunset_jd + (idx * step_days)
            end_jd = sunset_jd + ((idx + 1) * step_days)

        lord_idx = KalaKosha.HORA_ORDER[(start_lord_pos + (12 if not is_day else 0) + idx) % 7]
        lord_name = KalaKosha.GRAHAS[lang][lord_idx]

        if lord_idx in _HORA_AUSPICIOUS:
            nature = "Auspicious"
            code = "AUS"
        elif lord_idx in _HORA_INAUSPICIOUS:
            nature = "Inauspicious"
            code = "INA"
        else:
            nature = "Neutral"
            code = "NEU"

        return {
            "lord": lord_name,
            "lord_idx": lord_idx,
            "start": _time_str(start_jd, tz, jd_ut_start),
            "end": _time_str(end_jd, tz, jd_ut_start),
            "period": f"{(end_jd - start_jd) * 24.0 * 60:.0f} min",
            "nature": nature,
            "code": code,
        }

    day_horas = [hora_entry(i, True) for i in range(12)]
    night_horas = [hora_entry(i, False) for i in range(12)]

    return {
        "vaara": KalaKosha.VAARAS[lang][vaara_idx],
        "sunrise": _time_str(sunrise_jd, tz, jd_ut_start),
        "sunset": _time_str(sunset_jd, tz, jd_ut_start),
        "day_length_min": round(day_dur),
        "night_length_min": round(night_dur),
        "day_horas": day_horas,
        "night_horas": night_horas,
    }


# ---------------------------------------------------------------------------
# Muhurtas
# ---------------------------------------------------------------------------

def _overlaps(a1, a2, b1, b2) -> bool:
    return a1 < b2 and b1 < a2


def calculate_muhurtas(year: int, month: int, day: int, tz: float,
                       lat: float, lon: float, alt: float,
                       lang: str = "en") -> dict:
    """Compute 15 day + 15 night muhurtas with classification."""
    jd_ut_start = swe.julday(year, month, day, -tz)
    sunrise_jd, sunset_jd, _, _ = get_sun_moon_rise_set(jd_ut_start, lat, lon, alt)
    tomorrow_jd_ut = jd_ut_start + 1.0
    _tsr = swe.rise_trans_true_hor(
        tomorrow_jd_ut, swe.SUN, swe.CALC_RISE, (lon, lat, alt),
        1013.25, 15.0, 0.0, swe.FLG_MOSEPH)
    tomorrow_sunrise = _tsr[1][0] if isinstance(_tsr, tuple) and isinstance(_tsr[1], tuple) else (_tsr[0] if isinstance(_tsr, tuple) else _tsr)

    date_obj = _dt.date(year, month, day)
    vaara_idx = date_obj.weekday()

    day_dur = (sunset_jd - sunrise_jd) * 24.0 * 60.0
    night_dur = (tomorrow_sunrise - sunset_jd) * 24.0 * 60.0

    rahu_parts = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}
    yama_parts = {0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6, 6: 5}
    gulika_parts = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 7}

    def window(part_num, day_dur_min):
        start_min = (part_num - 1) * day_dur_min / 8.0
        end_min = part_num * day_dur_min / 8.0
        return (sunrise_jd + start_min / 1440.0, sunrise_jd + end_min / 1440.0)

    day_dur_min = day_dur
    rahu_w = window(rahu_parts[vaara_idx], day_dur_min)
    yama_w = window(yama_parts[vaara_idx], day_dur_min)
    gulika_w = window(gulika_parts[vaara_idx], day_dur_min)

    abhijit_start_jd = sunrise_jd + (day_dur_min * 7 / 15.0) / 1440.0
    abhijit_end_jd = sunrise_jd + (day_dur_min * 8 / 15.0) / 1440.0

    def muhurta_entries(start_jd, dur_min, count=15):
        entries = []
        muh_dur = dur_min / float(count)
        for i in range(count):
            s = start_jd + (i * muh_dur / 1440.0)
            e = start_jd + ((i + 1) * muh_dur / 1440.0)
            name = KalaKosha.MUHURTA_NAMES[lang][i % len(KalaKosha.MUHURTA_NAMES[lang])]

            s_unix = _jd_to_unix(s)
            e_unix = _jd_to_unix(e)
            is_abhijit = _overlaps(s_unix, e_unix,
                                   _jd_to_unix(abhijit_start_jd),
                                   _jd_to_unix(abhijit_end_jd))

            in_rahu = _overlaps(s_unix, e_unix, _jd_to_unix(rahu_w[0]), _jd_to_unix(rahu_w[1]))
            in_yama = _overlaps(s_unix, e_unix, _jd_to_unix(yama_w[0]), _jd_to_unix(yama_w[1]))
            in_gulika = _overlaps(s_unix, e_unix, _jd_to_unix(gulika_w[0]), _jd_to_unix(gulika_w[1]))

            if is_abhijit:
                status = "Abhijit"
            elif in_rahu or in_yama or in_gulika:
                status = "Inauspicious"
            else:
                status = "Neutral"

            entries.append({
                "name": name,
                "start": _time_str(s, tz, jd_ut_start),
                "end": _time_str(e, tz, jd_ut_start),
                "status": status,
            })
        return entries

    day_muhurtas = muhurta_entries(sunrise_jd, day_dur_min)
    night_muhurtas = muhurta_entries(sunset_jd, night_dur)

    return {
        "day_muhurtas": day_muhurtas,
        "night_muhurtas": night_muhurtas,
        "abhijit": {
            "start": _time_str(abhijit_start_jd, tz, jd_ut_start),
            "end": _time_str(abhijit_end_jd, tz, jd_ut_start),
        },
        "rahu_kala": f"{_time_str(rahu_w[0], tz, jd_ut_start)} - {_time_str(rahu_w[1], tz, jd_ut_start)}",
        "yamaghanta": f"{_time_str(yama_w[0], tz, jd_ut_start)} - {_time_str(yama_w[1], tz, jd_ut_start)}",
        "gulika": f"{_time_str(gulika_w[0], tz, jd_ut_start)} - {_time_str(gulika_w[1], tz, jd_ut_start)}",
    }


def _jd_to_unix(jd: float) -> float:
    """Convert Julian Day to Unix timestamp (approximate)."""
    return (jd - 2440587.5) * 86400.0


# ---------------------------------------------------------------------------
# Planet detail extraction
# ---------------------------------------------------------------------------

_COMBUSTION_ORBS = {1: 12.0, 2: 17.0, 3: 14.0, 4: 11.0, 5: 10.0, 6: 15.0}
_VARGA_DIVISIONS = [2, 3, 4, 7, 8, 9, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60]

_ADHIKA_PREFIX = {"en": "Adhika", "iast": "Adhika", "devanagari": "अधिक"}

_DIGNITY_LABELS = {
    "en": {"exalted": "Exalted", "debilitated": "Debilitated",
           "moolatrikona": "Moolatrikona", "own": "Own",
           "friend": "Friend", "neutral": "Neutral", "enemy": "Enemy",
           "own_exalted": "Own (Exalted)"},
    "iast": {"exalted": "Uccatā", "debilitated": "Nīcatā",
             "moolatrikona": "Mūlatrikoṇa", "own": "Svārāśi",
             "friend": "Mitra", "neutral": "Sāmānya", "enemy": "Śatru"},
    "devanagari": {"exalted": "उच्चता", "debilitated": "नीचता",
                   "moolatrikona": "मूलत्रिकोण", "own": "स्वराशि",
                   "friend": "मित्र", "neutral": "सामान्य", "enemy": "शत्रु"},
}

_CHART_TYPE_L10N = {
    "en": {"nirayana": "Nirayana (Sidereal)", "sayana": "Sayana (Tropical)"},
    "iast": {"nirayana": "Nirayāṇa (Jyotiṣa)", "sayana": "Sayana (Tropical)"},
    "devanagari": {"nirayana": "निरयण (ज्योतिष)", "sayana": "सायन (ट्रपिकल)"},
}


def _get_planetary_details(jd_ut: float, tropical: bool = False) -> dict:
    """{idx: (longitude, retrograde, speed_deg_per_day)} for all 12
    ephemeris-based bodies (9 classical grahas + Uranus/Neptune/Pluto)."""
    result = {}
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if not tropical:
        swe.set_sid_mode(_get_sid_mode())
        flags |= swe.FLG_SIDEREAL
    for idx in _PLANET_SWE_IDS:
        res = swe.calc_ut(jd_ut, _PLANET_SWE_IDS[idx], flags)
        lon = res[0][0] % 360.0
        retro = res[0][3] < 0
        speed = abs(res[0][3])
        result[idx] = (lon, retro, speed)
    rahu_lon, rahu_retro, rahu_speed = result[7]
    ketu_lon = (rahu_lon + 180.0) % 360.0
    result[8] = (ketu_lon, False, rahu_speed)
    return result


# ---------------------------------------------------------------------------
# Maandi (time-derived upagraha, "son of Saturn")
# ---------------------------------------------------------------------------
# Classical rule (Bṛhat Parāśara / Phala Dīpikā): the day (sunrise→sunset)
# and night (sunset→next sunrise) are each split into 8 parts.  Maandi rises
# at the fractions below of the total day/night length, counting from its
# start, for Sunday→Saturday.  The Maandi longitude is the (already
# nirayana) ascendant at that rising moment.
_MAANDI_DAY_PARTS   = {0: 26, 1: 22, 2: 18, 3: 14, 4: 10, 5: 6, 6: 2}
_MAANDI_NIGHT_PARTS = {0: 10, 1: 6, 2: 2, 3: 26, 4: 22, 5: 18, 6: 14}


def get_maandi_longitude(jd_ut: float, lat: float, lon: float, alt: float,
                         tropical: bool = False,
                         year: int = 0, month: int = 0, day: int = 0) -> float:
    """Sidereal/tropical longitude of Maandi for a given birth instant.

    year/month/day are the civil (local) date on which day/night is counted;
    the birth weekday is taken from them.  If they are all 0, the date is
    derived from jd_ut with a nominal +5.5 h offset (approximate; callers
    with a known civil date should pass it).
    """
    if year and month and day:
        wd_sun = (_dt.date(year, month, day).weekday() + 1) % 7  # Sunday=0
        day_start_jd = swe.julday(year, month, day, 0)
    else:
        y2, m2, d2, _ = swe.revjul(jd_ut + 5.5 / 24.0)
        wd_sun = (_dt.date(int(y2), int(m2), int(d2)).weekday() + 1) % 7
        day_start_jd = math.floor(jd_ut + 5.5 / 24.0) - 5.5 / 24.0

    sunrise, sunset, _, _ = get_sun_moon_rise_set(day_start_jd, lat, lon, alt)
    next_sunrise, _, _, _ = get_sun_moon_rise_set(day_start_jd + 1.0, lat, lon, alt)

    if sunrise <= jd_ut < sunset:
        frac = _MAANDI_DAY_PARTS[wd_sun] / 30.0
        maandi_jd = sunrise + frac * (sunset - sunrise)
    else:
        if jd_ut < sunrise:
            _, night_start, _, _ = get_sun_moon_rise_set(day_start_jd - 1.0, lat, lon, alt)
            night_end = sunrise
        else:
            night_start = sunset
            night_end = next_sunrise
        frac = _MAANDI_NIGHT_PARTS[wd_sun] / 30.0
        maandi_jd = night_start + frac * (night_end - night_start)

    ayan_val = 0.0 if tropical else get_ayanamsa_value(maandi_jd)
    ascmc, _ = swe.houses(maandi_jd, lat, lon, b"P")
    asc_tropical = ascmc[0] % 360.0
    if not tropical:
        swe.set_sid_mode(_get_sid_mode())
        return (asc_tropical - ayan_val) % 360.0
    return asc_tropical


def _planet_dignity(idx: int, sign: int, lang: str = "en") -> tuple[str, str]:
    """Return (localized_label, raw_code) for a planet's dignity in a sign."""
    if idx >= 7:
        return ("", "")

    ex_sign = KalaKosha.EXALTATION_SIGN[idx]
    if ex_sign is not None and sign == ex_sign:
        return (_DIGNITY_LABELS[lang]["exalted"], "exalted")
    if ex_sign is not None and sign == (ex_sign + 6) % 12:
        return (_DIGNITY_LABELS[lang]["debilitated"], "debilitated")

    own_signs = KalaKosha.OWN_SIGNS.get(idx, [])
    mt_sign = KalaKosha.MOOLATRIKONA_SIGN.get(idx)
    if sign in own_signs and sign == mt_sign:
        return (_DIGNITY_LABELS[lang]["moolatrikona"], "moolatrikona")
    if sign in own_signs:
        return (_DIGNITY_LABELS[lang]["own"], "own")

    friend_planets = KalaKosha.GRAHA_FRIENDS.get(idx, set())
    for f_idx in friend_planets:
        if sign in KalaKosha.OWN_SIGNS.get(f_idx, []):
            return (_DIGNITY_LABELS[lang]["friend"], "friend")

    enemy_planets = KalaKosha.GRAHA_ENEMIES.get(idx, set())
    for e_idx in enemy_planets:
        if sign in KalaKosha.OWN_SIGNS.get(e_idx, []):
            return (_DIGNITY_LABELS[lang]["enemy"], "enemy")

    return (_DIGNITY_LABELS[lang]["neutral"], "neutral")


# ---------------------------------------------------------------------------
# Vimshottari Dasha tree
# ---------------------------------------------------------------------------

def years_to_ymd(years: float) -> dict:
    """Split a (possibly fractional) Vimshottari period into whole years,
    months (1/12 of a solar year) and days for display.  The decimal
    ``years`` field is kept for arithmetic; ``duration`` carries this
    non-decimal breakdown."""
    y = int(years + 1e-9)
    frac = years - y
    m = int(frac * 12.0 + 1e-9)
    days = int(round((frac * 12.0 - m) * (_YEAR_DAYS / 12.0)))
    return {"years": y, "months": m, "days": days}


def calculate_vimshottari_tree(jd_ut: float, moon_lon: float, tz: float,
                               lang: str = "en",
                               now_jd: float | None = None,
                               dasha_depth: int = 3) -> dict:
    """Full Vimshottari tree.  Depth selects how many levels of the classical
    dasha ladder are materialised under each Mahadasha:

        3 = Mahadasha → Antardasha → Pratyantardasha       (default)

    Everything below the Mahadasha balance is pure proportional arithmetic
    (Vimshottari 9-cycle), so expanding to depth 5 is cheap and needs no
    additional Swiss Ephemeris calls."""
    nak_idx = get_nakshatra(moon_lon)
    nak_span = 360.0 / 27.0
    frac_elapsed = (moon_lon - nak_idx * nak_span) / nak_span
    dasha_idx0 = nak_idx % 9
    full_first = KalaKosha.VIMSHOTTARI_YEARS[dasha_idx0]
    balance = (1.0 - frac_elapsed) * full_first

    if now_jd is None:
        now_jd = _now_jd_ut()

    def dlord(cycle_pos):
        return KalaKosha.DASHA_LORDS[cycle_pos % 9]

    md_years_list = [0.0] * 9
    md_years_list[0] = full_first
    for j in range(1, 9):
        md_years_list[j] = KalaKosha.VIMSHOTTARI_YEARS[(dasha_idx0 + j) % 9]

    total_days = sum(y * _YEAR_DAYS for y in md_years_list)

    # Classical Vimshottari: at birth, `frac_elapsed` years of the natal
    # lord's mahadasha have already run and `balance` years remain.  So the
    # first mahadasha *contains* the birth instant: it started
    # (full_first - balance) before birth and ends `balance` after it.
    elapsed = full_first - balance
    md_start = jd_ut - elapsed * _YEAR_DAYS

    def name(planet_idx):
        return KalaKosha.GRAHAS[lang][planet_idx]

    def in_period(start, end):
        return start <= now_jd < end

    def build_md(p_md, md_start_jd, md_years):
        md_lord_idx = dlord(p_md)
        md_name = name(md_lord_idx)
        md_end_jd = md_start_jd + md_years * _YEAR_DAYS

        ads = []
        ad_start_jd = md_start_jd
        for j in range(9):
            p_ad = (p_md + j) % 9
            ad_years = md_years * KalaKosha.VIMSHOTTARI_YEARS[p_ad] / 120.0
            ad_end_jd = ad_start_jd + ad_years * _YEAR_DAYS
            ad_name = name(dlord(p_ad))

            pds = []
            pd_start_jd = ad_start_jd
            for k in range(9):
                p_pd = (p_md + j + k) % 9
                pd_years = ad_years * KalaKosha.VIMSHOTTARI_YEARS[p_pd] / 120.0
                pd_end_jd = pd_start_jd + pd_years * _YEAR_DAYS
                pd_name = name(dlord(p_pd))

                sukmas = []
                if dasha_depth >= 4:
                    sk_start_jd = pd_start_jd
                    ad_pd_years = pd_years
                    for s in range(9):
                        sk_ys = ad_pd_years * KalaKosha.VIMSHOTTARI_YEARS[(p_md+j+k+s) % 9] / 120.0
                        sk_end_jd = sk_start_jd + sk_ys * _YEAR_DAYS
                        pranas = []
                        if dasha_depth >= 5:
                            pr_start_jd = sk_start_jd
                            for t in range(9):
                                p_ys = sk_ys * KalaKosha.VIMSHOTTARI_YEARS[(p_md+j+k+s+t) % 9] / 120.0
                                p_end_jd = pr_start_jd + p_ys * _YEAR_DAYS
                                pranas.append({
                                    "lord": name(dlord((p_md+j+k+s+t) % 9)),
                                    "lord_idx": dlord((p_md+j+k+s+t) % 9),
                                    "years": round(p_ys, 4),
                                    "duration": years_to_ymd(p_ys),
                                    "start_jd": round(pr_start_jd, 4),
                                    "end_jd": round(p_end_jd, 4),
                                    "start_date": _jd_to_datetime_str(pr_start_jd, tz),
                                    "end_date": _jd_to_datetime_str(p_end_jd, tz),
                                    "is_current": in_period(pr_start_jd, p_end_jd),
                                })
                                pr_start_jd = p_end_jd
                        sukmas.append({
                            "lord": name(dlord((p_md+j+k+s) % 9)),
                            "lord_idx": dlord((p_md+j+k+s) % 9),
                            "years": round(sk_ys, 4),
                            "duration": years_to_ymd(sk_ys),
                            "start_jd": round(sk_start_jd, 4),
                            "end_jd": round(sk_end_jd, 4),
                            "start_date": _jd_to_datetime_str(sk_start_jd, tz),
                            "end_date": _jd_to_datetime_str(sk_end_jd, tz),
                            "is_current": in_period(sk_start_jd, sk_end_jd),
                            "prana_dashas": pranas,
                        })
                        sk_start_jd = sk_end_jd

                pds.append({
                    "lord": pd_name,
                    "lord_idx": dlord(p_pd),
                    "years": round(pd_years, 4),
                    "duration": years_to_ymd(pd_years),
                    "start_date": _jd_to_datetime_str(pd_start_jd, tz),
                    "end_date": _jd_to_datetime_str(pd_end_jd, tz),
                    "is_current": in_period(pd_start_jd, pd_end_jd),
                    "suk_ma_dashas": sukmas,
                })
                pd_start_jd = pd_end_jd

            ads.append({
                "lord": ad_name,
                "lord_idx": dlord(p_ad),
                "years": round(ad_years, 4),
                "duration": years_to_ymd(ad_years),
                "start_date": _jd_to_datetime_str(ad_start_jd, tz),
                "end_date": _jd_to_datetime_str(ad_end_jd, tz),
                "is_current": in_period(ad_start_jd, ad_end_jd),
                "pratyantardashas": pds,
            })
            ad_start_jd = ad_end_jd

        return {
            "lord": md_name,
            "lord_idx": dlord(p_md),
            "years": round(md_years, 4),
            "duration": years_to_ymd(md_years),
            "start_date": _jd_to_datetime_str(md_start_jd, tz),
            "end_date": _jd_to_datetime_str(md_end_jd, tz),
            "is_current": in_period(md_start_jd, md_end_jd),
            "antardashas": ads,
        }

    mahadashas = []
    cursor = md_start
    for i in range(9):
        p_md = (dasha_idx0 + i) % 9
        md_yrs = md_years_list[i]
        md = build_md(p_md, cursor, md_yrs)
        mahadashas.append(md)
        cursor = cursor + md_yrs * _YEAR_DAYS

    return {
        "start_lord_idx": dasha_idx0,
        "start_lord": name(dlord(dasha_idx0)),
        "balance_years": round(balance, 4),
        "balance_duration": years_to_ymd(balance),
        "elapsed_years": round(elapsed, 4),
        "elapsed_duration": years_to_ymd(elapsed),
        "total_years": round(sum(md_years_list), 4),
        "mahadashas": mahadashas,
    }


# ---------------------------------------------------------------------------
# Kundali (natal chart)
# ---------------------------------------------------------------------------

def calculate_kundali(year: int, month: int, day: int,
                      hour: int, minute: int, tz: float,
                      lat: float, lon: float, alt: float,
                      ayanamsa: str = "lahiri", lang: str = "en",
                      dasha_depth: int = 3) -> dict:
    """Full natal chart: lagna, planets, vargas, houses, dashas.

    dasha_depth controls the Vimshottari tree expansion depth:
      3 = mahadasha + antardasha + pratyantardasha (PD)
      4 = + sukshma (SS)
      5 = + prana (S-SS)
    The default (3) keeps the chart byte-identical with the classic
    three-level tree."""
    tropical = (ayanamsa == "sayana")
    if not tropical:
        set_ayanamsa(ayanamsa)

    jd_ut = swe.julday(year, month, day, (hour + minute / 60.0) - tz)
    ayan_val = 0.0 if tropical else get_ayanamsa_value(jd_ut)

    details = _get_planetary_details(jd_ut, tropical)
    details[_MAANDI_IDX] = (get_maandi_longitude(jd_ut, lat, lon, alt, tropical,
                                                 year, month, day), False, 0.0)

    # Lagna
    ascmc, _ = swe.houses(jd_ut, lat, lon, b"P")
    asc_tropical = ascmc[0] % 360.0
    asc_sidereal = (asc_tropical - ayan_val) % 360.0 if not tropical else asc_tropical
    asc_rashi = int(asc_sidereal / 30.0) % 12
    asc_nak_idx = int(asc_sidereal / KalaVartika.NAKSHATRA_SPAN) % 27
    asc_pada = KalaVartika.nakshatra_pada(asc_sidereal)

    ayanamsa_label = "Sayana" if tropical else ayanamsa.title()
    ayanamsa_label_en = "Sayana" if tropical else ayanamsa

    sun_lon = details[0][0]
    moon_lon = details[1][0]

    planets = {}
    for idx in range(13):
        plon, retro, speed = details[idx]
        if idx in (7, 8):
            retro = True  # Rahu/Ketu are always Vakri (retrograde nodes)
        rashi = get_rashi(plon)
        nak = get_nakshatra(plon)
        pada = get_nakshatra_pada(plon)
        deg_in_sign = plon - rashi * 30.0

        elon = abs(plon - sun_lon) % 360.0
        elon = min(elon, 360.0 - elon)
        combust = idx in _COMBUSTION_ORBS and elon <= _COMBUSTION_ORBS[idx]

        dignity_label, dignity_code = _planet_dignity(idx, rashi, lang)

        house = (rashi - asc_rashi) % 12 + 1
        is_vargottam = rashi == navamsa_sign(plon)

        graha_name = KalaKosha.GRAHAS[lang][idx]
        planets[graha_name] = {
            "idx": idx,
            "name": graha_name,
            "longitude": round(plon, 4),
            "degree_in_sign": round(deg_in_sign, 4),
            "degree": round(deg_in_sign, 4),
            "rashi": rashi,
            "rashi_name": KalaKosha.RASIS[lang][rashi],
            "nakshatra": nak,
            "nakshatra_name": KalaKosha.NAKSHATRAS[lang][nak],
            "nakshatra_pada": pada,
            "prograde": not retro,
            "retrograde": retro,
            "speed": round(speed, 4),
            "combust": combust,
            "asta": combust,
            "dignity": dignity_label,
            "dignity_code": dignity_code,
            "is_vargottam": is_vargottam,
            "house": house,
        }

    # Vimshottari dashas
    dashas = calculate_vimshottari_tree(jd_ut, moon_lon, tz, lang,
                                        dasha_depth=dasha_depth)

    # Vargas
    def varga_entry(lon_val, divisor):
        return {
            "rashi": varga_sign(lon_val, divisor),
            "degree": round(_varga_degree(lon_val, divisor), 3),
        }

    lagna_planet = {
        "idx": "lagna",
        "name": "Lagna",
        "longitude": round(asc_sidereal, 4),
        "degree_in_sign": round(asc_sidereal - asc_rashi * 30.0, 4),
        "rashi": asc_rashi,
        "rashi_name": KalaKosha.RASIS[lang][asc_rashi],
    }

    vargas = {}
    # D1
    d1_planets = {gname: {"rashi": p["rashi"], "degree": p["degree"]}
                  for gname, p in planets.items()}
    d1_planets["Lagna"] = {"rashi": asc_rashi,
                            "degree": round(asc_sidereal - asc_rashi * 30.0, 4)}
    vargas["D1"] = {"lagna": lagna_planet, "planets": d1_planets}

    # D2–D60
    for divisor in _VARGA_DIVISIONS:
        key = f"D{divisor}"
        v_planets = {}
        v_planets["Lagna"] = varga_entry(asc_sidereal, divisor)
        for idx in range(13):
            pname = KalaKosha.GRAHAS[lang][idx]
            lon_val = details[idx][0]
            v_planets[pname] = varga_entry(lon_val, divisor)
        vargas[key] = {"lagna": varga_entry(asc_sidereal, divisor), "planets": v_planets}

    # Houses (whole-sign)
    houses = {}
    for h in range(1, 13):
        h_rashi = (asc_rashi + h - 1) % 12
        h_lord_idx = KalaKosha.RASHI_LORD[h_rashi]
        houses[h] = {
            "rashi": h_rashi,
            "rashi_name": KalaKosha.RASIS[lang][h_rashi],
            "lord_idx": h_lord_idx,
            "lord": KalaKosha.GRAHAS[lang][h_lord_idx],
        }

    # Meta
    chart_type_en = _CHART_TYPE_L10N[lang].get("sayana" if tropical else "nirayana",
                                                _CHART_TYPE_L10N["en"]["nirayana"])
    meta = {
        "date": f"{day:02d}-{month:02d}-{year:04d}",
        "jd_ut": round(jd_ut, 6),
        "timezone_hours": tz,
        "lat": lat,
        "lon": lon,
        "alt": alt,
        "ayanamsa": ayanamsa_label,
        "ayanamsa_value": round(ayan_val, 5),
        "chart_type": chart_type_en,
    }

    lagna = {
        "rashi": asc_rashi,
        "rashi_name": KalaKosha.RASIS[lang][asc_rashi],
        "nakshatra": asc_nak_idx,
        "nakshatra_name": KalaKosha.NAKSHATRAS[lang][asc_nak_idx],
        "nakshatra_pada": asc_pada,
        "longitude": round(asc_sidereal, 4),
        "lord_idx": KalaKosha.RASHI_LORD[asc_rashi],
        "lord": KalaKosha.GRAHAS[lang][KalaKosha.RASHI_LORD[asc_rashi]],
    }

    # Moon summary for the Kundali tab (Moon sign, nakshatra lord, name initial)
    moon_rashi = get_rashi(moon_lon)
    moon_nak = get_nakshatra(moon_lon)
    moon_pada = get_nakshatra_pada(moon_lon)
    nak_initials = KalaKosha.NAKSHATRA_INITIALS[lang]
    nak_initial_idx = moon_nak * 4 + (moon_pada - 1)
    moon = {
        "rashi": moon_rashi,
        "rashi_name": KalaKosha.RASIS[lang][moon_rashi],
        "rashi_adhipati": KalaKosha.GRAHAS[lang][KalaKosha.RASHI_LORD[moon_rashi]],
        "nakshatra": moon_nak,
        "nakshatra_name": KalaKosha.NAKSHATRAS[lang][moon_nak],
        "nakshatra_pada": moon_pada,
        "nakshatra_adhipati": KalaKosha.GRAHAS[lang][KalaKosha.NAKSHATRA_LORD[moon_nak]],
        "nakshatra_initial": (nak_initials[nak_initial_idx]
                              if nak_initial_idx < len(nak_initials) else ""),
    }

    return {
        "meta": meta,
        "lagna": lagna,
        "moon": moon,
        "planets": planets,
        "houses": houses,
        "vargas": vargas,
        "dashas": dashas,
        "karakas": calculate_karakas(planets, lang),
        "ghatak": calculate_ghatak_chakra(moon_rashi, lang),
    }


# ---------------------------------------------------------------------------
# Chara Karakas + Ghataka Chakra (Jaimini / Muhurta additions)
# ---------------------------------------------------------------------------

# Seven-karaka scheme drops Pitrukaraka (index 4); the eight-karaka scheme
# adds Rahu (counted backward).  Ketu (8) is always excluded.
_KARAKA_SEVEN = [0, 1, 2, 3, 5, 6, 7]
_KARAKA_EIGHT = [0, 1, 2, 3, 4, 5, 6, 7]


def calculate_karakas(planets: dict, lang: str = "en") -> dict:
    """Jaimini Chara Karakas from a natal D1 planet map.

    Every graha is ranked by the degree it has travelled within its sign
    (0..30, sign itself ignored): highest = Atmakaraka, lowest = Darakaraka.
    The eight-karaka scheme includes Rahu with its degree measured backward
    (30° − degree); Ketu never participates.  Both schemes are returned.
    """
    grahas = [p for p in planets.values() if p.get("idx") in _KARAKA_EIGHT]
    grahas.sort(key=lambda p: p["idx"])

    def rank(with_rahu: bool, karaka_idxs):
        cands = []
        for p in grahas:
            if not with_rahu and p["idx"] == 7:
                continue
            deg = p.get("degree_in_sign", 0.0)
            eff = (30.0 - deg) if (with_rahu and p["idx"] == 7) else deg
            cands.append((eff, p))
        # Highest effective degree first; ties resolve toward the natural
        # karaka order (Surya, Chandra, Mangala, Budha, Guru, Sukra, Sani, Rahu).
        cands.sort(key=lambda c: (c[0], -c[1]["idx"]), reverse=True)
        out = []
        for rank_num, (eff, p) in enumerate(cands, start=1):
            k_idx = karaka_idxs[rank_num - 1]
            meanings = KalaKosha.KARAKA_MEANINGS.get(lang) or \
                KalaKosha.KARAKA_MEANINGS["en"]
            via_rahu = with_rahu and p["idx"] == 7
            out.append({
                "rank": rank_num,
                "karaka_idx": k_idx,
                "karaka": KalaKosha.KARAKAS[lang][k_idx],
                "meaning": meanings[k_idx],
                "planet": p["name"],
                "idx": p["idx"],
                "degree_in_sign": round(eff if via_rahu else p.get("degree_in_sign", 0.0), 4),
                "rashi": p["rashi"],
                "rashi_name": p["rashi_name"],
                "nakshatra_name": p["nakshatra_name"],
                "nakshatra_pada": p["nakshatra_pada"],
                "house": p["house"],
                "retrograde": p.get("retrograde", False),
                "via_rahu": via_rahu,
            })
        return out

    return {
        "seven": rank(False, _KARAKA_SEVEN),
        "eight": rank(True, _KARAKA_EIGHT),
        "note": ("Ranked by degree within the sign — highest = Atmakaraka, "
                 "lowest = Darakaraka. The eight-karaka scheme counts Rahu "
                 "backward (30° − degree); Ketu is excluded."),
    }


def calculate_ghatak_chakra(moon_rashi: int, lang: str = "en") -> dict:
    """Ghataka Chakra row for a birth (Moon) rashi.

    Lists the lunar month, tithi group, weekday, nakshatra, nitya yoga,
    karana, prahar and transit-Moon positions that are classically treated as
    inauspicious for starting new undertakings for a native of this rashi.
    """
    row = KalaKosha.GHATA_CHAKRA[moon_rashi % 12]
    cm = (moon_rashi + row["c_male"] - 1) % 12
    cf = (moon_rashi + row["c_female"] - 1) % 12
    return {
        "janma_rashi": KalaKosha.RASIS[lang][moon_rashi % 12],
        "ghat_maas": KalaKosha.MASAS[lang][row["maas"]],
        "ghat_tithis": list(row["tithis"]),
        "ghat_tithis_full": sorted(set(row["tithis"] + [t + 15 for t in row["tithis"]])),
        "ghat_vaara": KalaKosha.VAARAS[lang][row["vaara"]],
        "ghat_nakshatra": KalaKosha.NAKSHATRAS[lang][row["nakshatra"]],
        "ghat_yoga": KalaKosha.YOGAS[lang][row["yoga"]],
        "ghat_karana": KalaKosha.KARANAS[lang][row["karana"]],
        "prahar": row["prahar"],
        "ghat_chandra_male": {"position": row["c_male"],
                              "rashi": KalaKosha.RASIS[lang][cm]},
        "ghat_chandra_female": {"position": row["c_female"],
                                "rashi": KalaKosha.RASIS[lang][cf]},
    }


# ---------------------------------------------------------------------------
# Ashtakoota (Guna Milan)
# ---------------------------------------------------------------------------

def _resolve_person(person: dict, ayanamsa: str = "lahiri") -> dict:
    """Resolve a person dict to {rashi, nak, pada, deg_in_sign}."""
    if "rashi" in person:
        r = {"rashi": person["rashi"]}
        r["nak"] = person.get("nak", person.get("moon_nakshatra", 0))
        r["pada"] = person.get("pada", person.get("moon_pada", 1))
        r["deg_in_sign"] = person.get("deg_in_sign", (person["rashi"] * 30.0 + 15.0) % 30.0)
        return r
    if "moon_rashi" in person:
        r = {"rashi": person["moon_rashi"]}
        r["nak"] = person.get("moon_nakshatra", 0)
        r["pada"] = person.get("moon_pada", 1)
        r["deg_in_sign"] = person.get("deg_in_sign", (person["moon_rashi"] * 30.0 + 15.0) % 30.0)
        return r
    year = person["year"]
    month = person["month"]
    day = person["day"]
    hour = person.get("hour", 12)
    minute = person.get("minute", 0)
    tz = person.get("tz", 5.5)

    tropical = (ayanamsa == "sayana")
    if not tropical:
        set_ayanamsa(ayanamsa)
    jd_ut = swe.julday(year, month, day, (hour + minute / 60.0) - tz)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL if not tropical else swe.FLG_SWIEPH
    if not tropical:
        swe.set_sid_mode(_get_sid_mode())
    res = swe.calc_ut(jd_ut, swe.MOON, flags | swe.FLG_SPEED)
    moon_lon = res[0][0] % 360.0

    rashi = get_rashi(moon_lon)
    nak = get_nakshatra(moon_lon)
    pada = get_nakshatra_pada(moon_lon)
    deg_in_sign = moon_lon - rashi * 30.0
    return {"rashi": rashi, "nak": nak, "pada": pada, "deg_in_sign": deg_in_sign}


def _vashya_category(rashi: int, deg_in_sign: float) -> int:
    cat = KalaKosha.RASHI_VASHYA[rashi]
    if rashi in KalaKosha.VASHYA_SPLIT:
        lo, hi = KalaKosha.VASHYA_SPLIT[rashi]
        cat = lo if deg_in_sign < 15.0 else hi
    return cat


def _relation(a: int, b: int) -> str:
    if b in KalaKosha.GRAHA_FRIENDS.get(a, set()):
        return "friend"
    if b in KalaKosha.GRAHA_ENEMIES.get(a, set()):
        return "enemy"
    return "neutral"


def _mutual_friends(a: int, b: int) -> bool:
    return _relation(a, b) == "friend" and _relation(b, a) == "friend"


def calculate_ashtakoota(bride: dict, groom: dict,
                         ayanamsa: str = "lahiri",
                         lang: str = "en") -> dict:
    """36-point Guna Milan compatibility."""
    bp = _resolve_person(bride, ayanamsa)
    gp = _resolve_person(groom, ayanamsa)

    scores = {}

    # 1. Varna (max 1)
    bride_varna = KalaKosha.RASHI_VARNA[bp["rashi"]]
    groom_varna = KalaKosha.RASHI_VARNA[gp["rashi"]]
    scores["varna"] = KalaKosha.VARNA_SCORE[bride_varna][groom_varna]

    # 2. Vashya (max 2)
    bride_vash = _vashya_category(bp["rashi"], bp["deg_in_sign"])
    groom_vash = _vashya_category(gp["rashi"], gp["deg_in_sign"])
    scores["vashya"] = KalaKosha.VASHYA_SCORE[bride_vash][groom_vash]

    # 3. Tara (max 3)
    c_bg = (gp["nak"] - bp["nak"]) % 27 + 1
    c_gb = (bp["nak"] - gp["nak"]) % 27 + 1
    bride_fav = (c_bg % 9) not in KalaKosha.TARA_MALEFIC
    groom_fav = (c_gb % 9) not in KalaKosha.TARA_MALEFIC
    if bride_fav and groom_fav:
        scores["tara"] = 3.0
    elif bride_fav or groom_fav:
        scores["tara"] = 1.5
    else:
        scores["tara"] = 0.0

    # 4. Yoni (max 4)
    bride_yoni = KalaKosha.NAKSHATRA_YONI[bp["nak"]]
    groom_yoni = KalaKosha.NAKSHATRA_YONI[gp["nak"]]
    if bride_yoni == groom_yoni:
        scores["yoni"] = 4
    elif (bride_yoni, groom_yoni) in KalaKosha.YONI_BITTER_ENEMY or \
         (groom_yoni, bride_yoni) in KalaKosha.YONI_BITTER_ENEMY:
        scores["yoni"] = 0
    elif (bride_yoni, groom_yoni) in KalaKosha.YONI_MILD_ENEMY or \
         (groom_yoni, bride_yoni) in KalaKosha.YONI_MILD_ENEMY:
        scores["yoni"] = 1
    elif (bride_yoni, groom_yoni) in KalaKosha.YONI_FRIEND_PAIRS or \
         (groom_yoni, bride_yoni) in KalaKosha.YONI_FRIEND_PAIRS:
        scores["yoni"] = 3
    else:
        scores["yoni"] = 2

    # 5. Graha Maitri (max 5)
    bride_lord = KalaKosha.RASHI_LORD[bp["rashi"]]
    groom_lord = KalaKosha.RASHI_LORD[gp["rashi"]]
    if bride_lord == groom_lord:
        scores["graha_maitri"] = 5
    elif _mutual_friends(bride_lord, groom_lord):
        scores["graha_maitri"] = 5
    elif _relation(bride_lord, groom_lord) == "friend":
        scores["graha_maitri"] = 4
    elif _relation(bride_lord, groom_lord) == "neutral" and \
         _relation(groom_lord, bride_lord) == "neutral":
        scores["graha_maitri"] = 3
    elif _relation(bride_lord, groom_lord) == "friend" and \
         _relation(groom_lord, bride_lord) == "enemy":
        scores["graha_maitri"] = 1
    elif _relation(bride_lord, groom_lord) == "neutral" and \
         _relation(groom_lord, bride_lord) == "enemy":
        scores["graha_maitri"] = 0.5
    elif _relation(bride_lord, groom_lord) == "enemy" and \
         _relation(groom_lord, bride_lord) == "enemy":
        scores["graha_maitri"] = 0
    else:
        scores["graha_maitri"] = 2

    # 6. Gana (max 6)
    bride_gana = KalaKosha.NAKSHATRA_GANA[bp["nak"]]
    groom_gana = KalaKosha.NAKSHATRA_GANA[gp["nak"]]
    scores["gana"] = KalaKosha.GANA_SCORE[bride_gana][groom_gana]

    # 7. Bhakoot (max 7)
    dist = (gp["rashi"] - bp["rashi"]) % 12
    bhakoot_dosha = dist in KalaKosha.BHAKOOT_BAD_DIST
    bhakoot_cancelled = _mutual_friends(bride_lord, groom_lord)
    scores["bhakoot"] = 7 if (not bhakoot_dosha or bhakoot_cancelled) else 0

    # 8. Nadi (max 8)
    bride_nadi = KalaKosha.NAKSHATRA_NADI[bp["nak"]]
    groom_nadi = KalaKosha.NAKSHATRA_NADI[gp["nak"]]
    nadi_dosha = bride_nadi == groom_nadi
    nadi_cancelled = (bp["rashi"] != gp["rashi"] or bp["nak"] != gp["nak"])
    nadi_cancelled = nadi_cancelled or (bride_lord == groom_lord)
    scores["nadi"] = 8 if (not nadi_dosha or nadi_cancelled) else 0

    total = sum(scores.values())

    if total >= 33:
        verdict_idx = 0
    elif total >= 25:
        verdict_idx = 1
    elif total >= 18:
        verdict_idx = 2
    else:
        verdict_idx = 3

    verdict = KalaKosha.VERDICT_NAMES[lang][verdict_idx]

    return {
        "scores": scores,
        "total": total,
        "verdict": verdict,
        "bride": bp,
        "groom": gp,
        "nadi_dosha": nadi_dosha,
        "nadi_dosha_cancelled": nadi_dosha and nadi_cancelled,
        "bhakoot_dosha": bhakoot_dosha,
        "bhakoot_dosha_cancelled": bhakoot_dosha and bhakoot_cancelled,
    }


# ---------------------------------------------------------------------------
# Analysis (rule-based chart highlights)
# ---------------------------------------------------------------------------

def generate_analysis(kundali: dict, lang: str = "en") -> dict:
    """Offline rule-based chart analysis (no external services)."""
    highlights = []
    planets = kundali["planets"]
    lagna = kundali["lagna"]

    # Lagna lord placement
    lagna_lord_idx = lagna["lord_idx"]
    for pname, pdata in planets.items():
        if pdata["idx"] == lagna_lord_idx:
            house = pdata["house"]
            if house in (1, 4, 7, 10):
                highlights.append(f"Lagna lord {pname} in {house}th house (strong)")
            elif house in (6, 8, 12):
                highlights.append(f"Lagna lord {pname} in {house}th house (challenging)")
            break

    # Mangal Dosha check
    mangal_house = planets.get("Mangala", {}).get("house")
    if mangal_house in (1, 2, 4, 7, 8, 12):
        highlights.append("Mangal Dosha present")

    # Combust planets
    for pname, pdata in planets.items():
        if pdata["combust"]:
            highlights.append(f"{pname} is combust (near Sun)")

    # Retrograde planets
    for pname, pdata in planets.items():
        if pdata["retrograde"]:
            highlights.append(f"{pname} is retrograde (Vakri)")

    # Navamsa Moon dignity
    if "D9" in kundali.get("vargas", {}):
        d9_planets = kundali["vargas"]["D9"].get("planets", {})
        moon_d9 = d9_planets.get("Chandra", {})
        if "rashi" in moon_d9:
            d9_lord = KalaKosha.RASHI_LORD[moon_d9["rashi"]]
            d9_lord_name = KalaKosha.GRAHAS[lang][d9_lord]
            highlights.append(f"Navamsa Moon lord: {d9_lord_name}")

    return {"kundali": kundali, "highlights": highlights}


# ---------------------------------------------------------------------------
# Detailed Panchanga (panchanga + sunrise grahas + horas + muhurtas)
# ---------------------------------------------------------------------------

def calculate_detailed_panchanga(year: int, month: int, day: int, tz: float,
                                 lat: float, lon: float, alt: float,
                                 ayanamsa: str = "lahiri",
                                 lang: str = "en") -> dict:
    """Full daily panchanga with sunrise planet positions, horas, muhurtas."""
    pc = calculate_panchanga(year, month, day, tz, lat, lon, alt, lang=lang)

    jd_ut_start = swe.julday(year, month, day, -tz)
    sunrise_jd = pc["sunrise_jd"]

    ayan_val = get_ayanamsa_value(sunrise_jd) if ayanamsa != "sayana" else 0.0
    tropical = (ayanamsa == "sayana")
    details = _get_planetary_details(sunrise_jd, tropical)

    grahas = []
    for idx in range(9):
        plon, retro, speed = details[idx]
        rashi = get_rashi(plon)
        nak = get_nakshatra(plon)
        pada = get_nakshatra_pada(plon)
        deg_in_sign = plon - rashi * 30.0
        dignity_label, dignity_code = _planet_dignity(idx, rashi, lang)
        grahas.append({
            "idx": idx,
            "name": KalaKosha.GRAHAS[lang][idx],
            "longitude": round(plon, 4),
            "degree_in_sign": round(deg_in_sign, 4),
            "rashi": rashi,
            "rashi_name": KalaKosha.RASIS[lang][rashi],
            "nakshatra": nak,
            "nakshatra_name": KalaKosha.NAKSHATRAS[lang][nak],
            "nakshatra_pada": pada,
            "retrograde": retro,
            "dignity": dignity_code,
        })

    horas = calculate_dina_horas(year, month, day, tz, lat, lon, alt, lang)
    muhurtas = calculate_muhurtas(year, month, day, tz, lat, lon, alt, lang)

    pc["grahas"] = grahas
    pc["day_horas"] = horas["day_horas"]
    pc["night_horas"] = horas["night_horas"]
    pc["day_muhurtas"] = muhurtas["day_muhurtas"]
    pc["night_muhurtas"] = muhurtas["night_muhurtas"]

    return pc


# ---------------------------------------------------------------------------
# Gochara — planetary transit engine (Phase 12)
# ---------------------------------------------------------------------------

# Transit-house aspects for the slow grahas (Brihat Parashara Hora Shastra):
# index -> set of house offsets (1-based houses, 12 = 12th) aspected from the
# sign a graha currently transits.
_TRANSIT_ASPECTS = {
    6: {3, 7, 10},   # Shani: 3rd, 7th, 10th from its own transit sign
    4: {5, 7, 9},    # Guru:  5th, 7th, 9th from its transit sign
    2: {4, 7, 8},    # Mangala: 4th, 7th, 8th from its transit sign
}


def _transit_house_from_aspect(transit_rashi: int, aspected_offset: int) -> int:
    """House number (1-12) that the aspect offset reaches from the transiting rashi."""
    return ((transit_rashi + aspected_offset - 1) % 12) + 1


def calculate_gochara(birth_data: dict, year: int, month: int, day: int,
                      hour: float = 12.0, minute: float = 0.0,
                      tz: float = 5.5, lat: float = 23.1765, lon: float = 75.7885,
                      lang: str = "en", ayanamsa: str = "lahiri") -> dict:
    """Compute the Gochara (planetary transit) chart for a birth chart.

    `birth_data` must be the output of `calculate_kundali` (with a valid
    `lagna.rashi`, `planets`, and `houses`). Returns the current transit
    positions of all nine grahas, their transit houses relative to the birth
    lagna, special transit yogas (Sade Sati, Ashtama Shani, Vakra/Return,
    panchanga-aware transit classification), and the next sign-ingress edges.

    The `ayanamsa` argument must match the frame that `birth_data` was computed
    in — for a sidereal (Lahiri etc.) chart pass the same mode; for a Sayana
    chart pass ``"sayana"``.
    """
    tropical = (ayanamsa == "sayana")
    prev_mode = get_ayanamsa_mode()
    try:
        set_ayanamsa(ayanamsa) if not tropical else None
        jd_ut = swe.julday(year, month, day, (hour + minute / 60.0) - tz)

        # ---- Current transit longitudes ----
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        if not tropical:
            swe.set_sid_mode(_get_sid_mode())
            flags |= swe.FLG_SIDEREAL
        transit_lon = {}
        for idx in range(8):
            res = swe.calc_ut(jd_ut, _PLANET_SWE_IDS[idx], flags)
            transit_lon[idx] = res[0][0] % 360.0
        transit_lon[8] = (transit_lon[7] + 180.0) % 360.0

        # ---- Natal lagna rashi & natal positions ----
        natal_lagna_rashi = birth_data.get("lagna", {}).get("rashi")
        natal_planets = birth_data.get("planets", {})

        # Build a lookup from graha idx (0-8) -> natal rashi
        natal_rashi_by_idx = {}
        for gname, pdata in natal_planets.items():
            rashi = pdata.get("rashi")
            if rashi is None:
                continue
            idx = pdata.get("idx")
            if idx is None:
                continue
            natal_rashi_by_idx[idx] = rashi

        # ---- Per-graha transit record ----
        grahas = []
        for idx in range(9):
            tlon = transit_lon[idx]
            trashi = get_rashi(tlon)
            nak = get_nakshatra(tlon)
            pada = get_nakshatra_pada(tlon)
            deg_in_sign = tlon - trashi * 30.0
            speed = 0.0
            if idx < 8:
                speed = swe.calc_ut(jd_ut, _PLANET_SWE_IDS[idx], flags)[0][3]
            retro = (idx == 7) or (idx == 8) or (speed < 0)
            dignity_label, dignity_code = _planet_dignity(idx, trashi, lang)

            # If natal lagna is available we can report house(s) the transit
            # graha occupies or aspects (from its transit rashi).
            t_house = None
            aspects = []
            if natal_lagna_rashi is not None:
                t_house = ((trashi - natal_lagna_rashi) % 12) + 1
                for offset in _TRANSIT_ASPECTS.get(idx, set()):
                    aspects.append(_transit_house_from_aspect(trashi, offset))

            natal_rashi = natal_rashi_by_idx.get(idx)
            grahas.append({
                "idx": idx,
                "name": KalaKosha.GRAHAS[lang][idx],
                "longitude": round(tlon, 4),
                "degree_in_sign": round(deg_in_sign, 4),
                "rashi": trashi,
                "rashi_name": KalaKosha.RASIS[lang][trashi],
                "nakshatra": nak,
                "nakshatra_name": KalaKosha.NAKSHATRAS[lang][nak],
                "nakshatra_pada": pada,
                "retrograde": retro,
                "dignity": dignity_label,
                "dignity_code": dignity_code,
                "house": t_house,
                "aspects_house": aspects,
            })

        # ---- Special transit yogas ----
        yogas = []
        if natal_lagna_rashi is not None:
            moon_rashi = natal_rashi_by_idx.get(1)
            saturn_rashi = natal_rashi_by_idx.get(6)
            jupiter_rashi = natal_rashi_by_idx.get(4)
            t_saturn_idx = transit_lon[6]
            t_jupiter_idx = transit_lon[4]

            transit_saturn_rashi = get_rashi(t_saturn_idx)
            transit_jupiter_rashi = get_rashi(t_jupiter_idx)

            if moon_rashi is not None:
                moon_to_saturn = (transit_saturn_rashi - moon_rashi) % 12
                # Sade Sati: Shani in 12th, 1st, or 2nd from natal Moon
                if moon_to_saturn in (11, 0, 1):
                    phase = {11: "Vidhya (12th)", 0: "Peeda (1st)", 1: "Adha (2nd)"}[moon_to_saturn]
                    yogas.append({
                        "name": "Sade Sati",
                        "severity": "high",
                        "description": f"Shani transiting {KalaKosha.RASIS[lang][transit_saturn_rashi]}, which is {phase} from natal Chandra ({KalaKosha.RASIS[lang][moon_rashi]}).",
                    })
                elif moon_to_saturn == 7:
                    yogas.append({
                        "name": "Ashtama Shani",
                        "severity": "medium",
                        "description": f"Shani transiting {KalaKosha.RASIS[lang][transit_saturn_rashi]}, the 8th from natal Chandra.",
                    })
                elif moon_to_saturn == 3:
                    yogas.append({
                        "name": "Shani Dasama / Kanta Shani",
                        "severity": "low",
                        "description": f"Shani transiting the 4th from natal Chandra ({KalaKosha.RASIS[lang][transit_saturn_rashi]}).",
                    })

            if jupiter_rashi is not None:
                gopuram = (transit_jupiter_rashi - jupiter_rashi) % 12
                yogas.append({
                    "name": "Guru Gochara",
                    "severity": "medium",
                    "description": f"Guru ({KalaKosha.RASIS[lang][transit_jupiter_rashi]}) is {abs(gopuram) if gopuram <= 6 else 12 - gopuram} house(s) from its natal position ({KalaKosha.RASIS[lang][jupiter_rashi]}).",
                })

            # Guru from natal lagna (general benefic transit)
            guru_house_from_lagna = ((get_rashi(t_jupiter_idx) - natal_lagna_rashi) % 12) + 1
            yogas.append({
                "name": "Guru Transit",
                "severity": "low",
                "description": f"Guru transits house {guru_house_from_lagna} from natal Lagna.",
            })

        # Budha-Aditya Yoga: a Yuti (same-rashi conjunction, matching the
        # natal conjunction doctrine) of Surya and Budha in the transit chart.
        sun_rashi = get_rashi(transit_lon[0])
        budha_rashi = get_rashi(transit_lon[3])
        budha_sun_sep = abs((transit_lon[3] - transit_lon[0]) % 360.0)
        if budha_sun_sep > 180.0:
            budha_sun_sep = 360.0 - budha_sun_sep
        if budha_rashi == sun_rashi:
            yogas.append({
                "name": "Budha-Aditya Yoga",
                "severity": "low",
                "description": (
                    f"Surya and Budha are in a Yuti in {KalaKosha.RASIS[lang][sun_rashi]} "
                    f"(angular separation {budha_sun_sep:.1f}\u00B0) — a favourable yoga "
                    "bestowing sharp intellect, eloquence and quick grasping power."
                ),
            })

        # ---- Next sign ingress (transit edges) ----
        # Report each graha's next rashi change (forward or via retrograde
        # station), listed chronologically.  Surya and fast-moving Budha are
        # included; Chandra flips every ~2.3 days and would drown the list.
        edges = []

        def _rashi_at(jd):
            res = swe.calc_ut(jd, _PLANET_SWE_IDS[idx], flags)
            return get_rashi(res[0][0] % 360.0)

        for idx in (0, 2, 3, 4, 5, 6, 7):
            tlon = transit_lon[idx]
            cur_rashi = get_rashi(tlon)
            max_days = 1000.0
            found_jd = find_transition(jd_ut, _rashi_at, max_days=max_days, step_days=0.5)
            if found_jd is not None:
                new_rashi = get_rashi(swe.calc_ut(found_jd, _PLANET_SWE_IDS[idx], flags)[0][0] % 360.0)
                edge = {
                    "graha": KalaKosha.GRAHAS[lang][idx],
                    "from_rashi": KalaKosha.RASIS[lang][cur_rashi],
                    "to_rashi": KalaKosha.RASIS[lang][new_rashi],
                    "date": KalaVartika.format_datetime(found_jd, tz),
                }
                edges.append((found_jd, edge))

        edges.sort(key=lambda item: item[0])
        edges = [e for _, e in edges]

        result = {
            "date": f"{day:02d}-{month:02d}-{year:04d}",
            "jd_ut": round(jd_ut, 6),
            "ayanamsa": "sayana" if tropical else ayanamsa,
            "transits": grahas,
            "special_yogas": yogas,
            "next_sign_changes": edges,
        }

        # If we have a natal chart, also report which current transits fall
        # within a 1-degree orb of a natal planet (MU / Ashtakavarga-style).
        if natal_planets:
            conjunctions = []
            for idx in range(9):
                t_lon = transit_lon[idx]
                # skip Moon (fast) — orb only meaningful for slow bodies
                if idx == 1:
                    continue
                for gname, pdata in natal_planets.items():
                    n_lon = pdata.get("longitude")
                    if n_lon is None:
                        continue
                    diff = abs((t_lon - n_lon) % 360.0)
                    if diff > 180.0:
                        diff = 360.0 - diff
                    if diff <= 1.0:
                        conjunctions.append({
                            "transit": KalaKosha.GRAHAS[lang][idx],
                            "natal": gname,
                            "orb": round(diff, 2),
                        })
            result["transit_conjunctions"] = conjunctions

        return result
    finally:
        set_ayanamsa(prev_mode)


# Alias matching the classical spelling.
calculate_gocara = calculate_gochara
