import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: view
    implicitWidth: 520
    implicitHeight: 640

    property var result: null
    property var transitRows: []
    property var yogaRows: []
    property var signChangeRows: []
    property var cityChoices: []

    readonly property var rashisEn: ["Mesh", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrishchika", "Dhanu", "Makar", "Kumbha", "Meena"]
    readonly property var rashisIast: ["Meṣa", "Vṛṣabha", "Mithuna", "Karka", "Siṃha", "Kanyā", "Tulā", "Vṛścika", "Dhanu", "Makara", "Kumbha", "Mīna"]
    readonly property var rashisDev: ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]

    readonly property var uiTxt: ({
        "en": {
            "title": "Gochara (Planetary Transits)",
            "compute": "Compute",
            "searchCity": "City",
            "searchPlaceholder": "Search city…",
            "searchBtn": "Find",
            "manualCrd": "Or enter coordinates",
            "birthDate": "Birth date",
            "transitDate": "Transit date",
            "lat": "Lat",
            "lon": "Lon",
            "alt": "Alt (m)",
            "tzh": "TZ (h)",
            "nineGrahas": "Transiting Grahas",
            "transitYogas": "Special Yogas",
            "signChanges": "Next Sign Changes",
            "conjunctions": "Transit Conjunctions",
            "noneYoga": "No significant transit yogas.",
            "noneConj": "No conjunctions within 1\u00B0 at this instant.",
            "noneChange": "No sign change within the next 1000 days.",
            "ayanamsa": "Ayanamsa",
            "noChart": "No figure computed yet.",
            "invalidDate": "Enter a valid date as DD-MM-YYYY.",
            "computing": "Computing…",
            "parseFail": "Failed to parse response.",
            "engineErr": "Engine error (%1). Is the daemon running?",
            "searchErr": "City search failed (%1).",
            "house": "House",
            "sign": "Sign",
            "deg": "Deg",
            "retro": "Vakri",
            "when": "Date",
            "severity": "Sev"
        },
        "iast": {
            "title": "Gocāra (Graha Sañcāra)",
            "compute": "Gaṇanā",
            "searchCity": "Nagara",
            "searchPlaceholder": "Nagara khojeṁ…",
            "searchBtn": "Khojeṁ",
            "manualCrd": "Athavā nirdeśāṅka",
            "birthDate": "Janma dina",
            "transitDate": "Sañcāra dina",
            "lat": "Akṣāṁśa",
            "lon": "Reṣāṁśa",
            "alt": "Ucchtā (m)",
            "tzh": "Samaya (h)",
            "nineGrahas": "Gacchanta graha",
            "transitYogas": "Viśeṣa yoga",
            "signChanges": "Agrā rāśi parivartana",
            "conjunctions": "Graha-yuti",
            "noneYoga": "Na ko'pi viśeṣa yogaḥ.",
            "noneConj": "Na ko'pi yutiḥ 1\u00B0-sahitaḥ.",
            "noneChange": "Na rāśi parivartanaṁ 1000 dineṣu.",
            "ayanamsa": "Ayanāṁśa",
            "noChart": "Abhī gaṇanā na kṛtā.",
            "invalidDate": "Tithi DD-MM-YYYY deṁ.",
            "computing": "Gaṇanā…",
            "parseFail": "Uttara na milat.",
            "engineErr": "Yantra-truṭi (%1).",
            "searchErr": "Nagara khoja truṭi (%1).",
            "house": "Bhāva",
            "sign": "Rāśi",
            "deg": "Aṁśa",
            "retro": "Vakrī",
            "when": "Dina",
            "severity": "Bala"
        },
        "devanagari": {
            "title": "गोचर (ग्रह संचार)",
            "compute": "गणना करें",
            "searchCity": "शहर",
            "searchPlaceholder": "शहर खोजें…",
            "searchBtn": "खोजें",
            "manualCrd": "या निर्देशांक भरें",
            "birthDate": "जन्म तिथि",
            "transitDate": "गोचर तिथि",
            "lat": "अक्षांश",
            "lon": "रेखांश",
            "alt": "ऊँचाई (मी)",
            "tzh": "समय (घं)",
            "nineGrahas": "गोचर ग्रह",
            "transitYogas": "विशेष योग",
            "signChanges": "अगला राशि परिवर्तन",
            "conjunctions": "ग्रह युति",
            "noneYoga": "कोई विशेष गोचर योग नहीं।",
            "noneConj": "इस क्षण 1° के भीतर कोई युति नहीं।",
            "noneChange": "अगले 1000 दिनों में राशि परिवर्तन नहीं।",
            "ayanamsa": "अयनांश",
            "noChart": "अभी कोई गणना नहीं हुई।",
            "invalidDate": "दिनांक DD-MM-YYYY प्रारूप में दर्ज करें।",
            "computing": "गणना हो रही है…",
            "parseFail": "प्रतिक्रिया पार्स नहीं हुई।",
            "engineErr": "इंजन त्रुटि (%1)।",
            "searchErr": "शहर खोज विफल (%1)।",
            "house": "भाव",
            "sign": "राशि",
            "deg": "अंश",
            "retro": "वक्री",
            "when": "दिनांक",
            "severity": "गंभीरता"
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

    function severityColor(code) {
        switch (code) {
        case "high": return "#e74c3c";
        case "medium": return "#e67e22";
        case "low": return "#3498db";
        default: return "#bdc3c7";
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
        return [String(d).padStart(2, '0'), String(mo).padStart(2, '0'), y];
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

    function formatDeg(d) {
        if (d === undefined || d === null || isNaN(d)) return "--";
        var deg = Math.floor(d);
        var mn = Math.round((d - deg) * 60);
        if (mn === 60) { mn = 0; deg += 1; }
        return `${deg}\u00B0${String(mn).padStart(2, '0')}\u2032`;
    }

    function compute() {
        var birth = parseDateStr(birthDateField.text);
        var transit = parseDateStr(transitDateField.text);
        if (!birth) {
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
        var birthISO = `${birth[0]}-${birth[1]}-${birth[2]}`;
        var transitStr = transit ? `${transit[0]}-${transit[1]}-${transit[2]}` : "";
        var q = `date=${birthISO}` +
                `&hour=${hourSpin.value}&minute=${minuteSpin.value}` +
                `&lat=${lat}&lon=${lon}&alt=${alt}&tz=${tz}` +
                `&lang=${encodeURIComponent(langKey())}` +
                `&ayanamsa=${ayanamsaCombo.currentValue}` +
                (transitStr ? `&transit_date=${transitStr}` : "");
        statusMessage.type = Kirigami.MessageType.Information;
        statusMessage.text = txt("computing");
        statusMessage.visible = true;
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/gochara?" + q, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    view.result = data.gochara || data;
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
        };
        xhr.send();
    }

    function populate() {
        var g = view.result;
        if (!g || !g.transits) return;

        var rows = [];
        for (var i = 0; i < g.transits.length; i++) {
            var t = g.transits[i];
            rows.push({
                name: t.name,
                sign: rashiName(t.rashi),
                house: t.house,
                degree: formatDeg(t.degree_in_sign),
                retro: t.retrograde,
                dignity: t.dignity || "--"
            });
        }
        view.transitRows = rows;

        var yRows = [];
        var yogas = g.special_yogas || [];
        for (var y = 0; y < yogas.length; y++) {
            yRows.push({
                name: yogas[y].name,
                severity: yogas[y].severity,
                color: severityColor(yogas[y].severity),
                description: yogas[y].description || "--"
            });
        }
        view.yogaRows = yRows;

        var scRows = [];
        var changes = g.next_sign_changes || [];
        for (var c = 0; c < changes.length; c++) {
            scRows.push({
                graha: changes[c].graha,
                fromRashi: rashiNameStr(changes[c].from_rashi),
                toRashi: rashiNameStr(changes[c].to_rashi),
                when: changes[c].date
            });
        }
        view.signChangeRows = scRows;
    }

    function rashiNameStr(enName) {
        if (!enName) return "--";
        var idx = view.rashisEn.indexOf(enName);
        return idx >= 0 ? rashiName(idx) : enName;
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
                id: birthDateField
                placeholderText: "DD-MM-YYYY"
                text: view.todayStr()
                Layout.preferredWidth: Kirigami.Units.gridUnit * 8
                validator: RegularExpressionValidator { regularExpression: /^\d{2}-\d{2}-\d{4}$/ }
            }

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

            Button {
                text: view.txt("compute")
                icon.name: "view-refresh"
                onClicked: view.compute()
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            Label {
                text: view.txt("transitDate")
                opacity: 0.7
            }
            TextField {
                id: transitDateField
                placeholderText: "DD-MM-YYYY"
                text: view.todayStr()
                Layout.fillWidth: true
                validator: RegularExpressionValidator { regularExpression: /^\d{2}-\d{2}-\d{4}$/ }
                onAccepted: view.compute()
            }
        }

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
                    { "text": "Sayana (Tropical)", "value": "sayana" },
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
                width: parent.width - Kirigami.Units.largeSpacing
                spacing: Kirigami.Units.largeSpacing
                anchors.margins: Kirigami.Units.largeSpacing

                Label {
                    text: view.txt("noChart")
                    visible: view.transitRows.length === 0 && view.yogaRows.length === 0
                    opacity: 0.6
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }

                // Transiting grahas
                Kirigami.Card {
                    Layout.fillWidth: true
                    visible: view.transitRows.length > 0

                    header: RowLayout {
                        Layout.margins: Kirigami.Units.largeSpacing
                        spacing: Kirigami.Units.smallSpacing
                        Kirigami.Icon { source: "planets" }
                        Kirigami.Heading { text: view.txt("nineGrahas"); level: 4 }
                    }

                    contentItem: ColumnLayout {
                        spacing: 2
                        Repeater {
                            model: view.transitRows
                            delegate: RowLayout {
                                Layout.fillWidth: true
                                spacing: Kirigami.Units.smallSpacing

                                Label {
                                    text: modelData.name
                                    font.bold: true
                                    Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                                }
                                Label {
                                    text: modelData.retro ? "● " + view.txt("retro") : ""
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                    color: modelData.retro ? "#e74c3c" : "transparent"
                                    Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                                }
                                Label {
                                    text: modelData.sign
                                    opacity: 0.9
                                    Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                                }
                                Label {
                                    text: view.txt("house") + " " + modelData.house
                                    opacity: 0.7
                                    Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                                }
                                Label {
                                    text: modelData.degree
                                    opacity: 0.6
                                    Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                                }
                                Label {
                                    text: modelData.dignity
                                    opacity: 0.7
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }
                }

                // Special yogas
                Kirigami.Card {
                    Layout.fillWidth: true
                    visible: view.result !== null

                    header: RowLayout {
                        Layout.margins: Kirigami.Units.largeSpacing
                        spacing: Kirigami.Units.smallSpacing
                        Kirigami.Icon { source: "favorite" }
                        Kirigami.Heading { text: view.txt("transitYogas"); level: 4 }
                    }

                    contentItem: ColumnLayout {
                        spacing: 2
                        Label {
                            text: view.txt("noneYoga")
                            visible: view.yogaRows.length === 0
                            opacity: 0.6
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                        Repeater {
                            model: view.yogaRows
                            delegate: ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: Kirigami.Units.smallSpacing
                                    Rectangle {
                                        width: 10
                                        height: 10
                                        radius: 5
                                        color: modelData.color
                                    }
                                    Label {
                                        text: modelData.name
                                        font.bold: true
                                    }
                                    Label {
                                        text: modelData.severity
                                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                        opacity: 0.6
                                    }
                                }
                                Label {
                                    text: modelData.description
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                    opacity: 0.75
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }
                }

                // Next sign changes
                Kirigami.Card {
                    Layout.fillWidth: true
                    visible: view.result !== null

                    header: RowLayout {
                        Layout.margins: Kirigami.Units.largeSpacing
                        spacing: Kirigami.Units.smallSpacing
                        Kirigami.Icon { source: "arrow-right" }
                        Kirigami.Heading { text: view.txt("signChanges"); level: 4 }
                    }

                    contentItem: ColumnLayout {
                        spacing: 2
                        Label {
                            text: view.txt("noneChange")
                            visible: view.signChangeRows.length === 0
                            opacity: 0.6
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Kirigami.Units.smallSpacing
                            Repeater {
                                model: view.signChangeRows
                                delegate: RowLayout {
                                    Layout.fillWidth: true
                                    spacing: Kirigami.Units.smallSpacing
                                    Label {
                                        text: modelData.graha
                                        font.bold: true
                                        Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                                    }
                                    Label {
                                        text: modelData.fromRashi + " → " + modelData.toRashi
                                        opacity: 0.9
                                        Layout.preferredWidth: Kirigami.Units.gridUnit * 8
                                    }
                                    Label {
                                        text: modelData.when
                                        opacity: 0.7
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

    Component.onCompleted: view.compute()
}