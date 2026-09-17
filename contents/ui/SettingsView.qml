import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: view
    implicitWidth: 520
    implicitHeight: 640

    property var cityChoices: []
    property var configData: null
    property string cityName: ""

    readonly property var uiTxt: ({
        "en": {
            "title": "Settings & Location",
            "location": "Location",
            "searchPlaceholder": "Search city…",
            "searchBtn": "Find",
            "saveCity": "Save City",
            "city": "City",
            "lat": "Lat",
            "lon": "Lon",
            "alt": "Alt (m)",
            "tzh": "TZ (h)",
            "preferences": "Calendar Preferences",
            "lang": "Language",
            "ayanamsa": "Ayanamsa",
            "calendar": "Calendar",
            "month": "Month",
            "festival": "Festival Rule",
            "tithiMode": "Tithi Mode",
            "apply": "Apply",
            "refresh": "Reload",
            "loading": "Loading…",
            "appliedMsg": "Settings applied.",
            "savedMsg": "City saved.",
            "engineErr": "Engine error (%1). Is the daemon running?",
            "saveErr": "Could not save city (%1).",
            "langNames": "English,IAST,Devanagari",
            "calendarOptions": "Shalivahana Shaka,Vikram Samvat,Saura,Vikram Kartak",
            "monthOptions": "Amavasyanta (new-moon month),Purnimanta (full-moon month)",
            "festivalOptions": "Vaishnava (Haridasa),Smarta (Sankranti-gate)",
            "tithiOptions": "Traditional (sunrise anchor),Mean (midpoint anchor)",
            "applyHint": "Apply updates the widget and refreshes all panels."
        },
        "iast": {
            "title": "Sthiti–Sanracanā",
            "location": "Sthāna",
            "searchPlaceholder": "Nagara khojeṁ…",
            "searchBtn": "Khojeṁ",
            "saveCity": "Nagara rakṣet",
            "city": "Nagara",
            "lat": "Akṣāṁśa",
            "lon": "Reṣāṁśa",
            "alt": "Ucchtā (m)",
            "tzh": "Samaya (h)",
            "preferences": "Pāṭhya-niyamāḥ",
            "lang": "Bhāṣā",
            "ayanamsa": "Ayanāṁśa",
            "calendar": "Pañcāṅga",
            "month": "Māsa",
            "festival": "Utsava-niyama",
            "tithiMode": "Tithi-rītiḥ",
            "apply": "Āpārayatu",
            "refresh": "Punar-bhāraya",
            "loading": "Pūraṇaṁ…",
            "appliedMsg": "Niyamāḥ sthāpitāḥ.",
            "savedMsg": "Nagara rakṣitaṁ.",
            "engineErr": "Yantra-truṭi (%1).",
            "saveErr": "Nagara na rakṣitam (%1).",
            "langNames": "English,IAST,Devanāgarī",
            "calendarOptions": "Śālivāhana Śaka,Vikram Samvat,Saura,Vikram Kartak",
            "monthOptions": "Amāvāsyānta, Pūrṇimānta",
            "festivalOptions": "Vaiṣṇava, Smārta",
            "tithiOptions": "Udaya-mūla, Madhya-mūla",
            "applyHint": "Āpārya sarvāṇi pañcāṅgāni nūtanī-karoti."
        },
        "devanagari": {
            "title": "सेटिंग्स एवं स्थान",
            "location": "स्थान",
            "searchPlaceholder": "शहर खोजें…",
            "searchBtn": "खोजें",
            "saveCity": "शहर सहेजें",
            "city": "शहर",
            "lat": "अक्षांश",
            "lon": "रेखांश",
            "alt": "ऊँचाई (मी)",
            "tzh": "समय (घं)",
            "preferences": "कैलेंडर वरीयता",
            "lang": "भाषा",
            "ayanamsa": "अयनांश",
            "calendar": "कैलेंडर",
            "month": "मास",
            "festival": "त्योहार नियम",
            "tithiMode": "तिथि पद्धति",
            "apply": "लागू करें",
            "refresh": "पुनः लोड",
            "loading": "लोड हो रहा है…",
            "appliedMsg": "सेटिंग्स लागू की गईं।",
            "savedMsg": "शहर सहेजा गया।",
            "engineErr": "इंजन त्रुटि (%1)।",
            "saveErr": "शहर सहेजा नहीं गया (%1)।",
            "langNames": "अंग्रेज़ी,IAST,देवनागरी",
            "calendarOptions": "शालिवाहन शक,विक्रम संवत,सौर,विक्रम कार्तिक",
            "monthOptions": "अमान्त (अमावस्या अंत),पूर्णिमान्त (पूर्णिमा अंत)",
            "festivalOptions": "वैष्णव (हरिदास),स्मार्त (संक्रांति-द्वार)",
            "tithiOptions": "परंपरागत (सूर्योदय आधार),मध्य (मध्य बिंदु आधार)",
            "applyHint": "लागू करने से सभी पटल ताज़ा हो जाते हैं।"
        }
    })

    function langKey() {
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

    function fetchUrl(url, onOk, onErr) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642" + url, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200) {
                try {
                    onOk(JSON.parse(xhr.responseText));
                    return;
                } catch (e) {}
            }
            if (onErr) onErr(xhr.status);
        };
        xhr.send();
    }

    function loadConfig() {
        fetchUrl("/config", function(d) {
            view.configData = d;
            if (d.city) cityName = d.city;
            else if (!cityField.text.trim()) cityName = (typeof plasmoid !== "undefined" && plasmoid.configuration && plasmoid.configuration.cityName) ? plasmoid.configuration.cityName : "";
            if (d.lat !== undefined) latField.text = String(Number(d.lat).toFixed(4));
            if (d.lon !== undefined) lonField.text = String(Number(d.lon).toFixed(4));
            if (d.alt !== undefined) altField.text = String(Number(d.alt).toFixed(1));
            if (d.tz !== undefined) tzField.text = String(Number(d.tz).toFixed(1));
            setCombo(langCombo, d.lang || "en");
            setCombo(calCombo, d.calendar_system || "shaka");
            setCombo(monthCombo, d.month_system || "amavasyanta");
            setCombo(festCombo, d.festival_rule || "vaishnava");
            setCombo(tithiCombo, d.tithi_mode || "traditional");
            setCombo(ayanCombo, d.ayanamsa || "lahiri");
        }, function(code) {
            statusMessage.type = Kirigami.MessageType.Error;
            statusMessage.text = txt("engineErr").arg(code);
            statusMessage.visible = true;
        });
    }

    function setCombo(combo, value) {
        var i = combo.indexOfValue(value);
        combo.currentIndex = i >= 0 ? i : 0;
    }

    function comboValue(combo, dflt) {
        return combo.currentIndex >= 0 ? combo.model[combo.currentIndex].value : dflt;
    }

    function searchCities() {
        var q = cityField.text.trim();
        if (!q) return;
        fetchUrl("/search_city?q=" + encodeURIComponent(q), function(list) {
            view.cityChoices = list || [];
            cityCombo.model = view.cityChoices.map(function(c) { return c.name; });
            if (view.cityChoices.length > 0) { cityCombo.currentIndex = 0; applyCityChoice(0); }
        }, function(code) {
            statusMessage.type = Kirigami.MessageType.Error;
            statusMessage.text = txt("engineErr").arg(code);
            statusMessage.visible = true;
        });
    }

    function applyCityChoice(i) {
        var c = view.cityChoices[i];
        if (!c) return;
        cityName = c.name;
        cityField.text = c.name;
        latField.text = String(Number(c.lat).toFixed(4));
        lonField.text = String(Number(c.lon).toFixed(4));
        altField.text = String(Number(c.alt || 0).toFixed(1));
        tzField.text = String(Number(c.tz || 0).toFixed(1));
    }

    function saveCity() {
        var name = cityField.text.trim() || cityName.trim();
        if (!name) return;
        var q = "name=" + encodeURIComponent(name) +
                "&lat=" + encodeURIComponent(parseFloat(latField.text) || 0) +
                "&lon=" + encodeURIComponent(parseFloat(lonField.text) || 0) +
                "&tz=" + encodeURIComponent(parseFloat(tzField.text) || 0) +
                "&alt=" + encodeURIComponent(parseFloat(altField.text) || 0);
        fetchUrl("/save_custom_city?" + q, function() {
            cityName = name;
            if (typeof plasmoid !== "undefined" && plasmoid.configuration && plasmoid.configuration.cityName !== undefined)
                plasmoid.configuration.cityName = name;
            statusMessage.type = Kirigami.MessageType.Positive;
            statusMessage.text = txt("savedMsg");
            statusMessage.visible = true;
        }, function(code) {
            statusMessage.type = Kirigami.MessageType.Error;
            statusMessage.text = txt("saveErr").arg(code);
            statusMessage.visible = true;
        });
    }

    function apply() {
        if (typeof plasmoid !== "undefined" && plasmoid.configuration) {
            try {
                plasmaVarConfig(true);
            } catch (e) {}
        }
        statusMessage.type = Kirigami.MessageType.Positive;
        statusMessage.text = txt("appliedMsg");
        statusMessage.visible = true;
        if (typeof reloadAll === "function") Qt.callLater(reloadAll);
    }

    function plasmaVarConfig(write) {
        var cfg = plasmoid.configuration;
        if (cfg.cityName !== undefined) cfg.cityName = cityName.trim();
        cfg.latitude = parseFloat(latField.text) || 0;
        cfg.longitude = parseFloat(lonField.text) || 0;
        cfg.altitude = parseFloat(altField.text) || 0;
        cfg.timezone = parseFloat(tzField.text) || 0;
        cfg.lang = comboValue(langCombo, "en");
        cfg.ayanamsa = comboValue(ayanCombo, "lahiri");
        if (cfg.calendarSystem !== undefined) cfg.calendarSystem = comboValue(calCombo, "shaka");
        if (cfg.monthSystem !== undefined) cfg.monthSystem = comboValue(monthCombo, "amavasyanta");
        if (cfg.festivalRule !== undefined) cfg.festivalRule = comboValue(festCombo, "vaishnava");
        if (cfg.tithiMode !== undefined) cfg.tithiMode = comboValue(tithiCombo, "traditional");
    }

    // ---- Combo model helpers ----
    function comboModelFrom(values, titles) {
        var out = [];
        for (var i = 0; i < values.length; i++) out.push({ value: values[i], text: titles[i] });
        return out;
    }

    ScrollView {
        anchors.fill: parent
        clip: true
        ScrollBar.vertical.policy: ScrollBar.AsNeeded

        ColumnLayout {
            width: parent.width
            spacing: Kirigami.Units.smallSpacing

            Kirigami.Heading { text: view.txt("title"); level: 4 }

            Kirigami.Separator { Layout.fillWidth: true }
            Kirigami.Heading { text: view.txt("location"); level: 5 }

            RowLayout {
                Layout.fillWidth: true; spacing: Kirigami.Units.smallSpacing
                TextField {
                    id: cityField
                    Layout.fillWidth: true
                    placeholderText: view.cfg("cityName", "") || (view.configData && view.configData.city) || view.txt("searchPlaceholder")
                    onAccepted: view.searchCities()
                }
                Button { text: view.txt("searchBtn"); icon.name: "edit-find"; onClicked: view.searchCities() }
                ComboBox { id: cityCombo; Layout.preferredWidth: Kirigami.Units.gridUnit * 8; onActivated: view.applyCityChoice(currentIndex) }
                Button { text: view.txt("saveCity"); icon.name: "document-save"; onClicked: view.saveCity() }
            }

            RowLayout {
                Layout.fillWidth: true; spacing: Kirigami.Units.smallSpacing
                TextField { id: latField; placeholderText: view.txt("lat"); text: String(Number(view.cfg("latitude", 23.1765)).toFixed(4)); Layout.preferredWidth: Kirigami.Units.gridUnit * 4; validator: DoubleValidator { bottom: -90; top: 90; decimals: 4 } }
                TextField { id: lonField; placeholderText: view.txt("lon"); text: String(Number(view.cfg("longitude", 75.7885)).toFixed(4)); Layout.preferredWidth: Kirigami.Units.gridUnit * 4; validator: DoubleValidator { bottom: -180; top: 180; decimals: 4 } }
                TextField { id: altField; placeholderText: view.txt("alt"); text: String(Number(view.cfg("altitude", 0)).toFixed(1)); Layout.preferredWidth: Kirigami.Units.gridUnit * 3; validator: DoubleValidator { bottom: -500; top: 9000; decimals: 1 } }
                TextField { id: tzField; placeholderText: view.txt("tzh"); text: String(Number(view.cfg("timezone", 5.5)).toFixed(1)); Layout.preferredWidth: Kirigami.Units.gridUnit * 3; validator: DoubleValidator { bottom: -12; top: 14; decimals: 2 } }
            }

            Kirigami.Separator { Layout.fillWidth: true }
            Kirigami.Heading { text: view.txt("preferences"); level: 5 }

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                columnSpacing: Kirigami.Units.largeSpacing
                rowSpacing: Kirigami.Units.smallSpacing

                Label { text: view.txt("lang") }
                ComboBox {
                    id: langCombo
                    Layout.preferredWidth: Kirigami.Units.gridUnit * 12
                    model: view.comboModelFrom(["en", "iast", "devanagari"], view.txt("langNames").split(","))
                    currentIndex: {
                        var want = view.langKey();
                        var m = model;
                        for (var i = 0; i < m.length; i++) if (m[i].value === want) return i;
                        return 0;
                    }
                    textRole: "text"; valueRole: "value"
                }

                Label { text: view.txt("ayanamsa") }
                ComboBox { id: ayanCombo; Layout.preferredWidth: Kirigami.Units.gridUnit * 12; model: view.comboModelFrom(["lahiri", "raman", "krishnamurti", "true_citra", "fagan_bradley", "deluce"], ["Lahiri", "Raman", "Krishnamurti", "True Citra", "Fagan-Bradley", "DeLuce"]); currentIndex: 0; textRole: "text"; valueRole: "value" }

                Label { text: view.txt("calendar") }
                ComboBox { id: calCombo; Layout.preferredWidth: Kirigami.Units.gridUnit * 12; model: view.comboModelFrom(["shaka", "vikram", "saura", "kartak"], view.txt("calendarOptions").split(",")); currentIndex: 0; textRole: "text"; valueRole: "value" }

                Label { text: view.txt("month") }
                ComboBox { id: monthCombo; Layout.preferredWidth: Kirigami.Units.gridUnit * 14; model: view.comboModelFrom(["amavasyanta", "purnimanta"], view.txt("monthOptions").split(",")); currentIndex: 0; textRole: "text"; valueRole: "value" }

                Label { text: view.txt("festival") }
                ComboBox { id: festCombo; Layout.preferredWidth: Kirigami.Units.gridUnit * 14; model: view.comboModelFrom(["vaishnava", "smarta"], view.txt("festivalOptions").split(",")); currentIndex: 0; textRole: "text"; valueRole: "value" }

                Label { text: view.txt("tithiMode") }
                ComboBox { id: tithiCombo; Layout.preferredWidth: Kirigami.Units.gridUnit * 14; model: view.comboModelFrom(["traditional", "mean"], view.txt("tithiOptions").split(",")); currentIndex: 0; textRole: "text"; valueRole: "value" }
            }

            Kirigami.InlineMessage { id: statusMessage; Layout.fillWidth: true; type: Kirigami.MessageType.Warning; visible: false }

            Label { text: view.txt("applyHint"); Layout.fillWidth: true; wrapMode: Text.WordWrap; opacity: 0.6; font.pixelSize: Kirigami.Units.gridUnit * 0.75 }

            RowLayout {
                Layout.fillWidth: true; spacing: Kirigami.Units.smallSpacing
                Button { text: view.txt("apply"); icon.name: "dialog-ok"; onClicked: view.apply() }
                Button { text: view.txt("refresh"); icon.name: "view-refresh"; flat: true; onClicked: view.loadConfig() }
            }

            Item { Layout.fillHeight: true }
        }
    }

    Component.onCompleted: view.loadConfig()
}