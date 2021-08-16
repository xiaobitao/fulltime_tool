# -*- coding:utf-8 -*-
from functools import partial
import sys
import uuid
import time
import json

from PySide2 import QtCore, QtGui
from PySide2.QtCore import  QModelIndex, Qt
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLineEdit, QGridLayout, QDialog,
                               QTreeView, QPushButton, QLabel, QGroupBox, QTableView, QItemDelegate, QMessageBox)

from vehiclewidget.vehicleslider import DampingSlider
from invasionwidget.alerttablemodel import AlertTableModel

from util.util import get_config
from util.database import add_alarm, get_invasion_alarms, get_demo, update_alarm
from invasionwidget.mapview import MapViewer


class MyButtonDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(MyButtonDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            button_read = QPushButton(
                self.tr(u'处理'),
                self.parent(),
                clicked=self.parent().cellButtonClicked
            )
            button_read.index = [index.row(), index.column()]
            h_box_layout = QHBoxLayout()
            h_box_layout.addWidget(button_read)
            h_box_layout.setContentsMargins(0, 0, 0, 0)
            h_box_layout.setAlignment(Qt.AlignCenter)
            widget = QWidget()
            widget.setLayout(h_box_layout)
            self.parent().setIndexWidget(
                index,
                widget
            )

class ResolveDialog(QDialog):

    def __init__(self, parent=None):
        super(ResolveDialog, self).__init__(parent)
        vbox = QVBoxLayout()

        reslabel = QLabel("处理备注")
        peoplelable = QLabel("处理人")
        self.resln = QLineEdit()
        self.peopleLn = QLineEdit()
        self.okbut = QPushButton(u"确定")
        self.cancelbut = QPushButton(u"取消")
        hboxlayout = QHBoxLayout()
        hboxlayout.addWidget(self.okbut)
        hboxlayout.addWidget(self.cancelbut)
        vbox.addWidget(reslabel)
        vbox.addWidget(self.resln)
        vbox.addWidget(peoplelable)
        vbox.addWidget(self.peopleLn)
        vbox.addLayout(hboxlayout)
        self.setLayout(vbox)

        self.okbut.clicked.connect(self.butOk)
        self.cancelbut.clicked.connect(self.butCancel)

    def butOk(self):
        self.res_text = self.resln.text()
        self.people_text = self.peopleLn.text()
        if len(self.res_text.strip()) == 0 or len(self.people_text.strip()) == 0:
            QMessageBox.warning("请填写处理内容及处理人")
            return
        self.accept()

    def butCancel(self):
        self.close()

class MyTableView(QTableView):

    updateData = QtCore.Signal()
    def __init__(self, parent=None):
        super(MyTableView, self).__init__(parent)
        self.setItemDelegateForColumn(8, MyButtonDelegate(self))

    def cellButtonClicked(self):
        # print("Cell Button Clicked", self.sender().index)
        index = self.sender().index
        print(index)
        wid = ResolveDialog(self)
        res = wid.exec_()
        if res == QDialog.Accepted:
            print("accept")
            mod = self.model()
            alert_id = mod.getAlertID(index[0])
            update_alarm(alert_id, wid.res_text, wid.people_text)
            self.updateData.emit()
            # print(alert_id)


class InvasionWidget(QWidget):
    """原始数据控制类."""

    def __init__(self):
        super(InvasionWidget, self).__init__()
        self.config = get_config()

        vboxlayout = QVBoxLayout()
        vboxlayout.addWidget(self._init_invasionbox())
        vboxlayout.addWidget(self._init_alertbox())
        self.setLayout(vboxlayout)

        self.refreshTableFromDB()

    def setScreenWidth(self, width):
        self.mapview.setScreenWidth(width)

    def _init_invasionbox(self):
        box = QGroupBox(u"外部入侵实时位置报警信息")
        vboxlayout = QVBoxLayout()
        # self.vechslider = DampingSlider(QtCore.Qt.Horizontal)
        self.mapview = MapViewer()
        vboxlayout.addWidget(self.mapview)
        self.alert_lables = []
        hlablayout = QHBoxLayout()
        rpixmap = QtGui.QPixmap("./alertr.ico")
        ypixmap = QtGui.QPixmap("./alerty.ico")
        gpixmap = QtGui.QPixmap("./alertg.ico")
        near_points = self.config["invasion"]["near_points"].split(",")
        far_points = self.config["invasion"]["far_points"].split(",")
        for name in near_points:
            qlab = QLabel()
            if len(name) % 2 == 0:
                qlab.setPixmap(rpixmap)
            elif len(name) % 3 == 0:
                qlab.setPixmap(gpixmap)
            else:
                qlab.setPixmap(ypixmap)
            hlablayout.addWidget(qlab)
            self.alert_lables.append(qlab)

        hplace1layout = QHBoxLayout()
        for xlab in near_points:
                            
            qlab = QLabel()
            # if i % 3 == 0:
            qlab.setText(xlab)
            qlab.setFont(QtGui.QFont("Times", 8))
            hplace1layout.addWidget(qlab)
            self.alert_lables.append(qlab)
        hplace2layout = QHBoxLayout()
        for xlab in far_points:
                            
            qlab = QLabel()
            qlab.setText(xlab)
            qlab.setFont(QtGui.QFont("Times", 12))
            hplace2layout.addWidget(qlab)
            self.alert_lables.append(qlab)
        
        glayout = QGridLayout()
        glayout.addWidget(QLabel(u"正常"), 0, 0)
        glabel = QLabel()
        glabel.setPixmap(gpixmap)
        glayout.addWidget(glabel, 0, 1)
        glayout.addWidget(QLabel(u"当前正常区域个数:"), 0, 2)
        self.normal_ln = QLabel(u"10")
        glayout.addWidget(self.normal_ln, 0, 3)
        glayout.addWidget(QLabel(u"个"), 0, 4)

        glayout.addWidget(QLabel(u"一级预警"), 1, 0)
        ylabel = QLabel()
        ylabel.setPixmap(ypixmap)
        glayout.addWidget(ylabel, 1, 1)
        glayout.addWidget(QLabel(u"当前预警区域个数:"), 1, 2)
        self.yellow_ln = QLabel(u"10")
        glayout.addWidget(self.yellow_ln, 1, 3)
        glayout.addWidget(QLabel(u"个"), 1, 4)
        glayout.addWidget(QLabel(u"已预警时长:"), 1, 5)
        self.yeltime_ln = QLabel(u"1h20m22s")
        glayout.addWidget(self.yeltime_ln, 1, 6)

        glayout.addWidget(QLabel(u"二级预警"), 2, 0)
        rlabel = QLabel()
        rlabel.setPixmap(rpixmap)
        glayout.addWidget(rlabel, 2, 1)
        glayout.addWidget(QLabel(u"当前预警区域个数:"), 2, 2)
        self.red_ln = QLabel(u"10")
        glayout.addWidget(self.red_ln, 2, 3)
        glayout.addWidget(QLabel(u"个"), 2, 4)
        glayout.addWidget(QLabel(u"已预警时长:"), 2, 5)
        self.redtime_ln = QLabel(u"1h20m22s")
        glayout.addWidget(self.redtime_ln, 2 ,6)
        self.resolve_but = QPushButton(u"已处理")
        glayout.addWidget(self.resolve_but, 2, 7)
        
        glayout.setColumnStretch(6, 1)
        glayout.setColumnStretch(4, 1)
        glayout.setColumnStretch(1, 1)
      
        vboxlayout.addLayout(glayout)
        vboxlayout.addStretch(1)
       

        box.setLayout(vboxlayout)
        return box

    def _init_alertbox(self):
        box = QGroupBox(u"外部入侵报警记录")
        hboxlayout = QHBoxLayout()

        self.tableModel = AlertTableModel()
        self.tableView = MyTableView()
        # self.tableView.setItemDelegateForColumn(8, MyButtonDelegate(self.tableView))
        self.tableView.setModel(self.tableModel)
        self.tableView.updateData.connect(self.refreshTableFromDB)
        hboxlayout.addWidget(self.tableView)

        # vlayout = QVBoxLayout()
        # self.note_but = QPushButton(u"添加备注")
        # vlayout.addWidget(self.note_but)
        # self.modi_but = QPushButton(u"修正记录")
        # vlayout.addWidget(self.modi_but)
        # self.del_but = QPushButton(u"删除记录")
        # vlayout.addWidget(self.del_but)
        # self.clear_but = QPushButton(u"清空记录")
        # vlayout.addWidget(self.clear_but)
        # self.export_but = QPushButton(u"导出报表")
        # vlayout.addWidget(self.export_but)

        # hboxlayout.addLayout(vlayout)
        box.setLayout(hboxlayout)
        return box

    def addEntry(self, alert_dict=None):
        """ Add an entry to the addressbook. """
        # if name is None and address is None:
        #     addDialog = AddDialogWidget()

        #     if addDialog.exec_():
        #         name = addDialog.name
        #         address = addDialog.address

        # alert = {"zone": data_dict["zone"], "address": address, "time": time}
        alerts = self.tableModel.alerts[:]
        # check if exist
       
            # Step 1: create the  row
        self.tableModel.insertRows(0)

        # Step 2: get the index of the newly created row and use it.
        # to set the name
        ix = self.tableModel.index(0, 0, QModelIndex())
        self.tableModel.setData(ix, alert_dict["create_time"], Qt.EditRole)

        # Step 3: lather, rinse, repeat for the address.
        ix = self.tableModel.index(0, 1, QModelIndex())
        self.tableModel.setData(ix, alert_dict["alert_type"], Qt.EditRole)

        ix = self.tableModel.index(0, 2, QModelIndex())
        self.tableModel.setData(ix, alert_dict["position"], Qt.EditRole)

        ix = self.tableModel.index(0, 3, QModelIndex())
        self.tableModel.setData(ix, alert_dict["alert_level"], Qt.EditRole)

        ix = self.tableModel.index(0, 4, QModelIndex())
        self.tableModel.setData(ix, alert_dict["status"], Qt.EditRole)

        ix = self.tableModel.index(0, 5, QModelIndex())
        self.tableModel.setData(ix, alert_dict["reslove_people"], Qt.EditRole)

        ix = self.tableModel.index(0, 6, QModelIndex())
        self.tableModel.setData(ix, alert_dict["reslove_time"], Qt.EditRole)

        ix = self.tableModel.index(0, 7, QModelIndex())
        self.tableModel.setData(ix, alert_dict["note"], Qt.EditRole)

        ix = self.tableModel.index(0, 8, QModelIndex())
        self.tableModel.setData(ix, alert_dict["alert_id"], Qt.EditRole)

    def refresh_kafkamsg(self, key, value):
        print(value)
        alarm_val = json.loads(value)
        # 所有alarm从数据库读取
        # self.mapview.setAlarm(alarm_val)
        self.addAlarm(alarm_val)

    def addAlarm(self, alarmval):
        alarmlevel = alarmval["alarmLevel"]
        tmptype = alarmval["alarmType"]
        alarmtype = 0
        print(tmptype)
        if tmptype == u"外部入侵":
            alarmtype = 1
        elif tmptype == u"内部入侵":
            alarmtype = 2
        alarminfo = json.dumps(alarmval["alarmInfo"])
        demoid = alarmval["channels"]["demodulatorID"]
        channelnum = alarmval["channels"]["channelNo"]
        add_alarm(alarmlevel, alarmtype, demoid, channelnum, alarminfo, None)
        self.refreshTableFromDB()

    def refreshTableFromDB(self):
        self.tableModel.clear()
        self.mapview.clearAlerts()
        alarms = get_invasion_alarms()
        for alm in alarms:
            entry = {}
            demoid = alm.demoid
            entry["alert_id"] = alm.id
            entry["alert_level"] = alm.level
            entry["create_time"] = str(alm.create_time)
            entry["alert_type"] = alm.alarmtype
            # 获取位置
            demo = get_demo(demoid)
            entry["position"] = demo.position
            entry["note"] = alm.note
            entry["reslove_time"] = alm.resolve_time
            entry["reslove_people"] = alm.resolve_people
            entry["status"] = alm.status
            self.addEntry(entry)
            # 更新mapview的alarm

            if alm.status == 0:
                alarm_val = {}
                alarm_val["alarmLevel"] =alm.level
                alarm_val["alarmInfo"] = json.loads(alm.alarminfo)
                # alarm_val["channels"]
                channel = {}
                channel["demodulatorID"] = alm.demoid
                channel["sensorNum"] = alm.channelnum
                alarm_val["channels"] = channel
                self.mapview.setAlarm(alarm_val)



