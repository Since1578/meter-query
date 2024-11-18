# -*- coding: utf-8 -*-
"""
@Time ： 2022/8/29 11:38
@Auth ： DingKun
@File ：statistic_time.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import datetime

import PyQt5
import numpy as np
from PyQt5.QtCore import QDateTime

class stastic_diffTime_electricity:

    def __init__(self):
        self.all_position_difftime = {}
        self.time2electricity_dict = {}

    def caculate_diffTime_electricity(self):
        time_total = {}
        for position, time_dict in self.all_position_difftime.items():
            #  统计不同时段累计电量
            time_total[position] = {"尖峰": 0, "高峰": 0, "平时": 0, "谷时": 0}
            data = []  # [time_type, time, meter]
            for time_type, value_list in time_dict.items():

                if len(value_list) >= 2:
                    #  时间排序
                    every_day_time = split_time(value_list)
                    total_day_electricity = 0
                    for which_day, time_list in every_day_time.items():
                        every_hour_time = split_time(time_list, split_type='hour')
                        for key, value in every_hour_time.items():
                            if len(value) >= 2:
                                value_set = list(set(value))
                                value_set.sort()
                                value = value_set
                                start_electric = self.time2electricity_dict[position][time_type][value[0]]
                                end_electric = self.time2electricity_dict[position][time_type][value[-1]]
                                data.append(['', '', 0])
                                data[-1][0] = time_type
                                data[-1][1] = value[0]
                                data[-1][2] = end_electric - start_electric
                                total_day_electricity += end_electric - start_electric
                    time_total[position][time_type] = round(total_day_electricity, 2)
                else:
                    pass
            # dt = pandas.DataFrame(data)
            # # 把id设置成行索引
            # dt.columns = ['分时类型', '时间点', '用电量/每小时']
            # pandas.DataFrame.to_csv(dt,  '分时电量汇总.csv', encoding="utf_8_sig", index=False)


        print("[INFO] time_total", time_total)
        return time_total

    def judge_time_type(self, input_data, time_param):
        '''
        判断输入时间点是位于峰值还是
        @param input_time: 输入是 [ [站点1, [[电量数据1，时间点1], [电量数据2，时间点2]]] ]，类型list
        @param time_type: {"尖峰": [], "高峰": [], "平时": [], "谷时": []}
        @return:"尖峰"/"高峰"/"平时"/"谷时"
        '''
        for i in input_data:
            position_name = i[0]
            time_list = [j[1] for j in i[1:]]
            electricity = [j[0] for j in i[1:]]
            if len(electricity) >= 2:
                self.all_position_difftime[position_name] = {"尖峰": [], "高峰": [], "平时": [], "谷时": []}
                self.time2electricity_dict[position_name] = {"尖峰": {}, "高峰": {}, "平时": {}, "谷时": {}}
                for index, time_value in enumerate(time_list):
                    str_time = time_value.strftime("%Y-%m-%d %H:%M:%S")[-8:]
                    qt_time = PyQt5.QtCore.QTime.fromString(str_time, "hh:mm:ss")
                    for key, value in time_param.items():
                        # 13:00:02
                        # 遍历每个已配置的时段列表 eg："尖峰": [['10:00:00', '13:00:00'], ['13:00:00', '21:00:00']]
                        if len(value) != 0:
                            for t in value:
                                # 允许采集延迟导致的误差，容忍上限为10s，即13:00:10的数据，也算在['10:00:00', '13:00:00']区间内
                                right_time_diff = (abs(qt_time.msecsTo(t[1])) / 1000) <= 10
                                # print(t[0] <= qt_time < t[1], t[0] <= qt_time, right_time_diff)
                                if t[0] <= qt_time <= t[1]:
                                    self.all_position_difftime[position_name][key].append(time_value)
                                    self.time2electricity_dict[position_name][key][time_value] = electricity[index]
                                elif (t[0] <= qt_time) and right_time_diff:
                                    self.all_position_difftime[position_name][key].append(time_value)
                                    self.time2electricity_dict[position_name][key][time_value] = electricity[index]
                                else:
                                    continue
                        else:
                            continue
            else:
                continue


def get_time_now(date, date_format="%Y/%m/%dT%H:%M:%S"):
    """
    分离出日期的年月日
    @param date: 输入日期,字符串或datetime类型
    @param date_format: 输入为字符串时需要指定时间格式化类型
    @return:[年，月，日]
    """
    date_format = date_format
    if isinstance(date, str):
        return date[:-3]
    elif isinstance(date, datetime.datetime):
        year_month_day_hour = date
        if year_month_day_hour.month < 10:
            year_month_day_hour_month = '0' + str(year_month_day_hour.month)
        else:
            year_month_day_hour_month = str(year_month_day_hour.month)
        if year_month_day_hour.day < 10:
            year_month_day_hour_day = '0' + str(year_month_day_hour.day)
        else:
            year_month_day_hour_day = str(year_month_day_hour.day)
        if year_month_day_hour.hour < 10:
            year_month_day_hour_hour = '0' + str(year_month_day_hour.hour)
            year_month_day_hour_hour += ':00'
        else:
            year_month_day_hour_hour = str(year_month_day_hour.hour)
            year_month_day_hour_hour += ':00'
        return str(year_month_day_hour.year) + '-' + str(year_month_day_hour_month) + '-' + str(
            year_month_day_hour_day) + ' ' + str(year_month_day_hour_hour)
    else:
        return False


def split_time(date_list, split_type='day'):
    """
    将给定的日期列表，按照年/月/日单独分离出来, note:日期默认按升序排列
    @param date_list: 日期列表，数据类型为str 或 datetime
    @param split_type: year/month/day/hour
    @return: 字典——{‘day1’：[last, first],'day2':[]}
    """
    diff_time_dict = {}
    for i in range(len(date_list)):
        if get_time_now(date_list[i]):  # "%Y-%m-%d %H:%M"
            if split_type == 'hour':
                time_id = get_time_now(date_list[i])
            elif split_type == 'day':
                time_id = get_time_now(date_list[i])[:-6]
            elif split_type == 'month':
                time_id = get_time_now(date_list[i])[:-9]
            else:
                time_id = get_time_now(date_list[i])[:4]
            if time_id not in diff_time_dict:
                diff_time_dict[time_id] = []
            # if (i < len(date_list) - 1) and (split_type == 'hour') and (
            #         ((date_list[i + 1] - date_list[i]).total_seconds()) <= 660):
            #     if date_list[i] not in diff_time_dict[time_id]:
            #         diff_time_dict[time_id].append(date_list[i])
            #     diff_time_dict[time_id].append(date_list[i + 1])
            if (i < len(date_list) - 1) and (((date_list[i + 1] - date_list[i]).total_seconds()) <= 1860):
                if date_list[i] not in diff_time_dict[time_id]:
                    diff_time_dict[time_id].append(date_list[i])
                if date_list[i + 1] not in diff_time_dict[time_id]:
                    diff_time_dict[time_id].append(date_list[i + 1])
            else:
                if date_list[i] not in diff_time_dict[time_id]:
                    diff_time_dict[time_id].append(date_list[i])
    return diff_time_dict


def calculate_time_diff(split_time_dict):
    diff_time = {}
    for time, time_list in split_time_dict.items():
        # 删除时间段不足1小时的数据
        # print("diff_time", time_list)
        if (len(time_list) >= 2) and ((time_list[-1] - time_list[0]).total_seconds() >= (59 * 60)):
            diff_time[time] = [time_list[-1], time_list[0]]
    return diff_time


class calculate_pile_usage_times():
    def __init__(self, up_flag=0, down_flag=0, Begin_datetime='', End_datetime=''):
        self.up_flag = up_flag
        self.down_flag = down_flag

        self.Begin_datetime = datetime.datetime.strptime(Begin_datetime, "%Y-%m-%d %H:%M:%S")
        self.End_datetime = datetime.datetime.strptime(End_datetime, "%Y-%m-%d %H:%M:%S")

    def calculate_diff_times(self, date_dict, pile_nums):
        pile_usage_time = {}
        # 遍历每个场站
        for position_name, date_list in date_dict.items():
            # print('date_list', date_list)
            pile_usage_time[position_name] = [[] for _ in range(pile_nums)]
            #  遍历当前场站的每个桩
            # print('position_name', position_name)
            usage_time_total_list = []
            for index in range(len(date_list)):
                if len(date_list[index]) % 2 == 0:
                    pile_usage_date = date_list[index]
                else:
                    pile_usage_date = date_list[index][:-1]
                #  遍历当前桩的使用时间
                usage_time_total = 0
                for date_index in range(0, len(pile_usage_date), 2):  # 步长为2，即每两个时间为一组
                    # print((pile_usage_date[date_index + 1] - pile_usage_date[date_index]).seconds/3600)
                    usage_time_total += (pile_usage_date[date_index + 1] - pile_usage_date[date_index]).total_seconds()
                usage_time_total_list.append(usage_time_total)
                pile_usage_time[position_name][index].append(
                    round((usage_time_total / (self.End_datetime - self.Begin_datetime).total_seconds()) * 100, 1))
            print('[INFO] pile_usage_time' + '_' + position_name, list(pile_usage_time.values()), '\n',
                  usage_time_total_list)
        return list(pile_usage_time.values())[0]

    def combination_data_single_pile(self, data):
        meter_data = data
        data_temp = []
        for data in meter_data:
            temp = []
            for position_name, meter in data.items():
                temp.append([[value for key, value in i.items() if ('pile' in key) or ('time' in key)] for i in meter])
                temp[0].insert(0, position_name)
            data_temp.append(temp[0])
        return data_temp

    def statistic_use_time(self, original_data):
        """
        计算时间序列中的脉冲高电平持续时间
        @param original_data: 数据库中的电表数据，包含电度数和对应的采集时间
        @return:
        """
        data = self.combination_data_single_pile(original_data)
        pile_time_usage = {}
        for i in data:
            if len(data):
                position_name = i[0]
                pile_nums = len(i[1]) - 1
                pile_electric = np.array([j[:-1] for j in i[1:]])  # 取出电量数据
                pile_date = [j[-1] for j in i[1:]]  # 取出采集日期
                pile_time = {}
                pile_time[position_name] = [[] for id in range(pile_nums)]

                #  初始化上升、下降沿判断标志位
                for pile_id in range(pile_nums):
                    self.up_flag = 0
                    pile_id_electric = pile_electric[:, pile_id]
                    for index in range(len(pile_id_electric)):
                        #  充电状态判断
                        if pile_id_electric[index] >= 10:
                            self.up_flag += 1
                            if self.up_flag == 1:
                                pile_time[position_name][pile_id].append(pile_date[index])
                            else:
                                pass
                        #  未充电状态判断（从充电状态到结束充电状态）
                        elif pile_id_electric[index] < 10:
                            # 第一种情况，充电状态结束
                            if self.up_flag >= 1:
                                #  充电状态已结束
                                self.up_flag = 0
                                pile_time[position_name][pile_id].append(pile_date[index])
                            # 第二种情况，一直未充电
                            else:
                                pass
                    # if (self.up_flag == 1) and (self.down_flag == 1):
                    #     pile_time[position_name][pile_id].append([])
                    #     self.up_flag = 0
                    #     self.down_flag = 0
                    # else:
                    #     #  上升沿判断,初始状态为充电状态
                    #     if (pile_id_electric[index] >= 10) and (index == 0):
                    #         # print('首次检测到充电状态', pile_id, index, pile_id_electric[index], pile_date[index])
                    #         self.up_flag = 1
                    #         pile_time[position_name][pile_id][-1].append(pile_date[index])
                    #
                    #     elif (pile_id_electric[index + 1] >= pile_id_electric[index]) and (
                    #             pile_id_electric[index + 1] >= 10):
                    #         if self.up_flag != 1:
                    #             # print('首次检测到充电状态', pile_id, index, pile_id_electric[index],  pile_id_electric[index+1], pile_date[index])
                    #             pile_time[position_name][pile_id][-1].append(pile_date[index + 1])
                    #             self.up_flag = 1
                    #         else:
                    #             continue
                    #
                    #     #  下降沿判断（从充电状态到结束充电状态）
                    #     elif (pile_id_electric[index] > pile_id_electric[index + 1]) and (
                    #             pile_id_electric[index + 1] <= 10):
                    #         if self.down_flag != 1:
                    #             # print('检测充电结束状态', pile_id, index, pile_id_electric[index],  pile_id_electric[index+1], pile_date[index])
                    #             pile_time[position_name][pile_id][-1].append(pile_date[index + 1])
                    #             self.down_flag = 1
                    #         else:
                    #             continue
                # print(pile_time[position_name][0][-1], pile_time[position_name][1][-1], pile_time[position_name][2][-1], pile_time[position_name][3][-1])
                pile_time_usage[position_name] = self.calculate_diff_times(pile_time, pile_nums)
        return pile_time_usage
#
# conn, cursor = connectMysql()
# content = ['万家邻里地面站', ['2150000001', 'WG583LL0722052701376', 4], '2022-07-01 14:41:00', '2022-07-04 11:09:11']
# meter_data = [query_pile_usage(cursor, content)]#[i for i in query_meter_test(cursor, content)['万家邻里地面站']]
# a = calculate_pile_usage_times()
# a.statistic_use_time(meter_data)
