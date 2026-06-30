import QtQuick
import org.kde.plasma.configuration

ConfigModel {
    ConfigCategory {
         name: i18n("General Settings")
         icon: "configure"
         source: "configGeneral.qml"
    }
    ConfigCategory {
         name: i18n("Custom Observances")
         icon: "appointment-new"
         source: "configObservances.qml"
    }
}
