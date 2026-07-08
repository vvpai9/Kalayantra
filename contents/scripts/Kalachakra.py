#!/usr/bin/env python3
"""
Kalachakra - Pure Astronomical Calculation Engine
Responsible ONLY for astronomical computations and raw panchanga parameters.
Does NOT compute festivals or ritual events.
"""
import datetime
# pyrefly: ignore [missing-import]
import swisseph as swe
import Kalakosha

def find_transition(jd_start, get_index_func, max_days=1.2, step_days=0.05):
    start_idx = get_index_func(jd_start)
    jd_low = jd_start
    jd_high = None
    t = jd_start
    limit = jd_start + max_days
    
    while t < limit:
        t += step_days
        if get_index_func(t) != start_idx:
            jd_high = t
            break
        jd_low = t
        
    if jd_high is None:
        return None
        
    for _ in range(20):
        mid = (jd_low + jd_high) / 2.0
        if get_index_func(mid) == start_idx:
            jd_low = mid
        else:
            jd_high = mid
            
    return (jd_low + jd_high) / 2.0


def get_sidereal_longitudes(jd_ut):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    res_sun, _ = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    sun_long = res_sun[0]
    res_moon, _ = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    moon_long = res_moon[0]
    return sun_long, moon_long


def find_previous_conjunction(jd_ut):
    t = jd_ut
    sun_l, moon_l = get_sidereal_longitudes(t)
    diff = (moon_l - sun_l) % 360
    
    prev_t = t
    prev_diff = diff
    for _ in range(20):
        t -= 2.0
        sun_l, moon_l = get_sidereal_longitudes(t)
        curr_diff = (moon_l - sun_l) % 360
        if curr_diff > prev_diff:
            low = t
            high = prev_t
            for _ in range(30):
                mid = (low + high) / 2.0
                s_l, m_l = get_sidereal_longitudes(mid)
                d = (m_l - s_l) % 360
                if d > 180:
                    low = mid
                else:
                    high = mid
            return (low + high) / 2.0
        prev_t = t
        prev_diff = curr_diff
    return jd_ut - 29.53


def find_next_conjunction(jd_ut):
    t = jd_ut
    sun_l, moon_l = get_sidereal_longitudes(t)
    diff = (moon_l - sun_l) % 360
    
    prev_t = t
    prev_diff = diff
    for _ in range(20):
        t += 2.0
        sun_l, moon_l = get_sidereal_longitudes(t)
        curr_diff = (moon_l - sun_l) % 360
        if curr_diff < prev_diff:
            low = prev_t
            high = t
            for _ in range(30):
                mid = (low + high) / 2.0
                s_l, m_l = get_sidereal_longitudes(mid)
                d = (m_l - s_l) % 360
                if d > 180:
                    low = mid
                else:
                    high = mid
            return (low + high) / 2.0
        prev_t = t
        prev_diff = curr_diff
    return jd_ut + 29.53


def get_lunar_month_details(jd_ut, month_system="amavasyanta"):
    jd_prev_conj = find_previous_conjunction(jd_ut)
    jd_next_conj = find_next_conjunction(jd_ut)
    
    sun_l_prev, _ = get_sidereal_longitudes(jd_prev_conj)
    rashi_prev = int(sun_l_prev / 30.0)
    
    sun_l_next, _ = get_sidereal_longitudes(jd_next_conj)
    rashi_next = int(sun_l_next / 30.0)
    
    is_adhika = (rashi_prev == rashi_next)
    masa_idx = (rashi_prev + 1) % 12
    
    sun_l, moon_l = get_sidereal_longitudes(jd_ut)
    tithi_val = ((moon_l - sun_l) % 360) / 12.0
    tithi_idx = int(tithi_val)
    is_krishna = (tithi_idx >= 15)
    
    purnimanta_masa_idx = masa_idx
    if month_system == "purnimanta" and not is_adhika and is_krishna:
        purnimanta_masa_idx = (masa_idx + 1) % 12
        
    actual_masa_idx = purnimanta_masa_idx if month_system == "purnimanta" else masa_idx
    
    return actual_masa_idx, is_adhika, is_krishna, tithi_idx, tithi_val


def get_chaitra_pratipada_jd(year):
    jd_start = swe.julday(year, 3, 1, 0.0)
    t = jd_start
    for _ in range(30):
        jd_conj = find_next_conjunction(t)
        sun_l, _ = get_sidereal_longitudes(jd_conj)
        rashi = int(sun_l / 30.0)
        if rashi == 11:
            return jd_conj
        t = jd_conj + 2.0
    return jd_start


def get_kartika_pratipada_jd(year):
    jd_start = swe.julday(year, 10, 1, 0.0)
    t = jd_start
    for _ in range(30):
        jd_conj = find_next_conjunction(t)
        sun_l, _ = get_sidereal_longitudes(jd_conj)
        rashi = int(sun_l / 30.0)
        if rashi == 6:
            return jd_conj
        t = jd_conj + 2.0
    return jd_start


def get_sun_moon_rise_set(jd_ut_day_start, lat, lon, alt):
    geopos = (lon, lat, alt)
    _, res_rise = swe.rise_trans_true_hor(jd_ut_day_start, swe.SUN, swe.CALC_RISE, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
    sunrise_jd = res_rise[0]
    
    _, res_set = swe.rise_trans_true_hor(sunrise_jd, swe.SUN, swe.CALC_SET, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
    sunset_jd = res_set[0]
    
    try:
        _, res_mrise = swe.rise_trans_true_hor(sunrise_jd, swe.MOON, swe.CALC_RISE, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
        moonrise_jd = res_mrise[0]
    except Exception:
        moonrise_jd = None
        
    try:
        _, res_mset = swe.rise_trans_true_hor(sunrise_jd, swe.MOON, swe.CALC_SET, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
        moonset_jd = res_mset[0]
    except Exception:
        moonset_jd = None
        
    return sunrise_jd, sunset_jd, moonrise_jd, moonset_jd


def get_karana_name_from_idx(k_idx, lang):
    if k_idx == 0:
        return Kalakosha.KARANAS[lang][7]
    elif 1 <= k_idx <= 56:
        return Kalakosha.KARANAS[lang][(k_idx - 1) % 7]
    elif k_idx == 57:
        return Kalakosha.KARANAS[lang][8]
    elif k_idx == 58:
        return Kalakosha.KARANAS[lang][9]
    else:
        return Kalakosha.KARANAS[lang][10]


def calculate_panchanga(year, month, day, tz, lat, lon, alt, tithi_mode="traditional", calendar_system="shaka", month_system="amavasyanta", lang="en"):
    # Target date local midnight in UTC
    jd_ut_start = swe.julday(year, month, day, 0.0 - tz)
    
    # Sun & Moon rise/sets
    sunrise_jd, sunset_jd, moonrise_jd, moonset_jd = get_sun_moon_rise_set(jd_ut_start, lat, lon, alt)
    
    # Target day tomorrow morning sunrise for boundary checks
    jd_tomorrow_start = jd_ut_start + 1.0
    tomorrow_sunrise_jd, _, _, _ = get_sun_moon_rise_set(jd_tomorrow_start, lat, lon, alt)
    
    # In traditional mode calculations are anchored to Udaya (sunrise)
    jd_calc = sunrise_jd if tithi_mode == "traditional" else swe.julday(year, month, day, 12.0 - tz)
    
    sun_l, moon_l = get_sidereal_longitudes(jd_calc)
    
    # 1. Tithi & Paksha
    t_idx, is_adhika, is_krishna, t_num_idx, t_val = get_lunar_month_details(jd_calc, month_system)
    tithi_name = Kalakosha.TITHIS[lang][t_num_idx]
    
    prefix = ""
    if is_adhika:
        if lang == "en":
            prefix = "Adhika "
        elif lang == "iast":
            prefix = "Adhika "
        elif lang == "devanagari":
            prefix = "अधिक "
            
    if calendar_system == "saura":
        sun_rashi = int(sun_l / 30.0) % 12
        masa_name = Kalakosha.SAURA_MASAS[lang][sun_rashi]
    else:
        masa_name = prefix + Kalakosha.MASAS[lang][t_idx]
    paksha_name = Kalakosha.PAKSHAS[lang][1 if is_krishna else 0]
    
    # 2. Nakshatra
    nak_idx = int(moon_l / 13.333333) % 27
    nakshatra_name = Kalakosha.NAKSHATRAS[lang][nak_idx]
    
    # 3. Yoga
    yoga_idx = int(((moon_l + sun_l) % 360) / 13.333333) % 27
    yoga_name = Kalakosha.YOGAS[lang][yoga_idx]
    
    # 4. Karana
    diff_l = (moon_l - sun_l) % 360
    k_idx = int(diff_l / 6.0)
    karana_name = get_karana_name_from_idx(k_idx, lang)
    
    # 5. Vaara
    dt = datetime.date(year, month, day)
    vaara_idx = dt.weekday()
    vaara_name = Kalakosha.VAARAS[lang][vaara_idx]
    
    # 6. Ritu and Ayana
    ritu_idx = (t_idx // 2) % 6
    ritu_name = Kalakosha.RITUS[lang][ritu_idx]
    
    sun_rashi = int(sun_l / 30.0)
    ayana_idx = 1 if (3 <= sun_rashi <= 8) else 0
    ayana_name = Kalakosha.AYANAS[lang][ayana_idx]
    
    # 7. Era calculations
    chaitra_prat_jd = get_chaitra_pratipada_jd(year)
    is_after_chaitra_prat = (jd_calc >= chaitra_prat_jd)
    
    if calendar_system == "saura":
        shaka_year = year - 78 if (sun_rashi < 9) else year - 79
        vikram_year = year + 57 if (sun_rashi < 9) else year + 56
        era_year = shaka_year
        era_name = "Solar Shaka" if lang == "en" else ("Śaka (Saura)" if lang == "iast" else "शक (सौर)")
    else:
        shaka_year = year - 78 if is_after_chaitra_prat else year - 79
        if calendar_system == "kartak":
            kartika_prat_jd = get_kartika_pratipada_jd(year)
            is_after_kartika_prat = (jd_calc >= kartika_prat_jd)
            vikram_year = year + 57 if is_after_kartika_prat else year + 56
        else:
            vikram_year = year + 57 if is_after_chaitra_prat else year + 56
        era_year = vikram_year if calendar_system in ["vikram", "kartak"] else shaka_year
        era_name = "Vikram" if calendar_system in ["vikram", "kartak"] else ("शक" if lang == "devanagari" else ("Śaka" if lang == "iast" else "Shaka"))
        
    kali_year = shaka_year + 3180
    
    if calendar_system in ["vikram", "kartak"]:
        samvatsara_idx = (vikram_year + 10) % 60
    else:
        samvatsara_idx = (shaka_year + 11) % 60
    samvatsara_name = Kalakosha.SAMVATSARAS[lang][samvatsara_idx]
    
    # 8. Auspicious / Inauspicious times
    day_duration = sunset_jd - sunrise_jd
    part_duration = day_duration / 8.0
    
    rahu_parts = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}
    yama_parts = {0: 4, 1: 3, 2: 2, 3: 1, 4: 7, 5: 6, 6: 5}
    gulika_parts = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 7}
    
    rahu_k = rahu_parts[vaara_idx]
    rahu_start = sunrise_jd + (rahu_k - 1) * part_duration
    rahu_end = sunrise_jd + rahu_k * part_duration
    
    yama_k = yama_parts[vaara_idx]
    yama_start = sunrise_jd + (yama_k - 1) * part_duration
    yama_end = sunrise_jd + yama_k * part_duration
    
    gulika_k = gulika_parts[vaara_idx]
    gulika_start = sunrise_jd + (gulika_k - 1) * part_duration
    gulika_end = sunrise_jd + gulika_k * part_duration
    
    muhurta_duration = day_duration / 15.0
    abhijit_start = sunrise_jd + 7 * muhurta_duration
    abhijit_end = sunrise_jd + 8 * muhurta_duration
    
    # Time formatting helper (24+h after midnight)
    def jd_to_time_str(jd):
        if jd is None:
            return "--"
        jd_local = jd + tz / 24.0
        _, _, _, hr = swe.revjul(jd_local)
        total_minutes = int(round(hr * 60))
        h = (total_minutes // 60)
        m = total_minutes % 60
        if h == 24 and m == 0:
            h = 0
            
        # Add 24 for each crossed Gregorian day boundary relative to today's start
        jd_local_start = jd_ut_start + tz / 24.0
        days_crossed = int(jd_local - jd_local_start)
        if days_crossed >= 1:
            h += 24 * days_crossed
            
        return f"{h:02d}:{m:02d}"

    # Helper indexes at given Julian Date
    def get_tithi_idx(jd):
        s_l, m_l = get_sidereal_longitudes(jd)
        return int(((m_l - s_l) % 360) / 12.0)
        
    def get_nakshatra_idx(jd):
        _, m_l = get_sidereal_longitudes(jd)
        return int(m_l / (360.0 / 27.0)) % 27
        
    def get_yoga_idx(jd):
        s_l, m_l = get_sidereal_longitudes(jd)
        return int(((m_l + s_l) % 360) / (360.0 / 27.0)) % 27
        
    def get_karana_idx(jd):
        s_l, m_l = get_sidereal_longitudes(jd)
        return int(((m_l - s_l) % 360) / 6.0)

    # Transitions JDs
    tithi_end_jd = find_transition(jd_calc, get_tithi_idx)
    nakshatra_end_jd = find_transition(jd_calc, get_nakshatra_idx)
    yoga_end_jd = find_transition(jd_calc, get_yoga_idx)
    karana_end_jd = find_transition(jd_calc, get_karana_idx)
    
    # Survival checks (same at tomorrow sunrise)
    tithi_survives = (get_tithi_idx(sunrise_jd) == get_tithi_idx(tomorrow_sunrise_jd))
    nakshatra_survives = (get_nakshatra_idx(sunrise_jd) == get_nakshatra_idx(tomorrow_sunrise_jd))
    yoga_survives = (get_yoga_idx(sunrise_jd) == get_yoga_idx(tomorrow_sunrise_jd))
    karana_survives = (get_karana_idx(sunrise_jd) == get_karana_idx(tomorrow_sunrise_jd))
    
    tithi_end = jd_to_time_str(tithi_end_jd)
    nakshatra_end = jd_to_time_str(nakshatra_end_jd)
    yoga_end = jd_to_time_str(yoga_end_jd)
    karana_end = jd_to_time_str(karana_end_jd)
    
    # Second transition elements (using 0.02 days start offset past the boundary)
    tithi_2_name = "--"
    tithi_2_end = "--"
    tithi_2_end_jd = None
    if tithi_end_jd is not None:
        tithi_2_idx = get_tithi_idx(tithi_end_jd + 0.02)
        tithi_2_name = Kalakosha.TITHIS[lang][tithi_2_idx]
        tithi_2_end_jd = find_transition(tithi_end_jd + 0.02, get_tithi_idx)
        tithi_2_end = jd_to_time_str(tithi_2_end_jd)
        
    nakshatra_2_name = "--"
    nakshatra_2_end = "--"
    nakshatra_2_end_jd = None
    if nakshatra_end_jd is not None:
        nakshatra_2_idx = get_nakshatra_idx(nakshatra_end_jd + 0.02)
        nakshatra_2_name = Kalakosha.NAKSHATRAS[lang][nakshatra_2_idx]
        nakshatra_2_end_jd = find_transition(nakshatra_end_jd + 0.02, get_nakshatra_idx)
        nakshatra_2_end = jd_to_time_str(nakshatra_2_end_jd)
        
    yoga_2_name = "--"
    yoga_2_end = "--"
    yoga_2_end_jd = None
    if yoga_end_jd is not None:
        yoga_2_idx = get_yoga_idx(yoga_end_jd + 0.02)
        yoga_2_name = Kalakosha.YOGAS[lang][yoga_2_idx]
        yoga_2_end_jd = find_transition(yoga_end_jd + 0.02, get_yoga_idx)
        yoga_2_end = jd_to_time_str(yoga_2_end_jd)
        
    karana_2_name = "--"
    karana_2_end = "--"
    karana_2_end_jd = None
    if karana_end_jd is not None:
        karana_2_idx = get_karana_idx(karana_end_jd + 0.02)
        karana_2_name = get_karana_name_from_idx(karana_2_idx, lang)
        karana_2_end_jd = find_transition(karana_end_jd + 0.02, get_karana_idx)
        karana_2_end = jd_to_time_str(karana_2_end_jd)
        
    # Rain/Surya Nakshatra (Sun's Nakshatra)
    def get_surya_nakshatra_idx(jd):
        s_l, _ = get_sidereal_longitudes(jd)
        return int(s_l / (360.0 / 27.0)) % 27

    surya_nakshatra_idx = get_surya_nakshatra_idx(sunrise_jd)
    surya_nakshatra_tomorrow_idx = get_surya_nakshatra_idx(tomorrow_sunrise_jd)
    surya_nakshatra_survives = (surya_nakshatra_idx == surya_nakshatra_tomorrow_idx)
    
    surya_nakshatra_name = Kalakosha.NAKSHATRAS[lang][surya_nakshatra_idx]
    surya_nakshatra_end = "--"
    surya_nakshatra_end_jd = None
    surya_nakshatra_2_name = "--"
    surya_nakshatra_2_end = "--"
    
    if not surya_nakshatra_survives:
        surya_nakshatra_end_jd = find_transition(jd_calc, get_surya_nakshatra_idx)
        surya_nakshatra_end = jd_to_time_str(surya_nakshatra_end_jd)
        surya_nakshatra_2_idx = surya_nakshatra_tomorrow_idx
        surya_nakshatra_2_name = Kalakosha.NAKSHATRAS[lang][surya_nakshatra_2_idx]
        
    # Ghadi & Vipal High-precision calculations
    dt_utc = datetime.datetime.now(datetime.timezone.utc)
    jd_now_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                           dt_utc.hour + dt_utc.minute/60.0 + 
                           (dt_utc.second + dt_utc.microsecond/1000000.0)/3600.0)
    
    dt_local = dt_utc + datetime.timedelta(hours=tz)
    is_today = (dt_local.year == year and dt_local.month == month and dt_local.day == day)
    
    tithi_active_idx = 0
    nakshatra_active_idx = 0
    yoga_active_idx = 0
    karana_active_idx = 0
    surya_nakshatra_active_idx = 0
    
    if is_today:
        tithi_active_idx = 2 if (tithi_end_jd is not None and jd_now_ut > tithi_end_jd) else 1
        nakshatra_active_idx = 2 if (nakshatra_end_jd is not None and jd_now_ut > nakshatra_end_jd) else 1
        yoga_active_idx = 2 if (yoga_end_jd is not None and jd_now_ut > yoga_end_jd) else 1
        karana_active_idx = 2 if (karana_end_jd is not None and jd_now_ut > karana_end_jd) else 1
        surya_nakshatra_active_idx = 2 if (surya_nakshatra_end_jd is not None and jd_now_ut > surya_nakshatra_end_jd) else 1
    else:
        surya_nakshatra_active_idx = 1
 
    tithi_active_name = tithi_name
    if is_today and tithi_end_jd is not None and jd_now_ut > tithi_end_jd:
        tithi_active_name = tithi_2_name
        
    nakshatra_active_name = nakshatra_name
    if is_today and nakshatra_end_jd is not None and jd_now_ut > nakshatra_end_jd:
        nakshatra_active_name = nakshatra_2_name
        
    yoga_active_name = yoga_name
    if is_today and yoga_end_jd is not None and jd_now_ut > yoga_end_jd:
        yoga_active_name = yoga_2_name
        
    karana_active_name = karana_name
    if is_today and karana_end_jd is not None and jd_now_ut > karana_end_jd:
        karana_active_name = karana_2_name

    surya_nakshatra_active_name = surya_nakshatra_name
    if is_today and surya_nakshatra_end_jd is not None and jd_now_ut > surya_nakshatra_end_jd:
        surya_nakshatra_active_name = surya_nakshatra_2_name
        
    # Start of day selection
    if jd_now_ut < sunrise_jd:
        jd_yesterday_start = jd_ut_start - 1.0
        y_sunrise_jd, _, _, _ = get_sun_moon_rise_set(jd_yesterday_start, lat, lon, alt)
        day_length = sunrise_jd - y_sunrise_jd
        elapsed = jd_now_ut - y_sunrise_jd
    else:
        day_length = tomorrow_sunrise_jd - sunrise_jd
        elapsed = jd_now_ut - sunrise_jd
        
    proportion = elapsed / day_length
    total_ghadis = proportion * 60.0
    ghadi = int(total_ghadis)
    vipal = int((total_ghadis - ghadi) * 60.0)
    # Brahma Muhurta (96m to 48m before sunrise)
    brahma_start = sunrise_jd - (96.0 / 1440.0)
    brahma_end = sunrise_jd - (48.0 / 1440.0)
    brahma_muhurta = f"{jd_to_time_str(brahma_start)} - {jd_to_time_str(brahma_end)}"
    
    # Choghadiya
    day_part = (sunset_jd - sunrise_jd) / 8.0
    night_part = (tomorrow_sunrise_jd - sunset_jd) / 8.0
    
    day_choghadiyas = []
    night_choghadiyas = []
    
    for i in range(8):
        d_start = sunrise_jd + i * day_part
        d_end = sunrise_jd + (i + 1) * day_part
        d_idx = (Kalakosha.CHOGHADIYA_DAY_START[vaara_idx] + i) % 7
        d_name = Kalakosha.CHOGHADIYAS[lang][d_idx]
        day_choghadiyas.append({
            "name": d_name,
            "start": jd_to_time_str(d_start),
            "end": jd_to_time_str(d_end),
            "nature": Kalakosha.CHOGHADIYA_NATURES[lang][d_name]
        })
        
        n_start = sunset_jd + i * night_part
        n_end = sunset_jd + (i + 1) * night_part
        n_idx = (Kalakosha.CHOGHADIYA_NIGHT_START[vaara_idx] + i) % 7
        n_name = Kalakosha.CHOGHADIYAS[lang][n_idx]
        night_choghadiyas.append({
            "name": n_name,
            "start": jd_to_time_str(n_start),
            "end": jd_to_time_str(n_end),
            "nature": Kalakosha.CHOGHADIYA_NATURES[lang][n_name]
        })

    return {
        "date": f"{year:04d}-{month:02d}-{day:02d}",
        "vaara": vaara_name,
        "tithi": tithi_active_name,
        "tithi_end": tithi_end,
        "tithi_1": tithi_name,
        "tithi_1_end": tithi_end,
        "tithi_2": tithi_2_name,
        "tithi_2_end": tithi_2_end,
        "tithi_active_idx": tithi_active_idx,
        "tithi_survives": tithi_survives,
        
        "paksha": paksha_name,
        "masa": masa_name,
        "masa_idx": t_idx,
        
        "nakshatra": nakshatra_active_name,
        "nakshatra_end": nakshatra_end,
        "nakshatra_1": nakshatra_name,
        "nakshatra_1_end": nakshatra_end,
        "nakshatra_2": nakshatra_2_name,
        "nakshatra_2_end": nakshatra_2_end,
        "nakshatra_active_idx": nakshatra_active_idx,
        "nakshatra_survives": nakshatra_survives,
        
        "surya_nakshatra": surya_nakshatra_active_name,
        "surya_nakshatra_end": surya_nakshatra_end,
        "surya_nakshatra_1": surya_nakshatra_name,
        "surya_nakshatra_1_end": surya_nakshatra_end,
        "surya_nakshatra_2": surya_nakshatra_2_name,
        "surya_nakshatra_2_end": surya_nakshatra_2_end,
        "surya_nakshatra_active_idx": surya_nakshatra_active_idx,
        "surya_nakshatra_survives": surya_nakshatra_survives,
        
        "yoga": yoga_active_name,
        "yoga_end": yoga_end,
        "yoga_1": yoga_name,
        "yoga_1_end": yoga_end,
        "yoga_2": yoga_2_name,
        "yoga_2_end": yoga_2_end,
        "yoga_active_idx": yoga_active_idx,
        "yoga_survives": yoga_survives,
        
        "karana": karana_active_name,
        "karana_end": karana_end,
        "karana_1": karana_name,
        "karana_1_end": karana_end,
        "karana_2": karana_2_name,
        "karana_2_end": karana_2_end,
        "karana_active_idx": karana_active_idx,
        "karana_survives": karana_survives,
        
        "ritu": ritu_name,
        "ayana": ayana_name,
        "samvatsara": samvatsara_name,
        "shaka_year": shaka_year,
        "vikram_year": vikram_year,
        "kali_year": kali_year,
        "era_year": era_year,
        "era_name": era_name,
        "sunrise": jd_to_time_str(sunrise_jd),
        "sunset": jd_to_time_str(sunset_jd),
        "moonrise": jd_to_time_str(moonrise_jd),
        "moonset": jd_to_time_str(moonset_jd),
        "rahu_kala": f"{jd_to_time_str(rahu_start)} - {jd_to_time_str(rahu_end)}",
        "yamaghanta": f"{jd_to_time_str(yama_start)} - {jd_to_time_str(yama_end)}",
        "gulika": f"{jd_to_time_str(gulika_start)} - {jd_to_time_str(gulika_end)}",
        "abhijit_muhurta": f"{jd_to_time_str(abhijit_start)} - {jd_to_time_str(abhijit_end)}",
        "ghadi": f"{ghadi:02d}:{vipal:02d}",
        "brahma_muhurta": brahma_muhurta,
        "day_choghadiya": day_choghadiyas,
        "night_choghadiya": night_choghadiyas,
        "is_krishna_paksha": is_krishna,
        "tithi_num": (t_num_idx % 15) + 1,
        "tithi_idx": t_num_idx,
        
        # Raw transition JDs for other engines
        "sunrise_jd": sunrise_jd,
        "sunset_jd": sunset_jd,
        "moonrise_jd": moonrise_jd if moonrise_jd else 0.0,
        "moonset_jd": moonset_jd if moonset_jd else 0.0,
        "tomorrow_sunrise_jd": tomorrow_sunrise_jd,
        "jd_calc": jd_calc,
        "jd_ut_start": jd_ut_start
    }
