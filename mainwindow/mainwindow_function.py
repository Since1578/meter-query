# -*- coding: utf-8 -*-
"""
@Time    : 2021/10/26 17:49
@Author  : xuhaotian
@SoftWare: PyCharm
"""
import copy
import datetime
import os
import sys
import time

import numpy as np
import pandas
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit
from sql_operation.login_mysql import get_region_relation
from draw_method.pyqt5_plot import MyBarWindow
from .mainwindow_QThread_class import WorkThread_pyqt_plot, WorkThread_biaopan
from .mainwindow_UI_QMainwindow import Ui_MainWindow as Ui_Form



class function_realization(QtWidgets.QMainWindow, Ui_Form):
    def __init__(self):
        # 初始化载入json内容
        super(function_realization, self).__init__()
        self.setupUi(self)
        QtWidgets.QApplication.processEvents()
        self.setWindowIcon(QIcon("./shell.jpg"))
        # 初始化菜单栏内容
        # self.init_menu()
        ##
        # self.setFixedSize(self.width(), self.height())
        # col = QColor(255, 170, 0)
        # self.setStyleSheet('QWidget{background-color:%s}' % col.name())
        self.control_name = ''
        self.day_week_month = {"day": ['-', '-'], "week": ['-', '-'], "month": ['-', '-']}
        #  表格初始化
        # self.init_table()
        #  表格导出事件绑定
        # self.pushButton_7.clicked.connect(self.export_electric_degree)
        #  柱状图、饼状图
        # self.select_menu_layer()
        #  区域关系映射初始化
        self.init_region_relation()
        #  查询电量窗口实例化
        # self.query_meter_window = query_meter_function.function_realization(self)
        print('[INFO] 主窗口界面仪表盘初始化')
        print('[INFO] 主窗口界面电量排行初始化')
        #self.init_yibiaopan()
        # self.start_biaopan_event()
        self.init_plot_pyqt_gun_electricity_topN()
        self.init_plot_pyqt_24h_electricity()
        self.init_plot_pyqt_tongbi()
        self.init_plot_pyqt_week_electricity()
        self.start_pyqt_plot_24h_electricity_event()
        self.start_pyqt_plot_topN_event()
        self.start_pyqt_plot_week_electricity_event()
        self.start_pyqt_plot_month_electricity_event()

    # def init_yibiaopan(self):
    #     self.simulationView = Window()
    #     # self.simulationView2 = Window()
    #
    #     sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    #     sizePolicy.setHorizontalStretch(0)
    #     sizePolicy.setVerticalStretch(0)
    #
    #     sizePolicy.setHeightForWidth(self.simulationView.sizePolicy().hasHeightForWidth())
    #     # sizePolicy.setHeightForWidth(self.simulationView2.sizePolicy().hasHeightForWidth())
    #
    #     self.simulationView.setSizePolicy(sizePolicy)
    #     self.simulationView.setObjectName("biaopan")
    #
    #     # self.simulationView2.setSizePolicy(sizePolicy)
    #     # self.simulationView2.setObjectName("simulationView2")
    #
    #     self.gridLayout.addWidget(self.simulationView, 1, 2, 1, 1)  # 控件名称，行，列，占用行数，占用列数，对齐方式
    #     # self.gridLayout.addWidget(self.simulationView2, 1, 1, 1, 1)
    #     # self.biaopan.show()

    def init_plot_pyqt_gun_electricity_topN(self):
        self.plot_pyqt_topN = MyBarWindow(title_name="昨日单枪充电量排行")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plot_pyqt_topN.sizePolicy().hasHeightForWidth())
        self.plot_pyqt_topN.setSizePolicy(sizePolicy)
        self.plot_pyqt_topN.setObjectName("topN")
        self.gridLayout.addWidget(self.plot_pyqt_topN, 1, 0, 1, 1)  # 控件名称，行，列，占用行数，占用列数，对齐方式

    def init_plot_pyqt_24h_electricity(self):
        self.plot_pyqt_24h_electricity = MyBarWindow(title_name="24小时电量趋势")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plot_pyqt_24h_electricity.sizePolicy().hasHeightForWidth())
        self.plot_pyqt_24h_electricity.setSizePolicy(sizePolicy)
        self.plot_pyqt_24h_electricity.setObjectName("24h_electricity")
        self.gridLayout.addWidget(self.plot_pyqt_24h_electricity, 0, 0, 1, 2)  # 控件名称，行，列，占用行数，占用列数

    def init_plot_pyqt_week_electricity(self):
        self.plot_pyqt_week_electricity = MyBarWindow(title_name="周电量趋势")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plot_pyqt_week_electricity.sizePolicy().hasHeightForWidth())
        self.plot_pyqt_week_electricity.setSizePolicy(sizePolicy)
        self.plot_pyqt_week_electricity.setObjectName("week_electricity")
        self.gridLayout.addWidget(self.plot_pyqt_week_electricity, 0, 2, 1, 1)  # 控件名称，行，列，占用行数，占用列数

    def init_plot_pyqt_tongbi(self):
        self.plot_pyqt_tongbi = MyBarWindow(title_name='用电统计', is_lable=True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plot_pyqt_tongbi.sizePolicy().hasHeightForWidth())
        self.plot_pyqt_tongbi.setSizePolicy(sizePolicy)
        self.plot_pyqt_tongbi.setObjectName("tongbi")
        self.gridLayout.addWidget(self.plot_pyqt_tongbi, 1, 1, 1, 2)  # 控件名称，行，列，占用行数，占用列数
        self.plot_pyqt_tongbi.plot_tongbi(self.day_week_month['day'], self.day_week_month['week'],
                                          self.day_week_month['month'])

    def set_Textsytle(self, ob, text_size=10, text_cuxi=40):
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setBold(True)
        font.setPointSize(text_size)
        font.setWeight(text_cuxi)  # 字体粗细控制
        ob.setFont(font)
        # ob.setGeometry(1400, 250, 250, 80)  # （x坐标，y坐标，宽，高）
        # ob.setFlat(True)  # 透明背景

    def init_region_relation(self):
        while True:
            try:
                self.region_relation_dict = get_region_relation()
                # print('region_relation_dict', self.region_relation_dict)
                assert self.region_relation_dict != 'netfiled' and self.region_relation_dict != 'sqlfiled', "sqlfiled or netfiled"
            except Exception as e:
                except_type, except_value, except_traceback = sys.exc_info()
                except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
                exc_dict = {
                    "报错类型": except_type,
                    "报错信息": except_value,
                    "报错文件": except_file,
                    "报错行数": except_traceback.tb_lineno,
                }

                print(exc_dict, e)
                QM = QtWidgets.QMainWindow()
                reply = QMessageBox.question(QM, 'Message', '网络连接超时，确定重新连接吗', QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.No)  # 默认关闭界面选择No
                if reply == QtWidgets.QMessageBox.Yes:
                    pass  # 忽视点击X事件
                else:
                    sys.exit(0)  # 关闭窗口
                time.sleep(2)
            else:
                #print(self.region_relation_dict)
                break

    def displayMesg(self, mseg):
        QMessageBox_ = QMessageBox()
        QM = QtWidgets.QMainWindow()
        QMessageBox_.setStyleSheet("background-color: rgb(0, 255, 255);")
        result = QMessageBox_.information(QM, "Notice", mseg,
                                          QMessageBox_.StandardButtons(QMessageBox_.Ok))
        if result == QMessageBox_.Ok:
            pass

    def closeEvent(self, event):
        QM = QtWidgets.QMainWindow()
        reply = QMessageBox.question(QM, 'Message', '确定要退出吗', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)  # 默认关闭界面选择No
        if reply == QtWidgets.QMessageBox.Yes:
            sys.exit(0)  # 关闭窗口
        else:
            event.ignore()  # 忽视点击X事件

    def write(self, data):
        # 将数据转化成DataFrame数据格式
        print('[INFO] 开始导出')
        dt = pandas.DataFrame(data)
        # 把id设置成行索引
        dt.columns = ['站点', '查询开始时间', '查询结束时间', '经营总电量(kW·h)', '谷时电量(%)', '平时电量(%)', '峰时电量(%)', '经营性电量成本(元)',
                      '照明等用电量(kW·h)']
        # 写入数据数据
        text, okPressed = QInputDialog.getText(self, "请输入导出的地址", "导出为（D:/1.csv）：", QLineEdit.Normal, "")
        if okPressed and text != '':
            if os.path.exists(text):
                self.displayMesg('文件已存在,导出失败')
            else:
                pandas.DataFrame.to_csv(dt, text, encoding="utf_8_sig", index=False)
                self.displayMesg('导出成功')

    def return_gateway_code(self, time_mode=None):
        """
        时间模式：主界面动态更新的时间类型，eg：昨日单枪电量topN（topN），今日-昨日24h电量汇总（24h），昨日电量总计（last_day）,上周电量总计（last_week），上月电量总计（last_month）
        @param time_mode:
        @return:
        """
        gateway_position = []
        for city_name, city_content in self.region_relation_dict['city'].items():
            for region_key, region_dict in city_content.items():
                for region_name, region_content in region_dict.items():
                    for position_key, position_dict in region_content.items():
                        for position_name, position_content in position_dict.items():
                            end_time_date = datetime.datetime.now()  # .strftime("%Y-%m-%d %H:%M:%S")
                            if time_mode == "topN":
                                begining_time_date = end_time_date - datetime.timedelta(days=1)
                                end_time_str = end_time_date.strftime("%Y-%m-%d %H:%M:%S").split(' ')[0] + " 00:00:10"
                                begining_time_str = begining_time_date.strftime("%Y-%m-%d %H:%M:%S").split(' ')[
                                                        0] + " 00:00:00"
                            # elif time_mode == "24h":
                            #     begining_time_date = end_time_date - datetime.timedelta(days=1)
                            #     begining_time_str = begining_time_date.strftime("%Y-%m-%d %H:%M:%S").split(' ')[
                            #                             0] + " 00:00:00"
                            #     end_time_str = end_time_date.strftime("%Y-%m-%d %H:%M:%S")
                            elif time_mode == "24h":
                                begining_time_date = end_time_date - datetime.timedelta(days=2)
                                begining_time_str = begining_time_date.strftime("%Y-%m-%d %H:%M:%S").split(' ')[
                                                        0] + " 00:00:00 "
                                end_time_date = datetime.datetime.now()  # .strftime("%Y-%m-%d %H:%M:%S")
                                end_time_str = end_time_date.strftime("%Y-%m-%d %H:%M:%S")
                            elif time_mode == "last_week":
                                begining_time_str = (datetime.date.today() - datetime.timedelta(
                                    days=(14 + datetime.date.today().isoweekday() - 1))).strftime(
                                    "%Y-%m-%d") + " 00:00:00"
                                end_time_date = datetime.datetime.now()  # .strftime("%Y-%m-%d %H:%M:%S")
                                end_time_str = end_time_date.strftime("%Y-%m-%d %H:%M:%S")
                            #  上周起始时间 (datetime.date.today() - datetime.timedelta(days=(7+datetime.date.today().isoweekday()-1))).strftime("%Y-%m-%d")
                            else:
                                now = datetime.date.today()
                                this_month_start = datetime.datetime(now.year, now.month, 1)
                                last_month_end = this_month_start - datetime.timedelta(days=1)
                                begining_time_str = \
                                    datetime.datetime(last_month_end.year, last_month_end.month - 1, 1).strftime(
                                        "%Y-%m-%d %H:%M:%S").split(' ')[0] + " 00:00:00"
                                end_time_str = this_month_start.strftime("%Y-%m-%d %H:%M:%S").split(' ')[
                                                   0] + " 00:00:10"
                            gateway_position.append([position_name, position_content, begining_time_str, end_time_str])
        return gateway_position

    def update_contorl(self, control_name):
        """Therefore if you want to delete a QObject then it is safer to use deleteLater(), for other C++ objects (like
        QImage, QPixmap, QGraphicsItems, etc) you should use sip.delete().
        https://stackoverflow.com/questions/61969809/pyqt5-deletelater-vs-sip-delete """
        # self.findChild(QWidget, control_name).close()  # 关闭控件
        # self.gridLayout.removeWidget(self.findChild(QWidget, control_name))  # 从gridlayout布局中移除该控件
        # sip.delete(self.findChild(QWidget, control_name))  # 删除该控件
        # self.plot_pyqt_topN.deleteLater()  # 删除该控件

    def update_biaopan(self, signal_value):
        total_power = 0
        # print("[INFO] signal_value", signal_value)
        for index, value in enumerate(signal_value):
            total_power += value['current_power'] / 1000
        total_power = round(total_power, 2)
        print('[INFO] total_power MW:', round(total_power, 2))
        t1 = time.time()
        self.simulationView.setValue(total_power)

    def start_biaopan_event(self):
        try:
            self.thread_biaopan = WorkThread_biaopan()
            self.thread_biaopan.update_interval = 'tenmin'
            self.thread_biaopan.progressBarValue.connect(self.update_biaopan)
            self.thread_biaopan.start()
        except Exception as e:
            except_type, except_value, except_traceback = sys.exc_info()
            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
            exc_dict = {
                "报错类型": except_type,
                "报错信息": except_value,
                "报错文件": except_file,
                "报错行数": except_traceback.tb_lineno,
            }
            print(exc_dict)

    def update_pyqt_plot(self, signal_value):
        signal_value, plot_type = signal_value[0], signal_value[1]
        if len(signal_value) != 0:
            if plot_type == 'topN':
                # print(f"[INFO ] {datetime.datetime.now()} 所有场站单枪充电量汇总：", signal_value)
                label = [i[0] for i in signal_value]
                data = [i[1] for i in signal_value]
                dict_data = {}
                for i, j in zip(data, label):
                    dict_data[i] = j
                data.sort()
                temp_label = []
                for i in data:
                    temp_label.append(dict_data[i])
                self.plot_pyqt_topN.init_chart()
                self.plot_pyqt_topN.plot_topN(temp_label[-10:], data[-10:])
            elif plot_type == '24h_electricity':
                print(f"[INFO ] {datetime.datetime.now()} 所有场站24h充电量汇总：", signal_value)
                total_hour_meter = self.alignment_hour(signal_value)
                #print(f"[INFO ] {datetime.datetime.now()} 所有场站24h充电量汇总：", total_hour_meter)
                self.plot_pyqt_24h_electricity.init_chart()
                self.plot_pyqt_24h_electricity.plot_lineAndBar(total_hour_meter[1:], meter_type='24h')
                first_day_data = sum([value for key, value in total_hour_meter[0].items()])
                second_day_data = sum([value for key, value in total_hour_meter[1].items()])
                self.day_week_month['day'][0] = round(second_day_data, 1)
                if first_day_data != 0:
                    self.day_week_month['day'][1] = (second_day_data - first_day_data) / first_day_data
                else:
                    self.day_week_month['day'][1] = '-'
                self.plot_pyqt_tongbi.init_chart()
                self.plot_pyqt_tongbi.plot_tongbi(self.day_week_month['day'],
                                                  self.day_week_month['week'],
                                                  self.day_week_month['month'])
            elif plot_type == 'week':
                total_meter = self.alignment_week(signal_value)
                print(f"[INFO ] {datetime.datetime.now()} 所有场站周充电量汇总：", len(total_meter))
                first_week_meter = sum(total_meter[0])
                second_week_meter = sum(total_meter[1])
                self.plot_pyqt_week_electricity.init_chart()
                self.plot_pyqt_week_electricity.plot_lineAndBar([total_meter[1], total_meter[2]], 'week')

                self.day_week_month['week'][0] = round(second_week_meter, 1)
                if first_week_meter != 0:
                    self.day_week_month['week'][1] = (second_week_meter - first_week_meter) / first_week_meter
                else:
                    self.day_week_month['week'][1] = '-'
                self.plot_pyqt_tongbi.init_chart()
                self.plot_pyqt_tongbi.plot_tongbi(self.day_week_month['day'],
                                                  self.day_week_month['week'],
                                                  self.day_week_month['month'])
            elif plot_type == 'month':
                total_meter = self.alignment_month(signal_value)
                print(f"[INFO ] {datetime.datetime.now()} 所有场站月充电量汇总：", len(total_meter))
                first_month_meter = sum(total_meter[0])
                second_month_meter = sum(total_meter[1])
                self.day_week_month['month'][0] = round(second_month_meter, 1)
                if first_month_meter != 0:
                    self.day_week_month['month'][1] = (second_month_meter - first_month_meter) / first_month_meter
                else:
                    self.day_week_month['month'][1] = '-'
                self.plot_pyqt_tongbi.init_chart()
                self.plot_pyqt_tongbi.plot_tongbi(self.day_week_month['day'],
                                                  self.day_week_month['week'],
                                                  self.day_week_month['month'])

    def alignment_hour(self, datas):
        '''
        对所有场站每小时的耗电量进行累加
        @param datas: [[position，{“2023-03-20”:{"2023-03-20 17:00": 125, "2023-03-20 18:00": 225, ...}, ...}], ...]
        @return: [{“2023-03-20”:{"2023-03-20 17:00": 125, "2023-03-20 18:00": 225, ...}, ...}, {“2023-03-21”:{....}}]
        '''
        total_hour_meter = []
        whole_day = ['0' + str(i) + ':00' if len(str(i)) == 1 else str(i) + ":00" for i in range(24)]
        #  构造三天*24h数据
        for i in range(3):
            total_hour_meter.append({})
            for hour in whole_day:
                total_hour_meter[-1][hour] = []
        day_list = []
        for index, values in enumerate(datas):
            #  循环每一个天数据
            which_day = -1
            for key, value in values[1].items():
                which_day += 1
                if key not in day_list:
                    day_list.append(key)
                #  累加每个场站每小时的统计值
                for hour, hour_value in value.items():
                    if hour[-5:] in total_hour_meter[which_day]:
                        total_hour_meter[which_day][hour[-5:]].append(hour_value)
        total_hour_meter_temp = copy.deepcopy(total_hour_meter)
        for day, values in enumerate(total_hour_meter_temp):
            day_hour_list = list(values.keys())
            for hour in day_hour_list:
                total_hour_meter[day][hour] = sum(total_hour_meter_temp[day][hour])
        return total_hour_meter

    def start_pyqt_plot_topN_event(self):
        try:
            self.thread_plot_topN = WorkThread_pyqt_plot()
            self.thread_plot_topN.plot_type = 'topN'
            self.thread_plot_topN.time_mode = 'topN'
            self.thread_plot_topN.update_interval = 'hour'
            self.thread_plot_topN.progressBarValue.connect(self.update_pyqt_plot)
            self.thread_plot_topN.position_infos_dict = self.return_gateway_code
            self.thread_plot_topN.start()

        except Exception as e:
            except_type, except_value, except_traceback = sys.exc_info()
            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
            exc_dict = {
                "报错类型": except_type,
                "报错信息": except_value,
                "报错文件": except_file,
                "报错行数": except_traceback.tb_lineno,
            }
            print(exc_dict, e)

    def start_pyqt_plot_24h_electricity_event(self):
        try:
            self.thread_plot_24h_electricity = WorkThread_pyqt_plot()
            self.thread_plot_24h_electricity.plot_type = '24h_electricity'
            self.thread_plot_24h_electricity.time_mode = '24h'
            self.thread_plot_24h_electricity.update_interval = 'tenmin'
            self.thread_plot_24h_electricity.progressBarValue.connect(self.update_pyqt_plot)
            self.thread_plot_24h_electricity.position_infos_dict = self.return_gateway_code
            self.thread_plot_24h_electricity.start()

        except Exception as e:
            except_type, except_value, except_traceback = sys.exc_info()
            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
            exc_dict = {
                "报错类型": except_type,
                "报错信息": except_value,
                "报错文件": except_file,
                "报错行数": except_traceback.tb_lineno,
            }
            print(exc_dict, e)

    def start_pyqt_plot_week_electricity_event(self):
        try:
            self.thread_plot_week_electricity = WorkThread_pyqt_plot()
            self.thread_plot_week_electricity.plot_type = 'week'
            self.thread_plot_week_electricity.time_mode = 'last_week'
            self.thread_plot_week_electricity.update_interval = 'hour'
            self.thread_plot_week_electricity.progressBarValue.connect(self.update_pyqt_plot)
            self.thread_plot_week_electricity.position_infos_dict = self.return_gateway_code
            self.thread_plot_week_electricity.start()

        except Exception as e:
            except_type, except_value, except_traceback = sys.exc_info()
            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
            exc_dict = {
                "报错类型": except_type,
                "报错信息": except_value,
                "报错文件": except_file,
                "报错行数": except_traceback.tb_lineno,
            }
            print(exc_dict, e)

    def alignment_week(self, datas):
        '''
        对所有场站三周（从当前往前推三周）每天的耗电量进行累加
        @param datas: [[position，{“2023-03-20”: 125, "2023-03-22 18:00": 225, ...}], ...]
        @return: [[first week every day electricity], [second week every day electricity], [third week every day electricity]]
        '''
        total_meter = [[], [], []]
        week_list = []
        #  生成单日电量字典模版
        for i in range(21):
            week_list.append({(datetime.date.today() - datetime.timedelta(
                days=(14 + datetime.date.today().isoweekday() - 1 - i))).strftime("%Y-%m-%d"): 0})
        b = []
        #  根据数据日期填写模版中每天的电量
        for i in datas:
            time_list = copy.deepcopy(week_list)
            position_name = i[0]
            position_value = i[1]
            b.append([position_name])
            for time_, value_ in position_value.items():
                for time_temp in time_list:
                    if time_ in time_temp:
                        time_temp[time_] = value_
            b[-1].append(time_list)
        #  将单日电量划分为三周
        for i in b:
            day1_7 = [list(j.values())[0] for index, j in enumerate(i[1]) if (index + 1) <= 7]
            day8_14 = [list(j.values())[0] for index, j in enumerate(i[1]) if 8 <= (index + 1) <= 14]
            day15_21 = [list(j.values())[0] for index, j in enumerate(i[1]) if 15 <= (index + 1) <= 21]
            total_meter[0].append(day1_7)
            total_meter[1].append(day8_14)
            total_meter[2].append(day15_21)
        #  分别对所有场站每周的电量进行求和
        if len(total_meter[0]) == 0:
            total_meter[0] = [0, 0, 0, 0, 0, 0, 0]
        else:
            total_meter[0] = np.sum(total_meter[0], axis=0).tolist()
        if len(total_meter[1]) == 0:
            total_meter[1] = [0, 0, 0, 0, 0, 0, 0]
        else:
            total_meter[1] = np.sum(total_meter[1], axis=0).tolist()
        if len(total_meter[2]) == 0:
            total_meter[2] = [0, 0, 0, 0, 0, 0, 0]
        else:
            total_meter[2] = np.sum(total_meter[2], axis=0).tolist()
        return total_meter

    def start_pyqt_plot_month_electricity_event(self):
        try:
            self.thread_plot_month_electricity = WorkThread_pyqt_plot()
            self.thread_plot_month_electricity.plot_type = 'month'
            self.thread_plot_month_electricity.time_mode = 'last_month'
            self.thread_plot_month_electricity.update_interval = 'hour'
            self.thread_plot_month_electricity.progressBarValue.connect(self.update_pyqt_plot)
            self.thread_plot_month_electricity.position_infos_dict = self.return_gateway_code
            self.thread_plot_month_electricity.start()

        except Exception as e:
            except_type, except_value, except_traceback = sys.exc_info()
            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
            exc_dict = {
                "报错类型": except_type,
                "报错信息": except_value,
                "报错文件": except_file,
                "报错行数": except_traceback.tb_lineno,
            }
            print(exc_dict, e)

    def alignment_month(self, datas):
        total_meter = [[], []]
        now = datetime.date.today()
        this_month_start = datetime.datetime(now.year, now.month, 1)
        last_month_end = this_month_start - datetime.timedelta(days=1)
        begining_time_str = datetime.datetime(last_month_end.year, last_month_end.month - 1, 1).strftime("%Y-%m")
        end_time_str = last_month_end.strftime("%Y-%m")
        week_list = [{begining_time_str: 0}, {end_time_str: 0}]
        b = []
        for i in datas:
            time_list = copy.deepcopy(week_list)
            position_name = i[0]
            position_value = i[1]
            b.append([position_name])
            for time_, value_ in position_value.items():
                for time_temp in time_list:
                    if time_ in time_temp:
                        time_temp[time_] = value_
            b[-1].append(time_list)
        for i in b:
            first_moth = [list(j.values())[0] for index, j in enumerate(i[1]) if (index + 1) == 1]
            second_moth = [list(j.values())[0] for index, j in enumerate(i[1]) if (index + 1) == 2]
            total_meter[0].append(first_moth)
            total_meter[1].append(second_moth)
        #  分别对所有场站每月的电量进行求和
        if len(total_meter[0]) == 0:
            total_meter[0] = [0, 0, 0, 0, 0, 0, 0]
        else:
            total_meter[0] = np.sum(total_meter[0], axis=0).tolist()
        if len(total_meter[1]) == 0:
            total_meter[1] = [0, 0, 0, 0, 0, 0, 0]
        else:
            total_meter[1] = np.sum(total_meter[1], axis=0).tolist()
        return total_meter
