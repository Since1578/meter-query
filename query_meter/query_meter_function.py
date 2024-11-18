# -*- coding: utf-8 -*-
import copy
import datetime
import difflib

import time

import numpy as np
import paramiko
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QStandardItem, QIcon
from PyQt5.QtWidgets import QMessageBox, QProgressBar
from sql_operation.login_mysql import connectMysql, isConnected
from sql_operation.operation_mysql import query_meter, query_pile_usage, query_power_factor, query_cables_temp
from qt_module.qComboCheckBox import QComboCheckBox
from draw_method.matplotlib_draw import MainWindow
from base_model.statistic_time import calculate_pile_usage_times, stastic_diffTime_electricity
from .query_meter_UI import Ui_Form


class function_realization(QtWidgets.QMainWindow, Ui_Form):
    def __init__(self, main_window, table_window, time_window):
        # 初始化载入json内容
        super(function_realization, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("./shell.jpg"))
        self.query_type = ''
        self.Begin_datetime = ''
        self.End_datetime = ''
        self.window = main_window
        self.show_table_data = []
        self.show_figure_data = []
        self.query_flag = 0
        self.no_price = ''
        self.gun_nums_list = {}
        self.table_window = table_window
        self.time_window = time_window
        self.setFixedSize(self.width(), self.height())
        self.pushButton.clicked.connect(self.read_electric)
        self.init_progressbar()
        # self.progressBar_plot = self.init_progressbar_plot()
        self.Is_displayProgressbar('n')
        # 查询日期初始化
        self.dateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dateTimeEdit_2.setDateTime(QtCore.QDateTime.currentDateTime())
        # 区域、站点选择控件初始化
        self.box_name = []
        self.all_list = [[], [], []]
        self.init_combocheckbox()
        self.city_combocheckbox.activated.connect(self.city2region)
        self.region_combocheckbox.activated.connect(self.region2position)
        #  查询类型选择框初始化
        # 潮汐图可视化按钮绑定触发事件
        self.select_menu_layer_meter_total()  # 按钮添加菜单栏
        self.select_menu_layer_meter_use()
        self.select_menu_layer_single_pile_use()
        self.select_menu_layer_single_gun_use()
        self.pushButton_2.clicked.connect(self.display_meter_total_figure)
        self.pushButton_3.clicked.connect(self.display_meter_single_pile_figure)
        self.pushButton_5.clicked.connect(self.display_meter_total_use_figure)
        self.pushButton_4.clicked.connect(self.display_pile_usage_figure)
        self.pushButton_7.clicked.connect(self.display_meter_single_pile_use_figure)
        # self.pushButton_8.clicked.connect(self.display_power_factor)
        self.pushButton_9.clicked.connect(self.display_cables_temp)
        self.pushButton_10.clicked.connect(self.display_meter_single_gun_use_figure)
        self.pushButton_11.clicked.connect(self.display_difftime_meter)

    def display_difftime_meter(self):
        if self.query_type == 'meter':
            electricity_times = sum([len(value) for key, value in self.time_window.electricity_times.items()])
            if electricity_times != 0:
                meter_data = self.show_figure_data
                # meter_data=[{'position_name':[{'strong_meter':,'weak_meter':,'times':,'pile1_meter':,'pile2_meter':, pilen_meter]}]
                data_temp = []
                for data in meter_data:
                    temp = []
                    for position_name, meter in data.items():
                        for index, value in enumerate(meter):
                            meter_temp = [0, '']
                            for key, value_dict in value.items():
                                if 'strong' in key:
                                    meter_temp[0] += value_dict
                                if 'weak' in key:
                                    meter_temp[0] += value_dict
                                if 'time' in key:
                                    meter_temp[1] = value_dict
                            temp.append(meter_temp)
                        # temp.append([[i['strong_meter'], i['time']] for i in meter])
                        temp.insert(0, position_name)
                    data_temp.append(temp)
                #  只显示被选中的站点电量趋势图
                selected_position = self.position_combocheckbox.get_clickedcontent()
                data_temp = [i for i in data_temp if (i[0] in selected_position) and (len(i[1]) != 0)]
                #  判断电量数据是否为有效数据
                if len(data_temp):
                    t1 = time.time()
                    stastic_class = stastic_diffTime_electricity()
                    stastic_class.judge_time_type(data_temp, self.time_window.electricity_times)
                    print('[INFO] 分时时段划分耗时：', time.time() - t1)
                    print(stastic_class.time2electricity_dict)
                    t2 = time.time()
                    time_total = stastic_class.caculate_diffTime_electricity()
                    print('[INFO] 分时时段统计耗时：', time.time() - t2)
                    mainwindow = MainWindow(time_total, plot_type="difftime_electricity")
                    mainwindow.show_figure([])
                    self.table_window.table_data_figure = copy.deepcopy(mainwindow.table_data)
                    self.table_window.table_header_figure = copy.deepcopy(mainwindow.table_header)
                    self.table_window.save_table_data_type = 'figure_data'
                    mainwindow.exec()
                else:
                    self.displayMesg('已选择的站点未查询到电量数据')
            else:
                self.displayMesg('未进行分时时段设置！')
        else:
            self.displayMesg('已选场站未进行电量查询操作')

    def display_cables_temp(self):
        if self.query_type == 'cables_temp':
            meter_data = self.show_figure_data
            data_temp = []
            for data in meter_data:
                temp = []
                for position_name, meter in data.items():
                    for index, object_meter in enumerate(meter):
                        power_factor_value = [value for key, value in object_meter.items() if
                                              "temp" in key or "time" in key]
                        temp.append(power_factor_value)
                        if index == len(meter) - 1:
                            temp.insert(0, position_name)
                    data_temp.append(temp)
            selected_position = self.position_combocheckbox.get_clickedcontent()
            data = [i for index, i in enumerate(data_temp) if (i[0] in selected_position) and len(i[1]) != 0]
            if len(selected_position) == 1:
                if len(data) != 0:
                    mainwindow = MainWindow(data, plot_type='total_cables_temp')
                    mainwindow.show_figure([])
                    mainwindow.exec()
                else:
                    self.displayMesg('已选场站未查询到线缆温度数据')
            #  只显示被选中的站点电量趋势图
            else:
                self.displayMesg('请选择查询结果的一个站点进行操作')
        else:
            self.displayMesg('已选场站未进行场站线缆温度查询操作')

    def display_power_factor(self):
        if self.query_type == 'power_factor':
            meter_data = self.show_figure_data
            # print("[INFO] meter_data", meter_data)
            data_temp = []
            for data in meter_data:
                temp = []
                for position_name, meter in data.items():
                    for index, object_meter in enumerate(meter):
                        power_factor_value = [value for key, value in object_meter.items() if
                                              "power" in key or "time" in key]
                        temp.append(power_factor_value)
                        if index == len(meter) - 1:
                            temp.insert(0, position_name)
                    data_temp.append(temp)
            selected_position = self.position_combocheckbox.get_clickedcontent()
            data = [i for index, i in enumerate(data_temp) if (i[0] in selected_position) and len(i[1]) != 0]
            if len(selected_position) == 1:
                if len(data) != 0:
                    mainwindow = MainWindow(data, plot_type='total_power_factor')
                    mainwindow.show_figure([])
                    mainwindow.exec()
                else:
                    self.displayMesg('已选场站未查询到功率因素数据')
            #  只显示被选中的站点电量趋势图
            else:
                self.displayMesg('请选择查询结果的一个站点进行操作')
        else:
            self.displayMesg('已选场站未进行功率因素查询操作')

    def display_pile_usage_figure(self):
        if self.query_type == 'usage':
            selected_position = self.position_combocheckbox.get_clickedcontent()
            if len(selected_position) == 1:
                #  只显示被选中的站点电量趋势图
                meter_data = self.show_figure_data
                pile_time_usage = calculate_pile_usage_times(Begin_datetime=self.Begin_datetime,
                                                             End_datetime=self.End_datetime)
                time_usage = pile_time_usage.statistic_use_time(meter_data)
                pile_time_usage_temp = []
                for key, values in time_usage.items():
                    if key in selected_position:
                        pile_time_usage_temp.insert(0, key)
                        pile_time_usage_temp.insert(1, values)
                if len(pile_time_usage_temp):
                    mainwindow = MainWindow(pile_time_usage_temp, plot_type='usage_single_pile')
                    mainwindow.show_figure([])
                    mainwindow.exec()
                else:
                    self.displayMesg('已选场站未查询到单桩电量数据')
            else:
                self.displayMesg('请选择查询结果的一个站点进行操作')
        else:
            self.displayMesg('已选场站未进行使用率查询操作')

    def display_meter_single_pile_figure(self):
        if self.query_type == 'meter':
            meter_data = self.show_figure_data
            data_temp = []
            for data in meter_data:
                temp = []
                for position_name, meter in data.items():
                    # print("data", meter)
                    for index, object_meter in enumerate(meter):
                        key_list = list(object_meter.keys())
                        is_contain_pile_str = [i for i in key_list if "pile" in i]
                        if len(is_contain_pile_str) != 0:
                            pile_meter_list = [value for key, value in object_meter.items() if
                                               ('pile' in key) or ('time' in key)]
                            temp.append(pile_meter_list)
                            # print("pile_meter_list", pile_meter_list)
                            if index == len(meter) - 1:
                                temp.insert(0, position_name)
                        else:
                            temp.append([])
                            temp.insert(0, position_name)
                            break
                data_temp.append(temp)
                #     temp.append(
                #        [[value for key, value in i.items() if ('pile' in key) or ('time' in key)] for i in meter])
                #     temp[0].insert(0, position_name)
                # data_temp.append(temp[0])
            # print("data_temp", data_temp)
            #  只显示被选中的站点电量趋势图
            selected_position = self.position_combocheckbox.get_clickedcontent()
            # data_temp = [i for index, i in enumerate(data_temp) if (i[0] in selected_position) and len(i[1]) != 0]
            if len(selected_position) == 1:
                data = [i for index, i in enumerate(data_temp) if (i[0] in selected_position) and len(i[1]) != 0]
                # data = [i for i in data_temp if i[0] in selected_position]
                if len(data):
                    mainwindow = MainWindow(data, plot_type='single_pile_tidal')
                    mainwindow.show_figure([])
                    mainwindow.exec()
                else:
                    self.displayMesg('已选场站未查询到单桩电量数据')
            else:
                self.displayMesg('请选择查询结果的一个站点进行操作')
        else:
            self.displayMesg('已选场站未进行电量查询操作')

    def display_meter_single_pile_use_figure(self, menu_selected):
        if self.query_type == 'meter':
            time_interval = {'每小时': "hour", '每天': "day", '每月': "month", '每年': "year"}
            selected_interval_type = time_interval[menu_selected[1]]
            meter_data = self.show_figure_data
            data_temp = []
            for data in meter_data:
                temp = []
                for position_name, meter in data.items():
                    # print("data", meter)
                    for index, object_meter in enumerate(meter):
                        key_list = list(object_meter.keys())
                        is_contain_pile_str = [i for i in key_list if "pile" in i]
                        if len(is_contain_pile_str) != 0:
                            pile_meter_list = [value for key, value in object_meter.items() if
                                               ('pile' in key) or ('time' in key)]
                            temp.append(pile_meter_list)
                            # print("pile_meter_list", pile_meter_list)
                            if index == len(meter) - 1:
                                temp.insert(0, position_name)
                        else:
                            temp.append([])
                            temp.insert(0, position_name)
                            break
                data_temp.append(temp)
            selected_position = self.position_combocheckbox.get_clickedcontent()
            # data_temp = [i for index, i in enumerate(data_temp) if (i[0] in selected_position) and len(i[1]) != 0]
            if len(selected_position) == 1:
                data = [i for index, i in enumerate(data_temp) if (i[0] in selected_position) and len(i[1]) != 0]
                # data = [i for i in data_temp if i[0] in selected_position]
                if len(data):
                    mainwindow = MainWindow(data, plot_type='single_pile_use_tidal',
                                            time_interval=selected_interval_type)
                    mainwindow.show_figure([])
                    mainwindow.exec()
                else:
                    self.displayMesg('已选场站未查询到单桩电量数据')
            else:
                self.displayMesg('请选择查询结果的一个站点进行操作')
        else:
            self.displayMesg('已选场站未进行电量查询操作')

    def display_meter_single_gun_use_figure(self, menu_selected):
        if self.query_type == 'meter':
            time_interval = {'每小时': "hour", '每天': "day", '每月': "month", '每年': "year"}
            selected_interval_type = time_interval[menu_selected[1]]
            meter_data = self.show_figure_data
            gun_nums_list = self.gun_nums_list
            data_temp = []
            for data in meter_data:
                temp = []
                for position_name, meter in data.items():
                    # print("data", meter)
                    for index, object_meter in enumerate(meter):
                        key_list = list(object_meter.keys())
                        is_contain_pile_str = [i for i in key_list if "strong" in i]
                        if len(is_contain_pile_str) != 0:
                            pile_meter_list = [value for key, value in object_meter.items() if
                                               ('strong' in key) or ('time' in key)]
                            temp.append(pile_meter_list)
                            # print("pile_meter_list", pile_meter_list)
                            if index == len(meter) - 1:
                                temp.insert(0, position_name)
                        else:
                            temp.append([])
                            temp.insert(0, position_name)
                            break
                data_temp.append(temp)
            selected_position = self.position_combocheckbox.get_clickedcontent()
            data_temp = [i for i in data_temp if (i[0] in selected_position) and (len(i[1]) != 0)]
            # ('data_temp', data_temp)
            #  判断电量数据是否为有效数据
            if len(selected_position) == 1:
                if len(data_temp) != 0:
                    mainwindow = MainWindow(data_temp, time_interval=selected_interval_type,
                                            plot_type='single_gun_use_tidal')
                    mainwindow.show_figure(gun_nums_list)
                    self.table_window.table_data_figure = copy.deepcopy(mainwindow.table_data)
                    self.table_window.table_header_figure = copy.deepcopy(mainwindow.table_header)
                    self.table_window.save_table_data_type = 'figure_data'
                    mainwindow.exec()
                else:
                    self.displayMesg('已选择的站点未查询到单枪电量数据')
            else:
                self.displayMesg('请选择查询结果的一个站点进行操作')
        else:
            self.displayMesg('已选场站未进行电量查询操作')

    def display_meter_total_use_figure(self, menu_selected):
        if self.query_type == 'meter':
            type_meter = {'经营性用电': 'strong', '非经营性用电': 'weak'}
            time_interval = {'每小时': "hour", '每天': "day", '每月': "month", '每年': "year"}
            selected_meter_type = type_meter[menu_selected[0]]
            selected_interval_type = time_interval[menu_selected[1]]
            meter_data = self.show_figure_data  # meter_data=[{'position_name':[{'strong_meter':,'weak_meter':,'times':,'pile1_meter':,'pile2_meter':, pilen_meter]}]
            data_temp = []
            for data in meter_data:
                temp = []
                for position_name, meter in data.items():
                    temp.append([[i['strong_meter'], i['weak_meter'], i['time']] for i in meter])
                    temp[0].insert(0, position_name)
                data_temp.append(temp[0])
            # print('data_temp', data_temp)
            #  只显示被选中的站点电量趋势图
            selected_position = self.position_combocheckbox.get_clickedcontent()
            data_temp = [i for i in data_temp if (i[0] in selected_position) and (len(i[1]) != 0)]
            # print('data_temp', data_temp)
            #  判断电量数据是否为有效数据
            if len(data_temp):
                mainwindow = MainWindow(data_temp, meter_type=selected_meter_type, time_interval=selected_interval_type,
                                        plot_type='total_use_meter')
                mainwindow.show_figure([])
                self.table_window.table_data_figure = copy.deepcopy(mainwindow.table_data)
                self.table_window.table_header_figure = copy.deepcopy(mainwindow.table_header)
                self.table_window.save_table_data_type = 'figure_data'
                mainwindow.exec()

            else:
                self.displayMesg('已选择的站点未查询到电量数据')
        else:
            self.displayMesg('已选场站未进行电量查询操作')

    #
    def display_meter_total_figure(self, meter_type):
        if self.query_type == 'meter':
            type_list = {'经营性用电': 'strong', '非经营性用电': 'weak'}
            meter_data = self.show_figure_data  # meter_data=[{'position_name':[{'strong_meter':,'weak_meter':,'times':,'pile1_meter':,'pile2_meter':, pilen_meter]}]
            data_temp = []
            for data in meter_data:
                temp = []
                for position_name, meter in data.items():
                    temp.append([[i['strong_meter'], i['weak_meter'], i['time']] for i in meter])
                    temp[0].insert(0, position_name)
                data_temp.append(temp[0])
            # print('data_temp', data_temp)
            #  只显示被选中的站点电量趋势图
            selected_position = self.position_combocheckbox.get_clickedcontent()
            data_temp = [i for i in data_temp if (i[0] in selected_position) and (len(i[1]) != 0)]
            # print('data_temp', data_temp)
            #  判断电量数据是否为有效数据
            if len(data_temp):
                mainwindow = MainWindow(data_temp, meter_type=type_list[meter_type], plot_type='total_tidal_map')
                mainwindow.show_figure([])
                self.table_window.table_data_figure = copy.deepcopy(mainwindow.table_data)
                self.table_window.table_header_figure = copy.deepcopy(mainwindow.table_header)
                self.table_window.save_table_data_type = 'figure_data'
                mainwindow.exec()
            else:
                self.displayMesg('已选择的站点未查询到电量数据')
        else:
            self.displayMesg('已选场站未进行电量查询操作')

    def select_menu_layer_meter_total(self):
        menu = QtWidgets.QMenu(self)
        self.pushButton_2.setMenu(menu)
        layer_names = ['经营性用电', '非经营性用电']
        for i in layer_names:
            menu_name = QtWidgets.QAction(i, self)  #
            menu.addAction(menu_name)
        menu.triggered[QtWidgets.QAction].connect(self.processtrigger_class)

    def select_menu_layer_meter_use(self):
        menu = QtWidgets.QMenu(self)
        self.pushButton_5.setMenu(menu)
        layer2_names = ['每年', '每月', '每天', '每小时']
        menu1 = menu.addMenu('经营性用电')
        menu1.setObjectName('经营性用电')

        menu2 = menu.addMenu('非经营性用电')
        menu2.setObjectName('非经营性用电')
        for i in layer2_names:
            menu1.addAction(i)
            menu2.addAction(i)
        menu1.triggered[QtWidgets.QAction].connect(self.processtrigger_class_2)
        menu2.triggered[QtWidgets.QAction].connect(self.processtrigger_class_2)

    def select_menu_layer_single_pile_use(self):
        menu = QtWidgets.QMenu(self)
        self.pushButton_7.setMenu(menu)
        layer2_names = ['每年', '每月', '每天', '每小时']
        for i in layer2_names:
            menu_name = QtWidgets.QAction(i, self)  #
            menu.addAction(menu_name)
        menu.triggered[QtWidgets.QAction].connect(self.processtrigger_class_3)

    def select_menu_layer_single_gun_use(self):
        menu = QtWidgets.QMenu(self)
        self.pushButton_10.setMenu(menu)
        layer2_names = ['每年', '每月', '每天', '每小时']
        for i in layer2_names:
            menu_name = QtWidgets.QAction(i, self)  #
            menu.addAction(menu_name)
        menu.triggered[QtWidgets.QAction].connect(self.processtrigger_class_4)

    def processtrigger_class_4(self, q):
        # print('triggeres is :', q.text())
        sender_menu = self.sender().objectName()
        clicked_content = q.text()
        self.display_meter_single_gun_use_figure([sender_menu, clicked_content])

    def processtrigger_class_3(self, q):
        # print('triggeres is :', q.text())
        sender_menu = self.sender().objectName()
        clicked_content = q.text()
        self.display_meter_single_pile_use_figure([sender_menu, clicked_content])

    def processtrigger_class_2(self, q):
        # print('triggeres is :', q.text())
        sender_menu = self.sender().objectName()
        clicked_content = q.text()
        self.display_meter_total_use_figure([sender_menu, clicked_content])

    def processtrigger_class(self, q):
        # print('triggeres is :', q.text())
        self.display_meter_total_figure(q.text())

    def init_progressbar(self):
        self.progressBar = QProgressBar(self)
        self.progressBar.setStyleSheet(
            "QProgressBar {border-radius: 5px;   background-color: #FFFFFF;}QProgressBar::chunk {   background-color: #007FFF;   width: 10px;}QProgressBar {border-radius: 5px;   text-align: center;}")
        self.progressBar.setGeometry(QtCore.QRect(366, 110, 281, 33))

    def init_progressbar_plot(self):
        self.progressBar_plot = QProgressBar(self)
        self.progressBar_plot.setStyleSheet(
            "QProgressBar {border-radius: 5px;   background-color: #FFFFFF;}QProgressBar::chunk {   background-color: #007FFF;   width: 10px;}QProgressBar {border-radius: 5px;   text-align: center;}")
        self.progressBar_plot.setGeometry(QtCore.QRect(15, 260, 181, 41))
        return self.progressBar_plot

    def Is_displayProgressbar(self, display):
        if display == "n":
            #  电价参数配置事件进度条控件初始化
            self.progressBar_value = 0
            self.progressBar.setValue(self.progressBar_value)
            # 设置电价参数配置事件进度条控件透明度
            op = QtWidgets.QGraphicsOpacityEffect()
            op.setOpacity(0.01)
            self.progressBar.setGraphicsEffect(op)
            self.progressBar.setAutoFillBackground(True)
            self.progressBar.lower()
        elif display == "y":
            # 设置电价参数配置事件进度条控件透明度
            #  电价参数配置事件进度条控件初始化
            self.progressBar_value = 0
            self.progressBar.setValue(self.progressBar_value)
            # 设置电价参数配置事件进度条控件透明度
            op = QtWidgets.QGraphicsOpacityEffect()
            op.setOpacity(0.99)
            self.progressBar.setGraphicsEffect(op)
            self.progressBar.setAutoFillBackground(True)
            self.progressBar.raise_()

    def init_combocheckbox(self):
        #  下拉复选框初始化，固定位置
        self.box_name = []
        self.get_select_box_data(self.all_list)
        #  复选框初始化
        self.city_infos = self.all_list[0]
        self.region_infos = self.all_list[1]
        self.position_infos = self.all_list[2]

        self.city_combocheckbox = QComboCheckBox(self)
        self.city_combocheckbox.setGeometry(QtCore.QRect(103, 10, 251, 31))
        self.city_combocheckbox.add_items(self.city_infos)
        self.city_combocheckbox.select_reverse()
        self.box_name.append(self.city_combocheckbox)

        self.region_combocheckbox = QComboCheckBox(self)
        self.region_combocheckbox.setGeometry(QtCore.QRect(103, 60, 251, 31))
        self.region_combocheckbox.add_items(self.region_infos)
        self.region_combocheckbox.select_reverse()
        self.box_name.append(self.region_combocheckbox)

        self.position_combocheckbox = QComboCheckBox(self)
        self.position_combocheckbox.setGeometry(QtCore.QRect(103, 110, 251, 31))
        self.position_combocheckbox.add_items(self.position_infos)
        self.position_combocheckbox.select_reverse()
        self.box_name.append(self.position_combocheckbox)

    # 查询电量操作期间，使可视化展示功能按钮处于冻结状态
    def freeze_visual_presentation_button(self, freeze=False):
        if freeze:
            freeze = False
        else:
            freeze = True
        self.pushButton_2.setEnabled(freeze)
        self.pushButton_3.setEnabled(freeze)
        self.pushButton_4.setEnabled(freeze)
        self.pushButton_5.setEnabled(freeze)
        self.pushButton_7.setEnabled(freeze)
        # self.pushButton_8.setEnabled(freeze)
        self.pushButton_9.setEnabled(freeze)
        self.pushButton_10.setEnabled(freeze)
        self.pushButton_11.setEnabled(freeze)

    # 城市与区域信息进行绑定
    def city2region(self):
        city_content = self.city_combocheckbox.get_clickedcontent()  # 获取选择的区域子项内容
        # print("城市", city_content)
        region_content = []  # 所有年份子项对应的区域信息列表
        load_dict = self.window.region_relation_dict
        if city_content != []:  # 城市被选择，则将被选中城市对应区域列表覆盖初始化站点列表
            region_content.append('全部')
            for city in city_content:
                if city in load_dict['city']:
                    for region, val in load_dict['city'][city]['region'].items():
                        if region not in region_content:
                            region_content.append(region)
            self.region_combocheckbox.clear()
            self.region_combocheckbox.add_items(region_content)
            self.region2position()
        else:  # 城市未选择，则初始化年份
            self.region_infos.insert(0, '全选')
            self.region_combocheckbox.clear()
            self.region_combocheckbox.add_items(self.region_infos)
            # 复选框初始化
            self.region_combocheckbox.select_reverse()
            self.region_infos.remove('全选')
            self.region2position()

        #  区域与站点信息进行绑定

    def region2position(self):
        region_content = self.region_combocheckbox.get_clickedcontent()  # 获取选择的区域子项内容
        # print("区域", region_content)
        position_content = []  # 所有区域子项对应的站点信息列表
        load_dict = self.window.region_relation_dict
        if (region_content != []) and (
                self.city_combocheckbox.get_clickedcontent() != []):  # 区域被选择，则将被选中区域对应站点列表覆盖初始化站点列表
            position_content.append('全部')
            for city in self.city_combocheckbox.get_clickedcontent():
                for region in region_content:
                    if region in load_dict['city'][city]['region']:
                        for position, val in load_dict['city'][city]['region'][region]['position'].items():
                            if position not in position_content:
                                position_content.append(position)
            # print('选择的站点', position_content)
            self.position_combocheckbox.clear()
            # print('选择的站点', position_content)
            self.position_combocheckbox.add_items(position_content)
            # print("站点", position_content)

        else:  # 区域未选择，则初始化站点列表
            self.position_infos.insert(0, '全选')
            self.position_combocheckbox.clear()
            # print(self.position_infos)
            self.position_combocheckbox.add_items(self.position_infos)
            self.position_combocheckbox.select_reverse()
            self.position_infos.remove('全选')

    def obtain_begintime(self):
        Begin_datetime = self.dateTimeEdit.dateTime()
        Begin_datetime = Begin_datetime.toString("yyyy-MM-dd hh:mm:ss")
        datetime_format = datetime.datetime.strptime(Begin_datetime, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(
            seconds=10)
        # Begin_datetime = Begin_datetime[:-2] + '00'
        self.Begin_datetime = datetime.datetime.strftime(datetime_format, "%Y-%m-%d %H:%M:%S")
        print('[INFO] 查询开始时间:', self.Begin_datetime)

    def obtain_endtime(self):
        End_datetime = self.dateTimeEdit_2.dateTime()
        End_datetime = End_datetime.toString("yyyy-MM-dd hh:mm:ss")
        # End_datetime = End_datetime[:-2] + '00'
        datetime_format = datetime.datetime.strptime(End_datetime, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=10)
        self.End_datetime = datetime.datetime.strftime(datetime_format, "%Y-%m-%d %H:%M:%S")
        print('[INFO] 查询结束时间:', self.End_datetime)

    #  获得所有QBOX框被选中的子项
    def get_all_conditions(self):
        self.all_selected = []
        for i in self.box_name:
            i.get_clickedcontent()
            self.all_selected.append(i.get_clickedcontent())
        # print(self.all_selected)

        return self.all_selected

    def get_all_boxstatus(self, str):
        for i in self.box_name:
            pass
            # print('状态', i.get_boxstatus())

    def get_select_box_data(self, all_list):
        all_list[0], all_list[1], all_list[2] = [], [], []
        infos = self.window.region_relation_dict  # jsoninfo['年份']
        # all_list[0]为城市，all_list[1]为区域，all_list[2]为站点
        for city_keyname, content_city in infos.items():
            for city_name, content_region in content_city.items():
                if city_name not in all_list[0]:
                    all_list[0].append(city_name)
                for region_keyname, content_region in content_region.items():
                    for region_name, content_region in content_region.items():
                        if region_name not in all_list[1]:
                            all_list[1].append(region_name)
                        for position_keyname, content_position in content_region.items():
                            for position_name, content_position in content_position.items():
                                if position_name not in all_list[2]:
                                    all_list[2].append(position_name)

    def selected_query_type(self):
        # print(self.checkBox.checkState(), self.checkBox_2.checkState())
        checkBox_name_dice = {0: 'meter', 1: 'usage', 2: 'cables_temp'}
        checkBox_status = [self.checkBox.checkState(), self.checkBox_2.checkState(),
                           self.checkBox_4.checkState()]
        which_clicked = [index for index, value in enumerate(checkBox_status) if value == 2]
        print('[INFO] query type', which_clicked)
        if len(which_clicked) == 1:
            return checkBox_name_dice[which_clicked[0]]
        else:
            return None

    def read_electric(self):
        if isConnected() == True:
            self.obtain_endtime()
            self.obtain_begintime()
            self.query_type = self.selected_query_type()
            if self.query_type is not None:
                if datetime.datetime.strptime(self.Begin_datetime, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=10) < datetime.datetime.strptime(self.End_datetime, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(seconds=10):
                    all_selected_box = self.get_all_conditions()
                    is_selected = [len(i) for i in all_selected_box]
                    if (0 not in is_selected) or (0 == is_selected[0] and 0 == is_selected[1] and 0 != is_selected[2]):
                        if datetime.datetime.now().strftime('%M') in ['00', '10', '20', '30', '40', '50']:
                            self.displayMesg('本地端正在执行抄表，查询服务将有延迟，请稍等……')
                        print('[INFO] 开始查询……')
                        try:
                            self.Is_displayProgressbar('y')
                            # self.window.init_region_relation()
                            self.file_status(self.query_type)
                        except Exception as e:
                            print("[INFO] 查询异常", e)
                            mseg = "查询失败"
                            self.Is_displayProgressbar('n')
                            self.displayMesg(mseg)
                    elif 0 == is_selected[0]:
                        mseg = "城市未选择"
                        self.displayMesg(mseg)
                    elif 0 == is_selected[1]:
                        mseg = "区域未选择"
                        self.displayMesg(mseg)
                    elif 0 == is_selected[2]:
                        mseg = "站点未选择"
                        self.displayMesg(mseg)
                else:
                    self.displayMesg('时间设置错误')
            else:
                self.displayMesg('请选择一项查询类型')
        else:
            self.displayMesg('网络未连接')

    def downfile(self, filesname):
        transport = paramiko.Transport(('123.60.71.211', 22))
        transport.connect(username='root', password='yiweixny.666')

        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.get("/home/data/server/remotefolder/" + filesname, "cloudfiles/" + filesname,
                 callback=self.printTotals)  # 将Linux上的/root/Linux.txt下载到本地
        transport.close()

    def printTotals(self, transferred, toBeTransferred):
        # print(transferred / toBeTransferred)
        pass
        # self.progressBar.setValue(int(transferred / toBeTransferred * 100))

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

    def combination_split_position(self):
        if len(self.show_table_data) != 0:
            split_position = {}
            position_name_dict = {}  #
            for data in self.show_table_data:
                position_name_dict[data[0]] = data[:-2]
            position_name = list(position_name_dict.keys())
            for match_name in position_name:
                same_part_3_7 = []
                same_part_7_10 = []
                similar_name = []
                for position, value in position_name_dict:
                    if self.caculate_str_similar(value[0], match_name)[0]:
                        similar_name.append(value[0])
                        if value[3:7] not in same_part_3_7:
                            same_part_3_7.append(value[3:7])
                        if position_name_dict[match_name][3:7] not in same_part_3_7:
                            same_part_3_7.append(position_name_dict[match_name][3:7])
                        if value[7:10] not in same_part_7_10:
                            same_part_7_10.append(value[7:10])
                        if position_name_dict[match_name][7:10] not in same_part_7_10:
                            same_part_7_10.append(position_name_dict[match_name][7:10])
                    else:
                        pass
                if similar_name:
                    for name in similar_name:
                        del position_name_dict[name]

    def display_progress(self, num):
        self.progressBar.setValue(int((num + 1) / len(self.get_all_conditions()[2]) * 100))
        if (num == len(self.get_all_conditions()[2]) - 1) and (self.query_type == 'meter'):
            self.Is_displayProgressbar('n')
            self.show_table_data = self.work.show_table_data
            self.show_figure_data = self.work.show_figure_data
            self.gun_nums_list = self.work.gun_nums_list
            table_header = ['站点', '查询开始时间', '查询结束时间', '场站总用电量(kW·h)', '经营性用电量(kW·h)',
                            '非经营性用电量(kW·h)', '充电桩输出电量(kW·h)', "经营性用电量占比(%)"
                , "非经营性用电量占比(%)", '经营性用电量线损(%)', "平台订单电量(kW·h)", "线损+待机+异常订单损耗(%)"]
            # self.displayTable(self.work.show_table_data, table_header)
            self.table_window.table_header_electricity = table_header
            self.table_window.table_data_electricity = self.work.show_table_data
            self.table_window.save_table_data_type = 'electricity_data'
            mseg = "查询完毕！"
            # print(self.window.show_figure_data)
            self.displayMesg(mseg)
            #  Qbox框设置为可编辑状态
            self.city_combocheckbox.setEnabled(True)
            self.region_combocheckbox.setEnabled(True)
            self.position_combocheckbox.setEnabled(True)
            self.freeze_visual_presentation_button(freeze=False)
            self.query_flag = 1
            if self.work.no_data:
                self.displayMesg(str(self.work.no_data) + '无数据')
            print("[INFO] 查询结束")

        elif (num == len(self.get_all_conditions()[2]) - 1) and (self.query_type == 'usage'):
            self.Is_displayProgressbar('n')
            self.show_figure_data = self.work.show_figure_data
            self.gun_nums_list = self.work.gun_nums_list
            mseg = "查询完毕！"
            # print(self.window.show_figure_data)
            self.displayMesg(mseg)
            #  Qbox框设置为可编辑状态
            self.city_combocheckbox.setEnabled(True)
            self.region_combocheckbox.setEnabled(True)
            self.position_combocheckbox.setEnabled(True)
            self.freeze_visual_presentation_button(freeze=False)
            self.query_flag = 1
            if self.work.no_data:
                self.displayMesg(str(self.work.no_data) + '无数据')
            print("[INFO] 查询结束")

        elif (num == len(self.get_all_conditions()[2]) - 1) and (self.query_type == 'power_factor'):
            self.Is_displayProgressbar('n')
            self.show_figure_data = self.work.show_figure_data
            self.gun_nums_list = self.work.gun_nums_list
            mseg = "查询完毕！"
            # print(self.window.show_figure_data)
            self.displayMesg(mseg)
            #  Qbox框设置为可编辑状态
            self.city_combocheckbox.setEnabled(True)
            self.region_combocheckbox.setEnabled(True)
            self.position_combocheckbox.setEnabled(True)
            self.freeze_visual_presentation_button(freeze=False)
            self.query_flag = 1
            if self.work.no_data:
                self.displayMesg(str(self.work.no_data) + '无数据')
            print("[INFO] 查询结束")

        elif (num == len(self.get_all_conditions()[2]) - 1) and (self.query_type == 'cables_temp'):
            self.Is_displayProgressbar('n')
            self.show_figure_data = self.work.show_figure_data
            self.gun_nums_list = self.work.gun_nums_list
            mseg = "查询完毕！"
            # print(self.window.show_figure_data)
            self.displayMesg(mseg)
            #  Qbox框设置为可编辑状态
            self.city_combocheckbox.setEnabled(True)
            self.region_combocheckbox.setEnabled(True)
            self.position_combocheckbox.setEnabled(True)
            self.freeze_visual_presentation_button(freeze=False)
            self.query_flag = 1
            if self.work.no_data:
                self.displayMesg(str(self.work.no_data) + '无数据')
            print("[INFO] 查询结束")

    def return_position_code(self, selected_position):
        query_result = False
        for city_name, city_content in self.window.region_relation_dict['city'].items():
            for region_key, region_dict in city_content.items():
                for region_name, region_content in region_dict.items():
                    for position_key, position_dict in region_content.items():
                        for position_name, position_content in position_dict.items():
                            if position_name == selected_position:
                                query_result = position_content
        if query_result:
            return query_result
        else:
            return []

    def file_status(self, query_type):
        conn, cursor = connectMysql()
        try:
            assert conn != False, cursor
            print('[INFO] 数据库连接成功！')
            position_code = {}
            for selected_position in self.get_all_conditions()[2]:
                result = self.return_position_code(selected_position)
                if len(result):
                    position_code[selected_position] = result
            print('[INFO] 站点字典信息映射完成！')
            self.work = WorkThread()
            self.work.conn, self.work.cursor = conn, cursor
            self.work.num_process = position_code  # self.get_all_conditions()[2]
            self.work.Begin_datetime, self.work.End_datetime = self.Begin_datetime, self.End_datetime
            self.work.show_table_data = []
            self.work.no_data = []
            self.work.show_figure_data = []
            self.gun_nums_list = []
            self.work.infos = self.window.region_relation_dict
            self.work.progressBarValue.connect(self.display_progress)
            self.work.query_type = query_type
            self.work.start()
            self.city_combocheckbox.setEnabled(False)
            self.region_combocheckbox.setEnabled(False)
            self.position_combocheckbox.setEnabled(False)
            self.freeze_visual_presentation_button(freeze=True)
            print('[INFO] 开始启动查表线程！')
        except Exception as e:
            if conn != False:
                conn.close()
                cursor.close()
            print("[INFO] 数据库连接失败", e)
            self.Is_displayProgressbar('n')
            self.city_combocheckbox.setEnabled(True)
            self.region_combocheckbox.setEnabled(True)
            self.position_combocheckbox.setEnabled(True)
            self.freeze_visual_presentation_button(freeze=False)
            self.displayMesg('服务器连接超时，请重新操作')


class WorkThread(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    progressBarValue = pyqtSignal(int)
    num_process = []
    conn, cursor = None, None
    Begin_datetime, End_datetime = None, None
    no_data = []  # 无数据或仅有一条数据的场站
    show_table_data = []
    show_figure_data = []
    gun_nums_list = {}
    show_meter_level = {"SWPAC": [], "SWP": [], "SW": []}
    plot_figure = 0  # 是否满足画图条件， 0-满足，1-不满足
    infos = []
    query_type = ''

    def __int__(self):
        # 初始化函数
        super(WorkThread, self).__init__()

    def close_conn(self):
        if self.conn != False:
            self.cursor.close()
            self.conn.close()

    def query_fun(self, query_type):
        query_dict = {'usage': query_pile_usage, 'power_factor': query_power_factor, 'cables_temp': query_cables_temp,
                      'meter': query_meter}
        return query_dict[query_type]

    def run(self):
        print('[INFO] 需要查询：', len(self.num_process), '个场站数据')
        if len(self.num_process) != 0:
            for index, position_name in enumerate(self.num_process):
                try:
                    # 执行sql语句和实现事件
                    print('[INFO] 查询类型，', position_name, self.query_type)
                    data = self.query_fun(self.query_type)(self.cursor,
                                                           [position_name, self.num_process[position_name],
                                                            self.Begin_datetime,
                                                            self.End_datetime])
                    if self.query_type != 'meter':
                        if data == -1:
                            self.no_data.append(position_name)
                        else:
                            self.show_figure_data.append(data)
                    else:
                        data, meter_level, gun_nums = data[0], data[1], data[2]
                        if data == -1:
                            self.no_data.append(position_name)
                        else:
                            result = self.graded_statistics_electricity(data, meter_level)
                            if result == -1:
                                self.no_data.append(position_name)
                            else:
                                self.show_figure_data.append(data)
                                self.gun_nums_list[position_name] = gun_nums
                                # self.show_meter_level[meter_level].append(data)
                                self.once_caculate(position_name, result)
                        if index == len(self.num_process) - 1:
                            print('[INFO] 正在执行汇总操作……')
                            self.combin_caculate()
                            print('[INFO] 汇总操作执行完毕！')
                    self.progressBarValue.emit(index)  # 发送进度条的值信号
                except Exception as e:
                    print('[INFO] 查询异常：' + str(e), position_name)
                    # 发生异常所在的文件
                    print('[INFO] 查询异常', e.__traceback__.tb_frame.f_globals["__file__"])
                    # 发生异常所在的行数
                    print('[INFO] 查询异常', e.__traceback__.tb_lineno)
                    self.progressBarValue.emit(index)  # 发送进度条的值信号
                else:
                    continue
        self.close_conn()

    def once_caculate(self, position_name, result):
        total_meter, strong_meter, weak_meter, total_meter_use, strong_meter_use, weak_meter_use, pile_meter_use, L2_loss, order_meter, order_standby_loss, data_start_time, data_end_time = \
            result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], \
            result[8], result[9], result[10], result[11]
        self.show_table_data += [
            [position_name, data_start_time, data_end_time, round(total_meter_use, 3),
             round(strong_meter_use, 3), round(weak_meter_use, 3), round(pile_meter_use, 3),
             round((strong_meter_use / total_meter_use) * 100, 2),
             round((weak_meter_use / total_meter_use) * 100, 2),
             round(L2_loss * 100, 3), round(order_meter, 3),
             round(order_standby_loss, 3)]]

    def combin_caculate(self):
        all_total_meter, all_strong_meter, all_weak_meter, all_total_meter_use, all_strong_meter_use, all_weak_meter_use, all_pile_meter_use, all_jingying_proportion, all_feijingying_proportion, all_L2_loss, all_order_meter, all_order_standby_loss = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        effective_pile_meter_nums = 0
        effective_loss_nums = 0
        if len(self.show_table_data) != 0:
            for i in self.show_table_data:
                # all_total_meter += i[3]
                # all_strong_meter += i[4]
                # all_weak_meter += i[5]
                all_total_meter_use += i[3]
                all_strong_meter_use += i[4]
                all_weak_meter_use += i[5]
                all_feijingying_proportion += i[8]
                all_jingying_proportion += i[7]
                all_order_meter += i[10]
                all_order_standby_loss += i[11]
                if i[6] != 0:
                    effective_pile_meter_nums += 1
                    all_pile_meter_use += i[6]
                if i[9] != 0:
                    effective_loss_nums += 1
                    all_L2_loss += i[9]  # * i[4]
            #  避免除零
            if effective_loss_nums == 0:
                effective_loss_nums = 1
            if effective_pile_meter_nums == 0:
                effective_pile_meter_nums = 1

            self.show_table_data.insert(0, ['所有场站', self.Begin_datetime[:-3], self.End_datetime[:-3],
                                            round(all_total_meter_use, 3),
                                            round(all_strong_meter_use, 3),
                                            round(all_weak_meter_use, 3), round(all_pile_meter_use, 3),
                                            round(all_jingying_proportion / len(self.show_table_data),
                                                  3),
                                            round(all_feijingying_proportion / len(self.show_table_data), 3),
                                            round(all_L2_loss / effective_loss_nums, 3),
                                            round(all_order_meter, 3),
                                            round(all_order_standby_loss, 3)])
            print('[INFO] 汇总操作执行完毕', self.show_table_data, '\n', "effective_pile_meter_nums",
                  effective_pile_meter_nums, "effective_loss_nums", effective_loss_nums)

    def graded_statistics_electricity(self, meter_dict, meter_level):
        meter_list = list(meter_dict.values())[0]
        if len(meter_list) >= 2:
            data_start_time, data_end_time = str(meter_list[0]['time'])[:-3], str(meter_list[-1]['time'])[:-3]
            first_meter_strong = meter_list[0]["strong_meter"]
            last_meter_strong = meter_list[-1]["strong_meter"]
            first_meter_weak = meter_list[0]["weak_meter"]
            last_meter_weak = meter_list[-1]["weak_meter"]
            weak_meter_use = last_meter_weak - first_meter_weak
            strong_meter_use = last_meter_strong - first_meter_strong
            total_meter_use = strong_meter_use + weak_meter_use
            strong_meter = meter_list[-1]["strong_meter"]
            weak_meter = meter_list[-1]["weak_meter"]
            total_meter = strong_meter + weak_meter

            if meter_level == "SWP":
                pile_meter_use = sum([value for key, value in meter_list[-1].items() if 'pile' in key]) - sum(
                    [value for key, value in meter_list[0].items() if 'pile' in key])
                L2_loss = 1 - (pile_meter_use / strong_meter_use)
                return total_meter, strong_meter, weak_meter, total_meter_use, strong_meter_use, weak_meter_use, pile_meter_use, L2_loss, 0.00, 0.00, data_start_time, data_end_time

            elif meter_level == "SW":

                return total_meter, strong_meter, weak_meter, total_meter_use, strong_meter_use, weak_meter_use, 0.00, 0.00, 0.00, 0.00, data_start_time, data_end_time

            elif meter_level == "S":
                return total_meter, strong_meter, 0, total_meter_use, strong_meter_use, 0, 0.00, 0.00, 0.00, 0.00, data_start_time, data_end_time
        else:
            return -1
