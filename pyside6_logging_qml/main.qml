import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 400
    height: 300
    title: "Logging Example"

    Column {
        anchors.centerIn: parent
        spacing: 10

        Text {
            id: logText
            text: ""
            wrapMode: Text.Wrap
        }

        Button {
            text: "Log Test"
            onClicked: {
                logText.text = ""
            }
        }
    }

    Connections {
        target: logEmitter
        function onLogChanged(message) {
            logText.text += message + "\n"
        }
    }
}
