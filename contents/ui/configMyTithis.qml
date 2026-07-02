import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts as Layouts
import QtQuick.Dialogs
import org.kde.kirigami as Kirigami

Item {
    id: configMyTithisRoot
    implicitHeight: mainLayout.implicitHeight
    width: parent ? parent.width : 600
    property bool confirmDeleteAll: false

    ListModel {
        id: observancesModel
    }

    Timer {
        id: reloadTimer
        interval: 50
        running: false
        repeat: false
        onTriggered: {
            configMyTithisRoot.loadObservances();
        }
    }

    FileDialog {
        id: importFileDialog
        title: i18n("Select JSON file to import saved tithis")
        nameFilters: ["JSON files (*.json)"]
        fileMode: FileDialog.OpenFile
        onAccepted: {
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
                    if (xhr.status === 200) {
                        reloadTimer.start();
                    } else {
                        console.error("Failed to import:", xhr.responseText);
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
                    if (xhr.status === 200) {
                        // Success
                    } else {
                        console.error("Failed to export:", xhr.responseText);
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
                    configMyTithisRoot.syncModel(data);
                } catch(e) {
                    console.error("Failed to parse tithis:", e);
                }
            }
        };
        xhr.send();
    }

    function syncModel(data) {
        // 1. Remove items from local model that are not present in backend
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
        
        // 2. Add or update items from backend
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
            if (existingIndex === -1) {
                observancesModel.append({
                    "id": bItem.id,
                    "name": bItem.name,
                    "month": bItem.month,
                    "paksha": bItem.paksha,
                    "tithi": bItem.tithi,
                    "system": sysB
                });
            } else {
                var local = observancesModel.get(existingIndex);
                var sysL = local.system || "amavasyanta";
                if (local.name !== bItem.name || 
                    local.month !== bItem.month || 
                    local.paksha !== bItem.paksha || 
                    local.tithi !== bItem.tithi || 
                    sysL !== sysB) {
                    observancesModel.set(existingIndex, {
                        "id": bItem.id,
                        "name": bItem.name,
                        "month": bItem.month,
                        "paksha": bItem.paksha,
                        "tithi": bItem.tithi,
                        "system": sysB
                    });
                }
            }
        }
    }

    function addObservance(name, month, paksha, tithi, system) {
        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        var query = "name=" + encodeURIComponent(name) +
                    "&month=" + encodeURIComponent(month) +
                    "&paksha=" + encodeURIComponent(paksha) +
                    "&tithi=" + encodeURIComponent(tithi) +
                    "&system=" + encodeURIComponent(system) +
                    "&" + buster;
        xhr.open("GET", "http://127.0.0.1:8642/save_custom_observance?" + query, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    reloadTimer.start();
                    nameInput.text = "";
                    errorAlert.visible = false;
                } else {
                    try {
                        var errData = JSON.parse(xhr.responseText);
                        errorAlert.text = errData.error || i18n("Tithi already exists!");
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
        // Remove locally first for instant feedback and clean delegate lifecycle destruction
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

    Component.onCompleted: {
        loadObservances();
    }

    Layouts.ColumnLayout {
        id: mainLayout
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        spacing: Kirigami.Units.largeSpacing

        Kirigami.FormLayout {
            id: formLayout
            Layouts.Layout.fillWidth: true

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: i18n("Add My Tithi")
            }

            Kirigami.InlineMessage {
                id: errorAlert
                type: Kirigami.MessageType.Error
                text: i18n("Tithi already exists!")
                visible: false
                Layouts.Layout.fillWidth: true
                showCloseButton: true
            }

            Timer {
                id: errorHideTimer
                interval: 5000
                running: false
                repeat: false
                onTriggered: errorAlert.visible = false
            }

            Controls.TextField {
                id: nameInput
                Kirigami.FormData.label: i18n("Tithi Name:")
                placeholderText: i18n("e.g. Janmadin")
                onTextChanged: errorAlert.visible = false
            }

            Controls.ComboBox {
                id: monthInput
                Kirigami.FormData.label: i18n("Hindu Month:")
                model: ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"]
            }

            Controls.ComboBox {
                id: pakshaInput
                Kirigami.FormData.label: i18n("Paksha:")
                model: ["Shukla", "Krishna"]
            }

            Controls.ComboBox {
                id: tithiInput
                Kirigami.FormData.label: i18n("Tithi:")
                model: [
                    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami",
                    "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima", "Amavasya"
                ]
            }

            Controls.ComboBox {
                id: systemInput
                Kirigami.FormData.label: i18n("Month System:")
                model: ["Amavasyanta", "Purnimanta"]
            }

            Controls.Button {
                text: i18n("Add Tithi")
                onClicked: {
                    if (nameInput.text.trim() !== "") {
                        configMyTithisRoot.addObservance(nameInput.text.trim(), monthInput.currentText, pakshaInput.currentText, tithiInput.currentText, systemInput.currentText.toLowerCase());
                    }
                }
            }

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: i18n("Import & Export My Tithis")
            }

            Layouts.RowLayout {
                spacing: Kirigami.Units.largeSpacing
                
                Controls.Button {
                    text: i18n("Import from File...")
                    icon.name: "document-import"
                    onClicked: importFileDialog.open()
                }

                Controls.Button {
                    text: i18n("Export to File...")
                    icon.name: "document-export"
                    onClicked: exportFileDialog.open()
                }
            }

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: i18n("My Tithis")
            }
        }

        Layouts.RowLayout {
            Layouts.Layout.fillWidth: true
            Layouts.Layout.leftMargin: Kirigami.Units.largeSpacing
            Layouts.Layout.rightMargin: Kirigami.Units.largeSpacing
            
            Controls.Label {
                text: i18n("List of Saved Tithis:")
                font.bold: true
                Layouts.Layout.fillWidth: true
            }
            Controls.Button {
                text: i18n("Delete All")
                icon.name: "edit-clear-all"
                visible: observancesModel.count > 0 && !configMyTithisRoot.confirmDeleteAll
                onClicked: {
                    configMyTithisRoot.confirmDeleteAll = true;
                }
            }
            Controls.Button {
                text: i18n("Confirm Delete All?")
                visible: configMyTithisRoot.confirmDeleteAll
                contentItem: Controls.Label {
                    text: parent.text
                    color: Kirigami.Theme.negativeTextColor
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: {
                    configMyTithisRoot.confirmDeleteAll = false;
                    configMyTithisRoot.clearAllObservances();
                }
            }
            Controls.Button {
                text: i18n("Cancel")
                visible: configMyTithisRoot.confirmDeleteAll
                onClicked: {
                    configMyTithisRoot.confirmDeleteAll = false;
                }
            }
        }

        ListView {
            id: listView
            Layouts.Layout.fillWidth: true
            interactive: false
            height: contentHeight
            model: observancesModel
            
            delegate: Item {
                id: delegateItem
                width: listView.width
                height: rowLayout.implicitHeight + Kirigami.Units.smallSpacing * 2
                property bool confirmDelete: false

                Layouts.RowLayout {
                    id: rowLayout
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.leftMargin: Kirigami.Units.largeSpacing
                    anchors.rightMargin: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.largeSpacing

                    Controls.Label {
                        text: {
                            var n = (typeof name !== 'undefined' && name) ? name : "";
                            var m = (typeof month !== 'undefined' && month) ? month : "";
                            var p = (typeof paksha !== 'undefined' && paksha) ? paksha : "";
                            var t = (typeof tithi !== 'undefined' && tithi) ? tithi : "";
                            var s = (typeof system !== 'undefined' && system) ? system.toUpperCase() : "AMAVASYANTA";
                            return n + " (" + m + " " + p + " " + t + " - " + s + ")";
                        }
                        Layouts.Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    Controls.Button {
                        text: i18n("Edit")
                        visible: !delegateItem.confirmDelete
                        onClicked: {
                            var tName = (typeof name !== 'undefined') ? name : "";
                            var tMonth = (typeof month !== 'undefined') ? month : "";
                            var tPaksha = (typeof paksha !== 'undefined') ? paksha : "";
                            var tTithi = (typeof tithi !== 'undefined') ? tithi : "";
                            var tSystem = (typeof system !== 'undefined') ? system : "amavasyanta";
                            var tId = (typeof id !== 'undefined') ? id : "";
                            
                            nameInput.text = tName;
                            monthInput.currentIndex = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"].indexOf(tMonth);
                            pakshaInput.currentIndex = ["Shukla", "Krishna"].indexOf(tPaksha);
                            tithiInput.currentIndex = [
                                "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami",
                                "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima", "Amavasya"
                            ].indexOf(tTithi);
                            systemInput.currentIndex = ["amavasyanta", "purnimanta"].indexOf(tSystem);
                            configMyTithisRoot.deleteObservance(tId);
                        }
                    }

                    Controls.Button {
                        text: i18n("Delete")
                        visible: !delegateItem.confirmDelete
                        onClicked: {
                            delegateItem.confirmDelete = true;
                        }
                    }

                    Controls.Button {
                        text: i18n("Confirm Delete?")
                        visible: delegateItem.confirmDelete
                        contentItem: Controls.Label {
                            text: parent.text
                            color: Kirigami.Theme.negativeTextColor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        onClicked: {
                            delegateItem.confirmDelete = false;
                            configMyTithisRoot.deleteObservance((typeof id !== 'undefined') ? id : "");
                        }
                    }

                    Controls.Button {
                        text: i18n("Cancel")
                        visible: delegateItem.confirmDelete
                        onClicked: {
                            delegateItem.confirmDelete = false;
                        }
                    }
                }

                Kirigami.Separator {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                }
            }
        }
    }
}
