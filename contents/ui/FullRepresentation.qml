import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: fullRoot
    implicitWidth: 1024
    implicitHeight: 640

    Layout.preferredWidth: implicitWidth
    Layout.preferredHeight: implicitHeight
    Layout.minimumWidth: 900
    Layout.minimumHeight: 580
    
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
        var parts = days[0].date.split('-');
        var firstDayDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
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

    // Slide animation properties
    property string slideDirection: "none"
    property string tempMasaName: ""
    property int tempShakaYear: 0
    property string tempTargetDate: ""

    function commitGridData() {
        selectedMasaName = tempMasaName;
        selectedShakaYear = tempShakaYear;
        updateGrid();
        
        if (tempTargetDate) {
            var foundTargetInMonth = null;
            for (var j = 0; j < selectedMonthDays.length; j++) {
                if (selectedMonthDays[j].date === tempTargetDate) {
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
    }

    SequentialAnimation {
        id: slideAnimation
        
        ParallelAnimation {
            NumberAnimation {
                target: calendarGrid
                property: "x"
                to: slideDirection === "next" ? -150 : (slideDirection === "prev" ? 150 : 0)
                duration: 120
                easing.type: Easing.OutQuad
            }
            NumberAnimation {
                target: calendarGrid
                property: "opacity"
                to: slideDirection === "none" ? 1.0 : 0.0
                duration: 120
            }
        }
        
        ScriptAction {
            script: {
                commitGridData();
                calendarGrid.x = slideDirection === "next" ? 150 : (slideDirection === "prev" ? -150 : 0);
            }
        }
        
        ParallelAnimation {
            NumberAnimation {
                target: calendarGrid
                property: "x"
                to: 0
                duration: 150
                easing.type: Easing.OutQuad
            }
            NumberAnimation {
                target: calendarGrid
                property: "opacity"
                to: 1.0
                duration: 150
            }
        }
        
        onFinished: {
            slideDirection = "none";
        }
    }

    function prevHinduMonth() {
        slideDirection = "prev";
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
        slideDirection = "next";
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

    function initializeData() {
        if (root.threeMonthsData && root.threeMonthsData.length > 0) {
            var targetDate = pendingSelectDate;
            if (!targetDate) {
                targetDate = root.getTodayString();
            }
            
            var foundDay = null;
            for (var i = 0; i < root.threeMonthsData.length; i++) {
                if (root.threeMonthsData[i] && root.threeMonthsData[i].date === targetDate) {
                    foundDay = root.threeMonthsData[i];
                    break;
                }
            }
            
            if (!foundDay && root.threeMonthsData.length > 0) {
                foundDay = root.threeMonthsData[0];
            }
            
            if (foundDay) {
                tempMasaName = foundDay.masa;
                tempShakaYear = foundDay.shaka_year;
                tempTargetDate = targetDate;
                
                if (slideDirection === "none") {
                    commitGridData();
                } else {
                    slideAnimation.start();
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
                        text: (selectedMonthDays && selectedMonthDays.length > 0) ? `${selectedMonthDays[0].era_name} ${selectedMonthDays[0].era_year}` : `Śaka ${selectedShakaYear}`
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

            // Viewport container to enable slide/swipe animations
            Item {
                id: gridViewport
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                // Calendar Grid containing both Week Header and Days
                GridLayout {
                    id: calendarGrid
                    width: parent.width
                    height: parent.height
                    columns: 7
                    columnSpacing: Kirigami.Units.smallSpacing
                    rowSpacing: Kirigami.Units.smallSpacing

                // Weekday Header Labels (Row 1)
                Repeater {
                    model: [
                        i18n("Bhanu"), i18n("Indu"), i18n("Bhauma"), i18n("Saumya"), 
                        i18n("Guru"), i18n("Bhargava"), i18n("Sthira")
                    ]
                    
                    Label {
                        text: modelData
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize: Kirigami.Units.gridUnit * 0.7
                        opacity: 0.8
                        Layout.fillWidth: true
                        Layout.preferredWidth: 0
                    }
                }

                // Calendar Days (Rows 2-7)
                Repeater {
                    model: fullRoot.gridItems

                    Item {
                        id: cell
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.preferredWidth: 0

                        Rectangle {
                            anchors.fill: parent
                            radius: 4
                            border.width: 1
                            visible: modelData && modelData.type === "day"
                            
                            // Visual theme logic based on Shukla/Krishna Pakshas
                            color: {
                                if (!modelData || modelData.type !== "day") return "transparent";
                                if (modelData.is_krishna_paksha) {
                                    return cellMouse.containsMouse ? "#1c252c" : "#121b22";
                                } else {
                                    return cellMouse.containsMouse ? "#2f270a" : "#201a05";
                                }
                            }
                            
                            border.color: {
                                if (!modelData || modelData.type !== "day") return "transparent";
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
                                    text: modelData && modelData.type === "day" ? modelData.tithi_num : ""
                                    font.bold: true
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.85
                                    color: modelData && modelData.is_krishna_paksha ? "#9eb1c2" : "#ffe473"
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                Label {
                                    text: modelData && modelData.type === "day" ? `(${parseInt(modelData.date.split('-')[2])})` : ""
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.55
                                    opacity: 0.7
                                    color: modelData && modelData.is_krishna_paksha ? "#9eb1c2" : "#ffe473"
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
                            hoverEnabled: modelData && modelData.type === "day"
                            enabled: modelData && modelData.type === "day"
                            onClicked: {
                                fullRoot.selectedDayData = modelData;
                            }
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
            Layout.minimumWidth: 400
            Layout.preferredWidth: 440
            
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
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.leftMargin: 16
                    anchors.rightMargin: 16
                    spacing: Kirigami.Units.largeSpacing * 1.5



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
                        rowSpacing: Kirigami.Units.smallSpacing * 1.5
                        columnSpacing: Kirigami.Units.largeSpacing * 1.5
                        Layout.fillWidth: true

                        // Row: Masa
                        Label { text: i18n("Masa (Month):"); font.bold: true; opacity: 0.8 }
                        Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.masa : "--"; Layout.fillWidth: true; wrapMode: Text.WordWrap }

                        // Row: Tithi
                        Label { text: i18n("Tithi:"); font.bold: true; opacity: 0.8 }
                        Label {
                            text: {
                                if (!fullRoot.selectedDayData) return "--";
                                var color = fullRoot.selectedDayData.is_krishna_paksha ? "#3daee9" : "#ffb300";
                                return `${fullRoot.selectedDayData.tithi} &nbsp;&nbsp;&nbsp;<font color='${color}'>${fullRoot.selectedDayData.tithi_end}</font>`;
                            }
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        // Row: Nakshatra
                        Label { text: i18n("Nakshatra:"); font.bold: true; opacity: 0.8 }
                        Label {
                            text: {
                                if (!fullRoot.selectedDayData) return "--";
                                var color = fullRoot.selectedDayData.is_krishna_paksha ? "#3daee9" : "#ffb300";
                                return `${fullRoot.selectedDayData.nakshatra} &nbsp;&nbsp;&nbsp;<font color='${color}'>${fullRoot.selectedDayData.nakshatra_end}</font>`;
                            }
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        // Row: Yoga
                        Label { text: i18n("Yoga:"); font.bold: true; opacity: 0.8 }
                        Label {
                            text: {
                                if (!fullRoot.selectedDayData) return "--";
                                var color = fullRoot.selectedDayData.is_krishna_paksha ? "#3daee9" : "#ffb300";
                                return `${fullRoot.selectedDayData.yoga} &nbsp;&nbsp;&nbsp;<font color='${color}'>${fullRoot.selectedDayData.yoga_end}</font>`;
                            }
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        // Row: Karana
                        Label { text: i18n("Karana:"); font.bold: true; opacity: 0.8 }
                        Label {
                            text: {
                                if (!fullRoot.selectedDayData) return "--";
                                var color = fullRoot.selectedDayData.is_krishna_paksha ? "#3daee9" : "#ffb300";
                                return `${fullRoot.selectedDayData.karana} &nbsp;&nbsp;&nbsp;<font color='${color}'>${fullRoot.selectedDayData.karana_end}</font>`;
                            }
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

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
                        spacing: Kirigami.Units.smallSpacing * 1.5

                        Label { text: i18n("Daily Sun & Moon Times:"); font.bold: true }
                        
                        GridLayout {
                            columns: 3
                            rowSpacing: 6
                            columnSpacing: Kirigami.Units.largeSpacing * 1.5
                            Layout.fillWidth: true
                            
                            ColumnLayout {
                                spacing: 4
                                Label { text: `☀️ Rise: ${fullRoot.selectedDayData ? fullRoot.selectedDayData.sunrise : "--"}` }
                                Label { text: `☀️ Set:  ${fullRoot.selectedDayData ? fullRoot.selectedDayData.sunset : "--"}` }
                            }

                            ColumnLayout {
                                spacing: 4
                                Label { text: `🌙 Rise: ${fullRoot.selectedDayData ? fullRoot.selectedDayData.moonrise : "--"}` }
                                Label { text: `🌙 Set:  ${fullRoot.selectedDayData ? fullRoot.selectedDayData.moonset : "--"}` }
                            }

                            ColumnLayout {
                                spacing: 4
                                Label { text: `✨ Brahma:` }
                                Label { text: `${fullRoot.selectedDayData ? fullRoot.selectedDayData.brahma_muhurta : "--"}` }
                            }
                        }
                    }

                    // Auspicious/Inauspicious segments
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing * 1.5

                        Label { text: i18n("Auspicious / Inauspicious Periods:"); font.bold: true }
                        
                        GridLayout {
                            columns: 2
                            rowSpacing: Kirigami.Units.smallSpacing * 1.2
                            columnSpacing: Kirigami.Units.largeSpacing * 1.5

                            Label { text: "Abhijit Muhurta:" }
                            Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.abhijit_muhurta : "--"; font.bold: true; color: "#2ecc71" }

                            Label { text: "Rahu Kala:" }
                            Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.rahu_kala : "--"; font.bold: true; color: "#e74c3c" }

                            Label { text: "Yamaghanta:" }
                            Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.yamaghanta : "--"; font.bold: true; color: "#e74c3c" }

                            Label { text: "Gulika:" }
                            Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.gulika : "--"; font.bold: true; color: "#f1c40f" }
                        }
                    }

                    // Festivals & Observances
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing * 1.5
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

                    // Choghadiya Muhurtas Section
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing * 1.5

                        Label { text: i18n("Choghadiya Muhurtas:"); font.bold: true }

                        TabBar {
                            id: choghadiyaTabBar
                            Layout.fillWidth: true
                            TabButton { text: i18n("Daytime") }
                            TabButton { text: i18n("Nighttime") }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Repeater {
                                model: choghadiyaTabBar.currentIndex === 0 
                                       ? (fullRoot.selectedDayData ? fullRoot.selectedDayData.day_choghadiya : [])
                                       : (fullRoot.selectedDayData ? fullRoot.selectedDayData.night_choghadiya : [])
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: Kirigami.Units.smallSpacing
                                    
                                    Label {
                                        text: {
                                            if (modelData.nature === "Auspicious" || modelData.nature === "शुभ") return "🟢";
                                            if (modelData.nature === "Neutral" || modelData.nature === "सामान्य") return "🟡";
                                            return "🔴";
                                        }
                                    }
                                    
                                    Label {
                                        text: `${modelData.name}`
                                        font.bold: true
                                        Layout.preferredWidth: Kirigami.Units.gridUnit * 5
                                    }
                                    
                                    Label {
                                        text: `${modelData.end}`
                                        opacity: 0.9
                                        color: {
                                            if (modelData.nature === "Auspicious" || modelData.nature === "शुभ") return "#2ecc71";
                                            if (modelData.nature === "Neutral" || modelData.nature === "सामान्य") return "#f1c40f";
                                            return "#e74c3c";
                                        }
                                        font.bold: true
                                        horizontalAlignment: Text.AlignRight
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }
                    }

                    // Live Ghadi-Vipal Display (Only visible for today's selected day)
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.topMargin: Kirigami.Units.largeSpacing
                        visible: fullRoot.selectedDayData && fullRoot.selectedDayData.date === root.getTodayString()
                        
                        Label {
                            text: (plasmoid.configuration.lang === "devanagari") ? "वर्तमान घडी:विपल काल:" : i18n("Current Ghadi:Vipal time:")
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
