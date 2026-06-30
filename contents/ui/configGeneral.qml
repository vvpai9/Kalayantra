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

    // Searchable offline city results model
    ListModel {
        id: searchResultsModel
    }

    function queryCities(query) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/search_city?q=" + encodeURIComponent(query), true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    searchResultsModel.clear();
                    for (var i = 0; i < data.length; i++) {
                        searchResultsModel.append(data[i]);
                    }
                    cityNotFoundLabel.visible = (data.length === 0 && query.length >= 2);
                } catch(e) {
                    console.error("Failed to parse city search results:", e);
                }
            }
        };
        xhr.send();
    }

    Kirigami.Separator {
        Kirigami.FormData.isSection: true
        Kirigami.FormData.label: i18n("Geographic Location & Search")
    }

    Controls.TextField {
        id: citySearchField
        Kirigami.FormData.label: i18n("Search City:")
        placeholderText: i18n("Type city name to search...")
        onTextChanged: {
            if (text.trim().length >= 2) {
                queryCities(text.trim());
            } else {
                searchResultsModel.clear();
                cityNotFoundLabel.visible = false;
            }
        }
    }

    Controls.Label {
        id: cityNotFoundLabel
        text: i18n("City not found. Please enter coordinates.")
        color: "red"
        visible: false
    }

    Controls.ComboBox {
        id: cityResultsCombo
        Kirigami.FormData.label: i18n("Select Match:")
        model: searchResultsModel
        textRole: "name"
        visible: searchResultsModel.count > 0
        onActivated: (index) => {
            var selected = searchResultsModel.get(index);
            locationNameField.text = selected.name;
            latField.text = String(selected.lat);
            lonField.text = String(selected.lon);
            tzField.text = String(selected.tz);
            altField.text = String(selected.alt);
            searchResultsModel.clear();
            citySearchField.text = "";
        }
    }

    Controls.Button {
        text: i18n("Save Custom City")
        visible: locationNameField.text.trim() !== ""
        onClicked: {
            var xhr = new XMLHttpRequest();
            var query = "name=" + encodeURIComponent(locationNameField.text.trim()) +
                        "&lat=" + latField.text +
                        "&lon=" + lonField.text +
                        "&tz=" + tzField.text +
                        "&alt=" + altField.text;
            xhr.open("GET", "http://127.0.0.1:8642/save_custom_city?" + query, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                    citySearchField.placeholderText = i18n("Saved successfully!");
                }
            };
            xhr.send();
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
        Kirigami.FormData.label: i18n("Altitude (meters):")
        placeholderText: "e.g. 511.0"
    }

    Controls.TextField {
        id: tzField
        Kirigami.FormData.label: i18n("Timezone Offset:")
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
            {"text": "Traditional Mode (Sunrise Tithi)", "value": "traditional"},
            {"text": "Astronomical Mode (Live Transitions)", "value": "astronomical"}
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
