""" 减振柱形图，各传感器点位上测得的减振值以柱形对比列出。

可以查看不同日期、不同通道的情况。

"""

from functools import partial
import sys
import uuid
import time
from datetime import date

from PySide2 import QtCore
from PySide2.QtCore import Qt, Slot, Signal, QModelIndex, QMimeData, QTimer
from PySide2.QtWidgets import QWidget, QSplitter, QFileSystemModel,\
        QVBoxLayout, QHBoxLayout, QTreeView, QPushButton, QCalendarWidget, \
        QDateEdit, QLabel, QGroupBox, QCheckBox, QComboBox
from PySide2.QtWidgets import QAbstractItemView, QFormLayout, QComboBox, \
    QTableWidget, QSizePolicy, QGridLayout, QLayout
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QTranslator, QLocale, QLibraryInfo
from PySide2.QtWidgets import QApplication

from . import damping_data

class DampingAnalysisBarWidget(QWidget):
    """减振分析，柱状图

    Screen
    --------
    VBox Layout:

    
    Top: Inputs.
    HBox Layout:
    Left: Bar Plot. May go with matplotlib or qt plot.
    Right: Information Panel

    Logic
    ------
    从数据库中查询

    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.evals_data = []

        group_box = QGroupBox("按日期查询")
        # By default we provide the latest.
        vbox = QVBoxLayout()
        
        # assemble query inputs form.
        inputs = self.layout_query_input()
        vbox.addLayout(inputs)

        hbox = QHBoxLayout()
        self.barplot  = BarPlotWidget(data=self.evals_data)
        self.info = DailyInformationWidget()
        hbox.addWidget(self.barplot)
        hbox.addWidget(self.info)
        vbox.addLayout(hbox)

        # self.setSizePolicy()
        group_box.setLayout(vbox)
        layout = QVBoxLayout()
        layout.addWidget(group_box)
        self.setLayout(layout)

        # let's load the initial plot by default.
        self.list_sensors()
    
    @Slot()
    def list_sensors(self):
        a_channel = self.input_channel.currentData()
        a_qdate = self.input_date.date()
        damping_flag = self.input_damping_area_check.isChecked()
        # From a Qdate to a py date.
        a_pydate = date(a_qdate.year(), a_qdate.month(), a_qdate.day() )

        print("current channel:", a_channel)

        the_date, evals = damping_data.list_damping_evals_for_channel(a_channel, a_pydate, damping_flag=damping_flag)
        if evals is None or len(evals) == 0:
            # Fall back to the latest date case and signal it.
            the_date, evals = damping_data.list_damping_evals_for_channel(a_channel, latest=True, damping_flag=damping_flag)
            # TODO: add a visual hint of the latest.
            a_qdate2 = QtCore.QDate(the_date.year, the_date.month, the_date.day)
            self.input_date.setDate(a_qdate2)

        print("evals items len:", len(evals), 'as of date:', the_date)

        self.evals_data.clear()
        self.evals_data.extend(evals)
        # how to trigger a redraw?
        self.barplot.plot_bar_chart()


    def layout_query_input(self):
        layout = QHBoxLayout()

        self.input_date = QDateEdit()
        input_date_label = QLabel("日期:")

        self.input_channel = QComboBox()
        channel_rows = damping_data.list_channels()
        for a_channel in channel_rows:
            self.input_channel.addItem(a_channel.channelPos, a_channel)

        input_channel_label = QLabel("通道:")

        self.input_damping_area_check = QCheckBox("只显示减振道床区域")
        self.input_damping_area_check.setChecked(True) # Checked by default.

        self.input_button = QPushButton("确定")

        self.input_button.clicked.connect(self.list_sensors)

        items = [
            input_date_label, self.input_date,
            input_channel_label, self.input_channel,
            self.input_damping_area_check,
            self.input_button 

            ]
        aligns= [
            Qt.AlignRight, Qt.AlignLeft,
            Qt.AlignRight, Qt.AlignLeft,
            Qt.AlignRight,
            Qt.AlignRight
            
        ]

        max_w = [
            50, 140,
            50, 140,
            210,
            100
        ]

        params = zip(items, aligns, max_w)
        for item, align, w in params:
            item.setMaximumWidth(w)
            layout.addWidget(item, align)
        
        # layout.setSizeConstraint(QLayout.SetMaximumSize)
        # layout.SetMaximumSize(300,80)
        layout.setAlignment(Qt.AlignLeft)
        return layout


        


class BarPlotWidget(QWidget):
    """ Use QtCharts first, integrate Matplotlib if missing in QtCharts,
    or if the code has already been written in matplotlib.

    """
    def __init__(self, parent=None, data=[]):
        super().__init__(parent)
        layout = QHBoxLayout()

        self.data = data  # use this data to plot.
        # self.chart2 = QtCharts.QChart()
        self.chart_view2 = QtCharts.QChartView()
        # self.plot_bar_chart()

        layout.addWidget(self.chart_view2)
        self.setMinimumSize(600, 300)
        # self.setSizePolicy()
        self.setLayout(layout)

    
    def plot_bar_chart(self, reset=True):
        import numpy as np

        # if reset:
        #     # clear the chart first.
        #     # self.chart2.removeAllSeries()
        #     self.chart2 = QtCharts.QChart()
        #     self.chart_view2.setChart()

        # Reference: https://doc.qt.io/qt-5/qtcharts-barchart-example.html
        barset1 = QtCharts.QBarSet('传感器测得减振值')
        
        # TODO: 提供鼠标移动到图上以后的详细信息显示，以提供准确信息.
        
        values = [5, 14, 15, 7, 16, 6, 5, 15, 5, 14 ]
        values = np.random.randint(10, 30, 60)
        values = [ s.dampingPara for s in self.data]
        for i in values:
            barset1.append(i)

        bar_series1 = QtCharts.QBarSeries()
        bar_series1.append(barset1)
        chart = QtCharts.QChart()
        chart.addSeries(bar_series1)
        axis_x = QtCharts.QBarCategoryAxis()
        axis_x.append([str(i) for i in range(len(values)) ])

        chart.addAxis(axis_x, Qt.AlignBottom)
        bar_series1.attachAxis(axis_x)

        axis_y = QtCharts.QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series1.attachAxis(axis_y)

        # Use two spline series to mark the high and low points.
        # TODO(Gang): Ask how they have plotted. not sure if it is splines.
        # spline_series1 = QtCharts.QSplineSeries()

        # spline_series1.append()
        self.chart_view2.setChart(chart)  # use the new chart.


class DailyInformationWidget(QWidget):
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