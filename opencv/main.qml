import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.1

ApplicationWindow {
    visible: true
    width: 300
    height: 200
    title: "Hello World App"

    MessageDialog {
        id: messageDialog
        title: "Message"
        text: "Hello, Jimmy~~"
        onAccepted: console.log("Dialog closed")
    }

    Button {
        text: "Hello, World!"
        anchors.centerIn: parent
        onClicked: {
            messageDialog.open()
        }
    }
}