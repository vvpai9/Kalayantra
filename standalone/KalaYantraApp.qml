import QtQuick
import QtQuick.Window
import org.kde.kirigami as Kirigami
import "../contents/ui"

Window {
    id: root
    title: (plasmoid.configuration.lang === "devanagari") ? "कालयन्त्र" : "Kālayantra"
    width: 1200
    height: 760
    minimumWidth: 960
    minimumHeight: 620
    visible: true
    color: Kirigami.Theme.backgroundColor

    property QtObject plasmoid: QtObject {
        property QtObject configuration: QtObject {
            property string lang: "en"
            property double latitude: 23.1765
            property double longitude: 75.7885
            property double altitude: 511.0
            property double timezone: 5.5
            property string calendarSystem: "shaka"
            property string monthSystem: "amavasyanta"
            property string festivalRule: "vaishnava"
            property string tithiMode: "traditional"
            property string ayanamsa: "lahiri"
        }
    }

    function i18n(text) { return text; }
    function i18nc(context, text) { return text; }
    function i18nd(context, text) { return text; }
    function i18nct(context, comment, text) { return text; }

    readonly property string configLang: plasmoid.configuration.lang
    readonly property double configLatitude: plasmoid.configuration.latitude
    readonly property double configLongitude: plasmoid.configuration.longitude
    readonly property double configAltitude: plasmoid.configuration.altitude
    readonly property double configTimezone: plasmoid.configuration.timezone
    readonly property string configCalendarSystem: plasmoid.configuration.calendarSystem
    readonly property string configMonthSystem: plasmoid.configuration.monthSystem
    readonly property string configFestivalRule: plasmoid.configuration.festivalRule
    readonly property string configTithiMode: plasmoid.configuration.tithiMode
    readonly property string configAyanamsa: plasmoid.configuration.ayanamsa

    onConfigLangChanged: reloadAll()
    onConfigLatitudeChanged: reloadAll()
    onConfigLongitudeChanged: reloadAll()
    onConfigAltitudeChanged: reloadAll()
    onConfigTimezoneChanged: reloadAll()
    onConfigCalendarSystemChanged: reloadAll()
    onConfigMonthSystemChanged: reloadAll()
    onConfigFestivalRuleChanged: reloadAll()
    onConfigTithiModeChanged: reloadAll()
    onConfigAyanamsaChanged: reloadAll()

    property bool expanded: true

    property int currentYear: new Date().getFullYear()
    property int currentMonth: new Date().getMonth() + 1

    property string todayDateString: getTodayString()
    property string currentlyViewedDateString: getTodayString()

    property var threeMonthsData: []
    property var currentPanchanga: null
    property string liveGhadiTime: "00:00"

    function getTodayString() {
        var d = new Date();
        var y = d.getFullYear();
        var m = String(d.getMonth() + 1).padStart(2, '0');
        var day = String(d.getDate()).padStart(2, '0');
        return `${day}-${m}-${y}`;
    }

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
            `tithi_mode=${configTithiMode}`,
            `ayanamsa=${configAyanamsa}`
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
                    }
                } catch(e) {
                    console.error("Failed to parse day response: ", e);
                }
            }
        };
        xhr.send();
    }

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

    function applyConfig(data) {
        if (!data) return;
        plasmoid.configuration.lang = data.lang || plasmoid.configuration.lang;
        plasmoid.configuration.latitude = (data.lat !== undefined) ? data.lat : plasmoid.configuration.latitude;
        plasmoid.configuration.longitude = (data.lon !== undefined) ? data.lon : plasmoid.configuration.longitude;
        plasmoid.configuration.altitude = (data.alt !== undefined) ? data.alt : plasmoid.configuration.altitude;
        plasmoid.configuration.timezone = (data.tz !== undefined) ? data.tz : plasmoid.configuration.timezone;
        plasmoid.configuration.calendarSystem = data.calendar_system || plasmoid.configuration.calendarSystem;
        plasmoid.configuration.monthSystem = data.month_system || plasmoid.configuration.monthSystem;
        plasmoid.configuration.festivalRule = data.festival_rule || plasmoid.configuration.festivalRule;
        plasmoid.configuration.tithiMode = data.tithi_mode || plasmoid.configuration.tithiMode;
        plasmoid.configuration.ayanamsa = data.ayanamsa || plasmoid.configuration.ayanamsa;
        if (data.city) {
            root.title = (plasmoid.configuration.lang === "devanagari") ? "कालयन्त्र – " + data.city : "Kālayantra – " + data.city;
        }
        reloadAll();
    }

    function fetchConfig() {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/config", true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    try {
                        applyConfig(JSON.parse(xhr.responseText));
                    } catch(e) {
                        console.error("Failed to parse config response: ", e);
                        reloadAll();
                    }
                } else {
                    reloadAll();
                }
            }
        };
        xhr.send();
    }

    function reloadAll() {
        fetchDay(getTodayString());
        fetchThreeMonths(currentYear, currentMonth);
    }

    function getGregorianMonthName(m) {
        var names = [
            i18n("January"), i18n("February"), i18n("March"), i18n("April"),
            i18n("May"), i18n("June"), i18n("July"), i18n("August"),
            i18n("September"), i18n("October"), i18n("November"), i18n("December")
        ];
        return names[m - 1];
    }

    function formatGregorianDateStr(dateStr) {
        if (!dateStr) return "";
        var parts = dateStr.split('-');
        if (parts.length < 3) return dateStr;
        var day = parseInt(parts[0]);
        var monthIdx = parseInt(parts[1]);
        var year = parts[2];
        return `${day} ${getGregorianMonthName(monthIdx)} ${year}`;
    }

    Timer {
        interval: 5000
        running: true
        repeat: true
        onTriggered: {
            todayDateString = getTodayString();
            fetchDay(getTodayString());
        }
    }

    Component.onCompleted: {
        fetchConfig();
    }

    Kaladarshana {
        anchors.fill: parent
        showTools: true
    }
}