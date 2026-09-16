import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: view
    implicitWidth: 440
    implicitHeight: 540

    property var result: null

    readonly property var uiTxt: ({
        "en": {
            "title": "Ashtakoota Guna Milan",
            "bride": "Bride",
            "groom": "Groom",
            "birthPlaceholder": "Birth date DD-MM-YYYY",
            "compute": "Compute Compatibility",
            "invalidBoth": "Enter both dates as DD-MM-YYYY.",
            "computing": "Computing…",
            "parseFail": "Failed to parse response.",
            "engineErr": "Engine error (%1). Is the daemon running?",
            "nadiDosha": "Nadi Dosha:",
            "bhakootDosha": "Bhakoot Dosha:",
            "present": "present",
            "none": "none",
            "cancelled": "cancelled"
        },
        "devanagari": {
            "title": "अष्टकूट गुण मिलन",
            "bride": "वधू",
            "groom": "वर",
            "birthPlaceholder": "जन्म दिनांक DD-MM-YYYY",
            "compute": "अनुकूलता गणना करें",
            "invalidBoth": "दोनों दिनांक DD-MM-YYYY प्रारूप में दर्ज करें।",
            "computing": "गणना हो रही है…",
            "parseFail": "प्रतिक्रिया पार्स नहीं हुई।",
            "engineErr": "इंजन त्रुटि (%1)। क्या डेमॉन चल रहा है?",
            "nadiDosha": "नाड़ी दोष:",
            "bhakootDosha": "भकूट दोष:",
            "present": "विद्यमान",
            "none": "नहीं",
            "cancelled": "शांत"
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

    function personFrom(fields) {
        var p = parseDateStr(fields.date.text);
        if (!p) return null;
        return {
            year: p[0],
            month: p[1],
            day: p[2],
            hour: fields.hour.value,
            minute: fields.minute.value,
            tz: parseFloat(fields.tz.text)
        };
    }

    function verdictColor() {
        if (!view.result) return "#888888";
        var t = view.result.total;
        if (t >= 24) return "#2ecc71";
        if (t >= 18) return "#f1c40f";
        if (t >= 9) return "#e67e22";
        return "#e74c3c";
    }

    function compute() {
        var bride = personFrom(brideBox);
        var groom = personFrom(groomBox);
        if (!bride || !groom) {
            statusMessage.type = Kirigami.MessageType.Error;
            statusMessage.text = txt("invalidBoth");
            statusMessage.visible = true;
            return;
        }
        var body = JSON.stringify({ bride: bride, groom: groom });
        statusMessage.type = Kirigami.MessageType.Information;
        statusMessage.text = txt("computing");
        statusMessage.visible = true;

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "http://127.0.0.1:8642/ashtakoota?lang=" + encodeURIComponent(langKey()), true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    try {
                        view.result = JSON.parse(xhr.responseText);
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
        xhr.send(body);
    }

    function personFormHeader(name, color) {
        return name;
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Kirigami.Units.smallSpacing

        Kirigami.Heading {
            text: view.txt("title")
            level: 4
        }

        // Bride form
        Kirigami.Card {
            Layout.fillWidth: true

            header: Label {
                text: view.txt("bride")
                font.bold: true
                color: "#cf6a6a"
                Layout.margins: Kirigami.Units.smallSpacing
            }

            contentItem: ColumnLayout {
                id: brideBox
                spacing: 4

                TextField {
                    Layout.fillWidth: true
                    placeholderText: view.txt("birthPlaceholder")
                    text: "15-06-1990"
                    validator: RegularExpressionValidator { regularExpression: /^\d{2}-\d{2}-\d{4}$/ }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 6

                    SpinBox {
                        id: brideHour
                        from: 0
                        to: 23
                        value: 10
                        editable: true
                        textFromValue: function(v) { return v + i18n("h"); }
                        Layout.fillWidth: true
                    }
                    SpinBox {
                        from: 0
                        to: 59
                        value: 30
                        editable: true
                        textFromValue: function(v) { return v + i18n("m"); }
                        Layout.fillWidth: true
                    }
                    TextField {
                        id: brideTz
                        text: String(plasmoid.configuration.timezone)
                        validator: DoubleValidator { bottom: -12.0; top: 14.0 }
                        Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                    }
                }
            }
        }

        // Groom form
        Kirigami.Card {
            Layout.fillWidth: true

            header: Label {
                text: view.txt("groom")
                font.bold: true
                color: "#6a8fcf"
                Layout.margins: Kirigami.Units.smallSpacing
            }

            contentItem: ColumnLayout {
                id: groomBox
                spacing: 4

                TextField {
                    Layout.fillWidth: true
                    placeholderText: view.txt("birthPlaceholder")
                    text: "08-03-1992"
                    validator: RegularExpressionValidator { regularExpression: /^\d{2}-\d{2}-\d{4}$/ }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 6

                    SpinBox {
                        id: groomHour
                        from: 0
                        to: 23
                        value: 16
                        editable: true
                        textFromValue: function(v) { return v + i18n("h"); }
                        Layout.fillWidth: true
                    }
                    SpinBox {
                        from: 0
                        to: 59
                        value: 45
                        editable: true
                        textFromValue: function(v) { return v + i18n("m"); }
                        Layout.fillWidth: true
                    }
                    TextField {
                        id: groomTz
                        text: String(plasmoid.configuration.timezone)
                        validator: DoubleValidator { bottom: -12.0; top: 14.0 }
                        Layout.preferredWidth: Kirigami.Units.gridUnit * 4
                    }
                }
            }
        }

        Button {
            text: view.txt("compute")
            icon.name: "favorite"
            Layout.alignment: Qt.AlignHCenter
            onClicked: view.compute()
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

                // Result summary
                RowLayout {
                    visible: view.result !== null
                    Layout.fillWidth: true

                    Label {
                        text: view.result ? `${view.result.total.toFixed(1)} / ${view.result.max}` : ""
                        font.bold: true
                        font.pixelSize: Kirigami.Units.gridUnit * 1.6
                        color: view.verdictColor()
                    }

                    Label {
                        text: view.result ? view.result.verdict : ""
                        font.bold: true
                        font.pixelSize: Kirigami.Units.gridUnit * 1.1
                        Layout.fillWidth: true
                        color: view.verdictColor()
                    }
                }

                // Dosha flags
                ColumnLayout {
                    visible: view.result !== null
                    Layout.fillWidth: true
                    spacing: 2

                    Label {
                        text: `${view.txt("nadiDosha")} ${view.result ? (view.result.doshas.nadi_dosha ? "⚠ " + view.txt("present") : view.txt("none")) : ""}` +
                              (view.result && view.result.doshas.nadi_dosha_cancelled ? ` (${view.txt("cancelled")})` : "")
                        color: view.result && view.result.doshas.nadi_dosha && !view.result.doshas.nadi_dosha_cancelled ? "#e74c3c" : "#888888"
                    }
                    Label {
                        text: `${view.txt("bhakootDosha")} ${view.result ? (view.result.doshas.bhakoot_dosha ? "⚠ " + view.txt("present") : view.txt("none")) : ""}` +
                              (view.result && view.result.doshas.bhakoot_dosha_cancelled ? ` (${view.txt("cancelled")})` : "")
                        color: view.result && view.result.doshas.bhakoot_dosha && !view.result.doshas.bhakoot_dosha_cancelled ? "#e74c3c" : "#888888"
                    }
                }

                Kirigami.Separator { Layout.fillWidth: true; visible: view.result !== null }

                // Kootas
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    visible: view.result !== null

                    Repeater {
                        model: view.result ? view.result.kootas : []

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 1

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 6

                                Label {
                                    text: modelData.name
                                    font.bold: true
                                    Layout.preferredWidth: Kirigami.Units.gridUnit * 5
                                }

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 4
                                    radius: 2
                                    color: "#333333"

                                    Rectangle {
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: parent.width * Math.max(0, Math.min(1, modelData.score / modelData.max))
                                        height: 4
                                        radius: 2
                                        color: modelData.score === modelData.max ? "#2ecc71" : (modelData.score === 0 ? "#e74c3c" : "#f1c40f")
                                    }
                                }

                                Label {
                                    text: `${modelData.score.toFixed(1)}/${modelData.max}`
                                    font.bold: true
                                    Layout.preferredWidth: Kirigami.Units.gridUnit * 5
                                    horizontalAlignment: Text.AlignRight
                                }
                            }

                            Label {
                                text: modelData.detail && modelData.detail.note ? modelData.detail.note : ""
                                opacity: 0.7
                                font.pixelSize: Kirigami.Units.gridUnit * 0.7
                                wrapMode: Text.WordWrap
                                Layout.fillWidth: true
                                Layout.leftMargin: Kirigami.Units.gridUnit * 5
                            }
                        }
                    }
                }
            }
        }
    }
}