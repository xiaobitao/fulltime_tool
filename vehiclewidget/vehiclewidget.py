# -*- coding:utf-8 -*-
from functools import partial
import sys
import uuid
import time
import json
from datetime import datetime
from PySide2 import QtCore
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from PySide2.QtCore import QTimer

from vehiclewidget.vehicleslider import VehicleSlider
from vehiclewidget.vehicledriving import VehicleDriving

class VehicleWidget(QWidget):
    """车辆控件."""

    def __init__(self):
        super(VehicleWidget, self).__init__()
        self.lastrefresh = datetime.now()
        main_vlayout = QVBoxLayout()

        slide_layout = QVBoxLayout()
        self.vech_slider = VehicleSlider()
        slide_layout.addWidget(self.vech_slider)

        main_vlayout.addLayout(slide_layout, 0)
        self.vech_driving = VehicleDriving()
        main_vlayout.addWidget(self.vech_driving, 1)
        # main_vlayout.setRowStretch(1,2)

        self.setLayout(main_vlayout)

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.refresh)
        # self.timer.setInterval(1000*10)
        # self.timer.start()

    # def refresh(self):
    #     self.vech_slider.refresh()

    @Slot(str, str) 
    def refresh_kafkamsg(self, key, value):
        # print("init refresh msg")
        # 刷新太快会hung
        if (datetime.now() - self.lastrefresh).seconds < 5:
            # 不刷新界面，数据还是可以存储
            return
        self.lastrefresh = datetime.now()
        tun_dict = json.loads(value)
        # tun_dict = value
        print(key)
        print(tun_dict)
        self.vech_slider.refreshData(tun_dict)
        # self.vech_driving.refreshData(tun_dict)

