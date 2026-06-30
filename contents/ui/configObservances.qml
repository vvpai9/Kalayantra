import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
    id: observancesPage

    ListModel {
        id: observancesModel
    }

    FileDialog {
        id: importFileDialog
        title: i18n("Select JSON file to import saved tithis")
        nameFilters: ["JSON files (*.json)"]
        onAccepted: {
            var path = selectedFile.toString();
            if (path.startsWith("file://")) {
                path = path.substring(7);
            }
            path = decodeURIComponent(path);
            
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "http://127.0.0.1:8642/import_custom_observances?filepath=" + encodeURIComponent(path), true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        loadObservances();
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
            xhr.open("GET", "http://127.0.0.1:8642/export_custom_observances?filepath=" + encodeURIComponent(path), true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        // Export successful
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
        xhr.open("GET", "http://127.0.0.1:8642/get_custom_observances", true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    observancesModel.clear();
                    for (var i = 0; i < data.length; i++) {
                        observancesModel.append(data[i]);
                    }
                } catch(e) {
                    console.error("Failed to parse custom observances:", e);
                }
            }
        };
        xhr.send();
    }

    function addObservance(name, month, paksha, tithi) {
        var xhr = new XMLHttpRequest();
        var query = "name=" + encodeURIComponent(name) +
                    "&month=" + encodeURIComponent(month) +
                    "&paksha=" + encodeURIComponent(paksha) +
                    "&tithi=" + encodeURIComponent(tithi);
        xhr.open("GET", "http://127.0.0.1:8642/save_custom_observance?" + query, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                loadObservances();
                nameInput.text = "";
            }
        };
        xhr.send();
    }

    function deleteObservance(id) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/delete_custom_observance?id=" + encodeURIComponent(id), true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                loadObservances();
            }
        };
        xhr.send();
    }

    Component.onCompleted: {
        loadObservances();
    }

    Kirigami.Separator {
        Kirigami.FormData.isSection: true
        Kirigami.FormData.label: i18n("Add Custom Observance")
    }

    Controls.TextField {
        id: nameInput
        Kirigami.FormData.label: i18n("Observance Name:")
        placeholderText: i18n("e.g. Janmadin")
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

    RowLayout {
        spacing: Kirigami.Units.largeSpacing
        Controls.Button {
            text: i18n("Add Observance")
            onClicked: {
                if (nameInput.text.trim() !== "") {
                    addObservance(nameInput.text.trim(), monthInput.currentText, pakshaInput.currentText, tithiInput.currentText);
                }
            }
        }

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
        Kirigami.FormData.label: i18n("Existing Observances")
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: Kirigami.Units.smallSpacing

        Repeater {
            model: observancesModel
            delegate: RowLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.largeSpacing
                
                Controls.Label {
                    text: model.name + " (" + model.month + " " + model.paksha + " " + model.tithi + ")"
                    Layout.fillWidth: true
                }

                Controls.Button {
                    text: i18n("Edit")
                    onClicked: {
                        nameInput.text = model.name;
                        monthInput.currentIndex = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"].indexOf(model.month);
                        pakshaInput.currentIndex = ["Shukla", "Krishna"].indexOf(model.paksha);
                        tithiInput.currentIndex = [
                            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", "Saptami", "Ashtami",
                            "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima", "Amavasya"
                        ].indexOf(model.tithi);
                        deleteObservance(model.id);
                    }
                }

                Controls.Button {
                    text: i18n("Delete")
                    onClicked: {
                        deleteObservance(model.id);
                    }
                }
            }
        }
    }
}
