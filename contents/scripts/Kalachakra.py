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
        "Rakshasa", "Anala", "Pingala", "Kalayukta", "Siddharthi", "Raudri", "Durmati", "Dundubhi",
        "Rudhiraudgari", "Raktakshi", "Krodhana", "Kshaya"
    ],
    "iast": [
        "Prabhava", "Vibhava", "Śukla", "Pramoda", "Prajāpati", "Aṅgiras", "Śrīmukha", "Bhava",
        "Yuva", "Dhātṛ", "Īśvara", "Bahudhānya", "Pramāthin", "Vikrama", "Vṛṣa", "Citrabhānu",
        "Subhānu", "Tāraṇa", "Pārthiva", "Vyaya", "Sarvajit", "Sarvadhārin", "Virodhin", "Vikṛti",
        "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukha", "Hemalamba", "Vilamba",
        "Vikārin", "Śārvarī", "Plava", "Śubhakṛt", "Śobhakṛt", "Krodhin", "Viśvāvasu", "Parābhava",
        "Plavaṅga", "Kīlaka", "Saumya", "Sādhāraṇa", "Virodhakṛt", "Paridhāvin", "Pramādin", "Ānanda",
        "Rākṣasa", "Anala", "Piṅgala", "Kālayukta", "Siddhārthin", "Raudrī", "Durmati", "Dundubhi",
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
    "en": ["Indu", "Bhauma", "Saumya", "Guru", "Bhargava", "Sthira", "Bhanu"],
    "iast": ["Indu", "Bhauma", "Saumya", "Guru", "Bhargava", "Sthira", "Bhanu"],
    "devanagari": ["इन्दु", "भौम", "सौम्य", "गुरु", "भार्गव", "स्थिर", "भानु"]
}

CHOGHADIYAS = {
    "en": ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
    "iast": ["Udvega", "Cara", "Lābha", "Amṛta", "Kāla", "Śubha", "Roga"],
    "devanagari": ["उद्वेग", "चर", "लाभ", "अमृत", "काल", "शुभ", "रोग"]
}

CHOGHADIYA_NATURES = {
    "en": {
        "Udveg": "Inauspicious",
        "Char": "Neutral",
        "Labh": "Auspicious",
        "Amrit": "Auspicious",
        "Kaal": "Inauspicious",
        "Shubh": "Auspicious",
        "Rog": "Inauspicious"
    },
    "iast": {
        "Udvega": "Inauspicious",
        "Cara": "Neutral",
        "Lābha": "Auspicious",
        "Amṛta": "Auspicious",
        "Kāla": "Inauspicious",
        "Śubha": "Auspicious",
        "Roga": "Inauspicious"
    },
    "devanagari": {
        "उद्वेग": "अशुभ",
        "चर": "सामान्य",
        "लाभ": "शुभ",
        "अमृत": "शुभ",
        "काल": "अशुभ",
        "शुभ": "शुभ",
        "रोग": "अशुभ"
    }
}

# Day starts for Monday(0) to Sunday(6)
# Sunday(6): Sun(0), Monday(0): Moon(3), Tuesday(1): Mars(6), Wednesday(2): Mercury(2), Thursday(3): Jupiter(5), Friday(4): Venus(1), Saturday(5): Saturn(4)
CHOGHADIYA_DAY_START = {0: 3, 1: 6, 2: 2, 3: 5, 4: 1, 5: 4, 6: 0}

# Night starts for Monday(0) to Sunday(6)
# Sunday(6): Jupiter(5), Monday(0): Mars(6), Tuesday(1): Mercury(2), Wednesday(2): Sun(0), Thursday(3): Venus(1), Friday(4): Saturn(4), Saturday(5): Moon(3)
CHOGHADIYA_NIGHT_START = {0: 6, 1: 2, 2: 0, 3: 1, 4: 4, 5: 3, 6: 5}


# Calculation engine utilities
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
    _, res_set = swe.rise_trans_true_hor(sunrise_jd, swe.SUN, swe.CALC_SET, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
    sunset_jd = res_set[0]
    
    # Moonrise
    try:
        _, res_mrise = swe.rise_trans_true_hor(sunrise_jd, swe.MOON, swe.CALC_RISE, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
        moonrise_jd = res_mrise[0]
    except Exception:
        moonrise_jd = None
        
    # Moonset
    try:
        _, res_mset = swe.rise_trans_true_hor(sunrise_jd, swe.MOON, swe.CALC_SET, geopos, 1013.25, 15.0, 0.0, swe.FLG_SWIEPH)
        moonset_jd = res_mset[0]
    except Exception:
        moonset_jd = None
        
    return sunrise_jd, sunset_jd, moonrise_jd, moonset_jd

def get_karana_name_from_idx(k_idx, lang):
    if k_idx == 0:
        return KARANAS[lang][7]
    elif 1 <= k_idx <= 56:
        return KARANAS[lang][(k_idx - 1) % 7]
    elif k_idx == 57:
        return KARANAS[lang][8]
    elif k_idx == 58:
        return KARANAS[lang][9]
    else:
        return KARANAS[lang][10]

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
    if calendar_system in ["vikram", "kartak"]:
        samvatsara_idx = (vikram_year + 10) % 60
    else:
        samvatsara_idx = (shaka_year + 11) % 60
    samvatsara_name = SAMVATSARAS[lang][samvatsara_idx]
    
    era_year = vikram_year if calendar_system in ["vikram", "kartak"] else shaka_year
    era_name = "Vikram" if calendar_system in ["vikram", "kartak"] else ("शक" if lang == "devanagari" else ("Śaka" if lang == "iast" else "Shaka"))
    
    # 8. Auspicious & Inauspicious daytime segments
    # Dividing the daytime into 8 equal parts
    day_duration = sunset_jd - sunrise_jd
    part_duration = day_duration / 8.0
    
    # Part indices for Monday(0) to Sunday(6)
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
    
    # Abhijit Muhurta (8th of 15 divisions of the day)
    muhurta_duration = day_duration / 15.0
    abhijit_start = sunrise_jd + 7 * muhurta_duration
    abhijit_end = sunrise_jd + 8 * muhurta_duration
    
    # Format JD time utilities
    jd_tomorrow_start = jd_ut_start + 1.0
    tomorrow_sunrise_jd, _, _, _ = get_sun_moon_rise_set(jd_tomorrow_start, lat, lon, alt)

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
            
        # Format times after midnight but before sunrise of next day as 24+h
        if jd_tomorrow_start <= jd <= tomorrow_sunrise_jd:
            h += 24
            
        return f"{h:02d}:{m:02d}"

    # Getter functions for indices
    def get_tithi_idx(jd):
        s_l, m_l = get_sidereal_longitudes(jd)
        return int(((m_l - s_l) % 360) / 12.0)
        
    def get_nakshatra_idx(jd):
        _, m_l = get_sidereal_longitudes(jd)
        return int(m_l / 13.333333) % 27
        
    def get_yoga_idx(jd):
        s_l, m_l = get_sidereal_longitudes(jd)
        return int(((m_l + s_l) % 360) / 13.333333) % 27

    # Calculate end times
    get_karana_idx = lambda jd: int(((get_sidereal_longitudes(jd)[1] - get_sidereal_longitudes(jd)[0]) % 360) / 6.0)
    
    tithi_end_jd = find_transition(jd_calc, get_tithi_idx)
    nakshatra_end_jd = find_transition(jd_calc, get_nakshatra_idx)
    yoga_end_jd = find_transition(jd_calc, get_yoga_idx)
    karana_end_jd = find_transition(jd_calc, get_karana_idx)

    tithi_end = jd_to_time_str(tithi_end_jd)
    nakshatra_end = jd_to_time_str(nakshatra_end_jd)
    yoga_end = jd_to_time_str(yoga_end_jd)
    karana_end = jd_to_time_str(karana_end_jd)

    # Next (second) elements
    tithi_2_name = "--"
    tithi_2_end = "--"
    if tithi_end_jd is not None:
        tithi_2_idx = get_tithi_idx(tithi_end_jd + 0.001)
        tithi_2_name = TITHIS[lang][tithi_2_idx]
        tithi_2_end_jd = find_transition(tithi_end_jd + 0.001, get_tithi_idx)
        tithi_2_end = jd_to_time_str(tithi_2_end_jd)
        
    nakshatra_2_name = "--"
    nakshatra_2_end = "--"
    if nakshatra_end_jd is not None:
        nakshatra_2_idx = get_nakshatra_idx(nakshatra_end_jd + 0.001)
        nakshatra_2_name = NAKSHATRAS[lang][nakshatra_2_idx]
        nakshatra_2_end_jd = find_transition(nakshatra_end_jd + 0.001, get_nakshatra_idx)
        nakshatra_2_end = jd_to_time_str(nakshatra_2_end_jd)
        
    yoga_2_name = "--"
    yoga_2_end = "--"
    if yoga_end_jd is not None:
        yoga_2_idx = get_yoga_idx(yoga_end_jd + 0.001)
        yoga_2_name = YOGAS[lang][yoga_2_idx]
        yoga_2_end_jd = find_transition(yoga_end_jd + 0.001, get_yoga_idx)
        yoga_2_end = jd_to_time_str(yoga_2_end_jd)
        
    karana_2_name = "--"
    karana_2_end = "--"
    if karana_end_jd is not None:
        karana_2_idx = get_karana_idx(karana_end_jd + 0.001)
        karana_2_name = get_karana_name_from_idx(karana_2_idx, lang)
        karana_2_end_jd = find_transition(karana_end_jd + 0.001, get_karana_idx)
        karana_2_end = jd_to_time_str(karana_2_end_jd)

    # Ghadi-Pal time calculation (local time) using high-precision UTC with microseconds
    dt_utc = datetime.datetime.now(datetime.timezone.utc)
    jd_now_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                           dt_utc.hour + dt_utc.minute/60.0 + 
                           (dt_utc.second + dt_utc.microsecond/1000000.0)/3600.0)
    
    # Determine if today is selected
    dt_local = dt_utc + datetime.timedelta(hours=tz)
    is_today = (dt_local.year == year and dt_local.month == month and dt_local.day == day)
    
    tithi_active_idx = 0
    nakshatra_active_idx = 0
    yoga_active_idx = 0
    karana_active_idx = 0
    
    if is_today:
        tithi_active_idx = 2 if (tithi_end_jd is not None and jd_now_ut > tithi_end_jd) else 1
        nakshatra_active_idx = 2 if (nakshatra_end_jd is not None and jd_now_ut > nakshatra_end_jd) else 1
        yoga_active_idx = 2 if (yoga_end_jd is not None and jd_now_ut > yoga_end_jd) else 1
        karana_active_idx = 2 if (karana_end_jd is not None and jd_now_ut > karana_end_jd) else 1

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

    # Brahma Muhurta (starts 96 mins before sunrise, ends 48 mins before sunrise)
    brahma_start = sunrise_jd - (96.0 / 1440.0)
    brahma_end = sunrise_jd - (48.0 / 1440.0)
    brahma_muhurta = f"{jd_to_time_str(brahma_start)} - {jd_to_time_str(brahma_end)}"

    # Choghadiya calculations
    day_duration = sunset_jd - sunrise_jd
    day_part = day_duration / 8.0
    
    # Tomorrow's sunrise for night Choghadiya
    night_duration = tomorrow_sunrise_jd - sunset_jd
    night_part = night_duration / 8.0
    
    day_choghadiyas = []
    night_choghadiyas = []
    
    for i in range(8):
        # Day segment
        d_start = sunrise_jd + i * day_part
        d_end = sunrise_jd + (i + 1) * day_part
        d_idx = (CHOGHADIYA_DAY_START[vaara_idx] + i) % 7
        d_name = CHOGHADIYAS[lang][d_idx]
        day_choghadiyas.append({
            "name": d_name,
            "start": jd_to_time_str(d_start),
            "end": jd_to_time_str(d_end),
            "nature": CHOGHADIYA_NATURES[lang][d_name]
        })
        
        # Night segment
        n_start = sunset_jd + i * night_part
        n_end = sunset_jd + (i + 1) * night_part
        n_idx = (CHOGHADIYA_NIGHT_START[vaara_idx] + i) % 7
        n_name = CHOGHADIYAS[lang][n_idx]
        night_choghadiyas.append({
            "name": n_name,
            "start": jd_to_time_str(n_start),
            "end": jd_to_time_str(n_end),
            "nature": CHOGHADIYA_NATURES[lang][n_name]
        })

    # Determine if we are calculating for today

    
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
                
    # 1. Sankrantis: Sun enters any Rashi (we check if Sun's Rashi changes from today to tomorrow)
    sun_long_today, _ = get_sidereal_longitudes(sunrise_jd)
    jd_next_sunrise = sunrise_jd + 1.0
    sun_long_next, _ = get_sidereal_longitudes(jd_next_sunrise)
    
    rashi_today = int(sun_long_today / 30.0)
    rashi_tomorrow = int(sun_long_next / 30.0)
    
    if rashi_today != rashi_tomorrow:
        # Crosses boundary
        SANKRANTIS = {
            "en": ["Mesha Sankranti", "Vrishabha Sankranti", "Mithuna Sankranti", "Karka Sankranti", "Simha Sankranti", "Kanya Sankranti", "Tula Sankranti", "Vrishchika Sankranti", "Dhanu Sankranti", "Makar Sankranti", "Kumbha Sankranti", "Meena Sankranti"],
            "iast": ["Meṣa Saṅkrānti", "Vṛṣabha Saṅkrānti", "Mithuna Saṅkrānti", "Karka Saṅkrānti", "Siṃha Saṅkrānti", "Kanyā Saṅkrānti", "Tulā Saṅkrānti", "Vṛścika Saṅkrānti", "Dhanu Saṅkrānti", "Makara Saṅkrānti", "Kumbha Saṅkrānti", "Mīna Saṅkrānti"],
            "devanagari": ["मेष संक्रान्ति", "वृषभ संक्रान्ति", "मिथुन संक्रान्ति", "कर्क संक्रान्ति", "सिंह संक्रान्ति", "कन्या संक्रान्ति", "तुला संक्रान्ति", "वृश्चिक संक्रान्ति", "धनु संक्रान्ति", "मकर संक्रान्ति", "कुम्भ संक्रान्ति", "मीन संक्रान्ति"]
        }
        festivals.append(SANKRANTIS[lang][rashi_tomorrow])

    # 2. Lunar month and Tithi based festivals
    amav_masa_idx, _, _, _, _ = get_lunar_month_details(jd_calc, "amavasyanta")
    
    # Predefined Hindu festivals mapping
    # (month_idx, is_krishna, tithi_num_idx, en, iast, devanagari)
    festivals_db = [
        # Chaitra Shukla Pratipada: Ugadi / Gudi Padwa
        (0, False, 0, "Ugadi / Gudi Padwa", "Yugādi / Guḍhī Pāḍavā", "युगादि / गुढी पाडवा"),
        # Chaitra Shukla Navami: Ram Navami
        (0, False, 8, "Rama Navami", "Rāma Navamī", "राम नवमी"),
        # Chaitra Purnima: Hanuman Janmotsav
        (0, False, 14, "Hanuman Janmotsav", "Hanumān Janmotsava", "हनुमान जन्मोत्सव"),
        # Vaishakha Shukla Tritiya: Akshaya Tritiya
        (1, False, 2, "Akshaya Tritiya", "Akṣaya Tṛtīyā", "अक्षय तृतीया"),
        # Jyeshtha Amavasya: Vat Savitri Vrat (Amavasya)
        (2, True, 29, "Vat Savitri Vrat (Amavasya)", "Vaṭa Sāvitrī Vrata (Amāvāsyā)", "वट सावित्री व्रत (अमावस्या)"),
        # Jyeshtha Purnima: Vat Savitri Vrat (Purnima)
        (2, False, 14, "Vat Savitri Vrat (Purnima)", "Vaṭa Sāvitrī Vrata (Pūrṇimā)", "वट सावित्री व्रत (पूर्णिमा)"),
        # Ashadha Purnima: Guru Purnima
        (3, False, 14, "Guru Purnima", "Guru Pūrṇimā", "गुरु पूर्णिमा"),
        # Shravana Krishna Ashtami: Krishna Janmashtami
        (4, True, 22, "Krishna Janmashtami", "Kṛṣṇa Janmāṣṭamī", "कृष्ण जन्माष्टमी"),
        # Shravana Purnima: Raksha Bandhan
        (4, False, 14, "Raksha Bandhan", "Rakṣābandhana", "रक्षाबन्धन"),
        # Bhadrapada Shukla Chaturthi: Ganesh Chaturthi
        (5, False, 3, "Ganesh Chaturthi", "Gaṇeśa Caturthī", "गणेश चतुर्थी"),
        # Bhadrapada Shukla Chaturdashi: Anant Chaturdashi
        (5, False, 13, "Anant Chaturdashi", "Ananta Caturdaśī", "अनन्त चतुर्दशी"),
        # Ashvina Shukla Navami: Maha Navami
        (6, False, 8, "Maha Navami", "Mahā Navamī", "महानवमी"),
        # Ashvina Shukla Dashami: Dasara / Vijayadashami
        (6, False, 9, "Dasara / Vijayadashami", "Dasaharā / Vijayadaśamī", "दशहरा / विजयादशमी"),
        # Ashvina Amavasya: Deepawali (Diwali)
        (6, True, 29, "Deepawali", "Dīpāvalī", "दीपावली"),
        # Kartika Shukla Dwadashi: Tulsi Vivah
        (7, False, 11, "Tulsi Vivah", "Tulasī Vivāha", "तुलसी विवाह"),
        # Phalguna Krishna Chaturdashi: Maha Shivaratri
        (11, True, 28, "Maha Shivaratri", "Mahā Śivarātri", "महाशिवरात्रि"),
        # Phalguna Purnima: Holi
        (11, False, 14, "Holi", "Holī", "होली")
    ]
    
    for m_idx, is_k, t_idx, name_en, name_iast, name_dev in festivals_db:
        if amav_masa_idx == m_idx and is_krishna == is_k and t_num_idx == t_idx:
            fname = name_dev if lang == "devanagari" else (name_iast if lang == "iast" else name_en)
            festivals.append(fname)
            
    # 3. Sankashti Chaturthi (Krishna Paksha Chaturthi of every month)
    if is_krishna and t_num_idx == 18:
        sc_name = "Sankashti Chaturthi"
        if lang == "devanagari":
            sc_name = "संकष्टी चतुर्थी"
        elif lang == "iast":
            sc_name = "Saṅkaṣṭī Caturthī"
        festivals.append(sc_name)
        
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
        "paksha": paksha_name,
        "masa": masa_name,
        "nakshatra": nakshatra_active_name,
        "nakshatra_end": nakshatra_end,
        "nakshatra_1": nakshatra_name,
        "nakshatra_1_end": nakshatra_end,
        "nakshatra_2": nakshatra_2_name,
        "nakshatra_2_end": nakshatra_2_end,
        "nakshatra_active_idx": nakshatra_active_idx,
        "yoga": yoga_active_name,
        "yoga_end": yoga_end,
        "yoga_1": yoga_name,
        "yoga_1_end": yoga_end,
        "yoga_2": yoga_2_name,
        "yoga_2_end": yoga_2_end,
        "yoga_active_idx": yoga_active_idx,
        "karana": karana_active_name,
        "karana_end": karana_end,
        "karana_1": karana_name,
        "karana_1_end": karana_end,
        "karana_2": karana_2_name,
        "karana_2_end": karana_2_end,
        "karana_active_idx": karana_active_idx,
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
    print(f"Kālachakra Panchanga Engine starting on port {port}...")
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
