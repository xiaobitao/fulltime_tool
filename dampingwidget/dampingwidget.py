# -*- coding:utf-8 -*-
from functools import partial
import sys
import uuid
import time

from PySide2 import QtCore
from PySide2.QtCore import Qt, Slot, Signal, QModelIndex, QMimeData, QTimer
from PySide2.QtWidgets import QWidget, QSplitter, QFileSystemModel,\
        QVBoxLayout, QHBoxLayout, QTreeView, QPushButton, QCalendarWidget, \
        QDateEdit, QLabel, QGroupBox, QCheckBox
from PySide2.QtWidgets import QAbstractItemView, QFormLayout, QComboBox, \
    QTableWidget, QSizePolicy
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QTranslator, QLocale, QLibraryInfo
from PySide2.QtWidgets import QApplication

# cope with package dir issue.
try:
    from damping_bar import *
    from damping_trend import *
except ImportError as e:
    from dampingwidget.damping_bar import *
    from dampingwidget.damping_trend import *


style_sheet = """
    
    QCheckBox:!checked {
        color: grey
    }

    QCheckBox:checked {
        color: green
    }

    QPushButton#delete_report {
        color: red
    }


"""




class DampingReportsWidget(QWidget):
    """(离线)减振评估报告
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        group_box = QGroupBox(self.tr("Damping Evaluation Reports"))
        hbox = QHBoxLayout()
        left = DampingReportTable()
        right = DampingReportOpsBoard()
        hbox.addWidget(left)
        hbox.addWidget(right)
        group_box.setLayout(hbox)
        layout = QVBoxLayout()
        layout.addWidget(group_box)
        self.setLayout(layout)


class DampingReportTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # NOTE(Gang): Use table widget for now. Might seek for TableView instead.
        n_rows = 30
        n_columns = 3
        self.table = QTableWidget(n_rows, n_columns)
        self.table.setHorizontalHeaderLabels([
            self.tr('Report Name'),
            self.tr('Report Path'),
            self.tr('Report Date&Time'),

             ])
        # TODO(Gang): Use item row delegate to populate rows.
        # Might use QTableModel to help on this instead? it seems it is not exported.
        

        # Note(Gang): For growing rows, scrollbar is required.
        # The scroll bars are enabled when required automatically.
        # TODO(Gang): For growing rows, updating the row lenght is required.

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)




class DampingReportOpsBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout()

        self.report_cycle = QComboBox()
        self.report_cycle.addItems([self.tr('Weekly'), self.tr('Monthly')])
        layout.addRow(self.tr('Report Cycle'), self.report_cycle)

        self.auto_report_switch = QCheckBox(self.tr('Auto Report'))
        layout.addRow(self.tr('Auto Report Switch'), self.auto_report_switch)

        # NOTE(Gang): we might need to layout the three buttons further.
        self.btn_refresh = QPushButton(self.tr('Refresh Reports'))
        self.btn_open_report = QPushButton(self.tr('Open the Selected Report'))
        self.btn_delete_report = QPushButton(self.tr('Delete the Selected Report'))
        
        self.btn_delete_report.setObjectName('delete_report')

        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.btn_open_report)
        layout.addWidget(self.btn_delete_report)

        self.setLayout(layout)


        




class DampingWidget(QWidget):
    """减震控件类."""

    def __init__(self):
        super(DampingWidget, self).__init__()

        plot1 = DampingAnalysisBarWidget()
        plot2 = DampingAnalysisTrendWidget()
        layout = QVBoxLayout()
        layout.addWidget(plot1)
        layout.addWidget(plot2)

        self.setLayout(layout)
        self.setStyleSheet(style_sheet)
