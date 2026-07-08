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
        id: remindersModel
    }

    Timer {
        id: reloadTimer
        interval: 50
        running: false
        repeat: false
        onTriggered: {
            page.loadReminders();
        }
    }

    FileDialog {
        id: importFileDialog
        title: i18n("Select JSON file to import reminders")
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
            xhr.open("GET", "http://127.0.0.1:8642/import_reminders?filepath=" + encodeURIComponent(path) + "&" + buster, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    page.isWorking = false;
                    if (xhr.status === 200) {
                        importMessage.type = Kirigami.MessageType.Information;
                        importMessage.text = i18n("Reminders imported successfully!");
                        reloadTimer.start();
                    } else {
                        importMessage.type = Kirigami.MessageType.Error;
                        try {
                            var res = JSON.parse(xhr.responseText);
                            importMessage.text = res.message || i18n("Failed to import reminders.");
                        } catch(e) {
                            importMessage.text = i18n("Failed to import reminders.");
                        }
                    }
                }
            };
            xhr.send();
        }
    }

    FileDialog {
        id: exportFileDialog
        title: i18n("Choose destination JSON file to export reminders")
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
            xhr.open("GET", "http://127.0.0.1:8642/export_reminders?filepath=" + encodeURIComponent(path) + "&" + buster, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    page.isWorking = false;
                    if (xhr.status === 200) {
                        importMessage.type = Kirigami.MessageType.Information;
                        importMessage.text = i18n("Reminders exported successfully!");
                    } else {
                        importMessage.type = Kirigami.MessageType.Error;
                        importMessage.text = i18n("Failed to export reminders.");
                    }
                }
            };
            xhr.send();
        }
    }

    function loadReminders() {
        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        xhr.open("GET", "http://127.0.0.1:8642/get_reminders?" + buster, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    page.syncModel(data);
                } catch(e) {
                    console.error("Failed to parse reminders:", e);
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
        
        for (var j = remindersModel.count - 1; j >= 0; j--) {
            var item = remindersModel.get(j);
            if (!backendIds[item.id]) {
                remindersModel.remove(j);
            }
        }
        
        for (var k = 0; k < data.length; k++) {
            var bItem = data[k];
            var existingIndex = -1;
            for (var m = 0; m < remindersModel.count; m++) {
                if (remindersModel.get(m).id === bItem.id) {
                    existingIndex = m;
                    break;
                }
            }
            
            var paramsStr = JSON.stringify(bItem.params || {});
            var enabledVal = bItem.enabled !== undefined ? bItem.enabled : true;
            
            if (existingIndex === -1) {
                remindersModel.append({
                    "id": bItem.id,
                    "title": bItem.title,
                    "description": bItem.description || "",
                    "type": bItem.type,
                    "params_json": paramsStr,
                    "time_type": bItem.time_type,
                    "time_offset_mins": bItem.time_offset_mins || 0,
                    "time_exact_str": bItem.time_exact_str || "",
                    "enabled": enabledVal
                });
            } else {
                var local = remindersModel.get(existingIndex);
                if (local.title !== bItem.title ||
                    local.description !== bItem.description ||
                    local.type !== bItem.type ||
                    local.params_json !== paramsStr ||
                    local.time_type !== bItem.time_type ||
                    local.time_offset_mins !== (bItem.time_offset_mins || 0) ||
                    local.time_exact_str !== (bItem.time_exact_str || "") ||
                    local.enabled !== enabledVal) {
                    remindersModel.set(existingIndex, {
                        "id": bItem.id,
                        "title": bItem.title,
                        "description": bItem.description || "",
                        "type": bItem.type,
                        "params_json": paramsStr,
                        "time_type": bItem.time_type,
                        "time_offset_mins": bItem.time_offset_mins || 0,
                        "time_exact_str": bItem.time_exact_str || "",
                        "enabled": enabledVal
                    });
                }
            }
        }
    }

    function addReminder(title, description, type, params, time_type, time_offset_mins, time_exact_str, enabled) {
        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        var query = "title=" + encodeURIComponent(title) +
                    "&description=" + encodeURIComponent(description) +
                    "&type=" + encodeURIComponent(type) +
                    "&params=" + encodeURIComponent(JSON.stringify(params)) +
                    "&time_type=" + encodeURIComponent(time_type) +
                    "&time_offset_mins=" + encodeURIComponent(time_offset_mins) +
                    "&time_exact_str=" + encodeURIComponent(time_exact_str) +
                    "&enabled=" + encodeURIComponent(enabled) +
                    "&" + buster;
        xhr.open("GET", "http://127.0.0.1:8642/save_reminder?" + query, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    reloadTimer.start();
                    page.resetForm();
                } else {
                    try {
                        var errData = JSON.parse(xhr.responseText);
                        errorAlert.text = errData.message || errData.error || i18n("Duplicate reminder exists!");
                    } catch(e) {
                        errorAlert.text = i18n("Duplicate reminder exists!");
                    }
                    errorAlert.visible = true;
                    errorHideTimer.restart();
                }
            }
        };
        xhr.send();
    }

    function deleteReminder(id) {
        for (var i = 0; i < remindersModel.count; i++) {
            if (remindersModel.get(i).id === id) {
                remindersModel.remove(i);
                break;
            }
        }

        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        xhr.open("GET", "http://127.0.0.1:8642/delete_reminder?id=" + encodeURIComponent(id) + "&" + buster, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                reloadTimer.start();
            }
        };
        xhr.send();
    }

    function clearAllReminders() {
        remindersModel.clear();
        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        xhr.open("GET", "http://127.0.0.1:8642/clear_reminders?" + buster, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                reloadTimer.start();
            }
        };
        xhr.send();
    }

    function toggleReminder(id, enabledState) {
        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        xhr.open("GET", "http://127.0.0.1:8642/get_reminders?" + buster, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    for (var i = 0; i < data.length; i++) {
                        if (data[i].id === id) {
                            var r = data[i];
                            var saveXhr = new XMLHttpRequest();
                            var query = "id=" + encodeURIComponent(id) +
                                        "&title=" + encodeURIComponent(r.title) +
                                        "&description=" + encodeURIComponent(r.description || "") +
                                        "&type=" + encodeURIComponent(r.type) +
                                        "&params=" + encodeURIComponent(JSON.stringify(r.params || {})) +
                                        "&time_type=" + encodeURIComponent(r.time_type) +
                                        "&time_offset_mins=" + encodeURIComponent(r.time_offset_mins || 0) +
                                        "&time_exact_str=" + encodeURIComponent(r.time_exact_str || "") +
                                        "&enabled=" + encodeURIComponent(enabledState) +
                                        "&" + buster;
                            saveXhr.open("GET", "http://127.0.0.1:8642/save_reminder?" + query, true);
                            saveXhr.onreadystatechange = function() {
                                if (saveXhr.readyState === XMLHttpRequest.DONE) {
                                    reloadTimer.start();
                                }
                            };
                            saveXhr.send();
                            break;
                        }
                    }
                } catch(e) {
                    console.error("Failed to toggle:", e);
                }
            }
        };
        xhr.send();
    }

    function validateInputs() {
        if (titleInput.text.trim() === "") {
            validationMsg.text = "";
            return;
        }
        if (typeInput.currentIndex === 6 && festivalParam.text.trim() === "") {
            validationMsg.text = i18n("Festival Name cannot be empty.");
            return;
        }
        if (timeTypeInput.currentIndex === 2 && !offsetInput.acceptableInput) {
            validationMsg.text = i18n("Offset minutes must be a valid number between 0 and 1440.");
            return;
        }
        if (timeTypeInput.currentIndex === 3 && (exactInput.text.trim() === "" || !exactInput.text.match(/^\d{2}:\d{2}$/))) {
            validationMsg.text = i18n("Exact time must be in HH:MM format.");
            return;
        }
        validationMsg.text = "";
    }

    function resetForm() {
        titleInput.text = "";
        descInput.text = "";
        typeInput.currentIndex = 0;
        tithiParam.currentIndex = 0;
        pakshaParam.currentIndex = 0;
        masaParam.currentIndex = 0;
        nakshatraParam.currentIndex = 0;
        varaParam.currentIndex = 0;
        festivalParam.text = "";
        timeTypeInput.currentIndex = 0;
        offsetInput.text = "0";
        exactInput.text = "09:00";
        errorAlert.visible = false;
        validationMsg.text = "";
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

            // Top Error Alert
            Kirigami.InlineMessage {
                id: errorAlert
                type: Kirigami.MessageType.Error
                text: i18n("Duplicate reminder exists!")
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
                    Kirigami.Icon { source: "notifications"; implicitWidth: Kirigami.Units.gridUnit * 1.5; implicitHeight: Kirigami.Units.gridUnit * 1.5 }
                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading { text: i18n("Basic Information"); level: 3 }
                        Label { text: i18n("Add a name and optional description for your desktop notification reminder."); font.pixelSize: Kirigami.Units.gridUnit * 0.75; opacity: 0.6 }
                    }
                }
                contentItem: Kirigami.FormLayout {
                    Layout.fillWidth: true
                    TextField {
                        id: titleInput
                        Kirigami.FormData.label: i18n("Title:")
                        placeholderText: i18n("e.g. Fasting Day, Purnima")
                        Layout.fillWidth: true
                        onTextChanged: {
                            errorAlert.visible = false;
                            validateInputs();
                        }
                        Accessible.name: i18n("Reminder Title")
                    }
                    TextField {
                        id: descInput
                        Kirigami.FormData.label: i18n("Description:")
                        placeholderText: i18n("e.g. Fasting and contemplation")
                        Layout.fillWidth: true
                        Accessible.name: i18n("Reminder Description")
                    }
                }
            }

            // Card 2: Reminder Trigger Parameters
            Kirigami.Card {
                Layout.fillWidth: true
                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    Kirigami.Icon { source: "edit-select-all"; implicitWidth: Kirigami.Units.gridUnit * 1.5; implicitHeight: Kirigami.Units.gridUnit * 1.5 }
                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading { text: i18n("Reminder Trigger Parameters"); level: 3 }
                        Label { text: i18n("Choose which calendar elements or events trigger this reminder."); font.pixelSize: Kirigami.Units.gridUnit * 0.75; opacity: 0.6 }
                    }
                }
                contentItem: Kirigami.FormLayout {
                    Layout.fillWidth: true
                    ComboBox {
                        id: typeInput
                        Kirigami.FormData.label: i18n("Reminder Type:")
                        Layout.fillWidth: true
                        model: [
                            i18n("Tithi"),
                            i18n("Paksha + Tithi"),
                            i18n("Masa + Paksha + Tithi"),
                            i18n("Nakshatra"),
                            i18n("Vara + Tithi"),
                            i18n("Sankranti"),
                            i18n("Festival")
                        ]
                        onActivated: validateInputs()
                        Accessible.name: i18n("Reminder Parameter Type")
                    }
                    ComboBox {
                        id: tithiParam
                        Kirigami.FormData.label: i18n("Tithi:")
                        visible: typeInput.currentIndex === 0 || typeInput.currentIndex === 1 || typeInput.currentIndex === 2 || typeInput.currentIndex === 4
                        Layout.fillWidth: true
                        model: [
                            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami",
                            "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima", "Amavasya"
                        ]
                        Accessible.name: i18n("Tithi Parameter Selection")
                    }
                    ComboBox {
                        id: pakshaParam
                        Kirigami.FormData.label: i18n("Paksha:")
                        visible: typeInput.currentIndex === 1 || typeInput.currentIndex === 2
                        Layout.fillWidth: true
                        model: ["Shukla", "Krishna"]
                        Accessible.name: i18n("Paksha Parameter Selection")
                    }
                    ComboBox {
                        id: masaParam
                        Kirigami.FormData.label: i18n("Masa:")
                        visible: typeInput.currentIndex === 2
                        Layout.fillWidth: true
                        model: ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"]
                        Accessible.name: i18n("Masa Parameter Selection")
                    }
                    ComboBox {
                        id: nakshatraParam
                        Kirigami.FormData.label: i18n("Nakshatra:")
                        visible: typeInput.currentIndex === 3
                        Layout.fillWidth: true
                        model: [
                            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
                            "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Svati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
                            "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
                        ]
                        Accessible.name: i18n("Nakshatra Parameter Selection")
                    }
                    ComboBox {
                        id: varaParam
                        Kirigami.FormData.label: i18n("Vara (Day of Week):")
                        visible: typeInput.currentIndex === 4
                        Layout.fillWidth: true
                        model: ["Indu", "Bhauma", "Saumya", "Guru", "Bhargava", "Sthira", "Bhanu"]
                        Accessible.name: i18n("Vara Parameter Selection")
                    }
                    TextField {
                        id: festivalParam
                        Kirigami.FormData.label: i18n("Festival Name:")
                        placeholderText: i18n("e.g. Mahashivaratri")
                        visible: typeInput.currentIndex === 6
                        Layout.fillWidth: true
                        onTextChanged: validateInputs()
                        Accessible.name: i18n("Festival Name Parameter")
                    }
                }
            }

            // Card 3: Notification Schedule
            Kirigami.Card {
                Layout.fillWidth: true
                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    Kirigami.Icon { source: "appointment-reminder"; implicitWidth: Kirigami.Units.gridUnit * 1.5; implicitHeight: Kirigami.Units.gridUnit * 1.5 }
                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading { text: i18n("Notification Schedule"); level: 3 }
                        Label { text: i18n("Specify exact notification timing rule relative to sunrise."); font.pixelSize: Kirigami.Units.gridUnit * 0.75; opacity: 0.6 }
                    }
                }
                contentItem: Kirigami.FormLayout {
                    Layout.fillWidth: true
                    ComboBox {
                        id: timeTypeInput
                        Kirigami.FormData.label: i18n("Notification Time:")
                        Layout.fillWidth: true
                        model: [
                            i18n("Brahma Muhurta"),
                            i18n("Sunrise"),
                            i18n("Offset before sunrise"),
                            i18n("Exact clock time")
                        ]
                        onActivated: validateInputs()
                        Accessible.name: i18n("Notification Trigger Time Rule")
                    }
                    TextField {
                        id: offsetInput
                        Kirigami.FormData.label: i18n("Offset Minutes:")
                        text: "0"
                        placeholderText: i18n("Minutes before sunrise")
                        Layout.fillWidth: true
                        validator: IntValidator { bottom: 0; top: 1440 }
                        visible: timeTypeInput.currentIndex === 2
                        onTextChanged: validateInputs()
                        Accessible.name: i18n("Offset Minutes Value")
                    }
                    TextField {
                        id: exactInput
                        Kirigami.FormData.label: i18n("Exact Time:")
                        text: "09:00"
                        placeholderText: i18n("e.g. 09:30")
                        Layout.fillWidth: true
                        visible: timeTypeInput.currentIndex === 3
                        onTextChanged: validateInputs()
                        Accessible.name: i18n("Exact Time Clock Value")
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

            // Card 4: Actions
            Kirigami.Card {
                Layout.fillWidth: true
                contentItem: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    Button {
                        text: i18n("Add Reminder")
                        icon.name: "list-add"
                        Layout.fillWidth: true
                        enabled: (titleInput.text.trim() !== "" && validationMsg.text === "")
                        onClicked: {
                            var remTypeStr = "";
                            var remParams = {};
                            switch (typeInput.currentIndex) {
                                case 0:
                                    remTypeStr = "tithi";
                                    remParams = { "tithi": tithiParam.currentText };
                                    break;
                                case 1:
                                    remTypeStr = "paksha_tithi";
                                    remParams = { "paksha": pakshaParam.currentText, "tithi": tithiParam.currentText };
                                    break;
                                case 2:
                                    remTypeStr = "masa_paksha_tithi";
                                    remParams = { "masa": masaParam.currentText, "paksha": pakshaParam.currentText, "tithi": tithiParam.currentText };
                                    break;
                                case 3:
                                    remTypeStr = "nakshatra";
                                    remParams = { "nakshatra": nakshatraParam.currentText };
                                    break;
                                case 4:
                                    remTypeStr = "vara_tithi";
                                    remParams = { "vara": varaParam.currentText, "tithi": tithiParam.currentText };
                                    break;
                                case 5:
                                    remTypeStr = "sankranti";
                                    remParams = {};
                                    break;
                                case 6:
                                    remTypeStr = "festival";
                                    remParams = { "festival_name": festivalParam.text.trim() };
                                    break;
                            }

                            var tTypeStr = "";
                            switch (timeTypeInput.currentIndex) {
                                case 0: tTypeStr = "brahma_muhurta"; break;
                                case 1: tTypeStr = "sunrise"; break;
                                case 2: tTypeStr = "offset_before_sunrise"; break;
                                case 3: tTypeStr = "exact_time"; break;
                            }

                            page.addReminder(
                                titleInput.text.trim(),
                                descInput.text.trim(),
                                remTypeStr,
                                remParams,
                                tTypeStr,
                                parseInt(offsetInput.text) || 0,
                                exactInput.text.trim(),
                                true
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

            // Card 5: Import / Export Registry
            Kirigami.Card {
                Layout.fillWidth: true
                header: RowLayout {
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing
                    Kirigami.Icon { source: "document-share"; implicitWidth: Kirigami.Units.gridUnit * 1.5; implicitHeight: Kirigami.Units.gridUnit * 1.5 }
                    ColumnLayout {
                        spacing: 2
                        Kirigami.Heading { text: i18n("Import & Export Reminders"); level: 3 }
                        Label { text: i18n("Import or export your list of custom repeating reminders."); font.pixelSize: Kirigami.Units.gridUnit * 0.75; opacity: 0.6 }
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

            // Section: Saved Reminders Header
            RowLayout {
                Layout.fillWidth: true
                Label {
                    text: i18n("List of Reminders")
                    font.bold: true
                    font.pixelSize: Kirigami.Units.gridUnit * 1.1
                    Layout.fillWidth: true
                }
                Button {
                    text: i18n("Delete All")
                    icon.name: "edit-clear-all"
                    visible: remindersModel.count > 0 && !page.confirmDeleteAll
                    onClicked: page.confirmDeleteAll = true
                }
                Button {
                    text: i18n("Confirm Delete All?")
                    icon.name: "edit-delete"
                    visible: page.confirmDeleteAll
                    onClicked: {
                        page.confirmDeleteAll = false;
                        page.clearAllReminders();
                    }
                }
                Button {
                    text: i18n("Cancel")
                    visible: page.confirmDeleteAll
                    onClicked: page.confirmDeleteAll = false
                }
            }

            // Saved Reminders Card List
            ColumnLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.largeSpacing

                Repeater {
                    model: remindersModel
                    
                    delegate: Kirigami.Card {
                        id: savedReminderCard
                        Layout.fillWidth: true
                        property bool confirmDelete: false

                        contentItem: ColumnLayout {
                            Layout.margins: Kirigami.Units.largeSpacing
                            spacing: Kirigami.Units.smallSpacing

                            // Top line: Switch and Bold Title
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Kirigami.Units.largeSpacing
                                
                                Switch {
                                    checked: enabled
                                    onToggled: {
                                        page.toggleReminder(id, checked);
                                    }
                                    Accessible.name: i18n("Toggle Reminder")
                                }

                                Label {
                                    text: "🔔 " + title
                                    font.bold: true
                                    font.pixelSize: Kirigami.Units.gridUnit * 1.1
                                    Layout.fillWidth: true
                                }
                            }

                            // Description
                            Label {
                                text: description
                                visible: description !== ""
                                opacity: 0.8
                            }

                            // Trigger rules
                            Label {
                                text: {
                                    var typeStr = (typeof type !== 'undefined') ? type.replace("_", " ").toUpperCase() : "";
                                    var timeTypeStr = (typeof time_type !== 'undefined') ? time_type.replace(/_/g, " ").toUpperCase() : "";
                                    
                                    var params = {};
                                    try {
                                        params = JSON.parse(params_json);
                                    } catch(e) {}
                                    
                                    var paramStr = "";
                                    if (params.tithi) paramStr += "Tithi: " + params.tithi + " ";
                                    if (params.paksha) paramStr += "Paksha: " + params.paksha + " ";
                                    if (params.masa) paramStr += "Masa: " + params.masa + " ";
                                    if (params.nakshatra) paramStr += "Nakshatra: " + params.nakshatra + " ";
                                    if (params.vara) paramStr += "Vara: " + params.vara + " ";
                                    if (params.festival_name) paramStr += "Festival: " + params.festival_name + " ";
                                    
                                    return `<b>Rule</b>: ${typeStr} (${paramStr.trim()})<br/><b>Schedule</b>: ${timeTypeStr}` +
                                           (time_type === "offset_before_sunrise" ? ` (${time_offset_mins} mins offset)` : "") +
                                           (time_type === "exact_time" ? ` (at ${time_exact_str})` : "");
                                }
                                textFormat: Text.RichText
                                font.pixelSize: Kirigami.Units.gridUnit * 0.85
                                opacity: 0.7
                            }

                            // Actions
                            RowLayout {
                                Layout.topMargin: Kirigami.Units.smallSpacing
                                spacing: Kirigami.Units.largeSpacing

                                Button {
                                    text: i18n("Edit")
                                    icon.name: "edit-rename"
                                    visible: !confirmDelete
                                    onClicked: {
                                        var tTitle = (typeof title !== 'undefined') ? title : "";
                                        var tDesc = (typeof description !== 'undefined') ? description : "";
                                        var tType = (typeof type !== 'undefined') ? type : "";
                                        var tParams = {};
                                        try {
                                            tParams = JSON.parse(params_json);
                                        } catch(e) {}
                                        
                                        var tTimeType = (typeof time_type !== 'undefined') ? time_type : "sunrise";
                                        var tOffset = (typeof time_offset_mins !== 'undefined') ? time_offset_mins : 0;
                                        var tExact = (typeof time_exact_str !== 'undefined') ? time_exact_str : "";
                                        var tId = (typeof id !== 'undefined') ? id : "";
                                        
                                        titleInput.text = tTitle;
                                        descInput.text = tDesc;
                                        
                                        var typeIdx = 0;
                                        if (tType === "tithi") typeIdx = 0;
                                        else if (tType === "paksha_tithi") typeIdx = 1;
                                        else if (tType === "masa_paksha_tithi") typeIdx = 2;
                                        else if (tType === "nakshatra") typeIdx = 3;
                                        else if (tType === "vara_tithi") typeIdx = 4;
                                        else if (tType === "sankranti") typeIdx = 5;
                                        else if (tType === "festival") typeIdx = 6;
                                        typeInput.currentIndex = typeIdx;
                                        
                                        if (typeIdx === 0 || typeIdx === 1 || typeIdx === 2 || typeIdx === 4) {
                                            tithiParam.currentIndex = [
                                                "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami",
                                                "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima", "Amavasya"
                                            ].indexOf(tParams.tithi || "Pratipada");
                                        }
                                        if (typeIdx === 1 || typeIdx === 2) {
                                            pakshaParam.currentIndex = ["Shukla", "Krishna"].indexOf(tParams.paksha || "Shukla");
                                        }
                                        if (typeIdx === 2) {
                                            masaParam.currentIndex = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"].indexOf(tParams.masa || "Chaitra");
                                        }
                                        if (typeIdx === 3) {
                                            nakshatraParam.currentIndex = [
                                                "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
                                                "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Svati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
                                                "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
                                            ].indexOf(tParams.nakshatra || "Ashwini");
                                        }
                                        if (typeIdx === 4) {
                                            varaParam.currentIndex = ["Indu", "Bhauma", "Saumya", "Guru", "Bhargava", "Sthira", "Bhanu"].indexOf(tParams.vara || "Indu");
                                        }
                                        if (typeIdx === 6) {
                                            festivalParam.text = tParams.festival_name || "";
                                        }
                                        
                                        var timeIdx = 1;
                                        if (tTimeType === "brahma_muhurta") timeIdx = 0;
                                        else if (tTimeType === "sunrise") timeIdx = 1;
                                        else if (tTimeType === "offset_before_sunrise") timeIdx = 2;
                                        else if (tTimeType === "exact_time") timeIdx = 3;
                                        timeTypeInput.currentIndex = timeIdx;
                                        
                                        offsetInput.text = String(tOffset);
                                        exactInput.text = tExact;
                                        
                                        page.deleteReminder(tId);
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
                                        page.deleteReminder((typeof id !== 'undefined') ? id : "");
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
        loadReminders();
    }
}
