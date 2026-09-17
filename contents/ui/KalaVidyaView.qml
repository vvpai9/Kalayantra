import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: view
    implicitWidth: 520
    implicitHeight: 640

    property var catalog: []
    property var categories: []
    property var conceptDetail: null

    readonly property var uiTxt: ({
        "en": {
            "title": "KalaVidya — Knowledge Base",
            "all": "All topics",
            "searchPlaceholder": "Search concepts…",
            "searchBtn": "Search",
            "source": "Source",
            "formula": "Formula",
            "example": "Worked Example",
            "seeAlso": "See also",
            "category": "Category",
            "topic": "Topic:",
            "loading": "Loading…",
            "parseFail": "Failed to parse response.",
            "engineErr": "Engine error (%1). Is the daemon running?",
            "detailNotNeeded": "Select a concept for details."
        },
        "iast": {
            "title": "KālaVidyā — Jñāna-kośa",
            "all": "Sarve viṣayāḥ",
            "searchPlaceholder": "Khojeṁ…",
            "searchBtn": "Khojeṁ",
            "source": "Srotra",
            "formula": "Sūtra",
            "example": "Udāharaṇa",
            "seeAlso": "Dṛśyatu api",
            "category": "Varga",
            "topic": "Viṣayaḥ:",
            "loading": "Pūraṇaṁ…",
            "parseFail": "Uttara nahīṁ milā.",
            "engineErr": "Yantra-truṭi (%1).",
            "detailNotNeeded": "Vivaraṇa hṛdayaṁ pātu."
        },
        "devanagari": {
            "title": "कालविद्या — ज्ञान कोश",
            "all": "सभी विषय",
            "searchPlaceholder": "अवधारणा खोजें…",
            "searchBtn": "खोजें",
            "source": "स्रोत",
            "formula": "सूत्र",
            "example": "उदाहरण",
            "seeAlso": "इन्हें भी देखें",
            "category": "श्रेणी",
            "topic": "विषय:",
            "loading": "लोड हो रहा है…",
            "parseFail": "प्रतिक्रिया पार्स नहीं हुई।",
            "engineErr": "इंजन त्रुटि (%1)।",
            "detailNotNeeded": "विवरण के लिए अवधारणा चुनें।"
        }
    })

    function langKey() {
        return (typeof plasmoid !== "undefined" && plasmoid.configuration) ? plasmoid.configuration.lang : "en";
    }

    function txt(key) {
        var t = uiTxt[langKey()] || uiTxt["en"];
        return t[key] !== undefined ? t[key] : key;
    }

    function fetchUrl(url, onOk) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642" + url, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            if (xhr.status === 200) {
                try { onOk(JSON.parse(xhr.responseText)); return; } catch (e) {}
                statusMessage.type = Kirigami.MessageType.Error;
            } else {
                statusMessage.type = Kirigami.MessageType.Error;
                statusMessage.text = view.txt("engineErr").arg(xhr.status);
            }
            statusMessage.visible = true;
        };
        xhr.send();
    }

    function loadCatalog(category) {
        var cat = category || "";
        fetchUrl("/vidya?lang=" + encodeURIComponent(langKey()) + (cat ? "&category=" + encodeURIComponent(cat) : ""),
                 function(d) {
                     view.catalog = d.catalog || [];
                     view.categories = d.categories || [];
                     catCombo.model = [view.txt("all")].concat(view.categories.map(function(c) { return c.title; }));
                     if (view.catalog.length > 0) {
                         topicCombo.model = view.catalog;
                         topicCombo.currentIndex = 0;
                         view.openConcept(view.catalog[0].id);
                     } else {
                         topicCombo.model = [];
                         view.conceptDetail = null;
                     }
                 });
    }

    function openConcept(id) {
        view.conceptDetail = null;
        fetchUrl("/vidya?lang=" + encodeURIComponent(langKey()) + "&concept=" + encodeURIComponent(id),
                 function(d) { view.conceptDetail = d.concept || null; });
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Kirigami.Units.smallSpacing

        Kirigami.Heading { text: view.txt("title"); level: 4 }

        RowLayout {
            Layout.fillWidth: true; spacing: Kirigami.Units.smallSpacing
            Label { text: view.txt("category") }
            ComboBox {
                id: catCombo
                Layout.preferredWidth: Kirigami.Units.gridUnit * 10
                onActivated: {
                    var cid = catCombo.currentIndex <= 0 ? "" : (view.categories[catCombo.currentIndex - 1] || {}).id;
                    view.loadCatalog(cid);
                }
            }
            Label { text: view.txt("topic") }
            ComboBox {
                id: topicCombo
                Layout.fillWidth: true
                textRole: "title"
                onActivated: {
                    var c = view.catalog[ currentIndex ];
                    if (c) view.openConcept(c.id);
                }
            }
        }

        Kirigami.InlineMessage { id: statusMessage; Layout.fillWidth: true; type: Kirigami.MessageType.Warning; visible: false }

        ScrollView {
            id: detailScroll
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded
            contentItem: ColumnLayout {
                width: detailScroll.width
                    spacing: Kirigami.Units.smallSpacing

                    Label { text: view.txt("detailNotNeeded"); visible: !view.conceptDetail; opacity: 0.6; Layout.fillWidth: true; wrapMode: Text.WordWrap }

                    Text {
                        visible: !!view.conceptDetail
                        text: view.conceptDetail ? view.conceptDetail.title : ""
                        Layout.fillWidth: true
                        color: Kirigami.Theme.textColor
                        font.pixelSize: Kirigami.Units.gridUnit * 1.3
                        font.bold: true
                        wrapMode: Text.WordWrap
                    }

                    Label {
                        visible: !!view.conceptDetail
                        text: view.conceptDetail ? (txt("category") + ": " + (view.conceptDetail.category_title || view.conceptDetail.category || "")) : ""
                        Layout.fillWidth: true; font.pixelSize: Kirigami.Units.gridUnit * 0.75; opacity: 0.7
                    }

                    Label {
                        visible: !!view.conceptDetail && !!view.conceptDetail.summary
                        text: view.conceptDetail ? view.conceptDetail.summary : ""
                        Layout.fillWidth: true; wrapMode: Text.WordWrap; font.bold: true
                    }

                    Label {
                        visible: !!view.conceptDetail && !!view.conceptDetail.detail
                        text: view.conceptDetail ? view.conceptDetail.detail : ""
                        Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: Kirigami.Units.gridUnit * 0.9
                    }

                    ColumnLayout {
                        visible: !!view.conceptDetail && !!view.conceptDetail.formula
                        Layout.fillWidth: true; spacing: 2
                        Label { text: view.txt("formula"); font.bold: true }
                        Item {
                            Layout.fillWidth: true
                            implicitHeight: formulaText.implicitHeight + 12
                            Rectangle {
                                anchors.fill: parent
                                radius: 4
                                color: Kirigami.Theme.backgroundColor || Qt.rgba(0.18, 0.18, 0.18, 1)
                                border.color: Kirigami.Theme.separatorColor || "#555"
                            }
                            Text { id: formulaText; text: view.conceptDetail ? view.conceptDetail.formula : ""; anchors.fill: parent; anchors.margins: 6; color: Kirigami.Theme.textColor; font.family: "monospace"; font.pixelSize: Kirigami.Units.gridUnit * 0.8; wrapMode: Text.WordWrap }
                        }
                    }

                    ColumnLayout {
                        visible: !!view.conceptDetail && !!view.conceptDetail.example
                        Layout.fillWidth: true; spacing: 2
                        Label { text: view.txt("example"); font.bold: true }
                        Text { text: view.conceptDetail ? view.conceptDetail.example : ""; Layout.fillWidth: true; color: Kirigami.Theme.textColor; wrapMode: Text.WordWrap; font.pixelSize: Kirigami.Units.gridUnit * 0.85; font.italic: true }
                    }

                    ColumnLayout {
                        visible: !!view.conceptDetail && !!view.conceptDetail.source
                        Layout.fillWidth: true; spacing: 2
                        Label { text: view.txt("source"); font.bold: true }
                        Label { text: view.conceptDetail ? view.conceptDetail.source : ""; Layout.fillWidth: true; wrapMode: Text.WordWrap; font.pixelSize: Kirigami.Units.gridUnit * 0.8; opacity: 0.8 }
                    }

                    ColumnLayout {
                        visible: !!view.conceptDetail && !!(view.conceptDetail.see_also && view.conceptDetail.see_also.length > 0)
                        Layout.fillWidth: true; spacing: 4
                        Label { text: view.txt("seeAlso"); font.bold: true }
                        Flow {
                            Layout.fillWidth: true; spacing: 6
                            Repeater {
                                model: view.conceptDetail ? (view.conceptDetail.see_also || []) : []
                                Button {
                                    text: modelData
                                    flat: true
                                    padding: 4
                                    onClicked: view.openConcept(modelData)
                                    background: Rectangle { radius: 3; color: Kirigami.Theme.highlightColor; opacity: enabled ? 0.25 : 0.1 }
                                }
                            }
                        }
                    }
                }
            }
    }

    Component.onCompleted: view.loadCatalog("")
}