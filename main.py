# -*- coding:utf-8 -*-
import sys
import os
import PySide2
from PySide2 import QtCore
from PySide2.QtCore import Qt, QUrl, QDir
from PySide2.QtCore import QTranslator, QLocale, QLibraryInfo
from PySide2.QtGui import QCloseEvent, QKeySequence, QIcon
from PySide2.QtWidgets import (QAction, QApplication, QDesktopWidget,
    QDockWidget, QLabel, QLineEdit, QMainWindow, QMenu, QMenuBar, QPushButton,
    QStatusBar, QToolBar, QWidget)
# from PySide2.QtCore import pyqtSlot

from tabwidget import TabWidget
from initwidget.initwidget import InitWidget
from datawidget.datawidget import *
from dataviewwidget.dataviewwidget import DataViewWidget
# from dampingwidget.dampingwidget import *
from invasionwidget.invasionwidget import InvasionWidget
from vehiclewidget.vehiclewidget import VehicleWidget
# from walkwidget.walkwidget import WalkWidget

from util.wimlog import error,info, debug
from util.database import init_db
from util.kafka import KafkaClient


def exception_hook(exctype, value, traceback):
    # sys._excepthook(exctype, value, traceback)
    error(exctype)
    error(value)
    error(traceback)
    sys.exit(1)

sys._excepthook = exception_hook

def create_main_window():
    """Creates a MainWindow using 75% of the available screen resolution."""
    main_win = MainWindow()
    # main_windows.append(main_win)
    # available_geometry = app.desktop().availableGeometry(main_win)
    # main_win.resize(available_geometry.width(), available_geometry.height())
    main_win.showMaximized()
    return main_win

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle(u'全时全域大数据后端管理系统')

        self._tab_widget = TabWidget()

        # Replace widget
        # self.initwid = InitWidget()
        # 获取hadoop文件目录目前比较费时
        # self.datawid = DataWidget()
        self.datawid = DataViewWidget()
        self.vechwid = VehicleWidget()
        # self.dampwid = DampingWidget()
        self.invaswid = InvasionWidget()
        # self.walkwid = WalkWidget()
        # self._tab_widget.add_tab(self.initwid, u"初始化和评估")
        self._tab_widget.add_tab(self.datawid, u"原始数据管理")
        self._tab_widget.add_tab(self.vechwid, u"车辆数据信息")
        # self._tab_widget.add_tab(self.dampwid, u"减震区报表分析")
        self._tab_widget.add_tab(self.invaswid, u"外部入侵检测")
        # self._tab_widget.add_tab(self.walkwid, u"内部人员走动监测")
        # mainLayout.addWidget(buttonBox)
        self.setCentralWidget(self._tab_widget)

        # self.kafkacli = KafkaClient()
        # self.kafkacli.initmsg.connect(self.initwid.refresh_kafkamsg)
        # self.kafkacli.vechdrive.connect(self.vechwid.refresh_kafkamsg)
        # self.kafkacli.invasion.connect(self.invaswid.refresh_kafkamsg)
        # connect kafka signal to widget slot
        # self.kafkacli.start()

    def stop(self):
        self.kafkacli.stop()

    def setScreenWidth(self, width):
        self.invaswid.setScreenWidth(width)



if __name__ == '__main__':
    init_db()
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.dirname(PySide2.__file__) + '/plugins/platforms'
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    trans = QTranslator()
    # trans.load(QLocale.system(), "app.qm")
    ok = trans.load("qt_zh_CN", "./")
    
    # print(ok)
    # trans.load("qt_zh_CN", ".")
    app.installTranslator(trans)
    main_win = create_main_window()
    main_win.setScreenWidth(screen.size().width())
    info("start")
    exit_code = app.exec_()
    sys.exit(exit_code)
