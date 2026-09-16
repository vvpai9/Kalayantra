#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KalaUtsavachakra — Festival & Ritual Calculation Engine.

Computes all festivals, Vratas, monthly observances, Sankrantis,
Sankashti Chaturthis, Ekadashis (Smarta vs Vaishnava), and custom
user observances.

Contains no astronomical solvers; it queries KalaChakra for raw
sidereal parameters (sun/moon longitudes, sunrise/sunset, tithi,
masa) and resolves named observances from KalaKosha metadata.
"""

import datetime

import KalaChakra
import KalaKosha


def get_tithi_at_jd(jd: float) -> int:
    """Tithi index (0..29) prevailing at a given Julian Day."""
    sun_l, moon_l = KalaChakra.get_sidereal_longitudes(jd)
    return int(((moon_l - sun_l) % 360.0) / 12.0)


def get_masa_at_jd(jd: float, month_system: str = "amavasyanta") -> int:
    """Lunar month index (0..11) prevailing at a given Julian Day."""
    masa_idx, _, _, _, _ = KalaChakra.get_lunar_month_details(jd, month_system)
    return masa_idx


def resolve_festival_details(key: str, metadata_key: str, lang: str) -> dict:
    """Build a festival dict from KalaKosha.FESTIVAL_METADATA."""
    meta = KalaKosha.FESTIVAL_METADATA.get(metadata_key, {})
    name = meta.get(lang, meta.get("en", metadata_key))
    return {
        "name": name,
        "type": meta.get("type", "Vrata"),
        "color": meta.get("color", "#2ecc71"),
        "priority": meta.get("priority", 5),
        "description": meta.get("description", ""),
        "rule": meta.get("rule", "Tithi prevailing at Sunrise"),
        "notify": meta.get("notify", "normal"),
    }


def datetime_to_vaara_idx(date_str: str) -> int:
    """Weekday index (Monday=0) for a 'YYYY-MM-DD' date string."""
    parts = date_str.split('-')
    dt = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
    return dt.weekday()


# ---------------------------------------------------------------------------
# Core festival solver
# ---------------------------------------------------------------------------

def _calculate_festivals_internal(astro_data: dict, tz: float,
                                  custom_observances=None,
                                  festival_rule: str = "vaishnava",
                                  lang: str = "en") -> list:
    festivals = []

    sunrise_jd = astro_data["sunrise_jd"]
    sunset_jd = astro_data["sunset_jd"]
    tomorrow_sunrise_jd = astro_data["tomorrow_sunrise_jd"]
    jd_ut_start = astro_data["jd_ut_start"]
    jd_calc = astro_data["jd_calc"]

    lat = astro_data.get("lat", 23.1765)
    lon = astro_data.get("lon", 75.7885)
    alt = astro_data.get("alt", 0.0)

    is_saura = (astro_data.get("paksha") == "")
    if is_saura:
        _, _, is_krishna_lunar, tithi_idx_lunar, _ = \
            KalaChakra.get_lunar_month_details(jd_calc, "amavasyanta")
        t_sunrise = tithi_idx_lunar
        is_krishna = is_krishna_lunar
    else:
        t_sunrise = astro_data["tithi_idx"]
        is_krishna = astro_data["is_krishna_paksha"]

    masa_idx = get_masa_at_jd(jd_calc, "amavasyanta")
    vaara_idx = datetime_to_vaara_idx(astro_data["date"])

    # Traditional time points (in JD)
    jd_noon = (sunrise_jd + sunset_jd) / 2.0
    jd_nishitha = (sunset_jd + tomorrow_sunrise_jd) / 2.0
    jd_pradosha = sunset_jd + 36.0 / 1440.0  # mid-point of Pradosha (72 min)
    jd_arunodaya = sunrise_jd - 48.0 / 1440.0  # 96 minutes before sunrise

    moonrise_jd = astro_data["moonrise_jd"]
    jd_moonrise = moonrise_jd if moonrise_jd and moonrise_jd > 0.0 else sunset_jd

    t_noon = get_tithi_at_jd(jd_noon)
    t_pradosha = get_tithi_at_jd(jd_pradosha)
    t_nishitha = get_tithi_at_jd(jd_nishitha)
    t_arunodaya = get_tithi_at_jd(jd_arunodaya)
    t_moonrise = get_tithi_at_jd(jd_moonrise)

    masa_noon = get_masa_at_jd(jd_noon)
    masa_pradosha = get_masa_at_jd(jd_pradosha)
    masa_nishitha = get_masa_at_jd(jd_nishitha)

    # --- 1. Authentic Dharmaśāstra festival solvers ---

    # Ugadi / Gudi Padwa: Chaitra Shukla Pratipada (Udaya-vyapini)
    if masa_idx == 0 and not is_krishna and t_sunrise == 0:
        festivals.append(resolve_festival_details("gudi_padwa", "gudi_padwa", lang))

    # Rama Navami: Chaitra Shukla Navami at Madhyahna (Noon)
    if masa_noon == 0 and t_noon == 8:
        festivals.append(resolve_festival_details("rama_navami", "rama_navami", lang))

    # Hanuman Janmotsav: Chaitra Purnima (Udaya-vyapini)
    if masa_idx == 0 and not is_krishna and t_sunrise == 14:
        festivals.append(resolve_festival_details("hanuman_janmotsav", "hanuman_janmotsav", lang))

    # Parashurama Jayanti: Vaishakha Shukla Tritiya at Pradosha
    if masa_pradosha == 1 and t_pradosha == 2:
        festivals.append(resolve_festival_details("parashurama_jayanti", "parashurama_jayanti", lang))

    # Akshaya Tritiya: Vaishakha Shukla Tritiya (Udaya-vyapini)
    if masa_idx == 1 and not is_krishna and t_sunrise == 2:
        festivals.append(resolve_festival_details("akshaya_tritiya", "akshaya_tritiya", lang))

    # Narasimha Jayanti: Vaishakha Shukla Chaturdashi at Pradosha
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

    # Raksha Bandhan / Upakarma: Shravana Purnima at Aparahna (Noon)
    if masa_noon == 4 and t_noon == 14:
        festivals.append(resolve_festival_details("raksha_bandhan", "raksha_bandhan", lang))

    # Varamahalakshmi Vrata: Friday preceding Shravana Purnima
    if vaara_idx == 4 and masa_idx == 4 and not is_krishna:
        for d_ahead in range(1, 8):
            jd_fut = jd_calc + d_ahead
            if get_tithi_at_jd(jd_fut) == 14 and get_masa_at_jd(jd_fut) == 4:
                festivals.append(
                    resolve_festival_details("varamahalakshmi_vrata", "varamahalakshmi_vrata", lang))
                break

    # Krishna Janmashtami: Shravana Krishna Ashtami at Nishitha (Midnight)
    if masa_nishitha == 4 and t_nishitha == 22:
        festivals.append(resolve_festival_details("krishna_janmashtami", "krishna_janmashtami", lang))

    # Swarna Gauri: Bhadrapada Shukla Tritiya (Udaya-vyapini)
    if masa_idx == 5 and not is_krishna and t_sunrise == 2:
        festivals.append(resolve_festival_details("swarna_gauri", "swarna_gauri", lang))

    # Ganesh Chaturthi: Bhadrapada Shukla Chaturthi at Madhyahna (Noon)
    if masa_noon == 5 and t_noon == 3:
        festivals.append(resolve_festival_details("ganesh_chaturthi", "ganesh_chaturthi", lang))

    # Rishi Panchami: Bhadrapada Shukla Panchami at Madhyahna (Noon)
    if masa_noon == 5 and t_noon == 4:
        festivals.append(resolve_festival_details("rishi_panchami", "rishi_panchami", lang))

    # Ananta Chaturdashi: Bhadrapada Shukla Chaturdashi (Udaya-vyapini)
    if masa_idx == 5 and not is_krishna and t_sunrise == 13:
        festivals.append(resolve_festival_details("ananta_chaturdashi", "ananta_chaturdashi", lang))

    # Mahalaya Amavasya: Bhadrapada Amavasya (Pradosha-vyapini)
    if masa_pradosha == 5 and t_pradosha == 29:
        festivals.append(resolve_festival_details("mahalaya_amavasya", "mahalaya_amavasya", lang))

    # Mahanavami: Ashvina Shukla Navami at Madhyahna/Pradosha
    if masa_noon == 6 and t_noon == 8:
        festivals.append(resolve_festival_details("mahanavami", "mahanavami", lang))

    # Vijayadashami: Ashvina Shukla Dashami at Aparahna (Noon)
    if masa_noon == 6 and t_noon == 9:
        festivals.append(resolve_festival_details("vijayadashami", "vijayadashami", lang))

    # Kojagari Purnima: Ashvina Purnima at Nishitha (Midnight)
    if masa_nishitha == 6 and t_nishitha == 14:
        festivals.append(resolve_festival_details("kojagari_purnima", "kojagari_purnima", lang))

    # Naraka Chaturdashi: Ashvina Krishna Chaturdashi at Arunodaya (Pre-dawn)
    if masa_idx == 6 and is_krishna and t_arunodaya == 28:
        festivals.append(resolve_festival_details("naraka_chaturdashi", "naraka_chaturdashi", lang))

    # Deepavali / Laxmi Puja: Ashvina Amavasya at Pradosha (Evening)
    if masa_pradosha == 6 and t_pradosha == 29:
        festivals.append(resolve_festival_details("deepavali", "deepavali", lang))

    # Bali Pratipada: Kartika Shukla Pratipada (Udaya-vyapini)
    if masa_idx == 7 and not is_krishna and t_sunrise == 0:
        festivals.append(resolve_festival_details("bali_pratipada", "bali_pratipada", lang))

    # Tulsi Vivah: Kartika Shukla Dwadashi at Pradosha
    if masa_pradosha == 7 and t_pradosha == 11:
        festivals.append(resolve_festival_details("tulsi_vivah", "tulsi_vivah", lang))

    # Champa Shashthi: Margashirsha Shukla Shashti (Udaya-vyapini)
    if masa_idx == 8 and not is_krishna and t_sunrise == 5:
        festivals.append(resolve_festival_details("champa_shashthi", "champa_shashthi", lang))

    # Datta Jayanti: Margashirsha Purnima at Pradosha
    if masa_pradosha == 8 and t_pradosha == 14:
        festivals.append(resolve_festival_details("datta_jayanti", "datta_jayanti", lang))

    # Ratha Saptami: Magha Shukla Saptami at Arunodaya (Pre-dawn)
    if masa_idx == 10 and not is_krishna and t_arunodaya == 6:
        festivals.append(resolve_festival_details("ratha_saptami", "ratha_saptami", lang))

    # Bhishma Ashtami: Magha Shukla Ashtami at Madhyahna (Noon)
    if masa_noon == 10 and t_noon == 7:
        festivals.append(resolve_festival_details("bhishma_ashtami", "bhishma_ashtami", lang))

    # Madhwa Navami: Magha Shukla Navami (Udaya-vyapini)
    if masa_idx == 10 and not is_krishna and t_sunrise == 8:
        festivals.append(resolve_festival_details("madhwa_navami", "madhwa_navami", lang))

    # Mahashivaratri: Magha Krishna Chaturdashi at Nishitha (Midnight)
    if masa_nishitha == 10 and t_nishitha == 28:
        festivals.append(resolve_festival_details("mahashivaratri", "mahashivaratri", lang))

    # Holi: Phalguna Purnima at Pradosha (Evening)
    if masa_pradosha == 11 and t_pradosha == 14:
        festivals.append(resolve_festival_details("holi", "holi", lang))

    # --- 2. Monthly observance solvers ---

    # Sankashti Chaturthi: Krishna Chaturthi prevailing at Moonrise
    if is_krishna and t_moonrise == 18:
        festivals.append({
            "name": KalaKosha.FESTIVAL_METADATA["sankashti_chaturthi"][lang],
            "type": "Vrata",
            "color": "#9b59b6",
            "priority": 7,
            "description": "Monthly fast for Lord Ganesha, broken after observing the Moon.",
            "rule": "Krishna Chaturthi prevailing at Moonrise",
            "notify": "normal",
        })

    # Sankrantis: Sun transfers between Rashis
    sun_long_today, _ = KalaChakra.get_sidereal_longitudes(sunrise_jd)
    sun_long_next, _ = KalaChakra.get_sidereal_longitudes(sunrise_jd + 1.0)

    rashi_today = int(sun_long_today / 30.0)
    rashi_tomorrow = int(sun_long_next / 30.0)
    if rashi_today != rashi_tomorrow:
        rashi_now = rashi_tomorrow % 12
        s_name = KalaKosha.SANKRANTIS[lang][rashi_now]
        festivals.append({
            "name": s_name,
            "type": "Sankranti",
            "color": "#e67e22",
            "priority": 8,
            "description": f"Sun entering the zodiac sign of {KalaKosha.SANKRANTIS['en'][rashi_now].split(' ')[0]}.",
            "rule": "Solar Rashi Transition",
            "notify": "normal",
        })

    # Ekadashis: Shukla (t_sunrise == 10) and Krishna (t_sunrise == 25)
    shukla_ekadashi = (t_sunrise == 10)
    krishna_ekadashi = (t_sunrise == 25)

    if shukla_ekadashi or krishna_ekadashi:
        is_adhika = astro_data.get("is_adhika", False)
        masa_key = "adhika" if is_adhika else masa_idx
        ekadashi_key = (masa_key, not shukla_ekadashi)
        ekadashi_meta = KalaKosha.EKADASHI_NAMES.get(
            ekadashi_key,
            {"en": "Ekadashi", "iast": "Ekādaśī", "devanagari": "एकादशी"},
        )
        ekadashi_name = ekadashi_meta.get(lang, ekadashi_meta.get("en", "Ekadashi"))

        if festival_rule == "smarta":
            festivals.append({
                "name": ekadashi_name,
                "type": "Ekadashi",
                "color": "#3498db",
                "priority": 9,
                "description": f"{ekadashi_name} fast observed by Smartas.",
                "rule": "Tithi prevailing at Sunrise (Udaya-vyapini)",
                "notify": "high",
            })
        else:
            # Vaishnava rule: viddha (mixed with Dashami) if Dashami was
            # prevailing at Arunodaya (48 min before sunrise).
            is_viddha = (t_arunodaya in (9, 24))
            if not is_viddha:
                festivals.append({
                    "name": ekadashi_name,
                    "type": "Ekadashi",
                    "color": "#3498db",
                    "priority": 9,
                    "description": f"{ekadashi_name} fast observed by Vaishnavas.",
                    "rule": "Vaishnava Arunodaya Vyapini (Unmixed with Dashami)",
                    "notify": "high",
                })

    # Dwadashi day: Vaishnava Ekadashi may have been pushed here
    if t_sunrise in (11, 26):
        shukla_dwadashi = (t_sunrise == 11)
        t_yest = get_tithi_at_jd(sunrise_jd - 1.0)

        yesterday_had_ekadashi = False
        yesterday_was_viddha = False

        if t_yest in (10, 25):
            yesterday_had_ekadashi = True
            yest_sunrise, _, _, _ = \
                KalaChakra.get_sun_moon_rise_set(jd_ut_start - 1.0, lat, lon, alt)
            yest_arunodaya_jd = yest_sunrise - 96.0 / 1440.0
            t_yest_aru = get_tithi_at_jd(yest_arunodaya_jd)
            yesterday_was_viddha = (t_yest_aru in (9, 24))
        else:
            yest_sunrise, _, _, _ = \
                KalaChakra.get_sun_moon_rise_set(jd_ut_start - 1.0, lat, lon, alt)
            yest_tithi_end_jd = KalaChakra.find_transition(yest_sunrise, get_tithi_at_jd)
            if yest_tithi_end_jd is not None:
                t_yest_2 = get_tithi_at_jd(yest_tithi_end_jd + 0.02)
                if t_yest_2 in (10, 25):
                    yesterday_had_ekadashi = True
                    yesterday_was_viddha = True

        if yesterday_had_ekadashi and yesterday_was_viddha and festival_rule == "vaishnava":
            is_adhika = astro_data.get("is_adhika", False)
            masa_key = "adhika" if is_adhika else masa_idx
            ekadashi_key = (masa_key, not shukla_dwadashi)
            ekadashi_meta = KalaKosha.EKADASHI_NAMES.get(
                ekadashi_key,
                {"en": "Ekadashi", "iast": "Ekādaśī", "devanagari": "एकादशी"},
            )
            ekadashi_name = ekadashi_meta.get(lang, ekadashi_meta.get("en", "Ekadashi"))
            festivals.append({
                "name": f"{ekadashi_name} (Vaishnava)",
                "type": "Ekadashi",
                "color": "#3498db",
                "priority": 9,
                "description": f"{ekadashi_name} Vaishnava fast observed on Dwadashi due to "
                               "Dashami-Ekadashi mixture or Kshaya yesterday.",
                "rule": "Vaishnava Dwadashi (Mahadvadashi)",
                "notify": "high",
            })

    # --- 3. Custom lunar observance solver ---
    if custom_observances:
        masa_en_ama = KalaKosha.MASAS["en"][masa_idx]
        masa_idx_purn = get_masa_at_jd(jd_calc, "purnimanta")
        masa_en_purn = KalaKosha.MASAS["en"][masa_idx_purn]
        paksha_en = KalaKosha.PAKSHAS["en"][1 if is_krishna else 0]
        tithi_en = KalaKosha.TITHIS["en"][t_sunrise]

        for obs in custom_observances:
            obs_masa = obs.get("month", "")
            obs_paksha = obs.get("paksha", "")
            obs_tithi = obs.get("tithi", "")
            obs_system = obs.get("system", "amavasyanta")

            target_masa = masa_en_purn if obs_system == "purnimanta" else masa_en_ama

            if obs_masa == target_masa and obs_paksha == paksha_en and obs_tithi == tithi_en:
                anniversary_display = ""
                g_year = obs.get("gregorian_year", None)
                if g_year is not None and str(g_year).strip() != "":
                    calc_year = int(astro_data["date"].split("-")[0])
                    anniversary = calc_year - int(g_year)
                    if anniversary > 0:
                        if lang == "devanagari":
                            ordinal = f"{anniversary}वीं"
                        else:
                            if 11 <= (anniversary % 100) <= 13:
                                suffix = "th"
                            else:
                                suffix = {1: "st", 2: "nd", 3: "rd"}.get(anniversary % 10, "th")
                            ordinal = f"{anniversary}{suffix}"

                        name_lower = obs.get("name", "").lower()
                        has_special = any(x in name_lower for x in
                                         ["birthday", "janmadin", "jayanti"])
                        if has_special:
                            anniversary_display = f"{ordinal} {obs.get('name', '')}"
                        else:
                            ann_word = "वर्षगांठ" if lang == "devanagari" else (
                                "Varṣagāṇṭha" if lang == "iast" else "Anniversary")
                            anniversary_display = f"{ordinal} {ann_word}"

                festivals.append({
                    "name": obs.get("name", "My Tithi"),
                    "type": "My Tithi",
                    "color": "#e91e63",
                    "priority": 6,
                    "description": f"My Tithi: User-saved recurring traditional lunar event "
                                   f"({obs_system.capitalize()} system).",
                    "rule": "Custom Lunar Match",
                    "notify": "normal",
                    "anniversary_display": anniversary_display,
                })

    festivals.sort(key=lambda x: x["priority"], reverse=True)
    return festivals


def calculate_festivals(astro_data: dict, tz: float,
                        custom_observances=None,
                        festival_rule: str = "vaishnava",
                        lang: str = "en") -> list:
    """Top-level festival list for a panchanga record.

    When the day contains a kshaya (skipped) tithi, the solver runs a
    second time with the skipped tithi as the active one and merges any
    additional festivals that surface.
    """
    has_kshaya = astro_data.get("is_tithi_2_kshaya", False)
    t_kshaya = astro_data.get("tithi_2_idx")

    astro_data_copy = dict(astro_data)
    astro_data_copy["is_tithi_2_kshaya"] = False

    festivals = _calculate_festivals_internal(
        astro_data_copy, tz, custom_observances, festival_rule, lang)

    if has_kshaya and t_kshaya is not None:
        astro_data_kshaya = dict(astro_data_copy)
        astro_data_kshaya["tithi_idx"] = t_kshaya
        kshaya_fests = _calculate_festivals_internal(
            astro_data_kshaya, tz, custom_observances, festival_rule, lang)

        existing_names = {f["name"] for f in festivals}
        for f in kshaya_fests:
            if f["name"] not in existing_names:
                festivals.append(f)

    festivals.sort(key=lambda x: x["priority"], reverse=True)
    return festivals


# ---------------------------------------------------------------------------
# Reminder evaluation
# ---------------------------------------------------------------------------

def evaluate_reminders(astro_data: dict, festivals: list, reminders: list,
                       lang: str = "en") -> list:
    """Evaluate user reminders against today's panchanga + festivals."""
    matched = []
    if not reminders:
        return matched

    tithi_1 = astro_data.get("tithi_1", "")
    tithi_2 = astro_data.get("tithi_2", "")
    tithi_active = astro_data.get("tithi", "")

    paksha = astro_data.get("paksha", "")
    masa = astro_data.get("masa", "")

    nakshatra_1 = astro_data.get("nakshatra_1", "")
    nakshatra_2 = astro_data.get("nakshatra_2", "")
    nakshatra_active = astro_data.get("nakshatra", "")

    vaara = astro_data.get("vaara", "")

    today_tithis = {t for t in [tithi_1, tithi_2, tithi_active] if t and t != "--"}
    today_nakshatras = {n for n in [nakshatra_1, nakshatra_2, nakshatra_active] if n and n != "--"}

    has_sankranti = any(
        f.get("type") == "Sankranti" or "sankranti" in f.get("name", "").lower()
        for f in festivals)

    for r in reminders:
        if not r.get("enabled", True):
            continue

        r_type = r.get("type", "")
        params = r.get("params", {})
        is_match = False

        if r_type == "tithi":
            r_tithi = params.get("tithi", "")
            if r_tithi in today_tithis:
                is_match = True

        elif r_type == "paksha_tithi":
            r_paksha = params.get("paksha", "")
            r_tithi = params.get("tithi", "")
            if r_paksha == paksha and r_tithi in today_tithis:
                is_match = True

        elif r_type == "masa_paksha_tithi":
            r_masa = params.get("masa", "")
            r_paksha = params.get("paksha", "")
            r_tithi = params.get("tithi", "")
            if r_masa == masa and r_paksha == paksha and r_tithi in today_tithis:
                is_match = True

        elif r_type == "nakshatra":
            r_nakshatra = params.get("nakshatra", "")
            if r_nakshatra in today_nakshatras:
                is_match = True

        elif r_type == "vara_tithi":
            r_vara = params.get("vara", "")
            r_tithi = params.get("tithi", "")
            if r_vara == vaara and r_tithi in today_tithis:
                is_match = True

        elif r_type == "sankranti":
            if has_sankranti:
                is_match = True

        elif r_type == "festival":
            r_fest = params.get("festival_name", "").lower().strip()
            for f in festivals:
                if r_fest == f.get("name", "").lower().strip():
                    is_match = True
                    break

        if is_match:
            matched.append(r)

    return matched