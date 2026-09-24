# -*- coding: utf-8 -*-
"""
KalaVartika — pure time, calendar, and longitude-index utilities.

This module contains zero Swiss Ephemeris calls.  Every function operates on
raw numeric inputs (Julian Days, ecliptic longitudes, year numbers) so it
is testable and reusable without any ephemeris backend.
"""

import math
import datetime as _dt
import datetime as _dt

# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------
NAKSHATRA_SPAN = 360.0 / 27.0  # ≈ 13.3333°
YOGA_SPAN = 360.0 / 27.0
_KARANA_SPAN = 6.0
_TITHI_SPAN = 12.0
_YEAR_DAYS = 365.2425  # Gregorian (Julian) average year


# ---------------------------------------------------------------------------
#  Rashi / Nakshatra / Pada helpers (from ecliptic longitude)
# ---------------------------------------------------------------------------
def rashi_index(longitude: float) -> int:
    """Return 0–11 rashi index from sidereal longitude."""
    return int(longitude / 30.0) % 12


def rashi_longitude(longitude: float) -> float:
    """Degrees elapsed within the current rashi (0.0–29.999…)."""
    return longitude - rashi_index(longitude) * 30.0


def nakshatra_index(longitude: float) -> int:
    """Return 0–26 nakshatra index from sidereal longitude."""
    return int(longitude / NAKSHATRA_SPAN) % 27


def nakshatra_pada(longitude: float) -> int:
    """Pada 1–4 within the current nakshatra."""
    return int((longitude % NAKSHATRA_SPAN) / (NAKSHATRA_SPAN / 4.0)) + 1


def nakshatra_lagna_pada(longitude: float) -> int:
    """Pada 0–3 within the current nakshatra (0-based, used for lagna)."""
    return int((longitude % NAKSHATRA_SPAN) / (NAKSHATRA_SPAN / 4.0))


# ---------------------------------------------------------------------------
#  Tithi / Yoga / Karana indices (from Moon and Sun longitudes)
# ---------------------------------------------------------------------------
def tithi_index(moon_lon: float, sun_lon: float) -> int:
    """Tithi index 0–29 from sidereal Moon and Sun longitudes."""
    return int(((moon_lon - sun_lon) % 360.0) / _TITHI_SPAN) % 30


def tithi_value(moon_lon: float, sun_lon: float) -> float:
    """Continuous tithi value (0.0–29.999…) for interpolation."""
    return ((moon_lon - sun_lon) % 360.0) / _TITHI_SPAN


def yoga_index(moon_lon: float, sun_lon: float) -> int:
    """Yoga index 0–26 from sidereal Moon and Sun longitudes."""
    return int(((moon_lon + sun_lon) % 360.0) / YOGA_SPAN) % 27


def karana_index(moon_lon: float, sun_lon: float) -> int:
    """Karana index 0–57 from sidereal Moon and Sun longitudes."""
    return int(((moon_lon - sun_lon) % 360.0) / _KARANA_SPAN)


# ---------------------------------------------------------------------------
#  Varga sign computations
# ---------------------------------------------------------------------------
# Classical Parāśara vargā (matching Jagannatha Hora / PyJHora non-cyclic
# vargas).  A pure continuous-harmonic mapping (sign*divisor + part % 12) is
# correct ONLY for the divisions whose classical rule coincides with it
# (D7, D8, D11, D16, D20, D27); the other divisions use either element-based
# placements or even-sign reversal.

_ODD_SIGNS  = (0, 2, 4, 6, 8, 10)   # counted from Aries
_EVEN_SIGNS = (1, 3, 5, 7, 9, 11)
_FIXED_SIGNS = (1, 4, 7, 10)        # Taurus, Leo, Scorpio, Aquarius
_DUAL_SIGNS  = (2, 5, 8, 11)        # Gemini, Virgo, Sagittarius, Pisces


def _varga_part(longitude: float, divisor: int) -> int:
    """0-based varga part index within the rashi (clamped to divisor−1)."""
    sign = rashi_index(longitude)
    offset = longitude - sign * 30.0
    return min(divisor - 1, int(offset * divisor / 30.0))


def _harmonic_varga_sign(longitude: float, divisor: int) -> int:
    """Continuous-harmonic varga sign.

    Matches the classical Parāśara rule only for D7, D8, D11, D16, D20 and
    D27; do NOT use it for other divisions.
    """
    sign = rashi_index(longitude)
    offset = longitude - sign * 30.0
    part = min(divisor - 1, int(offset * divisor / 30.0))
    return (sign * divisor + part) % 12


def _hora_sign(longitude: float) -> int:
    """Classical Parasari D2 (Hora): savya-apasavya parivritti, even signs reversed."""
    sign = rashi_index(longitude)
    offset = longitude - sign * 30.0
    part = _varga_part(longitude, 2)
    if sign % 2 == 0:
        return (sign * 2 + part) % 12
    return (sign * 2 + 1 - part) % 12


def _chaturthamsa_sign(longitude: float) -> int:
    """Classical Parasari D4 (Chaturthamsa): 4 parts move +0/+3/+6/+9 from the sign."""
    sign = rashi_index(longitude)
    part = _varga_part(longitude, 4)
    return (sign + 3 * part) % 12


def _dasamsa_sign(longitude: float) -> int:
    """Classical Parasari D10 (Dasamsa): odd signs forward, even signs from the 9th."""
    sign = rashi_index(longitude)
    part = _varga_part(longitude, 10)
    if sign in _EVEN_SIGNS:
        return (sign + 8 + part) % 12
    return (sign + part) % 12


def _dwadasamsa_sign(longitude: float) -> int:
    """Classical Parasari D12 (Dvadasamsa): 12 parts counted from the sign itself."""
    sign = rashi_index(longitude)
    part = _varga_part(longitude, 12)
    return (sign + part) % 12


def _siddhamsa_sign(longitude: float) -> int:
    """Classical Parasari D24 (Siddhamsa): odd signs from Leo, even signs from Cancer."""
    sign = rashi_index(longitude)
    part = _varga_part(longitude, 24)
    base = 3 if sign in _EVEN_SIGNS else 4
    return (base + part) % 12


def _trimsamsa_sign(longitude: float) -> int:
    """Classical Parasari D30 (Trimsamsa): unequal 5/5/8/7/5 degree arcs."""
    sign = rashi_index(longitude)
    offset = longitude - sign * 30.0
    if sign in _ODD_SIGNS:
        arcs = [(0, 5, 0), (5, 10, 10), (10, 18, 8), (18, 25, 2), (25, 30, 6)]
    else:
        arcs = [(0, 5, 1), (5, 12, 5), (12, 20, 11), (20, 25, 9), (25, 30, 7)]
    for lo, hi, rasi in arcs:
        if lo <= offset < hi:
            return rasi % 12
    return 0


def _khavedamsa_sign(longitude: float) -> int:
    """Classical Parasari D40 (Khavedamsa): odd signs from Aries, even signs from Libra."""
    sign = rashi_index(longitude)
    part = _varga_part(longitude, 40)
    if sign in _EVEN_SIGNS:
        return (part + 6) % 12
    return part % 12


def _akshavedamsa_sign(longitude: float) -> int:
    """Classical Parasari D45 (Akshavedamsa): self/5th/9th anchored element parts."""
    sign = rashi_index(longitude)
    part = _varga_part(longitude, 45)
    if sign in _DUAL_SIGNS:
        return (part + 8) % 12
    if sign in _FIXED_SIGNS:
        return (part + 4) % 12
    return part % 12


def _shashtyamsa_sign(longitude: float) -> int:
    """Classical Parasari D60 (Shashtyamsa): 60 parts counted from the sign itself."""
    sign = rashi_index(longitude)
    part = _varga_part(longitude, 60)
    return (sign + part) % 12


def drekkana_sign(longitude: float) -> int:
    """Classical Parasari D3 (Drekkana): count the drekkana from the rashi itself."""
    sign = rashi_index(longitude)
    part = _varga_part(longitude, 3)
    return (sign + part * 4) % 12


def navamsa_sign(longitude: float) -> int:
    """Continuous 9-fold D9 (Navamsa) sign, 0–11."""
    sign = rashi_index(longitude)
    offset = longitude - sign * 30.0
    part = min(8, int(offset * 9.0 / 30.0))
    return (sign * 9 + part) % 12


def varga_sign(longitude: float, divisor: int) -> int:
    """Dispatcher: classical Parasari sign for a given varga divisor (D1–D60)."""
    if divisor == 1:
        return rashi_index(longitude)
    if divisor == 2:
        return _hora_sign(longitude)
    if divisor == 3:
        return drekkana_sign(longitude)
    if divisor == 4:
        return _chaturthamsa_sign(longitude)
    if divisor == 9:
        return navamsa_sign(longitude)
    if divisor == 10:
        return _dasamsa_sign(longitude)
    if divisor == 12:
        return _dwadasamsa_sign(longitude)
    if divisor == 24:
        return _siddhamsa_sign(longitude)
    if divisor == 30:
        return _trimsamsa_sign(longitude)
    if divisor == 40:
        return _khavedamsa_sign(longitude)
    if divisor == 45:
        return _akshavedamsa_sign(longitude)
    if divisor == 60:
        return _shashtyamsa_sign(longitude)
    return _harmonic_varga_sign(longitude, divisor)


def varga_degree(longitude: float, divisor: int) -> float:
    """Degrees elapsed within the varga rashi (0.0–29.999…)."""
    if divisor == 1:
        return longitude % 30.0
    if divisor == 3:
        return (longitude % 10.0) * 3.0
    if divisor == 2 and rashi_index(longitude) in _EVEN_SIGNS:
        return (30.0 - (longitude * divisor) % 30.0) % 30.0
    return (longitude * divisor) % 30.0


# ---------------------------------------------------------------------------
#  Era arithmetic (pure year-number functions)
# ---------------------------------------------------------------------------
def shaka_year(gregorian_year: int, is_after_chaitra_pratipada: bool) -> int:
    """Shaka era year from Gregorian year."""
    return gregorian_year - 78 if is_after_chaitra_pratipada else gregorian_year - 79


def vikram_year(gregorian_year: int, is_after_chaitra_pratipada: bool) -> int:
    """Vikram (Vikramādiptya) era year from Gregorian year."""
    return gregorian_year + 57 if is_after_chaitra_pratipada else gregorian_year + 56


def kali_year(shaka_yr: int) -> int:
    """Kali era year from Shaka year."""
    return shaka_yr + 3180


def samvatsara_idx_vikram(vikram_yr: int) -> int:
    """Samvatsara index (0–59) for the Vikram era year."""
    return (vikram_yr - 4) % 60


def samvatsara_idx_shaka(shaka_yr: int) -> int:
    """Samvatsara index (0–59) for the Shaka era year."""
    return (shaka_yr + 11) % 60


# ---------------------------------------------------------------------------
#  Ritu and Ayana
# ---------------------------------------------------------------------------
_RITUS = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

def ritu_from_tithi_idx(tithi_idx: int) -> int:
    """Ritu index 0–5 from lunar tithi index (0–29)."""
    return (tithi_idx // 2) % 6


def ritu_from_rashi(rashi_idx: int) -> int:
    """Ritu index 0–5 from solar (saura) rashi."""
    return (rashi_idx // 2) % 6


def ayana_from_rashi(rashi_idx: int) -> int:
    """Ayana index: 0 = Uttarayana, 1 = Dakshinayana."""
    return 1 if 3 <= rashi_idx <= 8 else 0


# ---------------------------------------------------------------------------
#  Time formatting
# ---------------------------------------------------------------------------
def _jd_to_local_dt(jd: float, tz: float) -> _dt.datetime:
    """Julian Day → naive local-time datetime."""
    return _dt.datetime(1970, 1, 1) + _dt.timedelta(days=jd + tz / 24.0 - 2440587.5)


def format_time_hhmm(jd: float, tz: float, jd_ut_start: float) -> str:
    """JD → local HH:MM string.

    Times past the Gregorian midnight boundary of *jd_ut_start* are shown
    in 24+h style (e.g. 31:09).
    """
    local = _jd_to_local_dt(jd, tz)
    start = _jd_to_local_dt(jd_ut_start, tz)
    days_diff = (local.date() - start.date()).days
    h_dec = local.hour + local.minute / 60.0 + local.second / 3600.0
    h = int(h_dec)
    mins = int(round((h_dec - h) * 60.0))
    if mins == 60:
        h += 1
        mins = 0
    if days_diff > 0:
        h += 24 * days_diff
    elif days_diff < 0 and h < 12:
        h += 24
    return f"{h:02d}:{mins:02d}"


def format_datetime(jd: float, tz: float) -> str:
    """JD → local 'DD-MM-YYYY HH:MM' string."""
    local = _jd_to_local_dt(jd, tz)
    h_dec = local.hour + local.minute / 60.0 + local.second / 3600.0
    h = int(h_dec)
    mins = int(round((h_dec - h) * 60.0))
    if mins == 60:
        h += 1
        mins = 0
    return f"{local.day:02d}-{local.month:02d}-{local.year:04d} {h:02d}:{mins:02d}"
