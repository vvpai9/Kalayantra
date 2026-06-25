import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: fullRoot
    implicitWidth: 720
    implicitHeight: 500

    Layout.preferredWidth: implicitWidth
    Layout.preferredHeight: implicitHeight
    Layout.minimumWidth: 640
    Layout.minimumHeight: 440
    
    property var selectedDayData: null
    property var gridItems: []

    // Hindu month navigation state
    property string selectedMasaName: ""
    property int selectedShakaYear: 0
    property string pendingSelectDate: ""
    property var selectedMonthDays: []

    onSelectedMasaNameChanged: updateGrid()
    onSelectedShakaYearChanged: updateGrid()

    // Helper to format Gregorian Month name
    function getGregorianMonthName(m) {
        var names = [
            i18n("January"), i18n("February"), i18n("March"), i18n("April"), 
            i18n("May"), i18n("June"), i18n("July"), i18n("August"), 
            i18n("September"), i18n("October"), i18n("November"), i18n("December")
        ];
        return names[m - 1];
    }

    // Filter and update the active grid list
    function updateGrid() {
        var days = [];
        if (root.threeMonthsData) {
            for (var i = 0; i < root.threeMonthsData.length; i++) {
                var day = root.threeMonthsData[i];
                if (day && day.masa === selectedMasaName && day.shaka_year === selectedShakaYear) {
                    days.push(day);
                }
            }
        }
        selectedMonthDays = days;
        gridItems = generateHinduGridItems(days);
    }

    function generateHinduGridItems(days) {
        if (!days || days.length === 0) return [];
        
        var grid = [];
        
        // Find the weekday of the first day
        var firstDayDate = new Date(days[0].date);
        var firstWeekday = firstDayDate.getDay(); // 0 = Sunday, 1 = Monday, ..., 6 = Saturday
        
        // Front padding
        for (var i = 0; i < firstWeekday; i++) {
            grid.push({ "type": "empty" });
        }
        
        // Days
        for (var d = 0; d < days.length; d++) {
            var dayData = days[d];
            dayData.type = "day";
            grid.push(dayData);
        }
        
        // End padding to fill up to 42 cells
        while (grid.length < 42) {
            grid.push({ "type": "empty" });
        }
        
        return grid;
    }

    function prevHinduMonth() {
        var days = selectedMonthDays;
        if (days.length === 0) return;
        
        var parts = days[0].date.split('-');
        var date = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
        date.setDate(date.getDate() - 15);
        
        var targetY = date.getFullYear();
        var targetM = date.getMonth() + 1;
        var targetD = date.getDate();
        
        root.currentYear = targetY;
        root.currentMonth = targetM;
        
        pendingSelectDate = `${targetY}-${String(targetM).padStart(2, '0')}-${String(targetD).padStart(2, '0')}`;
        root.fetchThreeMonths(targetY, targetM);
    }

    function nextHinduMonth() {
        var days = selectedMonthDays;
        if (days.length === 0) return;
        
        var parts = days[days.length - 1].date.split('-');
        var date = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
        date.setDate(date.getDate() + 15);
        
        var targetY = date.getFullYear();
        var targetM = date.getMonth() + 1;
        var targetD = date.getDate();
        
        root.currentYear = targetY;
        root.currentMonth = targetM;
        
        pendingSelectDate = `${targetY}-${String(targetM).padStart(2, '0')}-${String(targetD).padStart(2, '0')}`;
        root.fetchThreeMonths(targetY, targetM);
    }

    // Refresh grid items when three-month window data changes
    function initializeData() {
        if (root.threeMonthsData && root.threeMonthsData.length > 0) {
            var targetDate = pendingSelectDate;
            if (!targetDate) {
                targetDate = root.getTodayString();
            }
            
            // Find the day with targetDate in threeMonthsData
            var foundDay = null;
            for (var i = 0; i < root.threeMonthsData.length; i++) {
                if (root.threeMonthsData[i] && root.threeMonthsData[i].date === targetDate) {
                    foundDay = root.threeMonthsData[i];
                    break;
                }
            }
            
            // If not found, fall back to first day in threeMonthsData
            if (!foundDay && root.threeMonthsData.length > 0) {
                foundDay = root.threeMonthsData[0];
            }
            
            if (foundDay) {
                selectedMasaName = foundDay.masa;
                selectedShakaYear = foundDay.shaka_year;
            }
            
            updateGrid();
            
            // Also select the day in details panel
            if (foundDay) {
                var foundTargetInMonth = null;
                for (var j = 0; j < selectedMonthDays.length; j++) {
                    if (selectedMonthDays[j].date === targetDate) {
                        foundTargetInMonth = selectedMonthDays[j];
                        break;
                    }
                }
                if (foundTargetInMonth) {
                    selectedDayData = foundTargetInMonth;
                } else if (selectedMonthDays.length > 0) {
                    selectedDayData = selectedMonthDays[0];
                }
            }
            
            pendingSelectDate = "";
        }
    }

    Component.onCompleted: {
        initializeData();
    }

    // Refresh grid items when three-month window data changes
    Connections {
        target: root

        function onThreeMonthsDataChanged() {
            initializeData();
        }
    }

    GridLayout {
        anchors.fill: parent
        anchors.margins: Kirigami.Units.largeSpacing
        columns: width > Kirigami.Units.gridUnit * 28 ? 2 : 1
        rows: width > Kirigami.Units.gridUnit * 28 ? 1 : 2
        columnSpacing: Kirigami.Units.largeSpacing
        rowSpacing: Kirigami.Units.largeSpacing

        // Left/Top Panel: Calendar Control & Grid
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Kirigami.Units.largeSpacing

            // Month Navigation Header
            RowLayout {
                Layout.fillWidth: true
                
                Button {
                    icon.name: "go-previous"
                    flat: true
                    onClicked: prevHinduMonth()
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    
                    Kirigami.Heading {
                        level: 3
                        text: `${selectedMasaName} ${selectedDayData ? selectedDayData.paksha : ""} Paksha`
                        font.bold: true
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        color: Kirigami.Theme.highlightColor
                    }

                    Label {
                        text: `Śaka ${selectedShakaYear}`
                        font.bold: true
                        font.pixelSize: Kirigami.Units.gridUnit * 0.8
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                    }

                    Label {
                        text: {
                            var days = selectedMonthDays;
                            if (days.length === 0) return "";
                            var startDay = days[0];
                            var endDay = days[days.length - 1];
                            
                            var startParts = startDay.date.split('-');
                            var endParts = endDay.date.split('-');
                            
                            var getShortMonthName = function(m) {
                                var names = [
                                    i18n("Jan"), i18n("Feb"), i18n("Mar"), i18n("Apr"), 
                                    i18n("May"), i18n("Jun"), i18n("Jul"), i18n("Aug"), 
                                    i18n("Sep"), i18n("Oct"), i18n("Nov"), i18n("Dec")
                                ];
                                return names[m - 1];
                            };
                            
                            var startMonth = getShortMonthName(parseInt(startParts[1]));
                            var endMonth = getShortMonthName(parseInt(endParts[1]));
                            
                            var startD = parseInt(startParts[2]);
                            var endD = parseInt(endParts[2]);
                            
                            var startY = startParts[0];
                            var endY = endParts[0];
                            
                            if (startY === endY) {
                                return `${startD} ${startMonth} – ${endD} ${endMonth} ${startY}`;
                            } else {
                                return `${startD} ${startMonth} ${startY} – ${endD} ${endMonth} ${endY}`;
                            }
                        }
                        opacity: 0.7
                        font.pixelSize: Kirigami.Units.gridUnit * 0.75
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                    }
                }

                Button {
                    icon.name: "go-next"
                    flat: true
                    onClicked: nextHinduMonth()
                }
            }

            // Days of the week header
            GridLayout {
                columns: 7
                Layout.fillWidth: true
                columnSpacing: Kirigami.Units.smallSpacing
                rowSpacing: 0
                
                Repeater {
                    model: [
                        i18n("Sun"), i18n("Mon"), i18n("Tue"), i18n("Wed"), 
                        i18n("Thu"), i18n("Fri"), i18n("Sat")
                    ]
                    
                    Label {
                        text: modelData
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize: Kirigami.Units.gridUnit * 0.75
                        opacity: 0.8
                        Layout.fillWidth: true
                    }
                }
            }

            // 6x7 Calendar Grid
            GridLayout {
                id: calendarGrid
                columns: 7
                rows: 6
                Layout.fillWidth: true
                Layout.fillHeight: true
                columnSpacing: Kirigami.Units.smallSpacing
                rowSpacing: Kirigami.Units.smallSpacing

                Repeater {
                    model: fullRoot.gridItems

                    Item {
                        id: cell
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        visible: modelData.type !== "empty"

                        Rectangle {
                            anchors.fill: parent
                            radius: 4
                            border.width: 1
                            
                            // Visual theme logic based on Shukla/Krishna Pakshas
                            color: {
                                if (modelData.type === "empty") return "transparent";
                                if (modelData.is_krishna_paksha) {
                                    return cellMouse.containsMouse ? "#1c252c" : "#121b22";
                                } else {
                                    return cellMouse.containsMouse ? "#2f270a" : "#201a05";
                                }
                            }
                            
                            border.color: {
                                if (fullRoot.selectedDayData && fullRoot.selectedDayData.date === modelData.date) {
                                    return Kirigami.Theme.highlightColor;
                                }
                                if (modelData.date === root.getTodayString()) {
                                    return "#3daee9"; // Cyan outline for actual today's date
                                }
                                return modelData.is_krishna_paksha ? "#2e3b46" : "#c69b12";
                            }

                            // Dynamic cell text content
                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 1
                                
                                Label {
                                    text: modelData.type === "day" ? modelData.tithi_num : ""
                                    font.bold: true
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.85
                                    color: modelData.is_krishna_paksha ? "#9eb1c2" : "#ffe473"
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                Label {
                                    text: modelData.type === "day" ? `(${parseInt(modelData.date.split('-')[2])})` : ""
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.55
                                    opacity: 0.7
                                    color: modelData.is_krishna_paksha ? "#9eb1c2" : "#ffe473"
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }

                            // Indicator dot for festival presence
                            Rectangle {
                                anchors.top: parent.top
                                anchors.right: parent.right
                                anchors.margins: 4
                                width: 5
                                height: 5
                                radius: 2.5
                                color: "#ff4d4d"
                                visible: modelData && modelData.festivals ? modelData.festivals.length > 0 : false
                            }
                        }

                        MouseArea {
                            id: cellMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                fullRoot.selectedDayData = modelData;
                            }
                        }
                    }
                }
            }
        }

        // Right/Bottom Panel: Panchanga Details Card
        Kirigami.Card {
            id: detailsCard
            Layout.fillWidth: false
            Layout.fillHeight: true
            Layout.minimumWidth: 240
            Layout.preferredWidth: 270
            
            // Slate/Warm tinted card background depending on Paksha
            background: Rectangle {
                radius: 8
                color: {
                    if (!fullRoot.selectedDayData) return Kirigami.Theme.backgroundColor;
                    return fullRoot.selectedDayData.is_krishna_paksha ? "#141c22" : "#1a1608";
                }
                border.color: fullRoot.selectedDayData && fullRoot.selectedDayData.is_krishna_paksha ? "#2e3b46" : "#d4af37"
                border.width: 1.5
            }

            contentItem: Flickable {
                clip: true
                contentHeight: detailsLayout.implicitHeight
                
                ColumnLayout {
                    id: detailsLayout
                    width: parent.width
                    spacing: Kirigami.Units.largeSpacing

                    // Detail Card Header
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Label {
                            text: fullRoot.selectedDayData ? fullRoot.selectedDayData.date : ""
                            font.pixelSize: Kirigami.Units.gridUnit * 0.75
                            opacity: 0.8
                        }

                        Kirigami.Heading {
                            level: 2
                            text: fullRoot.selectedDayData ? fullRoot.selectedDayData.tithi : i18n("Select a day")
                            color: fullRoot.selectedDayData && fullRoot.selectedDayData.is_krishna_paksha ? "#7094b3" : "#ffcc00"
                            font.bold: true
                        }

                        Label {
                            text: fullRoot.selectedDayData ? `${fullRoot.selectedDayData.paksha} Paksha • ${fullRoot.selectedDayData.vaara}` : ""
                            font.bold: true
                            font.pixelSize: Kirigami.Units.gridUnit * 0.85
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }
                    }

                    Kirigami.Separator { Layout.fillWidth: true }

                    // Detailed Astronomical Grid
                    GridLayout {
                        columns: 2
                        rowSpacing: Kirigami.Units.smallSpacing
                        columnSpacing: Kirigami.Units.largeSpacing
                        Layout.fillWidth: true

                        // Row: Masa
                        Label { text: i18n("Masa (Month):"); font.bold: true; opacity: 0.8 }
                        Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.masa : "--"; Layout.fillWidth: true; wrapMode: Text.WordWrap }

                        // Row: Nakshatra
                        Label { text: i18n("Nakshatra:"); font.bold: true; opacity: 0.8 }
                        Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.nakshatra : "--"; Layout.fillWidth: true; wrapMode: Text.WordWrap }

                        // Row: Yoga
                        Label { text: i18n("Yoga:"); font.bold: true; opacity: 0.8 }
                        Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.yoga : "--"; Layout.fillWidth: true; wrapMode: Text.WordWrap }

                        // Row: Karana
                        Label { text: i18n("Karana:"); font.bold: true; opacity: 0.8 }
                        Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.karana : "--"; Layout.fillWidth: true; wrapMode: Text.WordWrap }

                        // Row: Ritu & Ayana
                        Label { text: i18n("Ritu & Ayana:"); font.bold: true; opacity: 0.8 }
                        Label { text: fullRoot.selectedDayData ? `${fullRoot.selectedDayData.ritu} • ${fullRoot.selectedDayData.ayana}` : "--"; Layout.fillWidth: true; wrapMode: Text.WordWrap }

                        // Row: Jovian Samvatsara & Years
                        Label { text: i18n("Samvatsara:"); font.bold: true; opacity: 0.8 }
                        Label { 
                            text: fullRoot.selectedDayData ? `${fullRoot.selectedDayData.samvatsara}` : "--"
                            font.bold: true
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        Label { text: i18n("Era Years:"); font.bold: true; opacity: 0.8 }
                        Label { 
                            text: fullRoot.selectedDayData ? `Shaka ${fullRoot.selectedDayData.shaka_year} • Vikram ${fullRoot.selectedDayData.vikram_year} • Kali ${fullRoot.selectedDayData.kali_year}` : "--"
                            font.pixelSize: Kirigami.Units.gridUnit * 0.7
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }
                    }

                    Kirigami.Separator { Layout.fillWidth: true }

                    // Sunrise, Sunset, Moonrise, Moonset Timings
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing

                        Label { text: i18n("Daily Sun & Moon Times:"); font.bold: true }
                        
                        RowLayout {
                            spacing: Kirigami.Units.largeSpacing
                            
                            ColumnLayout {
                                spacing: 2
                                Label { text: `☀️ Rise: ${fullRoot.selectedDayData ? fullRoot.selectedDayData.sunrise : "--"}` }
                                Label { text: `☀️ Set:  ${fullRoot.selectedDayData ? fullRoot.selectedDayData.sunset : "--"}` }
                            }

                            ColumnLayout {
                                spacing: 2
                                Label { text: `🌙 Rise: ${fullRoot.selectedDayData ? fullRoot.selectedDayData.moonrise : "--"}` }
                                Label { text: `🌙 Set:  ${fullRoot.selectedDayData ? fullRoot.selectedDayData.moonset : "--"}` }
                            }
                        }
                    }

                    // Auspicious/Inauspicious segments
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing

                        Label { text: i18n("Auspicious / Inauspicious Periods:"); font.bold: true }
                        
                        GridLayout {
                            columns: 2
                            rowSpacing: 2
                            columnSpacing: Kirigami.Units.largeSpacing

                            Label { text: "Abhijit Muhurta:" }
                            Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.abhijit_muhurta : "--"; font.bold: true; color: "#2ecc71" }

                            Label { text: "Rahu Kala:" }
                            Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.rahu_kala : "--"; font.bold: true; color: "#e74c3c" }

                            Label { text: "Yamaganda:" }
                            Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.yamaganda : "--" }

                            Label { text: "Gulika:" }
                            Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.gulika : "--" }
                        }
                    }

                    // Festivals & Observances
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing
                        visible: fullRoot.selectedDayData && fullRoot.selectedDayData.festivals && fullRoot.selectedDayData.festivals.length > 0

                        Label { text: i18n("Festivals & Observances:"); font.bold: true; color: "#ff4d4d" }
                        
                        Repeater {
                            model: fullRoot.selectedDayData ? fullRoot.selectedDayData.festivals : []
                            Label {
                                text: `• ${modelData}`
                                font.bold: true
                                font.pixelSize: Kirigami.Units.gridUnit * 0.8
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                            }
                        }
                    }

                    // Live Ghadi-Vipal Display (Only visible for today's selected day)
                    RowLayout {
                        Layout.fillWidth: true
                        visible: fullRoot.selectedDayData && fullRoot.selectedDayData.date === root.getTodayString()
                        
                        Label {
                            text: i18n("Current Ghadi:Vipal time:")
                            font.bold: true
                        }
                        
                        Label {
                            text: root.liveGhadiTime
                            font.bold: true
                            font.pixelSize: Kirigami.Units.gridUnit * 1.1
                            color: "#e67e22"
                        }
                    }
                }
            }
        }
    }
}
