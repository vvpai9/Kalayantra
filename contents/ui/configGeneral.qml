import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: page
    implicitWidth: 600
    implicitHeight: 450

    // Custom bindings to config keys using cfg_ prefix
    property alias cfg_locationName: locationNameField.text
    property alias cfg_latitude: latField.text
    property alias cfg_longitude: lonField.text
    property alias cfg_altitude: altField.text
    property alias cfg_timezone: tzField.text

    property string cfg_lang
    property string cfg_ayanamsa

    property bool inputsValid: (validationMessage.text === "" && 
                                locationNameField.text.trim() !== "" && 
                                latField.text.trim() !== "" && 
                                lonField.text.trim() !== "" && 
                                altField.text.trim() !== "" && 
                                tzField.text.trim() !== "")

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

    function validateInputs() {
        if (locationNameField.text.trim() === "") {
            validationMessage.text = "";
            return;
        }
        if (latField.text.trim() === "" || !latField.acceptableInput) {
            validationMessage.text = i18n("Latitude must be a valid number between -90 and 90.");
            return;
        }
        if (lonField.text.trim() === "" || !lonField.acceptableInput) {
            validationMessage.text = i18n("Longitude must be a valid number between -180 and 180.");
            return;
        }
        if (altField.text.trim() === "" || !altField.acceptableInput) {
            validationMessage.text = i18n("Altitude must be a valid number.");
            return;
        }
        if (tzField.text.trim() === "" || !tzField.acceptableInput) {
            validationMessage.text = i18n("Timezone offset must be a valid number between -12 and 14.");
            return;
        }
        validationMessage.text = "";
    }

    ScrollView {
        anchors.fill: parent
        clip: true
        ScrollBar.horizontal.policy: ScrollBar.AsNeeded
        ScrollBar.vertical.policy: ScrollBar.AsNeeded

        ColumnLayout {
            width: parent.width - Kirigami.Units.gridUnit
            spacing: Kirigami.Units.largeSpacing
            anchors.margins: Kirigami.Units.largeSpacing

            // Card 1: Geographic Location & Search
            Kirigami.Card {
                Layout.fillWidth: true
                
                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    
                    Kirigami.Icon {
                        source: "mark-location"
                        implicitWidth: Kirigami.Units.gridUnit * 1.5
                        implicitHeight: Kirigami.Units.gridUnit * 1.5
                    }
                    
                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading {
                            text: i18n("Geographic Location & Search")
                            level: 3
                        }
                        Label {
                            text: i18n("Choose your city or enter geographic coordinates manually to calculate local Sun and Moon transitions.")
                            font.pixelSize: Kirigami.Units.gridUnit * 0.75
                            opacity: 0.6
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }

                contentItem: Kirigami.FormLayout {
                    Layout.fillWidth: true

                    TextField {
                        id: citySearchField
                        Kirigami.FormData.label: i18n("Search City:")
                        placeholderText: i18n("Type city name to search...")
                        leftPadding: 24
                        Layout.fillWidth: true
                        onTextChanged: {
                            if (text.trim().length >= 2) {
                                page.queryCities(text.trim());
                            } else {
                                searchResultsModel.clear();
                                cityNotFoundLabel.visible = false;
                            }
                        }

                        Kirigami.Icon {
                            source: "edit-find"
                            width: 14
                            height: 14
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: 6
                        }
                        Accessible.name: i18n("Search Offline Cities Database")
                        Accessible.description: i18n("Enter a city name to search the built-in and custom offline registry")
                    }

                    Label {
                        id: cityNotFoundLabel
                        text: i18n("City not found. Please enter coordinates manually.")
                        color: Kirigami.Theme.negativeTextColor
                        visible: false
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }

                    ComboBox {
                        id: cityResultsCombo
                        Kirigami.FormData.label: i18n("Select Match:")
                        model: searchResultsModel
                        textRole: "name"
                        visible: searchResultsModel.count > 0
                        Layout.fillWidth: true
                        onActivated: (index) => {
                            var selected = searchResultsModel.get(index);
                            locationNameField.text = selected.name;
                            latField.text = String(selected.lat);
                            lonField.text = String(selected.lon);
                            tzField.text = String(selected.tz);
                            altField.text = String(selected.alt);
                            searchResultsModel.clear();
                            citySearchField.text = "";
                            page.validateInputs();
                        }
                        Accessible.name: i18n("Search Results Matches")
                    }

                    Kirigami.Separator { Layout.fillWidth: true }

                    TextField {
                        id: locationNameField
                        Kirigami.FormData.label: i18n("Location Name:")
                        placeholderText: "e.g. Ujjain"
                        Layout.fillWidth: true
                        onTextChanged: page.validateInputs()
                        Accessible.name: i18n("Location Name")
                    }

                    TextField {
                        id: latField
                        Kirigami.FormData.label: i18n("Latitude:")
                        placeholderText: "e.g. 23.1765"
                        Layout.fillWidth: true
                        validator: DoubleValidator { bottom: -90.0; top: 90.0; decimals: 6 }
                        onTextChanged: page.validateInputs()
                        Accessible.name: i18n("Latitude Coordinate")
                    }

                    TextField {
                        id: lonField
                        Kirigami.FormData.label: i18n("Longitude:")
                        placeholderText: "e.g. 75.7885"
                        Layout.fillWidth: true
                        validator: DoubleValidator { bottom: -180.0; top: 180.0; decimals: 6 }
                        onTextChanged: page.validateInputs()
                        Accessible.name: i18n("Longitude Coordinate")
                    }

                    TextField {
                        id: altField
                        Kirigami.FormData.label: i18n("Altitude (meters):")
                        placeholderText: "e.g. 511.0"
                        Layout.fillWidth: true
                        validator: DoubleValidator { bottom: -1000.0; top: 9000.0; decimals: 2 }
                        onTextChanged: page.validateInputs()
                        Accessible.name: i18n("Altitude")
                    }

                    TextField {
                        id: tzField
                        Kirigami.FormData.label: i18n("Timezone Offset:")
                        placeholderText: "e.g. 5.5 for IST"
                        Layout.fillWidth: true
                        validator: DoubleValidator { bottom: -12.0; top: 14.0; decimals: 2 }
                        onTextChanged: page.validateInputs()
                        Accessible.name: i18n("Timezone Offset")
                    }

                    Kirigami.InlineMessage {
                        id: validationMessage
                        type: Kirigami.MessageType.Warning
                        text: ""
                        visible: text !== ""
                        Layout.fillWidth: true
                    }

                    Kirigami.InlineMessage {
                        id: saveStatusMessage
                        type: Kirigami.MessageType.Information
                        text: ""
                        visible: text !== ""
                        Layout.fillWidth: true
                        showCloseButton: true
                    }

                    Timer {
                        id: saveStatusTimer
                        interval: 4000
                        running: false
                        repeat: false
                        onTriggered: saveStatusMessage.text = ""
                    }

                    Button {
                        text: i18n("Save Custom City")
                        icon.name: "document-save"
                        visible: locationNameField.text.trim() !== ""
                        enabled: page.inputsValid
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
                                    saveStatusMessage.type = Kirigami.MessageType.Information;
                                    saveStatusMessage.text = i18n("Custom city saved successfully!");
                                    saveStatusTimer.restart();
                                } else if (xhr.readyState === XMLHttpRequest.DONE) {
                                    saveStatusMessage.type = Kirigami.MessageType.Error;
                                    saveStatusMessage.text = i18n("Failed to save custom city.");
                                    saveStatusTimer.restart();
                                }
                            };
                            xhr.send();
                        }
                        Accessible.name: i18n("Save Custom City")
                        Accessible.description: i18n("Add current location coordinates to the custom offline database")
                    }
                }
            }

            // Card 2: Language Preferences
            Kirigami.Card {
                Layout.fillWidth: true

                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    
                    Kirigami.Icon {
                        source: "preferences-desktop-locale"
                        implicitWidth: Kirigami.Units.gridUnit * 1.5
                        implicitHeight: Kirigami.Units.gridUnit * 1.5
                    }
                    
                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading {
                            text: i18n("Language Preferences")
                            level: 3
                        }
                        Label {
                            text: i18n("Configure the script type and translation system used to display panchanga names.")
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
                        id: langCombo
                        Kirigami.FormData.label: i18n("Display Language:")
                        textRole: "text"
                        valueRole: "value"
                        Layout.fillWidth: true
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
                        Accessible.name: i18n("Display Language")
                        Accessible.description: i18n("Choose default display language for calendar entries")
                    }
                }
            }

                // Card 3: Ayanamsa & Chart Reference
            Kirigami.Card {
                Layout.fillWidth: true

                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing

                    Kirigami.Icon {
                        source: "kunknown"
                        implicitWidth: Kirigami.Units.gridUnit * 1.5
                        implicitHeight: Kirigami.Units.gridUnit * 1.5
                    }

                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading {
                            text: i18n("Ayanamsa / Chart Reference")
                            level: 3
                        }
                        Label {
                            text: i18n("Choose the zodiac reference for sidereal charts and the Detailed Panchang report.")
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
                        id: ayanamsaCombo
                        Kirigami.FormData.label: i18n("Ayanamsa:")
                        textRole: "text"
                        valueRole: "value"
                        Layout.fillWidth: true
                        model: [
                            {"text": "Sayana (Tropical)", "value": "sayana"},
                            {"text": "Lahiri (Chitrapaksha)", "value": "lahiri"},
                            {"text": "Raman", "value": "raman"},
                            {"text": "Krishnamurti (KP)", "value": "krishnamurti"},
                            {"text": "True Chitra", "value": "true_citra"},
                            {"text": "Fagan/Bradley", "value": "fagan_bradley"},
                            {"text": "DeLuce", "value": "deluce"}
                        ]
                        onActivated: {
                            page.cfg_ayanamsa = currentValue;
                        }
                        Component.onCompleted: {
                            currentIndex = indexOfValue(page.cfg_ayanamsa);
                        }
                        Connections {
                            target: page
                            function onCfg_ayanamsaChanged() {
                                ayanamsaCombo.currentIndex = ayanamsaCombo.indexOfValue(page.cfg_ayanamsa);
                            }
                        }
                        Accessible.name: i18n("Ayanamsa")
                        Accessible.description: i18n("Choose sidereal or tropical reference for chart calculations")
                    }

                    Label {
                        text: i18n("Sayana (tropical) uses the ecliptic directly; sidereal modes subtract the precession offset of the chosen system. Lahiri is the common Chitrapaksha standard.")
                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                        opacity: 0.6
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }

            // Card 4: About
            Kirigami.Card {
                Layout.fillWidth: true

                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing

                    Kirigami.Icon {
                        source: "help-about"
                        implicitWidth: Kirigami.Units.gridUnit * 1.5
                        implicitHeight: Kirigami.Units.gridUnit * 1.5
                    }

                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading {
                            text: i18n("About Kālayantra")
                            level: 3
                        }
                        Label {
                            text: i18n("Version, authorship, licensing and local backend runtime information.")
                            font.pixelSize: Kirigami.Units.gridUnit * 0.75
                            opacity: 0.6
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }

                contentItem: Kirigami.FormLayout {
                    Layout.fillWidth: true

                    Label {
                        text: i18n("Kālayantra (कालयन्त्र)")
                        Kirigami.FormData.label: i18n("Application:")
                        Layout.fillWidth: true
                    }
                    Label {
                        text: "2.0"
                        Kirigami.FormData.label: i18n("Version:")
                        Layout.fillWidth: true
                    }
                    Label {
                        text: i18n("Varun Vivek Pai")
                        Kirigami.FormData.label: i18n("Author:")
                        Layout.fillWidth: true
                    }
                    Label {
                        text: i18n("GPL-3.0 License")
                        Kirigami.FormData.label: i18n("License:")
                        Layout.fillWidth: true
                    }
                    Label {
                        text: i18n("Astronomical calculations are powered by the Swiss Ephemeris (© Astrodienst AG). Hindu eclipse data is based on publically available panchanga data and nautical almanacs.")
                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                        opacity: 0.7
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                        Kirigami.FormData.label: i18n("Attribution:")
                    }

                    Kirigami.Separator { Layout.fillWidth: true; Layout.topMargin: Kirigami.Units.smallSpacing }

                    Label {
                        id: backendArchLabel
                        text: i18n("Local backend offline. Checking backend...")
                        font.pixelSize: Kirigami.Units.gridUnit * 0.75
                        opacity: 0.7
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                        Kirigami.FormData.label: i18n("Backend:")
                    }

                    Timer {
                        id: aboutInfoTimer
                        interval: 300
                        running: true
                        repeat: false
                        onTriggered: {
                            var xhr = new XMLHttpRequest();
                            xhr.open("GET", "http://127.0.0.1:8642/system_info?_t=" + Date.now(), true);
                            xhr.onreadystatechange = function() {
                                if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                                    try {
                                        var info = JSON.parse(xhr.responseText);
                                        backendArchLabel.text = i18n("System: %1 · Processor: %2 · Architecture: %3")
                                            .arg(info.system || "")
                                            .arg(info.processor || "")
                                            .arg(info.architecture || "");
                                    } catch(e) {
                                        console.error("Failed to parse system info:", e);
                                    }
                                } else if (xhr.readyState === XMLHttpRequest.DONE) {
                                    backendArchLabel.text = i18n("Local backend not running. Start it with: kalayantra-cli serve");
                                }
                            };
                            xhr.send();
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        validateInputs();
    }
}
