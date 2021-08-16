from PySide2 import QtCore, QtWidgets, QtWidgets
import sys

app = QtWidgets.QApplication(sys.argv)
QtWidgets.qApp = app

folderTree = QtWidgets.QTreeWidget()

header = QtWidgets.QTreeWidgetItem(["Virtual folder tree","Comment"])
#...
folderTree.setHeaderItem(header)   #Another alternative is setHeaderLabels(["Tree","First",...])

root = QtWidgets.QTreeWidgetItem(folderTree, ["Untagged files"])
root.setData(2, QtCore.Qt.EditRole, 'Some hidden data here')	# Data set to column 2, which is not visible

folder1 = QtWidgets.QTreeWidgetItem(root, ["Interiors"])
folder1.setData(2, QtCore.Qt.EditRole, 'Some hidden data here')	# Data set to column 2, which is not visible

folder2 = QtWidgets.QTreeWidgetItem(root, ["Exteriors"])
folder2.setData(2, QtCore.Qt.EditRole, 'Some hidden data here')	# Data set to column 2, which is not visible

folder1_1 = QtWidgets.QTreeWidgetItem(folder1, ["Bathroom", "Seg was here"])
folder1_1.setData(2, QtCore.Qt.EditRole, 'Some hidden data here')	# Data set to column 2, which is not visible

folder1_2 = QtWidgets.QTreeWidgetItem(folder1, ["Living room", "Approved by client"])
folder1_2.setData(2, QtCore.Qt.EditRole, 'Some hidden data here')	# Data set to column 2, which is not visible



def printer( treeItem ):
	foldername = treeItem.text(0)
	comment = treeItem.text(1)
	data = treeItem.text(2)
	print(foldername + ': ' + comment + ' (' + data + ')')


folderTree.itemClicked.connect( lambda : printer( folderTree.currentItem() ) )


folderTree.show()
sys.exit(app.exec_())