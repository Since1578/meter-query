# -*- coding: utf-8 -*-
"""
@Time ： 2023/3/15 16:28
@Auth ： DingKun
@File ：mainwindow_QThread_class.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import datetime
import os
import sys
import time

from PyQt5.QtCore import QThread, pyqtSignal

from sql_operation.operation_mysql import connectMysql, query_power_value, query_meter
from base_model.statistic_time import split_time


class WorkThread_biaopan(QThread):
    # 该线程主要用于实现主界面控件的刷新与显示
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    progressBarValue = pyqtSignal(list)
    update_interval = 'hour'
    temp = {"hour": [-5, '00:30'], "tenmin": [-4, '0:30']}

    def run(self):
        #  初始化界面时，显示最新的功率
        time.sleep(2)
        conn, cursor = connectMysql()
        if conn is not False:
            try:
                data = query_power_value(cursor)
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
            else:
                conn.close()
                cursor.close()
                self.progressBarValue.emit(data)
            #  加时延防止重复查询数据库
            time.sleep(1)
        else:
            pass
        #  开始定时查询数据库，刷新最新功率数值
        while True:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if current_time[self.temp[self.update_interval][0]:] == self.temp[self.update_interval][1]:
                print('[INFO] 开始定时查询数据库，刷新最新功率数值')
                conn, cursor = connectMysql()
                if conn is not False:
                    try:
                        data = query_power_value(cursor)
                        print('[INFO] 功率数据库查询成功')
                        assert data != -1, '功率数据库查询失败'
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
                    else:
                        conn.close()
                        cursor.close()
                        self.progressBarValue.emit(data)
                    #  加时延防止重复查询数据库
                    time.sleep(1)
                else:
                    pass
            #  加时延防止主线程卡顿
            time.sleep(0.1)


class WorkThread_pyqt_plot(QThread):
    # 该线程主要用于实现主界面控件的刷新与显示
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    progressBarValue = pyqtSignal(list)
    position_infos_dict = {}
    time_mode = '24h'
    plot_type = ''  #: eg单枪排行榜（昨日所有场站的单枪充电量平均值）、充电量趋势图（显示昨日、今日充电量对比，以小时为单位）
    update_interval = 'hour'
    temp = {"tenmin": [-4, "0:50"], "hour": [-5, '00:50'], "day": [-8, '00:00:50']}

    def get_data(self, meter_data, gun_nums):
        """
        将查询到的数据进行合并处理，返回至画图函数中进行绘制
        @param meter_data: 查询数据库函数返回的数据
        @param gun_nums: 场站的充电枪数目
        @return:[handle_data, position_name]
        """
        temp = []
        for position_name, meter in meter_data.items():
            for index, object_meter in enumerate(meter):
                if self.plot_type == 'topN':
                    temp.append(object_meter['strong_meter'])
                    if index == len(meter) - 1:
                        temp = [round((temp[-1] - temp[0]) / gun_nums, 1)]
                        temp.insert(0, position_name)
                    else:
                        pass
                else:
                    if 'weak_meter' in object_meter:
                        temp.append([object_meter['strong_meter']+object_meter['weak_meter'], object_meter['time']])
                    else:
                        temp.append([object_meter['strong_meter'], object_meter['time']])
                    if index == len(meter) - 1:
                        if self.plot_type == '24h_electricity':
                            handle_data = self.combin_data_hour(temp)
                        elif self.plot_type == 'week':
                            handle_data = self.combin_data_day(temp)
                        else:
                            handle_data = self.combin_data_month(temp)
                        temp = [position_name, handle_data]
                    else:
                        pass
        return temp

    def combin_data_hour(self, datas):
        """
        根据查询结果，将时间数据按照每天进行分割，同时，统计出每小时的统计值
        @param datas: [[meter1，times1],[meter2，times2], ...]
        @return: {'2023-02-23 17:00':[2023-02-23 17:00:10, 2023-02-23 17:40:02, ...], '':[], ...}
        """
        #  单独分离出时间数据、电量数据
        times_list = [data[1] for index, data in enumerate(datas)]
        data_list = [data[0] for index, data in enumerate(datas)]
        #  按每天对时间数据进行划分
        split_result = split_time(times_list)
        return_data = {}
        #  对每小时的电量进行统计
        for time_day, value_day in split_result.items():
            #  将每天的时间划分为以小时为单位划分，并计算每小时的统计值
            return_data[time_day] = {}
            for time_hour, value_hour in split_time(value_day, split_type='hour').items():
                return_data[time_day][time_hour] = data_list[times_list.index(value_hour[-1])] - data_list[
                    times_list.index(value_hour[0])]
        return return_data

    def combin_data_day(self, datas):
        #  单独分离出时间数据、电量数据
        times_list = [data[1] for index, data in enumerate(datas)]
        data_list = [data[0] for index, data in enumerate(datas)]
        #  按每天对时间数据进行划分
        split_result = split_time(times_list)
        return_data = {}
        #  对每天的电量进行统计
        for time_day, value_day in split_result.items():
            return_data[time_day] = data_list[times_list.index(value_day[-1])] - data_list[
                times_list.index(value_day[0])]
        return return_data

    def combin_data_month(self, datas):
        #  单独分离出时间数据、电量数据
        times_list = [data[1] for index, data in enumerate(datas)]
        data_list = [data[0] for index, data in enumerate(datas)]
        #  按每周对时间数据进行划分
        split_result = split_time(times_list, split_type='month')
        return_data = {}
        #  对每月对时间数据进行划分
        for time_month, value_month in split_result.items():
            return_data[time_month] = data_list[times_list.index(value_month[-1])] - data_list[
                times_list.index(value_month[0])]
        return return_data

    def run(self):
        #  初始化界面
        time.sleep(1)
        conn, cursor = connectMysql()
        all_query_data = []
        try:
            assert conn is not False, cursor
            num_id = 0
            position_infos_dict = self.position_infos_dict(time_mode=self.time_mode)
            print(f"[INFO] {datetime.datetime.now()} 首次刷新 {self.plot_type}")
            for query_content in position_infos_dict:
                num_id += 1
                # 三个月数据查询较慢，防止连接超时，每个场站每次单独占用一个数据库连接
                if (self.time_mode == "month" or self.time_mode == 'week') and num_id == 1:
                    cursor.close()
                    conn.close()
                    conn, cursor = connectMysql()
                elif (self.time_mode == "month" or self.time_mode == 'week') and num_id != 1:
                    conn, cursor = connectMysql()
                assert conn is not False, cursor
                data = query_meter(cursor, query_content)
                if self.time_mode == "month" or self.time_mode == 'week':
                    cursor.close()
                    conn.close()
                query_data, meter_level, gun_nums = data[0], data[1], data[2]
                if query_data != -1:
                    data = self.get_data(query_data, gun_nums)
                    #print(f"[INFO] {datetime.datetime.now()} 首次刷新 {self.plot_type} {round(num_id / len(position_infos_dict) * 100, 2)}% 数据长度{len(data)}")
                    if len(data) != 0:
                        all_query_data.append(data)
            self.progressBarValue.emit([all_query_data, self.plot_type])
        except Exception as e:
            self.progressBarValue.emit([all_query_data, self.plot_type])
            except_type, except_value, except_traceback = sys.exc_info()
            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
            exc_dict = {
                "报错类型": except_type,
                "报错信息": except_value,
                "报错文件": except_file,
                "报错行数": except_traceback.tb_lineno,}
            print(exc_dict, e)
            if conn is not False:
                cursor.close()
                conn.close()
        else:
            cursor.close()
            conn.close()
        # 加时延防止重复查询数据库
        time.sleep(1)
        # 开始定时查询数据库，刷新最新单枪充电排行
        while True:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if current_time[self.temp[self.update_interval][0]:] == self.temp[self.update_interval][
                1]:  # current_time[-7:-3] == '0000-00-10 00:00:10'
                print(f"[INFO] {datetime.datetime.now()} 定时刷新 {self.plot_type}")
                conn, cursor = connectMysql()
                all_query_data = []
                try:
                    assert conn is not False, cursor
                    num_id = 0
                    position_infos_dict = self.position_infos_dict(time_mode=self.time_mode)
                    for query_content in position_infos_dict:
                        num_id += 1
                        # 三个月数据查询较慢，防止连接超时，每个场站每次单独占用一个数据库连接
                        if (self.time_mode == "month" or self.time_mode == 'week') and num_id == 1:
                            cursor.close()
                            conn.close()
                            conn, cursor = connectMysql()
                        elif (self.time_mode == "month" or self.time_mode == 'week') and num_id != 1:
                            conn, cursor = connectMysql()
                        assert conn is not False, cursor
                        data = query_meter(cursor, query_content)
                        if self.time_mode == "month" or self.time_mode == 'week':
                            cursor.close()
                            conn.close()
                        query_data, meter_level, gun_nums = data[0], data[1], data[2]
                        if query_data != -1:
                            data = self.get_data(query_data, gun_nums)
                            #print(f"[INFO] {datetime.datetime.now()} 定时刷新 {self.plot_type} {round(num_id / len(position_infos_dict) * 100, 2)}% 数据长度{len(data)}")
                            if len(data) != 0:
                                all_query_data.append(data)

                    self.progressBarValue.emit([all_query_data, self.plot_type])
                except Exception as e:
                    self.progressBarValue.emit([all_query_data, self.plot_type])
                    except_type, except_value, except_traceback = sys.exc_info()
                    except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
                    exc_dict = {
                        "报错类型": except_type,
                        "报错信息": except_value,
                        "报错文件": except_file,
                        "报错行数": except_traceback.tb_lineno,
                    }
                    print(exc_dict, e)
                    if conn is not False:
                        cursor.close()
                        conn.close()
                else:
                    cursor.close()
                    conn.close()
                #  加时延防止重复查询数据库
                time.sleep(1)
            #  加时延防止主线程卡顿
            time.sleep(0.1)
