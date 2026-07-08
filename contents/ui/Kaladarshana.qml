import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: kaladarshana
    implicitWidth: 1024
    implicitHeight: 640

    Layout.preferredWidth: implicitWidth
    Layout.preferredHeight: implicitHeight
    Layout.minimumWidth: 900
    Layout.minimumHeight: 580
    
    property var selectedDayData: null
    property bool userSelectedDate: false
    property bool editingDate: false
    
    function navigateToDate(y, m, d) {
        var dateStr = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        root.currentYear = y;
        root.currentMonth = m;
        userSelectedDate = true;
        pendingSelectDate = dateStr;
        root.currentlyViewedDateString = dateStr;
        root.fetchThreeMonths(y, m);
    }
    
    // Helper to format astronomical element with active highlights
    function formatAstroElement(el1, el1_end, el2, el2_end, activeIdx, isKrishna, survives, mode) {
        if (!el1) return "--";
        var color = isKrishna ? "#3daee9" : "#ffb300";
        

        
        var part1 = (el1_end && el1_end !== "--") ? `${el1} <font color='${color}'>${el1_end}</font>` : el1;
        var part2 = "";
        if (el2 && el2 !== "--") {
            part2 = (el2_end && el2_end !== "--") ? `${el2} <font color='${color}'>${el2_end}</font>` : el2;
        }
        
        if (activeIdx === 1) {
            return `<b>👉 ${part1}</b>` + (part2 ? ` &nbsp;&nbsp;•&nbsp;&nbsp; <font color='#888888'>${part2}</font>` : "");
        } else if (activeIdx === 2) {
            return `<font color='#888888'>${part1}</font>` + (part2 ? ` &nbsp;&nbsp;•&nbsp;&nbsp; <b>👉 ${part2}</b>` : "");
        } else {
            return part1 + (part2 ? ` &nbsp;&nbsp;•&nbsp;&nbsp; ${part2}` : "");
        }
    }

    function formatGregorianDateStr(dateStr) {
        if (!dateStr) return "";
        var parts = dateStr.split('-');
        if (parts.length < 3) return dateStr;
        var day = parseInt(parts[2]);
        var monthIdx = parseInt(parts[1]);
        var year = parts[0];
        return `${day} ${getGregorianMonthName(monthIdx)} ${year}`;
    }

    function getSortedFestivalDots(festivals) {
        if (!festivals || festivals.length === 0) return [];
        
        var getPriority = function(color) {
            if (color === "#2ecc71") return 1; // Major Festival (Green)
            if (color === "#3daee9") return 2; // Ekadashi (Blue)
            if (color === "#e67e22" || color === "#ff6b00") return 3; // Sankranti (Orange)
            if (color === "#9b59b6") return 4; // Sankashti Chaturthi (Purple)
            if (color === "#e91e63" || color === "#ff4081") return 5; // Custom Observance / My Tithi (Pink)
            return 6; // Other
        };
        
        var list = [];
        for (var i = 0; i < festivals.length; i++) {
            list.push(festivals[i]);
        }
        list.sort(function(a, b) {
            return getPriority(a.color) - getPriority(b.color);
        });
        return list.slice(0, 3);
    }
    property var gridItems: []

    // Hindu month navigation state
    property string selectedMasaName: ""
    property int selectedShakaYear: 0
    property string pendingSelectDate: ""
    property var selectedMonthDays: []

    onSelectedMasaNameChanged: updateGrid()
    onSelectedShakaYearChanged: updateGrid()

    Connections {
        target: root
        function onThreeMonthsDataChanged() {
            updateGrid();
        }
    }

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
                if (!userSelectedDate) {
                    selectedDayData = selectedMonthDays[0];
                }
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
        
        userSelectedDate = false;
        pendingSelectDate = `${targetY}-${String(targetM).padStart(2, '0')}-${String(targetD).padStart(2, '0')}`;
        root.currentlyViewedDateString = pendingSelectDate;
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
        
        userSelectedDate = false;
        pendingSelectDate = `${targetY}-${String(targetM).padStart(2, '0')}-${String(targetD).padStart(2, '0')}`;
        root.currentlyViewedDateString = pendingSelectDate;
        root.fetchThreeMonths(targetY, targetM);
    }

    function initializeData() {
        if (root.threeMonthsData && root.threeMonthsData.length > 0) {
            var targetDate = pendingSelectDate;
            if (!targetDate) {
                if (userSelectedDate && selectedDayData) {
                    targetDate = selectedDayData.date;
                } else {
                    targetDate = root.currentlyViewedDateString || root.todayDateString;
                }
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

        function onExpandedChanged() {
            if (root.expanded) {
                userSelectedDate = false;
                selectedDayData = null;
                root.currentlyViewedDateString = root.todayDateString;
                pendingSelectDate = root.todayDateString;
                root.currentYear = new Date().getFullYear();
                root.currentMonth = new Date().getMonth() + 1;
                root.fetchThreeMonths(root.currentYear, root.currentMonth);
                initializeData();
            } else {
                userSelectedDate = false;
                selectedDayData = null;
                pendingSelectDate = "";
                root.currentlyViewedDateString = "";
                initializeData();
            }
        }
    }

    GridLayout {
        id: mainGridLayout
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
                        text: selectedDayData ? `${selectedMasaName} ${selectedDayData.paksha} Paksha` : selectedMasaName
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
                    icon.name: "go-jump-today"
                    flat: true
                    display: AbstractButton.IconOnly
                    ToolTip.text: i18n("Go to Today")
                    ToolTip.visible: hovered
                    onClicked: {
                        var today = new Date();
                        kaladarshana.navigateToDate(today.getFullYear(), today.getMonth() + 1, today.getDate());
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
                    model: kaladarshana.gridItems

                    Item {
                        id: cell
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.preferredWidth: 0

                        Rectangle {
                            anchors.fill: parent
                            radius: 4
                            visible: modelData && modelData.type === "day"
                            
                            // Visual theme logic based on Shukla/Krishna Pakshas and Today's highlight
                            color: {
                                if (!modelData || modelData.type !== "day") return "transparent";
                                var isToday = (modelData.date === root.getTodayString());
                                if (modelData.is_krishna_paksha) {
                                    if (cellMouse.containsMouse) return "#1c252c";
                                    return isToday ? "#162836" : "#121b22";
                                } else {
                                    if (cellMouse.containsMouse) return "#2f270a";
                                    return isToday ? "#332c11" : "#201a05";
                                }
                            }

                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                            
                            border.width: {
                                if (!modelData || modelData.type !== "day") return 0;
                                if (kaladarshana.selectedDayData && kaladarshana.selectedDayData.date === modelData.date) {
                                    return 2.5;
                                }
                                if (modelData.date === root.getTodayString()) {
                                    return 2.5;
                                }
                                return 1;
                            }

                            border.color: {
                                if (!modelData || modelData.type !== "day") return "transparent";
                                if (kaladarshana.selectedDayData && kaladarshana.selectedDayData.date === modelData.date) {
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
                                spacing: 2
                                
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

                            // Horizontal row of up to 3 priority-sorted indicators at top right
                            RowLayout {
                                id: indicatorDots
                                anchors.top: parent.top
                                anchors.right: parent.right
                                anchors.topMargin: 4
                                anchors.rightMargin: 4
                                spacing: 2
                                visible: !!(modelData && modelData.festivals && modelData.festivals.length > 0)
                                
                                Repeater {
                                    model: kaladarshana.getSortedFestivalDots(modelData ? modelData.festivals : [])
                                    Rectangle {
                                        width: 7
                                        height: 7
                                        radius: 3.5
                                        color: modelData.color || "#2ecc71"
                                    }
                                }
                            }
                        }

                        MouseArea {
                            id: cellMouse
                            anchors.fill: parent
                            hoverEnabled: modelData ? modelData.type === "day" : false
                            enabled: modelData ? modelData.type === "day" : false
                            onClicked: {
                                kaladarshana.selectedDayData = modelData;
                                kaladarshana.userSelectedDate = true;
                                root.currentlyViewedDateString = modelData.date;
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
            Layout.fillWidth: mainGridLayout.columns === 1
            Layout.fillHeight: true
            Layout.minimumWidth: mainGridLayout.columns === 1 ? 250 : 400
            Layout.preferredWidth: mainGridLayout.columns === 1 ? -1 : 440
            
            // Slate/Warm tinted card background depending on Paksha
            background: Rectangle {
                radius: 8
                color: {
                    if (!kaladarshana.selectedDayData) return Kirigami.Theme.backgroundColor;
                    return kaladarshana.selectedDayData.is_krishna_paksha ? "#141c22" : "#1a1608";
                }
                border.color: kaladarshana.selectedDayData && kaladarshana.selectedDayData.is_krishna_paksha ? "#2e3b46" : "#d4af37"
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
                        // Editable Gregorian Date Row
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            
                            // Normal state: clickable label
                            MouseArea {
                                id: gregDateClickArea
                                Layout.fillWidth: true
                                implicitHeight: labelGregDate.implicitHeight
                                cursorShape: Qt.PointingHandCursor
                                visible: !kaladarshana.editingDate
                                hoverEnabled: true
                                
                                Label {
                                    id: labelGregDate
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    text: kaladarshana.selectedDayData ? kaladarshana.formatGregorianDateStr(kaladarshana.selectedDayData.date) : ""
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.75
                                    opacity: 0.8
                                    font.underline: gregDateClickArea.containsMouse
                                }
                                
                                onClicked: {
                                    if (kaladarshana.selectedDayData) {
                                        var parts = kaladarshana.selectedDayData.date.split('-');
                                        editDateInput.text = `${parts[2]}-${parts[1]}-${parts[0]}`;
                                        kaladarshana.editingDate = true;
                                        editDateInput.forceActiveFocus();
                                    }
                                }
                            }

                            // Editing state: editable text input
                            TextField {
                                id: editDateInput
                                Layout.fillWidth: true
                                placeholderText: "DD-MM-YYYY"
                                visible: kaladarshana.editingDate
                                
                                function commitEdit() {
                                    var txt = text.trim();
                                    var regex = /^(\d{2})-(\d{2})-(\d{4})$/;
                                    var match = txt.match(regex);
                                    if (!match) {
                                        showError("Invalid format. Use DD-MM-YYYY.");
                                        return;
                                    }
                                    var d = parseInt(match[1]);
                                    var m = parseInt(match[2]);
                                    var y = parseInt(match[3]);
                                    
                                    if (m < 1 || m > 12) {
                                        showError("Invalid month (1-12).");
                                        return;
                                    }
                                    if (d < 1 || d > 31) {
                                        showError("Invalid day (1-31).");
                                        return;
                                    }
                                    
                                    var parsedDate = new Date(y, m - 1, d);
                                    if (parsedDate.getFullYear() !== y || parsedDate.getMonth() !== (m - 1) || parsedDate.getDate() !== d) {
                                        showError("Invalid calendar date.");
                                        return;
                                    }
                                    
                                    inlineErrorMsg.visible = false;
                                    kaladarshana.navigateToDate(y, m, d);
                                    kaladarshana.editingDate = false;
                                }
                                
                                function cancelEdit() {
                                    inlineErrorMsg.visible = false;
                                    kaladarshana.editingDate = false;
                                }
                                
                                function showError(msg) {
                                    inlineErrorMsg.text = msg;
                                    inlineErrorMsg.visible = true;
                                }

                                Keys.onReturnPressed: commitEdit()
                                Keys.onEnterPressed: commitEdit()
                                Keys.onEscapePressed: cancelEdit()
                                
                                onActiveFocusChanged: {
                                    if (!activeFocus && kaladarshana.editingDate) {
                                        var txt = text.trim();
                                        var regex = /^(\d{2})-(\d{2})-(\d{4})$/;
                                        var match = txt.match(regex);
                                        if (match) {
                                            var d = parseInt(match[1]);
                                            var m = parseInt(match[2]);
                                            var y = parseInt(match[3]);
                                            var parsedDate = new Date(y, m - 1, d);
                                            if (m >= 1 && m <= 12 && d >= 1 && d <= 31 && parsedDate.getFullYear() === y && parsedDate.getMonth() === (m - 1) && parsedDate.getDate() === d) {
                                                commitEdit();
                                                return;
                                            }
                                        }
                                        cancelEdit();
                                    }
                                }
                            }

                            Kirigami.InlineMessage {
                                id: inlineErrorMsg
                                Layout.fillWidth: true
                                type: Kirigami.MessageType.Error
                                showCloseButton: true
                                visible: false
                            }
                        }


                         Kirigami.Heading {
                             level: 2
                             text: kaladarshana.selectedDayData ? (root.configTithiMode === "astronomical" ? kaladarshana.selectedDayData.tithi : kaladarshana.selectedDayData.tithi_1) : i18n("Select a day")
                             color: kaladarshana.selectedDayData && kaladarshana.selectedDayData.is_krishna_paksha ? "#7094b3" : "#ffcc00"
                             font.bold: true
                         }

                        Label {
                            text: kaladarshana.selectedDayData ? `${kaladarshana.selectedDayData.paksha} Paksha • ${kaladarshana.selectedDayData.vaara}` : ""
                            font.bold: true
                            font.pixelSize: Kirigami.Units.gridUnit * 0.85
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4
                            visible: kaladarshana.selectedDayData && kaladarshana.selectedDayData.festivals && kaladarshana.selectedDayData.festivals.length > 0
                            Layout.topMargin: 4
                            Layout.bottomMargin: 4

                            Repeater {
                                model: kaladarshana.selectedDayData ? kaladarshana.selectedDayData.festivals : []
                                Label {
                                    text: modelData.anniversary_display ? `${modelData.name}<br/><font size="-1" color="#888888">${modelData.anniversary_display}</font>` : modelData.name
                                    textFormat: Text.RichText
                                    font.bold: true
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.95
                                    color: modelData.color || "#2ecc71"
                                    Layout.fillWidth: true
                                    wrapMode: Text.WordWrap

                                    ToolTip.visible: festivalMouse.containsMouse
                                    ToolTip.text: (modelData.description ? modelData.description + "\n" : "") + (modelData.rule ? `Rule: ${modelData.rule}` : "")

                                    MouseArea {
                                        id: festivalMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                    }
                                }
                            }
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
                        Label { text: kaladarshana.selectedDayData ? kaladarshana.selectedDayData.masa : "--"; Layout.fillWidth: true; wrapMode: Text.WordWrap }

                        // Row: Tithi
                        Label { text: i18n("Tithi:"); font.bold: true; opacity: 0.8 }
                        Label {
                            text: {
                                if (!kaladarshana.selectedDayData) return "--";
                                return kaladarshana.formatAstroElement(
                                    kaladarshana.selectedDayData.tithi_1,
                                    kaladarshana.selectedDayData.tithi_1_end,
                                    kaladarshana.selectedDayData.tithi_2,
                                    kaladarshana.selectedDayData.tithi_2_end,
                                    kaladarshana.selectedDayData.tithi_active_idx,
                                    kaladarshana.selectedDayData.is_krishna_paksha,
                                    kaladarshana.selectedDayData.tithi_survives,
                                    root.configTithiMode
                                );
                            }
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        // Row: Nakshatra
                        Label { text: i18n("Chandra Nakshatra:"); font.bold: true; opacity: 0.8 }
                        Label {
                            text: {
                                if (!kaladarshana.selectedDayData) return "--";
                                return kaladarshana.formatAstroElement(
                                    kaladarshana.selectedDayData.nakshatra_1,
                                    kaladarshana.selectedDayData.nakshatra_1_end,
                                    kaladarshana.selectedDayData.nakshatra_2,
                                    kaladarshana.selectedDayData.nakshatra_2_end,
                                    kaladarshana.selectedDayData.nakshatra_active_idx,
                                    kaladarshana.selectedDayData.is_krishna_paksha,
                                    kaladarshana.selectedDayData.nakshatra_survives,
                                    root.configTithiMode
                                );
                            }
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        // Row: Sūrya Nakṣatra
                        Label {
                            text: {
                                if (root.configLang === "devanagari") return "सूर्य नक्षत्र:";
                                if (root.configLang === "iast") return "Sūrya Nakṣatra:";
                                return "Surya Nakshatra:";
                            }
                            font.bold: true
                            opacity: 0.8
                        }
                        Label {
                            text: {
                                if (!kaladarshana.selectedDayData) return "--";
                                if (kaladarshana.selectedDayData.surya_nakshatra_survives) {
                                    return kaladarshana.selectedDayData.surya_nakshatra_1;
                                }
                                return kaladarshana.formatAstroElement(
                                    kaladarshana.selectedDayData.surya_nakshatra_1,
                                    kaladarshana.selectedDayData.surya_nakshatra_1_end,
                                    kaladarshana.selectedDayData.surya_nakshatra_2,
                                    kaladarshana.selectedDayData.surya_nakshatra_2_end,
                                    kaladarshana.selectedDayData.surya_nakshatra_active_idx,
                                    false,
                                    false,
                                    root.configTithiMode
                                );
                            }
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        // Row: Yoga
                        Label { text: i18n("Yoga:"); font.bold: true; opacity: 0.8 }
                        Label {
                            text: {
                                if (!kaladarshana.selectedDayData) return "--";
                                return kaladarshana.formatAstroElement(
                                    kaladarshana.selectedDayData.yoga_1,
                                    kaladarshana.selectedDayData.yoga_1_end,
                                    kaladarshana.selectedDayData.yoga_2,
                                    kaladarshana.selectedDayData.yoga_2_end,
                                    kaladarshana.selectedDayData.yoga_active_idx,
                                    kaladarshana.selectedDayData.is_krishna_paksha,
                                    kaladarshana.selectedDayData.yoga_survives,
                                    root.configTithiMode
                                );
                            }
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        // Row: Karana
                        Label { text: i18n("Karana:"); font.bold: true; opacity: 0.8 }
                        Label {
                            text: {
                                if (!kaladarshana.selectedDayData) return "--";
                                return kaladarshana.formatAstroElement(
                                    kaladarshana.selectedDayData.karana_1,
                                    kaladarshana.selectedDayData.karana_1_end,
                                    kaladarshana.selectedDayData.karana_2,
                                    kaladarshana.selectedDayData.karana_2_end,
                                    kaladarshana.selectedDayData.karana_active_idx,
                                    kaladarshana.selectedDayData.is_krishna_paksha,
                                    kaladarshana.selectedDayData.karana_survives,
                                    root.configTithiMode
                                );
                            }
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        // Row: Ritu & Ayana
                        Label { text: i18n("Ritu & Ayana:"); font.bold: true; opacity: 0.8 }
                        Label { text: kaladarshana.selectedDayData ? `${kaladarshana.selectedDayData.ritu} • ${kaladarshana.selectedDayData.ayana}` : "--"; Layout.fillWidth: true; wrapMode: Text.WordWrap }

                        // Row: Jovian Samvatsara & Years
                        Label { text: i18n("Samvatsara:"); font.bold: true; opacity: 0.8 }
                        Label { 
                            text: kaladarshana.selectedDayData ? `${kaladarshana.selectedDayData.samvatsara}` : "--"
                            font.bold: true
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }

                        Label { text: i18n("Era Years:"); font.bold: true; opacity: 0.8 }
                        Label { 
                            text: kaladarshana.selectedDayData ? `Shaka ${kaladarshana.selectedDayData.shaka_year} • Vikram ${kaladarshana.selectedDayData.vikram_year} • Kali ${kaladarshana.selectedDayData.kali_year}` : "--"
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
                                Label { text: `☀️ Rise: ${kaladarshana.selectedDayData ? kaladarshana.selectedDayData.sunrise : "--"}` }
                                Label { text: `☀️ Set:  ${kaladarshana.selectedDayData ? kaladarshana.selectedDayData.sunset : "--"}` }
                            }

                            ColumnLayout {
                                spacing: 4
                                Label { text: `🌙 Rise: ${kaladarshana.selectedDayData ? kaladarshana.selectedDayData.moonrise : "--"}` }
                                Label { text: `🌙 Set:  ${kaladarshana.selectedDayData ? kaladarshana.selectedDayData.moonset : "--"}` }
                            }

                            ColumnLayout {
                                spacing: 4
                                Label { text: `✨ Brahma:` }
                                Label { text: `${kaladarshana.selectedDayData ? kaladarshana.selectedDayData.brahma_muhurta : "--"}` }
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
                            Label { text: kaladarshana.selectedDayData ? kaladarshana.selectedDayData.abhijit_muhurta : "--"; font.bold: true; color: "#2ecc71" }

                            Label { text: "Rahu Kala:" }
                            Label { text: kaladarshana.selectedDayData ? kaladarshana.selectedDayData.rahu_kala : "--"; font.bold: true; color: "#e74c3c" }

                            Label { text: "Yamaghanta:" }
                            Label { text: kaladarshana.selectedDayData ? kaladarshana.selectedDayData.yamaghanta : "--"; font.bold: true; color: "#e74c3c" }

                            Label { text: "Gulika:" }
                            Label { text: kaladarshana.selectedDayData ? kaladarshana.selectedDayData.gulika : "--"; font.bold: true; color: "#f1c40f" }
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
                                       ? (kaladarshana.selectedDayData ? kaladarshana.selectedDayData.day_choghadiya : [])
                                       : (kaladarshana.selectedDayData ? kaladarshana.selectedDayData.night_choghadiya : [])
                                
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
                        visible: kaladarshana.selectedDayData && kaladarshana.selectedDayData.date === root.getTodayString()
                        
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
