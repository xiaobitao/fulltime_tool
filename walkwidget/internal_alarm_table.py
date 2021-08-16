"""Provides a table to display the internal alarm events.
"""

from PySide2 import QtCore
from PySide2.QtCore import Qt, Slot, Signal, QModelIndex, QMimeData, QTimer
from PySide2.QtWidgets import QWidget, QSplitter, QFileSystemModel,\
        QVBoxLayout, QHBoxLayout, QTreeView, QPushButton, QCalendarWidget, \
        QDateEdit, QLabel, QGroupBox, QCheckBox
from PySide2.QtWidgets import QAbstractItemView, QFormLayout, QComboBox, \
    QTableWidget, QSizePolicy
from PySide2 import QtWidgets

from datetime import datetime

from . import internal_alarm_data

def format_cell(value):
    if value is None:
        text = ""
    else:
        if isinstance(value, datetime):
            dt_format = '%Y-%m-%d %H:%M:%S'
            text = value.strftime(dt_format)
        else:
            text = str(value)

    return QtWidgets.QTableWidgetItem(text)


class InternalAlarmTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table = QTableWidget(20,5)

        # construct the table.
        self.init_table()
        # TODO(Gang): a set of actions to filter, paging with the table.

        layout = QVBoxLayout()
        layout.addWidget(self.table)

        self.setLayout(layout)
    
    def init_table(self):
        header_labels = [
            "序号", "位置", "发现时间", "处理时间", "备注"
        ]
        self.table.setHorizontalHeaderLabels(header_labels)
        

        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # load by default.
        self.load_data()
        # self.table.sortByColumn(2) # sort by start Date time.
        self.table.setSortingEnabled(True)
        self.table.sortItems(2, Qt.SortOrder.AscendingOrder)

        print("internal alarm table init done.")

    def load_data(self):
        # TODO(Gang): fill in params 
        rows = internal_alarm_data.list_internal_alarms(1,1)

        row_index = 0
        for r in rows:
            # "序号", "位置", "发现时间", "处理时间", "备注"
                # Column 0
                self.table.setItem(row_index, 0,
                    format_cell(r.id))
                self.table.setItem(row_index, 1,
                    format_cell(r.metroMileage))
                self.table.setItem(row_index, 2,
                    format_cell(r.sDatetime))
                self.table.setItem(row_index, 3,
                    format_cell(r.eDatetime))
                self.table.setItem(row_index, 4,
                    format_cell(r.notes))
                
                row_index+=1

        
