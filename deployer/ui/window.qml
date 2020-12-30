import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls
import Qt.labs.platform
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
                row: 0
                delegate: Label {
                    text: model.display
                }
            }
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
                    onAccepted: model.edit = text
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
                delegate: TextField {
                    text: model.display
                    onAccepted: model.edit = text
                }
            }
            DelegateChoice {
                column: 4
                delegate: Button {
                    enabled: false
                    text: model.display
                    onClicked: function() {model.edit = folderDialog.open()}
                }
            }
            DelegateChoice {
                column: 5
                delegate: CheckBox {
                    checked: model.display
//                    enabled: false
//                    onToggled: model.edit = checked
//                    onValueChanged: application.devices.setData(0, {amount: value})
                }
            }
            DelegateChoice {
                column: 6
                delegate: Button {
                    text: "Deploy"
                    enabled: model.display
                    onClicked: function() {
                        application.deploy(model.row)
                    }
                }
            }
            DelegateChoice {
                column: 7
                delegate: ProgressBar {
                    value: model.progress==null?0:model.progress
                    z: 0
                    Label {
                        text: model.display
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        z: 1
                    }
                }
            }
        }
    }
    function listProperty(item)
    {
        for (var p in item)
        console.log(p + ": " + item[p]);
    }
    FolderDialog {
        id: folderDialog
        options: FolderDialog.ShowDirsOnly
    }
}

