from  PySide2.QtCore import Qt
from datawidget.hdfstree import HDFSTreeWidget
from util.wimhdfs import HDFSDir

class SingleHDFSTreeWidget(HDFSTreeWidget):

    def __init__(self, hdir):
        super(SingleHDFSTreeWidget, self).__init__(hdir)

        self.treewid.itemClicked.connect(self.itemclckSlot)
        self.checkitems = []

    
    def itemclckSlot(self, item, column):
        print("column %d" % column)
        if item.checkState(0):
            print("item checked")
            print(len(self.checkitems))
            for it in self.checkitems:
                if it.text(0) == item.text(0):
                    continue
                it.setCheckState(0, Qt.Unchecked)
            del self.checkitems[:]
            self.checkitems.append(item)
        else:
            if item in self.checkitems:
                self.checkitems.remove(it)

    def getSelectItemPath(self):
        if len(self.checkitems) == 0:
            return ""
        else:
            return self.checkitems[0].data(4, Qt.UserRole)


                

