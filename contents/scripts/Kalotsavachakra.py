#!/usr/bin/env python3
"""
Kalotsavachakra - Festival & Ritual Calculation Engine
Calculates all festivals, Vratas, monthly observances, Sankrantis,
Sankashti Chaturthis, Ekadashis (Smarta vs Vaishnava), and custom observances.
Contains no astronomical solvers; queries Kalachakra for raw parameters.
"""
import os
import json
import datetime
import Kalachakra
import Kalakosha

def get_tithi_at_jd(jd):
    sun_l, moon_l = Kalachakra.get_sidereal_longitudes(jd)
    tithi_val = ((moon_l - sun_l) % 360) / 12.0
    return int(tithi_val)


def get_masa_at_jd(jd, month_system="amavasyanta"):
    masa_idx, _, _, _, _ = Kalachakra.get_lunar_month_details(jd, month_system)
    return masa_idx


def resolve_festival_details(key, metadata_key, lang):
    meta = Kalakosha.FESTIVAL_METADATA.get(metadata_key, {})
    name = meta.get(lang, meta.get("en", metadata_key))
    return {
        "name": name,
        "type": meta.get("type", "Vrata"),
        "color": meta.get("color", "#2ecc71"),
        "priority": meta.get("priority", 5),
        "description": meta.get("description", ""),
        "rule": meta.get("rule", "Tithi prevailing at Sunrise"),
        "notify": meta.get("notify", "normal")
    }


def calculate_festivals(astro_data, tz, custom_observances=None, festival_rule="vaishnava", lang="en"):
    festivals = []
    
    # Extract raw parameters from astro_data
    sunrise_jd = astro_data["sunrise_jd"]
    sunset_jd = astro_data["sunset_jd"]
    tomorrow_sunrise_jd = astro_data["tomorrow_sunrise_jd"]
    jd_ut_start = astro_data["jd_ut_start"]
    jd_calc = astro_data["jd_calc"]
    
    masa_idx = get_masa_at_jd(jd_calc, "amavasyanta")
    t_num_idx = astro_data["tithi_idx"]
    is_krishna = astro_data["is_krishna_paksha"]
    vaara_idx = datetime_to_vaara_idx(astro_data["date"])
    
    # Calculate traditional time points in JDs
    jd_noon = (sunrise_jd + sunset_jd) / 2.0
    jd_nishitha = (sunset_jd + tomorrow_sunrise_jd) / 2.0
    jd_pradosha = sunset_jd + 36.0 / 1440.0 # Midpoint of Pradosha (72 mins duration)
    jd_arunodaya = sunrise_jd - 48.0 / 1440.0 # 96 minutes before sunrise
    
    moonrise_jd = astro_data["moonrise_jd"]
    jd_moonrise = moonrise_jd if moonrise_jd > 0.0 else sunset_jd
    
    # Resolve tithis at critical time points
    t_sunrise = t_num_idx
    t_noon = get_tithi_at_jd(jd_noon)
    t_pradosha = get_tithi_at_jd(jd_pradosha)
    t_nishitha = get_tithi_at_jd(jd_nishitha)
    t_arunodaya = get_tithi_at_jd(jd_arunodaya)
    t_moonrise = get_tithi_at_jd(jd_moonrise)
    
    # Resolve masa at noon to confirm boundary transitions
    masa_noon = get_masa_at_jd(jd_noon)
    masa_pradosha = get_masa_at_jd(jd_pradosha)
    masa_nishitha = get_masa_at_jd(jd_nishitha)
    
    # --- 1. Authentic Dharmaśāstra Festival Solvers ---
    
    # Ugadi / Gudi Padwa: Chaitra Shukla Pratipada (Udaya-vyapini)
    if masa_idx == 0 and not is_krishna and t_sunrise == 0:
        festivals.append(resolve_festival_details("gudi_padwa", "gudi_padwa", lang))
        
    # Rama Navami: Chaitra Shukla Navami prevailing at Madhyahna (Noon)
    if masa_noon == 0 and t_noon == 8:
        festivals.append(resolve_festival_details("rama_navami", "rama_navami", lang))
        
    # Hanuman Janmotsav: Chaitra Purnima (Udaya-vyapini)
    if masa_idx == 0 and not is_krishna and t_sunrise == 14:
        festivals.append(resolve_festival_details("hanuman_janmotsav", "hanuman_janmotsav", lang))
        
    # Parashurama Jayanti: Vaishakha Shukla Tritiya prevailing during Pradosha
    if masa_pradosha == 1 and t_pradosha == 2:
        festivals.append(resolve_festival_details("parashurama_jayanti", "parashurama_jayanti", lang))
        
    # Akshaya Tritiya: Vaishakha Shukla Tritiya (Udaya-vyapini / Purvahna)
    if masa_idx == 1 and not is_krishna and t_sunrise == 2:
        festivals.append(resolve_festival_details("akshaya_tritiya", "akshaya_tritiya", lang))
        
    # Narasimha Jayanti: Vaishakha Shukla Chaturdashi prevailing at Pradosha
    if masa_pradosha == 1 and t_pradosha == 13:
        festivals.append(resolve_festival_details("narasimha_jayanti", "narasimha_jayanti", lang))
        
    # Vat Savitri Vrata (Amavasya): Jyeshtha Amavasya (Udaya-vyapini)
    if masa_idx == 2 and is_krishna and t_sunrise == 29:
        festivals.append(resolve_festival_details("vat_savitri_amavasya", "vat_savitri_amavasya", lang))
        
    # Vat Savitri Vrata (Purnima): Jyeshtha Purnima (Udaya-vyapini)
    if masa_idx == 2 and not is_krishna and t_sunrise == 14:
        festivals.append(resolve_festival_details("vat_savitri_purnima", "vat_savitri_purnima", lang))
        
    # Guru Purnima: Ashadha Purnima (Udaya-vyapini)
    if masa_idx == 3 and not is_krishna and t_sunrise == 14:
        festivals.append(resolve_festival_details("guru_purnima", "guru_purnima", lang))
        
    # Nag Panchami: Shravana Shukla Panchami (Udaya-vyapini)
    if masa_idx == 4 and not is_krishna and t_sunrise == 4:
        festivals.append(resolve_festival_details("nag_panchami", "nag_panchami", lang))
        
    # Raksha Bandhan / Upakarma: Shravana Purnima prevailing during Aparahna (Noon-Afternoon)
    if masa_noon == 4 and t_noon == 14:
        festivals.append(resolve_festival_details("raksha_bandhan", "raksha_bandhan", lang))
        
    # Varamahalakshmi Vrata: Friday preceding Shravana Purnima
    if vaara_idx == 4 and masa_idx == 4 and not is_krishna:
        # Search ahead up to 7 days to see if Shravana Purnima occurs
        has_purnima_ahead = False
        for d_ahead in range(1, 8):
            jd_fut = jd_calc + d_ahead
            if get_tithi_at_jd(jd_fut) == 14 and get_masa_at_jd(jd_fut) == 4:
                has_purnima_ahead = True
                break
        if has_purnima_ahead:
            festivals.append(resolve_festival_details("varamahalakshmi_vrata", "varamahalakshmi_vrata", lang))
            
    # Krishna Janmashtami: Shravana Krishna Ashtami prevailing during Nishitha (Midnight)
    if masa_nishitha == 4 and t_nishitha == 22:
        festivals.append(resolve_festival_details("krishna_janmashtami", "krishna_janmashtami", lang))
        
    # Swarna Gauri: Bhadrapada Shukla Tritiya (Udaya-vyapini)
    if masa_idx == 5 and not is_krishna and t_sunrise == 2:
        festivals.append(resolve_festival_details("swarna_gauri", "swarna_gauri", lang))
        
    # Ganesh Chaturthi: Bhadrapada Shukla Chaturthi prevailing during Madhyahna (Noon)
    if masa_noon == 5 and t_noon == 3:
        festivals.append(resolve_festival_details("ganesh_chaturthi", "ganesh_chaturthi", lang))
        
    # Rishi Panchami: Bhadrapada Shukla Panchami prevailing during Madhyahna (Noon)
    if masa_noon == 5 and t_noon == 4:
        festivals.append(resolve_festival_details("rishi_panchami", "rishi_panchami", lang))
        
    # Ananta Chaturdashi: Bhadrapada Shukla Chaturdashi (Udaya-vyapini)
    if masa_idx == 5 and not is_krishna and t_sunrise == 13:
        festivals.append(resolve_festival_details("ananta_chaturdashi", "ananta_chaturdashi", lang))
        
    # Mahalaya Amavasya: Bhadrapada Amavasya (Aparahna/Pradosha-vyapini)
    if masa_pradosha == 5 and t_pradosha == 29:
        festivals.append(resolve_festival_details("mahalaya_amavasya", "mahalaya_amavasya", lang))
        
    # Mahanavami: Ashvina Shukla Navami prevailing during Madhyahna/Pradosha
    if masa_noon == 6 and t_noon == 8:
        festivals.append(resolve_festival_details("mahanavami", "mahanavami", lang))
        
    # Vijayadashami: Ashvina Shukla Dashami prevailing during Aparahna (Noon/Afternoon)
    if masa_noon == 6 and t_noon == 9:
        festivals.append(resolve_festival_details("vijayadashami", "vijayadashami", lang))
        
    # Kojagari Purnima: Ashvina Purnima prevailing during Nishitha (Midnight)
    if masa_nishitha == 6 and t_nishitha == 14:
        festivals.append(resolve_festival_details("kojagari_purnima", "kojagari_purnima", lang))
        
    # Naraka Chaturdashi: Ashvina Krishna Chaturdashi prevailing at Arunodaya (Pre-dawn)
    if masa_idx == 6 and is_krishna and t_arunodaya == 28:
        festivals.append(resolve_festival_details("naraka_chaturdashi", "naraka_chaturdashi", lang))
        
    # Deepavali / Laxmi Puja: Ashvina Amavasya prevailing during Pradosha (Evening)
    if masa_pradosha == 6 and t_pradosha == 29:
        festivals.append(resolve_festival_details("deepavali", "deepavali", lang))
        
    # Bali Pratipada: Kartika Shukla Pratipada (Udaya-vyapini)
    if masa_idx == 7 and not is_krishna and t_sunrise == 0:
        festivals.append(resolve_festival_details("bali_pratipada", "bali_pratipada", lang))
        
    # Tulsi Vivah: Kartika Shukla Dwadashi prevailing during Pradosha
    if masa_pradosha == 7 and t_pradosha == 11:
        festivals.append(resolve_festival_details("tulsi_vivah", "tulsi_vivah", lang))
        
    # Champa Shashthi: Margashirsha Shukla Shashti (Udaya-vyapini)
    if masa_idx == 8 and not is_krishna and t_sunrise == 5:
        festivals.append(resolve_festival_details("champa_shashthi", "champa_shashthi", lang))
        
    # Datta Jayanti: Margashirsha Purnima prevailing during Pradosha
    if masa_pradosha == 8 and t_pradosha == 14:
        festivals.append(resolve_festival_details("datta_jayanti", "datta_jayanti", lang))
        
    # Ratha Saptami: Magha Shukla Saptami prevailing at Arunodaya (Pre-dawn)
    if masa_idx == 10 and not is_krishna and t_arunodaya == 6:
        festivals.append(resolve_festival_details("ratha_saptami", "ratha_saptami", lang))
        
    # Bhishma Ashtami: Magha Shukla Ashtami prevailing during Madhyahna (Noon)
    if masa_noon == 10 and t_noon == 7:
        festivals.append(resolve_festival_details("bhishma_ashtami", "bhishma_ashtami", lang))
        
    # Madhwa Navami: Magha Shukla Navami (Udaya-vyapini)
    if masa_idx == 10 and not is_krishna and t_sunrise == 8:
        festivals.append(resolve_festival_details("madhwa_navami", "madhwa_navami", lang))
        
    # Mahashivaratri: Magha Krishna Chaturdashi prevailing during Nishitha (Midnight)
    if masa_nishitha == 10 and t_nishitha == 28:
        festivals.append(resolve_festival_details("mahashivaratri", "mahashivaratri", lang))
        
    # Holi: Phalguna Purnima prevailing during Pradosha (Evening)
    if masa_pradosha == 11 and t_pradosha == 14:
        festivals.append(resolve_festival_details("holi", "holi", lang))
        
    # --- 2. Monthly Observance Solvers ---
    
    # Sankashti Chaturthi: Krishna Chaturthi prevailing during Moonrise
    if is_krishna and t_moonrise == 18:
        festivals.append({
            "name": Kalakosha.FESTIVAL_METADATA["sankashti_chaturthi"][lang],
            "type": "Vrata",
            "color": "#9b59b6",
            "priority": 7,
            "description": "Monthly fast for Lord Ganesha, broken after observing the Moon.",
            "rule": "Krishna Chaturthi prevailing at Moonrise",
            "notify": "normal"
        })
        
    # Sankrantis: Sun transfers between Rashis
    sun_long_today, _ = Kalachakra.get_sidereal_longitudes(sunrise_jd)
    jd_next_sunrise = sunrise_jd + 1.0
    sun_long_next, _ = Kalachakra.get_sidereal_longitudes(jd_next_sunrise)
    
    rashi_today = int(sun_long_today / 30.0)
    rashi_tomorrow = int(sun_long_next / 30.0)
    if rashi_today != rashi_tomorrow:
        s_name = Kalakosha.SANKRANTIS[lang][rashi_tomorrow]
        festivals.append({
            "name": s_name,
            "type": "Sankranti",
            "color": "#e67e22",
            "priority": 8,
            "description": f"Sun entering the zodiac sign of {Kalakosha.SANKRANTIS['en'][rashi_tomorrow].split(' ')[0]}.",
            "rule": "Solar Rashi Transition",
            "notify": "normal"
        })
        
    # Ekadashis: Shukla (t_sunrise == 10) and Krishna (t_sunrise == 25)
    is_ekadashi_day = (t_sunrise == 10 or t_sunrise == 25)
    
    if is_ekadashi_day:
        shukla_ekadashi = (t_sunrise == 10)
        # Determine name of Ekadashi
        ekadashi_key = ("adhika" if astro_data.get("is_adhika", False) else masa_idx, not shukla_ekadashi)
        ekadashi_meta = Kalakosha.EKADASHI_NAMES.get(ekadashi_key, {"en": "Ekadashi", "iast": "Ekādaśī", "devanagari": "एकादशी"})
        ekadashi_name = ekadashi_meta[lang]
        
        if festival_rule == "smarta":
            festivals.append({
                "name": ekadashi_name,
                "type": "Ekadashi",
                "color": "#3498db",
                "priority": 9,
                "description": f"{ekadashi_name} fast observed by Smartas.",
                "rule": "Tithi prevailing at Sunrise (Udaya-vyapini)",
                "notify": "high"
            })
        else:
            # Vaishnava rule: check if Dashami was active at Arunodaya (96 mins before sunrise)
            # If t_arunodaya was Dashami (9 or 24), then it is viddha
            is_viddha = (t_arunodaya == 9 or t_arunodaya == 24)
            if not is_viddha:
                festivals.append({
                    "name": ekadashi_name,
                    "type": "Ekadashi",
                    "color": "#3498db",
                    "priority": 9,
                    "description": f"{ekadashi_name} fast observed by Vaishnavas.",
                    "rule": "Vaishnava Arunodaya Vyapini (Unmixed with Dashami)",
                    "notify": "high"
                })
                
    # Dwadashi Day: Check if Vaishnava Ekadashi was pushed to today
    if t_sunrise == 11 or t_sunrise == 26:
        shukla_dwadashi = (t_sunrise == 11)
        # Find yesterday's sunrise tithi
        jd_yest = sunrise_jd - 1.0
        t_yest = get_tithi_at_jd(jd_yest)
        
        # If yesterday was Ekadashi (10 or 25)
        if t_yest == 10 or t_yest == 25:
            # Check if yesterday was viddha at Arunodaya
            yest_sunrise_jd, _, _, _ = Kalachakra.get_sun_moon_rise_set(jd_ut_start - 1.0, astro_data.get("lat", 23.1765), astro_data.get("lon", 75.7885), astro_data.get("alt", 511.0))
            yest_arunodaya_jd = yest_sunrise_jd - (96.0 / 1440.0)
            t_yest_aru = get_tithi_at_jd(yest_arunodaya_jd)
            is_viddha = (t_yest_aru == 9 or t_yest_aru == 24)
            
            if is_viddha and festival_rule == "vaishnava":
                ekadashi_key = ("adhika" if astro_data.get("is_adhika", False) else masa_idx, not shukla_dwadashi)
                ekadashi_meta = Kalakosha.EKADASHI_NAMES.get(ekadashi_key, {"en": "Ekadashi", "iast": "Ekādaśī", "devanagari": "एकादशी"})
                ekadashi_name = ekadashi_meta[lang]
                festivals.append({
                    "name": f"{ekadashi_name} (Vaishnava)",
                    "type": "Ekadashi",
                    "color": "#3498db",
                    "priority": 9,
                    "description": f"{ekadashi_name} Vaishnava fast observed on Dwadashi due to Dashami-Ekadashi mixture at yesterday's Arunodaya.",
                    "rule": "Vaishnava Dwadashi (Mahadvadashi)",
                    "notify": "high"
                })

    # --- 3. Custom Lunar Observances Solver ---
    if custom_observances:
        # Resolve names of current day for comparison
        masa_en = Kalakosha.MASAS["en"][masa_idx]
        paksha_en = Kalakosha.PAKSHAS["en"][1 if is_krishna else 0]
        # Tithi name at sunrise or active
        tithi_en = Kalakosha.TITHIS["en"][t_sunrise]
        
        for obs in custom_observances:
            obs_masa = obs.get("month", "")
            obs_paksha = obs.get("paksha", "")
            obs_tithi = obs.get("tithi", "")
            if obs_masa == masa_en and obs_paksha == paksha_en and obs_tithi == tithi_en:
                festivals.append({
                    "name": obs.get("name", "Custom Observance"),
                    "type": "Custom",
                    "color": "#f1c40f",
                    "priority": 6,
                    "description": "User-defined recurring lunar observance.",
                    "rule": "Custom Lunar Match",
                    "notify": "normal"
                })

    # Sort festivals by priority descending
    festivals.sort(key=lambda x: x["priority"], reverse=True)
    return festivals


def datetime_to_vaara_idx(date_str):
    # Format YYYY-MM-DD
    parts = date_str.split('-')
    dt = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
    return dt.weekday()
