import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts as Layouts
import org.kde.kirigami as Kirigami

Item {
    id: fullRoot
    implicitWidth: Kirigami.Units.gridUnit * 35
    implicitHeight: Kirigami.Units.gridUnit * 25

    property var selectedDayData: null
    property var gridItems: []

    // Helper to format Gregorian Month name
    function getGregorianMonthName(m) {
        var names = [
            i18n("January"), i18n("February"), i18n("March"), i18n("April"), 
            i18n("May"), i18n("June"), i18n("July"), i18n("August"), 
            i18n("September"), i18n("October"), i18n("November"), i18n("December")
        ];
        return names[m - 1];
    }

    // Refresh grid items when month data changes
    onMonthDataChanged: {
        gridItems = root.generateGridItems(root.currentYear, root.currentMonth, root.monthData);
        // Default select current day or day 1
        if (root.monthData && root.monthData.length > 0) {
            var todayStr = root.getTodayString();
            var foundToday = false;
            for (var i = 0; i < root.monthData.length; i++) {
                if (root.monthData[i].date === todayStr) {
                    selectedDayData = root.monthData[i];
                    foundToday = true;
                    break;
                }
            }
            if (!foundToday) {
                selectedDayData = root.monthData[0];
            }
        }
    }

    Layouts.GridLayout {
        anchors.fill: parent
        anchors.margin: Kirigami.Units.largeSpacing
        columns: width > Kirigami.Units.gridUnit * 28 ? 2 : 1
        rows: width > Kirigami.Units.gridUnit * 28 ? 1 : 2
        columnSpacing: Kirigami.Units.largeSpacing
        rowSpacing: Kirigami.Units.largeSpacing

        // Left/Top Panel: Calendar Control & Grid
        Layouts.ColumnLayout {
            Layouts.fillWidth: true
            Layouts.fillHeight: true
            spacing: Kirigami.Units.largeSpacing

            // Month Navigation Header
            Layouts.RowLayout {
                Layouts.fillWidth: true
                
                Controls.Button {
                    icon.name: "go-previous"
                    flat: true
                    onClicked: root.prevMonth()
                }

                Kirigami.Heading {
                    level: 2
                    text: `${getGregorianMonthName(root.currentMonth)} ${root.currentYear}`
                    font.bold: true
                    Layouts.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                }

                Controls.Button {
                    icon.name: "go-next"
                    flat: true
                    onClicked: root.nextMonth()
                }
            }

            // Days of the week header
            Layouts.GridLayout {
                columns: 7
                Layouts.fillWidth: true
                columnSpacing: Kirigami.Units.smallSpacing
                rowSpacing: 0
                
                Repeater {
                    model: [
                        i18n("Sun"), i18n("Mon"), i18n("Tue"), i18n("Wed"), 
                        i18n("Thu"), i18n("Fri"), i18n("Sat")
                    ]
                    
                    Controls.Label {
                        text: modelData
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        font.pixelSize: Kirigami.Units.gridUnit * 0.75
                        opacity: 0.8
                        Layouts.fillWidth: true
                    }
                }
            }

            // 6x7 Calendar Grid
            Layouts.GridLayout {
                id: calendarGrid
                columns: 7
                rows: 6
                Layouts.fillWidth: true
                Layouts.fillHeight: true
                columnSpacing: Kirigami.Units.smallSpacing
                rowSpacing: Kirigami.Units.smallSpacing

                Repeater {
                    model: fullRoot.gridItems

                    Item {
                        id: cell
                        Layouts.fillWidth: true
                        Layouts.fillHeight: true
                        visible: modelData.type !== "empty"

                        Rectangle {
                            anchors.fill: parent
                            radius: 6
                            border.width: 1.5
                            
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
                            Layouts.ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 1
                                
                                Controls.Label {
                                    text: modelData.dayNumber || ""
                                    font.bold: true
                                    font.pixelSize: Kirigami.Units.gridUnit * 1.0
                                    color: modelData.is_krishna_paksha ? "#9eb1c2" : "#ffe473"
                                    Layouts.alignment: Qt.AlignHCenter
                                }

                                Controls.Label {
                                    text: modelData.type === "day" ? `${modelData.is_krishna_paksha ? "K" : "S"} ${modelData.tithi_num}` : ""
                                    font.pixelSize: Kirigami.Units.gridUnit * 0.55
                                    opacity: 0.7
                                    Layouts.alignment: Qt.AlignHCenter
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
                                visible: modelData.festivals && modelData.festivals.length > 0
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
            Layouts.fillWidth: true
            Layouts.fillHeight: true
            
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
                
                Layouts.ColumnLayout {
                    id: detailsLayout
                    anchors.fill: parent
                    spacing: Kirigami.Units.largeSpacing

                    // Detail Card Header
                    Layouts.ColumnLayout {
                        Layouts.fillWidth: true
                        spacing: 2

                        Controls.Label {
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

                        Controls.Label {
                            text: fullRoot.selectedDayData ? `${fullRoot.selectedDayData.paksha} Paksha • ${fullRoot.selectedDayData.vaara}` : ""
                            font.bold: true
                            font.pixelSize: Kirigami.Units.gridUnit * 0.85
                        }
                    }

                    Kirigami.Separator { Layouts.fillWidth: true }

                    // Detailed Astronomical Grid
                    Layouts.GridLayout {
                        columns: 2
                        rowSpacing: Kirigami.Units.smallSpacing
                        columnSpacing: Kirigami.Units.largeSpacing
                        Layouts.fillWidth: true

                        // Row: Masa
                        Controls.Label { text: i18n("Masa (Month):"); font.bold: true; opacity: 0.8 }
                        Controls.Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.masa : "--" }

                        // Row: Nakshatra
                        Controls.Label { text: i18n("Nakshatra:"); font.bold: true; opacity: 0.8 }
                        Controls.Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.nakshatra : "--" }

                        // Row: Yoga
                        Controls.Label { text: i18n("Yoga:"); font.bold: true; opacity: 0.8 }
                        Controls.Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.yoga : "--" }

                        // Row: Karana
                        Controls.Label { text: i18n("Karana:"); font.bold: true; opacity: 0.8 }
                        Controls.Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.karana : "--" }

                        // Row: Ritu & Ayana
                        Controls.Label { text: i18n("Ritu & Ayana:"); font.bold: true; opacity: 0.8 }
                        Controls.Label { text: fullRoot.selectedDayData ? `${fullRoot.selectedDayData.ritu} • ${fullRoot.selectedDayData.ayana}` : "--" }

                        // Row: Jovian Samvatsara & Years
                        Controls.Label { text: i18n("Samvatsara:"); font.bold: true; opacity: 0.8 }
                        Controls.Label { 
                            text: fullRoot.selectedDayData ? `${fullRoot.selectedDayData.samvatsara}` : "--"
                            font.bold: true
                        }

                        Controls.Label { text: i18n("Era Years:"); font.bold: true; opacity: 0.8 }
                        Controls.Label { 
                            text: fullRoot.selectedDayData ? `Shaka ${fullRoot.selectedDayData.shaka_year} • Vikram ${fullRoot.selectedDayData.vikram_year} • Kali ${fullRoot.selectedDayData.kali_year}` : "--"
                            font.pixelSize: Kirigami.Units.gridUnit * 0.7
                        }
                    }

                    Kirigami.Separator { Layouts.fillWidth: true }

                    // Sunrise, Sunset, Moonrise, Moonset Timings
                    Layouts.ColumnLayout {
                        Layouts.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing

                        Controls.Label { text: i18n("Daily Sun & Moon Times:"); font.bold: true }
                        
                        Layouts.RowLayout {
                            spacing: Kirigami.Units.largeSpacing
                            
                            Layouts.ColumnLayout {
                                spacing: 2
                                Controls.Label { text: `☀️ Rise: ${fullRoot.selectedDayData ? fullRoot.selectedDayData.sunrise : "--"}` }
                                Controls.Label { text: `☀️ Set:  ${fullRoot.selectedDayData ? fullRoot.selectedDayData.sunset : "--"}` }
                            }

                            Layouts.ColumnLayout {
                                spacing: 2
                                Controls.Label { text: `🌙 Rise: ${fullRoot.selectedDayData ? fullRoot.selectedDayData.moonrise : "--"}` }
                                Controls.Label { text: `🌙 Set:  ${fullRoot.selectedDayData ? fullRoot.selectedDayData.moonset : "--"}` }
                            }
                        }
                    }

                    // Auspicious/Inauspicious segments
                    Layouts.ColumnLayout {
                        Layouts.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing

                        Controls.Label { text: i18n("Auspicious / Inauspicious Periods:"); font.bold: true }
                        
                        Layouts.GridLayout {
                            columns: 2
                            rowSpacing: 2
                            columnSpacing: Kirigami.Units.largeSpacing

                            Controls.Label { text: "Abhijit Muhurta:" }
                            Controls.Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.abhijit_muhurta : "--"; font.bold: true; color: "#2ecc71" }

                            Controls.Label { text: "Rahu Kala:" }
                            Controls.Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.rahu_kala : "--"; font.bold: true; color: "#e74c3c" }

                            Controls.Label { text: "Yamaganda:" }
                            Controls.Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.yamaganda : "--" }

                            Controls.Label { text: "Gulika:" }
                            Controls.Label { text: fullRoot.selectedDayData ? fullRoot.selectedDayData.gulika : "--" }
                        }
                    }

                    // Festivals & Observances
                    Layouts.ColumnLayout {
                        Layouts.fillWidth: true
                        spacing: Kirigami.Units.smallSpacing
                        visible: fullRoot.selectedDayData && fullRoot.selectedDayData.festivals && fullRoot.selectedDayData.festivals.length > 0

                        Controls.Label { text: i18n("Festivals & Observances:"); font.bold: true; color: "#ff4d4d" }
                        
                        Repeater {
                            model: fullRoot.selectedDayData ? fullRoot.selectedDayData.festivals : []
                            Controls.Label {
                                text: `• ${modelData}`
                                font.bold: true
                                font.pixelSize: Kirigami.Units.gridUnit * 0.8
                            }
                        }
                    }

                    // Live Ghadi-Vipal Display (Only visible for today's selected day)
                    Layouts.RowLayout {
                        Layouts.fillWidth: true
                        visible: fullRoot.selectedDayData && fullRoot.selectedDayData.date === root.getTodayString()
                        
                        Controls.Label {
                            text: i18n("Current Ghadi:Vipal time:")
                            font.bold: true
                        }
                        
                        Controls.Label {
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
