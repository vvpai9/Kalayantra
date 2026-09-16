import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: view
    implicitWidth: 440
    implicitHeight: 540

    property var horaResult: null
    property var muhurtaResult: null

    readonly property var uiTxt: ({
        "en": {
            "title": "Hora & Muhurta",
            "load": "Load",
            "invalidDate": "Enter a valid date as DD-MM-YYYY.",
            "loading": "Loading…",
            "horaTab": "Hora",
            "muhurtaTab": "Muhurta",
            "vaara": "Vaara:",
            "sunrise": "Sunrise",
            "sunset": "Sunset",
            "minDay": "min day",
            "minNight": "min night",
            "pressHora": "Press Load to compute the hourly lords.",
            "dayHoras": "Day Horas",
            "nightHoras": "Night Horas",
            "abhijit": "Abhijit Muhurta:",
            "rahuKala": "Rahu Kala:",
            "yama": "Yama:",
            "gulika": "Gulika:",
            "pressMuhurta": "Press Load to compute the 30 muhurtas.",
            "dayMuhurtas": "Day Muhurtas",
            "nightMuhurtas": "Night Muhurtas",
            "abhijitStar": "★ Abhijit"
        },
        "devanagari": {
            "title": "होरा एवं मुहूर्त",
            "load": "लोड करें",
            "invalidDate": "दिनांक DD-MM-YYYY प्रारूप में दर्ज करें।",
            "loading": "लोड हो रहा है…",
            "horaTab": "होरा",
            "muhurtaTab": "मुहूर्त",
            "vaara": "वार:",
            "sunrise": "सूर्योदय",
            "sunset": "सूर्यास्त",
            "minDay": "मिनट दिन",
            "minNight": "मिनट रात",
            "pressHora": "घंटेवार स्वामी हेतु लोड दबाएँ।",
            "dayHoras": "दिन के होरा",
            "nightHoras": "रात के होरा",
            "abhijit": "अभिजित मुहूर्त:",
            "rahuKala": "राहु काल:",
            "yama": "यमघण्ट:",
            "gulika": "गुलिक:",
            "pressMuhurta": "30 मुहूर्त हेतु लोड दबाएँ।",
            "dayMuhurtas": "दिन के मुहूर्त",
            "nightMuhurtas": "रात के मुहूर्त",
            "abhijitStar": "★ अभिजित"
        }
    })

    function langKey() {
        return (typeof plasmoid !== "undefined" && plasmoid.configuration) ? plasmoid.configuration.lang : "en";
    }

    function txt(key) {
        var table = uiTxt[langKey()] || uiTxt["en"];
        return table[key] !== undefined ? table[key] : key;
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

    function natureColor(c) {
        if (c === "Auspicious" || c === "Abhijit") return "#2ecc71";
        if (c === "Inauspicious") return "#e74c3c";
        return "#f1c40f";
    }

    function natureDot(c) {
        if (c === "Auspicious" || c === "Abhijit") return "🟢";
        if (c === "Inauspicious") return "🔴";
        return "🟡";
    }

    function load() {
        var parts = parseDateStr(dateField.text);
        if (!parts) {
            statusMessage.type = Kirigami.MessageType.Error;
            statusMessage.text = txt("invalidDate");
            statusMessage.visible = true;
            return;
        }
        var q = `date=${String(parts[2]).padStart(2, '0')}-${String(parts[1]).padStart(2, '0')}-${parts[0]}` +
                `&tz=${plasmoid.configuration.timezone}` +
                `&lang=${encodeURIComponent(langKey())}`;
        statusMessage.type = Kirigami.MessageType.Information;
        statusMessage.text = txt("loading");
        statusMessage.visible = true;

        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/hora?" + q, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                try {
                    view.horaResult = JSON.parse(xhr.responseText);
                } catch (e) {}
                maybeDone();
            }
        };
        xhr.send();

        var xhr2 = new XMLHttpRequest();
        xhr2.open("GET", "http://127.0.0.1:8642/muhurta?" + q, true);
        xhr2.onreadystatechange = function() {
            if (xhr2.readyState === XMLHttpRequest.DONE && xhr2.status === 200) {
                try {
                    view.muhurtaResult = JSON.parse(xhr2.responseText);
                } catch (e) {}
                maybeDone();
            }
        };
        xhr2.send();
    }

    function maybeDone() {
        if (view.horaResult !== null && view.muhurtaResult !== null) {
            statusMessage.visible = false;
        }
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

            Button {
                text: view.txt("load")
                icon.name: "view-refresh"
                onClicked: view.load()
            }
        }

        Kirigami.InlineMessage {
            id: statusMessage
            Layout.fillWidth: true
            type: Kirigami.MessageType.Warning
            text: ""
            visible: false
        }

        TabBar {
            id: horaTabBar
            Layout.fillWidth: true

            TabButton { text: view.txt("horaTab") }
            TabButton { text: view.txt("muhurtaTab") }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            ColumnLayout {
                width: parent.width
                spacing: Kirigami.Units.smallSpacing

                // --- HORA PAGE ---
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    visible: horaTabBar.currentIndex === 0

                    Label {
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        text: view.horaResult ? `${view.txt("vaara")} <b>${view.horaResult.vaara}</b> • ${view.txt("sunrise")} ${view.horaResult.sunrise} • ${view.txt("sunset")} ${view.horaResult.sunset} • ${view.horaResult.day_length_min}${view.txt("minDay")} / ${view.horaResult.night_length_min}${view.txt("minNight")}` : view.txt("pressHora")
                        textFormat: Text.RichText
                        font.pixelSize: Kirigami.Units.gridUnit * 0.85
                    }

                    Repeater {
                        model: view.horaResult ? [
                            { "title": view.txt("dayHoras"), "list": view.horaResult.day_horas || [] },
                            { "title": view.txt("nightHoras"), "list": view.horaResult.night_horas || [] }
                        ] : []

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            Layout.topMargin: Kirigami.Units.smallSpacing

                            Label { text: modelData.title; font.bold: true }

                            Repeater {
                                model: modelData.list || []

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 6

                                    Label { text: view.natureDot(modelData.code || modelData.nature) }

                                    Label {
                                        text: modelData.lord
                                        font.bold: true
                                        Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                                    }

                                    Label {
                                        text: `${modelData.start} – ${modelData.end}`
                                        opacity: 0.9
                                        fontSizeMode: Text.HorizontalFit
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: horaTabBar.currentIndex === 0 }

                // --- MUHURTA PAGE ---
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    visible: horaTabBar.currentIndex === 1

                    Label {
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        text: view.muhurtaResult ? `${view.txt("abhijit")} <b style="color:#2ecc71;">${view.muhurtaResult.abhijit.start} – ${view.muhurtaResult.abhijit.end}</b>\n${view.txt("rahuKala")} ${view.muhurtaResult.rahu_kala}  •  ${view.txt("yama")} ${view.muhurtaResult.yamaghanta}  •  ${view.txt("gulika")} ${view.muhurtaResult.gulika}` : view.txt("pressMuhurta")
                        textFormat: Text.RichText
                        font.pixelSize: Kirigami.Units.gridUnit * 0.85
                    }

                    Repeater {
                        model: view.muhurtaResult ? [
                            { "title": view.txt("dayMuhurtas"), "list": view.muhurtaResult.day_muhurtas || [] },
                            { "title": view.txt("nightMuhurtas"), "list": view.muhurtaResult.night_muhurtas || [] }
                        ] : []

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            Layout.topMargin: Kirigami.Units.smallSpacing

                            Label { text: modelData.title; font.bold: true }

                            Repeater {
                                model: modelData.list || []

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 6
                                    Layout.topMargin: 1

                                    Label { text: view.natureDot(modelData.code || modelData.status) }

                                    Label {
                                        text: modelData.name
                                        font.bold: true
                                        Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                                    }

                                    Label {
                                        text: `${modelData.start} – ${modelData.end}`
                                        opacity: 0.9
                                        fontSizeMode: Text.HorizontalFit
                                        Layout.fillWidth: true
                                    }

                                    Label {
                                        text: modelData.abhijit ? view.txt("abhijitStar") : modelData.status
                                        color: view.natureColor(modelData.code || modelData.status)
                                        font.bold: true
                                        fontSizeMode: Text.HorizontalFit
                                        Layout.preferredWidth: Kirigami.Units.gridUnit * 6
                                        horizontalAlignment: Text.AlignRight
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