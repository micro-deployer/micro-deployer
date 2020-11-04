import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls
import Qt.labs.qmlmodels

ApplicationWindow {
    width: 800
    height: 400
    visible: true
    title: "Micro Deployer"

    onClosing: function() {application.stop()}

    TableView {
        id: tableView
        anchors.fill: parent
        columnSpacing: 1
        rowSpacing: 1
        boundsBehavior: Flickable.StopAtBounds


        model: application.devices



        delegate: DelegateChooser {
            DelegateChoice {
                column: 0
                delegate: CheckBox {
                    checked: model.display
                    onToggled: model.edit = checked
//                    onValueChanged: application.devices.setData(0, {amount: value})
                }
            }
             DelegateChoice {
                column: 1
                delegate: TextField {
                    text: model.display
                    selectByMouse: true
                    implicitWidth: 140
                    onTextEdited: model.edit = text
                }
            }
            DelegateChoice {
                column: 2
                delegate: TextField {
                    text: model.display
                    readOnly: true
                    selectByMouse: true
                    implicitWidth: 140
//                    onAccepted: model.display = text
                }
            }
            DelegateChoice {
                column: 3
                delegate: Button {
                    text: "Deploy"
                    enabled: model.display
                    onClicked: function() {this.enabled = false; application.deploy(model.row)}
                }
            }
            DelegateChoice {
                column: 4
                ProgressBar {
                    value: model.display==null?0:model.display
                    visible: model.display != null
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