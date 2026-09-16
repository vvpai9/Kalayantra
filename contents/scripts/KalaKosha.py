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
           "Shukra", "Shani", "Rahu", "Ketu"],
    "iast": ["Sūrya", "Candra", "Maṅgala", "Budha", "Guru",
             "Śukra", "Śani", "Rāhu", "Ketu"],
    "devanagari": ["सूर्य", "चन्द्र", "मङ्गल", "बुध", "गुरु",
                   "शुक्र", "शनि", "राहु", "केतु"],
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
    "en": ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"],
    "iast": ["Su", "Ca", "Ma", "Bu", "Gu", "Śu", "Śa", "Rā", "Ke"],
    "devanagari": ["सू", "चं", "मं", "बु", "गु", "शु", "श", "रा", "के"],
}

# Owner planet index (0..8) of each rashi.
RASHI_LORD = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]

# Exaltation (uccha) sign / degree per planet; nodes have none.
EXALTATION_SIGN = [0, 2, 10, 5, 4, 11, 6, None, None]
EXALTATION_DEGREE = [10.0, 3.0, 28.0, 15.0, 5.0, 27.0, 20.0, None, None]

# Own signs per planet.
OWN_SIGNS = {0: [4], 1: [3], 2: [0, 7], 3: [2, 5], 4: [8, 11],
             5: [6, 1], 6: [9, 10], 7: [], 8: []}

# Moolatrikona sign per planet; nodes have none.
MOOLATRIKONA_SIGN = {0: 4, 1: 3, 2: 0, 3: 5, 4: 8, 5: 6, 6: 9,
                     7: None, 8: None}

# Natural friends / enemies / neutrals (planetary index sets).
GRAHA_FRIENDS = {0: {1, 2, 4}, 1: {0, 3}, 2: {0, 4}, 3: {1, 5},
                 4: {0, 2, 6}, 5: {3, 6}, 6: {3, 5}}
GRAHA_ENEMIES = {0: {5, 6}, 1: set(), 2: {5}, 3: {4}, 4: {1, 5},
                 5: {0, 2}, 6: {0, 1, 4}}
GRAHA_NEUTRALS = {0: {3}, 1: {2, 4, 5, 6}, 2: {1, 3, 6}, 3: {0, 2, 6},
                  4: {3}, 5: {1, 4}, 6: {2}}

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