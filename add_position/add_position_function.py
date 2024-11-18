# -*- coding: utf-8 -*-
import datetime
import json
import sys
import time

import paramiko
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QCompleter

from .add_position_UI import Ui_Form
from base_model.query_administrative_division import Gaode_Search
from sql_operation.operation_mysql import query_position_nums, write_position_infos_to_sql, query_position_data


class function_realization(QtWidgets.QWidget, Ui_Form):
    def __init__(self, window):
        # 初始化载入json内容
        super(function_realization, self).__init__()
        self.setWindowIcon(QIcon("./shell.jpg"))
        self.query_window = window
        self.select_nums = None  # 断路器选择配置的数目
        self.position_write_result = False
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        # 进度条初始化
        # self.window = window
        self.position_data_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        #  添加场站参数配置下拉复选框初始化
        self.all_list = [[], [], [], []]
        self.position_code = {}
        self.position_infos = self.query_window.position_infos
        #  查询最小时间间隔
        self.query_interval_time = time.time()
        #  电价参数配置确定按钮函数绑定
        self.query_service_pushButton.clicked.connect(self.position_locate)
        self.add_position_pushButton.clicked.connect(self.add_position)
        self.position_data_query_pushButton.clicked.connect(self.position_data_query)
        self.init_position2gateway()
        self.init_combocheckbox()
        self.init_pile_gun_data()
        self.init_gateway_data()
        self.init_cut_address()
        self.init_electricity_data()
        self.init_comBbox_match()

    def position_data_query(self):
        if self.position_data_query_comboBox.currentText() != '':
            if self.position_data_query_comboBox.currentText() in self.position_code:
                position_gateway = self.position_code[self.position_data_query_comboBox.currentText()]
                realtime_data = query_position_data(position_gateway)
                if realtime_data[0]:
                    now_time = time.time()
                    if (now_time - self.query_interval_time) > 2:
                        power_data, gateway_status, electricity_data = realtime_data[1]['power'], realtime_data[1][
                            'gateway_status'], realtime_data[1]['electrivity_data']
                        now_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
                        data_total = ''
                        print("[INFO] 站点实时数据查询结果：", power_data, gateway_status, electricity_data)
                        data_total += now_time + '：' + self.position_data_query_comboBox.currentText() + '\n'
                        if gateway_status is not None:
                            data_1 = f'{now_time}, 场站网关心跳最新时间：{gateway_status[-1]}'
                            data_total += data_1 + '\n'
                        else:
                            data_1 = f'{now_time}, 未查询到当前网关心跳时间数据'
                            data_total += data_1 + '\n'
                        # if power_data is not None:
                        #     data_2 = f'{now_time}, 场站总功率数据最新时间：{power_data[-1]}, 总功率：{power_data[1]}kW'
                        #     data_total += data_2 + '\n'
                        # else:
                        #     data_2 = f'{now_time}, 未查询到当前场站总功率数据'
                        #     data_total += data_2 + '\n'
                        if electricity_data is not None:
                            operational_electricity = [value for key, value in json.loads(electricity_data[2]).items()
                                                       if "strong" in key]
                            operational_electricity = ["电表#" + str(index + 1) + "读数 " + str(value) + " kW·h" if len(
                                operational_electricity) > 1 else "电表" + "读数 " + str(value) + " kW·h" for
                                                       index, value in enumerate(operational_electricity)]
                            temp1 = ''
                            for index, value in enumerate(operational_electricity):
                                if index != len(operational_electricity) - 1:
                                    temp1 += value + '，'
                                else:
                                    temp1 += value + ''
                            non_operational_electricity = [value for key, value in
                                                           json.loads(electricity_data[2]).items() if "weak" in key]
                            non_operational_electricity = ["电表#" + str(index + 1) + "读数 " + str(value) + " kW·h" if len(
                                non_operational_electricity) > 1 else "电表" + "读数 " + str(value) + " kW·h" for
                                                           index, value in enumerate(non_operational_electricity)]
                            temp2 = ''
                            for index, value in enumerate(non_operational_electricity):
                                if index != len(non_operational_electricity) - 1:
                                    temp2 += value + '，'
                                else:
                                    temp2 += value + ''

                            data_3 = f'{now_time}, 场站电表数据最新时间：{electricity_data[-1]}, 经营性[{temp1}]，非经营性[{temp2}]'
                            data_total += data_3
                        else:
                            data_3 = f'{now_time}, 未查询到当前场站电表相关数据'
                            data_total += data_3
                        self.position_data_label.setText(data_total)
                        QMessageBox.warning(self, 'Notice', '站点实时数据查询成功')
                        self.query_interval_time = time.time()
                    else:
                        QMessageBox.warning(self, 'Notice', '查询操作过于频繁，请稍后再试')
                else:
                    QMessageBox.warning(self, 'Notice', '查询超时，请重试')
                    self.query_interval_time = time.time()
            else:
                QMessageBox.warning(self, 'Notice', '场站名称输入有误或站点尚未添加')
        else:
            QMessageBox.warning(self, 'Notice', '请输入正确的场站名称')

    def init_position_infos_edits(self):
        self.province_name_edit.setText('')
        self.city_name_edit.setText('')
        self.region_name_edit.setText('')
        self.adcode_edit.setText('')
        self.sql_table_id_edit.setText('')
        self.position_id_edit.setText('')

    def insert_combobox_position_place(self, insert_data):
        # 增加选项元素
        self.comboBox_position_place.clear()
        self.comboBox_position_place.addItem('--请选择--')
        self.return_result = {}
        for i in insert_data:
            self.comboBox_position_place.addItem(i['address'])
            self.return_result[i['address']] = i
        self.comboBox_position_place.setCurrentIndex(0)

    def init_position2gateway(self):
        for position in self.query_window.position_infos:
            result = self.query_window.return_position_code(position)
            self.position_code[position] = result[1]

    def init_comBbox_match(self):
        if self.query_window != '':
            self.position_data_query_comboBox.setEditable(True)
            self.position_data_query_comboBox.addItems(self.position_infos)
            completer = QCompleter(self.position_infos)
            completer.setFilterMode(Qt.MatchContains)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            self.position_data_query_comboBox.setCompleter(completer)

    def clicked_comboBox_position_place(self, index):
        self.comboBox_position_place.itemText(index)
        return_clicked_content = self.comboBox_position_place.currentText()
        if return_clicked_content != '--请选择--':
            self.province_name_edit.setText(self.return_result[return_clicked_content]['pname'])
            self.city_name_edit.setText(self.return_result[return_clicked_content]['cityname'])
            self.region_name_edit.setText(self.return_result[return_clicked_content]['adname'])
            self.adcode_edit.setText(self.return_result[return_clicked_content]['adcode'])
            position_nums = query_position_nums()
            if position_nums != -1:
                self.sql_table_id_edit.setText('%04d' % (position_nums + 1))
                self.position_id_edit.setText(
                    self.return_result[return_clicked_content]['adcode'] + '%04d' % (position_nums + 1))
                QMessageBox.warning(self, "Notice", '自动填充成功')
            else:
                QMessageBox.warning(self, "Notice", '自动填充超时，请重新选择')

        elif return_clicked_content == '--请选择--':
            self.init_position_infos_edits()

    def position_locate(self):
        if self.position_name_edit.text() == '':
            QMessageBox.warning(self, "Notice", "请输入站点名称")
        else:
            input_name = self.position_name_edit.text()
            try:
                search_result = Gaode_Search(input_name)
            except Exception as e:
                print(e)
                QMessageBox.warning(self, "Notice", '查询超时，请重试')
            else:
                if len(search_result) == 0:
                    QMessageBox.warning(self, "Notice", '未查询到相关站点信息')
                else:
                    QMessageBox.warning(self, "Notice", '定位服务查询成功')
                    self.insert_combobox_position_place(search_result)

    def position_data_write_result(self):
        if self.position_name_edit.text() != '' and self.province_name_edit.text() != '' and self.city_name_edit.text() != '' and self.region_name_edit.text() != '' \
                and self.sql_table_id_edit.text() != '' and self.adcode_edit.text() != '' and self.position_id_edit.text() != '' and (
                self.comboBox_position_place.currentText() != '--请选择--' or self.comboBox_position_place.currentText() != '') \
                and self.comboBox_fast_pile_num.currentText() != '--请选择--' and self.comboBox_fast_gun_num.currentText() != '' and self.comboBox_slow_gun_num.currentText() != '--请选择--':
            return True
        else:
            return False

    def pile_gun_write_result(self):
        if self.comboBox_fast_pile_num.currentText() != '--请选择--' and self.comboBox_fast_gun_num != '--请选择--' and self.comboBox_slow_gun_num != '--请选择--':
            return True
        else:
            return False

    def init_combocheckbox(self):
        self.comboBox_position_place.activated['int'].connect(self.clicked_comboBox_position_place)
        self.comboBox_fast_pile_num.activated['int'].connect(self.clicked_comboBox_fast_pile_num)
        self.comboBox_fast_gun_num.activated['int'].connect(self.clicked_comboBox_fast_gun_num)
        self.comboBox_slow_gun_num.activated['int'].connect(self.clicked_comboBox_slow_gun_num)
        self.comboBox_gateway_brand.activated['int'].connect(self.clicked_comboBox_gateway_brand)
        self.comboBox_gateway_model.activated['int'].connect(self.clicked_comboBox_gateway_model)
        self.comboBox_electricity_level.activated['int'].connect(self.clicked_comboBox_electricity_level)
        self.comboBox_strong_electricity_num.activated['int'].connect(self.clicked_comboBox_strong_electricity_num)
        self.comboBox_weak_electricity_num.activated['int'].connect(self.clicked_comboBox_weak_electricity_num)
        self.comboBox_cut_brand.activated['int'].connect(self.clicked_comboBox_cut_brand)
        self.comboBox_cut_model.activated['int'].connect(self.clicked_comboBox_cut_model)
        self.comboBox_cut_heart.activated['int'].connect(self.clicked_comboBox_cut_heart)
        self.comboBox_cut_485_address_1.activated['int'].connect(self.clicked_comboBox_cut_485_address_1)
        self.comboBox_cut_485_address_2.activated['int'].connect(self.clicked_comboBox_cut_485_address_2)
        self.comboBox_cut_485_address_3.activated['int'].connect(self.clicked_comboBox_cut_485_address_3)
        self.comboBox_cut_485_address_4.activated['int'].connect(self.clicked_comboBox_cut_485_address_4)

    def clicked_comboBox_fast_pile_num(self, index):
        self.comboBox_fast_pile_num.itemText(index)

    def clicked_comboBox_fast_gun_num(self, index):
        self.comboBox_fast_gun_num.itemText(index)

    def clicked_comboBox_slow_gun_num(self, index):
        self.comboBox_slow_gun_num.itemText(index)

    def clicked_comboBox_gateway_brand(self, index):
        self.comboBox_gateway_brand.itemText(index)

    def clicked_comboBox_gateway_model(self, index):
        self.comboBox_gateway_model.itemText(index)

    def clicked_comboBox_electricity_level(self, index):
        self.comboBox_electricity_level.itemText(index)

    def clicked_comboBox_strong_electricity_num(self, index):
        self.comboBox_strong_electricity_num.itemText(index)

    def clicked_comboBox_weak_electricity_num(self, index):
        self.comboBox_weak_electricity_num.itemText(index)

    def clicked_comboBox_cut_brand(self, index):
        self.comboBox_cut_brand.itemText(index)

    def clicked_comboBox_cut_model(self, index):
        self.comboBox_cut_model.itemText(index)

    def clicked_comboBox_cut_heart(self, index):
        self.comboBox_cut_heart.itemText(index)

    def clicked_comboBox_cut_485_address_1(self, index):
        self.comboBox_cut_485_address_1.itemText(index)

    def clicked_comboBox_cut_485_address_2(self, index):
        self.comboBox_cut_485_address_2.itemText(index)

    def clicked_comboBox_cut_485_address_3(self, index):
        self.comboBox_cut_485_address_3.itemText(index)

    def clicked_comboBox_cut_485_address_4(self, index):
        self.comboBox_cut_485_address_4.itemText(index)

    def init_pile_gun_data(self):
        fast_pile_list = [str(i) for i in range(0, 101)]
        fast_pile_list.insert(0, '--请选择--')
        self.comboBox_fast_pile_num.addItems(fast_pile_list)
        fast_gun_num = [str(i) for i in range(0, 201)]
        fast_gun_num.insert(0, '--请选择--')
        self.comboBox_fast_gun_num.addItems(fast_gun_num)
        slow_gun_num = [str(i) for i in range(0, 101)]
        slow_gun_num.insert(0, '--请选择--')
        self.comboBox_slow_gun_num.addItems(slow_gun_num)

    def init_gateway_data(self):
        gateway_brand_list = ['物通博联']
        gateway_brand_list.insert(0, '--请选择--')
        self.comboBox_gateway_brand.addItems(gateway_brand_list)
        gateway_model_list = ['WG581-LL07-MMQTT', 'WG583-MMQTT']
        gateway_model_list.insert(0, '--请选择--')
        self.comboBox_gateway_model.addItems(gateway_model_list)

    def gateway_data_write_result(self):
        if self.comboBox_gateway_model.currentText() != '--请选择--' and self.comboBox_gateway_brand.currentText() != '--请选择--' and \
                len(self.gateway_serial_edit.text()) == 20:
            return True
        else:
            return False

    def init_cut_address(self):
        address_485_list = [str(i) for i in range(0, 101)]
        address_485_list.insert(0, '--请选择--')
        self.comboBox_cut_485_address_1.addItems(address_485_list)
        self.comboBox_cut_485_address_2.addItems(address_485_list)
        self.comboBox_cut_485_address_3.addItems(address_485_list)
        self.comboBox_cut_485_address_4.addItems(address_485_list)
        self.comboBox_cut_model.addItems(['--请选择--', 'SWB1-125'])
        self.comboBox_cut_brand.addItems(['--请选择--', '麦多其'])
        self.comboBox_cut_heart.addItems(['--请选择--', '60', '90', '120', '240'])
        cut_serial_list = ['0' + str(id) for id in range(1, 5)]
        cut_serial_list.insert(0, '--请选择--')
        self.comboBox_cut_serial_1.addItems(cut_serial_list)
        self.comboBox_cut_serial_2.addItems(cut_serial_list)
        self.comboBox_cut_serial_3.addItems(cut_serial_list)
        self.comboBox_cut_serial_4.addItems(cut_serial_list)
        cut_variable_list = ['DLQ0' + str(id) for id in range(1, 5)]
        cut_variable_list.insert(0, '--请选择--')
        self.comboBox_cut_variable_1.addItems(cut_variable_list)
        self.comboBox_cut_variable_2.addItems(cut_variable_list)
        self.comboBox_cut_variable_3.addItems(cut_variable_list)
        self.comboBox_cut_variable_4.addItems(cut_variable_list)

    @staticmethod
    def delect_appoint_content(data: list, object_content):
        while object_content in data:
            data.remove(object_content)
        return data

    def cut_data_write_result(self):
        self.select_nums = []
        if self.comboBox_cut_brand.currentText() != '--请选择--' and self.comboBox_cut_model.currentText() != '--请选择--' and self.comboBox_cut_heart.currentText() != '--请选择--':
            if self.comboBox_cut_serial_1.currentText() != '--请选择--' and self.comboBox_cut_variable_1.currentText() != '--请选择--' and self.comboBox_cut_485_address_1.currentText() != '--请选择--':
                self.select_nums.append(
                    [self.comboBox_cut_serial_1.currentText(), self.comboBox_cut_variable_1.currentText(),
                     self.comboBox_cut_485_address_1.currentText()])
            if self.comboBox_cut_serial_2.currentText() != '--请选择--' and self.comboBox_cut_variable_2.currentText() != '--请选择--' and self.comboBox_cut_485_address_2.currentText() != '--请选择--':
                self.select_nums.append(
                    [self.comboBox_cut_serial_2.currentText(), self.comboBox_cut_variable_2.currentText(),
                     self.comboBox_cut_485_address_2.currentText()])
            if self.comboBox_cut_serial_3.currentText() != '--请选择--' and self.comboBox_cut_variable_3.currentText() != '--请选择--' and self.comboBox_cut_485_address_3.currentText() != '--请选择--':
                self.select_nums.append(
                    [self.comboBox_cut_serial_3.currentText(), self.comboBox_cut_variable_3.currentText(),
                     self.comboBox_cut_485_address_3.currentText()])
            if self.comboBox_cut_serial_4.currentText() != '--请选择--' and self.comboBox_cut_variable_4.currentText() != '--请选择--' and self.comboBox_cut_485_address_4.currentText() != '--请选择--':
                self.select_nums.append(
                    [self.comboBox_cut_serial_4.currentText(), self.comboBox_cut_variable_4.currentText(),
                     self.comboBox_cut_485_address_4.currentText()])
            cut_serial = [self.comboBox_cut_serial_1.currentText(), self.comboBox_cut_serial_2.currentText(),
                          self.comboBox_cut_serial_3.currentText(), self.comboBox_cut_serial_4.currentText()]
            cut_serial = self.delect_appoint_content(cut_serial, '--请选择--')
            cut_serial_set = set(cut_serial)
            cut_variable = [self.comboBox_cut_variable_1.currentText(), self.comboBox_cut_variable_2.currentText(),
                            self.comboBox_cut_variable_3.currentText(), self.comboBox_cut_variable_4.currentText()]
            cut_variable = self.delect_appoint_content(cut_variable, '--请选择--')
            cut_variable_set = set(cut_variable)
            cut_485_address = [self.comboBox_cut_485_address_1.currentText(),
                               self.comboBox_cut_485_address_2.currentText(),
                               self.comboBox_cut_485_address_3.currentText(),
                               self.comboBox_cut_485_address_4.currentText()]
            cut_485_address = self.delect_appoint_content(cut_485_address, '--请选择--')
            cut_485_address_set = set(cut_485_address)
            if (len(cut_serial) != len(cut_serial_set)) or (len(cut_variable) != len(cut_variable_set)) or (
                    len(cut_485_address) != len(cut_485_address_set)):
                self.select_nums = []
        else:
            return False
        if not self.select_nums:
            return False
        else:
            return True

    def init_electricity_data(self):
        self.comboBox_electricity_level.addItems(['--请选择--', 'SW', 'S'])
        strong_electricity_num = [str(i) for i in range(0, 51)]
        strong_electricity_num.insert(0, '--请选择--')
        self.comboBox_strong_electricity_num.addItems(strong_electricity_num)
        self.comboBox_weak_electricity_num.addItems(strong_electricity_num)

    def electricity_data_write_result(self):
        if self.comboBox_electricity_level.currentText() != '--请选择--' and self.comboBox_strong_electricity_num.currentText() != '--请选择--' and self.comboBox_weak_electricity_num.currentText() != '--请选择--':
            return True
        else:
            return False

    def add_position(self):
        if self.position_name_edit.text() != '' and self.position_data_write_result():
            self.position_infos_label.setStyleSheet("background-color: rgb(85, 255, 0);\n"
                                                    "font: 75 12pt \"Times New Roman\";")
            if self.gateway_data_write_result():
                self.gateway_infos_label.setStyleSheet("background-color: rgb(85, 255, 0);\n"
                                                       "font: 75 12pt \"Times New Roman\";")
                if self.electricity_data_write_result():
                    self.electricity_infos_label.setStyleSheet("background-color: rgb(85, 255, 0);\n"
                                                               "font: 75 12pt \"Times New Roman\";")
                    if self.cut_data_write_result():
                        self.cut_infos_label.setStyleSheet("background-color: rgb(85, 255, 0);\n"
                                                           "font: 75 12pt \"Times New Roman\";")
                        # position_id, position_name, position_province, position_city, position_county, position_postcode, position_place" \
                        # ", charge_pile_nums, charge_gun_nums, charge_AC_gun_nums,gateway_brand, gateway_type, heart_interval,
                        # position_id, meter_level, S, W
                        self.position_name_edit.setText(self.position_name_edit.text().replace(' ', ''))
                        self.gateway_serial_edit.setText(self.gateway_serial_edit.text().replace(' ', ''))
                        write_infos_position = {'id': self.sql_table_id_edit.text(),
                                                'position_id': self.position_id_edit.text(),
                                                'position_name': self.position_name_edit.text(),
                                                'position_province': self.province_name_edit.text(),
                                                'position_city': self.city_name_edit.text(),
                                                'position_county': self.region_name_edit.text(),
                                                'position_postcode': self.adcode_edit.text(),
                                                'position_place': self.province_name_edit.text() + self.city_name_edit.text() + self.region_name_edit.text() + self.comboBox_position_place.currentText(),
                                                'charge_pile_nums': self.comboBox_fast_pile_num.currentText(),
                                                'charge_gun_nums': self.comboBox_fast_gun_num.currentText(),
                                                'charge_AC_gun_nums': self.comboBox_slow_gun_num.currentText()}
                        write_infos_gateway = {'gateway_id': self.gateway_serial_edit.text(),
                                               'gateway_brand': self.comboBox_gateway_brand.currentText(),
                                               'gateway_type': self.comboBox_gateway_model.currentText(),
                                               'heart_interval': 60, 'position_id': self.position_id_edit.text()}
                        write_infos_electricity = {'position_id': self.position_id_edit.text(),
                                                   'meter_level': self.comboBox_electricity_level.currentText(),
                                                   'S': self.comboBox_strong_electricity_num.currentText(),
                                                   'W': self.comboBox_weak_electricity_num.currentText()}
                        wrint_infos_cut = {'breaker_brand': self.comboBox_cut_brand.currentText(),
                                           'breaker_model': self.comboBox_cut_model.currentText(),
                                           'breaker_heart': self.comboBox_cut_heart.currentText(),
                                           'total_cut': self.select_nums}
                        result = write_position_infos_to_sql(write_infos_position, write_infos_gateway,
                                                             write_infos_electricity, wrint_infos_cut)
                        print("[INFO 站点添加结果] ", result)
                        if result is True:
                            self.position_code[self.position_name_edit.text()] = self.gateway_serial_edit.text()
                            self.position_infos.append(self.position_name_edit.text())
                            self.init_comBbox_match()
                            QMessageBox.warning(self, 'Notice', '站点信息配置成功')
                        elif 'Duplicate' in result:
                            duplicate_content = result.split(' ')[3].replace("'", '')
                            if '壳牌' in duplicate_content:
                                self.position_infos_label.setStyleSheet("background-color: rgb(203, 203, 203);\n"
                                                                        "font: 75 12pt \"Times New Roman\";")
                                QMessageBox.warning(self, 'Notice', '充电站名称' + "【" + duplicate_content + "】" + '已存在')
                            elif 'WG' in duplicate_content:
                                self.gateway_infos_label.setStyleSheet("background-color: rgb(203, 203, 203);\n"
                                                                       "font: 75 12pt \"Times New Roman\";")
                                QMessageBox.warning(self, 'Notice', '网关序列号' + "【" + duplicate_content + "】" + '已存在')
                            elif len(duplicate_content) == 10:
                                self.electricity_infos_label.setStyleSheet("background-color: rgb(203, 203, 203);\n"
                                                                           "font: 75 12pt \"Times New Roman\";")
                                QMessageBox.warning(self, 'Notice', '充电站ID' + "【" + duplicate_content + "】" + '已存在')
                            elif len(duplicate_content) == 12:
                                self.cut_infos_label.setStyleSheet("background-color: rgb(203, 203, 203);\n"
                                                                   "font: 75 12pt \"Times New Roman\";")
                                QMessageBox.warning(self, 'Notice', "充电站ID【" + duplicate_content[
                                                                               :-2] + '】对应的断路器设备序列' + "【" + duplicate_content[
                                                                                                            -2:] + "】" + '已存在')
                        elif 'timeout' in result:
                            QMessageBox.warning(self, 'Notice', '服务器连接超时' + result)
                        elif '服务器连接超时' in result:
                            QMessageBox.warning(self, 'Notice', '服务器连接超时' + result)
                        else:
                            QMessageBox.warning(self, 'Notice', '信息配置异常' + result)
                    else:
                        self.cut_infos_label.setStyleSheet("background-color: rgb(203, 203, 203);\n"
                                                           "font: 75 12pt \"Times New Roman\";")
                        QMessageBox.warning(self, 'Notice', '请检查断路器信息是否完整及正确配置')
                else:
                    self.electricity_infos_label.setStyleSheet("background-color: rgb(203, 203, 203);\n"
                                                               "font: 75 12pt \"Times New Roman\";")
                    QMessageBox.warning(self, 'Notice', '请检查电表信息是否完整完整及正确配置')
            else:
                self.gateway_infos_label.setStyleSheet("background-color: rgb(203, 203, 203);\n"
                                                       "font: 75 12pt \"Times New Roman\";")
                QMessageBox.warning(self, 'Notice', '请检查网关信息是否完整完整及正确配置')
        else:
            self.position_infos_label.setStyleSheet("background-color: rgb(203, 203, 203);\n"
                                                    "font: 75 12pt \"Times New Roman\";")
            QMessageBox.warning(self, 'Notice', '请检查站点信息是否完整完整及正确配置')

    def printTotals(self, transferred, toBeTransferred):
        # print(transferred / toBeTransferred)
        self.progressBar.setValue(int(transferred / toBeTransferred * 100))
        pass

    def upfile(self, filesname):
        transport = paramiko.Transport(('123.60.71.211', 22))
        transport.connect(username='**', password='****')

        sftp = paramiko.SFTPClient.from_transport(transport)  # 如果连接需要密钥，则要加上一个参数，hostkey="密钥"

        sftp.put("cloudfiles/" + filesname, "/home/data/server/remotefolder/" + filesname,
                 callback=self.printTotals)  # 将本地的Windows.txt文件上传至服务器/root/Windows.txt

        transport.close()  # 关闭连接

    def downfile(self, filesname):
        transport = paramiko.Transport(('123.60.71.211', 22))
        transport.connect(username='**', password='****')

        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.get("/home/data/server/remotefolder/" + filesname, "cloudfiles/" + filesname,
                 callback=self.printTotals)  # 将Linux上的/root/Linux.txt下载到本地

        transport.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # QApplication相当于main函数，也就是整个程序（很多文件）的主入口函数。对于GUI程序必须至少有一个这样的实例来让程序运行。
    main_window = function_realization('')
    main_window.show()
    sys.exit(app.exec_())  # 调用sys库的exit退出方法，条件是app.exec_()也就是整个窗口关闭。
