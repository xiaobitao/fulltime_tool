# -*- coding:utf-8 -*-
from functools import partial
import sys
import uuid
import time
from datetime import date

from PySide2 import QtCore
from PySide2.QtCore import Qt, Slot, Signal, QModelIndex, QMimeData, QTimer
from PySide2.QtWidgets import QWidget, QSplitter, QFileSystemModel,\
        QVBoxLayout, QHBoxLayout, QTreeView, QPushButton, QCalendarWidget, \
        QDateEdit, QLabel, QGroupBox
from PySide2.QtWidgets import QAbstractItemView, QProgressBar, QMenu, QAction, \
    QDialog, QTableView, QLineEdit, QFormLayout
from PySide2.QtGui import QContextMenuEvent

from PySide2.QtCharts import QtCharts

import numpy as np

from datawidget.dataexplorer import *
from datawidget.hdfstree import HDFSTreeWidget
from util.wimhdfs import HDFSDir


class FileOpsWidget(QWidget):
    """FileOpsWidget consists of a list of ops or indicators.
    """
    def __init__(self, tree_view, parent=None):
        super().__init__(parent)
        self.tree_view = tree_view  # the related tree_view.
        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        label1 = QLabel()
        label1.setText(self.tr("Current File Operation Indicator"))
        self.progress_bar = QProgressBar()
        hbox.addWidget(label1)
        hbox.addWidget(self.progress_bar)

        self.btn_refresh = QPushButton(self.tr("Refresh Directory"))
        
        self.btn_export = QPushButton(self.tr("Export Selected Files"))
        self.btn_export.clicked.connect(self.export)

        self.btn_delete = QPushButton(self.tr("Delete Selected Files"))
        self.btn_migration = QPushButton(self.tr("Data Migration"))

        # On Time File Removal.
        #

        vbox.addLayout(hbox)
        vbox.addWidget(self.btn_refresh)
        vbox.addWidget(self.btn_export)
        vbox.addWidget(self.btn_delete)
        vbox.addWidget(self.btn_migration)

        self.setLayout(vbox)
    
    def export(self):
        """export selected files """
        selected: QtCore.QItemSelectionModel = self.tree_view.selectionModel()
        indexes = selected.selectedIndexes()
        
        for index in indexes:
            # p = self.tree_view.model().filePath(index)
            if index.column() == 0:
                p = index.model().filePath(index)
                # we only care about the file, so for each row, one column is fine.
            
                print("File path for export", p)
                self.progress_bar.setMaximum(10)
                self.progress_bar.setMinimum(0)
                
                # Use a separate thread to copy/move the files.
                self.progress_bar.setValue(6)


class SelectDateOpsWidget(QWidget):
    """ Ops on Select Date which indicates a list of files
    """
    def __init__(self, btn_label,  parent=None):
        super().__init__(parent)

        vbox = QVBoxLayout()

        self.label = QLabel(self.tr('Specify a Date'))
        self.date1 = QDateEdit()
        self.date1.setCalendarPopup(True)
        today = date.today()
        qdate = QtCore.QDate(today.year,today.month,today.day)

        self.date1.setDate(qdate)

        self.btn = QPushButton(btn_label)
        vbox.addWidget(self.label)
        vbox.addWidget(self.date1)
        vbox.addWidget(self.btn)

        self.setLayout(vbox)


class FSQTreeView(QTreeView):
    """
    Override to handle a few interactions.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def selectionChanged(self, selected: QtCore.QItemSelection, deselected):
        """
        """
        for index in selected.indexes():
            print("selected Row", index.row(), ",Col", index.column())
            # Show the model value.
            model: QFileSystemModel = self.model()
            p = model.filePath(index)
            
            print( "File path", p)


class DataFileWidget(QWidget):
    """

    Visual Layout Sketch
    ---------------------

    ```
        VBox:
            Row 1: Use a Splitter so that User can resize in addition to scroll.
                Col 1: File Tree,
                Col 2: a vertical list of buttons/items.
                    layout: Use a VBox to lay out them.
            Row 2: Three Ops Groups.
                layout: HBox to lay out them
                Col i: ops group i
                    layout: VBox layout to organize the items.
    ```

    The HBox/VBox might be replaced by a splitter which can be resized by
    end user.

    A Context Menu (Right click or a keyboard shortcut) is provided to add some
    extra utilities. It can be done by overriding the context menu event handler,
    or by custom context handle signal.

    """
    def __init__(self, parent=None):
        """ add the components and layout them.
        """

        super().__init__(parent)
        
        ltvbox = QVBoxLayout()

        ltsplitter = QSplitter()
        ltvbox.addWidget(ltsplitter)

        self.fs_model = QFileSystemModel()
        default_path = 'c:/Users/Wang Gang'
        self.fs_model.setRootPath(default_path)
        # self.lt_tree = FSQTreeView()
        rootdir = HDFSDir("./")
        self.lt_tree = HDFSTreeWidget(rootdir)
        # self.lt_tree = 
        # self.lt_tree.setModel(self.fs_model)
        # self.lt_tree.setRootIndex(self.fs_model.index(default_path))
        # The ExtendedSelection behaves as in Windows File Explorer.
        # self.lt_tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        # TODO(Gang): Set layout hint(?) to make sure the Tree uses most of the space
        

        self.fs_ops = FileOpsWidget(tree_view=self.lt_tree)
        ltsplitter.addWidget(self.lt_tree)
        ltsplitter.addWidget(self.fs_ops)

        # Bottom Ops
        # Three Ops, with HBoxLayout
        lb_box = QHBoxLayout()
        # TODO(Gang): Limit the Vertical space for the ops panel.
        self.ops_export = SelectDateOpsWidget(btn_label=self.tr('Export to Folder'))
        self.ops_delete = SelectDateOpsWidget(self.tr('Delete Files on date'))
        self.ops_mark = SelectDateOpsWidget(self.tr('Toggle Star Mark'))
        lb_box.addWidget(self.ops_export)
        lb_box.addWidget(self.ops_delete)
        lb_box.addWidget(self.ops_mark)


        ltvbox.addLayout(lb_box)

        self.setLayout(ltvbox)

        # create a context menu. it will be visible when called in the context menu event.
        self.menu = QMenu('Context Menu')
        # action1 = self.menu.addAction('Example Action')
        # # self.connect(action1, QAction.triggered, self, self.example_action)
        # action1.triggered.connect(self.example_action)
        data_explore = self.menu.addAction('Explore data files')
        data_explore.triggered.connect(self.explore_data)

        self.dataExplorer = DataExplorer(self)

    
    def contextMenuEvent(self, event: QContextMenuEvent):
        
        # create a menu and pop up.
        self.menu.popup(event.globalPos())
        # print('context menu called')

    @Slot()
    def example_action(self):
        print("Example Action Triggered")

    @Slot()
    def explore_data(self):
        """ open a dialog to plot and examine data
        """
        self.dataExplorer.show()


    @Slot(QModelIndex, QModelIndex)
    def showSelected(self, selected, deselected):
        print('Selected:', selected)



class FeatureDataWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)


class DataWidget(QWidget):
    """???????????????.
    Composition of DataFileWidget and FeatureDataWidget.
    """

    def __init__(self, parent=None):
        super(DataWidget, self).__init__(parent)
        layout = QVBoxLayout()

        splitter = QSplitter()
        

        left_group = QGroupBox(self.tr('Data File'))
        self.data_file_widget = DataFileWidget()
        left_vbox = QVBoxLayout()
        left_vbox.addWidget(self.data_file_widget)
        left_group.setLayout(left_vbox)
        
        right_group = QGroupBox(self.tr('Features'))
        right_vbox = QVBoxLayout()
        self.feature_widget = FeatureDataWidget()
        right_vbox.addWidget(self.feature_widget)
        right_group.setLayout(right_vbox)


        splitter.addWidget(left_group)
        splitter.addWidget(right_group)
        
        layout.addWidget(splitter)

        self.setLayout(layout)




