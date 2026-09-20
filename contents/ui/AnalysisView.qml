import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: view
    implicitWidth: 520
    implicitHeight: 640

    property var medhaResult: null
    property var cityChoices: []
    property string langOverride: ""
    property string ayanamsaOverride: ""

    readonly property var uiTxt: ({
        "en": {
            "title": "Chart Analysis (KalaMedha)",
            "compute": "Analyze",
            "searchCity": "City",
            "searchPlaceholder": "Search city…",
            "searchBtn": "Find",
            "lat": "Lat",
            "lon": "Lon",
            "alt": "Alt (m)",
            "tzh": "TZ (h)",
            "invalidDate": "Enter a valid date as DD-MM-YYYY.",
            "computing": "Computing…",
            "parseFail": "Failed to parse response.",
            "engineErr": "Engine error (%1). Is the daemon running?",
            "searchErr": "City search failed (%1).",
            "sayana": "Sayana (Tropical)",
            "noResult": "Press Analyze to generate a chart reading.",
            "lagnaSection": "Lagna",
            "grahasSection": "Graha Placements",
            "yogasSection": "Yogas",
            "dashaSection": "Current Dasha",
            "strengthsSection": "Strength & Weakness Rankings",
            "evidenceSection": "Supporting Evidence"
        },
        "iast": {
            "title": "Kuṇḍalī Vicāra (KalaMedha)",
            "compute": "Vicāretu",
            "searchCity": "Nagara",
            "searchPlaceholder": "Nagara khojeṁ…",
            "searchBtn": "Khojeṁ",
            "lat": "Akṣāṁśa",
            "lon": "Reṣāṁśa",
            "alt": "Ucchtā (m)",
            "tzh": "Samaya (h)",
            "invalidDate": "Tithi DD-MM-YYYY deṁ.",
            "computing": "Gaṇanā…",
            "parseFail": "Uttara nahīṁ milā.",
            "engineErr": "Yantra-truṭi (%1).",
            "searchErr": "Nagara khoja truṭi (%1).",
            "sayana": "Sāyana",
            "noResult": "Vicāretu iti press kuru.",
            "lagnaSection": "Lagna",
            "grahasSection": "Graha Sthiti",
            "yogasSection": "Yoga",
            "dashaSection": "Vartamāna Daśā",
            "strengthsSection": "Bala–Durbala Rankings",
            "evidenceSection": "Sākṣya"
        },
        "devanagari": {
            "title": "कुंडली विश्लेषण (कालमेध)",
            "compute": "विश्लेषण करें",
            "searchCity": "शहर",
            "searchPlaceholder": "शहर खोजें…",
            "searchBtn": "खोजें",
            "lat": "अक्षांश",
            "lon": "रेखांश",
            "alt": "ऊँचाई (मी)",
            "tzh": "समय (घं)",
            "invalidDate": "दिनांक DD-MM-YYYY प्रारूप में दर्ज करें।",
            "computing": "गणना हो रही है…",
            "parseFail": "प्रतिक्रिया पार्स नहीं हुई।",
            "engineErr": "इंजन त्रुटि (%1)।",
            "searchErr": "शहर खोज विफल (%1)।",
            "sayana": "सायन",
            "noResult": "विश्लेषण हेतु विश्लेषण दबाएँ।",
            "lagnaSection": "लग्न",
            "grahasSection": "ग्रह स्थिति",
            "yogasSection": "योग",
            "dashaSection": "वर्तमान दशा",
            "strengthsSection": "बल–दुर्बल क्रम",
            "evidenceSection": "साक्ष्य"
        }
    })

    function langKey() {
        if (view.langOverride) return view.langOverride;
        return (typeof plasmoid !== "undefined" && plasmoid.configuration) ? plasmoid.configuration.lang : "en";
    }

    function txt(key) {
        var t = uiTxt[langKey()] || uiTxt["en"];
        return t[key] !== undefined ? t[key] : key;
    }

    function cfg(key, dflt) {
        if (typeof plasmoid !== "undefined" && plasmoid.configuration) {
            var v = plasmoid.configuration[key];
            return (v === undefined || v === "") ? dflt : v;
        }
        return dflt;
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

    function applyCityChoice(i) {
        if (!cityChoices[i]) return;
        latField.text = String(Number(cityChoices[i].lat).toFixed(4));
        lonField.text = String(Number(cityChoices[i].lon).toFixed(4));
        altField.text = String(Number(cityChoices[i].alt || 0).toFixed(1));
        tzField.text = String(Number(cityChoices[i].tz || 0).toFixed(1));
    }

    function searchCities() {
        var q = cityField.text.trim();
        if (!q) return;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/search_city?q=" + encodeURIComponent(q), true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200) {
                try {
                    var list = JSON.parse(xhr.responseText) || [];
                    view.cityChoices = list;
                    cityCombo.model = list.map(function(c) { return c.name; });
                    if (list.length > 0) { cityCombo.currentIndex = 0; applyCityChoice(0); }
                } catch (e) {}
            }
        };
        xhr.send();
    }

    function analyze() {
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
        if (isNaN(lat) || isNaN(lon)) return;
        var q = `date=${String(parts[2]).padStart(2, '0')}-${String(parts[1]).padStart(2, '0')}-${parts[0]}` +
                `&hour=${hourSpin.value}&minute=${minuteSpin.value}` +
                `&lat=${lat}&lon=${lon}&alt=${alt}&tz=${tz}` +
                `&lang=${encodeURIComponent(langKey())}` +
                `&ayanamsa=${view.ayanamsaOverride || cfg("ayanamsa", "lahiri")}`;
        statusMessage.type = Kirigami.MessageType.Information;
        statusMessage.text = txt("computing");
        statusMessage.visible = true;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/medha?" + q, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            statusMessage.visible = false;
            if (xhr.status === 200) {
                try {
                    var d = JSON.parse(xhr.responseText);
                    view.medhaResult = d.medha || null;
                } catch (e) {
                    statusMessage.type = Kirigami.MessageType.Error;
                    statusMessage.text = txt("parseFail");
                    statusMessage.visible = true;
                }
            } else {
                statusMessage.type = Kirigami.MessageType.Error;
                statusMessage.text = view.serverErrorText(xhr) || view.txt("engineErr").arg(xhr.status);
                statusMessage.visible = true;
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

    function runWithParams(p) {
        dateField.text = p.date || dateField.text;
        hourSpin.value = (p.hour !== undefined) ? p.hour : hourSpin.value;
        minuteSpin.value = (p.minute !== undefined) ? p.minute : minuteSpin.value;
        latField.text = (p.lat !== undefined) ? String(Number(p.lat).toFixed(4)) : latField.text;
        lonField.text = (p.lon !== undefined) ? String(Number(p.lon).toFixed(4)) : lonField.text;
        altField.text = (p.alt !== undefined) ? String(Number(p.alt).toFixed(1)) : altField.text;
        tzField.text = (p.tz !== undefined) ? String(Number(p.tz).toFixed(1)) : tzField.text;
        view.langOverride = p.lang || "";
        view.ayanamsaOverride = p.ayanamsa || "";
        view.medhaResult = null;
        view.analyze();
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Kirigami.Units.smallSpacing

        Kirigami.Heading { text: view.txt("title"); level: 4 }

        // Params row 1
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
            SpinBox { id: hourSpin; from: 0; to: 23; value: 10; editable: true; textFromValue: function(v) { return v + i18n("h"); }; valueFromText: function(t) { return Math.max(0, Math.min(23, parseInt(t) || 0)); } }
            SpinBox { id: minuteSpin; from: 0; to: 59; value: 30; editable: true; textFromValue: function(v) { return v + i18n("m"); }; valueFromText: function(t) { return Math.max(0, Math.min(59, parseInt(t) || 0)); } }
            Button { text: view.txt("compute"); icon.name: "view-refresh"; onClicked: view.analyze() }
        }

        // Params row 2: city search
        RowLayout {
            Layout.fillWidth: true; spacing: Kirigami.Units.smallSpacing
            TextField { id: cityField; Layout.fillWidth: true; placeholderText: view.txt("searchPlaceholder"); onAccepted: view.searchCities() }
            Button { text: view.txt("searchBtn"); icon.name: "edit-find"; onClicked: view.searchCities() }
            ComboBox { id: cityCombo; Layout.preferredWidth: Kirigami.Units.gridUnit * 8; onActivated: view.applyCityChoice(currentIndex) }
        }

        // Params row 3: coords
        RowLayout {
            Layout.fillWidth: true; spacing: Kirigami.Units.smallSpacing
            TextField { id: latField; placeholderText: view.txt("lat"); text: String(Number(view.cfg("latitude", 23.1765)).toFixed(4)); Layout.preferredWidth: Kirigami.Units.gridUnit * 4; validator: DoubleValidator { bottom: -90; top: 90; decimals: 4 } }
            TextField { id: lonField; placeholderText: view.txt("lon"); text: String(Number(view.cfg("longitude", 75.7885)).toFixed(4)); Layout.preferredWidth: Kirigami.Units.gridUnit * 4; validator: DoubleValidator { bottom: -180; top: 180; decimals: 4 } }
            TextField { id: altField; placeholderText: view.txt("alt"); text: String(Number(view.cfg("altitude", 0)).toFixed(1)); Layout.preferredWidth: Kirigami.Units.gridUnit * 3; validator: DoubleValidator { bottom: -500; top: 9000; decimals: 1 } }
            TextField { id: tzField; placeholderText: view.txt("tzh"); text: String(Number(view.cfg("timezone", 5.5)).toFixed(1)); Layout.preferredWidth: Kirigami.Units.gridUnit * 3; validator: DoubleValidator { bottom: -12; top: 14; decimals: 2 } }
        }

        Kirigami.InlineMessage { id: statusMessage; Layout.fillWidth: true; type: Kirigami.MessageType.Warning; visible: false }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            ColumnLayout {
                width: parent.width; spacing: Kirigami.Units.smallSpacing

                Label { text: view.txt("noResult"); visible: !view.medhaResult; opacity: 0.6; Layout.fillWidth: true; wrapMode: Text.WordWrap }

                // Narrative: Lagna
                ColumnLayout {
                    visible: !!view.medhaResult && !!view.medhaResult.narrative && !!view.medhaResult.narrative.lagna
                    Layout.fillWidth: true; spacing: 2
                    Label { text: view.txt("lagnaSection"); font.bold: true }
                    Label { text: view.medhaResult ? (view.medhaResult.narrative.lagna || "") : ""; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                }

                // Narrative: Grahas list
                ColumnLayout {
                    visible: !!view.medhaResult && !!view.medhaResult.narrative && !!(view.medhaResult.narrative.grahas && view.medhaResult.narrative.grahas.length > 0)
                    Layout.fillWidth: true; spacing: 2
                    Label { text: view.txt("grahasSection"); font.bold: true }
                    Repeater {
                        model: view.medhaResult ? (view.medhaResult.narrative.grahas || []) : []
                        Label { text: "• " + modelData; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: Kirigami.Units.gridUnit * 0.8 }
                    }
                }

                // Narrative: Yogas
                ColumnLayout {
                    visible: !!view.medhaResult && !!view.medhaResult.narrative && !!(view.medhaResult.narrative.yogas && view.medhaResult.narrative.yogas.length > 0)
                    Layout.fillWidth: true; spacing: 2
                    Label { text: view.txt("yogasSection"); font.bold: true }
                    Repeater {
                        model: view.medhaResult ? (view.medhaResult.narrative.yogas || []) : []
                        Label { text: "• " + modelData; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: Kirigami.Units.gridUnit * 0.8 }
                    }
                }

                // Narrative: Dasha
                ColumnLayout {
                    visible: !!view.medhaResult && !!view.medhaResult.narrative && !!view.medhaResult.narrative.dasha
                    Layout.fillWidth: true; spacing: 2
                    Label { text: view.txt("dashaSection"); font.bold: true }
                    Label { text: view.medhaResult ? (view.medhaResult.narrative.dasha || "") : ""; Layout.fillWidth: true; wrapMode: Text.WordWrap }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: !!view.medhaResult }

                // Strength rankings
                ColumnLayout {
                    visible: !!view.medhaResult && !!view.medhaResult.strengths_weaknesses && !!(view.medhaResult.strengths_weaknesses.rankings && view.medhaResult.strengths_weaknesses.rankings.length > 0)
                    Layout.fillWidth: true; spacing: 4
                    Label { text: view.txt("strengthsSection"); font.bold: true }
                    Repeater {
                        model: view.medhaResult ? (view.medhaResult.strengths_weaknesses.rankings || []) : []
                        RowLayout {
                            Layout.fillWidth: true; spacing: 6
                            Label { text: modelData.name; font.bold: true; Layout.preferredWidth: Kirigami.Units.gridUnit * 4; color: (modelData.score || 0) > 0 ? "#2ecc71" : (modelData.score || 0) < 0 ? "#e74c3c" : "#bdc3c7" }
                            Label { text: (modelData.score || 0).toFixed(1); Layout.preferredWidth: Kirigami.Units.gridUnit * 2; opacity: 0.7 }
                            Label { text: (modelData.reasons || []).join("; "); Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: Kirigami.Units.gridUnit * 0.75; opacity: 0.8 }
                        }
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: !!view.medhaResult }

                // Evidence
                ColumnLayout {
                    visible: !!view.medhaResult && !!view.medhaResult.narrative && !!(view.medhaResult.narrative.notable_evidence && view.medhaResult.narrative.notable_evidence.length > 0)
                    Layout.fillWidth: true; spacing: 2
                    Label { text: view.txt("evidenceSection"); font.bold: true }
                    Repeater {
                        model: view.medhaResult ? (view.medhaResult.narrative.notable_evidence || []) : []
                        Label { text: "• " + modelData; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: Kirigami.Units.gridUnit * 0.75; opacity: 0.7 }
                    }
                }
            }
        }
    }
}
