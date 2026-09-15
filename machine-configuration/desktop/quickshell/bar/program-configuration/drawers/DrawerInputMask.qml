import Quickshell
import QtQuick

Region {
    id: drawerInputMaskRoot

    required property int barTotalWidth
    required property real windowWidth
    required property real windowHeight
    required property int shapeJunctionRadius
    required property Item popoutItem
    required property Item dashboardItem
    required property Item launcherItem
    required property Item sessionItem
    required property Item utilitiesItem
    required property Item osdItem
    required property Item sidebarItem

    x: barTotalWidth
    y: 0
    width: windowWidth - barTotalWidth
    height: windowHeight
    intersection: Intersection.Xor

    regions: [
        Region {
            x: barTotalWidth
            y: 0
            width: windowWidth - barTotalWidth
            height: barTotalWidth / 3
            intersection: Intersection.Subtract
        },
        Region {
            x: barTotalWidth
            y: windowHeight - barTotalWidth / 3
            width: windowWidth - barTotalWidth
            height: barTotalWidth / 3
            intersection: Intersection.Subtract
        },
        Region {
            x: windowWidth - barTotalWidth / 3
            y: barTotalWidth / 3
            width: barTotalWidth / 3
            height: windowHeight - barTotalWidth * 2 / 3
            intersection: Intersection.Subtract
        },
        Region {
            x: popoutItem.x
            y: popoutItem.visible ? popoutItem.y - shapeJunctionRadius : 0
            width: popoutItem.visible ? popoutItem.width : 0
            height: popoutItem.visible ? popoutItem.height + shapeJunctionRadius * 2 : 0
            intersection: Intersection.Subtract
        },
        Region {
            x: dashboardItem.x
            y: dashboardItem.visible ? dashboardItem.y : 0
            width: dashboardItem.visible ? dashboardItem.width : 0
            height: dashboardItem.visible ? dashboardItem.height : 0
            intersection: Intersection.Subtract
        },
        Region {
            x: launcherItem.x
            y: launcherItem.visible ? launcherItem.y : 0
            width: launcherItem.visible ? launcherItem.width : 0
            height: launcherItem.visible ? launcherItem.height : 0
            intersection: Intersection.Subtract
        },
        Region {
            x: sessionItem.visible ? sessionItem.x : 0
            y: sessionItem.visible ? sessionItem.y : 0
            width: sessionItem.visible ? sessionItem.width : 0
            height: sessionItem.visible ? sessionItem.height : 0
            intersection: Intersection.Subtract
        },
        Region {
            x: utilitiesItem.visible ? utilitiesItem.x : 0
            y: utilitiesItem.visible ? utilitiesItem.y : 0
            width: utilitiesItem.visible ? utilitiesItem.width : 0
            height: utilitiesItem.visible ? utilitiesItem.height : 0
            intersection: Intersection.Subtract
        },
        Region {
            x: osdItem.visible ? osdItem.x : 0
            y: osdItem.visible ? osdItem.y : 0
            width: osdItem.visible ? osdItem.width : 0
            height: osdItem.visible ? osdItem.height : 0
            intersection: Intersection.Subtract
        },
        Region {
            x: sidebarItem.visible ? sidebarItem.x : 0
            y: sidebarItem.visible ? sidebarItem.y : 0
            width: sidebarItem.visible ? sidebarItem.width : 0
            height: sidebarItem.visible ? sidebarItem.height : 0
            intersection: Intersection.Subtract
        }
    ]
}
