import QtQuick
import org.kde.plasma.plasmoid
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    width: Kirigami.Units.gridUnit * 35
    height: Kirigami.Units.gridUnit * 25

    // Bind to configuration to ensure reactivity
    readonly property string configLang: plasmoid.configuration.lang
    readonly property double configLatitude: plasmoid.configuration.latitude
    readonly property double configLongitude: plasmoid.configuration.longitude
    readonly property double configAltitude: plasmoid.configuration.altitude
    readonly property double configTimezone: plasmoid.configuration.timezone
    readonly property string configCalendarSystem: plasmoid.configuration.calendarSystem
    readonly property string configMonthSystem: plasmoid.configuration.monthSystem
    readonly property string configFestivalRule: plasmoid.configuration.festivalRule
    readonly property string configTithiMode: plasmoid.configuration.tithiMode

    onConfigLangChanged: reloadAll()
    onConfigLatitudeChanged: reloadAll()
    onConfigLongitudeChanged: reloadAll()
    onConfigAltitudeChanged: reloadAll()
    onConfigTimezoneChanged: reloadAll()
    onConfigCalendarSystemChanged: reloadAll()
    onConfigMonthSystemChanged: reloadAll()
    onConfigFestivalRuleChanged: reloadAll()
    onConfigTithiModeChanged: reloadAll()

    toolTipMainText: currentPanchanga ? `${currentPanchanga.masa} • ${currentPanchanga.paksha} ${configLang === "devanagari" ? "पक्ष" : "Paksha"} • ${currentPanchanga.tithi}` : i18n("Kālayantra")
    toolTipSubText: currentPanchanga ? (
        `${currentPanchanga.vaara}, ${currentPanchanga.date} (${currentPanchanga.era_name} ${currentPanchanga.era_year})\n\n` +
        (configLang === "devanagari" ? "सूर्योदय: " : "Sunrise: ") + `${currentPanchanga.sunrise}  •  ` + (configLang === "devanagari" ? "सूर्यास्त: " : "Sunset: ") + `${currentPanchanga.sunset}\n` +
        (configLang === "devanagari" ? "चंद्रोदय: " : "Moonrise: ") + `${currentPanchanga.moonrise}  •  ` + (configLang === "devanagari" ? "चंद्रास्त: " : "Moonset: ") + `${currentPanchanga.moonset}\n\n` +
        (configLang === "devanagari" ? "तिथि: " : "Tithi: ") + `${currentPanchanga.tithi}\n` +
        (configLang === "devanagari" ? "नक्षत्र: " : "Nakshatra: ") + `${currentPanchanga.nakshatra}\n` +
        (configLang === "devanagari" ? "योग: " : "Yoga: ") + `${currentPanchanga.yoga}\n` +
        (configLang === "devanagari" ? "करण: " : "Karana: ") + `${currentPanchanga.karana}\n` +
        (configLang === "devanagari" ? "वैदिक समय: " : "Vedic Time: ") + `${liveGhadiTime.split(':')[0]} Ghadi, ${liveGhadiTime.split(':')[1] || "00"} Vipal\n\n` +
        (configLang === "devanagari" ? "पर्व/उत्सव: " : "Festival: ") + `${currentPanchanga.festivals && currentPanchanga.festivals.length > 0 ? (currentPanchanga.festivals[0].name + (currentPanchanga.festivals[0].anniversary_display ? " (" + currentPanchanga.festivals[0].anniversary_display + ")" : "")) : (configLang === "devanagari" ? "कोई नहीं" : "None")}`
    ) : ""

    // Calendar state properties
    property int currentYear: new Date().getFullYear()
    property int currentMonth: new Date().getMonth() + 1 // 1-indexed

    property string todayDateString: getTodayString()
    property string currentlyViewedDateString: getTodayString()

    property var threeMonthsData: []
    property var currentPanchanga: null
    property string liveGhadiTime: "00:00"

    // Component configurations
    compactRepresentation: CompactRepresentation {}
    fullRepresentation: Kaladarshana {
        id: kaladarshanaView
    }

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
            `lat=${configLatitude}`,
            `lon=${configLongitude}`,
            `alt=${configAltitude}`,
            `tz=${configTimezone}`,
            `lang=${configLang}`,
            `calendar_system=${configCalendarSystem}`,
            `month_system=${configMonthSystem}`,
            `festival_rule=${configFestivalRule}`,
            `tithi_mode=${configTithiMode}`
        ];
        if (extraParams) {
            params.push(extraParams);
        }
        return params.join('&');
    }

    function fetchDay(dateStr) {
        var xhr = new XMLHttpRequest();
        var buster = "_t=" + Date.now();
        var query = buildQueryString(`date=${dateStr}&${buster}`);
        xhr.open("GET", `http://127.0.0.1:8642/day?${query}`, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    if (dateStr === getTodayString()) {
                        currentPanchanga = data;
                        liveGhadiTime = data.ghadi;

                        if (threeMonthsData) {
                            var tmp = threeMonthsData.slice();
                            var changed = false;
                            for (var i = 0; i < tmp.length; i++) {
                                if (tmp[i] && tmp[i].date === dateStr) {
                                    tmp[i] = data;
                                    changed = true;
                                    break;
                                }
                            }
                            if (changed) {
                                threeMonthsData = tmp;
                            }
                        }

                        if (typeof kaladarshanaView !== 'undefined' && kaladarshanaView && kaladarshanaView.selectedDayData && kaladarshanaView.selectedDayData.date === dateStr) {
                            kaladarshanaView.selectedDayData = data;
                        }
                    }
                } catch(e) {
                    console.error("Failed to parse day response: ", e);
                }
            }
        };
        xhr.send();
    }

    // Asynchronous network fetch for 3 consecutive months to cover full Hindu lunar month range
    function fetchThreeMonths(year, month) {
        var prevY = year;
        var prevM = month - 1;
        if (prevM === 0) { prevM = 12; prevY -= 1; }
        
        var nextY = year;
        var nextM = month + 1;
        if (nextM === 13) { nextM = 1; nextY += 1; }
        
        var results = { "prev": [], "curr": [], "next": [] };
        var completed = 0;
        
        function handleCompleted() {
            completed++;
            if (completed === 3) {
                var combined = [];
                combined = combined.concat(results.prev);
                combined = combined.concat(results.curr);
                combined = combined.concat(results.next);
                threeMonthsData = combined;
            }
        }
        
        function fetchSingle(y, m, key) {
            var xhr = new XMLHttpRequest();
            var buster = "_t=" + Date.now();
            var query = buildQueryString("year=" + y + "&month=" + m + "&" + buster);
            xhr.open("GET", "http://127.0.0.1:8642/month?" + query, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        try {
                            results[key] = JSON.parse(xhr.responseText);
                        } catch(e) {
                            console.error("Failed to parse month data for", y, m, e);
                            results[key] = [];
                        }
                    } else {
                        results[key] = [];
                    }
                    handleCompleted();
                }
            };
            xhr.send();
        }
        
        fetchSingle(prevY, prevM, "prev");
        fetchSingle(year, month, "curr");
        fetchSingle(nextY, nextM, "next");
    }

    // Reload all data on configuration changes
    function reloadAll() {
        fetchDay(getTodayString());
        fetchThreeMonths(currentYear, currentMonth);
    }



    // Periodic timer to sync current day data and update Ghadi-Pal time
    Timer {
        interval: 5000
        running: true
        repeat: true
        onTriggered: {
            todayDateString = getTodayString();
            fetchDay(getTodayString());
        }
    }

    // Initial load
    Component.onCompleted: {
        reloadAll();
    }
}
