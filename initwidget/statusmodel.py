
from PySide2.QtCore import (Qt, QAbstractTableModel, QModelIndex)

class StatusModel(QAbstractTableModel):

    def __init__(self, addresses=None, parent=None):
        super(StatusModel, self).__init__(parent)

        if addresses is None:
            self.addresses = []
        else:
            self.addresses = addresses

    def rowCount(self, index=QModelIndex()):
        """ Returns the number of rows the model holds. """
        return len(self.addresses)

    def columnCount(self, index=QModelIndex()):
        """ Returns the number of columns the model holds. """
        return 6

    def data(self, index, role=Qt.DisplayRole):
        """ Depending on the index and role given, return data. If not
            returning data, return None (PySide equivalent of QT's
            "invalid QVariant").
        """
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.addresses):
            return None

        if role == Qt.DisplayRole:
            num = self.addresses[index.row()]["number"]
            position = self.addresses[index.row()]["position"]
            online = self.addresses[index.row()]["online"]
            count = self.addresses[index.row()]["count"]
            freq = self.addresses[index.row()]["freq"]
            status = self.addresses[index.row()]["status"]
    
            if index.column() == 0:
                return num
            elif index.column() == 1:
                return position
            elif index.column() == 2:
                return online
            elif index.column() == 3:
                return count
            elif index.column() == 4:
                return freq
            elif index.column() == 5:
                return status


        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return u"仪表编号"
            elif section == 1:
                return u"仪表位置"
            elif section == 2:
                return u"上线时间"
            elif section == 3:
                return u"通道数"
            elif section == 4:
                return u"采集频率\n(单位:HZ)"
            elif section == 5:
                return u"状态"

        return None

    def insertRows(self, position, rows=1, index=QModelIndex()):
        """ Insert a row into the model. """
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.addresses.insert(position + row, {"name":"", "address":"", "time": ""})

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        del self.addresses[position:position+rows]

        self.endRemoveRows()
        return True

    def setData(self, index, value, role=Qt.EditRole):
        """ Adjust the data (set it to <value>) depending on the given
            index and role.
        """
        if role != Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.addresses):
            address = self.addresses[index.row()]
            if index.column() == 0:
                address["number"] = value
            elif index.column() == 1:
                address["position"] = value
            elif index.column() == 2:
                address["online"] = value
            elif index.column() == 3:
                address["count"] = value
            elif index.column() == 4:
                address["freq"] = value
            elif index.column() == 5:
                address["status"] = value
            else:
                return False

            self.dataChanged.emit(index, index, 0)
            return True

        return False

    def flags(self, index):
        """ Set the item flags at the given index. Seems like we're
            implementing this function just to see how it's done, as we
            manually adjust each tableView to have NoEditTriggers.
        """
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) |
                            Qt.ItemIsEditable)
