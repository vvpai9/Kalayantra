import QtQuick
import org.kde.plasma.configuration

ConfigModel {
    ConfigCategory {
         name: i18n("General Settings")
         icon: "configure"
         source: "configGeneral.qml"
    }
    ConfigCategory {
         name: i18n("Calendar Settings")
         icon: "office-calendar"
         source: "configCalendar.qml"
    }
    ConfigCategory {
         name: i18n("My Tithis")
         icon: "appointment-new"
         source: "configMyTithis.qml"
    }
    ConfigCategory {
         name: i18n("Reminders")
         icon: "notifications"
         source: "configReminders.qml"
    }
}
