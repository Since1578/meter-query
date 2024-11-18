import copy
import random
import sys
import datetime
import time

import matplotlib
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
from matplotlib import pyplot as plt
from scipy.interpolate import make_interp_spline
from cycler import cycler
import matplotlib.dates as mdates
import matplotlib.colors as mcolors

# from sklearn.linear_model import LinearRegression
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from base_model.statistic_time import split_time, get_time_now, calculate_time_diff, stastic_diffTime_electricity
import matplotlib.style as mplstyle

mplstyle.use('fast')
matplotlib.use("Qt5Agg")
# matplotlib.rcParams['font.sans-serif'] = ['KaiTi']  # 只有这样中文字体才可以显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


# 创建一个matplotlib图形绘制类
class MyFigure(FigureCanvas):
    def __init__(self, width, height, dpi):
        # 创建一个Figure,该Figure为matplotlib下的Figure，不是matplotlib.pyplot下面的Figure
        self.fig = plt.figure(figsize=(width, height), dpi=dpi)
        # 在父类中激活Figure窗口，此句必不可少，否则不能显示图形
        super(MyFigure, self).__init__(self.fig)
        # 调用Figure下面的add_subplot方法，类似于matplotlib.pyplot下面的subplot(1,1,1)方法


class MyFigureCanvas(FigureCanvas):
    def __init__(self, dpi=100):
        self.dpi = dpi  # 图像分辨率设置
        self.fig = Figure(dpi=self.dpi)
        self.axes = self.fig.add_subplot(111)
        # FigureCanvas.__init__(self, self.fig)
        super(FigureCanvas, self).__init__(self.fig)
        self.lined_cables_temp = {}
        self.lined_total_meter = {}
        self.lined_total_meter_usage = {}
        self.line_style = ['-'] * 20 + ['--'] * 20 + ['-.'] * 20 + [':'] * 20 + ['-'] * 20
        self.marker_ = ['x'] * 20 + ['d'] * 20 + ['p'] * 20 + ['^'] * 20 + ['o'] * 20
        self.axes.set_prop_cycle('color', plt.cm.tab20.colors)
        self.table_data = []
        self.table_header = []
        # self.axes.set_prop_cycle(custom_cycler)
        # self.dpi = dpi, dpi

    def on_pick_cables_temp(self, event):
        legl = event.artist
        origl = self.lined_cables_temp[legl]
        vis = not origl.get_visible()
        origl.set_visible(vis)
        if vis:
            legl.set_alpha(1.0)
        else:
            legl.set_alpha(0.1)
        event.canvas.draw()

    def on_pick_total_meter(self, event):
        legl = event.artist
        origl = self.lined_total_meter[legl]
        vis = not origl.get_visible()
        origl.set_visible(vis)
        if vis:
            legl.set_alpha(1.0)
        else:
            legl.set_alpha(0.1)
        event.canvas.draw()

    def on_pick_total_meter_usage(self, event):
        legl = event.artist
        origl = self.lined_total_meter_usage[legl]
        vis = not origl.get_visible()
        origl.set_visible(vis)
        if vis:
            legl.set_alpha(1.0)
        else:
            legl.set_alpha(0.1)
        event.canvas.draw()

    def position_cables_temp(self, cables_temp):
        """
        显示场站线缆温度走势图
        @param cables_temp: 原始场站的功率因素数据，[position_name, [cables_temp1, cables_temp2, ……, date]]
        @return:None
        """
        position_name = cables_temp[0][0]
        date = [i[-1] for i in cables_temp[0][1:]]
        pile_data = [i[:-1] for i in cables_temp[0][1:]]
        pile_data = np.array(pile_data)
        temp_max = np.max(pile_data)
        temp_min = np.min(pile_data)
        temp_mean = np.mean(pile_data)
        temp_std = np.std(pile_data)
        temp_diff = pile_data[:, 3:] - pile_data[:, :3]
        temp_diff_max = round(np.max(temp_diff), 1)
        temp_diff_min = round(np.min(temp_diff), 1)
        temp_diff_mean = np.round(np.mean(temp_diff), 1)
        power_factor_nums = len(cables_temp[0][1]) - 1
        legend_all = []
        # line_type = copy.deepcopy(self.line_style)
        # line_marker = copy.deepcopy(self.marker_)

        for pile in range(power_factor_nums):
            meter = pile_data[:, pile]
            leg_, = self.axes.plot_date(date, meter, linestyle='solid',#linestyle=line_type[-1], marker=line_marker[-1],
                                        linewidth=1,
                                        label=str(pile + 1))  # linestyle='solid'
            # line_type.pop()
            # line_marker.pop()
            # if len(line_type) != 0:
            #     pass
            # else:
            #     line_type = copy.deepcopy(self.line_style)
            #     line_marker = copy.deepcopy(self.marker_)
            legend_all.append(leg_)
        legend_label = ['点位' + str(pile + 1) + '出线侧线缆温度' if pile <= 2 else '点位' + str(pile + 1 - 3) + '进线侧线缆温度' for pile
                        in range(power_factor_nums)]
        x_label = "线缆温度最大值:" + str(round(temp_max, 1)) + '℃|' + "线缆温度最小值:" + str(
            round(temp_min, 1)) + '℃|' + "线缆温度平均值:" + \
                  str(np.round(temp_mean, 1)) + '\n' + "线缆进出侧温差最大值:" + str(temp_diff_max) + '℃|' + "线缆进出侧温差最小值:" + str(
            temp_diff_min) + '℃|' + "线缆进出侧温差平均值:" + str(temp_diff_mean)
        for i in range(3):
            plot_data = temp_diff[:, i]
            leg_, = self.axes.plot_date(date, plot_data, linewidth=1, linestyle='solid',
                                        label=str(i + 7))  # linestyle='solid'
            legend_all.append(leg_)
        legend_label.append("点位1进出侧线缆温度差")
        legend_label.append("点位2进出侧线缆温度差")
        legend_label.append("点位3进出侧线缆温度差")
        leg = self.axes.legend(legend_all, legend_label, loc='best', ncol=3)
        for index, value in enumerate(leg.get_lines()):
            value.set_picker(5)
            self.lined_cables_temp[value] = legend_all[index]
        self.fig.canvas.mpl_connect('pick_event', self.on_pick_cables_temp)
        locator = mdates.AutoDateLocator()  # interval_multiples=True
        flow_fmt = mdates.DateFormatter('%Y/%m/%d %H:%M')
        self.axes.xaxis.set_minor_locator(locator)
        # self.axes.xaxis.set_major_locator(mdates.MonthLocator())
        self.axes.xaxis.set_major_formatter(flow_fmt)
        self.axes.set_title(position_name + '-' + '场站线缆温度趋势图', fontsize=16)
        self.axes.set_ylabel('摄氏度', fontsize=16)
        self.axes.set_xlabel(x_label, fontsize=12)
        self.axes.ticklabel_format(axis="y", style='plain', useOffset=False)
        self.axes.grid()
        # self.fig.autofmt_xdate(rotation=90)
        self.fig.autofmt_xdate()

    def position_power_factor(self, power_factor):
        """
        显示场站功率因素走势图
        @param power_factor:原始场站的功率因素数据，[position_name, [power_factor1, power_factor2, ……, date]]
        @return:None
        """
        position_name = power_factor[0][0]
        date = [i[-1] for i in power_factor[0][1:]]
        pile_data = [i[:-1] for i in power_factor[0][1:]]
        pile_data = np.array(pile_data)
        power_factor_nums = len(power_factor[0][1]) - 1
        line_type = copy.deepcopy(self.line_style)
        line_marker = copy.deepcopy(self.marker_)
        for pile in range(power_factor_nums):
            meter = pile_data[:, pile]
            self.axes.plot_date(date, meter, linestyle=line_type[-1], marker=line_marker[-1],
                                linewidth=2)  # linestyle='solid'
            line_type.pop()
            line_marker.pop()
            if len(line_type) != 0:
                pass
            else:
                line_type = copy.deepcopy(self.line_style)
                line_marker = copy.deepcopy(self.marker_)
        legend_label = ['功率因素点位' + str(pile + 1) for pile in range(power_factor_nums)]
        self.axes.legend(labels=legend_label, loc='best', ncol=3)
        locator = mdates.AutoDateLocator()  # interval_multiples=True
        flow_fmt = mdates.DateFormatter('%Y/%m/%d %H:%M')
        self.axes.xaxis.set_minor_locator(locator)
        # self.axes.xaxis.set_major_locator(mdates.MonthLocator())
        self.axes.xaxis.set_major_formatter(flow_fmt)
        self.axes.set_title(position_name + '-' + '场站功率因素趋势图', fontsize=16)
        # self.axes.set_ylabel('kW·h', fontsize=16)
        self.axes.ticklabel_format(axis="y", style='plain', useOffset=False)
        self.axes.grid()
        # self.fig.autofmt_xdate(rotation=90)
        self.fig.autofmt_xdate()

    def usage_single_pile(self, usage_data):
        """
        显示单桩使用率
        @param usage_data: 查询场站的每台桩的使用率，['position_name', [[pile1_usage],[pile2_usage],[pile3_usage]]]
        @return:None
        """
        position_name = usage_data[0]
        usage_data_list = usage_data[1]
        pile_nums = len(usage_data_list)
        legend_label = [str(pile + 1) + '号充电桩' for pile in range(pile_nums)]
        x = legend_label
        # print("usage_data_list1", usage_data_list)
        y = [i[0] for i in usage_data_list]
        # print("usage_data_list2", y)
        for pile in range(pile_nums):
            self.axes.bar(x[pile], y[pile])
        for i, j in zip(x, y):
            self.axes.text(i, j - j / 2, str('%.1f' % j) + '%', ha="center", va="bottom")
        self.axes.tick_params(labelsize=12)
        # self.axes.grid()
        # self.axes.set_axisbelow(True)
        # self.axes.xaxis.xticks(rotation=45)
        self.axes.set_title(position_name + '-' + '单桩使用率对比图', fontsize=16)
        self.fig.autofmt_xdate()  # rotation=45
        self.axes.set_ylabel('百分比', fontsize=12)

    def meter_single_pile(self, meter_data):
        """
        显示单桩充电量走势图
        @param meter_data: 原始电量数据，[position_name, [pile1, pile2, ……, date]]
        @return:None
        """
        position_name = meter_data[0][0]
        date = [i[-1] for i in meter_data[0][1:]]
        pile_data = [i[:-1] for i in meter_data[0][1:]]
        pile_data = np.array(pile_data)
        pile_nums = len(meter_data[0][1]) - 1
        # print('pile_nums', pile_nums)
        line_type = copy.deepcopy(self.line_style)
        line_marker = copy.deepcopy(self.marker_)
        for pile in range(pile_nums):
            meter = pile_data[:, pile]
            self.axes.plot_date(date, meter, linestyle=line_type[-1], marker=line_marker[-1],
                                linewidth=2)  # linestyle='solid'
            line_type.pop()
            line_marker.pop()
            if len(line_type) != 0:
                pass
            else:
                line_type = copy.deepcopy(self.line_style)
                line_marker = copy.deepcopy(self.marker_)
        legend_label = [str(pile + 1) + '号充电桩' for pile in range(pile_nums)]
        self.axes.legend(labels=legend_label, loc='best', ncol=3)
        locator = mdates.AutoDateLocator()  # interval_multiples=True
        flow_fmt = mdates.DateFormatter('%Y/%m/%d %H:%M')
        self.axes.xaxis.set_minor_locator(locator)
        # self.axes.xaxis.set_major_locator(mdates.MonthLocator())
        self.axes.xaxis.set_major_formatter(flow_fmt)
        self.axes.set_title(position_name + '-' + '单桩总电量趋势图', fontsize=16)
        self.axes.set_ylabel('kW·h', fontsize=16)
        self.axes.ticklabel_format(axis="y", style='plain', useOffset=False)
        self.axes.grid()
        # self.fig.autofmt_xdate(rotation=90)
        self.fig.autofmt_xdate()

    def meter_single_pile_use_map(self, meter_data, time_interval='hour'):
        """
        统计指定时间段内单桩单位时间的充电量
        @param time_interval: 单位时间：year，month，day，hour
        @param meter_data: 查询到的电表数据
        @param meter_type: 显示的电量类型
        @return:None
        """
        time_interval_format = {'hour': "%Y-%m-%d %H:%M", 'day': "%Y-%m-%d", 'month': "%Y-%m", 'year': "%Y"}
        time_interval_dict = {'hour': "/小时", 'day': "/天", 'month': "/月", 'year': "/年"}
        legend_all = []
        position_name = meter_data[0][0]
        date = [i[-1] for i in meter_data[0][1:]]
        pile_data = [i[:-1] for i in meter_data[0][1:]]
        pile_data = np.array(pile_data)
        pile_nums = len(meter_data[0][1]) - 1
        split_time_data = split_time(date, split_type=time_interval)
        time_diff_data = calculate_time_diff(split_time_data)
        meter_diff = {}
        line_type = copy.deepcopy(self.line_style)
        line_marker = copy.deepcopy(self.marker_)
        for pile_id in range(pile_nums):
            for key, value in time_diff_data.items():
                meter_diff[key] = []
                for time in value:
                    index_time = date.index(time)
                    meter_diff[key].append(pile_data[index_time, pile_id])
                meter_diff[key] = meter_diff[key][0] - meter_diff[key][-1]
            x_date = [datetime.datetime.strptime(key, time_interval_format[time_interval]) for key, value in
                      meter_diff.items()]
            y_meter_diff = [value for key, value in meter_diff.items()]
            leg, = self.axes.plot_date(x_date, y_meter_diff, linestyle=line_type[-1],
                                       marker=line_marker[-1], linewidth=2)
            line_type.pop()
            line_marker.pop()
            if len(line_type) != 0:
                pass
            else:
                line_type = copy.deepcopy(self.line_style)
                line_marker = copy.deepcopy(self.marker_)
            legend_all.append(leg)
        leg = self.axes.legend(legend_all, [str(pile + 1) + '号充电桩' for pile in range(pile_nums)], loc='best', ncol=3)
        for index, value in enumerate(leg.get_lines()):
            value.set_picker(5)
            self.lined_total_meter_usage[value] = legend_all[index]
        self.fig.canvas.mpl_connect('pick_event', self.on_pick_total_meter_usage)
        locator = mdates.AutoDateLocator()  # interval_multiples=True
        flow_fmt = mdates.DateFormatter(time_interval_format[time_interval])  # '%Y/%m/%dT%H:%M'
        self.axes.xaxis.set_minor_locator(locator)
        # self.axes.xaxis.set_major_locator(mdates.MonthLocator())
        self.axes.xaxis.set_major_formatter(flow_fmt)
        self.axes.set_title(position_name + '—场站单桩用电量趋势图' + time_interval_dict[time_interval], fontsize=16)
        self.axes.set_ylabel('kW·h', fontsize=16)
        self.axes.ticklabel_format(axis="y", style='plain', useOffset=False)
        self.axes.grid()
        # self.fig.autofmt_xdate(rotation=90)
        self.fig.autofmt_xdate()

    def meter_single_gun_use_map(self, meter_data, gun_nums_list, time_interval='hour'):
        time_interval_format = {'hour': "%Y-%m-%d %H:%M", 'day': "%Y-%m-%d", 'month': "%Y-%m", 'year': "%Y"}
        time_interval_dict = {'hour': "/小时", 'day': "/天", 'month': "/月", 'year': "/年"}
        legend_all = []
        position_name_list = []
        line_type = copy.deepcopy(self.line_style)
        line_marker = copy.deepcopy(self.marker_)
        self.table_header.append('站点')
        self.table_header.append('时间')
        self.table_header.append('电量')
        self.table_header.append('统计间隔')
        self.table_header.append('电量类型')
        total_time = time.time()
        plot_nums = 0
        for index, value in enumerate(meter_data):
            plot_nums += 1
            position_name = value[0]
            position_name_list.append(position_name)
            if len(value[1]) != 0:
                date = [i[0] for i in value[1:]]
                pile_data = [sum(i[1:]) for i in value[1:]]
                t1 = time.time()
                split_time_data = split_time(date, split_type=time_interval)
                time_diff_data = calculate_time_diff(split_time_data)
                t2 = time.time()
                print(f'[INFO] {position_name} 数据长度{len(date)} 分离、计算时间差耗时:', time.time() - t1)
                meter_diff = {}
                for key, time_list in time_diff_data.items():
                    meter_diff[key] = []
                    for times in time_list:
                        index_time = date.index(times)
                        meter_diff[key].append(pile_data[index_time])
                    meter_diff[key] = meter_diff[key][0] - meter_diff[key][-1]
                x_date_ = [datetime.datetime.strptime(key, time_interval_format[time_interval]) for key, value in
                          meter_diff.items()]
                y_meter_diff_ = [round(value / gun_nums_list[position_name], 2) for key, value in meter_diff.items()]
                if len(x_date_) > 100:
                    #  保持单个场站数据最大长度为100
                    ratio = len(x_date_)//100
                    x_date = x_date_[::ratio]
                    y_meter_diff = y_meter_diff_[::ratio]
                    if x_date_[-1] not in x_date:
                        x_date.append(x_date_[-1])
                        y_meter_diff.append(y_meter_diff_[-1])

                else:
                    x_date = x_date_
                    y_meter_diff = y_meter_diff_
                # leg, = self.axes.plot_date(x_date, y_meter_diff, '-', marker='o', linewidth=2)
                for date, data in zip(x_date, y_meter_diff):
                    self.table_data.append([position_name, date.strftime(time_interval_format[time_interval]), data, time_interval_dict[time_interval], '单枪电量'])
                leg, = self.axes.plot_date(x_date, y_meter_diff, linestyle=line_type[-1],
                                           marker=line_marker[-1], linewidth=2)
                line_type.pop()
                line_marker.pop()
                if len(line_type) != 0:
                    pass
                else:
                    line_type = copy.deepcopy(self.line_style)
                    line_marker = copy.deepcopy(self.marker_)
                legend_all.append(leg)
                print(f'[INFO] {round((index+1)/plot_nums * 100)}% 单个画图耗时:', time.time() - t2)
        print(f'[INFO] {plot_nums}个场站绘图共计消耗{time.time()-total_time}s')
        t3 = time.time()
        leg = self.axes.legend(legend_all, [name for name in position_name_list], loc='best', ncol=3)
        for index, value in enumerate(leg.get_lines()):
            value.set_picker(5)
            self.lined_total_meter_usage[value] = legend_all[index]
        self.fig.canvas.mpl_connect('pick_event', self.on_pick_total_meter_usage)
        locator = mdates.AutoDateLocator()  # interval_multiples=True
        flow_fmt = mdates.DateFormatter(time_interval_format[time_interval])  # '%Y/%m/%dT%H:%M'
        self.axes.xaxis.set_minor_locator(locator)
        # self.axes.xaxis.set_major_locator(mdates.MonthLocator())
        self.axes.xaxis.set_major_formatter(flow_fmt)
        self.axes.set_title('场站单枪充电量趋势图' + time_interval_dict[time_interval], fontsize=16)
        self.axes.set_ylabel('kW·h', fontsize=16)
        self.axes.ticklabel_format(axis="y", style='plain', useOffset=False)
        self.axes.grid()
        # self.fig.autofmt_xdate(rotation=90)
        self.fig.autofmt_xdate()
        print(f'[INFO] 绘图后处理耗时{time.time() - t3}s')

    def difftime_electricity(self, meter_data):
        """
        统计不同时段每个场站的分时电量
        @param meter_data:{'position1':{"尖峰": 0, "高峰": 0, "平时": 0, "谷时": 0}, 'position2':{"尖峰": 0,
        "高峰": 0, "平时": 0, "谷时": 0}}
        @return: None
        """
        position_name = []
        top_percent = []
        high_percent = []
        ping_percent = []
        low_percent = []
        self.table_header.append('站点')
        self.table_header.append('尖峰电量')
        self.table_header.append('高峰电量')
        self.table_header.append('平时电量')
        self.table_header.append('谷时电量')
        self.table_header.append('尖峰占比')
        self.table_header.append('高峰占比')
        self.table_header.append('平时占比')
        self.table_header.append('谷时占比')
        plot_nums = 15
        for position, electricity_dict in meter_data.items():
            position_name.append(position)
            for time_type, value in electricity_dict.items():
                if time_type == "尖峰":
                    top_percent.append(value)

                elif time_type == "高峰":
                    high_percent.append(value)
                elif time_type == "平时":
                    ping_percent.append(value)
                elif time_type == "谷时":
                    low_percent.append(value)
        data = [top_percent, high_percent, ping_percent, low_percent]
        array_data_percent = np.vstack(data)
        sums_data = np.sum(data, axis=0)
        array_data_percent[0, :], array_data_percent[1, :], array_data_percent[2, :], array_data_percent[3, :] = \
            array_data_percent[0, :] / sums_data, array_data_percent[1, :] / sums_data, array_data_percent[2,
                                                                                        :] / sums_data, array_data_percent[
                                                                                                        3,
                                                                                                        :] / sums_data
        x = range(len(position_name))
        # left用来控制画当前柱状图当前层的起始位置

        self.axes.barh(x[:plot_nums], data[0][:plot_nums], label='尖峰', tick_label=position_name[:plot_nums])
        self.axes.barh(x[:plot_nums], data[1][:plot_nums], left=np.array(data[0][:plot_nums]), label='高峰', tick_label=position_name[:plot_nums])
        self.axes.barh(x[:plot_nums], data[2][:plot_nums], left=np.array(data[0][:plot_nums]) + np.array(data[1][:plot_nums]), label='平时', tick_label=position_name[:plot_nums])
        self.axes.barh(x[:plot_nums], data[3][:plot_nums], left=np.array(data[0][:plot_nums]) + np.array(data[1][:plot_nums]) + np.array(data[2][:plot_nums]), label='谷时',
                       tick_label=position_name[:plot_nums])
        for position, top, high, ping, low in zip(position_name, data[0], data[1], data[2], data[3]):
            print(position, top, high, ping, low)
            self.table_data.append([position, top, high, ping, low, round(top/(top+high+ping+low), 4), round(high/(top+high+ping+low), 4), round(ping/(top+high+ping+low), 4),
                                    round(low/(top+high+ping+low), 4)])
        top_high = np.array(data[0][:plot_nums])
        for position, high, percent in zip(x, top_high, array_data_percent[0][:plot_nums]):
            self.axes.text(high - high / 2, position, str('%.1f' % (percent * 100)) + '%', ha="center", va="center")

        high_high = np.array(data[0][:plot_nums]) + (np.array(data[1][:plot_nums])) / 2
        for position, high, percent in zip(x, high_high, array_data_percent[1][:plot_nums]):
            self.axes.text(high, position, str('%.1f' % (percent * 100)) + '%', ha="center", va="center")

        ping_high = np.array(data[0][:plot_nums]) + np.array(data[1][:plot_nums]) + np.array(data[2][:plot_nums]) / 2
        for position, high, percent in zip(x, ping_high, array_data_percent[2][:plot_nums]):
            self.axes.text(high, position, str('%.1f' % (percent * 100)) + '%', ha="center", va="center")

        low_high = np.array(data[0][:plot_nums]) + np.array(data[1][:plot_nums]) + np.array(data[2][:plot_nums]) + np.array(data[3][:plot_nums]) / 2
        for position, high, percent in zip(x, low_high, array_data_percent[3][:plot_nums]):
            self.axes.text(high, position, str('%.1f' % (percent * 100)) + '%', ha="center", va="center")
        self.axes.legend(loc='best')
        # self.axes.grid(b="True" , axis="y")
        self.axes.tick_params(labelsize=12)
        self.axes.set_title('场站分时电量占比图', fontsize=16)

    def meter_total_tidal_map(self, meter_data, meter_type):
        """
        绘制站点用电量曲线趋势图
        @param meter_type: 绘制类型，‘strong’-经营性用电，‘weak’-非经营性用电
        @param meter_data:原始电量数据，[position_name, [strong_meter, weak_meter, date]]
        @return:None
        """
        # 单个站点日/月/年
        # print(len(meter_data))
        position_name_list = []
        legend_all = []
        line_type = copy.deepcopy(self.line_style)
        line_marker = copy.deepcopy(self.marker_)
        self.table_header.append('站点')
        self.table_header.append('时间')
        self.table_header.append('截至当前总电量')
        self.table_header.append('电量类型')
        for infos in meter_data:
            position_name = infos[0]
            position_name_list.append(position_name)
            meter_temp = infos[1:]
            x = [i[2] for i in meter_temp]
            y_strong = [i[0] for i in meter_temp]
            y_weak = [i[1] for i in meter_temp]
            # 拟合数据
            # fit_meter = y[:]
            # dates, fit_meter = self.fit_meter_trend(x, fit_meter, False)
            # flow_locator = mdates.HourLocator()
            # self.axes.plot(dates, fit_meter, lw=2, color='b')  # flow_locator
            # smooth_x, smooth_y = self.smooth_curve(x, y)
            if meter_type == 'strong':
                if len(x) > 100:
                    ratio = len(x)//100
                    x_ = x[::ratio]
                    y_ = y_strong[::ratio]
                    if x[-1] not in x_:
                        x_.append(x[-1])
                        y_.append(y_strong[-1])
                else:
                    x_ = x
                    y_ = y_strong
                for position, date, data in zip([position_name] * len(x_), x_, y_):
                    self.table_data.append([position, date.strftime("%Y-%m-%d %H:%M"), data, '经营性用电'])
                leg, = self.axes.plot_date(x_, y_, linestyle=line_type[-1],
                                           marker=line_marker[-1], linewidth=2)  # linestyle='solid'
                legend_all.append(leg)
            if meter_type == 'weak':
                if len(x) > 100:
                    ratio = len(x)//100
                    x_ = x[::ratio]
                    y_ = y_weak[::ratio]
                    if x[-1] not in x_:
                        x_.append(x[-1])
                        y_.append(y_weak[-1])
                else:
                    x_ = x
                    y_ = y_weak
                for position, date, data in zip([position_name] * len(x_), x_, y_):
                    self.table_data.append([position, date.strftime("%Y-%m-%d %H:%M"), data, '非经营性用电'])
                leg, = self.axes.plot_date(x_, y_, linestyle=line_type[-1], marker=line_marker[-1],
                                           linewidth=2)  # linestyle='solid'
                legend_all.append(leg)
            line_type.pop()
            line_marker.pop()
            if len(line_type) != 0:
                pass
            else:
                line_type = copy.deepcopy(self.line_style)
                line_marker = copy.deepcopy(self.marker_)
            # self.axes.legend(labels=['万家邻里地面站-经营性用电', '万家邻里地面站-非经营性用电'], loc='best')  #, loc='upper left' legend placed at lower right ,frameon=False 去除图列边框
        # self.axes.legend(labels=[position_name for position_name in position_name_list], loc='best')
        leg = self.axes.legend(legend_all, [position_name for position_name in position_name_list], loc='best', ncol=3)
        for index, value in enumerate(leg.get_lines()):
            value.set_picker(5)
            self.lined_total_meter[value] = legend_all[index]
        self.fig.canvas.mpl_connect('pick_event', self.on_pick_total_meter)
        locator = mdates.AutoDateLocator()  # interval_multiples=True
        flow_fmt = mdates.DateFormatter('%Y/%m/%d %H:%M')
        self.axes.xaxis.set_minor_locator(locator)
        # self.axes.xaxis.set_major_locator(mdates.MonthLocator())
        self.axes.xaxis.set_major_formatter(flow_fmt)
        if meter_type == 'strong':
            self.axes.set_title('经营性总电量趋势图', fontsize=16)
        if meter_type == 'weak':
            self.axes.set_title('非经营性总电量趋势图', fontsize=16)
        self.axes.set_ylabel('kW·h', fontsize=16)
        self.axes.grid()
        self.axes.ticklabel_format(axis="y", style='plain', useOffset=False)
        # self.fig.autofmt_xdate(rotation=90)
        self.fig.autofmt_xdate()
        ##
        # legend_font = {
        #     'family': 'Times New Roman',  # 字体
        #     'style': 'normal',
        #     'size': 10,  # 字号
        #     'weight': "normal",  # 是否加粗，不加粗
        # }
        # ax.legend(labels=columns[1:32], loc='upper right', frameon=False, prop=legend_font, ncol=2)
        ##

    def meter_total_use_map(self, meter_data, meter_type='strong', time_interval='hour'):
        """
        统计指定时间段内单位时间的充电量
        @param time_interval: 单位时间：year，month，day，hour
        @param meter_data: 查询到的电表数据
        @param meter_type: 显示的电量类型
        @return:None
        """
        time_interval_format = {'hour': "%Y-%m-%d %H:%M", 'day': "%Y-%m-%d", 'month': "%Y-%m", 'year': "%Y"}
        time_interval_dict = {'hour': "/小时", 'day': "/天", 'month': "/月", 'year': "/年"}
        position_name_list = []
        legend_all = []
        line_type = copy.deepcopy(self.line_style)
        line_marker = copy.deepcopy(self.marker_)
        self.table_header.append('站点')
        self.table_header.append('时间')
        self.table_header.append('电量')
        self.table_header.append('统计间隔')
        self.table_header.append('电量类型')

        for infos in meter_data:
            if len(infos):
                position_name = infos[0]
                position_name_list.append(position_name)
                meter_temp = infos[1:]
                x_time = [i[2] for i in meter_temp]
                # print('time_interval ', time_interval)
                split_time_data = split_time(x_time, split_type=time_interval)
                # print('split_time_data ', split_time_data)
                time_diff_data = calculate_time_diff(split_time_data)
                # print('time_diff_data ', time_diff_data)
                meter_diff = {}
                y_strong = [i[0] for i in meter_temp]
                y_weak = [i[1] for i in meter_temp]
                for key, value in time_diff_data.items():
                    meter_diff[key] = []
                    for times in value:
                        index_time = x_time.index(times)
                        if meter_type == 'strong':
                            meter_diff[key].append(y_strong[index_time])
                        elif meter_type == 'weak':
                            meter_diff[key].append(y_weak[index_time])
                    meter_diff[key] = meter_diff[key][0] - meter_diff[key][-1]
                if meter_type == 'strong':
                    x_date = [datetime.datetime.strptime(key, time_interval_format[time_interval]) for key, value in
                              meter_diff.items()]
                    y_meter_diff = [value for key, value in meter_diff.items()]
                    if len(x_date) > 10000000:
                        ratio = len(x_date) // 100
                        x_date_ = x_date[::ratio]
                        y_meter_diff_ = y_meter_diff[::ratio]
                        if x_date[-1] not in x_date_:
                            x_date_.append(x_date[-1])
                            y_meter_diff_.append(y_meter_diff[-1])
                    else:
                        x_date_ = x_date
                        y_meter_diff_ = y_meter_diff
                    for position, date, data in zip([position_name] * len(x_date_), x_date_, y_meter_diff_):
                        self.table_data.append([position, date.strftime(time_interval_format[time_interval]), data, time_interval_dict[time_interval], '经营性用电'])
                    leg, = self.axes.plot_date(x_date_, y_meter_diff_, linestyle=line_type[-1],
                                               marker=line_marker[-1], linewidth=2)
                    legend_all.append(leg)
                if meter_type == 'weak':
                    x_date = [datetime.datetime.strptime(key, time_interval_format[time_interval]) for key, value in
                              meter_diff.items()]
                    y_meter_diff = [value for key, value in meter_diff.items()]
                    if len(x_date) > 10000000:
                        ratio = len(x_date) // 100
                        x_date_ = x_date[::ratio]
                        y_meter_diff_ = y_meter_diff[::ratio]
                        if x_date[-1] not in x_date_:
                            x_date_.append(x_date[-1])
                            y_meter_diff_.append(y_meter_diff[-1])
                    else:
                        x_date_ = x_date
                        y_meter_diff_ = y_meter_diff
                    for position, date, data in zip([position_name] * len(x_date_), x_date_, y_meter_diff_):
                        self.table_data.append([position, date.strftime(time_interval_format[time_interval]), data, time_interval_dict[time_interval], '非经营性用电'])
                    leg, = self.axes.plot_date(x_date_, y_meter_diff_, linestyle=line_type[-1],
                                               marker=line_marker[-1], linewidth=2)
                    legend_all.append(leg)
                line_type.pop()
                line_marker.pop()
                if len(line_type) != 0:
                    pass
                else:
                    line_type = copy.deepcopy(self.line_style)
                    line_marker = copy.deepcopy(self.marker_)
        # self.axes.legend(labels=[position_name for position_name in position_name_list], loc='best')
        leg = self.axes.legend(legend_all, [position_name for position_name in position_name_list], loc='best', ncol=3)
        for index, value in enumerate(leg.get_lines()):
            value.set_picker(5)
            self.lined_total_meter_usage[value] = legend_all[index]
        self.fig.canvas.mpl_connect('pick_event', self.on_pick_total_meter_usage)
        locator = mdates.AutoDateLocator()  # interval_multiples=True
        flow_fmt = mdates.DateFormatter(time_interval_format[time_interval])  # '%Y/%m/%dT%H:%M'
        self.axes.xaxis.set_minor_locator(locator)
        # self.axes.xaxis.set_major_locator(mdates.MonthLocator())
        self.axes.xaxis.set_major_formatter(flow_fmt)
        if meter_type == 'strong':
            self.axes.set_title('场站经营性用电量趋势图' + time_interval_dict[time_interval], fontsize=16)
        if meter_type == 'weak':
            self.axes.set_title('场站非经营性用电量趋势图' + time_interval_dict[time_interval], fontsize=16)
        self.axes.set_ylabel('kW·h', fontsize=16)
        self.axes.ticklabel_format(axis="y", style='plain', useOffset=False)
        self.axes.grid()
        # self.fig.autofmt_xdate(rotation=90)
        self.fig.autofmt_xdate()

    def date_correction(self, original_date, original_meter):
        """
        日期数据按不同时间间隔等距拆分后会存在缺失值，对其进行筛选，使x，y长度相同
        @param original_date: 从数据库中读出的抄表时间，数据格式为列表，数值类型为datetime
        @param original_meter: 对应时间下的抄表数值，数据格式为列表，数值类型为float
        @return: 对齐后的date，meter
        """
        delta = datetime.timedelta(hours=1)  # 时间间隔设置为1小时
        # 将抄表时间区间转换为mdate类型
        dates = mdates.drange(original_date[0], original_date[-1], delta=delta)
        # print(len(original_date), len(dates), original_date[0], original_date[-1], dates[-1])
        # 将原始日期和填充后的日期格式统一，方便找出缺失时间点
        x_temp = [str(i)[:-6].replace(' ', 'T') for i in original_date]
        dates_temp = [str(mdates.num2date(i))[:-12].replace(' ', 'T') for i in dates]
        # print(x_temp, dates_temp)
        fit_index = []
        # 左闭右开导致填充后的日期缺少原始日期中的最后一个数据，此处补充进来
        for index, value in enumerate(x_temp):
            if value not in dates_temp:
                dates = np.append(dates, mdates.date2num(original_date[index]))
                dates.sort()
        # 若填充后的日期不在原始日期中，则筛选出来
        for index, value in enumerate(dates_temp):
            if value not in x_temp:
                fit_index.append(index)
        # print(fit_index)
        # 根据缺失值索引对填充后的日期数据进行剔除
        dates_clear = [value for index, value in enumerate(dates) if index not in fit_index]
        # print(len(dates_clear), len(original_meter))
        return dates_clear, original_meter

    def smooth_curve(self, original_date, original_meter, is_smooth=False):
        """
        曲线平滑处理
        @param is_smooth: 是否进行曲线平滑处理
        @param original_date: 从数据库中读出的抄表时间，数据格式为列表，数值类型为datetime
        @param original_meter: 对应时间下的抄表数值，数据格式为列表，数值类型为float
        @return:平滑后的date，meter
        """
        dates, meter = self.date_correction(original_date, original_meter)
        if is_smooth:
            assert len(dates) == len(meter)
            x_smooth = np.linspace(min(dates), max(dates), 500)
            y_smooth1 = make_interp_spline(dates, meter)(x_smooth)
            return x_smooth, y_smooth1
        else:
            return dates, meter

    def fit_meter_trend(self, original_date, original_meter):
        """
        拟合由于抄表时段缺失导致的的电度数值
        @param original_date: 从数据库中读出的抄表时间，数据格式为列表，数值类型为datetime
        @param original_meter: 对应时间下的抄表数值，数据格式为列表，数值类型为float
        @return: 填充拟合后的日期及对应的电量
        """
        delta = datetime.timedelta(hours=1)  # 时间间隔设置为1小时
        # 将抄表时间区间转换为mdate类型
        dates = mdates.drange(original_date[0], original_date[-1], delta=delta)
        # 填充转换后可能存在的缺失数据
        if len(dates) != len(original_meter):
            # 将原始日期和填充后的日期格式统一，方便找出缺失时间点
            x_temp = [str(i)[:-6].replace(' ', 'T') for i in original_date]
            dates_temp = [str(mdates.num2date(i))[:-12].replace(' ', 'T') for i in dates]
            # print(x_temp, dates_temp)
            fit_index = []
            # 左闭右开导致填充后的日期缺少原始日期中的最后一个数据，此处补充进来
            for index, value in enumerate(x_temp):
                if value not in dates_temp:
                    dates = np.append(dates, mdates.date2num(original_date[index]))
                    dates.sort()
            # 若填充后的日期不在原始日期中，则筛选出来
            for index, value in enumerate(dates_temp):
                if value not in x_temp:
                    fit_index.append(index)
            # print(fit_index)
            # 根据缺失值索引对填充后的日期数据进行剔除
            dates_clear = [value for index, value in enumerate(dates) if index not in fit_index]
            # print(dates_clear, original_meter)
            # 根据清理后的填充日期和数据求拟合方程
            f = np.polyfit(dates_clear, original_meter, 3)
            p = np.poly1d(f)
            # print('p is :\n', p)
            # 根据拟合方程求缺失日期对应的电度数
            for index in fit_index:
                original_meter.insert(index, p(dates[index]))
            # original_meter.sort()
            return self.smooth_curve(dates, original_meter)
        else:
            return self.smooth_curve(dates, original_meter)


class WorkThread_plot(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    progressBarValue = pyqtSignal(int)
    gun_nums_list = []
    data = []
    display_class = ''

    def __int__(self):
        # 初始化函数
        super(WorkThread_plot, self).__init__()

    def run(self):
        for i in self.data:
            pass
            # self.progressBarValue.emit(index)  # 发送进度条的值信号


class MainWindow(QDialog):
    def __init__(self, meter_data, plot_type='total_tidal_map', meter_type='strong', time_interval='hour'):
        super().__init__()
        # self.initUI()
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('数据可视化')
        self.plot = MyFigureCanvas()
        self.table_data = self.plot.table_data
        self.table_header = self.plot.table_header
        self.meter_data = meter_data
        self.meter_type = meter_type
        self.plot_type = plot_type
        self.time_interval = time_interval

    def select_figure_type(self, gun_nums_list):
        if self.plot_type == 'total_tidal_map':
            self.plot.meter_total_tidal_map(meter_data=self.meter_data, meter_type=self.meter_type)
        elif self.plot_type == 'total_use_meter':
            self.plot.meter_total_use_map(meter_data=self.meter_data, meter_type=self.meter_type,
                                          time_interval=self.time_interval)
        elif self.plot_type == 'single_pile_tidal':
            self.plot.meter_single_pile(self.meter_data)
        elif self.plot_type == 'usage_single_pile':
            self.plot.usage_single_pile(self.meter_data)
        elif self.plot_type == "total_power_factor":
            self.plot.position_power_factor(self.meter_data)
        elif self.plot_type == "total_cables_temp":
            self.plot.position_cables_temp(self.meter_data)
        elif self.plot_type == "single_pile_use_tidal":
            self.plot.meter_single_pile_use_map(self.meter_data, time_interval=self.time_interval)
        elif self.plot_type == "single_gun_use_tidal":
            self.plot.meter_single_gun_use_map(self.meter_data, gun_nums_list, time_interval=self.time_interval)

        elif self.plot_type == "difftime_electricity":
            self.plot.difftime_electricity(self.meter_data)

    def show_figure(self, gun_nums_list):
        # self.plot = MyFigureCanvas(dpi=100)
        self.select_figure_type(gun_nums_list)
        toolbar = NavigationToolbar(self.plot, self)  # 添加matplotlib图像工具组件
        layout = QVBoxLayout()
        layout.addWidget(self.plot)
        layout.addWidget(toolbar)
        self.setLayout(layout)
        # self.plot.draw_figure()
        # self.buttonClose = QPushButton('点击此处关闭窗口')
        # self.buttonClose.clicked.connect(self.close)
        # layout.addWidget(self.buttonClose)
        # self.show()

# conn, cursor = connectMysql()
# content = ['万家邻里地面站', 'WG583LL0722052701376', '2022-07-01 14:41:00', '2024-07-18 08:09:11']
# meter_data = query_meter(cursor, content)
# data = meter_data['万家邻里地面站']
# # figure_data = [[json_dict['strong_meter'], json_dict['weak_meter'], json_dict['time']] for json_dict in data
# #                ]# if '00' == str(json_dict['time'])[-5:-3]
# figure_data = [[value for key, value in json_dict.items() if ('pile' in key) or ('time' in key)] for json_dict in data
#                ]  # if '00' == str(json_dict['time'])[-5:-3]
# figure_data.insert(0, content[0])
# print(figure_data)
# if __name__ == '__main__':
#     # when use Qwights
#     app = QApplication(sys.argv)
#     mainwindow = MainWindow([figure_data], plot_type='single_pile_tidal')
#     mainwindow.show_figure()
#     sys.exit(app.exec_())
# when use QDialog, and change  MainWindow(QWidget) to  MainWindow(QDialog), delect self.show()
# mainwindow = MainWindow([figure_data])
# mainwindow.show_figure()
# mainwindow.exec()
