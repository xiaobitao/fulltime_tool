# -*- coding:utf-8 -*-
from functools import partial
import sys
import uuid
import time

import numpy as np
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSlider, QGroupBox, QLabel, QLineEdit, QDial
from PySide2.QtGui import QBitmap, QPixmap, QPolygon
from PySide2.QtCore import QRect, QPoint, QSize, QTimer

# from util.rest import VechRest
from vehiclewidget.gaugecar import GaugeCar

class DampingSlider(QSlider):
    def __init__(self, orientation=None):
        super(DampingSlider, self).__init__(orientation)

    def paintEvent(self, e):
        super(DampingSlider, self).paintEvent(e)
        painter = QtGui.QPainter(self)
        QRect(QPoint(100, 200), QSize(11, 16))
        rect = self.rect()
        wid = rect.width()
        hei = rect.height()
        pf = QPolygon()
        # 画点的地方通过配置文件读取
        start = int(wid/3)
        leng = start
        for i in range(start, start + leng):
            if i % 3 != 0:
                continue
            for j in range(0, hei):
                if j % 3 != 0:
                    continue
                pf.append(QPoint(i, j))
                
        painter.drawPoints(pf)


class VehicleSlider(QWidget):
    """车辆滑动显示控件."""

    def __init__(self):
        super(VehicleSlider, self).__init__()
        main_vlayout = QVBoxLayout()

        groupBox = QGroupBox(u"列车实时定位")
        vlayout = QVBoxLayout()

        hlayout0 = QHBoxLayout()
        # hlayout_new.addLayout(vlayout)
        self.static_canvas = FigureCanvas(Figure(figsize=(5, 2)))
        hlayout0.addWidget(self.static_canvas, 1)
        self.gaugecar = GaugeCar(self)
        self.gaugecar.setCurrentValue(50)
        self._static_ax = self.static_canvas.figure.subplots()
        # t = np.linspace(0, 10, 501)
        # self._static_ax.plot(t, np.tan(t), ".")
        # self.speeddial.resize(100, 100) 
        hlayout0.addWidget(self.gaugecar)
        vlayout.addLayout(hlayout0)

        self.slider = DampingSlider(QtCore.Qt.Horizontal)
        # self.slider.setMask(QPixmap("./dot3.png"))
        # self.slider.setStyleSheet(css)
        vlayout.addWidget(self.slider)
        slide_hlayout = QHBoxLayout()
        slide_hlayout.addWidget(QLabel(u"野芷湖站"))
        slide_hlayout.addStretch(1)
        slide_hlayout.addWidget(QLabel(u"板桥站"))
        slide_hlayout.addStretch(1)
        slide_hlayout.addWidget(QLabel(u"湖工大站"))

        vlayout.addLayout(slide_hlayout)
        
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(QLabel(u"是否到达减震区间"))
        self.dampline = QLineEdit()
        self.dampline.setText(u"否")
        hlayout2.addWidget(self.dampline)
        hlayout2.addStretch(1)

        hlayout2.addWidget(QLabel(u"即将到站"))
        self.arrstation = QLineEdit()
        self.arrstation.setText(u"板桥站")
        hlayout2.addWidget(self.arrstation)
        hlayout2.addStretch(1)

        hlayout2.addWidget(QLabel(u"实时速度"))
        self.speed = QLineEdit()
        self.speed.setText(u"30km/h")
        hlayout2.addWidget(self.speed)
        hlayout2.addStretch(1)

        vlayout.addLayout(hlayout2)
        # add qdial
      
        groupBox.setLayout(vlayout)
        main_vlayout.addWidget(groupBox)
        main_vlayout.addStretch(1)
        self.setLayout(main_vlayout)

        self._update_vechpos()

    def refreshFreq(self):
        self._static_ax.clear()
        x = list(range(len(self.poinstvirb)))
        self._static_ax.bar(x, self.poinstvirb, width=0.5)
        self._static_ax.figure.canvas.draw()
        

    def refreshData(self, vechdata):
        self.poinstvirb =  vechdata["fs"]
        self.speed = vechdata["subwayV"]
        self.gaugecar.setCurrentValue(self.speed)
        self.bdamp = vechdata["sensors"]["buffered"]
        self.gpos = vechdata["sensors"]["groundPos"]
        self.refreshFreq()
        
        # self._update_vechpos()

    def _update_vechpos(self):
        pass
        # # v = VechRest()
        # data = v.get_vechpos()
        # # car reg should to be set by config
        # # car_reg = data["carRegion"]
        # # car_int = data["carSiteInterval"]
        # # det_time = data["detectedTime"]
        # if data is not None:
        #     car_speed = data["carSpeed"]
        #     self.speed.setText(str(car_speed))

if __name__ == '__main__':
    # client = HDFSFileSystem("192.168.2.21", "root", "wim123")
    # client.refresh()
    # client2 = HDFSFileSystem("192.168.2.21", "root", "wim123")

    # tdir = HDFSDir("/nfs")
    # print(tdir.get_childs())
    from PySide2.QtWidgets import QApplication
    app = QApplication(sys.argv)
 
    # model = TreeModel(tdir.get_dict())
    window = SpeedDial()
    window.show()
    sys.exit(app.exec_())
        
