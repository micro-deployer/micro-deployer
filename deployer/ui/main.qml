import QtQuick
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls
import Qt.labs.platform
import Qt.labs.qmlmodels


ApplicationWindow {
    id: mainWindow
    width: 800
    height: 400
    visible: true
    title: "Micro Deployer"

    onClosing: {application.stop()}

    TableView {
        anchors.fill: parent
        columnSpacing: 1
        rowSpacing: 1
        boundsBehavior: Flickable.StopAtBounds


        model: application.devices

        delegate: DelegateChooser {
            DelegateChoice {
                row: application.devices.header
                delegate: Label {
                    text: model.display
                }
            }
            DelegateChoice {
                column: application.devices.columns.IsSaved
                delegate: CheckBox {
                    checked: model.display
                    onToggled: model.edit = checked
//                    onValueChanged: application.devices.setData(0, {amount: value})
                }
            }
             DelegateChoice {
                column: application.devices.columns.Name
                delegate: TextField {
                    text: model.display
                    selectByMouse: true
                    implicitWidth: 140
                    onAccepted: model.edit = text
                }
            }
            DelegateChoice {
                column: application.devices.columns.UID
                delegate: TextField {
                    text: model.display
                    readOnly: true
                    selectByMouse: true
                    implicitWidth: 140
//                    onAccepted: model.display = text
                }
            }
//            DelegateChoice {
//                column: devices.columns.UID
//                delegate: TextField {
//                    text: model.display
//                    onAccepted: model.edit = text
//                }
//            }
//            DelegateChoice {
//                column: 4
//                delegate: Button {
//                    enabled: false
//                    text: model.display
//                    onClicked: function() {model.edit = folderDialog.open()}
//                }
//            }
            DelegateChoice {
                column: application.devices.columns.IsAvailable
                delegate: CheckBox {
                    checked: model.display
//                    enabled: false
//                    onToggled: model.edit = checked
//                    onValueChanged: application.devices.setData(0, {amount: value})
                }
            }
            DelegateChoice {
                column: application.devices.columns.Deploy
                delegate: Button {
                    text: "Deploy"
                    enabled: model.display
                    onClicked: function() {
                        application.deploy(model.row)
                    }
                }
            }
            DelegateChoice {
                column: application.devices.columns.Progress
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
//    FolderDialog {
//        id: folderDialog
//        options: FolderDialog.ShowDirsOnly
//    }
    Button {
        text: "Roles"
        onClicked: {
            rolesWindow.visible = true
//            var component = Qt.createComponent("roles.qml");
//            win = component.createObject(mainWindow);
//            win.show();
        }
    }
    RolesWindow {
        id: rolesWindow
        visible: false
    }
}

