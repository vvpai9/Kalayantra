import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: compactRoot
    implicitWidth: layout.implicitWidth
    implicitHeight: Kirigami.Units.gridUnit * 2

    Layout.minimumWidth: Kirigami.Units.gridUnit * 6
    Layout.minimumHeight: Kirigami.Units.gridUnit * 1.5
    Layout.preferredWidth: implicitWidth
    Layout.preferredHeight: implicitHeight

    RowLayout {
        id: layout
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        spacing: Kirigami.Units.smallSpacing

        // Moon phase indicator
        Rectangle {
            id: moonIndicator
            implicitWidth: Kirigami.Units.iconSizes.small
            implicitHeight: implicitWidth
            width: implicitWidth
            height: implicitHeight
            radius: width / 2
            Layout.alignment: Qt.AlignVCenter
            Layout.preferredWidth: implicitWidth
            Layout.preferredHeight: implicitHeight
            
            // Gold for Shukla (waxing), Slate-blue for Krishna (waning)
            color: {
                if (!root.currentPanchanga) return "grey";
                return root.currentPanchanga.is_krishna_paksha ? "#4f5b66" : "#ffd700";
            }
            
            // Border to make it pop
            border.color: Kirigami.Theme.textColor
            border.width: 1

            // Simple inner crescent effect for Krishna Paksha
            Rectangle {
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: parent.width / 2
                radius: parent.radius
                color: root.currentPanchanga && root.currentPanchanga.is_krishna_paksha ? Kirigami.Theme.backgroundColor : "transparent"
                visible: root.currentPanchanga ? root.currentPanchanga.is_krishna_paksha : false
            }
        }

        ColumnLayout {
            spacing: 0
            Layout.alignment: Qt.AlignVCenter
            
            Kirigami.Heading {
                id: firstLine
                level: 5
                text: root.currentPanchanga ? `${root.currentPanchanga.tithi} • ${root.currentPanchanga.vaara} • ${(plasmoid.configuration.lang === "devanagari") ? "घ" : "Gh"}: ${root.liveGhadiTime}` : "Loading..."
                font.bold: true
                elide: Text.ElideRight
            }

            Kirigami.Heading {
                id: secondLine
                level: 6
                text: root.currentPanchanga ? `${root.currentPanchanga.masa} ${root.currentPanchanga.paksha} • ${root.currentPanchanga.samvatsara} ${root.currentPanchanga.era_year}` : ""
                font.pixelSize: Kirigami.Units.gridUnit * 0.6
                opacity: 0.7
                elide: Text.ElideRight
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            root.expanded = !root.expanded;
        }
    }
}
