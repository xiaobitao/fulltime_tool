import math

from PySide2 import QtCore, QtGui, QtWidgets
import json
from util.database import get_demo


class InvasionAlert():
    # 数据库处理后发送事件过来，同步alert,根据ID同步
    demo_start_station = None
    demo_end_station = None
    rel_station = None
    rel_x = 0
    rel_y = 0
    level = 0
    status = 0
    # 对应到数据库, 更新状态
    alertid = 0
    def __init__(self, demo_start, demo_end, level):
        self.demo_start_station = demo_start
        self.demo_end_station = demo_end
        self.level = level

    def set_relpostion(self, rel_station, rel_x, rel_y):
        self.rel_station = rel_station
        self.rel_x = rel_x
        self.rel_y = rel_y



class LineItem(QtWidgets.QGraphicsLineItem):
    # if scene scale > item scale, show
    showscale = 0
    def __init__(self, x1, y1, x2, y2, parent=None):
        super(LineItem, self).__init__(x1, y1, x2, y2,parent)

    def setScaleFilter(self, scale):
        self.showscale = scale

class MarkItem(QtWidgets.QGraphicsItem):

    geomery = None
    text = ""
    # def __init__(self, parent=None, scene=None):
    #     super(MarkItem, self).__init__(parent, scene)

    def setBoundRect(self, rect):
        self.geomery = rect

    def setText(self, text):
        self.text = text

    def paint(self, painter, option, widget):
        # painter.drawText(self.geomery, self.text, QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
        painter.drawText(self.geomery, self.text, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)

    def boundingRect(self):
        return self.geomery

class MarkTextItem(QtWidgets.QGraphicsTextItem):
    showscale = 0
    lostFocus = QtCore.Signal(QtWidgets.QGraphicsTextItem)

    def __init__(self, parent=None, scene=None):
        super(MarkTextItem, self).__init__(parent, scene)
        self.textOP = QtGui.QTextOption()
        self.textOP.setAlignment(QtCore.Qt.AlignCenter)
        self.textOP.setWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            self.selectedChange.emit(self)
        return value

    def focusOutEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        pass

    def paint(self,painter, option, widget):
        painter.drawText(self.boundingRect(), "aaaaa", self.textOP)
        super(MarkTextItem, self).paint(painter, option, widget)




class StationCircleItem(QtWidgets.QGraphicsEllipseItem):
    showscale = 1.0
    text = ""
    
    # def paint(self, painter, option, widget):
    #     rect = self.rect()
    #     newrect = QtCore.QRectF(rect.left(), rect.top() - 2*rect.height(), 100, 20)
    #     painter.drawText(newrect, self.text)
    #     super(StationCircleItem, self).paint(painter, option, widget)

    def setText(self, text):
        self.text = text

class MapScene(QtWidgets.QGraphicsScene):

    InsertItem, InsertLine, InsertText, MoveItem  = range(4)

    stations = None
    doubleclick = QtCore.Signal(QtGui.QMouseEvent)

    rel_startx = 50
    rel_endx = 700
    rel_y = 145
    mode = "default"
    invalerts = []
    alertlineItems = []
    alertpointsItems = []
    alerttime = 0
    twostation_start = None

    def __init__(self, parent=None):
        super(MapScene, self).__init__(parent)

        # self.myItemMenu = itemMenu
        self.myMode = self.MoveItem
        # self.myItemType = DiagramItem.Step
        self.line = None
        self.textItem = None
        self.myItemColor = QtCore.Qt.white
        self.myTextColor = QtCore.Qt.black
        self.myLineColor = QtCore.Qt.black
        self.myCircleColor = QtCore.Qt.red
        self.myFont = QtGui.QFont()
        self.initfromjson()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.drawAlarm)
        self.timer.start(500)


    def setLineColor(self, color):
        self.myLineColor = color

    def setTextColor(self, color):
        self.myTextColor = color

    def setFont(self, font):
        self.myFont = font

    def setMode(self, mode):
        self.myMode = mode

    def setItemType(self, type):
        self.myItemType = type

    def clearAlerts(self):
        for item in self.alertlineItems:
            self.removeItem(item)
        for item in self.alertpointsItems:
            self.removeItem(item)
        del self.alertlineItems[:]
        del self.alertpointsItems[:]
        del self.invalerts[:]

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.mode == "station":
                return
            self.scaleTwoStation(event)
        elif event.button() == QtCore.Qt.RightButton:
            if self.mode == "default":
                return
            self.scaleToDefault()

    def setAlarmLine(self, x1, y1, x2, y2, color):
        # self.clear()
        for tmpl in self.alertlineItems:
            # print(type(tmpl))
            ln = tmpl.line()
            if self.floatequal(ln.x1(), x1) and self.floatequal(ln.x2(), x2) and self.floatequal(ln.y1(), y1) and self.floatequal(ln.y2(), y2):
            # if ln.x1() == x1 and ln.x2() == x2 and ln.y1() == y1 and ln.y2() == y2:
                tmpl.setPen(QtGui.QPen(color, 2))
                # print("return")
                return

        line = LineItem(x1, y1, x2, y2)
        line.setPen(QtGui.QPen(color, 2))
        line.setZValue(1)
        self.alertlineItems.append(line)
        self.addItem(line)
        
        

    def setLine(self, x1, y1, x2, y2, color=None):
        space = 50
        line = LineItem(x1, y1, x2, y2)
        # self.line.setMode(self.mode)
        # 不同mode决定画线不一样
        # 研究线如何适应屏幕分辨率
      
        line.setPen(QtGui.QPen(self.myLineColor, 2))
        if self.mode == "default":
            self.addItem(line)
        elif self.mode == "station":
            self.addItem(line)
            # width = y2 - y1
            rel_width = self.rel_endx - self.rel_startx
            dx = rel_width / space
            for i in range(1, int(dx)):
                # painter.setBrush(QtGui.QBrush(QtCore.Qt.green))
                # get alert, set alert color
                rect = QtCore.QRectF(self.rel_startx + i * space - 5,self.rel_y - 10 , 10, 20)
                ritem = QtWidgets.QGraphicsRectItem(rect)
                ritem.setPen(QtGui.QPen(QtCore.Qt.green, 2))
                ritem.setBrush(QtGui.QBrush( QtCore.Qt.green))
                ritem.setZValue(1)
                self.addItem(ritem)
                # painter.drawRect(x1 + i * self.space - 5, y1 -10, 10, 20)

    def floatequal(self, x, y):
        if abs(x - y) < 0.01:
            return True
        else:
            return False

    def setAlarmCircle(self, x, y, radius, color):
        for tmpp in self.alertpointsItems:
            # print(type(tmpl))
            rect = tmpp.rect()
            if (self.floatequal(rect.x(), x - radius / 2) and self.floatequal(rect.y(), y - radius / 2) and
               self.floatequal(rect.width(), radius) and self.floatequal(rect.height(), radius)):
            # if self.floatequal(ln.x1(), x1) and ln.x2() == x2 and ln.y1() == y1 and ln.y2() == y2:
                tmpp.setPen(QtGui.QPen(color, 2))
                tmpp.setBrush(QtGui.QBrush(color))
                return
        alertcircle = QtWidgets.QGraphicsEllipseItem(x - radius / 2, y - radius / 2, radius, radius)
        alertcircle.setPen(QtGui.QPen(color, 2))
        alertcircle.setBrush(QtGui.QBrush(color))
        alertcircle.setZValue(1)
        alertcircle.setOpacity(100)
        self.alertpointsItems.append(alertcircle)
        self.addItem(alertcircle)


    def setCircle(self, x, y, radius, name):
        circle = StationCircleItem(x - radius / 2, y - radius / 2, radius, radius)
        circle.setPen(QtGui.QPen(self.myCircleColor, 2))
        circle.setBrush(QtGui.QBrush(self.myCircleColor))
        circle.setZValue(1)
        circle.setOpacity(100)
        # circle.setText(name)
        stname = MarkItem()
        stname.setText(name)
        rect = QtCore.QRectF(x - radius, y +  2*radius, 20, 100)
        stname.setBoundRect(rect)
        # stname.setPos(x - radius / 2, y - radius )
        self.addItem(circle)
        self.addItem(stname)

    def initfromjson(self):
        with open('./stations.json', encoding="utf-8") as json_file:
            data = json.load(json_file)
            tmpstation = data["stations"]
            self.stations = sorted(tmpstation,  key=lambda k: k['number'])
            lst_x = -100
            lst_y = -100
            for st in self.stations:
                name = st["name"]
                x = st['x']
                y= st['y']
                # self.setText(x, y, name)
                self.setCircle(x, y, 10, name)
                if lst_y > 0 and lst_x > 0:
                    self.setLine(lst_x, lst_y, x, y)
                lst_x = x
                lst_y = y

    def setAlarm(self, alarm_val):
        # 目前暂时从左大到右，站与站之间记录距离，然后和传感器的间距匹配上
        # print(alarm_val)
        # print(type(alarm_val))
        # dtime = alarm_val["sDatetime"]
        level = alarm_val["alarmLevel"]
        infos = alarm_val["alarmInfo"]
        channel = alarm_val["channels"]
        demoid = channel["demodulatorID"]
        demostatus = get_demo(demoid)
        sensorNum = channel["sensorNum"]

        sensor_distance = sensorNum * 5 / 1000.0
        print(demostatus.position)
        ik = 0
        for st in self.stations:
            print(st['name'], demostatus.position)
            if st["name"] == demostatus.position:
                break
            ik += 1
        # start_index = ik
        if ik == len(self.stations):
            print("Not find the station")
            return
        
        start_index = ik
        start_station = self.stations[start_index]
        while ik < len(self.stations):
            tmp_station = self.stations[ik]
            dist = tmp_station["mileage"] - start_station["mileage"]
            if dist >= sensor_distance:
                break
            ik += 1
        end_index = ik + 1
        end_station = self.stations[end_index]

        for alinfo in infos:
            sensors = alinfo["alarmSensor"]
            print(sensors)
            sennum = len(sensors)
            midsensor = sensors[int(sennum/2)]
            sensor_dist = float(midsensor * 5) / 1000.0
            # 遍历的最后一个车站
            lst_station = None
            for sindex in range(start_index, end_index + 1):
                tmpsta = self.stations[sindex]
                tmp_mileage = tmpsta['mileage'] - start_station['mileage']
                print("station mileage %f, sensor_dist %f" % (tmp_mileage, sensor_dist))
                if lst_station and tmp_mileage > sensor_dist:
                    invalert = InvasionAlert(start_station, end_station, level)
                    # 获得传感器相对于最近一个车站的相对位置
                    # 传感器相对于仪表车站的位置 减去 最近一个车站到仪表车站的位置除以后面一战到最近一个车站的距离
                    twostation_mileage = tmpsta['mileage'] - lst_station["mileage"]
                    print(lst_station['mileage'] , start_station['mileage'])
                    print("sensor_dist %f" % sensor_dist)
                    rel_x = (sensor_dist - (lst_station['mileage'] - start_station['mileage']) )/ twostation_mileage
                    print("alert rel x %f" % rel_x)
                    invalert.set_relpostion(lst_station, rel_x, 0.3)
                    self.invalerts.append(invalert)
                lst_station = tmpsta
        # self.drawAlarm()

    def drawAlarm(self):
        # print("drawAlarm")
        self.alerttime += 1
        if self.alerttime % 2 == 0:
            linecolor = QtCore.Qt.red
            pointcolor = QtCore.Qt.red
        else:
            linecolor = QtCore.Qt.black
            pointcolor = QtCore.Qt.black
        if self.mode == "default":
            for alarm in self.invalerts:
                rel_index = self.stations.index(alarm.rel_station)
                next_station = self.stations[rel_index + 1]
                self.setAlarmLine(alarm.rel_station['x'], alarm.rel_station['y'],
                              next_station['x'], next_station['y'], linecolor)
            # 两站之间的线闪动报警
        elif self.mode == "station":
            width = self.rel_endx - self.rel_startx
            for alarm in self.invalerts:
                if alarm.rel_station["name"] != self.twostation_start["name"]:
                    continue
                self.setAlarmCircle(self.rel_startx + alarm.rel_x * width, alarm.rel_y * 100 + self.rel_y, 10, pointcolor)


    def scaleRefresh(self, curScale):
        items = self.items()
        for it in items:
            # if isinstance(it, StationCircleItem):
            # it.setScale(1/curScale)
            if it.showscale > curScale:
                it.hide()
            else:
                it.show()

    def scaleToDefault(self):
        self.mode = "default"
        self.refreshClear()
        lst_x = -100
        lst_y = -100
        for st in self.stations:
            name = st["name"]
            x = st['x']
            y= st['y']
            # self.setText(x, y, name)
            self.setCircle(x, y, 10, name)
            if lst_y > 0 and lst_x > 0:
                self.setLine(lst_x, lst_y, x, y)
            lst_x = x
            lst_y = y

    def refreshClear(self):
        self.clear()
        self.update()
        del self.alertlineItems[:]
        del self.alertpointsItems[:]

    def scaleTwoStation(self, event):
        self.mode = "station"
        print(event.scenePos())
        x = event.scenePos().x()
        self.rel_endx = self.width() - 50
        lstst = None
        width = self.rel_endx - self.rel_startx
        for it in self.stations:
            if lstst is not None:
                if x > lstst['x'] and x < it['x']:
                    # to two station
                    self.refreshClear()
                    # 清理对象，然后相对位置画图
                    self.setCircle(self.rel_startx, self.rel_y, 10, lstst['name'])
                    self.setCircle(self.rel_endx, self.rel_y, 10, it['name'])
                    self.setLine(self.rel_startx, self.rel_y, self.rel_endx, self.rel_y)
                    self.twostation_start = lstst
                    start_marks = lstst["marks"]
                    end_marks = it["marks"]
                    for mk in start_marks:
                        if mk["rel_x"] < 0:
                            continue
                        self.setCircle(self.rel_startx + width * mk["rel_x"], self.rel_y + 100 * mk["rel_y"], 10, mk["name"])
                    break
            lstst = it
        

class MapViewer(QtWidgets.QWidget):

    scaleFactor = 1
    screenwidth = 0

    def __init__(self, parent=None):
        super(MapViewer, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        self.scene = MapScene()
       
        self.view = QtWidgets.QGraphicsView(self.scene)
        layout.addWidget(self.view)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, 1200, 300))
        self.setLayout(layout)

        self.scene.doubleclick.connect(self.sceneDoubleClick)
        # self.scene.setSceneRect(QtCore.QRectF(0, 0, self.scene.width(), 240))

    def clearAlerts(self):
        self.scene.clearAlerts()

    # 双击进入两站之间，显示其他点
    def sceneDoubleClick(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            tmpScale = 1.2
        elif event.button() == QtCore.Qt.RightButton:
            tmpScale = 0.8
        self.scaleFactor = self.scaleFactor * tmpScale
        self.view.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.view.scale(tmpScale, tmpScale)
        # self.scene.scaleRefresh(self.scaleFactor)
        self.scene.scaleTwoStation(event.postion())

    def setScreenWidth(self, width):
        self.screenwidth = width -100
        self.scene.setSceneRect(QtCore.QRectF(0, 0, self.screenwidth, 300))

    def setAlarm(self, alarm):
        self.scene.setAlarm(alarm)


if __name__ == '__main__':
    # client = HDFSFileSystem("192.168.2.21", "root", "wim123")
    # client.refresh()
    # client2 = HDFSFileSystem("192.168.2.21", "root", "wim123")

    # tdir = HDFSDir("/nfs")
    import sys
    from PySide2.QtWidgets import QApplication
    app = QApplication(sys.argv)
 
    # model = TreeModel(tdir.get_dict())
    # global window
    window = MainViewer()
    window.show()
    # Timer(10.0, changevalue).start()

    sys.exit(app.exec_())
      