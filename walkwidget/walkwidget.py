# -*- coding:utf-8 -*-
from functools import partial
import sys
import uuid
import time

from PySide2 import QtCore
from PySide2.QtWidgets import QWidget
from PySide2 import QtWidgets

try:
    from internal_alarm_table import InternalAlarmTable
    print("loaded relatively")
except ImportError as e:
    from walkwidget.internal_alarm_table import InternalAlarmTable
    print("loaded absolutely")


"""
The basic: A Table of alarm events.
The Improved: a visual mark on the line/rectangle, + with mouse over hint/popup.

"""

class WalkWidget(QWidget):
    """内部人员监控控件."""

    def __init__(self):
        super(WalkWidget, self).__init__()
        table = InternalAlarmTable()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(table)
        self.setLayout(layout)




