import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: view
    implicitWidth: 520
    implicitHeight: 640

    property var result: null
    property var planetRows
    property var houseRows
    property var vargaPlacements
    property var shadbalaTable
    property var cityChoices
    property var karakaRows
    property var karakaCells
    property int karakaScheme: 7
    property var ghatakRows
    property var savedProfiles

    // Column widths (grid units) for the "Nine Grahas" list header + rows.
    readonly property var grahaSpan: ({
        "nm": Kirigami.Units.gridUnit * 4.2,
        "deg": Kirigami.Units.gridUnit * 3.0,
        "sign": Kirigami.Units.gridUnit * 3.6,
        "dig": Kirigami.Units.gridUnit * 3.8,
        "motion": Kirigami.Units.gridUnit * 3.0,
        "asta": Kirigami.Units.gridUnit * 2.8,
        "v": Kirigami.Units.gridUnit * 2.6,
        "r": Kirigami.Units.gridUnit * 3.6
    })

    property int expandedMd: -1
    property int expandedAd: -1
    property bool autoAdFocus: true

    property var analysisModel: null
    property string analysisError: ""
    property bool analysisBusy: false
    property var _analysisBodha: null
    property var _analysisMedha: null

    signal requestAnalysis()

    Timer {
        id: analysisTimer
        interval: 250
        onTriggered: view.reveal(analysisSection)
    }

    Component.onCompleted: {
        // QML defers `property var <name>: []` initializers to first read, so a
        // `visible: rows.length > 0` binding that runs first can see `undefined`
        // and its thrown binding never recovers.  Default them to [] eagerly.
        view.planetRows = [];
        view.houseRows = [];
        view.vargaPlacements = [];
        view.shadbalaTable = [];
        view.cityChoices = [];
        view.karakaRows = [];
        view.karakaCells = [];
        view.ghatakRows = [];
        view.savedProfiles = [];
        view.prefillCity();
    }

    readonly property var vargaKeys: ["D1", "D2", "D3", "D4", "D7", "D8", "D9", "D10", "D11", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]

    readonly property var rashisEn: ["Mesh", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makar", "Kumbha", "Meena"]
    readonly property var rashisIast: ["Meṣa", "Vṛṣabha", "Mithuna", "Karka", "Siṃha", "Kanyā", "Tulā", "Vṛścika", "Dhanu", "Makara", "Kumbha", "Mīna"]
    readonly property var rashisDev: ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]

    readonly property var uiTxt: ({
        "en": {
            "title": "Kundali (Natal Chart)",
            "compute": "Compute",
            "searchCity": "City",
            "searchPlaceholder": "Search city…",
            "searchBtn": "Find",
            "manualCrd": "Or enter coordinates",
            "actualCoords": "Birth place",
            "lat": "Lat",
            "lon": "Lon",
            "alt": "Alt (m)",
            "tzh": "TZ (h)",
            "date": "Date",
            "month": "Month",
            "year": "Year",
            "latLabel": "Lat",
            "lonLabel": "Lon",
            "altLabel": "Alt (m)",
            "tzLabel": "Time zone (h)",
            "lagna": "Lagna:",
            "nineGrahas": "Nine Grahas",
            "vargas": "Vargas (divisional charts)",
            "vargaChart": "Varga chart",
            "vimshottari": "Vimshottari Dasha",
            "balance": "balance",
            "ayanamsa": "Ayanamsa",
            "noChart": "No chart computed yet.",
            "invalidDate": "Enter a valid date as DD-MM-YYYY.",
            "computing": "Computing…",
            "analysing": "Analysing chart…",
            "parseFail": "Failed to parse response.",
            "engineErr": "Engine error (%1). Is the daemon running?",
            "searchErr": "City search failed (%1).",
            "housePrefix": "H",
            "houseHead": "House %1 · %2",
            "sayana": "Sayana (Tropical)",
            "style": "Chart style",
            "north": "North Indian",
            "south": "South Indian",
            "east": "East Indian",
            "motion": "Motion",
            "vakri": "Vakri (R)",
            "maargi": "Maargi",
            "asta": "Asta",
            "vargottam": "Vargottam",
            "dig": "Dignity",
            "deg": "Deg",
            "nakCol": "Nakshatra",
            "rashiCol": "Rashi #",
            "lord": "Lord",
            "houses": "Houses",
            "current": "Now running",
            "md": "Mahadasha",
            "ad": "Antardasha",
            "pd": "Pratyantardasha",
            "show": "Expand",
            "dashaHeader": "9 Mahadashas · current auto-expanded",
            "selectVarga": "Division",
            "digLegend": "<font color='#e67e22'><b>R</b></font> = Rashi (sign) number of the Graha · <b>ᴷ</b> = Kendra (1/4/7/10) · <font color='#2ecc71'><b>V</b></font> = Vargottam (same sign in D1 &amp; D9) · <font color='#c0392b'><b>ᴿ</b></font>/red names = Vakri · <b>●</b> = Asta",
            "rTooltip": "R = Rashi (sign) number: this Graha occupies sign no. %1 — %2. 1 = Mesh, 12 = Meena. Appended ᴷ means the sign is a Kendra (1/4/7/10).",
            "vTooltip": "V = Vargottam: this Graha sits in the same sign in both the Rashi (D1) and Navamsa (D9) charts — considered strong.",
            "analyze": "Analyse",
            "analyzing": "Analyzing…",
            "analysisYogas": "Yogas detected:",
            "noYogas": "No structured yogas detected.",
            "formation": "Formation:",
            "participants": "Planets:",
            "effect": "Effect:",
            "source": "Source:",
            "moonSign": "Moon Sign:",
            "nakLord": "Nakshatra Lord:",
            "nameInitial": "Name Initial:",
            "upapada": "Upapada Lagna",
            "shreeLagna": "Shree Lagna",
            "induLagna": "Indu Lagna",
            "specialLagnas": "Special Lagnas",
            "shadbala": "Shadbala (Six-fold Strength)",
            "strong": "Strong",
            "weak": "Weak",
            "rupas": "Rupas",
            "required": "Required",
            "total": "Total",
            "sbSthana": "Sthana",
            "sbDig": "Dig",
            "sbKala": "Kala",
            "sbChesta": "Chesta",
            "sbNaisargika": "Naisargika",
            "sbDrik": "Drik",
            "karakas": "Chara Karakas",
            "scheme": "Scheme",
            "sevenKaraka": "7-Karaka (no Rahu)",
            "eightKaraka": "8-Karaka (with Rahu)",
            "karakaCol": "Karaka",
            "meaningCol": "Represents",
            "graha": "Graha",
            "sign": "Rashi",
            "ghatak": "Ghatak Chakra",
            "ghatakIntro": "Inauspicious elements for a %1 (Moon) native — avoid launching new work when they coincide.",
            "ghatMaas": "Ghat Month",
            "ghatTithi": "Ghat Tithi",
            "ghatVaar": "Ghat Day",
            "ghatNak": "Ghat Nakshatra",
            "ghatYoga": "Ghat Yoga",
            "ghatKarana": "Ghat Karana",
            "prahar": "Ghat Prahar",
            "ghatChandraM": "Ghat Chandra (male)",
            "ghatChandraF": "Ghat Chandra (female)",
            "pos": "from sign",
            "saveKundali": "Save",
            "loadKundali": "Load",
            "saveTitle": "Save Kundali",
            "savePrompt": "Profile name",
            "saved": "Saved profile '%1'.",
            "savedFail": "Save failed (%1).",
            "listTitle": "Load Kundali",
            "loadPrompt": "Saved profiles:",
            "noProfiles": "No saved profiles yet.",
            "loadFail": "Load failed (%1).",
            "delProf": "Delete",
            "loaded": "Loaded '%1'.",
            "profSummary": "%1 · %2:%3 · %4, %5 · %6"
        },
        "iast": {
            "title": "Kundalī (Janma Kuṇḍalī)",
            "compute": "Gaṇanā",
            "searchCity": "Nagara",
            "searchPlaceholder": "Nagara khojeṁ…",
            "searchBtn": "Khojeṁ",
            "manualCrd": "Athavā nirdeśāṅka",
            "actualCoords": "Janma sthāna",
            "lat": "Akṣāṁśa",
            "lon": "Reṣāṁśa",
            "alt": "Ucchtā (m)",
            "tzh": "Samaya (h)",
            "date": "Dināṅka",
            "month": "Māsa",
            "year": "Varṣa",
            "latLabel": "Akṣāṁśa",
            "lonLabel": "Reṣāṁśa",
            "altLabel": "Ucchtā (m)",
            "tzLabel": "Samaya-kṣetra (h)",
            "lagna": "Lagna:",
            "nineGrahas": "Nava Graha",
            "vargas": "Varga Kuṇḍalī",
            "vargaChart": "Varga cakra",
            "vimshottari": "Vimśottarī Daśā",
            "balance": "śeṣa",
            "ayanamsa": "Ayanāṁśa",
            "noChart": "Abhī kuṇḍalī nahīṁ.",
            "invalidDate": "Tithi DD-MM-YYYY deṁ.",
            "computing": "Gaṇanā…",
            "analysing": "Kundalī-viśleṣaṇam…",
            "parseFail": "Uttara nahīṁ milā.",
            "engineErr": "Yantra-truṭi (%1).",
            "searchErr": "Nagara khoja truṭi (%1).",
            "housePrefix": "Bhāva",
            "houseHead": "Bhāva %1 · %2",
            "sayana": "Sāyana",
            "style": "Cakra śailī",
            "north": "Uttara",
            "south": "Dakṣiṇa",
            "east": "Pūrva",
            "motion": "Gati",
            "vakri": "Vakrī",
            "maargi": "Mārgī",
            "asta": "Asta",
            "vargottam": "Vargottama",
            "dig": "Uccatā",
            "deg": "Aṁśa",
            "nakCol": "Nakṣatra",
            "rashiCol": "Rāśi #",
            "lord": "Svāmī",
            "houses": "Bhāva",
            "current": "Adya",
            "md": "Mahādaśā",
            "ad": "Antardaśā",
            "pd": "Pratyantardaśā",
            "show": "Vistāra",
            "dashaHeader": "9 mahādaśā · adya svataḥ",
            "selectVarga": "Varga",
            "digLegend": "<font color='#e67e22'><b>R</b></font> = Rāśi-anka yatra grahaḥ · <b>ᴷ</b> = Kendra (1/4/7/10) · <font color='#2ecc71'><b>V</b></font> = Vargottama (sama rāśī D1-D9) · <font color='#c0392b'><b>ᴿ</b></font>/rakta-nāma = Vakrī · <b>●</b> = Asta",
            "rTooltip": "R = Rāśi-ankaḥ: asmin grahaḥ %1-tamāyāṁ rāśau — %2. 1 = Meṣa, 12 = Mīna. Yadi Kendra (1/4/7/10) tadā ᴷ añjyate.",
            "vTooltip": "V = Vargottama: grahaḥ D1-Rāśi-aye ehate D9-Navāṁśa samāna-rāśau — balavattaraḥ.",
            "analyze": "Viśleṣaṇa",
            "analyzing": "Viśleṣaṇa…",
            "analysisYogas": "Upa-labdha yogāḥ:",
            "noYogas": "Na kaścit yogaḥ upalabdhaḥ.",
            "formation": "Prakṛti-rītiḥ:",
            "participants": "Grahāḥ:",
            "effect": "Phalam:",
            "source": "Srotaḥ:",
            "moonSign": "Candra Rāśi:",
            "nakLord": "Nakṣatra Svāmī:",
            "nameInitial": "Nāma Prāraṁbha:",
            "upapada": "Upapada Lagna",
            "shreeLagna": "Śrī Lagna",
            "induLagna": "Indu Lagna",
            "specialLagnas": "Viśeṣa Lagnāni",
            "shadbala": "Ṣaḍbala (ṣaḍ-vidha-bala)",
            "strong": "Bala-vat",
            "weak": "Durbala",
            "rupas": "Rūpas",
            "required": "Apēkṣitaṁ",
            "total": "Yogaḥ",
            "sbSthana": "Sthāna",
            "sbDig": "Dik",
            "sbKala": "Kāla",
            "sbChesta": "Ceṣṭā",
            "sbNaisargika": "Naisargika",
            "sbDrik": "Drik",
            "karakas": "Cara Kārakas",
            "scheme": "Vidhi",
            "sevenKaraka": "7-Kāraka (vina Rāhu)",
            "eightKaraka": "8-Kāraka (saha Rāhu)",
            "karakaCol": "Kāraka",
            "meaningCol": "Artha",
            "graha": "Graha",
            "sign": "Rāśi",
            "ghatak": "Ghaṭaka Cakra",
            "ghatakIntro": "Aśubha-tattvāni %1-rāśi-jātasya — ghaṭaka-saṁyoge navakarma na kuryāt.",
            "ghatMaas": "Ghaṭa Māsa",
            "ghatTithi": "Ghaṭa Tithi",
            "ghatVaar": "Ghaṭa Vāra",
            "ghatNak": "Ghaṭa Nakṣatra",
            "ghatYoga": "Ghaṭa Yoga",
            "ghatKarana": "Ghaṭa Karaṇa",
            "prahar": "Ghaṭa Prahara",
            "ghatChandraM": "Ghaṭa Candra (puruṣa)",
            "ghatChandraF": "Ghaṭa Candra (strī)",
            "pos": "rāśi-ārabhya",
            "saveKundali": "Rakṣaṇa",
            "loadKundali": "Uddhāra",
            "saveTitle": "Kuṇḍalī rakṣaṇa",
            "savePrompt": "Profile nāma",
            "saved": "'%1' rakṣitam.",
            "savedFail": "Rakṣaṇa truṭi (%1).",
            "listTitle": "Kuṇḍalī uddhāra",
            "loadPrompt": "Rakṣitā profiles:",
            "noProfiles": "Na kaścit profile rakṣitaḥ.",
            "loadFail": "Uddhāra truṭi (%1).",
            "delProf": "Nāśa",
            "loaded": "'%1' uddhṛtam.",
            "profSummary": "%1 · %2:%3 · %4, %5 · %6"
        },
        "devanagari": {
            "title": "कुंडली (जन्म कुंडली)",
            "compute": "गणना करें",
            "searchCity": "शहर",
            "searchPlaceholder": "शहर खोजें…",
            "searchBtn": "खोजें",
            "manualCrd": "या निर्देशांक भरें",
            "actualCoords": "जन्म स्थान",
            "lat": "अक्षांश",
            "lon": "रेखांश",
            "alt": "ऊँचाई (मी)",
            "tzh": "समय (घं)",
            "date": "दिनांक",
            "month": "मास",
            "year": "वर्ष",
            "latLabel": "अक्षांश",
            "lonLabel": "रेखांश",
            "altLabel": "ऊँचाई (मी)",
            "tzLabel": "समय क्षेत्र (घं)",
            "lagna": "लग्न:",
            "nineGrahas": "नव ग्रह",
            "vargas": "वर्ग कुंडलियाँ (D चार्ट)",
            "vargaChart": "वर्ग चक्र",
            "vimshottari": "विमशोत्तरी दशा",
            "balance": "शेष",
            "ayanamsa": "अयनांश",
            "noChart": "अभी कोई कुंडली गणना नहीं हुई।",
            "invalidDate": "दिनांक DD-MM-YYYY प्रारूप में दर्ज करें।",
            "computing": "गणना हो रही है…",
            "analysing": "कुंडली विश्लेषण हो रहा है…",
            "parseFail": "प्रतिक्रिया पार्स नहीं हुई।",
            "engineErr": "इंजन त्रुटि (%1)।",
            "searchErr": "शहर खोज विफल (%1)।",
            "housePrefix": "भाव",
            "houseHead": "भाव %1 · %2",
            "sayana": "सायन",
            "style": "चक्र शैली",
            "north": "उत्तर भारतीय",
            "south": "दक्षिण भारतीय",
            "east": "पूर्व भारतीय",
            "motion": "गति",
            "vakri": "वक्री",
            "maargi": "मार्गी",
            "asta": "अस्त",
            "vargottam": "वर्गोत्तम",
            "dig": "स्थिति",
            "deg": "अंश",
            "nakCol": "नक्षत्र",
            "rashiCol": "राशि #",
            "lord": "स्वामी",
            "houses": "भाव",
            "current": "वर्तमान",
            "md": "महादशा",
            "ad": "अंतर्दशा",
            "pd": "प्रत्यंतर्दशा",
            "show": "विस्तार",
            "dashaHeader": "9 महादशाएँ · वर्तमान स्वतः खुला",
            "selectVarga": "वर्ग",
            "digLegend": "<font color='#e67e22'><b>R</b></font> = ग्रह की राशि का क्रमांक · <b>ᴷ</b> = केंद्र (1/4/7/10) · <font color='#2ecc71'><b>V</b></font> = वर्गोत्तम (D1 व D9 में समान राशि) · <font color='#c0392b'><b>ᴿ</b></font>/लाल नाम = वक्री · <b>●</b> = अस्त",
            "rTooltip": "R = राशि क्रमांक: यह ग्रह %1वीं राशि में स्थित है — %2। 1 = मेष, 12 = मीन। केंद्र (1/4/7/10) होने पर ᴷ जुड़ा है।",
            "vTooltip": "V = वर्गोत्तम: यह ग्रह राशि (D1) और नवांश (D9) दोनों चार्ट में एक ही राशि में है — बलवान माना जाता है।",
            "analyze": "विश्लेषण",
            "analyzing": "विश्लेषण हो रहा है…",
            "analysisYogas": "प्राप्त योग:",
            "noYogas": "कोई संरचित योग प्राप्त नहीं हुआ।",
            "formation": "गठन:",
            "participants": "ग्रह:",
            "effect": "फल:",
            "source": "स्रोत:",
            "moonSign": "चन्द्र राशि:",
            "nakLord": "नक्षत्र स्वामी:",
            "nameInitial": "नाम प्रारंभ:",
            "upapada": "उपपद लग्न",
            "shreeLagna": "श्री लग्न",
            "induLagna": "इन्दु लग्न",
            "specialLagnas": "विशेष लग्न",
            "shadbala": "षड्बल (छह प्रकार का बल)",
            "strong": "बलवान्",
            "weak": "दुर्बल",
            "rupas": "रूप",
            "required": "अपेक्षित",
            "total": "योग",
            "sbSthana": "स्थान",
            "sbDig": "दिक्",
            "sbKala": "काल",
            "sbChesta": "चेष्टा",
            "sbNaisargika": "नैसर्गिक",
            "sbDrik": "दृष्टि",
            "karakas": "चर कारक",
            "scheme": "विधि",
            "sevenKaraka": "7-कारक (राहु रहित)",
            "eightKaraka": "8-कारक (राहु सहित)",
            "karakaCol": "कारक",
            "meaningCol": "अर्थ",
            "graha": "ग्रह",
            "sign": "राशि",
            "ghatak": "घातक चक्र",
            "ghatakIntro": "%1 (चंद्र) राशि वाले के अशुभ तत्व — इनके मिलने पर नया कार्य शुरू न करें।",
            "ghatMaas": "घात मास",
            "ghatTithi": "घात तिथि",
            "ghatVaar": "घात वार",
            "ghatNak": "घात नक्षत्र",
            "ghatYoga": "घात योग",
            "ghatKarana": "घात करण",
            "prahar": "घात प्रहर",
            "ghatChandraM": "घात चंद्र (पुरुष)",
            "ghatChandraF": "घात चंद्र (स्त्री)",
            "pos": "राशि से",
            "saveKundali": "सहेजें",
            "loadKundali": "लोड करें",
            "saveTitle": "कुंडली सहेजें",
            "savePrompt": "प्रोफ़ाइल नाम",
            "saved": "'%1' सहेज ली गई।",
            "savedFail": "सहेजने में त्रुटि (%1)।",
            "listTitle": "कुंडली लोड करें",
            "loadPrompt": "सहेजी गई प्रोफ़ाइलें:",
            "noProfiles": "अभी कोई प्रोफ़ाइल सहेजी नहीं गई।",
            "loadFail": "लोड करने में त्रुटि (%1)।",
            "delProf": "हटाएँ",
            "loaded": "'%1' लोड हो गई।",
            "profSummary": "%1 · %2:%3 · %4, %5 · %6"
        }
    })

    function langKey() {
        return (typeof plasmoid !== "undefined" && plasmoid.configuration) ? plasmoid.configuration.lang : "en";
    }

    function txt(key) {
        var table = uiTxt[langKey()] || uiTxt["en"];
        return table[key] !== undefined ? table[key] : key;
    }

    function rashiName(idx) {
        switch (langKey()) {
        case "devanagari": return rashisDev[idx];
        case "iast": return rashisIast[idx];
        default: return rashisEn[idx];
        }
    }

    function todayStr() {
        var d = new Date();
        return `${String(d.getDate()).padStart(2, '0')}-${String(d.getMonth() + 1).padStart(2, '0')}-${d.getFullYear()}`;
    }

    function parseDateStr(s) {
        var m = s.trim().match(/^(\d{2})-(\d{2})-(\d{4})$/);
        if (!m) return null;
        var d = parseInt(m[1]), mo = parseInt(m[2]), y = parseInt(m[3]);
        var dt = new Date(y, mo - 1, d);
        if (dt.getFullYear() !== y || dt.getMonth() !== mo - 1 || dt.getDate() !== d) return null;
        return [y, mo, d];
    }

    function rangeModel(a, b) {
        var arr = [];
        for (var i = a; i <= b; i++) arr.push(i);
        return arr;
    }

    function monthNames() {
        switch (langKey()) {
        case "devanagari":
            return ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"];
        default:
            return ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        }
    }

    function daysInMonth(m, y) {
        m = parseInt(m) || 1;
        y = parseInt(y) || new Date().getFullYear();
        return new Date(y, (m % 12) + 1, 0).getDate();
    }

    function commitYear() {
        if (!yearCombo) return;
        var y = parseInt(yearCombo.editText) || parseInt(yearCombo.currentValue) || new Date().getFullYear();
        y = Math.max(1800, Math.min(2100, y));
        yearCombo.currentIndex = y - 1800;
        view.clampDay();
    }

    function clampDay() {
        if (!dayCombo || dayCombo.model === undefined) return;
        var maxD = daysInMonth(monthCombo.currentIndex + 1, yearCombo.currentIndex + 1800);
        if ((parseInt(dayCombo.currentValue) || 1) > maxD) {
            dayCombo.currentIndex = maxD - 1;
        }
    }

    function selectedDate() {
        view.commitYear();
        var y = yearCombo.currentIndex + 1800;
        var m = monthCombo.currentIndex + 1;
        var d = parseInt(dayCombo.currentValue) || 1;
        d = Math.min(d, daysInMonth(m, y));
        return [y, m, d];
    }

    function selectedDateStr() {
        var p = selectedDate();
        return `${String(p[2]).padStart(2, '0')}-${String(p[1]).padStart(2, '0')}-${p[0]}`;
    }

    function cfg(key, dflt) {
        if (typeof plasmoid !== "undefined" && plasmoid.configuration) {
            var v = plasmoid.configuration[key];
            return (v === undefined || v === "") ? dflt : v;
        }
        return dflt;
    }

    function prefillCity() {
        var preset = view.cfg("locationName", "") || view.cfg("cityName", "");
        if (preset) {
            cityField.text = preset;
            return;
        }
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/config", true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                try {
                    var d = JSON.parse(xhr.responseText);
                    if (d.city && !cityField.text.trim()) cityField.text = d.city;
                } catch (e) {}
            }
        };
        xhr.send();
    }

    function searchCities() {
        var q = cityField.text.trim();
        if (!q) return;
        statusMessage.type = Kirigami.MessageType.Information;
        statusMessage.text = txt("computing");
        statusMessage.visible = true;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/search_city?q=" + encodeURIComponent(q), true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200) {
                try {
                    var list = JSON.parse(xhr.responseText) || [];
                    view.cityChoices = list;
                    cityCombo.model = list.map(function(c) { return c.name; });
                    if (list.length > 0) {
                        cityCombo.currentIndex = 0;
                        applyCityChoice(0);
                    }
                } catch (e) {
                    statusMessage.type = Kirigami.MessageType.Error;
                    statusMessage.text = txt("parseFail");
                }
                statusMessage.visible = false;
            } else {
                statusMessage.type = Kirigami.MessageType.Error;
                statusMessage.text = txt("searchErr").arg(xhr.status);
            }
        };
        xhr.send();
    }

    function applyCityChoice(i) {
        if (!cityChoices[i]) return;
        latField.text = String(Number(cityChoices[i].lat).toFixed(4));
        lonField.text = String(Number(cityChoices[i].lon).toFixed(4));
        altField.text = String(Number(cityChoices[i].alt || 0).toFixed(1));
        tzField.text = String(Number(cityChoices[i].tz || 0).toFixed(1));
    }

    function compute(afterAnalyze) {
        var lat = parseFloat(latField.text);
        var lon = parseFloat(lonField.text);
        var alt = parseFloat(altField.text);
        var tz = parseFloat(tzField.text);
        if (isNaN(lat) || isNaN(lon)) {
            statusMessage.type = Kirigami.MessageType.Error;
            statusMessage.text = txt("manualCrd");
            statusMessage.visible = true;
            return;
        }
        var q = `date=${view.selectedDateStr()}` +
                `&hour=${hourSpin.value}&minute=${minuteSpin.value}` +
                `&lat=${lat}&lon=${lon}&alt=${alt}&tz=${tz}` +
                `&lang=${encodeURIComponent(langKey())}` +
                `&ayanamsa=${ayanamsaCombo.currentValue}`;
        statusMessage.type = Kirigami.MessageType.Information;
        statusMessage.text = txt("computing");
        statusMessage.visible = true;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/kundali?" + q, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    try {
                        view.result = JSON.parse(xhr.responseText);
                        populate();
                        statusMessage.visible = false;
                        if (afterAnalyze) view.analyze();
                    } catch (e) {
                        statusMessage.type = Kirigami.MessageType.Error;
                        statusMessage.text = txt("parseFail");
                    }
                } else {
                    statusMessage.type = Kirigami.MessageType.Error;
                    statusMessage.text = view.serverErrorText(xhr) || view.txt("engineErr").arg(xhr.status);
                }
            }
        };
        xhr.send();
    }

    function serverErrorText(xhr) {
        try {
            var j = JSON.parse(xhr.responseText);
            return j.message || j.error || "";
        } catch (e) { return ""; }
    }

    // ---------- data helpers ----------

    function grahaNames() {
        switch (langKey()) {
        case "devanagari":
            return ["सूर्य", "चन्द्र", "मङ्गल", "बुध", "गुरु", "शुक्र", "शनि", "राहु", "केतु"];
        case "iast":
            return ["Sūrya", "Candra", "Maṅgala", "Budha", "Guru", "Śukra", "Śani", "Rāhu", "Ketu"];
        default:
            return ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"];
        }
    }

    function birthParams() {
        return `date=${view.selectedDateStr()}` +
                `&hour=${hourSpin.value}&minute=${minuteSpin.value}` +
                `&lat=${parseFloat(latField.text)}&lon=${parseFloat(lonField.text)}` +
                `&alt=${parseFloat(altField.text)}&tz=${parseFloat(tzField.text)}` +
                `&lang=${encodeURIComponent(langKey())}&ayanamsa=${ayanamsaCombo.currentValue}`;
    }

    function currentParamsObject() {
        return {
            date: view.selectedDateStr(),
            hour: hourSpin.value,
            minute: minuteSpin.value,
            lat: parseFloat(latField.text),
            lon: parseFloat(lonField.text),
            alt: parseFloat(altField.text),
            tz: parseFloat(tzField.text),
            lang: langKey(),
            ayanamsa: ayanamsaCombo.currentValue
        };
    }

    // ---------- saved kundali profiles ----------

    function openSaveDialog() {
        profileNameField.text = ckLastName || "";
        saveKundaliDialog.open();
    }

    property string ckLastName: ""

    function doSave(name) {
        name = String(name || "").trim();
        if (!name) return;
        view.ckLastName = name;
        var body = currentParamsObject();
        body.name = name;
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "http://127.0.0.1:8642/save_kundali", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200) {
                statusMessage.type = Kirigami.MessageType.Positive;
                statusMessage.text = txt("saved").arg(name);
                statusMessage.visible = true;
                view.refreshProfiles();
            } else {
                statusMessage.type = Kirigami.MessageType.Error;
                statusMessage.text = txt("savedFail").arg(xhr.status);
            }
        };
        xhr.send(JSON.stringify(body));
    }

    function refreshProfiles() {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/list_kundalis", true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200) {
                try {
                    view.savedProfiles = JSON.parse(xhr.responseText).profiles || [];
                } catch (e) {
                    view.savedProfiles = [];
                }
            } else {
                view.savedProfiles = [];
            }
        };
        xhr.send();
    }

    function openLoadDialog() {
        view.refreshProfiles();
        loadKundaliDialog.open();
    }

    function profileSummary(p) {
        var params = p.params || {};
        var date = String(params.date || "");
        var hh = String(Number(params.hour) || 0);
        var mm = String(Number(params.minute) || 0).padStart(2, "0");
        var lat = Number(params.lat) || 0;
        var lon = Number(params.lon) || 0;
        var ay = String(params.ayanamsa || "lahiri");
        return txt("profSummary").arg(date, hh, mm, lat.toFixed(2), lon.toFixed(2), ay);
    }

    function loadProfile(id) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/load_kundali?id=" + encodeURIComponent(id), true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200) {
                var prof = null;
                try {
                    prof = JSON.parse(xhr.responseText).profile;
                } catch (e) { prof = null; }
                if (prof) {
                    view.applyProfile(prof);
                    loadKundaliDialog.close();
                    return;
                }
            }
            statusMessage.type = Kirigami.MessageType.Error;
            statusMessage.text = txt("loadFail").arg(xhr.status);
        };
        xhr.send();
    }

    function deleteProfile(id) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "http://127.0.0.1:8642/delete_kundali?id=" + encodeURIComponent(id), true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) view.refreshProfiles();
        };
        xhr.send();
    }

    function applyProfile(prof) {
        var p = prof.params || {};
        var d = view.parseDateStr(String(p.date || ""));
        if (d) {
            yearCombo.currentIndex = d[0] - 1800;
            monthCombo.currentIndex = d[1] - 1;
            dayCombo.currentIndex = d[2] - 1;
            view.clampDay();
        }
        hourSpin.value = Math.max(0, Math.min(23, Number(p.hour) || 0));
        minuteSpin.value = Math.max(0, Math.min(59, Number(p.minute) || 0));
        latField.text = String(Number(p.lat) || "");
        lonField.text = String(Number(p.lon) || "");
        altField.text = String(Number(p.alt) || "0");
        tzField.text = String(Number(p.tz) || "5.5");
        var ai = ayanamsaCombo.indexOfValue(String(p.ayanamsa || "lahiri"));
        ayanamsaCombo.currentIndex = ai >= 0 ? ai : ayanamsaCombo.currentIndex;
        statusMessage.type = Kirigami.MessageType.Positive;
        statusMessage.text = txt("loaded").arg(prof.name);
        statusMessage.visible = true;
        view.compute();
    }

    function fetchAnalysis(path, onOk) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642" + path + "?" + view.birthParams(), true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200) {
                try { onOk(JSON.parse(xhr.responseText)); return; } catch (e) {}
            }
            view.analysisError = txt("engineErr").arg(xhr.status);
            view.analysisBusy = false;
            statusMessage.type = Kirigami.MessageType.Error;
            statusMessage.text = view.analysisError;
            statusMessage.visible = true;
        };
        xhr.send();
    }

    function analyze() {
        if (!view.result) {
            view.compute(true);
            return;
        }
        view.analysisModel = null;
        view.analysisError = "";
        view.analysisBusy = true;
        view._analysisBodha = null;
        view._analysisMedha = null;
        statusMessage.type = Kirigami.MessageType.Information;
        statusMessage.text = txt("analysing");
        statusMessage.visible = true;
        analysisTimer.start();
        fetchAnalysis("/bodha", function(b) {
            view._analysisBodha = b;
            view.reportAnalysis();
            fetchAnalysis("/medha", function(m) {
                view._analysisMedha = m;
                view.reportAnalysis();
            });
        });
    }

    function reveal(obj) {
        if (!obj) return;
        var flick = resultsScroller.contentItem;
        var p = flick.mapFromItem(obj, 0, 0);
        flick.contentY = Math.max(0, p.y - 8);
    }

    function strengthText(s) {
        s = Math.max(0, parseInt(s) || 0);
        var out = "";
        for (var i = 0; i < s; i++) out += "●";
        return out;
    }

    function reportAnalysis() {
        var model = { lagna: "", dasha: "", yogas: [] };
        var b = view._analysisBodha;
        var m = view._analysisMedha;
        if (b && b.bodha) {
            var bo = b.bodha;
            if (bo.lagna && bo.lagna.rashi_name)
                model.lagna = bo.lagna.rashi_name + (bo.lagna.lagnesh ? " (" + bo.lagna.lagnesh + ")" : "");
            var cd = bo.current_dasha || {};
            if (cd.mahadasha || cd.antardasha || cd.pratyantardasha) {
                var d = [];
                if (cd.mahadasha) d.push(cd.mahadasha);
                if (cd.antardasha) d.push(cd.antardasha);
                if (cd.pratyantardasha) d.push(cd.pratyantardasha);
                model.dasha = d.join(" / ");
            }
            var names = view.grahaNames();
            model.yogas = (bo.yogas || []).map(function(y) {
                return {
                    name: y.name || "?",
                    strength: y.strength || 0,
                    condition: y.condition || "",
                    participants: (y.participants || []).map(function(ix) {
                        return names[ix] !== undefined ? names[ix] : String(ix);
                    }).join(", "),
                    interpretation: y.interpretation || "",
                    source: y.source || ""
                };
            });
        }
        if (m && m.medha) {
            var narr = m.medha.narrative || {};
            if (narr.lagna) model.lagna = narr.lagna;
            if (narr.dasha) model.dasha = narr.dasha;
        }
        view.analysisModel = model;
        view.analysisBusy = false;
        statusMessage.visible = false;
        view.reveal(analysisSection);
    }

    // ---------- data helpers ----------

    function planetArray() {
        var arr = [];
        var r = view.result;
        if (!r || !r.planets) return arr;
        for (var p in r.planets) {
            var obj = r.planets[p];
            arr[obj.idx] = obj;
        }
        return arr;
    }

    function dignityColor(code) {
        if (!code) return "#bdc3c7";
        switch (String(code).toLowerCase()) {
        case "exalted": return "#2ecc71";
        case "moolatrikona": return "#2cd9a0";
        case "own": case "own sign": return "#27ae60";
        case "debilitated": return "#e74c3c";
        case "friend": case "friendly sign": return "#3498db";
        case "neutral": case "neutral sign": return "#95a5a6";
        case "enemy": case "enemy sign": return "#e67e22";
        default: return "#bdc3c7";
        }
    }

    function formatDeg(d) {
        if (d === undefined || d === null || isNaN(d)) return "--";
        var deg = Math.floor(d);
        var mn = Math.round((d - deg) * 60);
        if (mn === 60) { mn = 0; deg += 1; }
        return `${deg}\u00B0${String(mn).padStart(2, '0')}\u2032`;
    }

    function makeChartData(chartKey) {
        var bars = planetArray();
        var signs = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1];
        var markers = [];
        var colors = [];
        var v = view.result.vargas[chartKey];
        if (chartKey === "D1") {
            for (var i = 0; i < 13; i++) {
                if (bars[i]) {
                    signs[i] = bars[i].rashi;
                    markers[i] = { retro: bars[i].retrograde, combust: bars[i].combust };
                    colors[i] = dignityColor(bars[i].dignity_code);
                }
            }
            return { signs: signs, markers: markers, colors: colors };
        }
        for (var j = 0; j < 13; j++) {
            if (bars[j]) {
                var ve = v.planets[bars[j].name];
                signs[j] = ve ? ve.rashi : -1;
                markers[j] = { retro: bars[j].retrograde, combust: bars[j].combust };
                colors[j] = dignityColor(bars[j].dignity_code);
            }
        }
        return { signs: signs, markers: markers, colors: colors };
    }

    function updateMainChart() {
        if (!view.result) return;
        var d = makeChartData("D1");
        mainChart.signs = d.signs;
        mainChart.markers = d.markers;
        mainChart.colors = d.colors;
        mainChart.ascRashi = view.result.lagna.rashi;
        mainChart.style = chartStyleCombo.currentValue || "north";
        mainChart.langKey = langKey();
    }

    function updateVargaChart() {
        if (!view.result) return;
        var key = vargaMenu.currentValue || "D1";
        var d = makeChartData(key);
        vargaChart.signs = d.signs;
        vargaChart.markers = d.markers;
        vargaChart.colors = d.colors;
        vargaChart.ascRashi = view.result.vargas[key].lagna.rashi;
        vargaChart.style = mainChart.style;
        vargaChart.langKey = langKey();
        vargaTitleText.text = vargaLabelFor(key) + " — " + rashiName(view.result.vargas[key].lagna.rashi);
        buildVargaPlacements(key);
    }

    function vargaLabelFor(key) {
        var dev = { "D1": "राशि", "D2": "होरा", "D3": "द्रेष्काण", "D4": "तुर्यांश", "D7": "सप्तांश", "D9": "नवांश", "D10": "दशांश", "D12": "द्वादशांश", "D16": "षोडशांश", "D20": "विंशांश", "D24": "चतुर्विंशांश", "D27": "सप्तविंशांश", "D30": "त्रिंशांश", "D40": "खवेदांश", "D45": "अक्षवेदांश", "D60": "षष्ट्यांश" };
        var en = key;
        if (langKey() === "devanagari") return `${key} · ${dev[key] || ""}`.trim();
        return key;
    }

    function buildVargaPlacements(key) {
        var bars = planetArray();
        var v = view.result.vargas[key];
        var rows = [];
        for (var i = 0; i < 13; i++) {
            if (!bars[i]) continue;
            var ve = v.planets[bars[i].name];
            rows.push({
                name: bars[i].name,
                sign: rashiName(ve ? ve.rashi : -1),
                deg: formatDeg(ve ? ve.degree : null)
            });
        }
        view.vargaPlacements = rows;
    }

    function populate() {
        var r = view.result;
        if (!r || !r.lagna) return;

        var bars = planetArray();
        var rows = [];
        for (var i = 0; i < 13; i++) {
            var p = bars[i];
            if (!p) continue;
            rows.push({
                name: p.name,
                degree: formatDeg(p.degree_in_sign),
                sign: p.rashi_name,
                nak: p.nakshatra_name + " " + p.nakshatra_pada,
                house: p.house,
                rashiNum: (p.rashi !== undefined && p.rashi !== null) ? p.rashi + 1 : (((r.lagna ? r.lagna.rashi : 0) + p.house - 1) % 12) + 1,
                dignity: p.dignity || "",
                digColor: dignityColor(p.dignity_code),
                retro: p.retrograde,
                combust: p.combust,
                vargottam: p.is_vargottam,
                kendra: (p.house === 1 || p.house === 4 || p.house === 7 || p.house === 10)
            });
        }
        view.planetRows = rows;

        var srows = [];
        if (r.shadbala && r.shadbala.planets) {
            var sp = r.shadbala.planets;
            var order = view.grahaNames();
            for (var so = 0; so < order.length; so++) {
                var ss = sp[order[so]];
                if (!ss) continue;
                var strong = (ss.minimum_rupas === null || ss.minimum_rupas === undefined) ? false : ss.rupas >= ss.minimum_rupas;
                srows.push({
                    name: ss.name,
                    sthana: ss.sthana.total,
                    dig: ss.dig,
                    kala: ss.kala.total,
                    chesta: ss.chesta,
                    naisargika: ss.naisargika,
                    drik: ss.drik,
                    total: ss.total,
                    rupas: ss.rupas,
                    minr: (ss.minimum_rupas === null || ss.minimum_rupas === undefined) ? "--" : ss.minimum_rupas,
                    strong: strong
                });
            }
        }
        view.shadbalaTable = srows;

        var houses = r.houses || {};
        var hrows = [];
        for (var h = 1; h <= 12; h++) {
            hrows.push({ num: h, signNum: ((r.lagna.rashi + h - 1) % 12) + 1, name: houses[h] ? houses[h].rashi_name : "--", lord: houses[h] ? houses[h].lord : "--" });
        }
        view.houseRows = hrows;

        view.rebuildKarakas();

        var gr = [];
        if (r.ghatak) {
            var g = r.ghatak;
            gr.push({ key: view.txt("ghatMaas"), value: g.ghat_maas });
            gr.push({ key: view.txt("ghatTithi"), value: g.ghat_tithis.join(", ") + (g.ghat_tithis_full.length ? "  ·  " + g.ghat_tithis_full.join(", ") : "") });
            gr.push({ key: view.txt("ghatVaar"), value: g.ghat_vaara });
            gr.push({ key: view.txt("ghatNak"), value: g.ghat_nakshatra });
            gr.push({ key: view.txt("ghatYoga"), value: g.ghat_yoga });
            gr.push({ key: view.txt("ghatKarana"), value: g.ghat_karana });
            gr.push({ key: view.txt("prahar"), value: (g.prahar !== undefined && g.prahar !== null) ? String(g.prahar) : "--" });
            gr.push({ key: view.txt("ghatChandraM"), value: g.ghat_chandra_male.rashi + " (" + view.txt("pos") + " " + g.ghat_chandra_male.position + ")" });
            gr.push({ key: view.txt("ghatChandraF"), value: g.ghat_chandra_female.rashi + " (" + view.txt("pos") + " " + g.ghat_chandra_female.position + ")" });
        }
        view.ghatakRows = gr;

        updateMainChart();

        var keys = view.vargaKeys;
        if (vargaMenu.count === 0) {
            var model = [];
            for (var k = 0; k < keys.length; k++) model.push(keys[k]);
            vargaMenu.model = model;
            vargaMenu.currentIndex = 0;
        }
        var d9 = vargaMenu.find("D9");
        vargaMenu.currentIndex = d9 >= 0 ? d9 : 0;
        updateVargaChart();

        // Expand the currently running dasha periods.
        var das = r.dashas;
        view.autoAdFocus = true;
        if (das && das.mahadashas) {
            for (var m = 0; m < das.mahadashas.length; m++) {
                if (das.mahadashas[m].is_current) {
                    view.expandedMd = m;
                    for (var a = 0; a < das.mahadashas[m].antardashas.length; a++) {
                        if (das.mahadashas[m].antardashas[a].is_current) {
                            view.expandedAd = a;
                            break;
                        }
                    }
                    break;
                }
            }
        }
    }

    function rebuildKarakas() {
        view.karakaRows = [];
        view.karakaCells = [];
        if (!view.result || !view.result.karakas) return;
        var range = (view.karakaScheme === 7) ? view.result.karakas.seven : view.result.karakas.eight;
        if (!range) return;
        var rows = [];
        var cells = [];
        for (var i = 0; i < range.length; i++) {
            var k = range[i];
            var planet = k.planet + (k.retrograde ? " ᴿ" : "") + (k.via_rahu ? " ◂" : "");
            rows.push({
                rank: k.rank,
                karaka: k.karaka,
                meaning: k.meaning || "",
                planet: planet,
                deg: formatDeg(k.degree_in_sign),
                sign: k.rashi_name,
                house: k.house
            });
            var r = i + 1;
            var band = (k.rank === 1 || k.rank === range.length);
            cells.push({ row: r, col: 0, text: planet, fill: true, bold: false, wrap: false, small: false, band: band });
            cells.push({ row: r, col: 1, text: view.formatDeg(k.degree_in_sign), fill: false, bold: false, wrap: false, small: false, band: false });
            cells.push({ row: r, col: 2, text: k.karaka, fill: true, bold: true, wrap: false, small: false, band: band });
            cells.push({ row: r, col: 3, text: k.meaning || "", fill: true, bold: false, wrap: true, small: true, band: false });
        }
        view.karakaRows = rows;
        view.karakaCells = cells;
    }

    function dashaSummary() {
        if (!view.result || !view.result.dashas) return "";
        var d = view.result.dashas;
        return `${view.txt("vimshottari")} — ${view.txt("balance")} ${view.fmtYears(d.balance_years)} · ${d.start_lord} ${view.fmtYears(d.balance_years)} — ${d.mahadashas[d.mahadashas.length - 1].end_date}`;
    }

    function fmtYears(y) {
        var v = Number(y);
        if (isNaN(v)) return "--";
        var years = Math.floor(v + 1e-9);
        var frac = v - years;
        var months = Math.floor(frac * 12 + 1e-9);
        var days = Math.round((frac * 12 - months) * (365.2425 / 12));
        var parts = [];
        if (years > 0) parts.push(years + "y");
        if (months > 0) parts.push(months + "m");
        if (days > 0) parts.push(days + "d");
        return parts.length ? parts.join(" ") : "0y";
    }

    function currentDashaText() {
        if (!view.result || !view.result.dashas || !view.result.dashas.mahadashas) return "";
        var list = view.result.dashas.mahadashas;
        for (var i = 0; i < list.length; i++) {
            if (list[i].is_current) return `● ${list[i].lord} · ${list[i].end_date}`;
        }
        return "";
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing

        Kirigami.Heading {
            text: view.txt("title")
            level: 4
        }

        // Birth date: Date / Month / Year dropdowns with invalid-date fallback
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4

            RowLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing

                ColumnLayout {
                    Layout.fillWidth: true
spacing: 4
            Label {
                text: view.txt("date")
                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                        opacity: 0.7
                    }
                    ComboBox {
                        id: dayCombo
                        Layout.fillWidth: true
                        model: view.rangeModel(1, 31)
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    Label {
                        text: view.txt("month")
                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                        opacity: 0.7
                    }
                    ComboBox {
                        id: monthCombo
                        Layout.fillWidth: true
                        model: view.monthNames()
                        onActivated: view.clampDay()
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    Label {
                        text: view.txt("year")
                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                        opacity: 0.7
                    }
                    ComboBox {
                        id: yearCombo
                        Layout.fillWidth: true
                        editable: true
                        model: view.rangeModel(1800, 2100)
                        onActivated: view.clampDay()
                        onAccepted: view.commitYear()
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing

                SpinBox {
                    id: hourSpin
                    from: 0
                    to: 23
                    value: 10
                    editable: true
                    textFromValue: function(v) { return v + i18n("h"); }
                    valueFromText: function(t) { return Math.max(0, Math.min(23, parseInt(t) || 0)); }
                }

                SpinBox {
                    id: minuteSpin
                    from: 0
                    to: 59
                    value: 30
                    editable: true
                    textFromValue: function(v) { return v + i18n("m"); }
                    valueFromText: function(t) { return Math.max(0, Math.min(59, parseInt(t) || 0)); }
                }

                Item { Layout.fillWidth: true }

                Button {
                    text: view.txt("compute")
                    icon.name: "view-refresh"
                    onClicked: view.compute()
                }

                Button {
                    text: view.txt("analyze")
                    icon.name: "tools-wizard"
                    enabled: view.result !== null
                    onClicked: view.requestAnalysis()
                }

                Button {
                    text: view.txt("saveKundali")
                    icon.name: "document-save"
                    onClicked: view.openSaveDialog()
                }

                Button {
                    text: view.txt("loadKundali")
                    icon.name: "document-open"
                    onClicked: view.openLoadDialog()
                }
            }

            Component.onCompleted: {
                var t = new Date();
                dayCombo.currentIndex = Math.max(0, Math.min(30, t.getDate() - 1));
                monthCombo.currentIndex = Math.max(0, Math.min(11, t.getMonth()));
                yearCombo.currentIndex = t.getFullYear() - 1800;
            }
        }

        // Birth location: city search (primary) + manual coordinates
        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            TextField {
                id: cityField
                Layout.fillWidth: true
                placeholderText: view.txt("searchPlaceholder")
                onAccepted: view.searchCities()
            }
            Button {
                text: view.txt("searchBtn")
                icon.name: "edit-find"
                onClicked: view.searchCities()
            }
            ComboBox {
                id: cityCombo
                Layout.preferredWidth: Kirigami.Units.gridUnit * 9
                onActivated: view.applyCityChoice(currentIndex)
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                Label {
                    text: view.txt("latLabel")
                    font.pixelSize: Kirigami.Units.gridUnit * 0.7
                    opacity: 0.7
                }
                TextField {
                    id: latField
                    placeholderText: view.txt("lat")
                    text: String(Number(view.cfg("latitude", 23.1765)).toFixed(4))
                    Layout.fillWidth: true
                    validator: DoubleValidator { bottom: -90; top: 90; decimals: 4 }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                Label {
                    text: view.txt("lonLabel")
                    font.pixelSize: Kirigami.Units.gridUnit * 0.7
                    opacity: 0.7
                }
                TextField {
                    id: lonField
                    placeholderText: view.txt("lon")
                    text: String(Number(view.cfg("longitude", 75.7885)).toFixed(4))
                    Layout.fillWidth: true
                    validator: DoubleValidator { bottom: -180; top: 180; decimals: 4 }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                Label {
                    text: view.txt("altLabel")
                    font.pixelSize: Kirigami.Units.gridUnit * 0.7
                    opacity: 0.7
                }
                TextField {
                    id: altField
                    placeholderText: view.txt("alt")
                    text: String(Number(view.cfg("altitude", 0)).toFixed(1))
                    Layout.fillWidth: true
                    validator: DoubleValidator { bottom: -500; top: 9000; decimals: 1 }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                Label {
                    text: view.txt("tzLabel")
                    font.pixelSize: Kirigami.Units.gridUnit * 0.7
                    opacity: 0.7
                }
                TextField {
                    id: tzField
                    placeholderText: view.txt("tzh")
                    text: String(Number(view.cfg("timezone", 5.5)).toFixed(1))
                    Layout.fillWidth: true
                    validator: DoubleValidator { bottom: -12; top: 14; decimals: 2 }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            ComboBox {
                id: ayanamsaCombo
                Layout.fillWidth: true
                textRole: "text"
                valueRole: "value"
                model: [
                    { "text": view.txt("sayana"), "value": "sayana" },
                    { "text": "Lahiri (Chitrapaksha)", "value": "lahiri" },
                    { "text": "Raman", "value": "raman" },
                    { "text": "Krishnamurti (KP)", "value": "krishnamurti" },
                    { "text": "True Chitra", "value": "true_citra" },
                    { "text": "Fagan/Bradley", "value": "fagan_bradley" },
                    { "text": "DeLuce", "value": "deluce" }
                ]
                Component.onCompleted: {
                    var idx = indexOfValue(view.cfg("ayanamsa", "lahiri"));
                    currentIndex = idx >= 0 ? idx : 0;
                }
            }

            ComboBox {
                id: chartStyleCombo
                Layout.fillWidth: true
                textRole: "text"
                valueRole: "value"
                model: [
                    { "text": view.txt("north"), "value": "north" },
                    { "text": view.txt("south"), "value": "south" },
                    { "text": view.txt("east"), "value": "east" }
                ]
                Component.onCompleted: currentIndex = 0
                onActivated: {
                    if (view.result) { view.updateMainChart(); view.updateVargaChart(); }
                }
            }
        }

        Kirigami.InlineMessage {
            id: statusMessage
            Layout.fillWidth: true
            type: Kirigami.MessageType.Warning
            text: ""
            visible: false
        }

        ScrollView {
            id: resultsScroller
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            ColumnLayout {
                width: parent.width
                spacing: Kirigami.Units.largeSpacing * 1.4
                Layout.topMargin: Kirigami.Units.largeSpacing
                Layout.bottomMargin: Kirigami.Units.largeSpacing

                // Meta
                Label {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    text: view.result ? `${view.result.meta.chart_type} • ${view.txt("ayanamsa")} ${view.result.meta.ayanamsa_value.toFixed(5)}\u00B0 • ${view.result.meta.date}` : view.txt("noChart")
                    opacity: 0.8
                }

                Label {
                    Layout.fillWidth: true
                    Layout.topMargin: 4
                    text: view.result ? `${view.txt("lagna")} <b>${view.result.lagna.rashi_name}</b> — ${view.result.lagna.nakshatra_name} ${view.result.lagna.nakshatra_pada} (${view.result.lagna.longitude.toFixed(2)}\u00B0) · ${view.txt("lord")}: ${view.result.lagna.lord}` : ""
                    textFormat: Text.RichText
                    font.pixelSize: Kirigami.Units.gridUnit * 0.85
                }

                Label {
                    Layout.fillWidth: true
                    Layout.topMargin: 2
                    visible: view.result && view.result.moon
                    text: (view.result && view.result.moon)
                          ? `${view.txt("moonSign")} <b>${view.result.moon.rashi_name}</b> (${view.result.moon.rashi_adhipati}) · ${view.txt("nakLord")} ${view.result.moon.nakshatra_name} ${view.result.moon.nakshatra_pada} (${view.result.moon.nakshatra_adhipati}) · ${view.txt("nameInitial")} <b>${view.result.moon.nakshatra_initial}</b>`
                          : ""
                    textFormat: Text.RichText
                    font.pixelSize: Kirigami.Units.gridUnit * 0.85
                }

                Label {
                    Layout.fillWidth: true
                    Layout.topMargin: 4
                    visible: view.result && view.result.special_lagnas
                    text: (view.result && view.result.special_lagnas)
                          ? `<b>${view.txt("specialLagnas")}</b>  ·  ${view.txt("upapada")}: <b>${view.result.special_lagnas.upapada.rashi_name}</b>  ·  ${view.txt("shreeLagna")}: <b>${view.result.special_lagnas.shree.rashi_name}</b>  ·  ${view.txt("induLagna")}: <b>${view.result.special_lagnas.indu.rashi_name}</b>`
                          : ""
                    textFormat: Text.RichText
                    font.pixelSize: Kirigami.Units.gridUnit * 0.85
                    opacity: 0.95
                }

                // Pictorial chart
                Rectangle {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredHeight: Math.max(320, mainChart.height + 12)
                    radius: 8
                    color: Qt.rgba(0, 0, 0, 0.15)
                    visible: view.result !== null
                    border.color: Qt.rgba(0.55, 0.55, 0.55, 0.4)
                    border.width: 1

                    KundaliChart {
                        id: mainChart
                        anchors.centerIn: parent
                        width: Math.min(640, parent.width - 16)
                        height: width
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.result !== null }

                // Analyse
                ColumnLayout {
                    id: analysisSection
                    Layout.fillWidth: true
                    Layout.topMargin: Kirigami.Units.largeSpacing
                    spacing: 6
                    visible: view.result !== null

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        Label { text: view.txt("analyze"); font.bold: true; color: Kirigami.Theme.highlightColor }
                        Item { Layout.fillWidth: true }
                        BusyIndicator {
                            Layout.preferredWidth: Kirigami.Units.gridUnit * 2
                            Layout.preferredHeight: Kirigami.Units.gridUnit * 2
                            running: view.analysisBusy
                            visible: running
                            opacity: 0.7
                        }
                    }

                    Kirigami.InlineMessage {
                        Layout.fillWidth: true
                        visible: view.analysisError !== ""
                        type: Kirigami.MessageType.Error
                        text: view.analysisError
                    }

                    Label {
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        visible: view.analysisModel !== null && view.analysisModel.lagna !== ""
                        text: view.analysisModel !== null && view.analysisModel.lagna !== ""
                              ? `${view.txt("lagna")} <b>${view.analysisModel.lagna}</b>` : ""
                        textFormat: Text.RichText
                    }

                    Label {
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        visible: view.analysisModel !== null && view.analysisModel.dasha !== ""
                        text: view.analysisModel !== null && view.analysisModel.dasha !== ""
                              ? `${view.txt("current")} ${view.analysisModel.dasha}` : ""
                        font.pixelSize: Kirigami.Units.gridUnit * 0.8
                        opacity: 0.9
                    }

                    Repeater {
                        model: view.analysisModel !== null ? view.analysisModel.yogas : []

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            Layout.topMargin: 6

                            Label {
                                Layout.fillWidth: true
                                text: `<b>${modelData.name}</b>  ${view.strengthText(modelData.strength)}`
                                textFormat: Text.RichText
                                color: Kirigami.Theme.highlightColor
                                font.bold: true
                            }
                            Label {
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                visible: modelData.condition !== ""
                                text: `<b>${view.txt("formation")}</b> ${modelData.condition}`
                                textFormat: Text.RichText
                                font.pixelSize: Kirigami.Units.gridUnit * 0.8
                            }
                            Label {
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                visible: modelData.participants !== ""
                                text: `<b>${view.txt("participants")}</b> ${modelData.participants}`
                                textFormat: Text.RichText
                                font.pixelSize: Kirigami.Units.gridUnit * 0.8
                            }
                            Label {
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                visible: modelData.interpretation !== ""
                                text: `<b>${view.txt("effect")}</b> ${modelData.interpretation}`
                                textFormat: Text.RichText
                                font.pixelSize: Kirigami.Units.gridUnit * 0.8
                            }
                            Label {
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                                visible: modelData.source !== ""
                                text: `${view.txt("source")} ${modelData.source}`
                                opacity: 0.6
                                font.pixelSize: Kirigami.Units.gridUnit * 0.7
                            }
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        visible: view.analysisModel !== null && view.analysisModel.yogas.length === 0 && view.analysisError === ""
                        opacity: 0.7
                        text: view.txt("noYogas")
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.planetRows && view.planetRows.length > 0 }

                // Planets
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: Kirigami.Units.largeSpacing
                    spacing: 4
                    visible: view.planetRows && view.planetRows.length > 0

                    Label { text: view.txt("nineGrahas"); font.bold: true }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        Label { text: view.txt("graha"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: view.grahaSpan.nm }
                        Label { text: view.txt("deg"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: view.grahaSpan.deg }
                        Label { text: view.txt("sign"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: view.grahaSpan.sign }
                        Label { text: view.txt("dig"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: view.grahaSpan.dig; elide: Text.ElideRight; ToolTip.text: view.txt("dig"); ToolTip.visible: false }
                        Label { text: view.txt("nakCol"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.fillWidth: true; elide: Text.ElideRight; ToolTip.text: view.txt("nakCol"); ToolTip.visible: false }
                        Label { text: view.txt("motion"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: view.grahaSpan.motion; elide: Text.ElideRight }
                        Label { text: view.txt("asta"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: view.grahaSpan.asta; elide: Text.ElideRight }
                        Label { text: view.txt("vargottam"); font.bold: true; color: "#2ecc71"; font.pixelSize: Kirigami.Units.gridUnit * 0.55; Layout.preferredWidth: view.grahaSpan.v; elide: Text.ElideRight; ToolTip.text: view.txt("vTooltip"); ToolTip.visible: false }
                        Label { text: view.txt("rashiCol"); font.bold: true; color: "#e67e22"; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: view.grahaSpan.r; elide: Text.ElideRight; ToolTip.text: view.txt("rTooltip").replace("%1", "?").replace("%2", "…"); ToolTip.visible: false }
                    }

                    Repeater {
                        model: view.planetRows

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Label {
                                text: modelData.name
                                font.bold: true
                                font.pixelSize: Kirigami.Units.gridUnit * 0.95
                                Layout.preferredWidth: view.grahaSpan.nm
                                color: modelData.digColor
                                elide: Text.ElideRight
                                ToolTip.text: modelData.name
                                HoverHandler { id: tName }
                                ToolTip.visible: truncated && tName.hovered
                            }
                            Label {
                                text: modelData.degree
                                font.pixelSize: Kirigami.Units.gridUnit * 0.9
                                Layout.preferredWidth: view.grahaSpan.deg
                                opacity: 0.9
                            }
                            Label {
                                text: modelData.sign
                                font.pixelSize: Kirigami.Units.gridUnit * 0.9
                                Layout.preferredWidth: view.grahaSpan.sign
                                elide: Text.ElideRight
                                ToolTip.text: modelData.sign
                                HoverHandler { id: tSign }
                                ToolTip.visible: truncated && tSign.hovered
                            }
                            Label {
                                text: modelData.dignity
                                color: modelData.digColor
                                font.bold: true
                                font.pixelSize: Kirigami.Units.gridUnit * 0.85
                                elide: Text.ElideRight
                                Layout.preferredWidth: view.grahaSpan.dig
                                ToolTip.text: modelData.dignity
                                HoverHandler { id: tDig }
                                ToolTip.visible: truncated && tDig.hovered
                            }
                            Label {
                                text: modelData.nak
                                opacity: 0.8
                                fontSizeMode: Text.HorizontalFit
                                Layout.fillWidth: true
                                ToolTip.text: modelData.nak
                                HoverHandler { id: tNak }
                                ToolTip.visible: truncated && tNak.hovered
                            }
                            Label {
                                text: modelData.retro ? `${view.txt("vakri")}` : view.txt("maargi")
                                color: modelData.retro ? "#e74c3c" : "#2ecc71"
                                font.bold: true
                                font.pixelSize: Kirigami.Units.gridUnit * 0.85
                                Layout.preferredWidth: view.grahaSpan.motion
                                elide: Text.ElideRight
                                ToolTip.text: modelData.retro ? view.txt("vakri") : view.txt("maargi")
                                HoverHandler { id: tMot }
                                ToolTip.visible: truncated && tMot.hovered
                            }
                            Label {
                                text: modelData.combust ? view.txt("asta") : ""
                                color: "#e67e22"
                                font.bold: true
                                font.pixelSize: Kirigami.Units.gridUnit * 0.85
                                Layout.preferredWidth: view.grahaSpan.asta
                                elide: Text.ElideRight
                            }
                            Rectangle {
                                Layout.alignment: Qt.AlignVCenter
                                Layout.preferredWidth: view.grahaSpan.v
                                Layout.preferredHeight: Math.max(Kirigami.Units.gridUnit * 1.6, 14)
                                radius: 5
                                color: modelData.vargottam ? "#2ecc71" : "transparent"
                                Label {
                                    anchors.centerIn: parent
                                    text: "V"
                                    visible: modelData.vargottam
                                    color: "#0b1210"
                                    font.bold: true
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.85
                                }
                                HoverHandler { id: tV }
                                ToolTip.visible: modelData.vargottam && tV.hovered
                                ToolTip.text: view.txt("vTooltip")
                            }
                            Rectangle {
                                Layout.alignment: Qt.AlignVCenter
                                Layout.preferredWidth: view.grahaSpan.r
                                Layout.preferredHeight: Math.max(Kirigami.Units.gridUnit * 1.6, 14)
                                radius: 5
                                color: modelData.kendra ? Qt.rgba(0.9, 0.6, 0.1, 0.30) : Qt.rgba(0.6, 0.6, 0.7, 0.16)
                                Label {
                                    anchors.centerIn: parent
                                    text: "R" + modelData.rashiNum + (modelData.kendra ? "ᴷ" : "")
                                    color: modelData.kendra ? "#f5a623" : Kirigami.Theme.textColor
                                    font.bold: modelData.kendra
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.8
                                }
                                HoverHandler { id: tR }
                                ToolTip.visible: tR.hovered
                                ToolTip.text: view.txt("rTooltip")
                                        .replace("%1", String(modelData.rashiNum))
                                        .replace("%2", view.rashiName(modelData.rashiNum - 1))
                            }
                        }
                    }

                    Label {
                        text: view.txt("digLegend")
                        textFormat: Text.RichText
                        opacity: 0.7
                        font.pixelSize: Kirigami.Units.gridUnit * 0.8
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        color: Kirigami.Theme.textColor
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.shadbalaTable && view.shadbalaTable.length > 0 }

                // Shadbala
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: Kirigami.Units.largeSpacing
                    spacing: 4
                    visible: view.shadbalaTable && view.shadbalaTable.length > 0

                    Label {
                        text: view.txt("shadbala")
                        font.bold: true
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        Label { text: view.txt("graha"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: 84 }
                        Label { text: view.txt("sbSthana"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: 46; horizontalAlignment: Text.AlignRight }
                        Label { text: view.txt("sbDig"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: 42; horizontalAlignment: Text.AlignRight }
                        Label { text: view.txt("sbKala"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: 46; horizontalAlignment: Text.AlignRight }
                        Label { text: view.txt("sbChesta"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: 42; horizontalAlignment: Text.AlignRight }
                        Label { text: view.txt("sbNaisargika"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: 52; horizontalAlignment: Text.AlignRight }
                        Label { text: view.txt("sbDrik"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: 42; horizontalAlignment: Text.AlignRight }
                        Label { text: view.txt("total"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: 58; horizontalAlignment: Text.AlignRight }
                        Label { text: view.txt("rupas"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: 44; horizontalAlignment: Text.AlignRight }
                        Label { text: view.txt("required"); font.bold: true; opacity: 0.7; font.pixelSize: Kirigami.Units.gridUnit * 0.6; Layout.preferredWidth: 46; horizontalAlignment: Text.AlignRight }
                        Label { text: ""; Layout.fillWidth: true }
                    }

                    Repeater {
                        model: view.shadbalaTable

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Label { text: modelData.name; font.bold: true; font.pixelSize: Kirigami.Units.gridUnit * 0.9; Layout.preferredWidth: 84; elide: Text.ElideRight }
                            Label { text: modelData.sthana.toFixed(1); font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.preferredWidth: 46; horizontalAlignment: Text.AlignRight; opacity: 0.9 }
                            Label { text: modelData.dig.toFixed(1); font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.preferredWidth: 42; horizontalAlignment: Text.AlignRight; opacity: 0.9 }
                            Label { text: modelData.kala.toFixed(1); font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.preferredWidth: 46; horizontalAlignment: Text.AlignRight; opacity: 0.9 }
                            Label { text: modelData.chesta.toFixed(1); font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.preferredWidth: 42; horizontalAlignment: Text.AlignRight; opacity: 0.9 }
                            Label { text: modelData.naisargika.toFixed(1); font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.preferredWidth: 52; horizontalAlignment: Text.AlignRight; opacity: 0.9 }
                            Label { text: modelData.drik.toFixed(1); font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.preferredWidth: 42; horizontalAlignment: Text.AlignRight; opacity: 0.9 }
                            Label { text: modelData.total.toFixed(1); font.bold: true; font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.preferredWidth: 58; horizontalAlignment: Text.AlignRight }
                            Label { text: modelData.rupas.toFixed(2); font.bold: true; font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.preferredWidth: 44; horizontalAlignment: Text.AlignRight }
                            Label { text: String(modelData.minr); font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.preferredWidth: 46; horizontalAlignment: Text.AlignRight; opacity: 0.8 }
                            Label { text: modelData.strong ? view.txt("strong") : view.txt("weak"); color: modelData.strong ? "#2ecc71" : "#e74c3c"; font.bold: true; font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.fillWidth: true }
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: view.result && view.result.shadbala ? view.result.shadbala.note : ""
                        opacity: 0.65
                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                        wrapMode: Text.WordWrap
                    }
                }

                // Chara Karakas (Jaimini)
                Kirigami.Separator { Layout.fillWidth: true; visible: view.karakaRows && view.karakaRows.length > 0 }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: Kirigami.Units.largeSpacing
                    spacing: 6
                    visible: view.karakaRows && view.karakaRows.length > 0

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        Label { text: view.txt("karakas"); font.bold: true }
                        Item { Layout.fillWidth: true }
                        Label { text: view.txt("scheme"); opacity: 0.7 }
                        ComboBox {
                            Layout.preferredWidth: Kirigami.Units.gridUnit * 7
                            model: [view.txt("sevenKaraka"), view.txt("eightKaraka")]
                            currentIndex: view.karakaScheme === 7 ? 0 : 1
                            onActivated: {
                                view.karakaScheme = (index === 0) ? 7 : 8;
                                view.rebuildKarakas();
                            }
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: (view.result && view.result.karakas) ? view.result.karakas.note : ""
                        wrapMode: Text.WordWrap
                        font.pixelSize: Kirigami.Units.gridUnit * 0.65
                        opacity: 0.75
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 4
                        columnSpacing: Kirigami.Units.smallSpacing
                        rowSpacing: 2

                        Label { text: view.txt("graha"); font.bold: true; opacity: 0.75 }
                        Label { text: view.txt("deg"); font.bold: true; opacity: 0.75 }
                        Label { text: view.txt("karakaCol"); font.bold: true; opacity: 0.75 }
                        Label { text: view.txt("meaningCol"); font.bold: true; opacity: 0.75 }

                        Repeater {
                            model: view.karakaCells

                            Label {
                                Layout.row: modelData.row
                                Layout.column: modelData.col
                                Layout.fillWidth: modelData.fill
                                Layout.minimumWidth: modelData.col === 1 ? Kirigami.Units.gridUnit * 4 : 0
                                text: modelData.text
                                font.bold: modelData.bold
                                font.pixelSize: modelData.small ? Kirigami.Units.gridUnit * 0.85 : 14
                                wrapMode: modelData.wrap ? Text.WordWrap : Text.NoWrap
                                elide: modelData.fill ? Text.ElideNone : Text.ElideRight
                                opacity: modelData.small ? 0.75 : (modelData.band ? 1 : 0.9)
                            }
                        }
                    }
                }

                // Ghatak Chakra (Muhurta)
                Kirigami.Separator { Layout.fillWidth: true; visible: view.ghatakRows && view.ghatakRows.length > 0 }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: Kirigami.Units.largeSpacing
                    spacing: 6
                    visible: view.ghatakRows && view.ghatakRows.length > 0

                    Label { text: view.txt("ghatak"); font.bold: true }

                    Label {
                        Layout.fillWidth: true
                        text: view.txt("ghatakIntro").replace("%1", (view.result && view.result.ghatak) ? view.result.ghatak.janma_rashi : "")
                        wrapMode: Text.WordWrap
                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                        opacity: 0.8
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Repeater {
                            model: view.ghatakRows

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 6
                                Label {
                                    text: modelData.key + ":"
                                    font.bold: true
                                    opacity: 0.85
                                    Layout.preferredWidth: Math.max(implicitWidth, Kirigami.Units.gridUnit * 12)
                                }
                                Label {
                                    text: modelData.value
                                    Layout.fillWidth: true
                                    font.bold: true
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.result !== null }

                // Selected varga chart + placements
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: Kirigami.Units.largeSpacing
                    spacing: 6
                    visible: view.result !== null

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 6

                        Label { text: view.txt("vargaChart"); font.bold: true }
                        Item { Layout.fillWidth: true }
                        Label { text: view.txt("selectVarga"); opacity: 0.7 }
                        ComboBox {
                            id: vargaMenu
                            Layout.preferredWidth: Kirigami.Units.gridUnit * 6
                            onActivated: view.updateVargaChart()
                        }
                    }

                    Label {
                        id: vargaTitleText
                        Layout.fillWidth: true
                        text: ""
                        font.bold: true
                        color: Kirigami.Theme.highlightColor
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignHCenter
                        Layout.preferredHeight: Math.max(320, vargaChart.height + 12)
                        radius: 8
                        color: Qt.rgba(0, 0, 0, 0.15)
                        border.color: Qt.rgba(0.55, 0.55, 0.55, 0.4)
                        border.width: 1

                        KundaliChart {
                            id: vargaChart
                            anchors.centerIn: parent
                            width: Math.min(640, parent.width - 16)
                            height: width
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: view.result ? view.txt("vargas") : ""
                        font.bold: true
                        Layout.topMargin: 4
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        columnSpacing: Kirigami.Units.smallSpacing
                        rowSpacing: 2
                        visible: view.vargaPlacements && view.vargaPlacements.length > 0

                        Repeater {
                            model: view.vargaPlacements

                            Label {
                                Layout.fillWidth: true
                                text: modelData.name + "  —  " + modelData.sign + "  (" + modelData.deg + ")"
                                font.pixelSize: Kirigami.Units.gridUnit * 0.85
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.result !== null }

                // Vimshottari dasha tree
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.topMargin: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.mediumSpacing
                    visible: view.result && view.result.dashas

                    Rectangle {
                        Layout.fillWidth: true
                        radius: 8
                        color: Qt.rgba(0.29, 0.69, 0.38, 0.10)
                        border.color: Qt.rgba(0.29, 0.69, 0.38, 0.45)
                        border.width: 1
                        implicitHeight: dashaHeader.implicitHeight + 12

                        ColumnLayout {
                            id: dashaHeader
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10
                            spacing: 4

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                Label {
                                    text: view.txt("vimshottari")
                                    font.bold: true
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.95
                                }

                                Item { Layout.fillWidth: true }

                                Rectangle {
                                    Layout.preferredWidth: currentTag.implicitWidth + 14
                                    Layout.preferredHeight: currentTag.implicitHeight + 5
                                    radius: 10
                                    color: "#2ecc71"
                                    visible: view.currentDashaText() !== ""
                                    Label {
                                        id: currentTag
                                        anchors.centerIn: parent
                                        text: view.currentDashaText()
                                        font.bold: true
                                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                        color: "#0b1210"
                                    }
                                }
                            }

                            Label {
                                text: view.dashaSummary()
                                opacity: 0.75
                                font.pixelSize: Kirigami.Units.gridUnit * 0.72
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                            }
                        }
                    }

                    Repeater {
                        model: view.result && view.result.dashas ? view.result.dashas.mahadashas : []

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 3

                            Rectangle {
                                Layout.fillWidth: true
                                radius: 6
                                color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.16) : "#1c232d"
                                border.color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.6) : Qt.rgba(0.35, 0.42, 0.55, 0.35)
                                border.width: 1
                                implicitHeight: mdRow.implicitHeight + 10

                                Rectangle {
                                    width: 4
                                    height: parent.height
                                    anchors.verticalCenter: parent.verticalCenter
                                    color: modelData.is_current ? "#2ecc71" : "#5a6b82"
                                }

                                RowLayout {
                                    id: mdRow
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.leftMargin: 10
                                    anchors.rightMargin: 6
                                    spacing: 8

                                    Label {
                                        text: modelData.lord
                                        font.bold: true
                                        font.pixelSize: Kirigami.Units.gridUnit * 0.9
                                        Layout.preferredWidth: Kirigami.Units.gridUnit * 5
                                    }

                                    Rectangle {
                                        radius: 4
                                        color: Qt.rgba(0, 0, 0, 0.25)
                                        implicitWidth: yearsBadge.implicitWidth + 10
                                        implicitHeight: yearsBadge.implicitHeight + 4
                                        Label {
                                            id: yearsBadge
                                            anchors.centerIn: parent
                                            text: view.fmtYears(modelData.years)
                                            font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                            opacity: 0.85
                                        }
                                    }

                                    Label {
                                        text: `${modelData.start_date} → ${modelData.end_date}`
                                        opacity: 0.75
                                        font.pixelSize: Kirigami.Units.gridUnit * 0.72
                                        elide: Text.ElideMiddle
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        text: view.txt("current")
                                        visible: modelData.is_current
                                        color: "#2ecc71"
                                        font.bold: true
                                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                    }

                                    ToolButton {
                                        icon.name: "go-down"
                                        rotation: view.expandedMd === model.index ? 180 : 0
                                        onClicked: {
                                            view.autoAdFocus = false;
                                            view.expandedMd = (view.expandedMd === model.index) ? -1 : model.index;
                                        }
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        view.autoAdFocus = false;
                                        view.expandedMd = (view.expandedMd === model.index) ? -1 : model.index;
                                    }
                                }
                            }

                            // Antardashas of an expanded mahadasha
                            ColumnLayout {
                                Layout.fillWidth: true
                                Layout.leftMargin: 18
                                visible: view.expandedMd === model.index

                                Repeater {
                                    model: modelData.antardashas

                                    ColumnLayout {
                                        id: adCol
                                        Layout.fillWidth: true
                                        spacing: 3
                                        visible: !view.autoAdFocus || modelData.is_current
                                        // Capture the antardasha index here: inside the nested
                                        // pratyantardasha repeater `model.index` would shadow it.
                                        readonly property int adIndex: model.index

                                        Rectangle {
                                            Layout.fillWidth: true
                                            radius: 5
                                            color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.14) : "#1c232d"
                                            border.color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.5) : Qt.rgba(0.35, 0.42, 0.55, 0.3)
                                            border.width: 1
                                            implicitHeight: adRow.implicitHeight + 8

                                            RowLayout {
                                                id: adRow
                                                anchors.left: parent.left
                                                anchors.right: parent.right
                                                anchors.verticalCenter: parent.verticalCenter
                                                anchors.leftMargin: 8
                                                anchors.rightMargin: 6
                                                spacing: 8

                                                Label { text: modelData.lord; font.bold: true; font.pixelSize: Kirigami.Units.gridUnit * 0.85; Layout.preferredWidth: Kirigami.Units.gridUnit * 5 }
                                                Label {
                                                    text: view.fmtYears(modelData.years)
                                                    font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                                    opacity: 0.85
                                                    Layout.preferredWidth: Kirigami.Units.gridUnit * 2.5
                                                }
                                                Label {
                                                    text: `${modelData.start_date} → ${modelData.end_date}`
                                                    opacity: 0.75
                                                    font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                                    elide: Text.ElideMiddle
                                                    Layout.fillWidth: true
                                                }
                                                Label {
                                                    text: view.txt("current")
                                                    visible: modelData.is_current
                                                    color: "#2ecc71"
                                                    font.bold: true
                                                    font.pixelSize: Kirigami.Units.gridUnit * 0.65
                                                }
                                                ToolButton {
                                                    icon.name: "go-down"
                                                    rotation: view.expandedAd === adCol.adIndex ? 180 : 0
                                                    onClicked: {
                                                        view.autoAdFocus = false;
                                                        view.expandedAd = (view.expandedAd === adCol.adIndex) ? -1 : adCol.adIndex;
                                                    }
                                                }
                                            }

                                            MouseArea {
                                                anchors.fill: parent
                                                onClicked: {
                                                    view.autoAdFocus = false;
                                                    view.expandedAd = (view.expandedAd === adCol.adIndex) ? -1 : adCol.adIndex;
                                                }
                                            }
                                        }

                                        // Pratyantardashas of an expanded antardasha
                                        Repeater {
                                            Layout.fillWidth: true
                                            Layout.leftMargin: 18
                                            visible: view.expandedAd === adCol.adIndex
                                            model: modelData.pratyantardashas

                                            Rectangle {
                                                Layout.fillWidth: true
                                                radius: 4
                                                color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.12) : "#1c232d"
                                                border.color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.45) : Qt.rgba(0.35, 0.42, 0.55, 0.25)
                                                border.width: 1
                                                implicitHeight: pdRow.implicitHeight + 7

                                                RowLayout {
                                                    id: pdRow
                                                    anchors.left: parent.left
                                                    anchors.right: parent.right
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    anchors.leftMargin: 8
                                                    anchors.rightMargin: 6
                                                    spacing: 8

                                                    Label { text: modelData.lord; font.bold: true; font.pixelSize: Kirigami.Units.gridUnit * 0.8; Layout.preferredWidth: Kirigami.Units.gridUnit * 5 }
                                                    Label {
                                                        text: view.fmtYears(modelData.years)
                                                        font.pixelSize: Kirigami.Units.gridUnit * 0.68
                                                        opacity: 0.85
                                                        Layout.preferredWidth: Kirigami.Units.gridUnit * 2.5
                                                    }
                                                    Label {
                                                        text: `${modelData.start_date} → ${modelData.end_date}`
                                                        opacity: 0.75
                                                        font.pixelSize: Kirigami.Units.gridUnit * 0.68
                                                        elide: Text.ElideMiddle
                                                        Layout.fillWidth: true
                                                    }
                                                    Label {
                                                        text: view.txt("current")
                                                        visible: modelData.is_current
                                                        color: "#2ecc71"
                                                        font.bold: true
                                                        font.pixelSize: Kirigami.Units.gridUnit * 0.62
                                                    }
                                                    Item { Layout.preferredWidth: Kirigami.Units.gridUnit * 2 }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Kirigami.Dialog {
        id: saveKundaliDialog
        title: view.txt("saveTitle")
        standardButtons: Kirigami.Dialog.Ok | Kirigami.Dialog.Cancel
        preferredWidth: Kirigami.Units.gridUnit * 32

        contentItem: RowLayout {
            spacing: Kirigami.Units.smallSpacing

            Label {
                text: view.txt("savePrompt")
                opacity: 0.85
            }
            TextField {
                id: profileNameField
                Layout.fillWidth: true
                placeholderText: view.txt("savePrompt")
                focus: true
                onAccepted: saveKundaliDialog.accept()
            }
        }

        onAccepted: view.doSave(profileNameField.text)
    }

    Kirigami.Dialog {
        id: loadKundaliDialog
        title: view.txt("listTitle")
        standardButtons: Kirigami.Dialog.Close
        preferredWidth: Math.min(view.width * 0.92, Kirigami.Units.gridUnit * 105)
        preferredHeight: Math.min(view.height * 0.85, Kirigami.Units.gridUnit * 52)

        contentItem: ColumnLayout {
            spacing: Kirigami.Units.largeSpacing

            Label {
                text: view.txt("loadPrompt")
                opacity: 0.85
                visible: view.savedProfiles && view.savedProfiles.length > 0
            }

            Label {
                text: view.txt("noProfiles")
                opacity: 0.6
                visible: view.savedProfiles.length === 0
                horizontalAlignment: Text.AlignHCenter
                Layout.fillWidth: true
            }

            ListView {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.min(view.savedProfiles.length * 100, 640)
                clip: true
                model: view.savedProfiles
                spacing: Kirigami.Units.mediumSpacing

                delegate: Rectangle {
                    width: ListView.view.width
                    height: profileRow.implicitHeight + 22
                    radius: 10
                    color: "#1c232d"
                    border.color: Qt.rgba(0.35, 0.42, 0.55, 0.25)
                    border.width: 1

                    RowLayout {
                        id: profileRow
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: 18
                        anchors.rightMargin: 14
                        spacing: 14

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            Label {
                                text: modelData.name
                                font.bold: true
                                font.pixelSize: Kirigami.Units.gridUnit * 0.9
                                elide: Text.ElideNone
                                wrapMode: Text.Wrap
                                Layout.fillWidth: true
                            }
                            Label {
                                text: view.profileSummary(modelData)
                                font.pixelSize: Kirigami.Units.gridUnit * 0.75
                                opacity: 0.75
                                wrapMode: Text.Wrap
                                Layout.fillWidth: true
                            }
                        }

                        ToolButton {
                            text: view.txt("delProf")
                            icon.name: "edit-delete"
                            Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                            Layout.preferredHeight: Kirigami.Units.gridUnit * 3
                            onClicked: view.deleteProfile(modelData.id)
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: view.loadProfile(modelData.id)
                    }
                }
            }
        }
    }
}