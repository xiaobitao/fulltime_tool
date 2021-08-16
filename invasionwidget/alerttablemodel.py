
from PySide2.QtCore import (Qt, QAbstractTableModel, QModelIndex)



class AlertTableModel(QAbstractTableModel):

    def __init__(self, alerts=None, parent=None):
        super(AlertTableModel, self).__init__(parent)
        self.COL_CREATETIME = 0
        self.COL_ALARMTYPE = 1
        # self.COL_SENSORZONE = 2
        self.COL_SENSORPOS = 2
        self.COL_ALARMLEVEL = 3
        # self.COL_ZONENUM = 1
        # self.COL_POSITION = 2
        # self.COL_ALERTTIME = 3
        self.COL_ALERTSTATUS = 4
        self.COL_RESPEOPLE = 5
        self.COL_RESTIME = 6
        self.COL_NOTE = 7
        # 设置alert id
        self.COL_OPERATION = 8
        # self.COL_ALERT_ID = 9
        if alerts is None:
            self.alerts = []
        else:
            self.alerts = alerts

    def rowCount(self, index=QModelIndex()):
        """ Returns the number of rows the model holds. """
        return len(self.alerts)

    def columnCount(self, index=QModelIndex()):
        """ Returns the number of columns the model holds. """
        return 9

    def data(self, index, role=Qt.DisplayRole):
        """ Depending on the index and role given, return data. If not
            returning data, return None (PySide equivalent of QT's
            "invalid QVariant").
        """
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.alerts):
            return None

        if role == Qt.DisplayRole:
            if index.column() == self.COL_CREATETIME:
                return self.alerts[index.row()]["create_time"]
            elif index.column() == self.COL_ALARMTYPE:
                alert_type = self.alerts[index.row()]["alert_type"]
                if alert_type == 1:
                    return u"外部入侵"
                else:
                    return u"未知"
            elif index.column() == self.COL_SENSORPOS:
                return self.alerts[index.row()]["position"]
            elif index.column() == self.COL_ALARMLEVEL:
                return self.alerts[index.row()]["alert_level"]
            elif index.column() == self.COL_ALERTSTATUS:
                if self.alerts[index.row()]["status"] == 0:
                    return "未处理"
                else:
                    return "已处理"
            elif index.column() == self.COL_RESPEOPLE:
                return self.alerts[index.row()]["resolve_people"]
            elif index.column() == self.COL_RESTIME:
                return self.alerts[index.row()]["resolve_time"]
            elif index.column() == self.COL_NOTE:
                return self.alerts[index.row()]["note"]
            elif index.column() == self.COL_OPERATION:
                return u"编辑"
            elif index.column() == self.COL_ALERT_ID:
                return self.alerts[index.row()]["alert_id"]
            else:
                return False
        return None

    def getAlertID(self, row):
        return self.alerts[row]["alert_id"]


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return u"时间"
            elif section == 1:
                return u"入侵类型"
            elif section == 2:
                return u"位置"
            elif section == 3:
                return u"报警级别"
            elif section == 4:
                return u"状态"
            elif section == 5:
                return u"处理人"
            elif section == 6:
                return u"处理时间"
            elif section == 7:
                return u"备注"
            elif section == 8:
                return u"操作"


        return None

    def insertRows(self, position, rows=1, index=QModelIndex()):
        """ Insert a row into the model. """
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.alerts.insert(position + row, {"name":"", "address":"", "time": ""})

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        del self.alerts[position:position+rows]

        self.endRemoveRows()
        return True

    def clear(self):
        self.removeRows(0, len(self.alerts))
        # del self.alerts[:]

    def setData(self, index, value, role=Qt.EditRole):
        """ Adjust the data (set it to <value>) depending on the given
            index and role.
        """
        if role != Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.alerts):
            alert = self.alerts[index.row()]
            if index.column() == self.COL_CREATETIME:
                alert["create_time"] = value
            elif index.column() == self.COL_ALARMTYPE:
                alert["alert_type"] = value
            elif index.column() == self.COL_SENSORPOS:
                alert["position"] = value
            elif index.column() == self.COL_ALARMLEVEL:
                alert["alert_level"] = value
            elif index.column() == self.COL_ALERTSTATUS:
                alert["status"] = value
            elif index.column() == self.COL_RESPEOPLE:
                alert["resolve_people"] = value
            elif index.column() == self.COL_RESTIME:
                alert["resolve_time"] = value
            elif index.column() == self.COL_NOTE:
                alert["note"] = value
            elif index.column() == self.COL_OPERATION:
                alert["alert_id"] = value
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
