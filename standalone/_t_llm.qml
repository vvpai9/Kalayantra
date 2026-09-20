import QtQuick 2.15

Window {
    width: 200
    height: 200
    visible: true

    Component.onCompleted: {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "http://127.0.0.1:8642/llm", true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== XMLHttpRequest.DONE) return;
            console.log("STATUS=" + xhr.status + " BODY=" + xhr.responseText);
            Qt.quit();
        };
        xhr.send();
    }
}