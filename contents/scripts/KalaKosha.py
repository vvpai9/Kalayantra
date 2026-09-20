# -*- coding: utf-8 -*-
"""
KalaKosha — the static knowledge base of Kālayantra.

This module contains ONLY data: multilingual name tables, planetary lordship
maps, classical compatibility tables, festival metadata and the offline city
registry.  No calculations are performed here.

Indexing conventions (documented in the module docstring):
    Planets   (grahas)    : 0..8  = Surya, Chandra, Mangala, Budha, Guru,
                                    Shukra, Shani, Rahu, Ketu
    Rāśi      (signs)     : 0..11 = Mesha .. Meena
    Nakṣatra  (stars)     : 0..26 = Ashvini .. Revati
    Tithi                 : 0..29 = Shukla Pratipada(0) .. Purnima(14),
                                    Krishna Pratipada(15) .. Amavasya(29)
    Vara      (weekday)   : 0..6  = Monday .. Sunday

All multilingual tables share the shape {"en": [...], "iast": [...],
"devanagari": [...]} unless noted otherwise.
"""

# ---------------------------------------------------------------------------
# 60-year Jovian cycle (Samvatsara)
# ---------------------------------------------------------------------------
SAMVATSARAS = {
    "en": ["Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati",
           "Angirasa", "Shrimukha", "Bhava", "Yuva", "Dhatu",
           "Ishvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha",
           "Chitrabhanu", "Svabhanu", "Tarana", "Parthiva", "Vyaya",
           "Sarvajit", "Sarvadhari", "Virodhi", "Vikriti", "Khara",
           "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukha",
           "Hevilambi", "Vilambi", "Vikari", "Sharvari", "Plava",
           "Shubhakrut", "Shobhakrut", "Krodhi", "Vishvavasu", "Parabhava",
           "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhakrit",
           "Paridhavi", "Pramadi", "Ananda", "Rakshasa", "Anala",
           "Pingala", "Kalayukta", "Siddharthi", "Raudra", "Durmati",
           "Dundubhi", "Rudhirodgari", "Raktaksha", "Krodhana", "Kshaya"],
    "iast": ["Prabhava", "Vibhava", "Śukla", "Pramoda", "Prajāpati",
             "Aṅgirasa", "Śrīmukha", "Bhāva", "Yuva", "Dhātu",
             "Īśvara", "Bahudhānya", "Pramāthi", "Vikrama", "Vṛṣa",
             "Citrabhānu", "Svabhānu", "Tāraṇa", "Pārthiva", "Vyaya",
             "Sarvajit", "Sarvadhārī", "Virodhi", "Vikṛti", "Khara",
             "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukha",
             "Hevilambi", "Vilambi", "Vikāri", "Śarvari", "Plava",
             "Śubhakṛt", "Śobhakṛt", "Krodhi", "Viśvāvasu", "Parābhava",
             "Plavaṅga", "Kīlaka", "Saumya", "Sādhāraṇa", "Virodhakṛt",
             "Paridhāvi", "Pramādi", "Ānanda", "Rākṣasa", "Anala",
             "Piṅgala", "Kālayukta", "Siddhārthi", "Raudra", "Durmati",
             "Dundubhi", "Rudhirodgāri", "Raktākṣa", "Krodhana", "Kṣaya"],
    "devanagari": ["प्रभव", "विभव", "शुक्ल", "प्रमोद", "प्रजापति",
                   "अङ्गिरस", "श्रीमुख", "भाव", "युव", "धातु",
                   "ईश्वर", "बहुधान्य", "प्रमाथि", "विक्रम", "वृष",
                   "चित्रभानु", "स्वभानु", "तारण", "पार्थिव", "व्यय",
                   "सर्वजित्", "सर्वधारी", "विरोधि", "विकृति", "खर",
                   "नन्दन", "विजय", "जय", "मन्मथ", "दुर्मुख",
                   "हेविलम्बि", "विलम्बि", "विकारि", "शर्वरी", "प्लव",
                   "शुभकृत्", "शोभकृत्", "क्रोधि", "विश्वावसु", "पराभव",
                   "प्लवङ्ग", "कीलक", "सौम्य", "साधारण", "विरोधिकृत्",
                   "परिधावि", "प्रमादि", "आनन्द", "राक्षस", "अनल",
                   "पिङ्गल", "कालयुक्त", "सिद्धार्थि", "रौद्र", "दुर्मति",
                   "दुन्दुभि", "रुधिरोद्गारि", "रक्ताक्ष", "क्रोधन", "क्षय"],
}

# ---------------------------------------------------------------------------
# Tithis — 30 entries: Shukla Pratipada(0) .. Purnima(14),
#                      Krishna Pratipada(15) .. Amavasya(29)
# ---------------------------------------------------------------------------
TITHIS = {
    "en": ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
           "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
           "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
           "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
           "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
           "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"],
    "iast": ["Pratipadā", "Dvitīyā", "Tṛtīyā", "Caturthī", "Pañcamī",
             "Ṣaṣṭhī", "Saptamī", "Aṣṭamī", "Navamī", "Daśamī",
             "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī", "Pūrṇimā",
             "Pratipadā", "Dvitīyā", "Tṛtīyā", "Caturthī", "Pañcamī",
             "Ṣaṣṭhī", "Saptamī", "Aṣṭamī", "Navamī", "Daśamī",
             "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī", "Amāvasyā"],
    "devanagari": ["प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पञ्चमी",
                   "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी",
                   "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "पूर्णिमा",
                   "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पञ्चमी",
                   "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी",
                   "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "अमावस्या"],
}

# ---------------------------------------------------------------------------
# Nakshatras — 27 asterisms
# ---------------------------------------------------------------------------
NAKSHATRAS = {
    "en": ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
           "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
           "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
           "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
           "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
           "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"],
    "iast": ["Aśvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśira",
             "Ārdrā", "Punarvasu", "Puṣya", "Āśleṣā", "Maghā",
             "Pūrva Phalgunī", "Uttara Phalgunī", "Hasta", "Citrā", "Svātī",
             "Viśākhā", "Anurādhā", "Jyeṣṭhā", "Mūla", "Pūrvāṣāḍhā",
             "Uttarāṣāḍhā", "Śravaṇa", "Dhanīṣṭhā", "Śatabhiṣā",
             "Pūrva Bhādrapadā", "Uttara Bhādrapadā", "Revatī"],
    "devanagari": ["अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिर",
                   "आर्द्रा", "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा",
                   "पूर्व फाल्गुनी", "उत्तर फाल्गुनी", "हस्त", "चित्रा", "स्वाती",
                   "विशाखा", "अनुराधा", "ज्येष्ठा", "मूल", "पूर्वाषाढा",
                   "उत्तराषाढा", "श्रवण", "धनिष्ठा", "शतभिषा",
                   "पूर्व भाद्रपदा", "उत्तर भाद्रपदा", "रेवती"],
}

# ---------------------------------------------------------------------------
# Nitya yogas — 27
# ---------------------------------------------------------------------------
YOGAS = {
    "en": ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
           "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
           "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
           "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
           "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
           "Indra", "Vaidhriti"],
    "iast": ["Viṣkambha", "Prīti", "Āyuṣmān", "Saubhāgya", "Śobhana",
             "Atigaṇḍa", "Sukarmā", "Dhṛti", "Śūla", "Gaṇḍa",
             "Vṛddhi", "Dhruva", "Vyāghāta", "Harṣaṇa", "Vajra",
             "Siddhi", "Vyatīpāta", "Variyān", "Parigha", "Śiva",
             "Siddha", "Sādhya", "Śubha", "Śukla", "Brahma",
             "Indra", "Vaidhṛti"],
    "devanagari": ["विष्कम्भ", "प्रीति", "आयुष्मान्", "सौभाग्य", "शोभन",
                   "अतिगण्ड", "सुकर्मा", "धृति", "शूल", "गण्ड",
                   "वृद्धि", "ध्रुव", "व्याघात", "हर्षण", "वज्र",
                   "सिद्धि", "व्यतीपात", "वरियान्", "परिघ", "शिव",
                   "सिद्ध", "साध्य", "शुभ", "शुक्ल", "ब्रह्म",
                   "इन्द्र", "वैधृति"],
}

# ---------------------------------------------------------------------------
# Karanas — 7 movable (Bava..Vishti) + 4 fixed (Kimstughna, Shakuni,
# Chatushpada, Naga).  Karana index k_idx uses the 7 movable names for full
# tithi halves (k_idx 0..55 → 56 half-tithis), and the four fixed names for
# the special positions (Kathódya/Shakuni, Chatushpada, Naga, Kimstughna).
# ---------------------------------------------------------------------------
KARANAS = {
    "en": ["Bava", "Balava", "Kaulava", "Taitila", "Garaja",
           "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kimstughna"],
    "iast": ["Bāva", "Bālava", "Kaulava", "Taitila", "Garoja",
             "Vaṇija", "Vishti", "Śakuni", "Catuṣpāda", "Nāga", "Kimstughna"],
    "devanagari": ["बाव", "बालव", "कौलव", "तैतिल", "गरोज",
                   "वणिज", "विष्टि", "शकुनि", "चतुष्पाद", "नाग", "किंस्तुघ्न"],
}

# ---------------------------------------------------------------------------
# Lunar months (Chandra māsa) — Chaitra .. Phalguna
# ---------------------------------------------------------------------------
MASAS = {
    "en": ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana",
           "Bhadrapada", "Ashwina", "Kartika", "Margashirsha", "Pausha",
           "Magha", "Phalguna"],
    "iast": ["Caitra", "Vaiśākha", "Jyeṣṭha", "Āṣāḍha", "Śrāvaṇa",
             "Bhādrapada", "Āśvina", "Kārtika", "Mārgaśīrṣa", "Pauṣa",
             "Māgha", "Phālguna"],
    "devanagari": ["चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ", "श्रावण",
                   "भाद्रपद", "आश्विन", "कार्तिक", "मार्गशीर्ष", "पौष",
                   "माघ", "फाल्गुन"],
}

# ---------------------------------------------------------------------------
# Saura (solar) months with their rashi in parentheses
# ---------------------------------------------------------------------------
SAURA_MASAS = {
    "en": ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha",
           "Kanya", "Tula", "Vrischika", "Dhanu", "Makara",
           "Kumbha", "Meena"],
    "iast": ["Meṣa", "Vṛṣabha", "Mithuna", "Karkaṭa", "Siṁha",
             "Kanyā", "Tulā", "Vṛścika", "Dhanu", "Makara",
             "Kumbha", "Mīna"],
    "devanagari": ["मेष", "वृषभ", "मिथुन", "कर्कट", "सिंह",
                   "कन्या", "तुला", "वृश्चिक", "धनु", "मकर",
                   "कुम्भ", "मीन"],
}

# ---------------------------------------------------------------------------
# Ritus (seasons) and Ayanas
# ---------------------------------------------------------------------------
RITUS = {
    "en": ["Vasanta (Spring)", "Grishma (Summer)", "Varsha (Monsoon)",
           "Sharad (Autumn)", "Hemanta (Pre-winter)", "Shishira (Winter)"],
    "iast": ["Vasanta", "Grīṣma", "Varṣā", "Śarad", "Hemanta", "Śiśira"],
    "devanagari": ["वसन्त", "ग्रीष्म", "वर्षा", "शरद्", "हेमन्त", "शिशिर"],
}

AYANAS = {
    "en": ["Uttarayana", "Dakshinayana"],
    "iast": ["Uttarāyaṇa", "Dakṣiṇāyana"],
    "devanagari": ["उत्तरायण", "दक्षिणायन"],
}

PAKSHAS = {
    "en": ["Shukla", "Krishna"],
    "iast": ["Śukla", "Kṛṣṇa"],
    "devanagari": ["शुक्ल", "कृष्ण"],
}

# ---------------------------------------------------------------------------
# Vaaras — weekday names by traditional deity naming. Index 0 = Monday.
# ---------------------------------------------------------------------------
VAARAS = {
    "en": ["Indu", "Bhauma", "Saumya", "Guru", "Bhargava", "Sthira", "Bhanu"],
    "iast": ["Indu", "Bhauma", "Saumya", "Guru", "Bhārgava", "Sthira", "Bhānu"],
    "devanagari": ["इन्दु", "भौम", "सौम्य", "गुरु", "भार्गव", "स्थिर", "भानु"],
}

# ---------------------------------------------------------------------------
# Chara Karakas (Jaimini movable significators).
# Index-position matches KARAKA_INFO below: [0..7] = Atma, Amatya, Bhratru,
# Matru, Pitru, Putra, Gnati, Dara. The seven-karaka scheme drops Pitru (4).
# ---------------------------------------------------------------------------
KARAKAS = {
    "en": ["Atmakaraka", "Amatyakaraka", "Bhratrukaraka", "Matrukaraka",
           "Pitrukaraka", "Putrakaraka", "Gnatikaraka", "Darakaraka"],
    "iast": ["Ātmakāraka", "Amātyakāraka", "Bhrātṛkāraka", "Mātṛkāraka",
             "Pitṛkāraka", "Putrakāraka", "Jñātikāraka", "Dārakāraka"],
    "devanagari": ["आत्मकारक", "अमात्यकारक", "भ्रातृकारक", "मातृकारक",
                   "पितृकारक", "पुत्रकारक", "ज्ञातिकारक", "दारकारक"],
}

KARAKA_MEANINGS = {
    "en": ["Soul · self", "Career · counsel", "Siblings · courage",
           "Mother · home", "Father · dharma", "Children · devotion",
           "Kin · obstacles", "Spouse · partnership"],
    "devanagari": ["आत्मा · स्वयं", "कर्म · मंत्री", "भ्राता · साहस",
                   "माता · गृह", "पिता · धर्म", "पुत्र · भक्ति",
                   "ज्ञाति · विघ्न", "दार · साझेदारी"],
}

# ---------------------------------------------------------------------------
# Ghataka Chakra — classical Muhurta table of inauspicious elements keyed by
# birth (Moon) rashi. One row per Janma Rashi (0..11):
#   maas      → index into MASAS (Chandra māsa that is harmful)
#   tithis    → the three waxing tithis of the harmful group (the same three
#               repeated +15 give the Kṛṣṇa pakṣa half)
#   vaara     → index into VAARAS (Monday = 0 convention)
#   nakshatra → index into NAKSHATRAS
#   yoga      → index into YOGAS
#   karana    → index into KARANAS
#   prahar    → harmful time-of-day division (1..4)
#   c_male / c_female → harmful transit-Moon position counted from the birth
#               rashi (1 = same sign)
# ---------------------------------------------------------------------------
GHATA_CHAKRA = [
    {"maas": 7,  "tithis": [1, 6, 11], "vaara": 6, "nakshatra": 9,  "yoga": 0,  "karana": 0,  "prahar": 1, "c_male": 1,  "c_female": 1},   # Mesha
    {"maas": 8,  "tithis": [5, 10, 15], "vaara": 5, "nakshatra": 12, "yoga": 23, "karana": 7,  "prahar": 4, "c_male": 5,  "c_female": 8},   # Vrishabha
    {"maas": 3,  "tithis": [2, 7, 12], "vaara": 0, "nakshatra": 14, "yoga": 18, "karana": 2,  "prahar": 3, "c_male": 9,  "c_female": 7},   # Mithuna
    {"maas": 9,  "tithis": [2, 7, 12], "vaara": 2, "nakshatra": 16, "yoga": 12, "karana": 9,  "prahar": 1, "c_male": 2,  "c_female": 9},   # Karka
    {"maas": 2,  "tithis": [3, 8, 13], "vaara": 5, "nakshatra": 18, "yoga": 7,  "karana": 0,  "prahar": 1, "c_male": 6,  "c_female": 4},   # Simha
    {"maas": 5,  "tithis": [5, 10, 15], "vaara": 5, "nakshatra": 21, "yoga": 23, "karana": 2,  "prahar": 1, "c_male": 10, "c_female": 3},   # Kanya
    {"maas": 10, "tithis": [4, 9, 14], "vaara": 3, "nakshatra": 23, "yoga": 23, "karana": 3,  "prahar": 4, "c_male": 3,  "c_female": 6},   # Tula
    {"maas": 6,  "tithis": [1, 6, 11], "vaara": 4, "nakshatra": 26, "yoga": 16, "karana": 4,  "prahar": 1, "c_male": 7,  "c_female": 2},   # Vrischika
    {"maas": 4,  "tithis": [3, 8, 13], "vaara": 4, "nakshatra": 1,  "yoga": 14, "karana": 3,  "prahar": 1, "c_male": 4,  "c_female": 10},  # Dhanu
    {"maas": 1,  "tithis": [4, 9, 14], "vaara": 1, "nakshatra": 3,  "yoga": 26, "karana": 7,  "prahar": 4, "c_male": 8,  "c_female": 11},  # Makara
    {"maas": 0,  "tithis": [3, 8, 13], "vaara": 3, "nakshatra": 5,  "yoga": 9,  "karana": 10, "prahar": 3, "c_male": 11, "c_female": 5},   # Kumbha
    {"maas": 11, "tithis": [5, 10, 15], "vaara": 4, "nakshatra": 8,  "yoga": 14, "karana": 8,  "prahar": 4, "c_male": 12, "c_female": 12},  # Meena
]

# ---------------------------------------------------------------------------
# Choghadiya — 7 names, nature mapping, weekday start offsets
# ---------------------------------------------------------------------------
CHOGHADIYAS = {
    "en": ["Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
    "iast": ["Udvega", "Chala", "Lābha", "Amṛta", "Kāla", "Śubha", "Roga"],
    "devanagari": ["उद्वेग", "चल", "लाभ", "अमृत", "काल", "शुभ", "रोग"],
}

CHOGHADIYA_NATURES = {
    "en": {"Udveg": "Inauspicious", "Chal": "Neutral", "Labh": "Auspicious",
           "Amrit": "Auspicious", "Kaal": "Inauspicious", "Shubh": "Auspicious",
           "Rog": "Inauspicious"},
    "iast": {"Udvega": "Inauspicious", "Chala": "Neutral", "Lābha": "Auspicious",
             "Amṛta": "Auspicious", "Kāla": "Inauspicious", "Śubha": "Auspicious",
             "Roga": "Inauspicious"},
    "devanagari": {"उद्वेग": "अशुभ", "चल": "शुभ/अशुभ मध्यम", "लाभ": "शुभ",
                   "अमृत": "शुभ", "काल": "अशुभ", "शुभ": "शुभ", "रोग": "अशुभ"},
}

# First choghadiya slice after sunrise / after sunset, keyed by vaara (0..6).
CHOGHADIYA_DAY_START = {0: 3, 1: 6, 2: 2, 3: 5, 4: 1, 5: 4, 6: 0}
CHOGHADIYA_NIGHT_START = {0: 5, 1: 4, 2: 0, 3: 1, 4: 6, 5: 3, 6: 2}

# ---------------------------------------------------------------------------
# Sankranti festival names
# ---------------------------------------------------------------------------
SANKRANTIS = {
    "en": ["Mesha Sankranti", "Vrishabha Sankranti", "Mithuna Sankranti",
           "Karka Sankranti", "Simha Sankranti", "Kanya Sankranti",
           "Tula Sankranti", "Vrischika Sankranti", "Dhanu Sankranti",
           "Makara Sankranti", "Kumbha Sankranti", "Meena Sankranti"],
    "iast": ["Meṣa Saṅkrānti", "Vṛṣabha Saṅkrānti", "Mithuna Saṅkrānti",
             "Karkaṭa Saṅkrānti", "Siṁha Saṅkrānti", "Kanyā Saṅkrānti",
             "Tulā Saṅkrānti", "Vṛścika Saṅkrānti", "Dhanu Saṅkrānti",
             "Makara Saṅkrānti", "Kumbha Saṅkrānti", "Mīna Saṅkrānti"],
    "devanagari": ["मेष संक्रान्ति", "वृषभ संक्रान्ति", "मिथुन संक्रान्ति",
                   "कर्कट संक्रान्ति", "सिंह संक्रान्ति", "कन्या संक्रान्ति",
                   "तुला संक्रान्ति", "वृश्चिक संक्रान्ति", "धनु संक्रान्ति",
                   "मकर संक्रान्ति", "कुम्भ संक्रान्ति", "मीन संक्रान्ति"],
}

# ---------------------------------------------------------------------------
# Ekadashi names — keyed by (masa_idx, is_krishna); plus the two Adhika
# (intercalary) Ekadashis under the special key ("adhika", _).
# ---------------------------------------------------------------------------
EKADASHI_NAMES = {
    # Chaitra
    (0, False): {"en": "Kamada Ekadashi", "iast": "Kāmadā Ekādaśī", "devanagari": "कामदा एकादशी"},
    (0, True): {"en": "Varuthini Ekadashi", "iast": "Varūthinī Ekādaśī", "devanagari": "वरूथिनी एकादशी"},
    # Vaishakha
    (1, False): {"en": "Mohini Ekadashi", "iast": "Mohinī Ekādaśī", "devanagari": "मोहिनी एकादशी"},
    (1, True): {"en": "Apara Ekadashi", "iast": "Aparā Ekādaśī", "devanagari": "अपरा एकादशी"},
    # Jyeshtha
    (2, False): {"en": "Nirjala Ekadashi", "iast": "Nirjalā Ekādaśī", "devanagari": "निर्जला एकादशी"},
    (2, True): {"en": "Yogini Ekadashi", "iast": "Yoginī Ekādaśī", "devanagari": "योगिनी एकादशी"},
    # Ashadha
    (3, False): {"en": "Devashayani Ekadashi", "iast": "Devaśayanī Ekādaśī", "devanagari": "देवशयनी एकादशी"},
    (3, True): {"en": "Kamika Ekadashi", "iast": "Kāmikā Ekādaśī", "devanagari": "कामिका एकादशी"},
    # Shravana
    (4, False): {"en": "Shravana Putrada Ekadashi", "iast": "Śrāvaṇa Putradā Ekādaśī", "devanagari": "पुत्रदा एकादशी"},
    (4, True): {"en": "Aja Ekadashi", "iast": "Ajā Ekādaśī", "devanagari": "अजा एकादशी"},
    # Bhadrapada
    (5, False): {"en": "Parsva Ekadashi", "iast": "Pārśva Ekādaśī", "devanagari": "पार्श्व एकादशी"},
    (5, True): {"en": "Indira Ekadashi", "iast": "Indirā Ekādaśī", "devanagari": "इन्दिरा एकादशी"},
    # Ashvina
    (6, False): {"en": "Papankusha Ekadashi", "iast": "Pāpāṅkuśā Ekādaśī", "devanagari": "पापांकुशा एकादशी"},
    (6, True): {"en": "Rama Ekadashi", "iast": "Ramā Ekādaśī", "devanagari": "रमा एकादशी"},
    # Kartika
    (7, False): {"en": "Devutthana Ekadashi", "iast": "Devutthāna Ekādaśī", "devanagari": "प्रबोधिनी एकादशी"},
    (7, True): {"en": "Utpanna Ekadashi", "iast": "Utpannā Ekādaśī", "devanagari": "उत्पन्ना एकादशी"},
    # Margashirsha
    (8, False): {"en": "Mokshada Ekadashi", "iast": "Mokṣadā Ekādaśī", "devanagari": "मोक्षदा एकादशी"},
    (8, True): {"en": "Saphala Ekadashi", "iast": "Saphalā Ekādaśī", "devanagari": "सफला एकादशी"},
    # Pausha
    (9, False): {"en": "Pausha Putrada Ekadashi", "iast": "Pauṣa Putradā Ekādaśī", "devanagari": "पुत्रदा एकादशी"},
    (9, True): {"en": "Shattila Ekadashi", "iast": "Ṣaṭtilā Ekādaśī", "devanagari": "षट्तिला एकादशी"},
    # Magha
    (10, False): {"en": "Jaya Ekadashi", "iast": "Jayā Ekādaśī", "devanagari": "जया एकादशी"},
    (10, True): {"en": "Vijaya Ekadashi", "iast": "Vijayā Ekādaśī", "devanagari": "विजया एकादशी"},
    # Phalguna
    (11, False): {"en": "Amalaki Ekadashi", "iast": "Āmalakī Ekādaśī", "devanagari": "आमलकी एकादशी"},
    (11, True): {"en": "Papamochani Ekadashi", "iast": "Pāpamocanī Ekādaśī", "devanagari": "पापमोचनी एकादशी"},
    # Adhika Masa
    ("adhika", False): {"en": "Padmini Ekadashi", "iast": "Padminī Ekādaśī", "devanagari": "पद्मिनी एकादशी"},
    ("adhika", True): {"en": "Parama Ekadashi", "iast": "Paramā Ekādaśī", "devanagari": "परमा एकादशी"},
}

# ---------------------------------------------------------------------------
# Rashi and Graha names, glyphs, lordships
# ---------------------------------------------------------------------------
RASIS = {
    "en": ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
           "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"],
    "iast": ["Meṣa", "Vṛṣabha", "Mithuna", "Karkaṭa", "Siṁha", "Kanyā",
             "Tulā", "Vṛścika", "Dhanu", "Makara", "Kumbha", "Mīna"],
    "devanagari": ["मेष", "वृषभ", "मिथुन", "कर्कट", "सिंह", "कन्या",
                   "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"],
}

GRAHAS = {
    "en": ["Surya", "Chandra", "Mangala", "Budha", "Guru",
           "Shukra", "Shani", "Rahu", "Ketu",
           "Uranus", "Neptune", "Pluto", "Maandi"],
    "iast": ["Sūrya", "Candra", "Maṅgala", "Budha", "Guru",
             "Śukra", "Śani", "Rāhu", "Ketu",
             "Aruna", "Varuṇa", "Pluto", "Māndi"],
    "devanagari": ["सूर्य", "चन्द्र", "मङ्गल", "बुध", "गुरु",
                   "शुक्र", "शनि", "राहु", "केतु",
                   "अरुण", "वरुण", "यम", "मान्दि"],
}

# Modern outer-planet / Upagraha names used when a longer label is shown.
GRAHA_LONG_NAMES = {
    "en": ["Surya", "Chandra", "Mangala", "Budha", "Guru",
           "Shukra", "Shani", "Rahu", "Ketu",
           "Aruna (Uranus)", "Varuna (Neptune)", "Yama (Pluto)", "Maandi"],
    "iast": ["Sūrya", "Candra", "Maṅgala", "Budha", "Guru",
             "Śukra", "Śani", "Rāhu", "Ketu",
             "Aruna (Uranus)", "Varuṇa (Neptune)", "Yama (Pluto)", "Māndi"],
    "devanagari": ["सूर्य", "चन्द्र", "मङ्गल", "बुध", "गुरु",
                   "शुक्र", "शनि", "राहु", "केतु",
                   "अरुण (यूरेनस)", "वरुण (नेपच्यून)", "यम (प्लूटो)", "मान्दि"],
}

RASHI_GLYPHS = {
    "en": ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
           "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"],
    "iast": ["Me", "Vṛ", "Mi", "Ka", "Si", "Ka",
             "Tu", "Vṙ", "Dhu", "Ma", "Ku", "Mi"],
    "devanagari": ["मेष", "वृष", "मिथु", "कर्क", "सिंह", "कन्या",
                   "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"],
}

GRAHA_GLYPHS = {
    "en": ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke",
           "Ur", "Ne", "Pl", "Md"],
    "iast": ["Su", "Ca", "Ma", "Bu", "Gu", "Śu", "Śa", "Rā", "Ke",
             "Ar", "Va", "Pl", "Mā"],
    "devanagari": ["सू", "चं", "मं", "बु", "गु", "शु", "श", "रा", "के",
                   "अ", "व", "प्लू", "मा"],
}

# Owner planet index (0..8) of each rashi.
RASHI_LORD = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]

# Exaltation (uccha) sign / degree per planet. Chandra: Vrishabha, Guru: Karka,
# Rahu: Vrishabha, Ketu: Vrischika (Bṛhat Pārāśarī Horāśāstra).
EXALTATION_SIGN = [0, 1, 10, 5, 3, 11, 6, 1, 7]
EXALTATION_DEGREE = [10.0, 3.0, 28.0, 15.0, 5.0, 27.0, 20.0, None, None]

# Own signs per planet.
OWN_SIGNS = {0: [4], 1: [3], 2: [0, 7], 3: [2, 5], 4: [8, 11],
             5: [6, 1], 6: [9, 10], 7: [], 8: []}

# Moolatrikona sign per planet; nodes have none.
MOOLATRIKONA_SIGN = {0: 4, 1: 3, 2: 0, 3: 5, 4: 8, 5: 6, 6: 9,
                     7: None, 8: None}

# Natural friends / enemies / neutrals for all nine grahas (Lahiri-table
# convention, including Rahu and Ketu); the three sets partition the other
# eight grahas for every planet except Surya, whose list omits Ketu.
GRAHA_FRIENDS = {0: {1, 2, 4}, 1: {0, 3}, 2: {0, 1, 4}, 3: {0, 5, 7},
                 4: {0, 1, 2}, 5: {3, 6, 7}, 6: {3, 5, 7},
                 7: {3, 5, 6}, 8: {5, 6, 3}}
GRAHA_ENEMIES = {0: {5, 6, 7}, 1: {7, 8}, 2: {6, 5}, 3: {1, 4},
                 4: {3, 5}, 5: {0, 1}, 6: {0, 2, 1},
                 7: {0, 2, 1}, 8: {0, 2, 1}}
GRAHA_NEUTRALS = {0: {3}, 1: {6, 5, 4, 2}, 2: {3, 7, 8}, 3: {2, 6, 8},
                  4: {7, 6, 8}, 5: {4, 2, 8}, 6: {4, 8},
                  7: {4, 8}, 8: {4, 7}}

# Lord planet (0..8) of each nakshatra (9-planet cycle starting with Ketu).
NAKSHATRA_LORD = [8, 5, 0, 1, 2, 7, 4, 6, 3] * 3

# ---------------------------------------------------------------------------
# Vimshottari Dasha
# ---------------------------------------------------------------------------
DASHA_LORDS = [8, 5, 0, 1, 2, 7, 4, 6, 3]
VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

# ---------------------------------------------------------------------------
# Nakshatra birth syllables: 27 nakshatras × 4 padas = 108 entries,
# flattened as nakshatra*4 + pada.
# ---------------------------------------------------------------------------
NAKSHATRA_INITIALS = {
    "en": ["Chu", "Che", "Cho", "La",
           "Li", "Lu", "Le", "Lo",
           "A", "I", "U", "E",
           "O", "Va", "Vi", "Vu",
           "Ve", "Vo", "Ka", "Ki",
           "Ku", "Gha", "Nga", "Chha",
           "Ke", "Ko", "Ha", "Hi",
           "Hu", "He", "Ho", "Da",
           "Di", "Du", "De", "Do",
           "Ma", "Me", "Mu", "Mi",
           "Mo", "Ta", "Ti", "Tu",
           "Te", "To", "Pa", "Pi",
           "Pu", "Sha", "Na", "Tha",
           "Pe", "Po", "Ra", "Ri",
           "Ru", "Re", "Ro", "Ta",
           "Ti", "Tu", "Te", "To",
           "Na", "Ni", "Nu", "Ne",
           "No", "Ya", "Yi", "Yu",
           "Ye", "Yo", "Bha", "Bhi",
           "Bhu", "Dha", "Pha", "Dha",
           "Bhe", "Bho", "Ja", "Ji",
           "Ju", "Je", "Jo", "Gha",
           "Ga", "Gi", "Gu", "Ge",
           "Go", "Sa", "Si", "Su",
           "Se", "So", "Da", "Di",
           "Du", "Tha", "Jha", "Nja",
           "De", "Do", "Cha", "Chi"],
    "iast": ["Chu", "Che", "Cho", "Lā",
             "Lī", "Lū", "Le", "Lo",
             "A", "I", "U", "E",
             "O", "Vā", "Vī", "Vū",
             "Ve", "Vo", "Kā", "Kī",
             "Kū", "Gha", "Ṁ", "Chha",
             "Ke", "Ko", "Hā", "Hī",
             "Hū", "He", "Ho", "Ḍā",
             "Ḍī", "Ḍū", "Ḍe", "Ḍo",
             "Mā", "Mī", "Mū", "Mī",
             "Mo", "Ṭā", "Ṭī", "Ṭū",
             "Ṭe", "Ṭo", "Pā", "Pī",
             "Pū", "Sha", "Ṇā", "Ṭha",
             "Pe", "Po", "Rā", "Rī",
             "Rū", "Re", "Ro", "Tā",
             "Tī", "Tū", "Te", "To",
             "Nā", "Nī", "Nū", "Ne",
             "No", "Yā", "Yī", "Yū",
             "Ye", "Yo", "Bhā", "Bhī",
             "Bhū", "Dhā", "Phā", "Ḍhā",
             "Bhe", "Bho", "Jā", "Jī",
             "Jū", "Je", "Jo", "Gha",
             "Gā", "Gī", "Gū", "Ge",
             "Go", "Sā", "Sī", "Sū",
             "Se", "So", "Dā", "Dī",
             "Dū", "Thā", "Jha", "Ña",
             "De", "Do", "Chā", "Chī"],
    "devanagari": ["चु", "चे", "चो", "ला",
                   "ली", "लू", "ले", "लो",
                   "अ", "इ", "उ", "ए",
                   "ओ", "वा", "वि", "वु",
                   "वे", "वो", "का", "कि",
                   "कु", "घ", "ङ", "छ",
                   "के", "को", "हा", "हि",
                   "हु", "हे", "हो", "डा",
                   "डि", "डु", "डे", "डो",
                   "मा", "मि", "मु", "मे",
                   "मो", "टा", "टि", "टु",
                   "टे", "टो", "पा", "पि",
                   "पु", "ष", "ण", "ठ",
                   "पे", "पो", "रा", "रि",
                   "रु", "रे", "रो", "ता",
                   "ति", "तु", "ते", "तो",
                   "ना", "नि", "नु", "ने",
                   "नो", "या", "यि", "यु",
                   "ये", "यो", "भा", "भि",
                   "भू", "धा", "फा", "ढा",
                   "भे", "भो", "जा", "जि",
                   "जु", "जे", "जो", "घ",
                   "गा", "गि", "गु", "गे",
                   "गो", "सा", "सि", "सु",
                   "से", "सो", "दा", "दि",
                   "दु", "था", "झ", "ञ",
                   "दे", "दो", "चा", "चि"],
}

# ---------------------------------------------------------------------------
# Hora (Chaldean) order and weekday lords
# ---------------------------------------------------------------------------
# Planet index sequence for successive horas: Sun, Venus, Mercury, Moon,
# Saturn, Jupiter, Mars (the Chaldean order).
HORA_ORDER = [0, 5, 3, 1, 6, 4, 2]

# Lord planet of each weekday vaara (Monday=0 .. Sunday=6).
WEEKDAY_LORD = [1, 2, 3, 4, 5, 6, 0]

# ---------------------------------------------------------------------------
# Muhurta names (15 day muhurtas) and status labels
# ---------------------------------------------------------------------------
MUHURTA_NAMES = {
    "en": ["Raudra", "Ahi", "Mitra", "Pitru", "Vasu",
           "Vara", "Vishvadeva", "Vidhi", "Satamukhi", "Puruhuta",
           "Vahini", "Naktanaka", "Tvashtri", "Savita", "Vishvadeva"],
    "iast": ["Raudra", "Ahi", "Mitra", "Pitṛ", "Vasu",
             "Vara", "Viśvadeva", "Vidhi", "Śatamukhī", "Puruhūta",
             "Vāhinī", "Naktanakā", "Tvaṣṭṛ", "Savitā", "Viśvadeva"],
    "devanagari": ["रौद्र", "अहि", "मित्र", "पितृ", "वसु",
                   "वार", "विश्वदेव", "विधि", "शतमुखी", "पुरुहूत",
                   "वाहिनी", "नक्तनका", "त्वष्टृ", "सविता", "विश्वदेव"],
}

MUHURTA_STATUSES = {
    "en": {"Abhijit": "Abhijit", "Auspicious": "Auspicious",
           "Inauspicious": "Inauspicious", "Neutral": "Neutral"},
    "iast": {"Abhijit": "Abhijit", "Auspicious": "Maṅgala",
             "Inauspicious": "Amaṅgala", "Neutral": "Madhyama"},
    "devanagari": {"Abhijit": "अभिजित", "Auspicious": "मङ्गल",
                   "Inauspicious": "अमङ्गल", "Neutral": "मध्यम"},
}

# ---------------------------------------------------------------------------
# Festival metadata (used by KalaUtsavachakra; documented for reference)
# ---------------------------------------------------------------------------
FESTIVAL_METADATA = {
    "ugadi": {
        "priority": 8, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Chaitra Shukla Pratipada at Udaya",
        "en": "Ugadi", "iast": "Ugādi", "devanagari": "उगादि",
        "description": "New Year of the lunar calendar (amavasyanta tradition).",
    },
    "gudi_padwa": {
        "priority": 8, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Chaitra Shukla Pratipada at Udaya",
        "en": "Gudi Padwa", "iast": "Guḍī Pāḍavā", "devanagari": "गुड़ी पाडवा",
        "description": "New Year observed in Maharashtra (Shalivahana era).",
    },
    "rama_navami": {
        "priority": 7, "type": "Maha", "color": "#2ecc71", "notify": "normal",
        "rule": "Chaitra Shukla Navami at Udaya",
        "en": "Rama Navami", "iast": "Rāma Navamī", "devanagari": "राम नवमी",
        "description": "Birth anniversary of Sri Rama.",
    },
    "hanuman_janmotsav": {
        "priority": 7, "type": "Maha", "color": "#2ecc71", "notify": "normal",
        "rule": "Chaitra Shukla Purnima at Udaya",
        "en": "Hanuman Janmotsav", "iast": "Hanumān Janmotsava",
        "devanagari": "हनुमान जन्मोत्सव",
        "description": "Birth anniversary of Hanuman.",
    },
    "parashurama_jayanti": {
        "priority": 6, "type": "Maha", "color": "#2ecc71", "notify": "normal",
        "rule": "Vaishakha Shukla Tritiya at Udaya",
        "en": "Parashurama Jayanti", "iast": "Paraśurāma Jayantī",
        "devanagari": "परशुराम जयन्ती",
        "description": "Birth anniversary of Parashurama.",
    },
    "akshaya_tritiya": {
        "priority": 8, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Vaishakha Shukla Tritiya (Akshaya)",
        "en": "Akshaya Tritiya", "iast": "Akṣaya Tṛtīyā",
        "devanagari": "अक्षय तृतीया",
        "description": "Immutable day, auspicious for beginnings.",
    },
    "narasimha_jayanti": {
        "priority": 6, "type": "Maha", "color": "#2ecc71", "notify": "normal",
        "rule": "Vaishakha Shukla Chaturdashi at Nishita",
        "en": "Narasimha Jayanti", "iast": "Narasiṁha Jayantī",
        "devanagari": "नरसिंह जयन्ती",
        "description": "Appearance day of Narasimha.",
    },
    "vat_savitri_amavasya": {
        "priority": 6, "type": "Vrata", "color": "#2ecc71", "notify": "normal",
        "rule": "Jyeshtha Krishna Amavasya at Udaya",
        "en": "Vat Savitri Amavasya", "iast": "Vaṭa Sāvitrī Amāvasyā",
        "devanagari": "वट सावित्री अमावस्या",
        "description": "Wife's observance for husband's longevity.",
    },
    "vat_savitri_purnima": {
        "priority": 6, "type": "Vrata", "color": "#2ecc71", "notify": "normal",
        "rule": "Jyeshtha Shukla Purnima at Udaya",
        "en": "Vat Savitri Purnima", "iast": "Vaṭa Sāvitrī Pūrṇimā",
        "devanagari": "वट सावित्री पूर्णिमा",
        "description": "Vat Savitri observance in western traditions.",
    },
    "guru_purnima": {
        "priority": 9, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Ashadha Shukla Purnima at Udaya",
        "en": "Guru Purnima", "iast": "Guru Pūrṇimā", "devanagari": "गुरु पूर्णिमा",
        "description": "Day of reverence for one's guru; Vyasa Purnima.",
    },
    "nag_panchami": {
        "priority": 8, "type": "Vrata", "color": "#2ecc71", "notify": "normal",
        "rule": "Shravana Shukla Panchami at Udaya",
        "en": "Nag Panchami", "iast": "Nāga Pañcamī", "devanagari": "नाग पञ्चमी",
        "description": "Worship of the naga deities.",
    },
    "raksha_bandhan": {
        "priority": 9, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Shravana Shukla Purnima (Rakhi)",
        "en": "Raksha Bandhan", "iast": "Rakṣā Bandhana", "devanagari": "रक्षा बन्धन",
        "description": "Protective thread festival of brothers and sisters.",
    },
    "varamahalakshmi_vrata": {
        "priority": 8, "type": "Vrata", "color": "#2ecc71", "notify": "normal",
        "rule": "Friday before/on Shravana Purnima",
        "en": "Varamahalakshmi Vrata", "iast": "Varamahālakṣmī Vrata",
        "devanagari": "वरमहालक्ष्मी व्रत",
        "description": "Observance for the grace of Mahalakshmi.",
    },
    "krishna_janmashtami": {
        "priority": 10, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Shravana Krishna Ashtami at Nishita",
        "en": "Krishna Janmashtami", "iast": "Kṛṣṇa Janmāṣṭamī",
        "devanagari": "कृष्ण जन्माष्टमी",
        "description": "Birth of Sri Krishna at midnight.",
    },
    "swarna_gauri": {
        "priority": 6, "type": "Vrata", "color": "#2ecc71", "notify": "normal",
        "rule": "Bhadrapada Shukla Tritiya at Udaya",
        "en": "Swarna Gauri", "iast": "Svarṇa Gaurī", "devanagari": "स्वर्ण गौरी",
        "description": "Gauri puja for conjugal happiness.",
    },
    "ganesh_chaturthi": {
        "priority": 10, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Bhadrapada Shukla Chaturthi at Udaya",
        "en": "Ganesh Chaturthi", "iast": "Gaṇeśa Caturthī",
        "devanagari": "गणेश चतुर्थी",
        "description": "Appearance day of Ganesha.",
    },
    "rishi_panchami": {
        "priority": 5, "type": "Vrata", "color": "#2ecc71", "notify": "normal",
        "rule": "Bhadrapada Shukla Panchami at Udaya",
        "en": "Rishi Panchami", "iast": "Ṛṣi Pañcamī", "devanagari": "ऋषि पञ्चमी",
        "description": "Veneration of the seven rishis.",
    },
    "ananta_chaturdashi": {
        "priority": 6, "type": "Vrata", "color": "#2ecc71", "notify": "normal",
        "rule": "Bhadrapada Shukla Chaturdashi at Udaya",
        "en": "Ananta Chaturdashi", "iast": "Ananta Caturdaśī",
        "devanagari": "अनन्त चतुर्दशी",
        "description": "Worship of Ananta (Vishnu).",
    },
    "mahalaya_amavasya": {
        "priority": 7, "type": "Ritual", "color": "#2ecc71", "notify": "normal",
        "rule": "Ashwina Krishna Amavasya (beginning of Pitru Paksha)",
        "en": "Mahalaya Amavasya", "iast": "Mahālayā Amāvasyā",
        "devanagari": "महालया अमावस्या",
        "description": "Conclusion of Pitru Paksha; offerings to ancestors.",
    },
    "mahanavami": {
        "priority": 8, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Ashwina Shukla Navami at Udaya",
        "en": "Mahanavami", "iast": "Mahānavamī", "devanagari": "महानवमी",
        "description": "Final day of worship before Vijayadashami.",
    },
    "vijayadashami": {
        "priority": 10, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Ashwina Shukla Dashami at Udaya",
        "en": "Vijayadashami", "iast": "Vijayādaśamī", "devanagari": "विजयादशमी",
        "description": "Celebration of victory of dharma; Dusshera.",
    },
    "kojagari_purnima": {
        "priority": 8, "type": "Maha", "color": "#2ecc71", "notify": "normal",
        "rule": "Ashwina Shukla Purnima",
        "en": "Kojagari Purnima", "iast": "Ko-jāgarī Pūrṇimā",
        "devanagari": "कोजागरी पूर्णिमा",
        "description": "Lakshmi puja on Sharad Purnima night.",
    },
    "naraka_chaturdashi": {
        "priority": 8, "type": "Maha", "color": "#2ecc71", "notify": "normal",
        "rule": "Kartika Krishna Chaturdashi at Udaya",
        "en": "Naraka Chaturdashi", "iast": "Naraka Caturdaśī",
        "devanagari": "नरक चतुर्दशी",
        "description": "Day before Deepavali; defeat of Narakasura.",
    },
    "deepavali": {
        "priority": 10, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Kartika Krishna Amavasya (Diwali)",
        "en": "Deepavali", "iast": "Dīpāvalī", "devanagari": "दीपावली",
        "description": "Festival of lights.",
    },
    "bali_pratipada": {
        "priority": 6, "type": "Maha", "color": "#2ecc71", "notify": "normal",
        "rule": "Kartika Shukla Pratipada at Udaya",
        "en": "Bali Pratipada", "iast": "Bali Pratipadā", "devanagari": "बलि प्रतिपदा",
        "description": "Homage to King Bali on the first day of Kartika.",
    },
    "tulsi_vivah": {
        "priority": 7, "type": "Ritual", "color": "#2ecc71", "notify": "normal",
        "rule": "Kartika Shukla Ekadashi to Purnima (commence day)",
        "en": "Tulsi Vivah", "iast": "Tulasī Vivāha", "devanagari": "तुलसी विवाह",
        "description": "Symbolic marriage of Tulsi to Vishnu.",
    },
    "champa_shashthi": {
        "priority": 5, "type": "Vrata", "color": "#2ecc71", "notify": "normal",
        "rule": "Margashirsha Shukla Shashthi at Udaya",
        "en": "Champa Shashthi", "iast": "Champā Ṣaṣṭhī", "devanagari": "चम्पा षष्ठी",
        "description": "Regional festival honouring Khandoba.",
    },
    "datta_jayanti": {
        "priority": 6, "type": "Maha", "color": "#2ecc71", "notify": "normal",
        "rule": "Margashirsha Shukla Purnima at Udaya",
        "en": "Datta Jayanti", "iast": "Dattā Jayantī", "devanagari": "दत्त जयन्ती",
        "description": "Appearance day of Dattatreya.",
    },
    "ratha_saptami": {
        "priority": 6, "type": "Vrata", "color": "#2ecc71", "notify": "normal",
        "rule": "Magha Shukla Saptami at Udaya",
        "en": "Ratha Saptami", "iast": "Ratha Saptamī", "devanagari": "रथ सप्तमी",
        "description": "Surya's northward-turn festival.",
    },
    "bhishma_ashtami": {
        "priority": 5, "type": "Vrata", "color": "#2ecc71", "notify": "normal",
        "rule": "Magha Shukla Ashtami at Udaya",
        "en": "Bhishma Ashtami", "iast": "Bhīṣma Aṣṭamī", "devanagari": "भीष्म अष्टमी",
        "description": "Remembrance of Bhishma's vows.",
    },
    "madhwa_navami": {
        "priority": 5, "type": "Maha", "color": "#2ecc71", "notify": "normal",
        "rule": "Magha Shukla Navami at Udaya",
        "en": "Madhwa Navami", "iast": "Madhva Navamī", "devanagari": "मध्व नवमी",
        "description": "Anniversary of Madhvacharya.",
    },
    "mahashivaratri": {
        "priority": 9, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Magha Krishna Chaturdashi (night observance)",
        "en": "Mahashivaratri", "iast": "Mahāśivarātri", "devanagari": "महाशिवरात्रि",
        "description": "Great night of Shiva (Phalguna Krishna in some regions).",
    },
    "holi": {
        "priority": 9, "type": "Maha", "color": "#2ecc71", "notify": "high",
        "rule": "Phalguna Shukla Purnima at Udaya",
        "en": "Holi", "iast": "Holī", "devanagari": "होली",
        "description": "Festival of colours.",
    },
    "sankashti_chaturthi": {
        "priority": 8, "type": "Vrata", "color": "#9b59b6", "notify": "normal",
        "rule": "Krishna Chaturthi at moonrise",
        "en": "Sankashti Chaturthi", "iast": "Sankāṣṭhī Caturthī",
        "devanagari": "सङ्कष्टी चतुर्थी",
        "description": "Ganesha vrata on each Krishna Chaturthi.",
    },
    "rigveda_upakarma": {
        "priority": 4, "type": "Ritual", "color": "#2ecc71", "notify": "normal",
        "rule": "Shravana Shukla Purnima / Ashadha (school-dependent)",
        "en": "Rigveda Upakarma", "iast": "Ṛgveda Upākarma",
        "devanagari": "ऋग्वेद उपाकर्म",
        "description": "Commemoration of the Vedic year for Rigvedins.",
    },
    "yajurveda_upakarma": {
        "priority": 4, "type": "Ritual", "color": "#2ecc71", "notify": "normal",
        "rule": "Shravana Shukla Purnima (school-dependent)",
        "en": "Yajurveda Upakarma", "iast": "Yajurveda Upākarma",
        "devanagari": "यजुर्वेद उपाकर्म",
        "description": "Commemoration of the Vedic year for Yajurvedins.",
    },
    "samaveda_upakarma": {
        "priority": 4, "type": "Ritual", "color": "#2ecc71", "notify": "normal",
        "rule": "Ashadha Shukla Purnima (school-dependent)",
        "en": "Samaveda Upakarma", "iast": "Sāmaveda Upākarma",
        "devanagari": "सामवेद उपाकर्म",
        "description": "Commemoration of the Vedic year for Samavedins.",
    },
    "atharvaveda_upakarma": {
        "priority": 4, "type": "Ritual", "color": "#2ecc71", "notify": "normal",
        "rule": "Shravana Shukla Purnima (school-dependent)",
        "en": "Atharvaveda Upakarma", "iast": "Atharvaveda Upākarma",
        "devanagari": "अथर्ववेद उपाकर्म",
        "description": "Commemoration of the Vedic year for Atharvavedins.",
    },
    "ayodhya_ramlalla_vardhanti": {
        "priority": 5, "type": "Maha", "color": "#2ecc71", "notify": "normal",
        "rule": "Margashirsha Shukla Saptami at Udaya",
        "en": "Ayodhya Ramlalla Vardhanti", "iast": "Ayodhyā Rāmlālā Vardhantī",
        "devanagari": "अयोध्या रामलला वर्धन्ति",
        "description": "Celebration of Ramlalla at Ayodhya.",
    },
}

# ---------------------------------------------------------------------------
# Offline built-in city registry
# ---------------------------------------------------------------------------
BUILTIN_CITIES = [
    {"name": "Ujjain", "lat": 23.1765, "lon": 75.7885, "tz": 5.5, "alt": 0.0},
    {"name": "New Delhi", "lat": 28.6139, "lon": 77.2090, "tz": 5.5, "alt": 216.0},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "tz": 5.5, "alt": 14.0},
    {"name": "Chennai", "lat": 13.0827, "lon": 80.2707, "tz": 5.5, "alt": 6.0},
    {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639, "tz": 5.5, "alt": 9.0},
    {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "tz": 5.5, "alt": 920.0},
    {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "tz": 5.5, "alt": 505.0},
    {"name": "Pune", "lat": 18.5204, "lon": 73.8567, "tz": 5.5, "alt": 560.0},
    {"name": "Ahmedabad", "lat": 23.0225, "lon": 72.5714, "tz": 5.5, "alt": 53.0},
    {"name": "Jaipur", "lat": 26.9124, "lon": 75.7873, "tz": 5.5, "alt": 431.0},
    {"name": "Lucknow", "lat": 26.8467, "lon": 80.9462, "tz": 5.5, "alt": 128.0},
    {"name": "Kanpur", "lat": 26.4499, "lon": 80.3319, "tz": 5.5, "alt": 126.0},
    {"name": "Nagpur", "lat": 21.1458, "lon": 79.0882, "tz": 5.5, "alt": 310.0},
    {"name": "Indore", "lat": 22.7196, "lon": 75.8577, "tz": 5.5, "alt": 553.0},
    {"name": "Bhopal", "lat": 23.2599, "lon": 77.4126, "tz": 5.5, "alt": 527.0},
    {"name": "Patna", "lat": 25.5941, "lon": 85.1376, "tz": 5.5, "alt": 53.0},
    {"name": "Vadodara", "lat": 22.3072, "lon": 73.1812, "tz": 5.5, "alt": 39.0},
    {"name": "Ghaziabad", "lat": 28.6692, "lon": 77.4538, "tz": 5.5, "alt": 219.0},
    {"name": "Ludhiana", "lat": 30.9010, "lon": 75.8573, "tz": 5.5, "alt": 262.0},
    {"name": "Agra", "lat": 27.1767, "lon": 78.0081, "tz": 5.5, "alt": 171.0},
    {"name": "Nashik", "lat": 19.9975, "lon": 73.7898, "tz": 5.5, "alt": 569.0},
    {"name": "Faridabad", "lat": 28.4089, "lon": 77.3178, "tz": 5.5, "alt": 198.0},
    {"name": "Meerut", "lat": 28.9845, "lon": 77.7064, "tz": 5.5, "alt": 225.0},
    {"name": "Rajkot", "lat": 22.3039, "lon": 70.8022, "tz": 5.5, "alt": 134.0},
    {"name": "Varanasi", "lat": 25.3176, "lon": 82.9739, "tz": 5.5, "alt": 80.0},
    {"name": "Srinagar", "lat": 34.0837, "lon": 74.7973, "tz": 5.5, "alt": 1585.0},
    {"name": "Aurangabad", "lat": 19.8762, "lon": 75.3433, "tz": 5.5, "alt": 568.0},
    {"name": "Dhanbad", "lat": 23.7957, "lon": 86.4304, "tz": 5.5, "alt": 227.0},
    {"name": "Amritsar", "lat": 31.6340, "lon": 74.8723, "tz": 5.5, "alt": 234.0},
    {"name": "Prayagraj", "lat": 25.4358, "lon": 81.8463, "tz": 5.5, "alt": 98.0},
    {"name": "Coimbatore", "lat": 11.0168, "lon": 76.9558, "tz": 5.5, "alt": 411.0},
    {"name": "Jabalpur", "lat": 23.1815, "lon": 79.9864, "tz": 5.5, "alt": 411.0},
    {"name": "Gwalior", "lat": 26.2183, "lon": 78.1828, "tz": 5.5, "alt": 196.0},
    {"name": "Vijayawada", "lat": 16.5062, "lon": 80.6480, "tz": 5.5, "alt": 24.0},
    {"name": "Jodhpur", "lat": 26.2389, "lon": 73.0243, "tz": 5.5, "alt": 231.0},
    {"name": "Madurai", "lat": 9.9252, "lon": 78.1198, "tz": 5.5, "alt": 101.0},
    {"name": "Raipur", "lat": 21.2514, "lon": 81.6296, "tz": 5.5, "alt": 298.0},
    {"name": "Kota", "lat": 25.2138, "lon": 75.8648, "tz": 5.5, "alt": 268.0},
    {"name": "Guwahati", "lat": 26.1445, "lon": 91.7362, "tz": 5.5, "alt": 55.0},
    {"name": "Chandigarh", "lat": 30.7333, "lon": 76.7794, "tz": 5.5, "alt": 350.0},
    {"name": "Solapur", "lat": 17.6599, "lon": 75.9064, "tz": 5.5, "alt": 457.0},
    {"name": "Hubballi", "lat": 15.3647, "lon": 75.1240, "tz": 5.5, "alt": 671.0},
    {"name": "Tiruchirappalli", "lat": 10.7905, "lon": 78.7047, "tz": 5.5, "alt": 88.0},
    {"name": "Bareilly", "lat": 28.3670, "lon": 79.4304, "tz": 5.5, "alt": 268.0},
    {"name": "Moradabad", "lat": 28.8386, "lon": 78.7768, "tz": 5.5, "alt": 200.0},
    {"name": "Mysuru", "lat": 12.2958, "lon": 76.6394, "tz": 5.5, "alt": 763.0},
    {"name": "Gurugram", "lat": 28.4595, "lon": 77.0266, "tz": 5.5, "alt": 219.0},
    {"name": "Aligarh", "lat": 27.8974, "lon": 78.0880, "tz": 5.5, "alt": 187.0},
    {"name": "Jalandhar", "lat": 31.3260, "lon": 75.5762, "tz": 5.5, "alt": 234.0},
    {"name": "Tirupati", "lat": 13.6288, "lon": 79.4192, "tz": 5.5, "alt": 143.0},
    {"name": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245, "tz": 5.5, "alt": 58.0},
    {"name": "Salem", "lat": 11.6643, "lon": 78.1460, "tz": 5.5, "alt": 278.0},
    {"name": "Warangal", "lat": 17.9689, "lon": 79.5941, "tz": 5.5, "alt": 302.0},
    {"name": "Guntur", "lat": 16.3067, "lon": 80.4365, "tz": 5.5, "alt": 22.0},
    {"name": "Bhiwandi", "lat": 19.2914, "lon": 73.0639, "tz": 5.5, "alt": 24.0},
    {"name": "Saharanpur", "lat": 29.9640, "lon": 77.5459, "tz": 5.5, "alt": 264.0},
    {"name": "Gorakhpur", "lat": 26.7606, "lon": 83.3732, "tz": 5.5, "alt": 84.0},
    {"name": "Bikaner", "lat": 28.0229, "lon": 73.3119, "tz": 5.5, "alt": 242.0},
    {"name": "Amravati", "lat": 20.9374, "lon": 77.7796, "tz": 5.5, "alt": 343.0},
    {"name": "Noida", "lat": 28.5355, "lon": 77.3910, "tz": 5.5, "alt": 200.0},
    {"name": "Mangaluru", "lat": 12.9141, "lon": 74.8560, "tz": 5.5, "alt": 22.0},
    {"name": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366, "tz": 5.5, "alt": 10.0},
    {"name": "Rishikesh", "lat": 30.0869, "lon": 78.2676, "tz": 5.5, "alt": 345.0},
    {"name": "Hardwar", "lat": 29.9457, "lon": 78.1642, "tz": 5.5, "alt": 314.0},
    {"name": "Sringeri", "lat": 13.4194, "lon": 75.2524, "tz": 5.5, "alt": 674.0},
    {"name": "Kanchipuram", "lat": 12.8180, "lon": 79.6941, "tz": 5.5, "alt": 83.0},
    {"name": "Srimushnam", "lat": 11.4024, "lon": 79.4135, "tz": 5.5, "alt": 29.0},
    {"name": "Imphal", "lat": 24.8170, "lon": 93.9368, "tz": 5.5, "alt": 785.0},
    {"name": "Shillong", "lat": 25.5788, "lon": 91.8933, "tz": 5.5, "alt": 1525.0},
    {"name": "Aizawl", "lat": 23.7307, "lon": 92.7173, "tz": 5.5, "alt": 1132.0},
    {"name": "Kohima", "lat": 25.6751, "lon": 94.1086, "tz": 5.5, "alt": 1444.0},
    {"name": "Gangtok", "lat": 27.3389, "lon": 88.6065, "tz": 5.5, "alt": 1650.0},
    {"name": "Itanagar", "lat": 27.0844, "lon": 93.6053, "tz": 5.5, "alt": 750.0},
    {"name": "Dispur", "lat": 26.1433, "lon": 91.7898, "tz": 5.5, "alt": 55.0},
    {"name": "Panaji", "lat": 15.4909, "lon": 73.8278, "tz": 5.5, "alt": 7.0},
    {"name": "Puducherry", "lat": 11.9416, "lon": 79.8083, "tz": 5.5, "alt": 3.0},
    {"name": "Bengaluru Rural", "lat": 13.1322, "lon": 77.6131, "tz": 5.5, "alt": 920.0},
    {"name": "Kolar", "lat": 13.1356, "lon": 78.1331, "tz": 5.5, "alt": 838.0},
    {"name": "Tirunelveli", "lat": 8.7139, "lon": 77.7567, "tz": 5.5, "alt": 47.0},
    {"name": "Thanjavur", "lat": 10.7870, "lon": 79.1378, "tz": 5.5, "alt": 59.0},
    {"name": "Mattur", "lat": 13.3200, "lon": 75.9400, "tz": 5.5, "alt": 900.0},
    # --- More Indian cities ---
    {"name": "Kochi", "lat": 9.9312, "lon": 76.2673, "tz": 5.5, "alt": 6.0},
    {"name": "Kozhikode", "lat": 11.2588, "lon": 75.7804, "tz": 5.5, "alt": 8.0},
    {"name": "Visakhapatnam", "lat": 17.6868, "lon": 83.2185, "tz": 5.5, "alt": 45.0},
    {"name": "Jammu", "lat": 32.7266, "lon": 74.8570, "tz": 5.5, "alt": 327.0},
    {"name": "Dehradun", "lat": 30.3165, "lon": 78.0322, "tz": 5.5, "alt": 450.0},
    {"name": "Ranchi", "lat": 23.3441, "lon": 85.3096, "tz": 5.5, "alt": 629.0},
    {"name": "Jamshedpur", "lat": 22.8046, "lon": 86.2029, "tz": 5.5, "alt": 134.0},
    {"name": "Cuttack", "lat": 20.4625, "lon": 85.8828, "tz": 5.5, "alt": 36.0},
    {"name": "Siliguri", "lat": 26.7271, "lon": 88.3953, "tz": 5.5, "alt": 122.0},
    {"name": "Agartala", "lat": 23.8315, "lon": 91.2868, "tz": 5.5, "alt": 16.0},
    {"name": "Leh", "lat": 34.1526, "lon": 77.5771, "tz": 5.5, "alt": 3500.0},
    {"name": "Mount Abu", "lat": 24.5926, "lon": 72.7156, "tz": 5.5, "alt": 1220.0},
    {"name": "Udupi", "lat": 13.3409, "lon": 74.7421, "tz": 5.5, "alt": 27.0},
    {"name": "Manipal", "lat": 13.3526, "lon": 74.7935, "tz": 5.5, "alt": 50.0},
    {"name": "Kundapura", "lat": 13.6313, "lon": 74.6902, "tz": 5.5, "alt": 12.0},
    {"name": "Byndoor", "lat": 13.8667, "lon": 74.6333, "tz": 5.5, "alt": 9.0},
    {"name": "Bijoor", "lat": 13.8439, "lon": 74.6397, "tz": 5.5, "alt": 15.0},
    {"name": "Bhatkal", "lat": 13.9852, "lon": 74.5551, "tz": 5.5, "alt": 10.0},
    {"name": "Honnavar", "lat": 14.2797, "lon": 74.4450, "tz": 5.5, "alt": 8.0},
    {"name": "Manjeshwar", "lat": 12.7243, "lon": 74.8743, "tz": 5.5, "alt": 0.0},
    {"name": "Murudeshwar", "lat": 14.0943, "lon": 74.4845, "tz": 5.5, "alt": 5.0},
    {"name": "Shirali", "lat": 14.0167, "lon": 74.5167, "tz": 5.5, "alt": 12.0},
    {"name": "Gunavante", "lat": 14.2224, "lon": 74.4658, "tz": 5.5, "alt": 5.0},
    {"name": "Padukuli", "lat": 14.2542, "lon": 74.5052, "tz": 5.5, "alt": 15.0},
    {"name": "Kumta", "lat": 14.4258, "lon": 74.4117, "tz": 5.5, "alt": 2.0},
    {"name": "Ankola", "lat": 14.6606, "lon": 74.3047, "tz": 5.5, "alt": 16.0},
    {"name": "Sirsi", "lat": 14.6207, "lon": 74.8355, "tz": 5.5, "alt": 590.0},
    {"name": "Yellapur", "lat": 14.9637, "lon": 74.7093, "tz": 5.5, "alt": 480.0},
    {"name": "Karwar", "lat": 14.8136, "lon": 74.1297, "tz": 5.5, "alt": 10.0},
    {"name": "Puri", "lat": 19.8135, "lon": 85.8312, "tz": 5.5, "alt": 3.0},
    {"name": "Dwarka", "lat": 22.2394, "lon": 68.9678, "tz": 5.5, "alt": 10.0},
    {"name": "Somnath", "lat": 20.8898, "lon": 70.4008, "tz": 5.5, "alt": 3.0},
    {"name": "Rameswaram", "lat": 9.2876, "lon": 79.3129, "tz": 5.5, "alt": 2.0},
    {"name": "Tiruvannamalai", "lat": 12.2253, "lon": 79.0747, "tz": 5.5, "alt": 67.0},
    {"name": "Palakkad", "lat": 10.7867, "lon": 76.6548, "tz": 5.5, "alt": 84.0},
    {"name": "Bhuj", "lat": 23.2420, "lon": 69.6669, "tz": 5.5, "alt": 110.0},
    {"name": "Gandhinagar", "lat": 23.2156, "lon": 72.6369, "tz": 5.5, "alt": 81.0},
    {"name": "Shirdi", "lat": 19.7645, "lon": 74.4767, "tz": 5.5, "alt": 514.0},
    {"name": "Kanyakumari", "lat": 8.0883, "lon": 77.5385, "tz": 5.5, "alt": 30.0},
    {"name": "Belagavi", "lat": 15.8497, "lon": 74.4977, "tz": 5.5, "alt": 751.0},
    {"name": "Kalaburagi", "lat": 17.3297, "lon": 76.8343, "tz": 5.5, "alt": 454.0},
    {"name": "Kolhapur", "lat": 16.7050, "lon": 74.2433, "tz": 5.5, "alt": 546.0},
    {"name": "Nanded", "lat": 19.1383, "lon": 77.3210, "tz": 5.5, "alt": 364.0},
    {"name": "Bhagalpur", "lat": 25.2425, "lon": 86.9843, "tz": 5.5, "alt": 51.0},
    {"name": "Muzaffarpur", "lat": 26.1209, "lon": 85.3647, "tz": 5.5, "alt": 49.0},
    {"name": "Gaya", "lat": 24.7914, "lon": 85.0002, "tz": 5.5, "alt": 111.0},
    {"name": "Bodh Gaya", "lat": 24.6951, "lon": 84.9914, "tz": 5.5, "alt": 110.0},
    {"name": "Vrindavan", "lat": 27.5782, "lon": 77.6468, "tz": 5.5, "alt": 170.0},
    {"name": "Mathura", "lat": 27.4924, "lon": 77.6737, "tz": 5.5, "alt": 174.0},
    {"name": "Ayodhya", "lat": 26.7922, "lon": 82.1998, "tz": 5.5, "alt": 93.0},
    {"name": "Pushkar", "lat": 26.4897, "lon": 74.5511, "tz": 5.5, "alt": 500.0},
    {"name": "Kurukshetra", "lat": 29.9695, "lon": 76.8783, "tz": 5.5, "alt": 250.0},
    {"name": "Nainital", "lat": 29.3803, "lon": 79.4636, "tz": 5.5, "alt": 2084.0},
    {"name": "Mussoorie", "lat": 30.4599, "lon": 78.0397, "tz": 5.5, "alt": 1880.0},
    {"name": "Shimla", "lat": 31.1048, "lon": 77.1734, "tz": 5.5, "alt": 2276.0},
    {"name": "Dharamshala", "lat": 32.2190, "lon": 76.3234, "tz": 5.5, "alt": 1457.0},
    {"name": "Manali", "lat": 32.2396, "lon": 77.1887, "tz": 5.5, "alt": 2050.0},
    {"name": "Rishikesh", "lat": 30.0869, "lon": 78.2676, "tz": 5.5, "alt": 345.0},
    # --- South & South-East Asia ---
    {"name": "Kathmandu", "lat": 27.7172, "lon": 85.3240, "tz": 5.75, "alt": 1400.0},
    {"name": "Lumbini", "lat": 27.4725, "lon": 83.2763, "tz": 5.75, "alt": 105.0},
    {"name": "Pokhara", "lat": 28.2096, "lon": 83.9856, "tz": 5.75, "alt": 822.0},
    {"name": "Colombo", "lat": 6.9271, "lon": 79.8612, "tz": 5.5, "alt": 1.0},
    {"name": "Kandy", "lat": 7.2906, "lon": 80.6337, "tz": 5.5, "alt": 500.0},
    {"name": "Dhaka", "lat": 23.8103, "lon": 90.4125, "tz": 6.0, "alt": 4.0},
    {"name": "Singapur", "lat": 1.3521, "lon": 103.8198, "tz": 8.0, "alt": 15.0},
    {"name": "Kuala Lumpur", "lat": 3.1390, "lon": 101.6869, "tz": 8.0, "alt": 21.0},
    {"name": "Jakarta", "lat": -6.2088, "lon": 106.8456, "tz": 7.0, "alt": 8.0},
    {"name": "Bangkok", "lat": 13.7563, "lon": 100.5018, "tz": 7.0, "alt": 2.0},
    {"name": "Hanoi", "lat": 21.0278, "lon": 105.8342, "tz": 7.0, "alt": 12.0},
    {"name": "Ho Chi Minh City", "lat": 10.8231, "lon": 106.6297, "tz": 7.0, "alt": 19.0},
    {"name": "Manila", "lat": 14.5995, "lon": 120.9842, "tz": 8.0, "alt": 15.0},
    {"name": "Yangon", "lat": 16.8409, "lon": 96.1735, "tz": 6.5, "alt": 9.0},
    {"name": "Phnom Penh", "lat": 11.5564, "lon": 104.9282, "tz": 7.0, "alt": 6.0},
    {"name": "Vientiane", "lat": 17.9757, "lon": 102.6331, "tz": 7.0, "alt": 120.0},
    # --- West Asia / Middle East ---
    {"name": "Dubai", "lat": 25.2048, "lon": 55.2708, "tz": 4.0, "alt": 5.0},
    {"name": "Abu Dhabi", "lat": 24.4539, "lon": 54.3773, "tz": 4.0, "alt": 2.0},
    {"name": "Muscat", "lat": 23.5880, "lon": 58.3829, "tz": 4.0, "alt": 6.0},
    {"name": "Doha", "lat": 25.2854, "lon": 51.5310, "tz": 3.0, "alt": 11.0},
    {"name": "Kuwait City", "lat": 29.3759, "lon": 47.9774, "tz": 3.0, "alt": 5.0},
    {"name": "Manama", "lat": 26.2285, "lon": 50.5860, "tz": 3.0, "alt": 2.0},
    {"name": "Riyadh", "lat": 24.7136, "lon": 46.6753, "tz": 3.0, "alt": 612.0},
    {"name": "Tehran", "lat": 35.6892, "lon": 51.3890, "tz": 3.5, "alt": 1100.0},
    {"name": "Baghdad", "lat": 33.3152, "lon": 44.3661, "tz": 3.0, "alt": 34.0},
    {"name": "Amman", "lat": 31.9539, "lon": 35.9106, "tz": 3.0, "alt": 777.0},
    {"name": "Jerusalem", "lat": 31.7683, "lon": 35.2137, "tz": 2.0, "alt": 786.0},
    {"name": "Beirut", "lat": 33.8938, "lon": 35.5018, "tz": 2.0, "alt": 25.0},
    {"name": "Istanbul", "lat": 41.0082, "lon": 28.9784, "tz": 3.0, "alt": 100.0},
    # --- South-Central Asia ---
    {"name": "Karachi", "lat": 24.8607, "lon": 67.0011, "tz": 5.0, "alt": 8.0},
    {"name": "Lahore", "lat": 31.5497, "lon": 74.3436, "tz": 5.0, "alt": 217.0},
    {"name": "Islamabad", "lat": 33.6844, "lon": 73.0479, "tz": 5.0, "alt": 507.0},
    {"name": "Kabul", "lat": 34.5553, "lon": 69.2075, "tz": 4.5, "alt": 1791.0},
    {"name": "Tashkent", "lat": 41.2995, "lon": 69.2401, "tz": 5.0, "alt": 465.0},
    {"name": "Almaty", "lat": 43.2220, "lon": 76.8512, "tz": 5.0, "alt": 785.0},
    {"name": "Bishkek", "lat": 42.8746, "lon": 74.5698, "tz": 6.0, "alt": 800.0},
    {"name": "Dushanbe", "lat": 38.5598, "lon": 68.7870, "tz": 5.0, "alt": 706.0},
    {"name": "Tbilisi", "lat": 41.7151, "lon": 44.8271, "tz": 4.0, "alt": 380.0},
    {"name": "Yerevan", "lat": 40.1792, "lon": 44.4991, "tz": 4.0, "alt": 990.0},
    {"name": "Baku", "lat": 40.4093, "lon": 49.8671, "tz": 4.0, "alt": 28.0},
    {"name": "Moscow", "lat": 55.7558, "lon": 37.6173, "tz": 3.0, "alt": 144.0},
    # --- East Asia ---
    {"name": "Beijing", "lat": 39.9042, "lon": 116.4074, "tz": 8.0, "alt": 43.0},
    {"name": "Shanghai", "lat": 31.2304, "lon": 121.4737, "tz": 8.0, "alt": 4.0},
    {"name": "Guangzhou", "lat": 23.1291, "lon": 113.2644, "tz": 8.0, "alt": 21.0},
    {"name": "Hong Kong", "lat": 22.3193, "lon": 114.1694, "tz": 8.0, "alt": 8.0},
    {"name": "Taipei", "lat": 25.0330, "lon": 121.5654, "tz": 8.0, "alt": 9.0},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "tz": 9.0, "alt": 40.0},
    {"name": "Osaka", "lat": 34.6937, "lon": 135.5023, "tz": 9.0, "alt": 6.0},
    {"name": "Seoul", "lat": 37.5665, "lon": 126.9780, "tz": 9.0, "alt": 38.0},
    # --- Africa ---
    {"name": "Cairo", "lat": 30.0444, "lon": 31.2357, "tz": 2.0, "alt": 23.0},
    {"name": "Alexandria", "lat": 31.2001, "lon": 29.9187, "tz": 2.0, "alt": 5.0},
    {"name": "Lagos", "lat": 6.5244, "lon": 3.3792, "tz": 1.0, "alt": 41.0},
    {"name": "Nairobi", "lat": -1.2921, "lon": 36.8219, "tz": 3.0, "alt": 1795.0},
    {"name": "Addis Ababa", "lat": 9.0320, "lon": 38.7469, "tz": 3.0, "alt": 2355.0},
    {"name": "Kampala", "lat": 0.3476, "lon": 32.5825, "tz": 3.0, "alt": 1190.0},
    {"name": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "tz": 2.0, "alt": 1753.0},
    {"name": "Cape Town", "lat": -33.9249, "lon": 18.4241, "tz": 2.0, "alt": 25.0},
    {"name": "Accra", "lat": 5.6037, "lon": -0.1870, "tz": 0.0, "alt": 61.0},
    # --- Europe ---
    {"name": "London", "lat": 51.5074, "lon": -0.1278, "tz": 0.0, "alt": 11.0},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522, "tz": 1.0, "alt": 35.0},
    {"name": "Berlin", "lat": 52.5200, "lon": 13.4050, "tz": 1.0, "alt": 34.0},
    {"name": "Rome", "lat": 41.9028, "lon": 12.4964, "tz": 1.0, "alt": 21.0},
    {"name": "Madrid", "lat": 40.4168, "lon": -3.7038, "tz": 1.0, "alt": 655.0},
    {"name": "Amsterdam", "lat": 52.3676, "lon": 4.9041, "tz": 1.0, "alt": 0.0},
    {"name": "Zurich", "lat": 47.3769, "lon": 8.5417, "tz": 1.0, "alt": 408.0},
    {"name": "Vienna", "lat": 48.2082, "lon": 16.3738, "tz": 1.0, "alt": 190.0},
    {"name": "Prague", "lat": 50.0755, "lon": 14.4378, "tz": 1.0, "alt": 235.0},
    {"name": "Warsaw", "lat": 52.2297, "lon": 21.0122, "tz": 1.0, "alt": 110.0},
    {"name": "Brussels", "lat": 50.8503, "lon": 4.3517, "tz": 1.0, "alt": 13.0},
    {"name": "Stockholm", "lat": 59.3293, "lon": 18.0686, "tz": 1.0, "alt": 28.0},
    {"name": "Copenhagen", "lat": 55.6761, "lon": 12.5683, "tz": 1.0, "alt": 14.0},
    {"name": "Athens", "lat": 37.9838, "lon": 23.7275, "tz": 2.0, "alt": 70.0},
    {"name": "Bucharest", "lat": 44.4268, "lon": 26.1025, "tz": 2.0, "alt": 90.0},
    {"name": "Kyiv", "lat": 50.4501, "lon": 30.5234, "tz": 2.0, "alt": 179.0},
    # --- North & South America ---
    {"name": "New York", "lat": 40.7128, "lon": -74.0060, "tz": -5.0, "alt": 10.0},
    {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "tz": -8.0, "alt": 71.0},
    {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194, "tz": -8.0, "alt": 16.0},
    {"name": "Chicago", "lat": 41.8781, "lon": -87.6298, "tz": -6.0, "alt": 181.0},
    {"name": "Houston", "lat": 29.7604, "lon": -95.3698, "tz": -6.0, "alt": 13.0},
    {"name": "Miami", "lat": 25.7617, "lon": -80.1918, "tz": -5.0, "alt": 2.0},
    {"name": "Boston", "lat": 42.3601, "lon": -71.0589, "tz": -5.0, "alt": 43.0},
    {"name": "Seattle", "lat": 47.6062, "lon": -122.3321, "tz": -8.0, "alt": 56.0},
    {"name": "Denver", "lat": 39.7392, "lon": -104.9903, "tz": -7.0, "alt": 1609.0},
    {"name": "Dallas", "lat": 32.7767, "lon": -96.7970, "tz": -6.0, "alt": 130.0},
    {"name": "Atlanta", "lat": 33.7490, "lon": -84.3880, "tz": -5.0, "alt": 320.0},
    {"name": "Phoenix", "lat": 33.4484, "lon": -112.0740, "tz": -7.0, "alt": 331.0},
    {"name": "Toronto", "lat": 43.6532, "lon": -79.3832, "tz": -5.0, "alt": 76.0},
    {"name": "Montreal", "lat": 45.5019, "lon": -73.5674, "tz": -5.0, "alt": 36.0},
    {"name": "Vancouver", "lat": 49.2827, "lon": -123.1207, "tz": -8.0, "alt": 5.0},
    {"name": "Mexico City", "lat": 19.4326, "lon": -99.1332, "tz": -6.0, "alt": 2240.0},
    {"name": "Sao Paulo", "lat": -23.5505, "lon": -46.6333, "tz": -3.0, "alt": 760.0},
    {"name": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729, "tz": -3.0, "alt": 5.0},
    {"name": "Buenos Aires", "lat": -34.6037, "lon": -58.3816, "tz": -3.0, "alt": 25.0},
    {"name": "Lima", "lat": -12.0464, "lon": -77.0428, "tz": -5.0, "alt": 154.0},
    {"name": "Bogota", "lat": 4.7110, "lon": -74.0721, "tz": -5.0, "alt": 2640.0},
    {"name": "Santiago", "lat": -33.4489, "lon": -70.6693, "tz": -4.0, "alt": 570.0},
    {"name": "Montevideo", "lat": -34.9011, "lon": -56.1645, "tz": -3.0, "alt": 43.0},
    {"name": "Quito", "lat": -0.1807, "lon": -78.4678, "tz": -5.0, "alt": 2850.0},
    # --- Oceania ---
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093, "tz": 10.0, "alt": 58.0},
    {"name": "Melbourne", "lat": -37.8136, "lon": 144.9631, "tz": 10.0, "alt": 31.0},
    {"name": "Brisbane", "lat": -27.4698, "lon": 153.0251, "tz": 10.0, "alt": 28.0},
    {"name": "Perth", "lat": -31.9505, "lon": 115.8605, "tz": 8.0, "alt": 15.0},
    {"name": "Auckland", "lat": -36.8509, "lon": 174.7645, "tz": 12.0, "alt": 25.0},
    {"name": "Wellington", "lat": -41.2865, "lon": 174.7762, "tz": 12.0, "alt": 50.0},
]

# ---------------------------------------------------------------------------
# Ashtakoota / Guna Milan data
# ---------------------------------------------------------------------------
KOOTA_NAMES = {
    "en": ["Varna", "Vashya", "Tara", "Yoni", "Graha Maitri",
           "Gana", "Bhakoot", "Nadi"],
    "iast": ["Varṇa", "Vaśya", "Tārā", "Yoni", "Graha Maitrī",
             "Gaṇa", "Bhakūṭa", "Nāḍī"],
    "devanagari": ["वर्ण", "वश्य", "तारा", "योनि", "ग्रह मैत्री",
                   "गण", "भकूट", "नाडी"],
}

TARA_NAMES = {
    "en": ["Janma", "Sampat", "Vipat", "Kshema", "Pratyari",
           "Sadha", "Vadha", "Mitra", "Ati-mitra"],
    "iast": ["Janma", "Sampat", "Vipat", "Kṣema", "Pratyari",
             "Sādhā", "Vadha", "Mitra", "Param-mitra"],
    "devanagari": ["जन्म", "सम्पत्", "विपत्", "क्षेम", "प्रत्यरि",
                   "साधा", "वध", "मित्र", "परम-मित्र"],
}

VERDICT_NAMES = {
    "en": ["Excellent", "Good", "Average", "Poor"],
    "iast": ["Uttama", "Madhyama", "Sāmānya", "Adhama"],
    "devanagari": ["उत्तम", "मध्यम", "सामान्य", "अधम"],
}

VARNA_NAMES = {
    "en": ["Brahmin", "Kshatriya", "Vaishya", "Shudra"],
    "iast": ["Brāhmaṇa", "Kṣatriya", "Vaiśya", "Śūdra"],
    "devanagari": ["ब्राह्मण", "क्षत्रिय", "वैश्य", "शूद्र"],
}

# Varna (caste) by moon sign.
RASHI_VARNA = [1, 2, 3, 0, 1, 2, 3, 0, 1, 3, 2, 0]

# Varna score matrix [bride][groom]; 1 when groom is not inferior, else 0.
VARNA_SCORE = [
    [1, 1, 1, 1],
    [0, 1, 1, 1],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
]

VASHYA_NAMES = {
    "en": ["Chatushpad", "Manav", "Jalachar", "Vanachar", "Dwipad"],
    "iast": ["Chatuṣpada", "Manava", "Jalacara", "Vanacara", "Dvipada"],
    "devanagari": ["चतुष्पद", "मानव", "जलचर", "वनचर", "द्विपद"],
}

# Vashya category of each moon sign (whole-sign assignment).
RASHI_VASHYA = [0, 0, 4, 1, 2, 4, 4, 3, 4, 1, 4, 1]

# Degree-based split for Sagittarius (8) and Capricorn (9):
# (category below split-degree, category at-or-above split-degree).
VASHYA_SPLIT = {8: (4, 0), 9: (0, 1)}

# Vashya score matrix [bride][groom]; max 2.
VASHYA_SCORE = [
    [2, 1, 1, 2, 0],
    [1, 2, 1, 1, 0],
    [1, 1, 2, 1, 0],
    [2, 1, 1, 2, 0],
    [0, 0, 0, 0, 2],
]

GANA_NAMES = {
    "en": ["Deva", "Manushya", "Rakshasa"],
    "iast": ["Deva", "Manuṣya", "Rākṣasa"],
    "devanagari": ["देव", "मनुष्य", "राक्षस"],
}

# Gana by nakshatra.
NAKSHATRA_GANA = [
    1, 1, 0, 0, 1, 2, 0, 0, 2, 2, 1, 1, 0, 2, 0, 1, 0, 2, 2,
    1, 1, 0, 2, 2, 1, 1, 0,
]

# Gana score matrix [bride][groom]; max 6.
GANA_SCORE = [
    [6, 5, 0],
    [5, 6, 0],
    [0, 0, 4],
]

NADI_NAMES = {
    "en": ["Aadi", "Madhya", "Antya"],
    "iast": ["Ādi", "Madhya", "Antya"],
    "devanagari": ["आदि", "मध्य", "अन्त्य"],
}

# Nadi by nakshatra.
NAKSHATRA_NADI = [
    2, 2, 2, 0, 0, 0, 1, 1, 1, 2, 2, 2, 0, 0, 0, 1, 1, 1, 2, 2,
    2, 0, 0, 0, 1, 1, 1,
]

YONI_NAMES = {
    "en": ["Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat",
           "Rat", "Cow", "Buffalo", "Tiger", "Deer", "Monkey",
           "Mongoose", "Lion"],
    "iast": ["Aśva", "Gaja", "Meṣa", "Sarpa", "Śvāna", "Mārjāra",
             "Ākhu", "Gau", "Mahiṣa", "Vyāghra", "Mṛga", "Mārkaṭa",
             "Nakula", "Siṁha"],
    "devanagari": ["अश्व", "गज", "मेष", "सर्प", "श्वान", "मार्जार",
                   "आखु", "गौ", "महिष", "व्याघ्र", "मृग", "मार्कट",
                   "नकुल", "सिंह"],
}

# Yoni index (into YONI_NAMES) by nakshatra.
NAKSHATRA_YONI = [
    0, 1, 2, 3, 13, 12, 4, 2, 5, 6, 11, 10, 7, 0, 8, 9, 10, 2,
    12, 11, 13, 6, 5, 3, 13, 7, 0,
]

YONI_FRIEND_PAIRS = {(0, 1), (1, 7)}
YONI_BITTER_ENEMY = {(0, 2), (0, 3), (0, 4), (1, 5), (2, 10), (5, 8), (6, 7)}
YONI_MILD_ENEMY = {(3, 6)}

# Tara (Dina) favourable / malefic remainder sets.
TARA_FAVOURABLE = {0, 1, 2, 4, 6, 8}
TARA_MALEFIC = {3, 5, 7}

# Bhakoot (moon-sign distance based) sets.
BHAKOOT_BAD_DIST = {2, 5, 6, 7, 10}
BHAKOOT_GOOD_DIST = {0, 1, 3, 4, 8, 9, 11}

# Cross-language grouping names for API convenience.
GROUPING_NAMES = {
    "varna": VARNA_NAMES,
    "vashya": VASHYA_NAMES,
    "gana": GANA_NAMES,
    "nadi": NADI_NAMES,
}