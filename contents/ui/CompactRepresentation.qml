import QtQuick
import QtQuick.Layouts as Layouts
import org.kde.kirigami as Kirigami

Item {
    id: compactRoot
    implicitWidth: layout.implicitWidth
    implicitHeight: layout.implicitHeight

    Layouts.RowLayout {
        id: layout
        anchors.fill: parent
        spacing: Kirigami.Units.smallSpacing

        // Moon phase indicator
        Rectangle {
            id: moonIndicator
            width: Kirigami.Units.iconSizes.small
            height: width
            radius: width / 2
            
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

        // Tithi and Masa text
        Layouts.ColumnLayout {
            spacing: 0
            
            Kirigami.Heading {
                level: 5
                text: root.currentPanchanga ? root.currentPanchanga.tithi : i18n("Loading...")
                font.bold: true
                Layouts.fillWidth: true
                elide: Text.ElideRight
            }

            Kirigami.Heading {
                level: 6
                text: root.currentPanchanga ? `${root.currentPanchanga.paksha} • ${root.currentPanchanga.masa}` : ""
                font.pixelSize: Kirigami.Units.gridUnit * 0.6
                opacity: 0.7
                Layouts.fillWidth: true
                elide: Text.ElideRight
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            plasmoid.expanded = !plasmoid.expanded;
        }
    }
}
