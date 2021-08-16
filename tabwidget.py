# -*- coding:utf-8 -*-
from functools import partial
import sys
import uuid
import time

from PySide2 import QtCore
from PySide2.QtCore import QPoint, Qt, QUrl
from PySide2.QtWidgets import (QAction, QMenu, QTabBar, QTabWidget)
from PySide2.QtWebEngineWidgets import (QWebEngineDownloadItem,
    QWebEngineHistory, QWebEnginePage, QWebEngineProfile)

class TabWidget(QTabWidget):
    """Enables having several tabs with QWebEngineView."""

    def __init__(self):
        super(TabWidget, self).__init__()
        self.setTabsClosable(False)
        self._actions_enabled = {}
        self.tab_bar = self.tabBar()

    def add_tab(self, widget, title):
        index = self.count()
        self.addTab(widget, title)

