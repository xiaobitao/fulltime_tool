try:
    import cpickle as pickle
except ImportError:
    import pickle

from PySide2.QtCore import (Qt, Signal, QRegExp, QModelIndex,
                            QItemSelection, QItemSelectionModel, QSortFilterProxyModel)
from PySide2.QtWidgets import (QWidget, QTabWidget, QMessageBox, QTableView,
                               QAbstractItemView, QVBoxLayout, QHeaderView)
# from PySide2 import QtGui
from initwidget.statusmodel import StatusModel

# from util.database import get_reports
# from newaddresstab import NewAddressTab
# from adddialogwidget import AddDialogWidget


class MeterStatus(QWidget):
    """ The central widget of the application. Most of the addressbook's
        functionality is contained in this class.
    """

    selectionChanged = Signal(QItemSelection)

    def __init__(self, parent=None):
        """ Initialize the AddressWidget. """
        super(MeterStatus, self).__init__(parent)

        self.tableModel = StatusModel()
        self.tableView = QTableView()
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setModel(self.tableModel)
        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.refreshtable()

        # self.setupTabs()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tableView)
        self.setLayout(main_layout)
        
    def refreshtable(self):
        # reports = get_reports()
        # self.tableModel.addresses.clear()
        # for r in reports:
        #     # filename = r.filename
        #     # datetime = r.create_time
        #     # name = r.name
        #     self.addEntry(r.name, r.filename, r.create_time)
        pass


    def addEntry(self, num=None, pos=None, online=None, count=None, freq=None, status=True):
        """ Add an entry to the addressbook. """
        # if name is None and address is None:
        #     addDialog = AddDialogWidget()

        #     if addDialog.exec_():
        #         name = addDialog.name
        #         address = addDialog.address

        address = {"number": num, "position": pos, "online": online,
                   "count": count, "freq": freq, "status": status}
        addresses = self.tableModel.addresses[:]

        # The QT docs for this example state that what we're doing here
        # is checking if the entered name already exists. What they
        # (and we here) are actually doing is checking if the whole
        # name/address pair exists already - ok for the purposes of this
        # example, but obviously not how a real addressbook application
        # should behave.
        try:
            addresses.remove(address)
            QMessageBox.information(self, "Duplicate Name",
                                    "The name \"%s\" already exists." % name)
        except ValueError:
            # The address didn't already exist, so let's add it to the model.

            # Step 1: create the  row
            self.tableModel.insertRows(0)

            # Step 2: get the index of the newly created row and use it.
            # to set the name
            ix = self.tableModel.index(0, 0, QModelIndex())
            self.tableModel.setData(ix, address["number"], Qt.EditRole)

            # Step 3: lather, rinse, repeat for the address.
            ix = self.tableModel.index(0, 1, QModelIndex())
            self.tableModel.setData(ix, address["position"], Qt.EditRole)

            ix = self.tableModel.index(0, 2, QModelIndex())
            self.tableModel.setData(ix, str(address["online"]), Qt.EditRole)

            ix = self.tableModel.index(0, 3, QModelIndex())
            self.tableModel.setData(ix, str(address["count"]), Qt.EditRole)

            ix = self.tableModel.index(0, 4, QModelIndex())
            self.tableModel.setData(ix, str(address["freq"]), Qt.EditRole)
            
            ix = self.tableModel.index(0, 5, QModelIndex())
            self.tableModel.setData(ix, str(address["status"]), Qt.EditRole)
            
    def removeEntry(self):
        """ Remove an entry from the addressbook. """
        tableView = self.currentWidget()
        proxyModel = tableView.model()
        selectionModel = tableView.selectionModel()

        # Just like editEntry, but this time remove the selected row.
        indexes = selectionModel.selectedRows()

        for index in indexes:
            row = proxyModel.mapToSource(index).row()
            self.tableModel.removeRows(row)

        # If we've removed the last address in the model, display the
        # newAddressTab
        if self.tableModel.rowCount() == 0:
            self.insertTab(0, self.newAddressTab, "Address Book")
