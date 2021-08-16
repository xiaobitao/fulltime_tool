from functools import partial
import sys
import uuid
import time
from datetime import date

from PySide2 import QtCore
from PySide2.QtCore import Qt, Slot, Signal, QModelIndex, QMimeData, QTimer
from PySide2.QtWidgets import QWidget, QSplitter, QFileSystemModel,\
        QVBoxLayout, QHBoxLayout, QTreeView, QPushButton, QCalendarWidget, \
        QDateEdit, QLabel, QGroupBox, QStatusBar, QTabWidget, QTextEdit 
from PySide2.QtWidgets import QAbstractItemView, QProgressBar, QMenu, QAction, \
    QDialog, QTableView, QLineEdit, QFormLayout, QScrollBar, QSizePolicy
from PySide2.QtGui import QContextMenuEvent

from PySide2.QtCharts import QtCharts
from PySide2 import QtWebEngineCore
from PySide2 import QtWebEngine

from PySide2.QtWebEngineWidgets import QWebEngineView

import numpy as np

import pandas as pd

from datawidget.core import list_files, load_data


class DataExplorer(QDialog):
    """DataExplorer is a utility window to explore a single (or a continuous set of) file
    to find some hints.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(False)
        self.setWindowTitle('Data Explorer')
        # self.setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowState(Qt.WindowMaximized)
        self.setMinimumSize(1440, 900)
        
        self.status_bar = QStatusBar()

        self.status_bar.setMaximumHeight(40)
        self.status_bar.setStyleSheet("* {background-color: yellow}")
        

        self.status_bar.showMessage('sample message', 10)

        self.left_right_splitter = QSplitter()
        self.left_tree = QTreeView()
        self.left_tree.setMinimumWidth(200)
        self.left_right_splitter.addWidget(self.left_tree)
        self.right_panel = QSplitter(Qt.Orientation.Vertical)  # a vertical splitter.
        self.right_panel.setMinimumWidth(1000)

        """ specifying self as parent is required for child items to locate it before calling
         setlayout which will help specify the parent.
        """
        self.details_panel = ExplorerDetails() # tabbed area of details, like table, text, and etc.

        self.charts_panel = ExplorerCharts(self.details_panel, self)  
        
        self.right_panel.addWidget(self.charts_panel)
        self.right_panel.addWidget(self.details_panel)


        self.left_right_splitter.addWidget(self.right_panel)

        layout = QVBoxLayout()
        layout.addWidget(self.left_right_splitter)
      
        layout.addSpacing(20)
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    


class ExplorerCharts(QWidget):
    """
    ExplorerCharts help us visiualize the data.
    """

    def __init__(self, details, parent=None):
        super().__init__(parent)
        self.details = details  # Hold a Reference to the details widget.
        
        # For now, we use a single chart and a set of ops.
        # Latter we might enable selection of multiple chart types.
        # 

        layout = QHBoxLayout()

        # Layout 2 charts. 3 is too much to display. We might enable more flexible display later.
        #

        self.n_charts = 2

        chart_layout = QVBoxLayout()
        self.charts = list()
        for i in range(self.n_charts):
            
            chart_i = QtCharts.QChart()  # data related.
            chart_view_i = QtCharts.QChartView(chart_i)  # View related.
            chart_view_i.setMinimumSize(1200, 300)
            # RubberBand is for zooming effect.
            chart_view_i.setRubberBand(QtCharts.QChartView.HorizontalRubberBand)
            # TODO(Gang): We'll have to synchronize the ops on all the charts when zooming.
            """It might be calling some slots, or a custom RubberBand."""

            self.charts.append(chart_i)
            chart_layout.addWidget(chart_view_i)
       
        layout.addLayout(chart_layout)
        
        # Operations/Options/
        ops_panel = QFormLayout()
        self.ops_x_tick = QLineEdit()
        self.ops_x_tick.setText('15')
        self.ops_x_tick.editingFinished.connect(self.update_x_ticks)


        
        ops_panel.addRow('X Ticks', self.ops_x_tick)

        self.ops_reset_x = QPushButton('Reset X')
        self.ops_reset_x.clicked.connect(self.reset_x)
        ops_panel.addWidget(self.ops_reset_x)

        self.ops_target_node = QLineEdit()
        self.ops_target_node.setText('100')  # Default Node Point.
        self.ops_target_node.editingFinished.connect(self.node_updated)
        ops_panel.addRow('Target Node', self.ops_target_node)

        self.ops_node_count = QLineEdit()
        self.ops_node_count.setText(str(self.n_charts))  # We see 2 nodes a time by default.
        self.ops_target_node.editingFinished.connect(self.node_updated)
        ops_panel.addRow('Node Count', self.ops_node_count)

        self.ops_start_timestamp = QLineEdit()
        self.ops_start_timestamp.setText('2019-07-15 00:00')
        self.ops_start_timestamp.editingFinished.connect(self.reload_data)
        ops_panel.addRow('Start Timestamp', self.ops_start_timestamp)

        self.ops_time_length = QLineEdit()
        self.ops_time_length.setText('5')  # 0..5, or 6 minutes by default.
        self.ops_time_length.editingFinished.connect(self.reload_data)
        ops_panel.addRow('Time length(minute)', self.ops_time_length)

        self.ops_a1 = QPushButton('Line Plot')
        self.ops_a1.clicked.connect(self.do_line_plot)
        ops_panel.addWidget(self.ops_a1)

        g1 = QGroupBox("Plain Signal Stats. Check")
        g1_layout = QFormLayout()
        self.g1_plain_signal_button = QPushButton("Run")
        self.g1_plain_signal_button.clicked.connect(self.run_plain_signal_check)
        g1_layout.addRow(self.g1_plain_signal_button)
        g1.setLayout(g1_layout)
        ops_panel.addRow(g1)

        g2 = QGroupBox("Find Significant Signal Bounds")
        g2_layout = QFormLayout()
        self.g2_find_sig_bounds_button = QPushButton("Run")
        self.g2_find_sig_bounds_button.clicked.connect(self.run_find_sig_bounds)

        layout.addLayout(ops_panel)


        self.setLayout(layout)
        
        self.matrix = None
        # self.line = None
        self.has_to_update_chart_flag = True  # even the first plot is considered to be an update.
        self.has_to_reload_data_flag = False


        # find and bind a status bar of the parents.
        self.status_bar = QStatusBar()  # our own status_bar, not shown.
        # We prefer to show it in a parent status bar.
        parent = self.parent()
        for x in range(10):

            if hasattr(parent, 'status_bar'):
                self.status_bar = parent.status_bar
                break
            else:
                if hasattr(parent, 'parent'):
                    parent = parent.parent()
                else:
                    print("Failed to find a parent object with status_bar in place.")
                    break
        


    @Slot()
    def update_x_ticks(self):
        new_tick_count = self.ops_x_tick.text()

        for chart in self.charts:
            chart.axisX().setTickCount(int(new_tick_count))
    
    @Slot()
    def reload_data(self):
        self.has_to_reload_data_flag = True
        self.has_to_update_chart_flag = True
        # self.do_line_plot()

    @Slot()
    def node_updated(self):
        self.has_to_update_chart_flag = True
        # self.do_line_plot()
    
    @Slot()
    def reset_x(self):
        """Reset X Axis after we have rubber zoom ops.
        """
        for chart in self.charts:
            chart.axisX().setMin(0)

    @Slot()
    def do_line_plot(self):
        """ 
        
        Plot Three or Five monitoring nodes
            user input: center node, total nodes.

        Time window: 1, 5 or 10 minutes
            user input: length in minute, starting time.

        """
        
        
        dt_input = self.ops_start_timestamp.text()  # '2019-07-15 00:00'
        len_ = int(self.ops_time_length.text())

        if self.matrix is None or self.has_to_reload_data_flag:
            self.status_bar.showMessage("About to load new data...")
            self.matrix = load_data('p0', dt_input , len_, 527)
            
            self.status_bar.showMessage("About to load new data... Done..." )
           

            self.has_to_reload_data_flag = False  # reset flag.

        # TODO(Gang): plot multiple charts at a time.
        if self.has_to_update_chart_flag:

            selected_m = int(self.ops_target_node.text())
            # TODO(Gang): validate and prompt (User has to be sure all of them are valid)
            # we plot m, m+1, and m+2 

            
            # remove old series first. for the init case, it will be noops
            for chart in self.charts:
                chart.removeAllSeries()

                if chart.axisX() is not None:
                    chart.removeAxis(chart.axisX())
                if chart.axisY() is not None:
                    chart.removeAxis(chart.axisY())

            for i in range(self.n_charts):
                line = QtCharts.QLineSeries()
                selected_data = self.matrix[:, selected_m + i]
                len1 = selected_data.size
                listp = list(zip(range(len1), selected_data))
                # line.append(listp)
                for p in listp:
                    line.append(*p)
                x = QtCharts.QValueAxis()
                x.setTickCount(int(self.ops_x_tick.text()))
                x.setMin(0)
                x.setTickAnchor(0)
                y = QtCharts.QValueAxis()
                y.setTickAnchor(0)
                y.setRange(selected_data.min()-2, selected_data.max()+2)
                self.charts[i].addSeries(line)
            

            # setAxisX do two things in one step: addAxis and attachAxis.
            # But addAxis can do more, for example, we can have multiple axises.
                self.charts[i].setAxisX(x, line)
                self.charts[i].setAxisY(y, line)


    @Slot()
    def run_find_sig_bounds(self):
        """ Based on the fact that the self-vibration std is very small.
            We use a window to get the moving std. 
            It can be an adaptive window or fixed window.

            NOTE: It can be a streaming problem, or a batch program. it
            is more flexible to view it as a streaming problem.

        """

        mw = 500  # use 500 as the moving window size.

        # NOTE(Gang): Here we use a static model to find the bounds of the signal.
        # Later we need to transform it to be a stream based.
        selected_m = int(self.ops_target_node.text())  # selected monitoring node.
        data = self.matrix[:, selected_m]

        s = pd.Series(data)
        




    @Slot()
    def run_plain_signal_check(self):
        self.status_bar.showMessage("传感器在无外部激励时，其振动信号标准差不能太大...")
        # self.details.stats_message.append("Stats. std:0, mean:0. Confidence: 0.95")

        def append_(msg):
            self.details.stats_message.append(msg)
        
        shape = self.matrix.shape
        cols = shape[1]
        std_data = list()
        for i in range(cols):
            node_i_data = self.matrix[:, i]

            std_i = np.std(node_i_data)
            mean_i = np.mean(node_i_data)
            # append_('Node {}: mean:{:.4f}, std:{:.4f}'.format(i, mean_i, std_i))

            std_data.append(std_i)
        std_series = pd.Series(std_data)
        std_sorted_desc = std_series.sort_values(ascending=False)
        top10 = std_sorted_desc.head(10)
        tail10 = std_sorted_desc.tail(10)
        
        std_mean = std_series.mean()
        append_("STD Mean: {:.4f}".format(std_mean) )
        append_('STD Least 10:')
        append_(str(tail10))
        append_('STD Max Top 10:')
        append_(str(top10))
        append_('STD Stats. Describe:')
        append_(str(std_series.describe()))



        
        


        
        

class ExplorerDetails(QWidget):
    """
    First, a table;
    Then a set of tables or text areas in Tabs

    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        # Use a Tab to host multiple detail pages.
        self.tabs = QTabWidget()
        self.stats_message = QTextEdit("Some default texts")
        
        self.tabs.addTab(self.stats_message, "Stats. Message")

        # It seems it can't be activated and painted within a tab.
        # self.web = QWebEngineView()
        # self.web.show()
        # self.web.load(QtCore.QUrl("http://www.baidu.com"))
        # tabIndex = self.tabs.addTab(self.web, "Web Engine")

        self.table_view = QTableView()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)
