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
def _harmonic_varga_sign(longitude: float, divisor: int) -> int:
    """Continuous-harmonic varga sign (standard for D2, D4, D7, …).

    Note: D3 (drekkana) and D9 (navamsa) have their own classical rules;
    this function should NOT be used for them.
    """
    sign = rashi_index(longitude)
    offset = longitude - sign * 30.0
    part = min(divisor - 1, int(offset * divisor / 30.0))
    return (sign * divisor + part) % 12


def drekkana_sign(longitude: float) -> int:
    """Classical Parasari D3 (Drekkana) sign, 0–11."""
    sign = rashi_index(longitude)
    offset = longitude - sign * 30.0
    third = min(2, int(offset * 3.0 / 30.0))
    sequence = [
        (0, 4, 8),   # movable signs: Me/Vri/Mith/Scl/Dha/Aqr
        (8, 0, 4),   # fixed signs:   Tau/Leo/Sco/Cap
        (4, 8, 0),   # dual signs:    Gem/Lib/Aqu/Pis
    ]
    return (sign + sequence[sign % 3][third]) % 12


def navamsa_sign(longitude: float) -> int:
    """Continuous 9-fold D9 (Navamsa) sign, 0–11."""
    sign = rashi_index(longitude)
    offset = longitude - sign * 30.0
    part = min(8, int(offset * 9.0 / 30.0))
    return (sign * 9 + part) % 12


def varga_sign(longitude: float, divisor: int) -> int:
    """Dispatcher: correct sign for a given varga divisor (D1–D60).

    D1 → rashi, D3 → drekkana, D9 → navamsa; all others → harmonic.
    """
    if divisor == 1:
        return rashi_index(longitude)
    if divisor == 3:
        return drekkana_sign(longitude)
    if divisor == 9:
        return navamsa_sign(longitude)
    return _harmonic_varga_sign(longitude, divisor)


def varga_degree(longitude: float, divisor: int) -> float:
    """Degrees elapsed within the varga rashi (0.0–29.999…)."""
    if divisor == 1:
        return longitude % 30.0
    if divisor == 3:
        return (longitude % 10.0) * 3.0
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
