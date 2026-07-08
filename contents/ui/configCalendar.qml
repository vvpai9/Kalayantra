import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: page
    implicitWidth: 600
    implicitHeight: 450

    // Custom bindings to config keys using cfg_ prefix
    property string cfg_calendarSystem
    property string cfg_monthSystem
    property string cfg_festivalRule
    property string cfg_tithiMode

    ScrollView {
        anchors.fill: parent
        clip: true
        ScrollBar.horizontal.policy: ScrollBar.AsNeeded
        ScrollBar.vertical.policy: ScrollBar.AsNeeded

        ColumnLayout {
            width: parent.width - Kirigami.Units.gridUnit
            spacing: Kirigami.Units.largeSpacing
            anchors.margins: Kirigami.Units.largeSpacing

            // Card 1: Lunisolar Calculation Systems
            Kirigami.Card {
                Layout.fillWidth: true

                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing

                    Kirigami.Icon {
                        source: "office-calendar"
                        implicitWidth: Kirigami.Units.gridUnit * 1.5
                        implicitHeight: Kirigami.Units.gridUnit * 1.5
                    }

                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading {
                            text: i18n("Lunisolar Calculation Systems")
                            level: 3
                        }
                        Label {
                            text: i18n("Configure traditional year systems and lunar month starting boundaries.")
                            font.pixelSize: Kirigami.Units.gridUnit * 0.75
                            opacity: 0.6
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }

                contentItem: Kirigami.FormLayout {
                    Layout.fillWidth: true

                    ComboBox {
                        id: calCombo
                        Kirigami.FormData.label: i18n("Calendar Era:")
                        textRole: "text"
                        valueRole: "value"
                        Layout.fillWidth: true
                        model: [
                            {"text": i18n("Shalivahana Shaka (Saka Samvat)"), "value": "shaka"},
                            {"text": i18n("Vikram Samvat (Chaitradi)"), "value": "vikram"},
                            {"text": i18n("Vikram Kartak (Kartikadi)"), "value": "kartak"},
                            {"text": i18n("Solar Calendar (Saura)"), "value": "saura"}
                        ]
                        onActivated: {
                            page.cfg_calendarSystem = currentValue;
                        }
                        Component.onCompleted: {
                            currentIndex = indexOfValue(page.cfg_calendarSystem);
                        }
                        Connections {
                            target: page
                            function onCfg_calendarSystemChanged() {
                                calCombo.currentIndex = calCombo.indexOfValue(page.cfg_calendarSystem);
                            }
                        }
                        Accessible.name: i18n("Calendar Era")
                        Accessible.description: i18n("Select traditional era system (Shaka/Vikram/Saura)")
                    }

                    ComboBox {
                        id: monthCombo
                        Kirigami.FormData.label: i18n("Month Boundary:")
                        textRole: "text"
                        valueRole: "value"
                        Layout.fillWidth: true
                        model: [
                            {"text": i18n("Amavasyanta (New Moon to New Moon)"), "value": "amavasyanta"},
                            {"text": i18n("Purnimanta (Full Moon to Full Moon)"), "value": "purnimanta"}
                        ]
                        onActivated: {
                            page.cfg_monthSystem = currentValue;
                        }
                        Component.onCompleted: {
                            currentIndex = indexOfValue(page.cfg_monthSystem);
                        }
                        Connections {
                            target: page
                            function onCfg_monthSystemChanged() {
                                monthCombo.currentIndex = monthCombo.indexOfValue(page.cfg_monthSystem);
                            }
                        }
                        Accessible.name: i18n("Month Boundary System")
                        Accessible.description: i18n("Choose month start/end boundary system (Amavasyanta or Purnimanta)")
                    }
                }
            }

            // Card 2: Ritual Rules & Real-time Transitions
            Kirigami.Card {
                Layout.fillWidth: true

                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing

                    Kirigami.Icon {
                        source: "history"
                        implicitWidth: Kirigami.Units.gridUnit * 1.5
                        implicitHeight: Kirigami.Units.gridUnit * 1.5
                    }

                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading {
                            text: i18n("Ritual Rules & Real-time Transitions")
                            level: 3
                        }
                        Label {
                            text: i18n("Select sectarian calculations for observances and choose static or live transition times.")
                            font.pixelSize: Kirigami.Units.gridUnit * 0.75
                            opacity: 0.6
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }

                contentItem: Kirigami.FormLayout {
                    Layout.fillWidth: true

                    ComboBox {
                        id: festCombo
                        Kirigami.FormData.label: i18n("Sectarian Festival Rules:")
                        textRole: "text"
                        valueRole: "value"
                        Layout.fillWidth: true
                        model: [
                            {"text": i18n("Vaishnava (Default, Ekadashi rules)"), "value": "vaishnava"},
                            {"text": i18n("Smarta"), "value": "smarta"}
                        ]
                        onActivated: {
                            page.cfg_festivalRule = currentValue;
                        }
                        Component.onCompleted: {
                            currentIndex = indexOfValue(page.cfg_festivalRule);
                        }
                        Connections {
                            target: page
                            function onCfg_festivalRuleChanged() {
                                festCombo.currentIndex = festCombo.indexOfValue(page.cfg_festivalRule);
                            }
                        }
                        Accessible.name: i18n("Sectarian Festival Rules")
                        Accessible.description: i18n("Select ritual system parameters (Vaishnava or Smarta)")
                    }

                    ComboBox {
                        id: tithiCombo
                        Kirigami.FormData.label: i18n("Tithi Display Mode:")
                        textRole: "text"
                        valueRole: "value"
                        Layout.fillWidth: true
                        model: [
                            {"text": i18n("Traditional Mode (Sunrise Tithi)"), "value": "traditional"},
                            {"text": i18n("Astronomical Mode (Live Transitions)"), "value": "astronomical"}
                        ]
                        onActivated: {
                            page.cfg_tithiMode = currentValue;
                        }
                        Component.onCompleted: {
                            currentIndex = indexOfValue(page.cfg_tithiMode);
                        }
                        Connections {
                            target: page
                            function onCfg_tithiModeChanged() {
                                tithiCombo.currentIndex = tithiCombo.indexOfValue(page.cfg_tithiMode);
                            }
                        }
                        Accessible.name: i18n("Tithi Display Mode")
                        Accessible.description: i18n("Toggle between traditional Sunrise tithi and real-time live transitions")
                    }
                }
            }
        }
    }
}
