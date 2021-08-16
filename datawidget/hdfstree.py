from PySide2 import QtCore, QtWidgets, QtWidgets
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel,
                               QComboBox, QLineEdit, QGridLayout)


from PySide2.QtCore import Signal, QObject
import sys
from util.wimhdfs import HDFSDir, HDFSFile

class HDFSTreeWidget(QtWidgets.QWidget):

    class treeitemselected(QObject):
        someSignal = Signal()

    def __init__(self, hdir):
        super(HDFSTreeWidget, self).__init__()
        vsub_box1 = QVBoxLayout()
        self.treewid = QtWidgets.QTreeWidget()
        self.treewid.setColumnWidth(0, 600)
        vsub_box1.addWidget(self.treewid)
        self.rootdir = hdir
        QtCore.QTimer.singleShot(1, self.__init_treewid)
        self.treewid.itemClicked.connect(self.__dataitem_click)
        self.treewid.currentItemChanged.connect(self.__dateitem_changed)
        self.setLayout(vsub_box1)
        isel = self.treeitemselected()
        self.itemselected = isel.someSignal

    def get_item_dir(self, item, path):
        ipar = item.parent()
        path = item.text(0) + path
        if ipar is None:
            return path
        else:
            return self.get_item_dir(ipar, path)

    def selected_items(self):
        print("selected items")
        file_paths = []
        for item in self.treewid.findItems("", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive):
            if item.checkState(0)>0:
                # print(type(item))
                # print (item.data(4, QtCore.Qt.UserRole),item.checkState(0))
                file_paths.append(item.data(4, QtCore.Qt.UserRole))
        return file_paths
            
    # @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def __dataitem_click(self, it, col):
        print(it, col, it.text(col))
        print(self.itemselected)
        print(dir(self.itemselected))
        self.itemselected.emit()

    def __init_treewid(self):
        # header = QtWidgets.QTreeWidgetItem([u"名称", u"路径", u"文件大小", u"创建时间"])
        header = QtWidgets.QTreeWidgetItem([u"名称", u"文件大小", u"创建时间"])
       
        # hsize = QtCore.QSize(400, 20)
        # header.setSizeHint(0, hsize)
        
        self.treewid.setHeaderItem(header)
        # self.treewid.headerView().resizeSection(0, 200);
        
        self.rootdir.refresh()
        self.__add_hdfschilditem(self.rootdir)

    def __dateitem_changed(self, current, previous):
        # previous.setCheckState(0, QtCore.Qt.Unchecked)
        # current.setCheckState(0, QtCore.Qt.Checked)
        pass
        
    def __add_hdfschilditem(self, hfobj, parentitem = None):
        path = hfobj.path
        name = path.split("/")[-1]
        length = hfobj.length
        # print(type(hfobj.modtime))
        # print(length)
        if hfobj.modtime != 0:
            strtime = '{0:%Y-%m-%d %H:%M:%S}'.format(hfobj.modtime)
        else:
            strtime = ""
        curitem = None
        if parentitem is not None:
            curitem = QtWidgets.QTreeWidgetItem(parentitem, [name, str(length), strtime])
        else:
            curitem = QtWidgets.QTreeWidgetItem(self.treewid, [name, str(length), strtime])
        if isinstance(hfobj, HDFSFile):
            curitem.setFlags(curitem.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
            curitem.setCheckState(0, QtCore.Qt.Unchecked)
        # hsize = QtCore.QSize(400, 20)
        # curitem.setSizeHint(0, hsize)
        curitem.setData(4, QtCore.Qt.UserRole, hfobj.path)
        if isinstance(hfobj, HDFSDir):
            # add item first
            QtWidgets.QApplication.processEvents()
            hfobj.refresh()
            for ch in hfobj.childs:
                # QtWidgets.QApplication().instance().processEvents()
                self.__add_hdfschilditem(ch, curitem)



# if __name__ == '__main__':
#     from PySide2.QtWidgets import QApplication
#     app = QApplication(sys.argv)
#     tdir = HDFSDir("/nfs/test/")
#     # model = TreeModel(tdir.get_dict())
#     window = HDFSTreeWidget(tdir)
#     window.show()
#     sys.exit(app.exec_())