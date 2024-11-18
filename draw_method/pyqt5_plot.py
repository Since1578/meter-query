# -*- coding: utf-8 -*-
"""
@Time ： 2023/3/14 11:44
@Auth ： DingKun
@File ：pyqt5_plot.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import sys

import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtChart import QBarSet, QBarSeries, QChart, QChartView, QValueAxis, QBarCategoryAxis, \
    QHorizontalBarSeries, QAbstractBarSeries, QLineSeries, QScatterSeries
from PyQt5.QtWidgets import QGraphicsSimpleTextItem
from PyQt5.QtCore import QPointF


class display_text(QGraphicsSimpleTextItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_point = QPointF()

    def setPoint(self, point1):
        self.m_point = point1

    def getPoint(self):
        return self.m_point


class MyChartView(QChartView):
    def __init__(self, chart, text_label=None, text_xy_point=None):
        super().__init__(chart)
        self.text_label = text_label
        self.text_xy_point = text_xy_point
        self.chart = chart

    def init_point_Item(self):
        #  构造指定数目的QGraphicsSimpleTextItem用于显示文本
        self.point_Item = [QGraphicsSimpleTextItem(self.chart) for i in range(len(self.text_label))]

    def init_text_display(self):
        # print("self.text_label", self.text_label)
        for index, label_point in enumerate(zip(self.text_label, self.text_xy_point)):
            #  字体设置
            self.point_Item[index].setFont(QFont("黑体", 8))
            if '-' in label_point[0]:
                self.point_Item[index].setBrush(QColor(77, 214, 12))
            else:
                self.point_Item[index].setBrush(QColor(244, 51, 8))
            self.point_Item[index].setText(label_point[0])
            #  坐标由视图转换为场景坐标
            start_ = QPointF(label_point[1][0], label_point[1][1])
            start = self.chart.mapToPosition(start_)
            width = self.point_Item[index].boundingRect().width()
            self.point_Item[index].setPos(start.x() - width / 2, start.y())
            #  控件调整至最前面，防止被遮挡
            self.point_Item[index].setZValue(100)

    # 重写鼠标事件，用于更新文本位置
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.text_label is not None:
            self.init_text_display()


class MyBarWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, title_name=None, is_lable=False):
        super(MyBarWindow, self).__init__(parent)
        self.setMinimumWidth(100)
        self.setMinimumHeight(100)
        # self.setStyleSheet("background-color: rgba(0, 0, 0)")
        self.title_name = title_name
        self.is_lable = is_lable
        self.init_chart()

    # def paintEvent(self, event):
    #     opt = QtWidgets.QStyleOption()
    #     opt.initFrom(self)
    #     painter = QtGui.QPainter(self)
    #     style = self.style()
    #     style.drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, painter, self)

    #  重写鼠标事件，当窗口大小发生变化时，更换title文本位置
    def resizeEvent(self, event):
        if hasattr(self, "qwiget_title"):
            self.qwiget_title.move(event.size().width() / 2.3, 15)
        else:
            pass

    # include "qgraphicsitem.h"
    # include <QPointF>

    def init_chart(self):
        #  创建图
        if self.is_lable:
            """"""
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.vbox = QGridLayout()
            self.qwiget = QWidget()
            # self.chartView.setRenderHint(QPainter.Antialiasing)
            # # vbox = QGridLayout()
            # # vbox.addWidget(self.chartView)
            # self.chartView.setStyleSheet(
            #     'background-color: rgba(255, 255, 255, 0.1)')
            # self.chartView.setStyleSheet(
            #     'border: 1px solid rgba(255, 255, 255, 0);background-color: rgba(255, 255, 255, 0.1);border-radius:15px')
            self.setStyleSheet('background-color: rgba(255, 255, 255, 0.1);border-radius:1px')
            self.qwiget.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.qwiget.setMinimumSize(self.width(), self.height())
            self.qwiget_title = QLabel(self.qwiget)
            self.qwiget_title.setStyleSheet("color:rgb(110, 255, 207);font: 75 15pt \"Times New "
                                            "Roman\";font: 14pt \"黑体\"")
            self.qwiget_title.setText(self.title_name)
            self.qwiget_title.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.qwiget_title.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            self.qwiget_title.move(int(self.width() // 2.3), 15)
            # qwiget_title.setBaseSize(self.qwiget.width(), self.qwiget.height())
            self.qwiget.setLayout(self.vbox)
            self.setCentralWidget(self.qwiget)
        else:
            self.chart = QChart()
            #  创建X、Y轴
            self.axisX = QBarCategoryAxis()
            self.axisY = QValueAxis()
            # self.axisY.setRange(0, 1000)
            #  设置图具有动画过度属性
            self.chart.setAnimationOptions(QChart.AllAnimations)
            #  设置图表动画的擦除曲线
            self.chart.setAnimationEasingCurve(QEasingCurve.OutBack)
            #  设置图表背景为透明
            self.chart.setBackgroundVisible(False)
            #  字体样式
            # font = QFont()  # 实例化字体对象
            # font.setFamily('微软雅黑')  # 字体
            # font.setPointSize(15)  # 字体大小
            font = QFont()
            font.setPointSize(14)
            # font.setBold(True)
            font.setFamily('黑体')
            if self.title_name is not False:
                self.chart.setTitle(self.title_name)
                self.chart.setTitleFont(font)
            #  设置表头字体颜色
            self.chart.setTitleBrush(QColor(110, 255, 207))
            #  设置x轴横线不可见
            self.axisX.setGridLineVisible(False)
            #  设置图表内外留白
            self.chart.setMargins(QMargins(-10, -10, -10, -10))
            self.chart.setContentsMargins(0, 0, 0, 0)
            #  设置图例不可见
            self.chart.legend().setVisible(False)
            self.chart.setFont(font)
            #  设置指定图例不可见
            # legendMarkers = chart.legend().markers()
            # for legend in legendMarkers:
            #     legend.setVisible(False)
            #  设置表头字体样式
            self.chart.setTitleFont(font)
            self.chart.setZValue(0)
            self.chartView = MyChartView(self.chart)
            self.chartView.setChart(self.chart)
            self.chartView.setRenderHint(QPainter.Antialiasing)
            # vbox = QGridLayout()
            # vbox.addWidget(self.chartView)
            self.chartView.setStyleSheet(
                'border: 1px solid rgba(255, 255, 255, 0);background-color: rgba(255, 255, 255, 0.1);border-radius:15px')
            self.setCentralWidget(self.chartView)

    def plot_lineAndBar(self, datas, meter_type=None):
        #  创建柱状图柱体
        font = QFont()
        # font.setBold(True)
        font.setFamily('黑体')
        if meter_type == '24h':
            qtbar_set = QBarSet('昨日所有场站24h汇总电量')
            bar_data = [value for key, value in datas[0].items()]
            line_data = [value for key, value in datas[1].items()]
            font.setPointSize(12)
        else:
            font.setPointSize(12)
            bar_data = datas[0]
            line_data = datas[1]
            qtbar_set = QBarSet('上周所有场站每日汇总电量')
        for data in bar_data:
            qtbar_set.append(data)
        #  创建柱状图Series
        qt_bar_series = QBarSeries()
        qt_bar_series.append(qtbar_set)
        #  创建曲线Series
        qt_line_series = QLineSeries()
        # qt_line_series.setPen(QPen(QColor(45, 74, 247)))
        if meter_type == '24h':
            qt_line_series.setName('今日所有场站24h汇总电量')
            value_max_line = max(value for index, value in enumerate(line_data))
            value_max_bar = max(value for index, value in enumerate(bar_data))
            value_max = max(value_max_bar, value_max_line)
            change_xy_point = [[index, value + value_max/8] for index, value in enumerate(line_data)]

        else:
            qt_line_series.setName('本周所有场站每日汇总电量')
            value_max_line = max(value for index, value in enumerate(line_data))
            value_max_bar = max(value for index, value in enumerate(bar_data))
            value_max = max(value_max_bar, value_max_line)
            change_xy_point = [[index, value + value_max/7] for index, value in enumerate(line_data)]
        for index, value in enumerate(line_data):
            qt_line_series.append(index, value)
        #  QScatterSeries标记点序列设置
        change_trend = [str(round((line_ - bar_) / bar_ * 100, 1)) + '%' if bar_ != 0 and line_ != 0 else ' ' for
                        line_, bar_ in
                        zip(line_data, bar_data)]
        scatterSeries = QScatterSeries()
        scatterSeries.setName('标记点')
        scatterSeries.setPointLabelsFormat("@yPoint")  # 折线图标记点只显示y值
        scatterSeries.setPointsVisible(True)
        scatterSeries.setPointLabelsVisible(True)
        scatterSeries.setMarkerShape(QScatterSeries.MarkerShapeCircle)
        scatterSeries.setMarkerSize(6)
        # scatterSeries.setPointLabelsFont(font)
        for index, value in enumerate(line_data):
            scatterSeries.append(QPointF(index, int(value)))
        scatterSeries.setPointLabelsColor(Qt.white)
        #  Series 添加到chart
        self.chart.addSeries(qt_bar_series)
        self.chart.addSeries(qt_line_series)
        self.chart.addSeries(scatterSeries)
        #  设置坐标轴
        if meter_type == '24h':
            for i in range(24):
                if i < 10:
                    label = '0' + str(i)  # + ':00'
                else:
                    label = str(i)  # + ":00"
                self.axisX.append(label)
        else:
            for i in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']:
                self.axisX.append(i)
        self.chart.setAxisX(self.axisX, qt_bar_series)
        self.chart.setAxisX(self.axisX, qt_line_series)
        self.chart.setAxisX(self.axisX, scatterSeries)
        if meter_type == '24h':
            self.axisX.setLabelsFont(QFont("mm"))
            # self.axisX.setLabelsAngle(45)
        self.axisX.setLabelsColor(Qt.white)
        self.axisX.setLabelsFont(font)
        self.chart.setAxisY(self.axisY, qt_bar_series)
        self.chart.setAxisY(self.axisY, qt_line_series)
        self.chart.setAxisY(self.axisY, scatterSeries)
        self.axisY.setLabelsColor(Qt.white)
        max_value = max(line_data + bar_data)
        if meter_type == '24h':
            self.axisY.setRange(0, max_value + 1000)
        else:
            self.axisY.setRange(0, max_value + 30000)
        self.axisY.setLabelsFont(font)
        #  设置图例
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self.chart.legend().markers()[-1].setVisible(False)
        self.chart.legend().setFont(font)
        self.chart.legend().setLabelColor(Qt.white)
        self.chartView.text_label = change_trend
        self.chartView.text_xy_point = change_xy_point
        self.chartView.init_point_Item()
        self.chartView.init_text_display()
        # self.chart.legend().setAlignment(Qt.AlignTop)
        #  添加chart到视图

    def plot_topN(self, labels, datas):
        # set0 = QBarSet("站点1")  # 添加图例，每一个图例代表一簇柱状图
        # labels, datas = ['12', '13'], [12, 13]
        datas = np.array(datas)
        self.barSeries = QHorizontalBarSeries()  # 横向柱状图
        font = QFont()  # 实例化字体对象
        font.setFamily('黑体')  # 字体
        font.setPointSize(14)  # 字体大小
        # font.setBold(True)  # 加粗
        set0 = QBarSet("label")  # 添加图例，每一个图例代表一簇柱状图
        set0.setLabelFont(font)
        for label, data in zip(labels, datas):
            # 添加单个图例中的柱状图
            set0.append(data)
            self.axisX.append(label)
        self.barSeries.append(set0)
        self.chart.addSeries(self.barSeries)
        self.axisX.setGridLineVisible(False)
        self.axisX.setLabelsColor(Qt.white)
        self.axisX.setLineVisible(False)
        font = QFont()  # 实例化字体对象
        font.setFamily('黑体')  # 字体
        font.setPointSize(12)  # 字体大小
        self.axisX.setLabelsFont(font)
        self.axisX.setGridLineVisible(False)
        #  不显示刻度线
        # self.axisX.setVisible(False)
        self.chart.setAxisY(self.axisX)
        self.barSeries.attachAxis(self.axisX)
        self.barSeries.setLabelsPosition(QAbstractBarSeries.LabelsInsideEnd)  # LabelsOutsideEnd
        self.barSeries.setLabelsVisible(True)
        # self.barSeries.setBarWidth(0.1)
        # 初始化图属性

    def plot_tongbi(self, last_day, last_week, last_month):
        """"""
        # label
        label_day = QtWidgets.QLabel()
        label_day.setStyleSheet("QLabel{""background-image:url(last_day.png);"
                                "background-position:center;"
                                "background-repeat:none;color: rgb(1, 255, 255);font: 75 15pt \"Times New "
                                "Roman\";font: 10pt \"黑体\";"
                                "}")
        label_day.setAlignment(Qt.AlignCenter)
        if last_day[1] != '-':
            label_day.setText(
                '\n' + '\n' + str(last_day[0]) + ' kW/h' + '\n' + '环比增加：' + str(round(last_day[1] * 100, 1)) + '%')
        else:
            # label_4.setScaledContents(True)
            label_day.setText('\n' + '\n' + str(last_day[0]) + ' kW/h' + '\n' + '环比增加：' + '-')

        label_week = QtWidgets.QLabel()
        label_week.setStyleSheet("QLabel{""background-image:url(last_week.png);"
                                 "background-position:center;"
                                 "background-repeat:none;color: rgb(1, 255, 255);font: 75 15pt \"Times New "
                                 "Roman\";font: 10pt \"黑体\";"
                                 "}")
        label_week.setAlignment(Qt.AlignCenter)
        if last_week[1] != '-':
            label_week.setText(
                '\n' + '\n' + str(last_week[0]) + ' kW/h' + '\n' + '环比增加：' + str(round(last_week[1] * 100, 1)) + '%')
        else:
            label_week.setText('\n' + '\n' + str(last_week[0]) + ' kW/h' + '\n' + '环比增加：' + '-')

        label_month = QtWidgets.QLabel()
        label_month.setStyleSheet("QLabel{""background-image:url(last_month.png);"
                                  "background-position:center;"
                                  "background-repeat:none;color: rgb(1, 255, 255);font: 75 15pt \"Times New "
                                  "Roman\";font: 10pt \"黑体\";"
                                  "}")
        label_month.setAlignment(Qt.AlignCenter)
        if last_month[1] != '-':
            label_month.setText(
                '\n' + '\n' + str(last_month[0]) + ' kW/h' + '\n' + '环比增加：' + str(round(last_month[1] * 100, 1)) + '%')
        else:
            label_month.setText('\n' + '\n' + str(last_month[0]) + ' kW/h' + '\n' + '环比增加：' + '-')

        self.vbox.addWidget(label_day, 0, 0, 1, 1)
        self.vbox.addWidget(label_week, 0, 1, 1, 1)
        self.vbox.addWidget(label_month, 0, 2, 1, 1)
        self.vbox.setSpacing(0)
        # self.chartView.setLayout(vbox)
        # self.setCentralWidget(self.chartView)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    labels, datas = ['112', '13', '14', '15', '1112', '113', '114', '115', '13', '14', '15', '11112', '1113', '1114',
                     '1115'], [121, 111, 121, 111, 111, 121, 111, 111, 111, 121, 111, 111, 121, 111, 111]
    data = [{'00:00': 54611.1100000001024, '01:00': 328.7500000002037, '02:00': 246.08999999955995,
             '03:00': 10711.78000000026077, '04:00': 164.01000000003842, '05:00': 183.95999999987544,
             '06:00': 238.9299999999057, '07:00': 100.67000000012922, '08:00': 470.7699999999022,
             '09:00': 493.8299999999872, '10:00': 699.5299999999697, '11:00': 621.6900000000023,
             '12:00': 350.00000000034925, '13:00': 546.1100000001024, '14:00': 328.7500000002037,
             '15:00': 246.08999999955995,
             '16:00': 107.78000000026077, '17:00': 164.01000000003842, '18:00': 183.95999999987544,
             '19:00': 238.9299999999057, '20:00': 100.67000000012922, '21:00': 470.7699999999022,
             '22:00': 493.8299999999872, '23:00': 699.5299999999697},
            {'00:00': 546.1100000001024, '01:00': 328.7500000002037, '02:00': 246.08999999955995,
             '03:00': 107.78000000026077, '04:00': 164.01000000003842, '05:00': 183.95999999987544,
             '06:00': 238.9299999999057, '07:00': 10011.67000000012922, '08:00': 470.7699999999022,
             '09:00': 493.8299999999872, '10:00': 699.5299999999697, '11:00': 621.6900000000023,
             '12:00': 350.00000000034925, '13:00': 546.1100000001024, '14:00': 328.7500000002037,
             '15:00': 246.08999999955995,
             '16:00': 107.78000000026077, '17:00': 164.01000000003842, '18:00': 183.95999999987544,
             '19:00': 238.9299999999057, '20:00': 100.67000000012922, '21:00': 470.7699999999022,
             '22:00': 493.8299999999872, '23:00': 699.5299999999697}]
    win = MyBarWindow(is_lable=False, title_name='电量趋势')
    # win.plot_topN(labels, datas)
    win.plot_lineAndBar(data, meter_type='24h')
    win.chartView.setStyleSheet(
        'border: 1px solid rgb(3, 11, 30);background-color: rgb(3, 11, 30);border-radius:15px')
    # win.plot_tongbi(1, 2, 3)
    win.show()
    sys.exit(app.exec_())
