from PySide2.QtCore import QPropertyAnimation, QRectF, QSize, Qt, Property
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import (
    QAbstractButton,
    QApplication,
    QHBoxLayout,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox
)

from initwidget.reportwidget import ReportWidget
from initwidget.gendocx import GenReport

from util.wimlog import error,info, debug
from util.database import add_report

class MeterReport(QWidget):
    """
    仪表报表控件
    """
    def __init__(self):
        super(MeterReport, self).__init__()

        main_hbox = QHBoxLayout()

        table_vbox = QVBoxLayout()
        self.report_widget = ReportWidget()
        txt_label = QLabel(u"仪表评估报表")
        table_vbox.addWidget(txt_label)
        table_vbox.addWidget(self.report_widget)

        # 按钮
        vbox = QVBoxLayout()
        para_but = QPushButton(u"参数更新并启动")
        para_gen = QPushButton(u"生成报表")
        para_open = QPushButton(u"打开报表")
        vbox.addWidget(para_but)
        vbox.addStretch(1)
        vbox.addWidget(para_gen)
        vbox.addWidget(para_open)
        main_hbox.addLayout(table_vbox)
        main_hbox.addLayout(vbox)
        self.setLayout(main_hbox)

        para_gen.clicked.connect(self._gen_report)
        

    def _gen_report(self):
        info("gent report")
        gen = GenReport()
        filename = gen.gen_report()
        msgBox =  QMessageBox()
      
        if len(filename) == 0:
            error("Gen doc failed")
            msgBox.setText(u"初始化报告生成失败.")
        else:
            msgBox.setText(u"文档生成成功")
            add_report(u"初始化报表", filename)
        msgBox.exec()
        self.report_widget.refreshtable()
