"""
Test Run of the DataWidget and its sub items.

"""
import os
import PySide2

import sys
from PySide2.QtCore import QTranslator, QLocale, QLibraryInfo
from PySide2.QtWidgets import QApplication
# from PySide2.QtWebEngine import *

import datawidget

def fix_env():
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(
        os.path.dirname(PySide2.__file__),
         'plugins', 'platforms')

def test_hello1(qtbot):
    print("hi")

if __name__ == "__main__":
    fix_env()
    app = QApplication()
    # QtWebEngine.initialize()  # Required, otherwise it doesn't load the extension right.

    #load system module locale.
    trans1 = QTranslator()
    trans1path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    print("qt module trans path:", trans1path)
    # NOTE(Gang): looks like the treeview column names are not translated to zh cn??
    # we can provide overriden for it if insist.
    trans1.load("qt_" + QLocale.system().name(),
     QLibraryInfo.location(QLibraryInfo.TranslationsPath))

    trans = QTranslator()
    qm = "datawidget/datawidget.qt.qm"
    # By default, it is loading from the app directory (or the working dir) if it is relative.   
    ret = trans.load(QLocale.system(), qm)
    if ret is False:
        print("Failed to load the qm file")
    app.installTranslator(trans)

    window = datawidget.DataWidget()
    window.show()
    sys.exit(app.exec_())
