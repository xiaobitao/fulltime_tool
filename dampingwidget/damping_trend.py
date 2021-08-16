""" 减振趋势图

某个传感器，测得的减振效果随日期的变化趋势曲线

可以指定日期范围、传感器位置（通道位置 + 传感器位置）

"""

from functools import partial
import sys
import uuid
import time
import numpy as np
from datetime import datetime, date

from PySide2 import QtCore
from PySide2.QtCore import Qt, Slot, Signal, QModelIndex, QMimeData, QTimer
from PySide2.QtWidgets import QWidget, QSplitter, QFileSystemModel,\
        QVBoxLayout, QHBoxLayout, QTreeView, QPushButton, QCalendarWidget, \
        QDateEdit, QLabel, QGroupBox, QCheckBox, QLineEdit
from PySide2.QtWidgets import QAbstractItemView, QFormLayout, QComboBox, \
    QTableWidget, QSizePolicy
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QTranslator, QLocale, QLibraryInfo
from PySide2.QtWidgets import QApplication

from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib.pyplot as plt

from . import damping_data

class DampingAnalysisTrendWidget(QWidget):
    """减振趋势分析
    
    界面要点
    --------
    VBox Layout:
        Row 1: Input Area
        Row 2: 
        HBox Layout:
            Left: Trend Plot with lines. May go with matplotlib or qt plot.
            Right: Information Panel

    """
    def __init__(self, parent=None):
        super().__init__(parent)
        group_box = QGroupBox(self.tr("减振趋势分析"))
        vbox = QVBoxLayout()
        input_panel = self.layout_input_panel()
        vbox.addLayout(input_panel)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        self.trend = TrendPlotWidget()
        self.info = TrendInformationWidget()
        hbox.addWidget(self.trend)
        hbox.addWidget(self.info)
        # self.setSizePolicy()
        group_box.setLayout(vbox)
        layout = QVBoxLayout()
        layout.addWidget(group_box)
        self.setLayout(layout)
    
    def parse_date_range(self):

        start_qdate = self.input_start_date.date()
        end_qdate = self.input_end_date.date()

        return [date(a_qdate.year(), a_qdate.month(), a_qdate.day())
            for a_qdate in (start_qdate, end_qdate)]

    def parse_sensor_no(self):
        """It should parse
            1. a single number
            2. numbers separated with comma,
            3. number range.
        """

        text = self.input_sensor_no.text()

        parts1 = text.split(",")

        sensor_no_list = list()

        for part in parts1:
            range_spec = part.split('-')
            if len(range_spec) == 1:
                sensor_no_list.append(int(range_spec[0]))
            else:
                sensor_no_list.extend(
                    [int(x) for x in range( int(range_spec[0]), int(range_spec[1]) )]
                )
        return sensor_no_list


    @Slot()
    def list_sensors(self):

        # TODO: list sensors from db.
        sensor_no_list = self.parse_sensor_no()
        date_range = self.parse_date_range()
        trend_data_map = {}
        for a_sensor_no in sensor_no_list:
            trend_data = damping_data.list_damping_trend_for_sensor(
                self.input_channel.currentData(),
                a_sensor_no,
                date_range=date_range

            )
            trend_data_map[a_sensor_no] = trend_data
        # construct data fro plot
        self.trend.data_map = trend_data_map

        self.trend.plot_line_chart()

        # TODO: Update Info panel accordingly.


    def layout_input_panel(self):

        layout = QHBoxLayout()

        self.input_start_date = QDateEdit()
        input_start_date_label = QLabel("起始日期:")

        self.input_end_date = QDateEdit()
        input_end_date_label = QLabel("结束日期:")

        # TODO(Gang): set default date range: Today (latest date when there're data) and the previous 90 days.

        self.input_channel = QComboBox()
        channel_rows = damping_data.list_channels()
        for a_channel in channel_rows:
            self.input_channel.addItem(a_channel.channelPos, a_channel)

        input_channel_label = QLabel("通道:")

        self.input_sensor_no = QLineEdit()
        input_sensor_no_label = QLabel("传感器编号:")
        # TODO(Gang): 可以指定一个传感器，也可以指定多个。例如 1,3-5

        self.input_button = QPushButton("确定")

        self.input_button.clicked.connect(self.list_sensors)

        items = [
            input_channel_label, self.input_channel,
            input_sensor_no_label,  self.input_sensor_no,
            input_start_date_label, self.input_start_date,
            input_end_date_label, self.input_end_date,

            self.input_button 

            ]
            

        max_w = [
            100, 140,
            120, 140,
            100, 140,
            100, 140,

            100
        ]

        
        aligns= [
            Qt.AlignRight, Qt.AlignLeft,
            Qt.AlignRight, Qt.AlignLeft,
            Qt.AlignRight, Qt.AlignLeft,
            Qt.AlignRight, Qt.AlignLeft,

            Qt.AlignRight
            
        ]

        params = zip(items, aligns, max_w)
        for item, align, w in params:
            item.setMaximumWidth(w)
            layout.addWidget(item, align)
        
        # layout.setSizeConstraint(QLayout.SetMaximumSize)
        # layout.SetMaximumSize(300,80)
        layout.setAlignment(Qt.AlignLeft)
        return layout

        


class TrendPlotWidget(QWidget):
    """

    """
    def __init__(self, parent=None):

        self.data_map = {}

        super().__init__(parent)
        layout = QHBoxLayout()

        self.matfig: plt.Figure = plt.figure(figsize=(8,6))
        self.figcanvas = FigureCanvas(self.matfig)
        # self.figcanvas
        self.ax = self.matfig.subplots()  # a single axes by default.
        
        # self.plot_line_chart()  # It will create the chart and place it in the chart view.

        self.figcanvas.setMinimumWidth(300)
        
        # layout.addWidget(self.chart_view1)
        layout.addWidget(self.figcanvas)
        self.setMinimumSize(600, 300)
        # self.setSizePolicy()
        self.setLayout(layout)

    def plot_line_chart(self):
        print("dump datamap:", self.data_map)
       
        if self.data_map is None:
            return
        
        self.ax.clear()  # clear only draws.
        sensor_nos = self.data_map.keys()
        for sno in sorted(sensor_nos):
            print("For sensor no", sno)
            data = self.data_map[sno]
            print("data list ", data)
           
            # series1.setName(f'趋势图 {sno}')
            x_dates = [r.evalDate for r in data]
            y_values = [r.dampingPara for r in data]

            print('x_dates', x_dates, 'y values', y_values)
            # TODO(Gang): Figure size accordingly; Legend/Color for each sensor No.
            # TODO(Gang): X-axis ticks and date formats for proper visualization.
            self.ax.plot_date(x_dates, y_values, '-')
            # self.matfig.show()
            self.figcanvas.draw()


class TrendInformationWidget(QWidget):
    """实时信息展示区
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout()
        
        damping_range = QLabel("3-5")
        layout.addRow(self.tr("Damping Range:"), damping_range)

        last_train = QLabel('x')
        layout.addRow(self.tr('Last Train:'), last_train)

        current_train = QLabel('x')
        layout.addRow(self.tr('Current Train:'), current_train)
        
        power_range = QLabel('x')
        layout.addRow(self.tr('Response Power Range:'), power_range)
        
        damping_effect = QLabel('x')
        layout.addRow(self.tr('Damping Effect:'), damping_effect)

        realtime_flag = QLabel('x')
        layout.addRow(self.tr('Realtime On/Off:'), realtime_flag)

        self.setLayout(layout)