from PyQt5 import QtCore
from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QDialog, QGridLayout
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarCategoryAxis, QStackedBarSeries, QValueAxis, QPieSeries
from PyQt5.QtGui import QIcon, QFont

class QchartPlot(QDialog):
    def __init__(self, window):
        super().__init__()
        self.window = window
        # window requirements
        self.setGeometry(200, 200, 600, 400)
        self.setWindowIcon(QIcon("python.png"))
        # change the color of the window
        self.setStyleSheet('background-color:gray')
        self.setWindowFlags(QtCore.Qt.Window)
    def plotQBarSet(self):
        # create barseries
        self.setWindowTitle("站点用电量详情")
        self.setFont(QFont('微软雅黑', 12))
        set0 = QBarSet("峰时电量")
        set1 = QBarSet("平时电量")
        set2 = QBarSet("谷时电量")
        #position, TroughElectric,BopingElectric, PeakElectric
        # insert data to the barseries
        categories = []
        #print(self.window.show_figure_data)
        for val in self.window.show_figure_data:
            position, TroughElectric, BopingElectric, PeakElectric = val[0], val[1], val[2], val[3]
            set0.append(PeakElectric)
            set1.append(BopingElectric)
            set2.append(TroughElectric)
            categories.append(position)

        # we want to create percent bar series
        series = QStackedBarSeries()
        series.append(set0)
        series.append(set1)
        series.append(set2)

        # create chart and add the series in the chart
        chart = QChart()
        chart.addSeries(series)
        chart.setBackgroundVisible(False)
        chart.setTitle("站点用电量详情(kW/h)")
        chart.setTitleFont(QFont('微软雅黑', 13))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeDark)
        chart.legend().setFont(QFont('微软雅黑', 10))  # 图例字体
        # 设置横向坐标(X轴)
        ax_X = QBarCategoryAxis()
        ax_X.append(categories)
        ax_X.setLabelsAngle(60)
        #ax_X.setLabelsFont(45)
        ax_X.setLabelsFont(QFont("微软雅黑", 8))
        chart.setAxisX(ax_X, series)
        # chart.addAxis(ax_X, Qt.AlignBottom)
        # series.attachAxis(ax_X)
        # 设置纵向坐标(Y轴)
        ax_Y = QValueAxis()
        ax_Y.setLabelFormat("%d")
        chart.setAxisY(ax_Y, series)
        chart.adjustSize()
        chart.setMargins(QMargins(0.005, 5, 0.005, 0.005))
        #QMargins(intleft, int top, intright, intbottom)
        # chart.addAxis(ax_Y, Qt.AlignLeft)
        # series.attachAxis(ax_Y)
        #chart.createDefaultAxes()
        #chart.setAxisX(axis, series)
        # create chartview and add the chart in the chartview
        chartview = QChartView(chart)

        vbox = QGridLayout()
        vbox.addWidget(chartview)
        self.setLayout(vbox)

    def plotQPieSeries(self):
        self.setWindowTitle("站点用电量汇总")
        self.setFont(QFont('微软雅黑', 12))
        TroughProportion, BopingProportion, PeakProportion = self.window.show_table_data[0][4], self.window.show_table_data[0][5], self.window.show_table_data[0][6]
        print(TroughProportion, BopingProportion, PeakProportion)
        #TroughElectric, BopingElectric, PeakElectric = self.window.show_table_data[0][3] * float(TroughProportion[:-1]), self.window.show_table_data[0][3] * float(BopingProportion[:-1]), self.window.show_table_data[0][3] * float(PeakProportion[:-1])
        #设置饼图数据
        #print(float(PeakProportion[:-1]), float(BopingProportion[:-1]), float(TroughProportion[:-1]))
        pieSeries = QPieSeries()
        pieSeries.setHoleSize(0)
        #
        pieSlice1 = pieSeries.append('峰时占比:' + PeakProportion, float(PeakProportion[:-1]))  # 图列添加
        #pieSlice1.setExploded()
        pieSlice1.setLabelVisible()
        #
        pieSlice2 = pieSeries.append('平时占比:' + BopingProportion, float(BopingProportion[:-1]))  # 图列添加
        #pieSlice2.setExploded()
        pieSlice2.setLabelVisible()
        #
        pieSlice3 = pieSeries.append('谷时占比:' + TroughProportion, float(TroughProportion[:-1]))  # 图列添加
        #pieSlice3.setExploded()
        pieSlice3.setLabelVisible()
        #pieSeries.setLabelsPosition(QPieSlice.LabelInsideHorizontal)
        #图表视图
        #
        chart = QChart()
        chart.addSeries(pieSeries)
        chart.setBackgroundVisible(False)
        chart.setTitle('站点用电量汇总')
        chart.setTitleFont(QFont('微软雅黑', 10))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTheme(QChart.ChartThemeBlueIcy)
        chart.adjustSize()
        chart.setMargins(QMargins(0.005, 5, 0.005, 0.005))
        chart.legend().setFont(QFont('微软雅黑', 10))# 图例字体
        chartview = QChartView(chart)

        vbox = QGridLayout()
        vbox.addWidget(chartview)
        self.setLayout(vbox)
        #
        # chartView = QChartView()
        #
        # chartView.setRenderHint(QPainter.Antialiasing)
        # chartView.chart().setBackgroundVisible(False)
        # chartView.chart().setTitle('站点用电量汇总')
        # chartView.chart().addSeries(pieSeries)
        # chartView.chart().legend().setAlignment(Qt.AlignBottom)
        # #chartView.chart().legend().setAlignment()
        # chartView.chart().setTheme(QChart.ChartThemeBlueNcs)
        # chartView.chart().legend().setFont(QFont('微软雅黑', 12))# 图例字体
        # #chartView.chart().setFont(QFont('微软雅黑', 15))
        # vbox = QGridLayout()
        # vbox.addWidget(chartView)
        # self.setLayout(vbox)