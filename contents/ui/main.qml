import QtQuick
import org.kde.plasma.plasmoid
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    // Calendar state properties
    property int currentYear: new Date().getFullYear()
    property int currentMonth: new Date().getMonth() + 1 // 1-indexed

    property var monthData: []
    property var currentPanchanga: null
    property string liveGhadiTime: "00:00"

    // Component configurations
    compactRepresentation: CompactRepresentation {}
    fullRepresentation: FullRepresentation {}

    // Format helper to get YYYY-MM-DD
    function getTodayString() {
        var d = new Date();
        var y = d.getFullYear();
        var m = String(d.getMonth() + 1).padStart(2, '0');
        var day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
    }

    // Build query parameters string from plasmoid settings
    function buildQueryString(extraParams) {
        var params = [
            `lat=${plasmoid.configuration.latitude}`,
            `lon=${plasmoid.configuration.longitude}`,
            `alt=${plasmoid.configuration.altitude}`,
            `tz=${plasmoid.configuration.timezone}`,
            `lang=${plasmoid.configuration.lang}`,
            `calendar_system=${plasmoid.configuration.calendarSystem}`,
            `month_system=${plasmoid.configuration.monthSystem}`,
            `festival_rule=${plasmoid.configuration.festivalRule}`,
            `tithi_mode=${plasmoid.configuration.tithiMode}`
        ];
        if (extraParams) {
            params.push(extraParams);
        }
        return params.join('&');
    }

    // Asynchronous network fetch for a single day
    function fetchDay(dateStr) {
        var xhr = new XMLHttpRequest();
        var query = buildQueryString(`date=${dateStr}`);
        xhr.open("GET", `http://127.0.0.1:8642/day?${query}`, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    if (dateStr === getTodayString()) {
                        currentPanchanga = data;
                        liveGhadiTime = data.ghadi;
                    }
                } catch(e) {
                    console.error("Failed to parse day response: ", e);
                }
            }
        };
        xhr.send();
    }

    // Asynchronous network fetch for the calendar month grid
    function fetchMonth(year, month) {
        var xhr = new XMLHttpRequest();
        var query = buildQueryString(`year=${year}&month=${month}`);
        xhr.open("GET", `http://127.0.0.1:8642/month?${query}`, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                try {
                    monthData = JSON.parse(xhr.responseText);
                } catch(e) {
                    console.error("Failed to parse month response: ", e);
                }
            }
        };
        xhr.send();
    }

    // Grid construction helper for FullRepresentation
    function generateGridItems(year, month, data) {
        if (!data || data.length === 0) return [];
        
        var firstDay = new Date(year, month - 1, 1).getDay(); // Sunday = 0
        var items = [];
        
        // Front padding
        for (var i = 0; i < firstDay; i++) {
            items.push({"type": "empty"});
        }
        
        // Days
        for (var d = 0; d < data.length; d++) {
            var dayData = data[d];
            dayData.type = "day";
            dayData.dayNumber = d + 1;
            items.push(dayData);
        }
        
        // End padding
        while (items.length < 42) {
            items.push({"type": "empty"});
        }
        
        return items;
    }

    // Month Navigation Functions
    function nextMonth() {
        if (currentMonth === 12) {
            currentMonth = 1;
            currentYear += 1;
        } else {
            currentMonth += 1;
        }
        fetchMonth(currentYear, currentMonth);
    }

    function prevMonth() {
        if (currentMonth === 1) {
            currentMonth = 12;
            currentYear -= 1;
        } else {
            currentMonth -= 1;
        }
        fetchMonth(currentYear, currentMonth);
    }

    // Reload all data on configuration changes
    function reloadAll() {
        fetchDay(getTodayString());
        fetchMonth(currentYear, currentMonth);
    }

    // Configuration change connections
    Connections {
        target: plasmoid.configuration
        function onLatitudeChanged() { reloadAll() }
        function onLongitudeChanged() { reloadAll() }
        function onAltitudeChanged() { reloadAll() }
        function onTimezoneChanged() { reloadAll() }
        function onLangChanged() { reloadAll() }
        function onCalendarSystemChanged() { reloadAll() }
        function onMonthSystemChanged() { reloadAll() }
        function onFestivalRuleChanged() { reloadAll() }
        function onTithiModeChanged() { reloadAll() }
    }

    // Periodic timer to sync current day data and update Ghadi-Vipal time
    Timer {
        interval: 5000
        running: true
        repeat: true
        onTriggered: {
            fetchDay(getTodayString());
        }
    }

    // Initial load
    Component.onCompleted: {
        reloadAll();
    }
}
