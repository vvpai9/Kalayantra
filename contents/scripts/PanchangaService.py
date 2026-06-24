#!/usr/bin/env python3
import sys
import os
import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import swisseph as swe

# Constants for calculations
# 60 Samvatsara names in three languages
SAMVATSARAS = {
    "en": [
        "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati", "Angirasa", "Shrimukha", "Bhava",
        "Yuva", "Dhatri", "Ishvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha", "Chitrabhanu",
        "Subhanu", "Tarana", "Parthiva", "Vyaya", "Sarvajit", "Sarvadhari", "Virodhi", "Vikriti",
        "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukha", "Hemalamba", "Vilamba",
        "Vikari", "Sharvari", "Plava", "Shubhakrit", "Shobhakrit", "Krodhi", "Vishvavasu", "Parabhava",
        "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrit", "Paridhavi", "Pramadi", "Ananda",
        "Rakshasa", "Anala", "Pingala", "Kalayukta", "Siddharthi", "Raudra", "Durmati", "Dundubhi",
        "Rudhiraudgari", "Raktakshi", "Krodhana", "Kshaya"
    ],
    "iast": [
        "Prabhava", "Vibhava", "Śukla", "Pramoda", "Prajāpati", "Aṅgiras", "Śrīmukha", "Bhava",
        "Yuva", "Dhātṛ", "Īśvara", "Bahudhānya", "Pramāthin", "Vikrama", "Vṛṣa", "Citrabhānu",
        "Subhānu", "Tāraṇa", "Pārthiva", "Vyaya", "Sarvajit", "Sarvadhārin", "Virodhin", "Vikṛti",
        "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukha", "Hemalamba", "Vilamba",
        "Vikārin", "Śārvarī", "Plava", "Śubhakṛt", "Śobhakṛt", "Krodhin", "Viśvāvasu", "Parābhava",
        "Plavaṅga", "Kīlaka", "Saumya", "Sādhāraṇa", "Virodhakṛt", "Paridhāvin", "Pramādin", "Ānanda",
        "Rākṣasa", "Anala", "Piṅgala", "Kālayukta", "Siddhārthin", "Raudra", "Durmati", "Dundubhi",
        "Rudhiraudgārin", "Raktākṣī", "Krodhana", "Akṣaya"
    ],
    "devanagari": [
        "प्रभव", "विभव", "शुक्ल", "प्रमोद", "प्रजापति", "अङ्गिरस", "श्रीमख", "भाव",
        "युव", "धातृ", "ईश्वर", "बहुधान्य", "प्रमाथि", "विक्रम", "वृष", "चित्रभानु",
        "सुभानु", "तारण", "पार्थिव", "व्यय", "सर्वजित्", "सर्वधारि", "विरोधी", "विकृति",
        "खर", "नन्दन", "विजय", "जय", "मन्मथ", "दुर्मुख", "हेमलम्ब", "विलम्ब",
        "विकारी", "शार्वरी", "प्लव", "शुभकृत्", "शोभकृत्", "क्रोधी", "विश्वावसु", "पराभव",
        "प्लवङ्ग", "कीलक", "सौम्य", "साधारण", "विरोधकृत्", "परिधावी", "प्रमादी", "आनन्द",
        "राक्षस", "अनल", "पिङ्गल", "कालयुक्त", "सिद्धार्थी", "रौद्र", "दुर्मति", "दुन्दुभि",
        "रुधिरोद्गारी", "रक्ताक्षी", "क्रोधन", "अक्षय"
    ]
}

TITHIS = {
    "en": [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami",
        "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami",
        "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
    ],
    "iast": [
        "Pratipadā", "Dvitīyā", "Tṛtīyā", "Caturthī", "Pañcamī", "Ṣaṣṭhī", "Saptamī", "Aṣṭamī",
        "Navamī", "Daśamī", "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī", "Pūrṇimā",
        "Pratipadā", "Dvitīyā", "Tṛtīyā", "Caturthī", "Pañcamī", "Ṣaṣṭhī", "Saptamī", "Aṣṭamī",
        "Navamī", "Daśamī", "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī", "Amāvāsyā"
    ],
    "devanagari": [
        "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पञ्चमी", "षष्ठी", "सप्तमी", "अष्टमी",
        "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "पूर्णिमा",
        "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पञ्चमी", "षष्ठी", "सप्तमी", "अष्टमी",
        "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "अमावास्या"
    ]
}

NAKSHATRAS = {
    "en": [
        "Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu", "Pushya",
        "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
        "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
        "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ],
    "iast": [
        "Aśvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśīrṣa", "Ārdrā", "Punarvasu", "Puṣya",
        "Āśleṣā", "Maghā", "Pūrva Phālguni", "Uttara Phālguni", "Hasta", "Citrā", "Svātī",
        "Viśākhā", "Anurādhā", "Jyesṭhā", "Mūla", "Pūrva Āṣāḍhā", "Uttara Āṣāḍhā", "Śravaṇa",
        "Dhaniṣṭhā", "Śatabhiṣā", "Pūrva Bhādrapadā", "Uttara Bhādrapadā", "Revatī"
    ],
    "devanagari": [
        "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशीर्ष", "आर्द्रा", "पुनर्वसु", "पुष्य",
        "आश्लेषा", "मघा", "पूर्व फाल्गुनी", "उत्तर फाल्गुनी", "हस्त", "चित्रा", "स्वाती",
        "विशाखा", "अनुराधा", "ज्येष्ठा", "मूल", "पूर्वाषाढा", "उत्तराषाढा", "श्रवण",
        "धनिष्ठा", "शतभिषा", "पूर्व भाद्रपदा", "उत्तर भाद्रपदा", "रेवती"
    ]
}

YOGAS = {
    "en": [
        "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti",
        "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi",
        "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
        "Brahma", "Aindra", "Vaidhriti"
    ],
    "iast": [
        "Viṣkambha", "Prīti", "Āyuṣmān", "Saubhāgya", "Śobhana", "Atigaṇda", "Sukarmā", "Dhṛti",
        "Śūla", "Gaṇḍa", "Vṛddhi", "Dhruva", "Vyāghāta", "Harṣaṇa", "Vajra", "Siddhi",
        "Vyatīpāta", "Varīyān", "Parigha", "Śiva", "Siddha", "Sādhya", "Śubha", "Śukla",
        "Brahma", "Aindra", "Vaidhṛti"
    ],
    "devanagari": [
        "विष्कम्भ", "प्रीति", "आयुष्मान्", "सौभाग्य", "शोभन", "अतिगण्ड", "सुकर्मा", "धृति",
        "शूल", "गण्ड", "वृद्धि", "ध्रुव", "व्याघात", "हर्षण", "वज्र", "सिद्धि",
        "व्यतिपात", "वरीयान्", "परिघ", "शिव", "सिद्ध", "साध्य", "शुभ", "शुक्ल",
        "ब्रह्म", "ऐन्द्र", "वैधृति"
    ]
}

KARANAS = {
    "en": [
        "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
        "Kimstughna", "Shakuni", "Chatushpada", "Naga"
    ],
    "iast": [
        "Bava", "Bālava", "Kaulava", "Taitila", "Gara", "Vaṇija", "Viṣṭi",
        "Kiṃstughna", "Śakuni", "Catuṣpadā", "Nāga"
    ],
    "devanagari": [
        "बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टि",
        "किंस्तुघ्न", "शकुनि", "चतुष्पाद", "नाग"
    ]
}

MASAS = {
    "en": [
        "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
        "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"
    ],
    "iast": [
        "Caitra", "Vaiśākha", "Jyesṭha", "Āṣāḍha", "Śrāvaṇa", "Bhādrapada",
        "Āśvina", "Kārtika", "Mārgaśīrṣa", "Pauṣa", "Māgha", "Phālguna"
    ],
    "devanagari": [
        "चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ", "श्रावण", "भाद्रपद",
        "आश्विन", "कार्तिक", "मार्गशीर्ष", "पौष", "माघ", "फाल्गुन"
    ]
}

RITUS = {
    "en": ["Vasanta (Spring)", "Grishma (Summer)", "Varsha (Monsoon)", "Sharad (Autumn)", "Hemanta (Pre-winter)", "Shishira (Winter)"],
    "iast": ["Vasanta", "Grīṣma", "Varṣā", "Śarad", "Hemanta", "Śiśira"],
    "devanagari": ["वसन्त", "ग्रीष्म", "वर्षा", "शरद", "हेमन्त", "शिशिर"]
}

AYANAS = {
    "en": ["Uttarayana (Northern)", "Dakshinayana (Southern)"],
    "iast": ["Uttarāyaṇa", "Dakṣiṇāyana"],
    "devanagari": ["उत्तरायण", "दक्षिणायन"]
}

PAKSHAS = {
    "en": ["Shukla", "Krishna"],
    "iast": ["Śukla", "Kṛṣṇa"],
    "devanagari": ["शुक्ल", "कृष्ण"]
}

VAARAS = {
    "en": ["Monday (Somavaara)", "Tuesday (Bhaumavaara)", "Wednesday (Budhavaara)", "Thursday (Guruvaara)", "Friday (Shukravaara)", "Saturday (Shanivaara)", "Sunday (Bhanuvaara)"],
    "iast": ["Somavāra", "Bhaumavāra", "Budhavāra", "Guruvāra", "Śukravāra", "Śanivāra", "Bhānuvāra"],
    "devanagari": ["सोमवार", "भौमवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "भानुवार"]
}


# Calculation engine utilities
def get_sidereal_longitudes(jd_ut):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    # Calculate Sun position
    res_sun, err = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    sun_long = res_sun[0]
    # Calculate Moon position
    res_moon, err = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    moon_long = res_moon[0]
    return sun_long, moon_long

def find_previous_conjunction(jd_ut):
    t = jd_ut
    sun_l, moon_l = get_sidereal_longitudes(t)
    diff = (moon_l - sun_l) % 360
    
    prev_t = t
    prev_diff = diff
    # Step backward
    for _ in range(20):
        t -= 2.0
        sun_l, moon_l = get_sidereal_longitudes(t)
        curr_diff = (moon_l - sun_l) % 360
        if curr_diff > prev_diff:
            # Crossed conjunction
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
            # Crossed conjunction
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
    # Previous conjunction
    jd_prev_conj = find_previous_conjunction(jd_ut)
    # Next conjunction
    jd_next_conj = find_next_conjunction(jd_ut)
    
    # Sun Rashi at previous conjunction
    sun_l_prev, _ = get_sidereal_longitudes(jd_prev_conj)
    rashi_prev = int(sun_l_prev / 30.0)
    
    # Sun Rashi at next conjunction
    sun_l_next, _ = get_sidereal_longitudes(jd_next_conj)
    rashi_next = int(sun_l_next / 30.0)
    
    # Check for Adhika Masa
    is_adhika = (rashi_prev == rashi_next)
    
    # Month index (0 to 11, Chaitra to Phalguna)
    masa_idx = (rashi_prev + 1) % 12
    
    # Calculate current tithi to check paksha
    sun_l, moon_l = get_sidereal_longitudes(jd_ut)
    tithi_val = ((moon_l - sun_l) % 360) / 12.0
    tithi_idx = int(tithi_val) # 0 to 29
    is_krishna = (tithi_idx >= 15)
    
    # Purnimanta month name shift (shifts in Krishna Paksha of regular months)
    purnimanta_masa_idx = masa_idx
    if month_system == "purnimanta" and not is_adhika and is_krishna:
        purnimanta_masa_idx = (masa_idx + 1) % 12
        
    actual_masa_idx = purnimanta_masa_idx if month_system == "purnimanta" else masa_idx
    
    return actual_masa_idx, is_adhika, is_krishna, tithi_idx, tithi_val

def get_chaitra_pratipada_jd(year):
    # Search for conjunction in March/April where Sun Rashi is in Meena (idx 11)
    # Start at March 1st
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
    # Search for conjunction in October/November where Sun Rashi is in Kanya (idx 6)
    # Start at October 1st
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
    # Sunrise
    _, res_rise = swe.rise_trans_true_hor(jd_ut_day_start, swe.SUN, swe.CALC_RISE, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
    sunrise_jd = res_rise[0]
    
    # Sunset
    _, res_set = swe.rise_trans_true_hor(jd_ut_day_start, swe.SUN, swe.CALC_SET, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
    sunset_jd = res_set[0]
    
    # Moonrise
    try:
        _, res_mrise = swe.rise_trans_true_hor(jd_ut_day_start, swe.MOON, swe.CALC_RISE, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
        moonrise_jd = res_mrise[0]
    except Exception:
        moonrise_jd = None
        
    # Moonset
    try:
        _, res_mset = swe.rise_trans_true_hor(jd_ut_day_start, swe.MOON, swe.CALC_SET, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
        moonset_jd = res_mset[0]
    except Exception:
        moonset_jd = None
        
    return sunrise_jd, sunset_jd, moonrise_jd, moonset_jd

def calculate_panchanga(year, month, day, tz, lat, lon, alt, tithi_mode="sunrise", calendar_system="shaka", month_system="amavasyanta", festival_rule="vaishnava", lang="en"):
    # Target date local 12:00 AM (midnight) in UTC to ensure sunrise/sunset are for the same calendar date
    jd_ut_start = swe.julday(year, month, day, 0.0 - tz)
    
    # Sunrise, Sunset, etc.
    sunrise_jd, sunset_jd, moonrise_jd, moonset_jd = get_sun_moon_rise_set(jd_ut_start, lat, lon, alt)
    
    # Determine the JD for calculations (either sunrise or request time)
    # Default to local noon for calculations if not sunrise tithi mode
    jd_calc = sunrise_jd if tithi_mode == "sunrise" else swe.julday(year, month, day, 12.0 - tz)
    
    # Calculate positions
    sun_l, moon_l = get_sidereal_longitudes(jd_calc)
    
    # 1. Tithi & Paksha
    t_idx, is_adhika, is_krishna, t_num_idx, t_val = get_lunar_month_details(jd_calc, month_system)
    tithi_name = TITHIS[lang][t_num_idx]
    
    # Adhika month prefix
    prefix = ""
    if is_adhika:
        if lang == "en":
            prefix = "Adhika "
        elif lang == "iast":
            prefix = "Adhika "
        elif lang == "devanagari":
            prefix = "अधिक "
            
    masa_name = prefix + MASAS[lang][t_idx]
    paksha_name = PAKSHAS[lang][1 if is_krishna else 0]
    
    # 2. Nakshatra
    nak_idx = int(moon_l / 13.333333) % 27
    nakshatra_name = NAKSHATRAS[lang][nak_idx]
    
    # 3. Yoga
    yoga_idx = int(((moon_l + sun_l) % 360) / 13.333333) % 27
    yoga_name = YOGAS[lang][yoga_idx]
    
    # 4. Karana
    diff_l = (moon_l - sun_l) % 360
    k_idx_float = diff_l / 6.0
    k_idx = int(k_idx_float)
    if k_idx == 0:
        # Kimstughna (idx 7 in Karanas dictionary)
        karana_name = KARANAS[lang][7]
    elif 1 <= k_idx <= 56:
        karana_name = KARANAS[lang][(k_idx - 1) % 7]
    elif k_idx == 57:
        # Shakuni (idx 8)
        karana_name = KARANAS[lang][8]
    elif k_idx == 58:
        # Chatushpada (idx 9)
        karana_name = KARANAS[lang][9]
    else:
        # Naga (idx 10)
        karana_name = KARANAS[lang][10]
        
    # 5. Vaara
    dt = datetime.date(year, month, day)
    vaara_idx = dt.weekday() # 0 = Monday, ..., 6 = Sunday
    vaara_name = VAARAS[lang][vaara_idx]
    
    # 6. Ritu and Ayana
    # Ritu is based on the lunar month (masa_idx // 2)
    ritu_idx = (t_idx // 2) % 6
    ritu_name = RITUS[lang][ritu_idx]
    
    # Ayana is based on the Sun's Rashi (Uttarayana: Makara to Mithuna, Dakshinayana: Karka to Dhanu)
    sun_rashi = int(sun_l / 30.0)
    # Uttarayana is Sun in Rashi 9 to 2 (Makara to Mithuna)
    # Dakshinayana is Sun in Rashi 3 to 8 (Karka to Dhanu)
    ayana_idx = 1 if (3 <= sun_rashi <= 8) else 0
    ayana_name = AYANAS[lang][ayana_idx]
    
    # 7. Year and Jovian cycle
    # Compute Chaitra Shukla Pratipada JD for Year determinations
    chaitra_prat_jd = get_chaitra_pratipada_jd(year)
    is_after_chaitra_prat = (jd_calc >= chaitra_prat_jd)
    
    # Shalivahana Shaka Year
    shaka_year = year - 78 if is_after_chaitra_prat else year - 79
    # Vikram Samvat Year (Chaitradi or Kartikadi)
    if calendar_system == "kartak":
        kartika_prat_jd = get_kartika_pratipada_jd(year)
        is_after_kartika_prat = (jd_calc >= kartika_prat_jd)
        vikram_year = year + 57 if is_after_kartika_prat else year + 56
    else:
        vikram_year = year + 57 if is_after_chaitra_prat else year + 56
        
    # Kali Yuga Year
    kali_year = shaka_year + 3179
    
    # Samvatsara Jovian Cycle (60 year cycle names, 0-indexed where 39 = Parabhava)
    samvatsara_idx = (shaka_year + 11) % 60
    samvatsara_name = SAMVATSARAS[lang][samvatsara_idx]
    
    # 8. Auspicious & Inauspicious daytime segments
    # Dividing the daytime into 8 equal parts
    day_duration = sunset_jd - sunrise_jd
    part_duration = day_duration / 8.0
    
    # Part indices for Monday(0) to Sunday(6)
    rahu_parts = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}
    yama_parts = {0: 4, 1: 3, 2: 2, 3: 1, 4: 8, 5: 7, 6: 5}
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
    
    # Abhijit Muhurta (8th of 15 divisions of the day)
    muhurta_duration = day_duration / 15.0
    abhijit_start = sunrise_jd + 7 * muhurta_duration
    abhijit_end = sunrise_jd + 8 * muhurta_duration
    
    # Format JD time utilities
    def jd_to_time_str(jd):
        if jd is None:
            return "--:--"
        jd_local = jd + tz / 24.0
        _, _, _, hr = swe.revjul(jd_local)
        h = int(hr)
        m = int(round((hr - h) * 60))
        if m == 60:
            h = (h + 1) % 24
            m = 0
        return f"{h:02d}:{m:02d}"
        
    # Ghadi-Vipal time calculation (local time)
    # Find active sunrise for Ghadi calculation
    dt_now = datetime.datetime.now()
    jd_now_ut = swe.julday(dt_now.year, dt_now.month, dt_now.day, dt_now.hour + dt_now.minute/60.0 + dt_now.second/3600.0 - tz)
    
    # Determine the start of day (sunrise of today, or yesterday if before sunrise)
    if jd_now_ut < sunrise_jd:
        # It is before today's sunrise; day started at yesterday's sunrise
        jd_yesterday_start = jd_ut_start - 1.0
        y_sunrise_jd, y_sunset_jd, _, _ = get_sun_moon_rise_set(jd_yesterday_start, lat, lon, alt)
        day_length = sunrise_jd - y_sunrise_jd
        elapsed = jd_now_ut - y_sunrise_jd
    else:
        # Today's sunrise is active
        # Find next day's sunrise
        jd_tomorrow_start = jd_ut_start + 1.0
        t_sunrise_jd, _, _, _ = get_sun_moon_rise_set(jd_tomorrow_start, lat, lon, alt)
        day_length = t_sunrise_jd - sunrise_jd
        elapsed = jd_now_ut - sunrise_jd
        
    proportion = elapsed / day_length
    total_ghadis = proportion * 60.0
    ghadi = int(total_ghadis)
    vipal = int((total_ghadis - ghadi) * 60.0)
    
    # 9. Festivals (Vaishnava vs Smarta)
    festivals = []
    
    # Ekadashi determination
    # Shukla Ekadashi (tithi 11, which is t_num_idx = 10)
    # Krishna Ekadashi (tithi 26, which is t_num_idx = 25)
    is_ekadashi = (t_num_idx == 10 or t_num_idx == 25)
    
    if is_ekadashi:
        ekadashi_name = "Shukla Ekadashi" if t_num_idx == 10 else "Krishna Ekadashi"
        # Translate name
        if lang == "devanagari":
            ekadashi_name = "शुक्ल एकादशी" if t_num_idx == 10 else "कृष्ण एकादशी"
        elif lang == "iast":
            ekadashi_name = "Śukla Ekādaśī" if t_num_idx == 10 else "Kṛṣṇa Ekādaśī"
            
        if festival_rule == "smarta":
            # Smartas celebrate simply on the sunrise tithi day
            festivals.append(ekadashi_name)
        else:
            # Vaishnava rule: check if Dashami was active at Arunodaya (96 mins before sunrise)
            arunodaya_jd = sunrise_jd - (96.0 / 1440.0)
            sun_l_aru, moon_l_aru = get_sidereal_longitudes(arunodaya_jd)
            t_val_aru = ((moon_l_aru - sun_l_aru) % 360) / 12.0
            t_idx_aru = int(t_val_aru)
            
            # If t_idx_aru is Dashami (10 or 25) or earlier, it's viddha
            is_viddha = (t_idx_aru == 9 or t_idx_aru == 24)
            if not is_viddha:
                festivals.append(ekadashi_name)
    
    # Dwadashi day (tithi 12 or 27, i.e., t_num_idx = 11 or 26)
    # Check if Vaishnava Ekadashi was pushed to this day (if yesterday was viddha)
    if t_num_idx == 11 or t_num_idx == 26:
        # Find yesterday's sunrise
        jd_yest = sunrise_jd - 1.0
        # Calculate tithi at yesterday's sunrise
        sun_l_y, moon_l_y = get_sidereal_longitudes(jd_yest)
        t_val_y = ((moon_l_y - sun_l_y) % 360) / 12.0
        t_idx_y = int(t_val_y)
        
        # If yesterday was Ekadashi (10 or 25)
        if t_idx_y == 10 or t_idx_y == 25:
            # Check if yesterday was viddha
            yest_sunrise_jd, _, _, _ = get_sun_moon_rise_set(jd_yest, lat, lon, alt)
            arunodaya_jd = yest_sunrise_jd - (96.0 / 1440.0)
            sun_l_aru, moon_l_aru = get_sidereal_longitudes(arunodaya_jd)
            t_val_aru = ((moon_l_aru - sun_l_aru) % 360) / 12.0
            t_idx_aru = int(t_val_aru)
            
            is_viddha = (t_idx_aru == 9 or t_idx_aru == 24)
            if is_viddha and festival_rule == "vaishnava":
                ekadashi_name = "Vaishnava Ekadashi (Dwadashi Paksha)"
                if lang == "devanagari":
                    ekadashi_name = "वैष्णव एकादशी (द्वादशी पक्ष)"
                elif lang == "iast":
                    ekadashi_name = "Vaiṣṇava Ekādaśī"
                festivals.append(ekadashi_name)
                
    # Other festivals (Rama Navami, Maha Shivaratri, etc.)
    # Rama Navami: Chaitra Shukla Navami (masa = 0, paksha = Shukla, tithi = 8 (Navami is idx 8))
    # We use Amavasyanta month index for these checks
    amav_masa_idx, _, _, _, _ = get_lunar_month_details(jd_calc, "amavasyanta")
    if amav_masa_idx == 0 and not is_krishna and t_num_idx == 8:
        name = "Rama Navami"
        if lang == "devanagari":
            name = "राम नवमी"
        elif lang == "iast":
            name = "Rāma Navamī"
        festivals.append(name)
        
    # Maha Shivaratri: Phalguna Krishna Chaturdashi (masa = 11, paksha = Krishna, tithi = 28 (Chaturdashi is idx 28))
    if amav_masa_idx == 11 and is_krishna and t_num_idx == 28:
        name = "Maha Shivaratri"
        if lang == "devanagari":
            name = "महाशिवरात्रि"
        elif lang == "iast":
            name = "Mahā Śivarātri"
        festivals.append(name)
        
    # Krishna Janmashtami: Shravana Krishna Ashtami (masa = 4, paksha = Krishna, tithi = 22 (Ashtami is idx 22))
    if amav_masa_idx == 4 and is_krishna and t_num_idx == 22:
        name = "Krishna Janmashtami"
        if lang == "devanagari":
            name = "कृष्ण जन्माष्टमी"
        elif lang == "iast":
            name = "Kṛṣṇa Janmāṣṭamī"
        festivals.append(name)
        
    # Makar Sankranti: Sun enters Capricorn (sidereal longitude 270 degrees)
    # Check if Sun enters Makara on this day
    # Get Sun longitude at sunrise and next sunrise
    sun_long_today, _ = get_sidereal_longitudes(sunrise_jd)
    # Next day sunrise
    jd_next_sunrise = sunrise_jd + 1.0
    sun_long_next, _ = get_sidereal_longitudes(jd_next_sunrise)
    
    # Check if crossed 270
    if sun_long_today < 270 <= sun_long_next or (sun_long_today > 350 and sun_long_next < 10 and 270 <= sun_long_today):
        name = "Makar Sankranti"
        if lang == "devanagari":
            name = "मकर संक्रान्ति"
        elif lang == "iast":
            name = "Makara Saṅkrānti"
        festivals.append(name)
        
    return {
        "date": f"{year:04d}-{month:02d}-{day:02d}",
        "vaara": vaara_name,
        "tithi": tithi_name,
        "paksha": paksha_name,
        "masa": masa_name,
        "nakshatra": nakshatra_name,
        "yoga": yoga_name,
        "karana": karana_name,
        "ritu": ritu_name,
        "ayana": ayana_name,
        "samvatsara": samvatsara_name,
        "shaka_year": shaka_year,
        "vikram_year": vikram_year,
        "kali_year": kali_year,
        "sunrise": jd_to_time_str(sunrise_jd),
        "sunset": jd_to_time_str(sunset_jd),
        "moonrise": jd_to_time_str(moonrise_jd),
        "moonset": jd_to_time_str(moonset_jd),
        "rahu_kala": f"{jd_to_time_str(rahu_start)} - {jd_to_time_str(rahu_end)}",
        "yamaganda": f"{jd_to_time_str(yama_start)} - {jd_to_time_str(yama_end)}",
        "gulika": f"{jd_to_time_str(gulika_start)} - {jd_to_time_str(gulika_end)}",
        "abhijit_muhurta": f"{jd_to_time_str(abhijit_start)} - {jd_to_time_str(abhijit_end)}",
        "ghadi": f"{ghadi:02d}:{vipal:02d}",
        "festivals": festivals,
        "is_krishna_paksha": is_krishna,
        "tithi_num": (t_num_idx % 15) + 1
    }


# HTTP Handler for REST endpoints
class PanchangaRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/day':
            query = parse_qs(url.query)
            try:
                # Parse query parameters
                lat = float(query.get('lat', [23.1765])[0])
                lon = float(query.get('lon', [75.7885])[0])
                alt = float(query.get('alt', [0.0])[0])
                tz = float(query.get('tz', [5.5])[0])
                
                # Date parameter
                date_str = query.get('date', [None])[0]
                if date_str:
                    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    dt = datetime.datetime.now()
                    
                tithi_mode = query.get('tithi_mode', ['sunrise'])[0]
                calendar_system = query.get('calendar_system', ['shaka'])[0]
                month_system = query.get('month_system', ['amavasyanta'])[0]
                festival_rule = query.get('festival_rule', ['vaishnava'])[0]
                lang = query.get('lang', ['en'])[0]
                
                # Perform calculations
                data = calculate_panchanga(
                    dt.year, dt.month, dt.day, tz, lat, lon, alt,
                    tithi_mode, calendar_system, month_system, festival_rule, lang
                )
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                
        elif url.path == '/month':
            query = parse_qs(url.query)
            try:
                lat = float(query.get('lat', [23.1765])[0])
                lon = float(query.get('lon', [75.7885])[0])
                alt = float(query.get('alt', [0.0])[0])
                tz = float(query.get('tz', [5.5])[0])
                
                year = int(query.get('year', [datetime.datetime.now().year])[0])
                month = int(query.get('month', [datetime.datetime.now().month])[0])
                
                tithi_mode = query.get('tithi_mode', ['sunrise'])[0]
                calendar_system = query.get('calendar_system', ['shaka'])[0]
                month_system = query.get('month_system', ['amavasyanta'])[0]
                festival_rule = query.get('festival_rule', ['vaishnava'])[0]
                lang = query.get('lang', ['en'])[0]
                
                # Calculate for all days in the month
                days_data = []
                # Find number of days in month
                if month == 12:
                    next_month_start = datetime.date(year + 1, 1, 1)
                else:
                    next_month_start = datetime.date(year, month + 1, 1)
                month_days = (next_month_start - datetime.date(year, month, 1)).days
                
                for d in range(1, month_days + 1):
                    day_calc = calculate_panchanga(
                        year, month, d, tz, lat, lon, alt,
                        tithi_mode, calendar_system, month_system, festival_rule, lang
                    )
                    days_data.append(day_calc)
                    
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(days_data).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run(port=8642):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, PanchangaRequestHandler)
    print(f"Kālayantra Panchanga Service starting on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    print("Service stopped.")

if __name__ == '__main__':
    port = 8642
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run(port)
