# -*- coding:utf-8 -*-
from functools import partial
import sys
import os
import uuid
import time
import numpy as np

from PySide2 import QtCore
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QLineEdit, QMessageBox, QProgressDialog,
                               QTreeView, QPushButton, QLabel, QGroupBox, QFileSystemModel, QFileDialog)

from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from vehiclewidget.vehicleslider import VehicleSlider
from initwidget.switchbutton import SwitchButton
from vehiclewidget.shdfstree import SingleHDFSTreeWidget
from util.wimhdfs import HDFSDir, HDFSFile

from util.rest import PointsData
# from util.util import read_binfile, get_current_directory
from util.util import DownloadThread, readpoints_whufile

class VehicleDriving(QWidget):
    """行车分析控件."""

    def __init__(self):
        super(VehicleDriving, self).__init__()

        left_vlayout = QVBoxLayout()

        h_layout = QHBoxLayout()
        # slide_layout.addWidget(VehicleSlider())

        # matplotlib 显示
        static_canvas = FigureCanvas(Figure(figsize=(3, 2)))
        h_layout.addWidget(static_canvas, 1)

        dynamic_canvas = FigureCanvas(Figure(figsize=(3, 2)))
        h_layout.addWidget(dynamic_canvas, 1)

        self._spect_ax = static_canvas.figure.subplots()
        # t = np.linspace(0, 10, 501)
        # self._static_ax.plot(t, np.tan(t), ".")

        self._freqdom_ax = dynamic_canvas.figure.subplots()
        self._timer = dynamic_canvas.new_timer(
            100, [(self._update_canvas, (), {})])
        # self._timer.start()

        # 瀑布图需要资源过多，暂时不显示
        # # end matplotlib 显示
        # # 下面的控件显示
        # h_layout2 = QHBoxLayout()
        # static_canvas_vech = FigureCanvas(Figure(figsize=(3, 2)))
        # h_layout2.addWidget(static_canvas_vech, 1)
        # self._vech_ax = static_canvas_vech.figure.subplots()
        # # t2 = np.linspace(0, 10, 501)
        # # self._vech_ax.plot(t2, np.tan(t), ".")
        # 控件layout
        but_layout = QHBoxLayout()
        layout1 = QHBoxLayout()
        layout1.addWidget(QLabel(u"显示点"))
        # self.zone_cmb = QComboBox()
        # self.zone_cmb.addItem("1")
        # self.zone_cmb.addItem("2")
        # self.zone_cmb.addItem("3")
        self.pointlne = QLineEdit()
        layout1.addWidget(self.pointlne)
        but_layout.addLayout(layout1)

        self.timedomain_but = QPushButton(u"生成频域频谱图")
        but_layout.addWidget(self.timedomain_but)
        self.timedomain_but.clicked.connect(self.spectrogramSlot)
        # but_layout.addLayout(layout1)
        self.freqdomain_but = QPushButton(u"生成时域波形图")
        self.freqdomain_but.clicked.connect(self.freqdomSlot)
        but_layout.addWidget(self.freqdomain_but)
        

        layout2 = QHBoxLayout()
        layout2.addWidget(QLabel(u"区间选择"))
        self.station_cmb = QComboBox()
        self.station_cmb.addItem(u"湖-板")
        self.station_cmb.addItem(u"板-野")
        # self.station_cmb.addItem("3")
        # layout2.addWidget(self.station_cmb)
        # but_layout.addLayout(layout2)
        # h_layout2.addLayout(but_layout)
        self.waterfall_but = QPushButton(u"生成行车瀑布图")
        # but_layout.addWidget(self.waterfall_but)
        but_layout.addStretch(1)

        # h_layout2.addLayout(but_layout, 0)
        left_vlayout.addLayout(h_layout, 1)
        left_vlayout.addLayout(but_layout)
        # left_vlayout.addLayout(h_layout2)
        groupBox = QGroupBox(u"行车数据分析")
        groupBox.setLayout(left_vlayout)
        main_vlayout = QHBoxLayout()
        main_vlayout.addWidget(groupBox)
        main_vlayout.addWidget(self._init_vechman())
        self.setLayout(main_vlayout)


    def _update_canvas(self):
        self._dynamic_ax.clear()
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._dynamic_ax.plot(t, np.sin(t + time.time()))
        self._dynamic_ax.figure.canvas.draw()

    def refreshData(self, data):
        pass

    def _init_vechman(self):
        groupBox = QGroupBox(u"行车数据分析")
        # self.tree = QTreeView()
        # self.model = QFileSystemModel()
        # self.model.setRootPath('c://')
        # self.tree.setModel(self.model)
        rootdir = HDFSDir("./")
        self.tree = SingleHDFSTreeWidget(rootdir)
        vlayout =QVBoxLayout()
        vlayout.addWidget(self.tree)

        hlayout1 = QHBoxLayout()
        hlayout1.addWidget(QLabel(u"导出到："))
        self.outdir_ln = QLineEdit()
        self.outdir_ln.setReadOnly(True)
        hlayout1.addWidget(self.outdir_ln)
        self.outchoose_but = QPushButton(u"...")
        self.outchoose_but.clicked.connect(self.outchooseSlot)
        hlayout1.addWidget(self.outchoose_but)
        self.export_but = QPushButton(u"导出")
        self.export_but.clicked.connect(self.outputData)
        hlayout1.addWidget(self.export_but)
        
        # vlayout.addLayout(hlayout1)

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(QLabel(u"删除数据"))
        self.del_ln = QLineEdit()
        # self.del_ln.setText("c://aaa.txt")
        hlayout2.addWidget(self.del_ln)
        self.del_but = QPushButton(u"删除")
        hlayout2.addWidget(self.del_but)

        # vlayout.addLayout(hlayout2)

        hlayout3 = QHBoxLayout()
        hlayout3.addWidget(QLabel(u"保存当前缓冲区行车数据"))
        hlayout3.addStretch(1)
        self.save_but = QPushButton(u"保存")
        hlayout3.addWidget(self.save_but)

        # vlayout.addLayout(hlayout3)
        
        hlayout4 = QHBoxLayout()
        hlayout4.addWidget(QLabel(u"是否自动保存数据"))
        hlayout4.addStretch(1)
        self.switch_but = SwitchButton()
        hlayout4.addWidget(self.switch_but)
        # vlayout.addLayout(hlayout4)

        groupBox.setLayout(vlayout)
        return groupBox

    def outchooseSlot(self):
        outputdir = QFileDialog.getExistingDirectory()
        self.outdir_ln.setText(outputdir)

    def outputData(self):
        outputdir = self.outdir_ln.text()
        if len(outputdir) == 0:
            QMessageBox.warning(self, u"警告", u"没有设定导出目录").exec()
            return
        srcPath = self.tree.getSelectItemPath()
        if len(srcPath) == 0:
            QMessageBox.warning(self, u"警告", u"没有选择源文件").exec()
            return
        hfile = HDFSFile(srcPath)
        if  hfile.download(outputdir) is not None:
            QMessageBox.information(self, u"警告", u"下载成功").exec()
        else:
            QMessageBox.warning(self, u"警告", u"下载失败").exec()

    def generatorPicture(self, pictype):
        srcPath = self.tree.getSelectItemPath()
        print(srcPath)
        if len(self.pointlne.text()) == 0:
            pointnum = 100
        else:
            pointnum = int(self.pointlne.text())
        # pd = PointsData()
        folder = 'tmp'
        filename = srcPath.split("/")[-1]
        dstPath = "./%s/%s" % (folder, filename)
        if not os.path.exists(dstPath):
            self.downloadthread = DownloadThread()
            self.downloadthread.folder = folder
            self.downloadthread.fullpaths = [srcPath]
            self.downloadthread.start()
            
            progressDialog = QProgressDialog(
                "加载", "取消", 0, 0, parent=self)
            self.downloadthread.showdlg = progressDialog
            progressDialog.setWindowTitle("加载")
            progressDialog.setMinimumDuration(0)
            progressDialog.setMinimum(0)
            progressDialog.setMaximum(100)
            progressDialog.setRange(0, 0)

            progressDialog.setFixedSize(progressDialog.width(),
                                        progressDialog.height())
            progressDialog.show()
        print("pd get points data")
        points = readpoints_whufile(dstPath)
        
        sepc_points = points[ :, pointnum]
        print(sepc_points)
        # js_points = pd.get_points(srcPath, [pointnum])
        # print(len(js_points))
        # if len(js_points) == 0:
        #     QMessageBox.warning(self, u"警告", u"获取数据失败")
        # else:
     
        if pictype == "spec":
            self.drawSpectrogram(sepc_points)
        elif pictype == "freq":
            self.drawFreqdom(sepc_points)

    def drawSpectrogram(self, points):
        print("drawSpectrogram")
        self._spect_ax.clear()
        # x = list(range(len(self.points)))
        # self._spec_ax.bar(x, self.poinstvirb, width=0.5)
        self._spect_ax.specgram(points, Fs=1000)
        self._spect_ax.figure.canvas.draw()

    def drawFreqdom(self, points):
        self._freqdom_ax.clear()
        # x = list(range(len(self.points)))
        self._freqdom_ax.plot(points)
        # self._freqdom_ax.specgram(points, Fs=1000)
        self._freqdom_ax.figure.canvas.draw()

    def spectrogramSlot(self):
        # QtCore.QTimer.singleShot(1, lambda : self.generatorPicture("spec"))
        self.generatorPicture("spec")

    def freqdomSlot(self):
        # QtCore.QTimer.singleShot(1, lambda : self.generatorPicture("freq"))
        self.generatorPicture("freq")
        
   
