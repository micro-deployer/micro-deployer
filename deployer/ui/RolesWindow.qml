import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls
import Qt.labs.platform
import Qt.labs.qmlmodels

Window {
    width: 800
    height: 400
    visible: false
    title: "Roles"

    TableView {
        anchors.fill: parent
        columnSpacing: 1
        rowSpacing: 1
        boundsBehavior: Flickable.StopAtBounds


        model: application.roles

        delegate: DelegateChooser {
            DelegateChoice {
                row: application.roles.header
                delegate: Label {
                    text: model.display
                }
            }
            DelegateChoice {
                column: application.roles.columns.Name
                delegate: TextField {
                    text: model.display
                    selectByMouse: true
                    implicitWidth: 140
                    onAccepted: model.edit = text
                }
            }
        }
    }
    function listProperty(item)
    {
        for (var p in item)
        console.log(p + ": " + item[p]);
    }
}

