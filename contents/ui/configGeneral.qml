import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts as Layouts
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
    id: page

    // Custom bindings to config keys using cfg_ prefix
    property alias cfg_locationName: locationNameField.text
    property alias cfg_latitude: latField.text
    property alias cfg_longitude: lonField.text
    property alias cfg_altitude: altField.text
    property alias cfg_timezone: tzField.text

    property string cfg_lang
    property string cfg_calendarSystem
    property string cfg_monthSystem
    property string cfg_festivalRule
    property string cfg_tithiMode

    // Quick location presets
    property var presets: [
        {"name": "Ujjain", "lat": "23.1765", "lon": "75.7885", "tz": "5.5", "alt": "0.0"},
        {"name": "New Delhi", "lat": "28.6139", "lon": "77.2090", "tz": "5.5", "alt": "0.0"},
        {"name": "Mumbai", "lat": "19.0760", "lon": "72.8777", "tz": "5.5", "alt": "0.0"},
        {"name": "Bengaluru", "lat": "12.9716", "lon": "77.5946", "tz": "5.5", "alt": "0.0"},
        {"name": "Kolkata", "lat": "22.5726", "lon": "88.3639", "tz": "5.5", "alt": "0.0"},
        {"name": "London", "lat": "51.5074", "lon": "-0.1278", "tz": "1.0", "alt": "0.0"},
        {"name": "New York", "lat": "40.7128", "lon": "-74.0060", "tz": "-5.0", "alt": "0.0"},
        {"name": "San Francisco", "lat": "37.7749", "lon": "-122.4194", "tz": "-8.0", "alt": "0.0"}
    ]

    Controls.ComboBox {
        id: presetCombo
        Kirigami.FormData.label: i18n("City Preset:")
        model: page.presets
        textRole: "name"
        onActivated: (index) => {
            var selected = page.presets[index];
            locationNameField.text = selected.name;
            latField.text = selected.lat;
            lonField.text = selected.lon;
            tzField.text = selected.tz;
            altField.text = selected.alt;
        }
    }

    Controls.TextField {
        id: locationNameField
        Kirigami.FormData.label: i18n("Location Name:")
        placeholderText: "e.g. Ujjain"
    }

    Controls.TextField {
        id: latField
        Kirigami.FormData.label: i18n("Latitude:")
        placeholderText: "e.g. 23.1765"
    }

    Controls.TextField {
        id: lonField
        Kirigami.FormData.label: i18n("Longitude:")
        placeholderText: "e.g. 75.7885"
    }

    Controls.TextField {
        id: altField
        Kirigami.FormData.label: i18n("Altitude (m):")
        placeholderText: "e.g. 0.0"
    }

    Controls.TextField {
        id: tzField
        Kirigami.FormData.label: i18n("Timezone Offset (hours):")
        placeholderText: "e.g. 5.5 for IST"
    }

    Kirigami.Separator {
        Kirigami.FormData.isSection: true
        Kirigami.FormData.label: i18n("Calculations & View Settings")
    }

    Controls.ComboBox {
        id: langCombo
        Kirigami.FormData.label: i18n("Display Language:")
        textRole: "text"
        valueRole: "value"
        model: [
            {"text": "English", "value": "en"},
            {"text": "Sanskrit (IAST)", "value": "iast"},
            {"text": "Devanagari (Sanskrit/Hindi)", "value": "devanagari"}
        ]
        onActivated: {
            page.cfg_lang = currentValue;
        }
        Component.onCompleted: {
            currentIndex = indexOfValue(page.cfg_lang);
        }
        Connections {
            target: page
            function onCfg_langChanged() {
                langCombo.currentIndex = langCombo.indexOfValue(page.cfg_lang);
            }
        }
    }

    Controls.ComboBox {
        id: calCombo
        Kirigami.FormData.label: i18n("Calendar System:")
        textRole: "text"
        valueRole: "value"
        model: [
            {"text": "Shalivahana Shaka (Saka Samvat)", "value": "shaka"},
            {"text": "Vikram Samvat (Chaitradi)", "value": "vikram"},
            {"text": "Vikram Kartak (Kartikadi)", "value": "kartak"}
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
    }

    Controls.ComboBox {
        id: monthCombo
        Kirigami.FormData.label: i18n("Month System:")
        textRole: "text"
        valueRole: "value"
        model: [
            {"text": "Amavasyanta (Ends on New Moon)", "value": "amavasyanta"},
            {"text": "Purnimanta (Ends on Full Moon)", "value": "purnimanta"}
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
    }

    Controls.ComboBox {
        id: festCombo
        Kirigami.FormData.label: i18n("Festival Rules:")
        textRole: "text"
        valueRole: "value"
        model: [
            {"text": "Vaishnava (Default, Ekadashi rules)", "value": "vaishnava"},
            {"text": "Smarta", "value": "smarta"}
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
    }

    Controls.ComboBox {
        id: tithiCombo
        Kirigami.FormData.label: i18n("Tithi Mode:")
        textRole: "text"
        valueRole: "value"
        model: [
            {"text": "Sunrise Tithi (Traditional Day)", "value": "sunrise"},
            {"text": "Astronomical Tithi (Real-time)", "value": "astronomical"}
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
    }
}
