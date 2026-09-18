import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: view
    implicitWidth: 520
    implicitHeight: 640

    property var result: null
    property var planetRows: []
    property var houseRows: []
    property var vargaPlacements: []
    property var cityChoices: []

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
            "lord": "Lord",
            "houses": "Houses",
            "current": "Now running",
            "md": "Mahadasha",
            "ad": "Antardasha",
            "pd": "Pratyantardasha",
            "show": "Expand",
            "dashaHeader": "9 Mahadashas · current auto-expanded",
            "selectVarga": "Division",
            "digLegend": "ᴷ = Kendra (1/4/7/10) · V = Vargottam · red-tinted names = Vakri, ◆ = Asta",
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
            "nameInitial": "Name Initial:"
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
            "lord": "Svāmī",
            "houses": "Bhāva",
            "current": "Adya",
            "md": "Mahādaśā",
            "ad": "Antardaśā",
            "pd": "Pratyantardaśā",
            "show": "Vistāra",
            "dashaHeader": "9 mahādaśā · adya svataḥ",
            "selectVarga": "Varga",
            "digLegend": "ᴷ = Kendra (1/4/7/10) · V = Vargottama · ᴿ-coloured names = Vakrī, ◆ = Asta",
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
            "nameInitial": "Nāma Prāraṁbha:"
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
            "lord": "स्वामी",
            "houses": "भाव",
            "current": "वर्तमान",
            "md": "महादशा",
            "ad": "अंतर्दशा",
            "pd": "प्रत्यंतर्दशा",
            "show": "विस्तार",
            "dashaHeader": "9 महादशाएँ · वर्तमान स्वतः खुला",
            "selectVarga": "वर्ग",
            "digLegend": "ᴷ = केंद्र (1/4/7/10) · V = वर्गोत्तम · लाल रंग के नाम = वक्री, ◆ = अस्त",
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
            "nameInitial": "नाम प्रारंभ:"
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
                    statusMessage.text = txt("engineErr").arg(xhr.status);
                }
            }
        };
        xhr.send();
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

        var houses = r.houses || {};
        var hrows = [];
        for (var h = 1; h <= 12; h++) {
            hrows.push({ num: h, signNum: ((r.lagna.rashi + h - 1) % 12) + 1, name: houses[h] ? houses[h].rashi_name : "--", lord: houses[h] ? houses[h].lord : "--" });
        }
        view.houseRows = hrows;

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

    function dashaSummary() {
        if (!view.result || !view.result.dashas) return "";
        var d = view.result.dashas;
        return `${view.txt("vimshottari")} — ${view.txt("balance")} ${d.balance_years.toFixed(2)}y · ${d.start_lord} ${d.balance_years.toFixed(2)}y — ${d.mahadashas[d.mahadashas.length - 1].end_date}`;
    }

    function fmtYears(y) {
        var v = Number(y);
        if (isNaN(v)) return "--";
        var s = (Math.floor(v) === v) ? String(v) : v.toFixed(3);
        return s.replace(/\.?0+$/, "") + "y";
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
        spacing: Kirigami.Units.smallSpacing

        Kirigami.Heading {
            text: view.txt("title")
            level: 4
        }

        // Birth date: Date / Month / Year dropdowns with invalid-date fallback
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2

            RowLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
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
                    spacing: 2
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
                    spacing: 2
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
                spacing: 2
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
                spacing: 2
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
                spacing: 2
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
                spacing: 2
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
                spacing: Kirigami.Units.smallSpacing

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

                // Pictorial chart
                Rectangle {
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredHeight: Math.max(280, mainChart.height + 8)
                    radius: 8
                    color: Qt.rgba(0, 0, 0, 0.15)
                    visible: view.result !== null
                    border.color: Qt.rgba(0.55, 0.55, 0.55, 0.4)
                    border.width: 1

                    KundaliChart {
                        id: mainChart
                        anchors.centerIn: parent
                        width: Math.min(560, parent.width - 12)
                        height: width
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.result !== null }

                // Analyse
                ColumnLayout {
                    id: analysisSection
                    Layout.fillWidth: true
                    spacing: 4
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
                            spacing: 2
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

                Kirigami.Separator { Layout.fillWidth: true; visible: view.planetRows.length > 0 }

                // Planets
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    visible: view.planetRows.length > 0

                    Label { text: view.txt("nineGrahas"); font.bold: true }

                    Repeater {
                        model: view.planetRows

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Label {
                                text: modelData.name
                                font.bold: true
                                Layout.preferredWidth: Kirigami.Units.gridUnit * 4.5
                                color: modelData.digColor
                            }
                            Label {
                                text: modelData.degree
                                Layout.preferredWidth: Kirigami.Units.gridUnit * 3.2
                                opacity: 0.9
                            }
                            Label {
                                text: modelData.sign
                                Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                            }
                            Label {
                                text: modelData.dignity
                                color: modelData.digColor
                                font.bold: true
                                font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                elide: Text.ElideRight
                                Layout.preferredWidth: Kirigami.Units.gridUnit * 5
                                ToolTip.text: modelData.dignity
                                ToolTip.visible: containedText !== text && hovered
                            }
                            Label {
                                text: modelData.nak
                                opacity: 0.8
                                fontSizeMode: Text.HorizontalFit
                                Layout.fillWidth: true
                            }
                            Label {
                                text: modelData.retro ? `${view.txt("vakri")}` : view.txt("maargi")
                                color: modelData.retro ? "#e74c3c" : "#2ecc71"
                                font.bold: true
                                font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                Layout.preferredWidth: Kirigami.Units.gridUnit * 3.4
                            }
                            Label {
                                text: modelData.combust ? view.txt("asta") : ""
                                color: "#e67e22"
                                font.bold: true
                                font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                            }
                            Label {
                                text: modelData.vargottam ? "V" : ""
                                color: "#2ecc71"
                                font.bold: true
                                Layout.preferredWidth: Kirigami.Units.gridUnit * 1.4
                            }
                            Label {
                                text: "R" + modelData.rashiNum + (modelData.kendra ? " ᴷ" : "")
                                color: modelData.kendra ? "#e67e22" : Kirigami.Theme.textColor
                                font.bold: modelData.kendra
                                Layout.preferredWidth: Kirigami.Units.gridUnit * 2.6
                            }
                        }
                    }

                    Label {
                        text: view.txt("digLegend")
                        opacity: 0.6
                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.houseRows.length > 0 }

                // Houses
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    visible: view.houseRows.length > 0

                    Label { text: view.txt("houses"); font.bold: true }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 3

                        Repeater {
                            model: view.houseRows

                            Label {
                                text: `${modelData.signNum}. ${modelData.name} (${modelData.lord})`
                                font.pixelSize: Kirigami.Units.gridUnit * 0.75
                            }
                        }
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.result !== null }

                // Selected varga chart + placements
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
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
                        Layout.preferredHeight: Math.max(280, vargaChart.height + 8)
                        radius: 8
                        color: Qt.rgba(0, 0, 0, 0.15)
                        border.color: Qt.rgba(0.55, 0.55, 0.55, 0.4)
                        border.width: 1

                        KundaliChart {
                            id: vargaChart
                            anchors.centerIn: parent
                            width: Math.min(560, parent.width - 12)
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
                        visible: view.vargaPlacements.length > 0

                        Repeater {
                            model: view.vargaPlacements

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 4

                                Label {
                                    text: modelData.name
                                    font.bold: true
                                    Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                                }
                                Label {
                                    text: modelData.sign
                                    opacity: 0.9
                                    Layout.fillWidth: true
                                }
                                Label {
                                    text: modelData.deg
                                    opacity: 0.75
                                }
                            }
                        }
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.result !== null }

                // Vimshottari dasha tree
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 6
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
                            spacing: 2

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
                            spacing: 1

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
                                        Layout.fillWidth: true
                                        spacing: 1
                                        visible: !view.autoAdFocus || modelData.is_current

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
                                                    rotation: view.expandedAd === model.index ? 180 : 0
                                                    onClicked: {
                                                        view.autoAdFocus = false;
                                                        view.expandedAd = (view.expandedAd === model.index) ? -1 : model.index;
                                                    }
                                                }
                                            }

                                            MouseArea {
                                                anchors.fill: parent
                                                onClicked: {
                                                    view.autoAdFocus = false;
                                                    view.expandedAd = (view.expandedAd === model.index) ? -1 : model.index;
                                                }
                                            }
                                        }

                                        // Pratyantardashas of an expanded antardasha
                                        Repeater {
                                            Layout.fillWidth: true
                                            Layout.leftMargin: 18
                                            visible: view.expandedAd === model.index
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
}