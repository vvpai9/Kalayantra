#!/usr/bin/env python3
"""
Kalakosha - Static Knowledge Repository
Contains static data, translations, constants, offline city database,
and festival metadata. No calculations are performed in this module.
"""

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

SAURA_MASAS = {
    "en": [
        "Madhu (Mesha)", "Madhava (Vrishabha)", "Shukra (Mithuna)", "Suchi (Karka)", "Nabhas (Simha)", "Nabhasya (Kanya)",
        "Issa (Tula)", "Urja (Vrischika)", "Sahas (Dhanu)", "Sahasya (Makara)", "Tapas (Kumbha)", "Tapasya (Mina)"
    ],
    "iast": [
        "Madhu (Meṣa)", "Mādhava (Vṛṣabha)", "Śukra (Mithuna)", "Śuci (Karka)", "Nabhas (Siṃha)", "Nabhasya (Kanyā)",
        "Iṣa (Tulā)", "Ūrja (Vṛścika)", "Sahas (Dhanu)", "Sahasya (Makara)", "Tapas (Kumbha)", "Tapasya (Mīna)"
    ],
    "devanagari": [
        "मधु (मेष)", "माधव (वृषभ)", "शुक्र (मिथुन)", "शुचि (कर्क)", "नभस् (सिंह)", "नभस्य (कन्या)",
        "इष (तुला)", "ऊर्ज (वृश्चिक)", "सहस (धनु)", "सहस्य (मकर)", "तपस् (कुंभ)", "तपस्य (मीन)"
    ]
}

RITUS = {
    "en": ["Vasanta (Spring)", "Grishma (Summer)", "Varsha (Monsoon)", "Sharad (Autumn)", "Hemanta (Pre-winter)", "Shishira (Winter)"],
    "iast": ["Vasanta", "Grīṣma", "Varṣā", "Śarad", "Hemanta", "Śiśira"],
    "devanagari": ["वसन्त", "ग्रीष्म", "वर्षा", "शरद", "हेमन्त", "शिशिर"]
}

AYANAS = {
    "en": ["Uttarayana", "Dakshinayana"],
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

CHOGHADIYA_DAY_START = {0: 3, 1: 6, 2: 2, 3: 5, 4: 1, 5: 4, 6: 0}
CHOGHADIYA_NIGHT_START = {0: 6, 1: 2, 2: 0, 3: 1, 4: 4, 5: 3, 6: 5}

SANKRANTIS = {
    "en": ["Mesha Sankranti", "Vrishabha Sankranti", "Mithuna Sankranti", "Karka Sankranti", "Simha Sankranti", "Kanya Sankranti", "Tula Sankranti", "Vrishchika Sankranti", "Dhanu Sankranti", "Makar Sankranti", "Kumbha Sankranti", "Meena Sankranti"],
    "iast": ["Meṣa Saṅkrānti", "Vṛṣabha Saṅkrānti", "Mithuna Saṅkrānti", "Karka Saṅkrānti", "Siṃha Saṅkrānti", "Kanyā Saṅkrānti", "Tulā Saṅkrānti", "Vṛścika Saṅkrānti", "Dhanu Saṅkrānti", "Makara Saṅkrānti", "Kumbha Saṅkrānti", "Mīna Saṅkrānti"],
    "devanagari": ["मेष संक्रान्ति", "वृषभ संक्रान्ति", "मिथुन संक्रान्ति", "कर्क संक्रान्ति", "सिंह संक्रान्ति", "कन्या संक्रान्ति", "तुला संक्रान्ति", "वृश्चिक संक्रान्ति", "धनु संक्रान्ति", "मकर संक्रान्ति", "कुम्भ संक्रान्ति", "मीन संक्रान्ति"]
}

# Names of 24 Ekadashis (+2 for Adhika Masa)
EKADASHI_NAMES = {
    # (masa_idx, is_krishna) -> {"en": ..., "iast": ..., "devanagari": ...}
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
    ("adhika", True): {"en": "Parama Ekadashi", "iast": "Paramā Ekādaśī", "devanagari": "परमा एकादशी"}
}

FESTIVAL_METADATA = {
    "gudi_padwa": {
        "priority": 10,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi at Sunrise (Udaya-vyapini)",
        "en": "Ugadi / Gudi Padwa",
        "iast": "Yugādi / Guḍhī Pāḍavā",
        "devanagari": "युगादि / गुढी पाडवा",
        "description": "Chaitra Shukla Pratipada Hindu New Year marking the dawn of the creation."
    },
    "rama_navami": {
        "priority": 10,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing at Madhyahna (Noon)",
        "en": "Rama Navami",
        "iast": "Rāma Navamī",
        "devanagari": "राम नवमी",
        "description": "Celebration of the birth of Lord Rama, incarnation of Vishnu."
    },
    "hanuman_janmotsav": {
        "priority": 9,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi at Sunrise (Udaya-vyapini)",
        "en": "Hanuman Janmotsav",
        "iast": "Hanumān Janmotsava",
        "devanagari": "हनुमान जन्मोत्सव",
        "description": "Celebration of the birth of Lord Hanuman, the supreme devotee of Lord Rama."
    },
    "parashurama_jayanti": {
        "priority": 8,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing at Pradosha (Evening)",
        "en": "Parashurama Jayanti",
        "iast": "Paraśurāma Jayantī",
        "devanagari": "परशुराम जयंती",
        "description": "Appearance day of Lord Parashurama, the sixth incarnation of Lord Vishnu."
    },
    "akshaya_tritiya": {
        "priority": 9,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing at Sunrise (Purvahna-vyapini)",
        "en": "Akshaya Tritiya",
        "iast": "Akṣaya Tṛtīyā",
        "devanagari": "अक्षय तृतीया",
        "description": "Highly auspicious day for new ventures, charity, and buying gold."
    },
    "narasimha_jayanti": {
        "priority": 9,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing at Pradosha (Evening)",
        "en": "Narasimha Jayanti",
        "iast": "Narasiṃha Jayantī",
        "devanagari": "नरसिंह जयंती",
        "description": "Appearance day of Lord Narasimha, the half-man half-lion avatar of Vishnu."
    },
    "vat_savitri_amavasya": {
        "priority": 8,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing at Sunrise",
        "en": "Vat Savitri Vrata (Amavasya)",
        "iast": "Vaṭa Sāvitrī Vrata (Amāvāsyā)",
        "devanagari": "वट सावित्री व्रत (अमावस्या)",
        "description": "Fast observed by married women for longevity and well-being of husbands."
    },
    "vat_savitri_purnima": {
        "priority": 8,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing at Sunrise",
        "en": "Vat Savitri Vrata (Purnima)",
        "iast": "Vaṭa Sāvitrī Vrata (Pūrṇimā)",
        "devanagari": "वट सावित्री व्रत (पूर्णिमा)",
        "description": "Fast observed by married women in West/South India during Jyeshtha Purnima."
    },
    "guru_purnima": {
        "priority": 9,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing at Sunrise",
        "en": "Guru Purnima",
        "iast": "Guru Pūrṇimā",
        "devanagari": "गुरु पूर्णिमा",
        "description": "Day dedicated to expressing gratitude to spiritual and academic gurus."
    },
    "nag_panchami": {
        "priority": 8,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing at Sunrise",
        "en": "Nag Panchami",
        "iast": "Nāga Pañcamī",
        "devanagari": "नाग पञ्चमी",
        "description": "Nag Panchami snake worship day."
    },
    "raksha_bandhan": {
        "priority": 9,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing during Aparahna (Afternoon)",
        "en": "Raksha Bandhan / Upakarma",
        "iast": "Rakṣābandhana / Upākarma",
        "devanagari": "रक्षाबन्धन / उपाकर्म",
        "description": "Celebration of sibling bonds and traditional Vedic thread ceremony."
    },
    "varamahalakshmi_vrata": {
        "priority": 8,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Friday preceding Shravana Purnima",
        "en": "Varamahalakshmi Vrata",
        "iast": "Varamahālakṣmī Vrata",
        "devanagari": "वरमहालक्ष्मी व्रत",
        "description": "Worship of Goddess Lakshmi for prosperity and wealth."
    },
    "krishna_janmashtami": {
        "priority": 10,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing during Nishitha (Midnight)",
        "en": "Krishna Janmashtami",
        "iast": "Kṛṣṇa Janmāṣṭamī",
        "devanagari": "कृष्ण जन्माष्टमी",
        "description": "Celebration of the birth of Lord Krishna, incarnation of Vishnu."
    },
    "swarna_gauri": {
        "priority": 8,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing at Sunrise",
        "en": "Swarna Gauri Vrata",
        "iast": "Svarṇa Gaurī Vrata",
        "devanagari": "स्वर्ण गौरी व्रत",
        "description": "Worship of Goddess Gauri preceding Ganesh Chaturthi."
    },
    "ganesh_chaturthi": {
        "priority": 10,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing during Madhyahna (Noon)",
        "en": "Ganesh Chaturthi",
        "iast": "Gaṇeśa Caturthī",
        "devanagari": "गणेश चतुर्थी",
        "description": "Grand festival celebrating the birth of Lord Ganesha, the remover of obstacles."
    },
    "rishi_panchami": {
        "priority": 7,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing during Madhyahna (Noon)",
        "en": "Rishi Panchami",
        "iast": "Ṛṣi Pañcamī",
        "devanagari": "ऋषि पञ्चमी",
        "description": "Worship of the Saptarishis (seven sages) for purification and debt release."
    },
    "ananta_chaturdashi": {
        "priority": 9,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing at Sunrise",
        "en": "Ananta Chaturdashi",
        "iast": "Ananta Caturdaśī",
        "devanagari": "अनन्त चतुर्दशी",
        "description": "Worship of Lord Ananta (Vishnu) with the sacred 14-knot thread."
    },
    "mahalaya_amavasya": {
        "priority": 8,
        "type": "Ritual",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing during Aparahna / Pradosha",
        "en": "Mahalaya Amavasya",
        "iast": "Mahālaya Amāvāsyā",
        "devanagari": "महालया अमावस्या",
        "description": "Highly sacred day for performing ancestral shradh rites."
    },
    "mahanavami": {
        "priority": 9,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing during Madhyahna / Pradosha",
        "en": "Maha Navami",
        "iast": "Mahā Navamī",
        "devanagari": "महानवमी",
        "description": "Ninth day of Navratri dedicated to Goddess Siddhidatri."
    },
    "vijayadashami": {
        "priority": 10,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing during Aparahna (Afternoon)",
        "en": "Vijayadashami / Dasara",
        "iast": "Vijayadaśamī / Dasaharā",
        "devanagari": "विजयादशमी / दशहरा",
        "description": "Celebration of good over evil: Lord Rama over Ravana, Durga over Mahishasura."
    },
    "kojagari_purnima": {
        "priority": 8,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing during Nishitha (Midnight)",
        "en": "Kojagari / Sharad Purnima",
        "iast": "Kojāgarī Pūrṇimā",
        "devanagari": "कोजागरी पूर्णिमा",
        "description": "Night of wakefulness and worship of Goddess Lakshmi and Moon god."
    },
    "naraka_chaturdashi": {
        "priority": 9,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing at Arunodaya (Pre-dawn)",
        "en": "Naraka Chaturdashi",
        "iast": "Naraka Caturdaśī",
        "devanagari": "नरक चतुर्दशी",
        "description": "Deepavali pre-dawn holy bath celebrating victory over Narakasura."
    },
    "deepavali": {
        "priority": 10,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing during Pradosha (Evening)",
        "en": "Deepavali / Laxmi Puja",
        "iast": "Dīpāvalī / Lakṣmī Pūjā",
        "devanagari": "दीपावली / लक्ष्मी पूजा",
        "description": "Festival of Lights celebrating return of Lord Rama and welcoming Goddess Lakshmi."
    },
    "bali_pratipada": {
        "priority": 9,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing at Sunrise",
        "en": "Bali Pratipada / Govardhan Puja",
        "iast": "Bali Pratipadā / Govardhana Pūjā",
        "devanagari": "बलि प्रतिपदा / गोवर्धन पूजा",
        "description": "Worship of King Bali and Lord Krishna's lifting of Govardhan hill."
    },
    "tulsi_vivah": {
        "priority": 9,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing during Pradosha (Evening)",
        "en": "Tulsi Vivah",
        "iast": "Tulasī Vivāha",
        "devanagari": "तुलसी विवाह",
        "description": "Ceremonial wedding of Tulsi plant (Goddess Vrinda) to Shaligram (Lord Vishnu)."
    },
    "champa_shashthi": {
        "priority": 7,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing at Sunrise",
        "en": "Champa Shashthi",
        "iast": "Campā Ṣaṣṭhī",
        "devanagari": "चम्पा षष्ठी",
        "description": "Festival dedicated to Lord Khandoba, avatar of Lord Shiva."
    },
    "datta_jayanti": {
        "priority": 8,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing during Pradosha (Evening)",
        "en": "Datta Jayanti",
        "iast": "Datta Jayantī",
        "devanagari": "दत्त जयंती",
        "description": "Birth anniversary of Lord Dattatreya, the unified form of Trimurti."
    },
    "ratha_saptami": {
        "priority": 9,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing at Arunodaya (Pre-dawn)",
        "en": "Ratha Saptami",
        "iast": "Ratha Saptamī",
        "devanagari": "रथसप्तमी",
        "description": "Auspicious day when Sun changes his path to Northern hemisphere."
    },
    "bhishma_ashtami": {
        "priority": 7,
        "type": "Ritual",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing during Madhyahna (Noon)",
        "en": "Bhishma Ashtami",
        "iast": "Bhīṣma Aṣṭamī",
        "devanagari": "भीष्म अष्टमी",
        "description": "Day dedicated to memory of Bhishma Pitamah's voluntary departure."
    },
    "madhwa_navami": {
        "priority": 8,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing at Sunrise",
        "en": "Madhwa Navami",
        "iast": "Madhva Navamī",
        "devanagari": "मध्व नवमी",
        "description": "Day commemorating Sri Madhvacharya's departure to Badri."
    },
    "mahashivaratri": {
        "priority": 10,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing during Nishitha (Midnight)",
        "en": "Maha Shivaratri",
        "iast": "Mahā Śivarātri",
        "devanagari": "महाशिवरात्रि",
        "description": "Great Night of Lord Shiva, celebrating cosmic cosmic union and spiritual awakening."
    },
    "holi": {
        "priority": 10,
        "type": "Maha",
        "color": "#2ecc71",
        "notify": "high",
        "rule": "Tithi prevailing during Pradosha (Evening)",
        "en": "Holi / Holika Dahan",
        "iast": "Holī / Holikā Dahana",
        "devanagari": "होली / होलिका दहन",
        "description": "Spring Festival of colors celebrating the victory of Bhakta Prahlada."
    },
    "sankashti_chaturthi": {
        "priority": 8,
        "type": "Vrata",
        "color": "#2ecc71",
        "notify": "normal",
        "rule": "Tithi prevailing during Moonrise",
        "en": "Sankashti Chaturthi",
        "iast": "Saṅkaṣṭī Caturthī",
        "devanagari": "संकष्टी चतुर्थी",
        "description": "Monthly fast for Lord Ganesha, broken after moonrise."
    }
}

# Pre-packaged 100+ cities database
BUILTIN_CITIES = [
    # Defaults and major Indian cities
    {"name": "Ujjain", "lat": 23.1765, "lon": 75.7885, "tz": 5.5, "alt": 511.0},
    {"name": "New Delhi", "lat": 28.6139, "lon": 77.2090, "tz": 5.5, "alt": 216.0},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "tz": 5.5, "alt": 14.0},
    {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "tz": 5.5, "alt": 920.0},
    {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639, "tz": 5.5, "alt": 9.0},
    {"name": "Chennai", "lat": 13.0827, "lon": 80.2707, "tz": 5.5, "alt": 6.0},
    {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "tz": 5.5, "alt": 542.0},
    {"name": "Pune", "lat": 18.5204, "lon": 73.8567, "tz": 5.5, "alt": 560.0},
    {"name": "Ahmedabad", "lat": 23.0225, "lon": 72.5714, "tz": 5.5, "alt": 53.0},
    {"name": "Jaipur", "lat": 26.9124, "lon": 75.7873, "tz": 5.5, "alt": 431.0},
    {"name": "Varanasi", "lat": 25.3176, "lon": 82.9739, "tz": 5.5, "alt": 81.0},
    {"name": "Surat", "lat": 21.1702, "lon": 72.8311, "tz": 5.5, "alt": 13.0},
    {"name": "Lucknow", "lat": 26.8467, "lon": 80.9462, "tz": 5.5, "alt": 123.0},
    {"name": "Kanpur", "lat": 26.4499, "lon": 80.3319, "tz": 5.5, "alt": 126.0},
    {"name": "Nagpur", "lat": 21.1458, "lon": 79.0882, "tz": 5.5, "alt": 310.0},
    {"name": "Indore", "lat": 22.7196, "lon": 75.8577, "tz": 5.5, "alt": 553.0},
    {"name": "Thane", "lat": 19.2183, "lon": 72.9781, "tz": 5.5, "alt": 8.0},
    {"name": "Bhopal", "lat": 23.2599, "lon": 77.4126, "tz": 5.5, "alt": 427.0},
    {"name": "Visakhapatnam", "lat": 17.6868, "lon": 83.2185, "tz": 5.5, "alt": 45.0},
    {"name": "Patna", "lat": 25.5941, "lon": 85.1376, "tz": 5.5, "alt": 53.0},
    {"name": "Vadodara", "lat": 22.3072, "lon": 73.1812, "tz": 5.5, "alt": 129.0},
    {"name": "Ghaziabad", "lat": 28.6692, "lon": 77.4538, "tz": 5.5, "alt": 210.0},
    {"name": "Ludhiana", "lat": 30.9010, "lon": 75.8573, "tz": 5.5, "alt": 244.0},
    {"name": "Agra", "lat": 27.1767, "lon": 78.0081, "tz": 5.5, "alt": 171.0},
    {"name": "Nashik", "lat": 19.9975, "lon": 73.7898, "tz": 5.5, "alt": 600.0},
    {"name": "Faridabad", "lat": 28.4089, "lon": 77.3178, "tz": 5.5, "alt": 198.0},
    {"name": "Meerut", "lat": 28.9845, "lon": 77.7064, "tz": 5.5, "alt": 219.0},
    {"name": "Rajkot", "lat": 22.3039, "lon": 70.8022, "tz": 5.5, "alt": 128.0},
    {"name": "Kalyan", "lat": 19.2403, "lon": 73.1305, "tz": 5.5, "alt": 9.0},
    {"name": "Vasai", "lat": 19.3913, "lon": 72.8397, "tz": 5.5, "alt": 4.0},
    {"name": "Srinagar", "lat": 34.0837, "lon": 74.7973, "tz": 5.5, "alt": 1585.0},
    {"name": "Aurangabad", "lat": 19.8762, "lon": 75.3433, "tz": 5.5, "alt": 583.0},
    {"name": "Dhanbad", "lat": 23.7957, "lon": 86.4304, "tz": 5.5, "alt": 222.0},
    {"name": "Amritsar", "lat": 31.6340, "lon": 74.8723, "tz": 5.5, "alt": 234.0},
    {"name": "Navi Mumbai", "lat": 19.0330, "lon": 73.0297, "tz": 5.5, "alt": 14.0},
    {"name": "Prayagraj", "lat": 25.4358, "lon": 81.8463, "tz": 5.5, "alt": 98.0},
    {"name": "Howrah", "lat": 22.5958, "lon": 88.2636, "tz": 5.5, "alt": 12.0},
    {"name": "Gwalior", "lat": 26.2183, "lon": 78.1828, "tz": 5.5, "alt": 197.0},
    {"name": "Jabalpur", "lat": 22.1560, "lon": 79.9320, "tz": 5.5, "alt": 411.0},
    {"name": "Coimbatore", "lat": 11.0168, "lon": 76.9558, "tz": 5.5, "alt": 411.0},
    {"name": "Vijayawada", "lat": 16.5062, "lon": 80.6480, "tz": 5.5, "alt": 11.0},
    {"name": "Jodhpur", "lat": 26.2389, "lon": 73.0243, "tz": 5.5, "alt": 231.0},
    {"name": "Madurai", "lat": 9.9252, "lon": 78.1198, "tz": 5.5, "alt": 101.0},
    {"name": "Raipur", "lat": 21.2514, "lon": 81.6296, "tz": 5.5, "alt": 298.0},
    {"name": "Kota", "lat": 25.1825, "lon": 75.8262, "tz": 5.5, "alt": 271.0},
    {"name": "Guwahati", "lat": 26.1158, "lon": 91.7086, "tz": 5.5, "alt": 55.0},
    {"name": "Chandigarh", "lat": 30.7333, "lon": 76.7794, "tz": 5.5, "alt": 321.0},
    {"name": "Dehradun", "lat": 30.3165, "lon": 78.0322, "tz": 5.5, "alt": 648.0},
    {"name": "Shimla", "lat": 31.1048, "lon": 77.1734, "tz": 5.5, "alt": 2206.0},
    {"name": "Haridwar", "lat": 29.9457, "lon": 78.1642, "tz": 5.5, "alt": 314.0},
    {"name": "Rishikesh", "lat": 30.0869, "lon": 78.2676, "tz": 5.5, "alt": 372.0},
    {"name": "Mathura", "lat": 27.4924, "lon": 77.6737, "tz": 5.5, "alt": 174.0},
    {"name": "Ayodhya", "lat": 26.7922, "lon": 82.1998, "tz": 5.5, "alt": 93.0},
    {"name": "Tirupati", "lat": 13.6288, "lon": 79.4192, "tz": 5.5, "alt": 162.0},
    {"name": "Puri", "lat": 19.8135, "lon": 85.8312, "tz": 5.5, "alt": 0.0},
    {"name": "Mysuru", "lat": 12.2958, "lon": 76.6394, "tz": 5.5, "alt": 763.0},
    {"name": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366, "tz": 5.5, "alt": 5.0},
    {"name": "Kochi", "lat": 9.9312, "lon": 76.2673, "tz": 5.5, "alt": 4.0},
    {"name": "Kozhikode", "lat": 11.2588, "lon": 75.7804, "tz": 5.5, "alt": 1.0},
    {"name": "Ranchi", "lat": 23.3441, "lon": 85.3096, "tz": 5.5, "alt": 651.0},
    {"name": "Jamshedpur", "lat": 22.8046, "lon": 86.2029, "tz": 5.5, "alt": 135.0},
    {"name": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245, "tz": 5.5, "alt": 45.0},
    {"name": "Cuttack", "lat": 20.4625, "lon": 85.8830, "tz": 5.5, "alt": 37.0},
    
    # Major International Cities
    {"name": "London", "lat": 51.5074, "lon": -0.1278, "tz": 0.0, "alt": 11.0},
    {"name": "New York", "lat": 40.7128, "lon": -74.0060, "tz": -5.0, "alt": 10.0},
    {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194, "tz": -8.0, "alt": 16.0},
    {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "tz": -8.0, "alt": 71.0},
    {"name": "Chicago", "lat": 41.8781, "lon": -87.6298, "tz": -6.0, "alt": 179.0},
    {"name": "Houston", "lat": 29.7604, "lon": -95.3698, "tz": -6.0, "alt": 12.0},
    {"name": "Boston", "lat": 42.3601, "lon": -71.0589, "tz": -5.0, "alt": 14.0},
    {"name": "Seattle", "lat": 47.6062, "lon": -122.3321, "tz": -8.0, "alt": 53.0},
    {"name": "Washington D.C.", "lat": 38.9072, "lon": -77.0369, "tz": -5.0, "alt": 7.0},
    {"name": "Toronto", "lat": 43.6532, "lon": -79.3832, "tz": -5.0, "alt": 76.0},
    {"name": "Vancouver", "lat": 49.2827, "lon": -123.1207, "tz": -8.0, "alt": 4.0},
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093, "tz": 10.0, "alt": 19.0},
    {"name": "Melbourne", "lat": -37.8136, "lon": 144.9631, "tz": 10.0, "alt": 31.0},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503, "tz": 9.0, "alt": 44.0},
    {"name": "Singapore", "lat": 1.3521, "lon": 103.8198, "tz": 8.0, "alt": 15.0},
    {"name": "Dubai", "lat": 25.2048, "lon": 55.2708, "tz": 4.0, "alt": 5.0},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522, "tz": 1.0, "alt": 35.0},
    {"name": "Berlin", "lat": 52.5200, "lon": 13.4050, "tz": 1.0, "alt": 34.0},
    {"name": "Rome", "lat": 41.9028, "lon": 12.4964, "tz": 1.0, "alt": 21.0},
    {"name": "Munich", "lat": 48.1351, "lon": 11.5820, "tz": 1.0, "alt": 519.0},
    {"name": "Geneva", "lat": 46.2044, "lon": 6.1432, "tz": 1.0, "alt": 375.0},
    {"name": "Moscow", "lat": 55.7558, "lon": 37.6173, "tz": 3.0, "alt": 156.0},
    {"name": "Johannesburg", "lat": -26.2041, "lon": 28.0473, "tz": 2.0, "alt": 1753.0}
]
