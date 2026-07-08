import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import org.kde.kirigami as Kirigami

Item {
    id: page
    implicitWidth: 600
    implicitHeight: 450
    property bool confirmDeleteAll: false
    property bool isWorking: false

    ListModel {
        id: observancesModel
    }

    Timer {
        id: reloadTimer
        interval: 50
        running: false
        repeat: false
        onTriggered: {
            page.loadObservances();
        }
    }

    FileDialog {
        id: importFileDialog
        title: i18n("Select JSON file to import saved tithis")
        nameFilters: ["JSON files (*.json)"]
        fileMode: FileDialog.OpenFile
        onAccepted: {
            page.isWorking = true;
            importMessage.text = "";
            var path = selectedFile.toString();
            if (path.startsWith("file://")) {
                path = path.substring(7);
            }
            path = decodeURIComponent(path);
            
            var xhr = new XMLHttpRequest();
            var buster = "_t=" + Date.now();
            xhr.open("GET", "http://127.0.0.1:8642/import_custom_observances?filepath=" + encodeURIComponent(path) + "&" + buster, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    page.isWorking = false;
                    if (xhr.status === 200) {
                        importMessage.type = Kirigami.MessageType.Information;
                        importMessage.text = i18n("Tithis imported successfully!");
                        reloadTimer.start();
                    } else {
                        importMessage.type = Kirigami.MessageType.Error;
                        try {
                            var res = JSON.parse(xhr.responseText);
                            importMessage.text = res.message || i18n("Failed to import tithis.");
                        } catch(e) {
                            importMessage.text = i18n("Failed to import tithis.");
                        }
                    }
                }
            };
            xhr.send();
        }
    }

    FileDialog {
        id: exportFileDialog
        title: i18n("Choose destination JSON file to export saved tithis")
        fileMode: FileDialog.SaveFile
        nameFilters: ["JSON files (*.json)"]
        onAccepted: {
            page.isWorking = true;
            importMessage.text = "";
            var path = selectedFile.toString();
            if (path.startsWith("file://")) {
                path = path.substring(7);
            }
            path = decodeURIComponent(path);
            if (!path.endsWith(".json")) {
                path += ".json";
            }
            
            var xhr = new XMLHttpRequest();
            var buster = "_t=" + Date.now();
            xhr.open("GET", "http://127.0.0.1:8642/export_custom_observances?filepath=" + encodeURIComponent(path) + "&" + buster, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    page.isWorking = false;
                    if (xhr.status === 200) {
                        importMessage.type = Kirigami.MessageType.Information;
                        importMessage.text = i18n("Tithis exported successfully!");
                    } else {
                        importMessage.type = Kirigami.MessageType.Error;
                        importMessage.text = i18n("Failed to export tithis.");
                    }
                }
            };
            xhr.send();
        }
    }

    function loadObservances() {
        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        xhr.open("GET", "http://127.0.0.1:8642/get_custom_observances?" + buster, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    page.syncModel(data);
                } catch(e) {
                    console.error("Failed to parse tithis:", e);
                }
            }
        };
        xhr.send();
    }

    function syncModel(data) {
        var backendIds = {};
        for (var i = 0; i < data.length; i++) {
            backendIds[data[i].id] = data[i];
        }
        
        for (var j = observancesModel.count - 1; j >= 0; j--) {
            var item = observancesModel.get(j);
            if (!backendIds[item.id]) {
                observancesModel.remove(j);
            }
        }
        
        for (var k = 0; k < data.length; k++) {
            var bItem = data[k];
            var existingIndex = -1;
            for (var m = 0; m < observancesModel.count; m++) {
                if (observancesModel.get(m).id === bItem.id) {
                    existingIndex = m;
                    break;
                }
            }
            
            var sysB = bItem.system || "amavasyanta";
            var gregB = (bItem.gregorian_year !== undefined && bItem.gregorian_year !== null) ? bItem.gregorian_year : "";
            if (existingIndex === -1) {
                observancesModel.append({
                    "id": bItem.id,
                    "name": bItem.name,
                    "month": bItem.month,
                    "paksha": bItem.paksha,
                    "tithi": bItem.tithi,
                    "system": sysB,
                    "gregorian_year": gregB
                });
            } else {
                var local = observancesModel.get(existingIndex);
                var sysL = local.system || "amavasyanta";
                var gregL = local.gregorian_year || "";
                if (local.name !== bItem.name || 
                    local.month !== bItem.month || 
                    local.paksha !== bItem.paksha || 
                    local.tithi !== bItem.tithi || 
                    sysL !== sysB ||
                    gregL !== gregB) {
                    observancesModel.set(existingIndex, {
                        "id": bItem.id,
                        "name": bItem.name,
                        "month": bItem.month,
                        "paksha": bItem.paksha,
                        "tithi": bItem.tithi,
                        "system": sysB,
                        "gregorian_year": gregB
                    });
                }
            }
        }
    }

    function addObservance(name, month, paksha, tithi, system, gregorian_year) {
        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        var query = "name=" + encodeURIComponent(name) +
                    "&month=" + encodeURIComponent(month) +
                    "&paksha=" + encodeURIComponent(paksha) +
                    "&tithi=" + encodeURIComponent(tithi) +
                    "&system=" + encodeURIComponent(system) +
                    "&gregorian_year=" + encodeURIComponent(gregorian_year) +
                    "&" + buster;
        xhr.open("GET", "http://127.0.0.1:8642/save_custom_observance?" + query, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    reloadTimer.start();
                    page.resetForm();
                } else {
                    try {
                        var errData = JSON.parse(xhr.responseText);
                        errorAlert.text = errData.message || errData.error || i18n("Tithi already exists!");
                    } catch(e) {
                        errorAlert.text = i18n("Tithi already exists!");
                    }
                    errorAlert.visible = true;
                    errorHideTimer.restart();
                }
            }
        };
        xhr.send();
    }

    function deleteObservance(id) {
        for (var i = 0; i < observancesModel.count; i++) {
            if (observancesModel.get(i).id === id) {
                observancesModel.remove(i);
                break;
            }
        }

        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        xhr.open("GET", "http://127.0.0.1:8642/delete_custom_observance?id=" + encodeURIComponent(id) + "&" + buster, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                reloadTimer.start();
            }
        };
        xhr.send();
    }

    function clearAllObservances() {
        observancesModel.clear();

        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        xhr.open("GET", "http://127.0.0.1:8642/clear_custom_observances?" + buster, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                reloadTimer.start();
            }
        };
        xhr.send();
    }

    function validateInputs() {
        if (nameInput.text.trim() === "") {
            validationMsg.text = "";
            return;
        }
        if (gregorianYearInput.text !== "" && !gregorianYearInput.acceptableInput) {
            validationMsg.text = i18n("Gregorian Year must be a valid number between 1 and 3000.");
            return;
        }
        validationMsg.text = "";
    }

    function resetForm() {
        nameInput.text = "";
        monthInput.currentIndex = 0;
        pakshaInput.currentIndex = 0;
        tithiInput.currentIndex = 0;
        systemInput.currentIndex = 0;
        gregorianYearInput.text = "";
        errorAlert.visible = false;
        validationMsg.text = "";
    }

    function getAnniversaryDisplay(gregYear, name) {
        if (!gregYear) return "";
        var yr = parseInt(gregYear);
        if (isNaN(yr) || yr <= 0) return "";
        var currentYear = new Date().getFullYear();
        var diff = currentYear - yr;
        if (diff <= 0) return "";
        
        var ordinal = function(n) {
            var s = ["th", "st", "nd", "rd"];
            var v = n % 100;
            return n + (s[(v - 20) % 10] || s[v] || s[0]);
        };
        
        var isBirthday = name.toLowerCase().indexOf("birthday") !== -1 || name.toLowerCase().indexOf("janmadin") !== -1;
        var typeStr = isBirthday ? i18n("Birthday") : i18n("Anniversary");
        return ordinal(diff) + " " + typeStr;
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

            // Top Error alert
            Kirigami.InlineMessage {
                id: errorAlert
                type: Kirigami.MessageType.Error
                text: i18n("Tithi already exists!")
                visible: false
                Layout.fillWidth: true
                showCloseButton: true
            }

            Timer {
                id: errorHideTimer
                interval: 5000
                running: false
                repeat: false
                onTriggered: errorAlert.visible = false
            }

            // Card 1: Basic Information
            Kirigami.Card {
                Layout.fillWidth: true
                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    Kirigami.Icon { source: "appointment-new"; implicitWidth: Kirigami.Units.gridUnit * 1.5; implicitHeight: Kirigami.Units.gridUnit * 1.5 }
                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading { text: i18n("Basic Information"); level: 3 }
                        Label { text: i18n("Define the name and year references for this observance."); font.pixelSize: Kirigami.Units.gridUnit * 0.75; opacity: 0.6 }
                    }
                }
                contentItem: Kirigami.FormLayout {
                    Layout.fillWidth: true
                    TextField {
                        id: nameInput
                        Kirigami.FormData.label: i18n("Tithi Name:")
                        placeholderText: i18n("e.g. Birthday, Shradha")
                        Layout.fillWidth: true
                        onTextChanged: {
                            errorAlert.visible = false;
                            validateInputs();
                        }
                        Accessible.name: i18n("Tithi Name")
                        Accessible.description: i18n("Enter a custom name for the traditional observance")
                    }
                    TextField {
                        id: gregorianYearInput
                        Kirigami.FormData.label: i18n("Gregorian Year (Optional):")
                        placeholderText: i18n("e.g. 2005 (for anniversary calculations)")
                        Layout.fillWidth: true
                        validator: IntValidator { bottom: 1; top: 3000 }
                        onTextChanged: {
                            errorAlert.visible = false;
                            validateInputs();
                        }
                        Accessible.name: i18n("Event Year")
                        Accessible.description: i18n("Enter original Gregorian event year to calculate anniversaries dynamically")
                    }
                    Kirigami.InlineMessage {
                        id: validationMsg
                        type: Kirigami.MessageType.Warning
                        text: ""
                        visible: text !== ""
                        Layout.fillWidth: true
                    }
                }
            }

            // Card 2: Lunar Date
            Kirigami.Card {
                Layout.fillWidth: true
                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    Kirigami.Icon { source: "office-calendar"; implicitWidth: Kirigami.Units.gridUnit * 1.5; implicitHeight: Kirigami.Units.gridUnit * 1.5 }
                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading { text: i18n("Lunar Date"); level: 3 }
                        Label { text: i18n("Configure the exact Hindu calendar parameters."); font.pixelSize: Kirigami.Units.gridUnit * 0.75; opacity: 0.6 }
                    }
                }
                contentItem: Kirigami.FormLayout {
                    Layout.fillWidth: true
                    ComboBox {
                        id: monthInput
                        Kirigami.FormData.label: i18n("Masa (Month):")
                        Layout.fillWidth: true
                        model: ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"]
                        Accessible.name: i18n("Hindu Month Selection")
                    }
                    ComboBox {
                        id: pakshaInput
                        Kirigami.FormData.label: i18n("Paksha:")
                        Layout.fillWidth: true
                        model: ["Shukla", "Krishna"]
                        Accessible.name: i18n("Paksha Selection")
                    }
                    ComboBox {
                        id: tithiInput
                        Kirigami.FormData.label: i18n("Tithi:")
                        Layout.fillWidth: true
                        model: [
                            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami",
                            "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima", "Amavasya"
                        ]
                        Accessible.name: i18n("Tithi Selection")
                    }
                    ComboBox {
                        id: systemInput
                        Kirigami.FormData.label: i18n("Month System:")
                        Layout.fillWidth: true
                        model: ["Amavasyanta", "Purnimanta"]
                        Accessible.name: i18n("Month System Selection")
                    }
                }
            }

            // Card 3: Actions
            Kirigami.Card {
                Layout.fillWidth: true
                contentItem: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    Button {
                        text: i18n("Add Tithi")
                        icon.name: "list-add"
                        enabled: (nameInput.text.trim() !== "" && validationMsg.text === "")
                        Layout.fillWidth: true
                        onClicked: {
                            page.addObservance(
                                nameInput.text.trim(),
                                monthInput.currentText,
                                pakshaInput.currentText,
                                tithiInput.currentText,
                                systemInput.currentText.toLowerCase(),
                                gregorianYearInput.text.trim()
                            );
                        }
                    }
                    Button {
                        text: i18n("Reset Form")
                        icon.name: "edit-clear"
                        Layout.fillWidth: true
                        onClicked: page.resetForm()
                    }
                }
            }

            // Card 4: Import / Export Registry
            Kirigami.Card {
                Layout.fillWidth: true
                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    Kirigami.Icon { source: "document-share"; implicitWidth: Kirigami.Units.gridUnit * 1.5; implicitHeight: Kirigami.Units.gridUnit * 1.5 }
                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading { text: i18n("Import & Export Observances"); level: 3 }
                        Label { text: i18n("Backup or restore your custom tithis database file."); font.pixelSize: Kirigami.Units.gridUnit * 0.75; opacity: 0.6 }
                    }
                }
                contentItem: Kirigami.FormLayout {
                    Layout.fillWidth: true
                    
                    Kirigami.InlineMessage {
                        id: importMessage
                        text: ""
                        visible: text !== ""
                        Layout.fillWidth: true
                        showCloseButton: true
                    }
                    
                    RowLayout {
                        spacing: Kirigami.Units.largeSpacing
                        Button {
                            text: i18n("Import from File...")
                            icon.name: "document-import"
                            onClicked: importFileDialog.open()
                        }
                        Button {
                            text: i18n("Export to File...")
                            icon.name: "document-export"
                            onClicked: exportFileDialog.open()
                        }
                        BusyIndicator {
                            running: page.isWorking
                            visible: running
                        }
                    }
                }
            }

            // Section: Saved Observances Header
            RowLayout {
                Layout.fillWidth: true
                Label {
                    text: i18n("Saved Custom Tithis")
                    font.bold: true
                    font.pixelSize: Kirigami.Units.gridUnit * 1.1
                    Layout.fillWidth: true
                }
                Button {
                    text: i18n("Delete All")
                    icon.name: "edit-clear-all"
                    visible: observancesModel.count > 0 && !page.confirmDeleteAll
                    onClicked: page.confirmDeleteAll = true
                }
                Button {
                    text: i18n("Confirm Delete All?")
                    icon.name: "edit-delete"
                    visible: page.confirmDeleteAll
                    onClicked: {
                        page.confirmDeleteAll = false;
                        page.clearAllObservances();
                    }
                }
                Button {
                    text: i18n("Cancel")
                    visible: page.confirmDeleteAll
                    onClicked: page.confirmDeleteAll = false
                }
            }

            // Saved Tithis Card List
            ColumnLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.largeSpacing

                Repeater {
                    model: observancesModel
                    
                    delegate: Kirigami.Card {
                        id: savedTithiCard
                        Layout.fillWidth: true
                        property bool confirmDelete: false

                        contentItem: ColumnLayout {
                            Layout.margins: Kirigami.Units.largeSpacing
                            spacing: Kirigami.Units.smallSpacing

                            // Top title line with emoji & bold name
                            RowLayout {
                                Layout.fillWidth: true
                                Label {
                                    text: {
                                        var isB = name.toLowerCase().indexOf("birthday") !== -1 || name.toLowerCase().indexOf("janmadin") !== -1;
                                        return (isB ? "🎂 " : "📅 ") + name;
                                    }
                                    font.bold: true
                                    font.pixelSize: Kirigami.Units.gridUnit * 1.1
                                    Layout.fillWidth: true
                                }
                            }

                            // Lunar date details
                            Label {
                                text: `${month} ${paksha} ${tithi} (${(system || "AMAVASYANTA").toUpperCase()})`
                                opacity: 0.8
                            }

                            // Optional Anniversary Dynamic calculation line
                            Label {
                                text: page.getAnniversaryDisplay(gregorian_year, name)
                                visible: gregorian_year !== undefined && gregorian_year !== null && gregorian_year !== ""
                                font.italic: true
                                color: Kirigami.Theme.activeTextColor
                            }

                            // Action buttons row
                            RowLayout {
                                Layout.topMargin: Kirigami.Units.smallSpacing
                                spacing: Kirigami.Units.largeSpacing

                                Button {
                                    text: i18n("Edit")
                                    icon.name: "edit-rename"
                                    visible: !confirmDelete
                                    onClicked: {
                                        var tName = (typeof name !== 'undefined') ? name : "";
                                        var tMonth = (typeof month !== 'undefined') ? month : "";
                                        var tPaksha = (typeof paksha !== 'undefined') ? paksha : "";
                                        var tTithi = (typeof tithi !== 'undefined') ? tithi : "";
                                        var tSystem = (typeof system !== 'undefined') ? system : "amavasyanta";
                                        var tGreg = (typeof gregorian_year !== 'undefined' && gregorian_year) ? gregorian_year : "";
                                        var tId = (typeof id !== 'undefined') ? id : "";
                                        
                                        nameInput.text = tName;
                                        monthInput.currentIndex = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"].indexOf(tMonth);
                                        pakshaInput.currentIndex = ["Shukla", "Krishna"].indexOf(tPaksha);
                                        tithiInput.currentIndex = [
                                            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami",
                                            "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima", "Amavasya"
                                        ].indexOf(tTithi);
                                        systemInput.currentIndex = ["amavasyanta", "purnimanta"].indexOf(tSystem);
                                        gregorianYearInput.text = String(tGreg);
                                        page.deleteObservance(tId);
                                    }
                                }

                                Button {
                                    text: i18n("Delete")
                                    icon.name: "edit-delete"
                                    visible: !confirmDelete
                                    onClicked: confirmDelete = true
                                }

                                Button {
                                    text: i18n("Confirm Delete?")
                                    icon.name: "edit-delete"
                                    visible: confirmDelete
                                    onClicked: {
                                        confirmDelete = false;
                                        page.deleteObservance((typeof id !== 'undefined') ? id : "");
                                    }
                                }

                                Button {
                                    text: i18n("Cancel")
                                    visible: confirmDelete
                                    onClicked: confirmDelete = false
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        loadObservances();
    }
}
