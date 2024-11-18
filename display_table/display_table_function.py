# -*- coding: utf-8 -*-
import time
import difflib

import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QMessageBox, QFileDialog
from .display_table_UI import Ui_MainWindow as Ui_Form


class function_realization(QtWidgets.QMainWindow, Ui_Form):

    def __init__(self, window):
        super(function_realization, self).__init__()
        self.setWindowIcon(QIcon("./shell.jpg"))
        self.model = None
        self.main_windows = window
        self.table_work = None
        self.save_table_data_type = ''
        self.setupUi(self)
        #  表格初始化
        self.init_table()
        #  表格数据初始化
        self.table_data_electricity = []
        self.table_header_electricity = []
        self.table_data_temp_electricity = []
        self.table_header_figure = []
        self.table_data_figure = []
        self.table_data_temp_figure = []
        self.order_data = []
        #  表格数据刷新线程初始化
        self.table_thread()
        self.pushbutton2display_table()
        self.pushButton_3.clicked.connect(self.calcuate_orderAndstandby_loss)
        self.pushButton_4.clicked.connect(self.read_order_files)
        self.pushButton_5.clicked.connect(self.export_electric_degree)

    def pushbutton2display_table(self):
        self.pushButton.clicked.connect(self.display_electricity_table)
        self.pushButton_2.clicked.connect(self.display_figure_table)

    def display_electricity_table(self):
        self.displayTable(self.table_data_electricity, self.table_header_electricity)
        print("[INFO ] 电量数据表格显示按钮触发")
        self.displayMesg("刷新成功")
        self.save_table_data_type = 'electricity_data'

    def display_figure_table(self):
        self.displayTable(self.table_data_figure, self.table_header_figure)
        print("[INFO ] 图分析数据表格显示按钮触发")
        self.displayMesg("刷新成功")
        self.save_table_data_type = 'figure_data'

    def write_new(self, data, header):
        if len(data) == 0:
            self.displayMesg('未进行电量查询操作')
        else:
            # file_name = QFileDialog.getOpenFileName(self, "open file dialog", "C:\Users\Administrator\Desktop",
            #                                        "Excel files(*.xlsx);;Excel files(*.xls);;Excel files(*.csv)")
            ##"open file Dialog "为文件对话框的标题，第三个是打开的默认路径，第四个是文件类型过滤器,file_name-绝对路径
            file_path = QFileDialog.getSaveFileName(self, "save file", r"C:\Users\Administrator\Desktop",
                                                    "Excel files(*.xlsx);;Excel files(*.xls);;Excel files(*.csv)")

            if file_path == ('', ''):
                pass
            elif file_path != '':
                try:
                    dt = pd.DataFrame(data)
                    dt.columns = header
                    pd.DataFrame.to_excel(dt, file_path[0], index=False)
                except Exception as e:
                    self.displayMesg('文件已打开,请关闭后再进行导出' + str(e))
                else:
                    pass

    def export_electric_degree(self):
        if self.save_table_data_type == 'electricity_data':
            data = self.table_data_electricity
            print('[INFO] 开始写入', data)
            self.write_new(data, self.table_header_electricity)
        elif self.save_table_data_type == 'figure_data':
            data = self.table_data_figure
            print('[INFO] 开始写入', data)
            self.write_new(data, self.table_header_figure)
        #  网关编号——[站点编号，场站名称]字典映射

    def export_order_loss(self, data):
        export_data = []
        for i in self.order_data.loc[:, ['ERP名称', '总充电量']].values:
            export_data.append([])
            export_data[-1].append(i[0])  # 添加站点名称
            export_data[-1].append(i[1])  # 添加平台电量
            export_data[-1].append('')  # 添加购电量
            export_data[-1].append('')  # 添加电损
            if "玖隆大厦二期" not in i[0]:
                combination_data = 0
                for name, value in data.items():
                    if self.caculate_str_similar(i[0], name)[0]:
                        combination_data += value
                    else:
                        pass
                if combination_data != 0:
                    export_data[-1][-2] = combination_data
                    export_data[-1][-1] = round((combination_data - i[1])/ combination_data, 5)
                else:
                    pass
            else:
                pass

        return export_data

    def calcuate_orderAndstandby_loss(self):
        if self.load_order_data():
            if len(self.table_data_electricity) != 0:
                order_loss = {}
                for row in range(self.tableView.model().rowCount()):
                    print([self.model.index(row, i).data() for i in range(12)])
                    if (float(self.model.index(row, 3).data()) != 0) and float(
                            self.model.index(row, 10).data()) != 0:
                        orderAndstandby_loss = (float(self.model.index(row, 3).data()) - float(
                            self.model.index(row, 10).data())) / float(self.model.index(row, 3).data())
                        order_loss[self.model.index(row, 0).data()] = float(self.model.index(row, 3).data())
                        # 添加损耗数据
                        item = QStandardItem()
                        item.setEditable(False)
                        item.setData(round(orderAndstandby_loss * 100, 2),
                                     QtCore.Qt.DisplayRole)  # 将number_data替换为数值即可
                        self.model.setItem(row, 11, item)
                        self.table_data_electricity[row][11] = round(orderAndstandby_loss * 100, 2)
                        self.table_data_electricity[row][10] = float(self.model.index(row, 10).data())
                    else:
                        pass
                self.displayMesg('电量损耗计算完成, 请选择保存路径')
                header = ['ERP名称', '总充电量', "购电量", "电损"]
                self.write_new(self.export_order_loss(order_loss), header)

            else:
                self.displayMesg("未进行电量数据查询操作")
        else:
            pass

    def init_table(self):
        self.model = QStandardItemModel()  # 创建存储数据的模式
        # 根据空间自动改变列宽度并且不可修改列宽度
        # self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表头可见
        self.tableView.horizontalHeader().setVisible(True)
        # 纵向表头可见
        self.tableView.verticalHeader().setVisible(True)
        # 设置表格内容文字大小
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tableView.setFont(font)
        # 设置表格内容不可编辑
        self.tableView.setEditTriggers(QAbstractItemView.AllEditTriggers)
        # 垂直滚动条始终开启
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def displayTable(self, data, table_header):
        self.model.clear()
        for index_row, value_row in enumerate(data):
            for index_column, value_column in enumerate(table_header):
                # 添加表格内容
                if isinstance(data[index_row][index_column], str):
                    # 向表格存储模式中添加表格具体信息
                    item = QStandardItem(data[index_row][index_column])
                    item.setEditable(False)
                    # 添加提示框：用于显示较长的站点名称字符串
                    if ":" not in data[index_row][index_column]:
                        item.setToolTip(data[index_row][index_column])
                    self.model.setItem(index_row, index_column, item)

                elif isinstance(data[index_row][index_column], float) or isinstance(data[index_row][index_column], int):
                    item = QStandardItem()
                    item.setEditable(False)
                    # if index_column == 10:
                    #     item.setEditable(True)
                    # else:
                    #     item.setEditable(False)
                    item.setData(data[index_row][index_column], QtCore.Qt.DisplayRole)  # 将number_data替换为数值即可
                    # 向表格存储模式中添加表格具体信息
                    self.model.setItem(index_row, index_column, item)

        # 设置表格存储数据的模式
        font = self.tableView.horizontalHeader().font()  # 获取当前表头的字体
        font.setFamily("微软雅黑")  # 修改字体设置
        self.tableView.horizontalHeader().setFont(font)  # 重新设置表头的字体
        self.tableView.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:#efefef;}")
        # 水平方向，表格大小拓展到适当的尺寸
        self.tableView.horizontalHeader().setStretchLastSection(True)
        # 水平方向，表格列宽均等划分
        # self.window.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置表格内容点击可排序
        self.tableView.setSortingEnabled(True)
        # self.window.tableView.resizeColumnToContents(0)
        self.tableView.setModel(self.model)
        # 设置表格列宽宽度
        for i in range(len(table_header)):
            self.tableView.horizontalHeader().resizeSection(i, 200)
        self.model.setHorizontalHeaderLabels(table_header)

    def displayMesg(self, mseg):
        result = QMessageBox.information(self, "Notice", mseg,
                                         QMessageBox.StandardButtons(QMessageBox.Ok))
        if result == QMessageBox.Ok:
            pass

    def caculate_str_similar(self, object_str, match_str):
        if difflib.SequenceMatcher(None, object_str, match_str).quick_ratio() > 0.9:
            return True, difflib.SequenceMatcher(None, object_str, match_str).quick_ratio()
        else:
            return False, difflib.SequenceMatcher(None, object_str, match_str).quick_ratio()

    def read_order_files(self):
        file_path = QFileDialog.getOpenFileName(self, "open file", r"C:\Users\Administrator\Desktop",
                                                "Excel files(*.xlsx);;Excel files(*.xls);;Excel files(*.csv)")
        if file_path == ('', ''):
            self.order_data = []
            self.displayMesg('未导入订单数据')
        elif file_path != '':
            try:
                data = pd.read_excel(file_path[0])
                assert list(data.columns) == ['ERP名称', '总充电量'], "导入订单格式不匹配，请确认表头内容仅包含'ERP名称'和'总充电量'，其中,ERP名称列为具体的场站名称"
            except Exception as e:
                print('[INFO ] 文件读取失败,' + str(e))
                self.displayMesg(str(e))
                self.order_data = []
            else:
                self.order_data = data
                self.displayMesg('订单数据导入成功！')
                #print('[INFO ] 订单数据,' + str(self.order_data))

    def load_order_data(self):
        self.pushButton.setChecked(True)
        time.sleep(1)
        if isinstance(self.order_data, list):
            self.displayMesg('未导入订单数据')
            return False
        else:
            data_obj = self.order_data.loc[:, ['ERP名称', '总充电量']].values
            if len(self.table_data_electricity) != 0:
                for row in range(self.tableView.model().rowCount()):
                    for i in data_obj:
                        if self.caculate_str_similar(self.model.index(row, 0).data(),
                                                i[0].replace('轻客', '').replace('轻卡', '').replace('可充', ''))[0] or \
                                (self.model.index(row, 0).data() == '所有场站' and i[0] == '---'):
                            # 添加订单数据
                            item = QStandardItem()
                            item.setEditable(False)
                            item.setData(round(i[1], 2), QtCore.Qt.DisplayRole)  # 将number_data替换为数值即可
                            self.model.setItem(row, 10, item)
                            break
                        else:
                            continue
                return True
            else:
                self.displayMesg("未进行电量数据查询操作")
                return False

    def refush_table(self, str):
        if self.table_data_electricity != self.table_data_temp_electricity:
            print('[INFO] 检测到电量表格数据变化，开始刷新表格')
            try:
                self.displayTable(self.table_data_electricity, self.table_header_electricity)
                print('[INFO] 表格刷新已完成')
            except Exception as e:
                self.displayMesg('[INFO] 电量数据表格刷新失败' + str(e))
                print('[INFO] 表格刷新失败', str(e))
            finally:
                self.table_data_temp_electricity = self.table_data_electricity[:]
        elif self.table_data_figure != self.table_data_temp_figure:
            print('[INFO] 检测到图分析数据变化，开始刷新表格')
            try:
                print('[INFO] 图分析数据', self.table_header_figure)
                self.displayTable(self.table_data_figure, self.table_header_figure)
                print('[INFO] 图分析数据刷新已完成')
            except Exception as e:
                self.displayMesg('[INFO] 图分析数据表格刷新失败' + str(e))
                print('[INFO] 表格刷新失败', str(e))
            finally:
                self.table_data_temp_figure = self.table_data_figure[:]
        else:
            pass

    def table_thread(self):
        self.table_work = WorkThread()
        self.table_work.progressValue.connect(self.refush_table)
        self.table_work.start()


class WorkThread(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    progressValue = pyqtSignal(str)

    def __int__(self):
        # 初始化函数
        super(WorkThread, self).__init__()

    def run(self):
        while True:
            self.progressValue.emit('continue')
            # print('[INFO] 表格数据刷新线程运行中……')
            time.sleep(1)


def caculate_str_similar(object_str, match_str):
    # print(object_str, match_str, difflib.SequenceMatcher(None, object_str, match_str).quick_ratio())
    if difflib.SequenceMatcher(None, object_str, match_str).quick_ratio() > 0.9:
        return True, difflib.SequenceMatcher(None, object_str, match_str).quick_ratio()
    else:
        return False, 0

