from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSlider, QGroupBox, QLabel, QLineEdit, QDial
from PySide2.QtGui import QBitmap, QPixmap, QPolygon, QPainter, QColor, QPen, QFont
from PySide2.QtCore import QRect, QPoint, QSize, QTimer, Qt, QRectF, QPoint

from threading import Timer
import random
import math

M_PI = 3.1415926

window = None

class GaugeCar(QWidget):

    PieStyle_Three = 0,         	#三色圆环
    PieStyle_Current = 1        	#当前圆环

    PointerStyle_Circle = 0,        #圆形指示器
    PointerStyle_Indicator = 1,     #指针指示器
    PointerStyle_IndicatorR = 2,    #圆角指针指示器
    PointerStyle_Triangle = 3       #三角形指示器


    minValue=0.0                #最小值
    maxValue=120.0                #最大值
    value = 30                   #目标值
    precision = 0                  #精确度,小数点后几位

    scaleMajor = 12                 #大刻度数量
    scaleMinor = 60                #小刻度数量
    startAngle = 30                 #开始旋转角度
    endAngle = 30                  #结束旋转角度

    animation = False                 #是否启用动画显示
    animationStep = 1           #动画显示时步长

    outerCircleColor = QColor(127, 127, 127, 127)        #外圆背景颜色
    innerCircleColor = QColor(0, 0, 0, 200)       #内圆背景颜色

    pieColorStart  = QColor(0, 255, 0, 127)         #饼圆开始颜色
    pieColorMid  =  QColor(0, 255, 0, 127)          #饼圆中间颜色
    pieColorEnd = QColor(0, 255, 0, 127)            #饼圆结束颜色

    coverCircleColor = QColor(0, 0, 255, 127)       #覆盖圆背景颜色
    scaleColor = QColor(255, 255, 255, 127)             #刻度尺颜色
    pointerColor = QColor(255, 255, 255, 127)           #指针颜色
    centerCircleColor = QColor(0, 0, 255, 127)      #中心圆颜色
    textColor = QColor(255, 255, 255, 127)              #文字颜色

    showOverlay = False               #显示遮罩层
    overlayColor = QColor(0, 0, 255, 127)           #遮罩层颜色

    pieStyle = 1             #饼图样式
    pointerStyle = 1     #指针样式

    reverse = False                   #是否往回走
    currentValue = 20.0            #当前值
    timer  = None                #定时器绘制动画
    
    def __init__(self, parent=None):
        super(GaugeCar, self).__init__(parent)
        self.setMinimumSize(200, 200)

    def setCurrentValue(self, value):
        self.currentValue = value
        self.update()


    def paintEvent(self, event):
        width = self.width()
        height = self.height()
        side = min(width, height)

        #绘制准备工作,启用反锯齿,平移坐标轴中心,等比例缩放
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        painter.translate(width / 2, height / 2)
        painter.scale(side / 200.0, side / 200.0)

        #绘制外圆
        self.drawOuterCircle(painter)
        #绘制内圆
        self.drawInnerCircle(painter)
        #绘制饼圆
        self.drawColorPie(painter)
        #绘制覆盖圆 用以遮住饼圆多余部分
        self.drawCoverCircle(painter)
        #绘制刻度线
        self.drawScale(painter)
        #绘制刻度值
        self.drawScaleNum(painter)

        #根据指示器形状绘制指示器
        if self.pointerStyle == self.PointerStyle_Circle:
            self.drawPointerCircle(painter)
        elif self.pointerStyle == self.PointerStyle_Indicator:
            self.drawPointerIndicator(painter)
        elif self.pointerStyle == self.PointerStyle_IndicatorR:
            self.drawPointerIndicatorR(painter)
        elif self.pointerStyle == self.PointerStyle_Triangle:
            self.drawPointerTriangle(painter)

        #绘制指针中心圆外边框
        self.drawRoundCircle(painter)
        #绘制指针中心圆
        self.drawCenterCircle(painter)
        #绘制当前值
        self.drawValue(painter)
        #绘制遮罩层
        self.drawOverlay(painter)

        self.drawPointerIndicator(painter)

    def drawOuterCircle(self, painter):
        radius = 99
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.outerCircleColor)
        painter.drawEllipse(-radius, -radius, radius * 2, radius * 2)
        painter.restore()

    def drawInnerCircle(self, painter):
        radius = 90
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.innerCircleColor)
        painter.drawEllipse(-radius, -radius, radius * 2, radius * 2)
        painter.restore()

    def drawColorPie(self, painter):
        radius = 60
        painter.save()
        painter.setPen(Qt.NoPen)

        rect = QRect(-radius, -radius, radius * 2, radius * 2)

        if self.pieStyle == self.PieStyle_Three:
            #计算总范围角度,根据占比例自动计算三色圆环范围角度
            #可以更改比例
            angleAll = 360.0 - self.startAngle - self.endAngle
            angleStart = angleAll * 0.7
            angleMid = angleAll * 0.15
            angleEnd = angleAll * 0.15

            #增加偏移量使得看起来没有脱节
            offset = 3

            #绘制开始饼圆
            painter.setBrush(self.pieColorStart)
            painter.drawPie(rect, (270 - self.startAngle - angleStart) * 16, angleStart * 16)

            #绘制中间饼圆
            painter.setBrush(self.pieColorMid)
            painter.drawPie(rect, (270 - self.startAngle - angleStart - angleMid) * 16 + offset, angleMid * 16)

            #绘制结束饼圆
            painter.setBrush(self.pieColorEnd)
            painter.drawPie(rect, (270 - self.startAngle - angleStart - angleMid - angleEnd) * 16 + offset * 2, angleEnd * 16)
        elif self.pieStyle == self.PieStyle_Current:
            #计算总范围角度,当前值范围角度,剩余值范围角度
            angleAll = 360.0 - self.startAngle - self.endAngle
            angleCurrent = angleAll * ((self.currentValue - self.minValue) / (self.maxValue - self.minValue))
            angleOther = angleAll - angleCurrent

            #绘制当前值饼圆
            painter.setBrush(self.pieColorStart)
            painter.drawPie(rect, (270 - self.startAngle - angleCurrent) * 16, angleCurrent * 16)

            #绘制剩余值饼圆
            painter.setBrush(self.pieColorEnd)
            painter.drawPie(rect, (270 - self.startAngle - angleCurrent - angleOther) * 16, angleOther * 16)
        
        painter.restore()

    def drawCoverCircle(self, painter):
        radius = 50
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.coverCircleColor)
        painter.drawEllipse(-radius, -radius, radius * 2, radius * 2)
        painter.restore()

    def drawScale(self, painter):
        radius = 72
        painter.save()

        painter.rotate(self.startAngle)
        steps = (self.scaleMajor * self.scaleMinor)
        angleStep = (360.0 - self.startAngle - self.endAngle) / steps

        pen = QPen()
        pen.setColor(self.scaleColor)
        pen.setCapStyle(Qt.RoundCap)

        # for (i = 0 i <= steps i++) 
        for i in range(steps):
            if i % self.scaleMinor == 0:
                pen.setWidthF(1.5)
                painter.setPen(pen)
                painter.drawLine(0, radius - 10, 0, radius)
            else:
                pen.setWidthF(0.5)
                painter.setPen(pen)
                painter.drawLine(0, radius - 5, 0, radius)

            painter.rotate(angleStep)

        painter.restore()

    def drawScaleNum(self, painter):

        radius = 82
        painter.save()
        painter.setPen(self.scaleColor)

        startRad = (360 - self.startAngle - 90) * (M_PI / 180)
        deltaRad = (360 - self.startAngle - self.endAngle) * (M_PI / 180) / self.scaleMajor

        # for (i = 0 i <= scaleMajor i++) 
        for i in range(self.scaleMajor):
            sina = math.sin(startRad - i * deltaRad)
            cosa = math.cos(startRad - i * deltaRad)
            value = 1.0 * i * ((self.maxValue - self.minValue) / self.scaleMajor) + self.minValue

            # strValue = QString("%1").arg(float(value), 0, 'f', precision)
            strValue = str(int(value))
            textWidth = self.fontMetrics().width(strValue)
            textHeight = self.fontMetrics().height()
            x = radius * cosa - textWidth / 2
            y = -radius * sina + textHeight / 4
            painter.drawText(x, y, strValue)
        

        painter.restore()


    def drawPointerCircle(self, painter):
        radius = 6
        offset = 30
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(pointerColor)

        painter.rotate(startAngle)
        degRotate = (360.0 - startAngle - endAngle) / (maxValue - minValue) * (currentValue - minValue)
        painter.rotate(degRotate)
        painter.drawEllipse(-radius, radius + offset, radius * 2, radius * 2)

        painter.restore()


    def drawPointerIndicator(self, painter):
        radius = 75
        painter.save()
        painter.setOpacity(0.8)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.pointerColor)

        pts = QPolygon()
        # pts.setPoints(3, -5, 0, 5, 0, 0, radius)
        pts.append(QPoint(-5, 0))
        pts.append(QPoint(5, 0))
        pts.append(QPoint(0, radius))
        # pts.append(radius)
        painter.rotate(self.startAngle)
        degRotate = (360.0 - self.startAngle - self.endAngle) / (self.maxValue - self.minValue) * (self.currentValue - self.minValue)
        painter.rotate(degRotate)
        painter.drawConvexPolygon(pts)

        painter.restore()

    def drawPointerIndicatorR(self, painter):
        radius = 75
        painter.save()
        painter.setOpacity(1.0)

        pen = QPen() 
        pen.setWidth(1)
        pen.setColor(pointerColor)
        painter.setPen(pen)
        painter.setBrush(pointerColor)

        pts = QPolygon()
        pts.setPoints(3, -5, 0, 5, 0, 0, radius)

        painter.rotate(startAngle)
        degRotate = (360.0 - startAngle - endAngle) / (maxValue - minValue) * (currentValue - minValue)
        painter.rotate(degRotate)
        painter.drawConvexPolygon(pts)

        #增加绘制圆角直线,与之前三角形重叠,形成圆角指针
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidthF(4)
        painter.setPen(pen)
        painter.drawLine(0, 0, 0, radius)

        painter.restore()

    def drawPointerTriangle(self, painter):
        radius = 10
        offset = 38
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.pointerColor)

        pts = QPolygon()
        pts.setPoints(3, -5, 0 + offset, 5, 0 + offset, 0, radius + offset)

        painter.rotate(self.startAngle)
        degRotate = (360.0 - self.startAngle - self.endAngle) / (self.maxValue - self.minValue) * (self.currentValue - self.minValue)
        painter.rotate(degRotate)
        painter.drawConvexPolygon(pts)

        painter.restore()

    def drawRoundCircle(self, painter):
        radius = 18
        painter.save()
        painter.setOpacity(0.8)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.pointerColor)
        painter.drawEllipse(-radius, -radius, radius * 2, radius * 2)
        painter.restore()

    def drawCenterCircle(self, painter):
        radius = 15
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.centerCircleColor)
        painter.drawEllipse(-radius, -radius, radius * 2, radius * 2)
        painter.restore()            

    
    def drawValue(self, painter):

        radius = 100
        painter.save()
        painter.setPen(self.textColor)

        font = QFont()
        font.setPixelSize(18)
        painter.setFont(font)

        textRect= QRectF(-radius, -radius, radius * 2, radius * 2)
        # strValue = QString("%1").arg(float(currentValue), 0, 'f', precision)
        strValue = str(int(self.currentValue))
        print(strValue)
        painter.drawText(textRect, Qt.AlignCenter, strValue)

        painter.restore()


    def drawOverlay(self, painter):

        if not self.showOverlay:
            return
        

        radius = 90
        painter.save()
        painter.setPen(Qt.NoPen)

        smallCircle = QPainterPath()
        bigCircleQPainterPath()
        radius -= 1
        smallCircle.addEllipse(-radius, -radius, radius * 2, radius * 2)
        radius *= 2
        bigCircle.addEllipse(-radius, -radius + 140, radius * 2, radius * 2)

        #高光的形状为小圆扣掉大圆的部分
        highlight = smallCircle - bigCircle

        linearGradient = QLinearGradient(0, -radius / 2, 0, 0)
        overlayColor.setAlpha(100)
        linearGradient.setColorAt(0.0, overlayColor)
        overlayColor.setAlpha(30)
        linearGradient.setColorAt(1.0, overlayColor)
        painter.setBrush(linearGradient)
        painter.rotate(-20)
        painter.drawPath(highlight)

        painter.restore()

def changevalue():
    # global window
    window.setCurrentValue(random.choice(range(100)))
    Timer(10.0, changevalue).start()



if __name__ == '__main__':
    # client = HDFSFileSystem("192.168.2.21", "root", "wim123")
    # client.refresh()
    # client2 = HDFSFileSystem("192.168.2.21", "root", "wim123")

    # tdir = HDFSDir("/nfs")
    # print(tdir.get_childs())
    import sys
    from PySide2.QtWidgets import QApplication
    app = QApplication(sys.argv)
 
    # model = TreeModel(tdir.get_dict())
    # global window
    window = GaugeCar()
    window.show()
    # Timer(10.0, changevalue).start()

    sys.exit(app.exec_())
      