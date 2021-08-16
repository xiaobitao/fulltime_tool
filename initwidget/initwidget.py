# -*- coding:utf-8 -*-
from functools import partial
import sys
import uuid
import time
import json
import datetime

from PySide2 import QtCore
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel,
                               QComboBox, QLineEdit, QGridLayout)

from initwidget.switchbutton import SwitchButton
# from initwidget.meterreport import MeterReport
from initwidget.meterstatus import MeterStatus

# from util.rest import InitReport
from util.util import get_config
from util.database import get_demos, get_channels, add_demo, add_channel

class InitWidget(QWidget):
    """
    初始化控件
    仪表的相关参数，需要通过配置文件配置
    """

    def __init__(self):
        super(InitWidget, self).__init__()
        self.config = get_config()
        # 

        vsub_box1 = QVBoxLayout()
        # vsub_box1.addWidget(groupBox)
        h4_box = QHBoxLayout()
        lab4 = QLabel(u"数据初始化")
        self.sbut = SwitchButton()
        h4_box.addWidget(lab4)
        h4_box.addWidget(self.sbut)
        vsub_box1.addLayout(h4_box)
      

        init_hbox = QVBoxLayout()
        init_hbox.addLayout(vsub_box1)
        self.tunnel_gb = QGridLayout()
        self.gridlayouts = []
        for i in range(1, 5):
            box = self.create_tunnel_groupbox(None)
            self.gridlayouts.append(box)
            self.tunnel_gb.addLayout(box, int((i-1) / 2), (i-1) % 2 )

        main_vbox = QVBoxLayout()
        main_vbox.addLayout(init_hbox)
        self.meterwid = MeterStatus()
        demos = get_demos()
        for dm in demos:
            self.meterwid.addEntry(dm.id, dm.position, dm.onlinetime, count=4, freq=dm.freq)
        main_vbox.addWidget(self.meterwid)
        main_vbox.addLayout(self.tunnel_gb)
        # main_vbox.addWidget(MeterReport())
        self.setLayout(main_vbox)

        
        self.meterwid.tableView.selectionModel().selectionChanged.connect(self.on_selectionChanged)
        
        index = self.meterwid.tableModel.index(0, 0)
        self.meterwid.tableView.setCurrentIndex(index)

    @Slot('QItemSelection', 'QItemSelection')
    def on_selectionChanged(self, selected, deselected):
        print("selected: ")

        for ix in selected.indexes():
            if ix.column() == 0:
                demo_id = int(ix.data())
                channels = get_channels(demo_id)
                i = 1 
                for ch in channels:
                    chdict = {}
                    chdict["channelPos"] = ch.position
                    chdict["dataFlow"] = ch.dataflow
                    chdict["frameSize"] = ch.framesize
                    chdict["sensorNum"] = ch.sensornum
                    chdict["channelNo"] = ch.number
                    chdict["demodulatorID"] = ch.demoid
                    chdict["packetSize"] = ch.packetsize
                    self.set_tunnel_groupbox(chdict, self.gridlayouts[i-1])
                    i += 1



    @Slot(str, str) 
    def refresh_kafkamsg(self, key, value):
        # print("init refresh msg")
        tun_dict = json.loads(value)
        demo = tun_dict["demodulator"]
        add_demo(demo["demodulatorID"], demo["demodulatorPos"], demo["channelNum"],
                 demo["sampleFreq"], demo["onlineTime"], demo["status"])
        for i in range(1, 5):
            key = "channel%d" % i
            channel = tun_dict[key]
            add_channel(channel["channelNo"], channel["demodulatorID"], channel["channelPos"], channel["sensorNum"],
                        channel["dataFlow"], channel["frameSize"], channel["packetSize"], datetime.datetime.now())
            self.set_tunnel_groupbox(channel, self.gridlayouts[i-1])

        # save to db


    def set_tunnel_groupbox(self, chnvalue, chngrid):
        # 
        qnumber_line = chngrid.itemAtPosition(0, 1).widget()
        text = u"%s号通道" % str(chnvalue["channelNo"])
        qnumber_line.setText(text)
        
        # 通道位置 
        chngrid.itemAtPosition(1, 1).widget().setText(str(chnvalue["channelPos"]))
        # 数据流量
        chngrid.itemAtPosition(1, 3).widget().setText(str(chnvalue["dataFlow"]) + "MB/s")
        # 数据帧
        chngrid.itemAtPosition(2, 1).widget().setText(str(chnvalue["frameSize"])+ u"帧")
        # 测区数量
        chngrid.itemAtPosition(2, 3).widget().setText(str(chnvalue["sensorNum"]))
        # 数据包
        chngrid.itemAtPosition(3, 1).widget().setText(
            str(chnvalue["packetSize"]) + "*" + str(chnvalue["sensorNum"]))
        # #数据类型
        # chngrid.itemAtPosition(3, 3).widget().setText(str(chnvalue[""]))
        
 
    def create_tunnel_groupbox(self, tunneldata):
        if tunneldata == None:
            tunnelnum = -1
            tunnelpos = " "
            dataflow = " "
            sensornum = " "
            frame = " "
            # packetnum = " "
        else:
            tunnelnum = tunneldata.number
            tunnelpos = tunneldata.position
            sensornum = tunneldata.sensornum
            frame = tunneldata.frame


        # refresh data from data
        group_lay = QGridLayout()
        lab = QLabel(u"通道编号")
        qlin = QLineEdit(u"%s号通道" % tunnelnum)
        group_lay.addWidget(lab, 0, 0)
        group_lay.addWidget(qlin, 0, 1)

      
        
        lab = QLabel(u"通道位置")
        qlin = QLineEdit(tunnelpos)
        lab2 = QLabel(u"数据流量")
        qlin2 = QLineEdit(dataflow)
        group_lay.addWidget(lab, 1, 0)
        group_lay.addWidget(qlin, 1, 1)
        group_lay.addWidget(lab2, 1, 2)
        group_lay.addWidget(qlin2, 1, 3)

        lab = QLabel(u"数据帧")
        qlin = QLineEdit(frame)
        lab2 = QLabel(u"测区数量")
        qlin2 = QLineEdit(sensornum)
        group_lay.addWidget(lab, 2, 0)
        group_lay.addWidget(qlin, 2, 1)
        group_lay.addWidget(lab2, 2, 2)
        group_lay.addWidget(qlin2, 2, 3)

        lab = QLabel(u"数据包")
        qlin = QLineEdit(u"200*527")
        lab2 = QLabel(u"数据类型")
        qlin2 = QLineEdit(u"float")
        group_lay.addWidget(lab, 3, 0)
        group_lay.addWidget(qlin, 3, 1)
        group_lay.addWidget(lab2, 3, 2)
        group_lay.addWidget(qlin2, 3, 3)

        return group_lay


