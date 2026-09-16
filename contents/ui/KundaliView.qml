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
            "selectVarga": "Division"
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
            "selectVarga": "Varga"
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
            "selectVarga": "वर्ग"
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

    function compute() {
        var parts = parseDateStr(dateField.text);
        if (!parts) {
            statusMessage.type = Kirigami.MessageType.Error;
            statusMessage.text = txt("invalidDate");
            statusMessage.visible = true;
            return;
        }
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
        var q = `date=${String(parts[2]).padStart(2, '0')}-${String(parts[1]).padStart(2, '0')}-${parts[0]}` +
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
        switch (code) {
        case "Exalted": return "#2ecc71";
        case "Moolatrikona": return "#2cd9a0";
        case "Own Sign": return "#27ae60";
        case "Debilitated": return "#e74c3c";
        case "Friendly Sign": return "#3498db";
        case "Neutral Sign": return "#95a5a6";
        case "Enemy Sign": return "#e67e22";
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
        var signs = [-1, -1, -1, -1, -1, -1, -1, -1, -1];
        var markers = [];
        var colors = [];
        var v = view.result.vargas[chartKey];
        if (chartKey === "D1") {
            for (var i = 0; i < 9; i++) {
                if (bars[i]) {
                    signs[i] = bars[i].rashi;
                    markers[i] = { retro: bars[i].retrograde, combust: bars[i].combust };
                    colors[i] = dignityColor(bars[i].dignity_code);
                }
            }
            return { signs: signs, markers: markers, colors: colors };
        }
        for (var j = 0; j < 9; j++) {
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
        for (var i = 0; i < 9; i++) {
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
        for (var i = 0; i < 9; i++) {
            var p = bars[i];
            if (!p) continue;
            rows.push({
                name: p.name,
                degree: formatDeg(p.degree_in_sign),
                sign: p.rashi_name,
                nak: p.nakshatra_name + " " + p.nakshatra_pada,
                house: p.house,
                dignity: p.dignity,
                digColor: dignityColor(p.dignity_code),
                retro: p.retrograde,
                combust: p.combust,
                vargottam: p.is_vargottam
            });
        }
        view.planetRows = rows;

        var houses = r.houses || {};
        var hrows = [];
        for (var h = 1; h <= 12; h++) {
            hrows.push({ num: h, name: houses[h] ? houses[h].rashi_name : "--", lord: houses[h] ? houses[h].lord : "--" });
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

    ColumnLayout {
        anchors.fill: parent
        spacing: Kirigami.Units.smallSpacing

        Kirigami.Heading {
            text: view.txt("title")
            level: 4
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            TextField {
                id: dateField
                placeholderText: "DD-MM-YYYY"
                text: view.todayStr()
                Layout.fillWidth: true
                validator: RegularExpressionValidator { regularExpression: /^\d{2}-\d{2}-\d{4}$/ }
            }

            SpinBox {
                id: hourSpin
                from: 0
                to: 23
                value: 10
                editable: true
                textFromValue: function(v) { return v + i18n("h"); }
            }

            SpinBox {
                id: minuteSpin
                from: 0
                to: 59
                value: 30
                editable: true
                textFromValue: function(v) { return v + i18n("m"); }
            }

            Button {
                text: view.txt("compute")
                icon.name: "view-refresh"
                onClicked: view.compute()
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

            TextField {
                id: latField
                placeholderText: view.txt("lat")
                text: String(Number(view.cfg("latitude", 23.1765)).toFixed(4))
                Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                validator: DoubleValidator { bottom: -90; top: 90; decimals: 4 }
            }
            TextField {
                id: lonField
                placeholderText: view.txt("lon")
                text: String(Number(view.cfg("longitude", 75.7885)).toFixed(4))
                Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                validator: DoubleValidator { bottom: -180; top: 180; decimals: 4 }
            }
            TextField {
                id: altField
                placeholderText: view.txt("alt")
                text: String(Number(view.cfg("altitude", 0)).toFixed(1))
                Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                validator: DoubleValidator { bottom: -500; top: 9000; decimals: 1 }
            }
            TextField {
                id: tzField
                placeholderText: view.txt("tzh")
                text: String(Number(view.cfg("timezone", 5.5)).toFixed(1))
                Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                validator: DoubleValidator { bottom: -12; top: 14; decimals: 2 }
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
                        width: Math.min(340, parent.width - 12)
                        height: width
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.result !== null }

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
                                text: view.txt("housePrefix") + modelData.house
                                Layout.preferredWidth: Kirigami.Units.gridUnit * 2
                            }
                        }
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
                                text: `${modelData.num}. ${modelData.name} (${modelData.lord})`
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
                        Layout.preferredHeight: Math.max(240, vargaChart.height + 8)
                        radius: 8
                        color: Qt.rgba(0, 0, 0, 0.15)
                        border.color: Qt.rgba(0.55, 0.55, 0.55, 0.4)
                        border.width: 1

                        KundaliChart {
                            id: vargaChart
                            anchors.centerIn: parent
                            width: Math.min(300, parent.width - 12)
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
                    spacing: 2
                    visible: view.result && view.result.dashas

                    Label {
                        text: view.dashaSummary()
                        font.bold: true
                    }
                    Label {
                        text: view.txt("dashaHeader")
                        opacity: 0.7
                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                    }

                    Repeater {
                        model: view.result && view.result.dashas ? view.result.dashas.mahadashas : []

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 1

                            Rectangle {
                                Layout.fillWidth: true
                                radius: 4
                                color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.22) : "transparent"
                                implicitHeight: mdRow.implicitHeight + 6
                                border.color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.6) : "transparent"
                                border.width: 1

                                RowLayout {
                                    id: mdRow
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.leftMargin: 6
                                    anchors.rightMargin: 6
                                    spacing: 6

                                    Label {
                                        text: modelData.is_current ? "\u25CF " : ""
                                        color: "#2ecc71"
                                        font.bold: true
                                    }
                                    Label {
                                        text: modelData.lord
                                        font.bold: true
                                        Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                                    }
                                    Label {
                                        text: modelData.years + "y"
                                        Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                                    }
                                    Label {
                                        text: `${modelData.start_date} → ${modelData.end_date}`
                                        opacity: 0.8
                                        fontSizeMode: Text.HorizontalFit
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        text: modelData.is_current ? view.txt("current") : ""
                                        color: "#2ecc71"
                                        font.bold: true
                                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                    }
                                    ToolButton {
                                        icon.name: view.expandedMd === model.index ? "go-up" : "go-down"
                                        onClicked: view.expandedMd = (view.expandedMd === model.index) ? -1 : model.index
                                    }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: view.expandedMd = (view.expandedMd === model.index) ? -1 : model.index
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

                                        Rectangle {
                                            Layout.fillWidth: true
                                            radius: 3
                                            color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.18) : "transparent"
                                            implicitHeight: adRow.implicitHeight + 4
                                            border.color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.5) : "transparent"
                                            border.width: 1

                                            RowLayout {
                                                id: adRow
                                                anchors.left: parent.left
                                                anchors.right: parent.right
                                                anchors.verticalCenter: parent.verticalCenter
                                                anchors.leftMargin: 6
                                                anchors.rightMargin: 6
                                                spacing: 5

                                                Label { text: modelData.is_current ? "\u25CF " : ""; color: "#2ecc71"; font.bold: true }
                                                Label { text: modelData.lord; font.bold: true; Layout.preferredWidth: Kirigami.Units.gridUnit * 4 }
                                                Label { text: modelData.years + "y"; Layout.preferredWidth: Kirigami.Units.gridUnit * 4 }
                                                Label {
                                                    text: `${modelData.start_date} → ${modelData.end_date}`
                                                    opacity: 0.8
                                                    fontSizeMode: Text.HorizontalFit
                                                    Layout.fillWidth: true
                                                }
                                                ToolButton {
                                                    icon.name: view.expandedAd === model.index ? "go-up" : "go-down"
                                                    onClicked: view.expandedAd = (view.expandedAd === model.index) ? -1 : model.index
                                                }
                                            }

                                            MouseArea {
                                                anchors.fill: parent
                                                onClicked: view.expandedAd = (view.expandedAd === model.index) ? -1 : model.index
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
                                                radius: 2
                                                color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.15) : "transparent"
                                                implicitHeight: pdRow.implicitHeight + 4
                                                border.color: modelData.is_current ? Qt.rgba(0.29, 0.69, 0.38, 0.4) : "transparent"
                                                border.width: 1

                                                RowLayout {
                                                    id: pdRow
                                                    anchors.left: parent.left
                                                    anchors.right: parent.right
                                                    anchors.verticalCenter: parent.verticalCenter
                                                    anchors.leftMargin: 6
                                                    anchors.rightMargin: 6
                                                    spacing: 5

                                                    Label { text: modelData.is_current ? "\u25CF " : ""; color: "#2ecc71"; font.bold: true }
                                                    Label { text: modelData.lord; font.bold: true; Layout.preferredWidth: Kirigami.Units.gridUnit * 4 }
                                                    Label { text: modelData.years + "y"; Layout.preferredWidth: Kirigami.Units.gridUnit * 4 }
                                                    Label {
                                                        text: `${modelData.start_date} → ${modelData.end_date}`
                                                        opacity: 0.8
                                                        fontSizeMode: Text.HorizontalFit
                                                        Layout.fillWidth: true
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
}