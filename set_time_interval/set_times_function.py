# -*- coding: utf-8 -*-
import PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
from .set_times_UI import Ui_Form

class function_realization(QtWidgets.QWidget, Ui_Form):

    def __init__(self):
        super(function_realization, self).__init__()
        self.setWindowIcon(QIcon("./shell.jpg"))
        self.time_flag = 0
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.box_name = []
        self.electricity_times = {"尖峰": [], "高峰": [], "平时": [], "谷时": []}
        #  初始化电价模式复选框状态
        self.price_box_model = {'尖峰': 0, '高峰': 0, '平时': 0, '谷时': 0}  # [尖峰，高峰，平时，谷时]
        #  初始化时间框数据
        self.timebox = {}  # 键对应到具体的timebox控件
        #  电价时段配置菜单栏
        self.init_price_times()
        #  电价参数配置模式刷新函数绑定
        self.init_pricemodel_box()
        self.init_timeintervalbox()
        #  电价时段配置确定按钮函数绑定
        self.pushButton.clicked.connect(self.write2dict)

    def init_price_times(self):
        #  创建菜单控件
        menu2 = QtWidgets.QMenu(self)
        #  为菜单控件对象命名
        menu2.setObjectName("menu2")
        menu3 = QtWidgets.QMenu(self)
        menu3.setObjectName("menu3")
        menu4 = QtWidgets.QMenu(self)
        menu4.setObjectName("menu4")
        menu5 = QtWidgets.QMenu(self)
        menu5.setObjectName("menu5")
        #  按钮添加菜单控件
        self.pushButton_2.setMenu(menu2)
        self.pushButton_3.setMenu(menu3)
        self.pushButton_4.setMenu(menu4)
        self.pushButton_5.setMenu(menu5)
        #  创建网格布局，用于放置控件
        self.layout2 = QtWidgets.QGridLayout()
        self.layout3 = QtWidgets.QGridLayout()
        self.layout4 = QtWidgets.QGridLayout()
        self.layout5 = QtWidgets.QGridLayout()
        #  菜单内容初始化
        layer_names = ['添加时段', '删除时段']
        for i in layer_names:
            menu_name2 = QtWidgets.QAction(i, self)
            menu_name3 = QtWidgets.QAction(i, self)
            menu_name4 = QtWidgets.QAction(i, self)
            menu_name5 = QtWidgets.QAction(i, self)
            menu2.addAction(menu_name2)
            menu3.addAction(menu_name3)
            menu4.addAction(menu_name4)
            menu5.addAction(menu_name5)
        menu2.triggered[QtWidgets.QAction].connect(self.processtrigger_class)
        menu3.triggered[QtWidgets.QAction].connect(self.processtrigger_class)
        menu4.triggered[QtWidgets.QAction].connect(self.processtrigger_class)
        menu5.triggered[QtWidgets.QAction].connect(self.processtrigger_class)
        #  建立点击菜单内容动作与要显示的控件之间的映射，用于确认哪个按钮的菜单被触发
        self.sender_dict = {}
        self.sender_dict['menu2'] = [self.layout2, '尖峰', 0]  # [时间控件对象，时段名称， 电价模式索引]
        self.sender_dict['menu3'] = [self.layout3, '高峰', 1]
        self.sender_dict['menu4'] = [self.layout4, '平时', 2]
        self.sender_dict['menu5'] = [self.layout5, '谷时', 3]
        self.timebox['尖峰'] = []
        self.timebox['高峰'] = []
        self.timebox['平时'] = []
        self.timebox['谷时'] = []

    def processtrigger_class(self, q):
        #  获得哪个按钮的菜单被触发
        sender = self.sender().objectName()
        # print(sender + 'is :', q.text(), sender)
        #  获得菜单被触发时对应要显示的控件对象
        layout_name = self.sender_dict[sender][0]
        if q.text() == "添加时段":
            btncont = layout_name.count()
            #  添加时间框
            add_result = self.add_timebox(btncont, sender, self.sender_dict[sender][1])
            if add_result != None:
                timebox, timebox2, connectLine = add_result
                layout_name.addWidget(timebox)
                layout_name.addWidget(connectLine)
                layout_name.addWidget(timebox2)
                timebox.timeChanged.connect(self.get_all_timeboxs)
                timebox2.timeChanged.connect(self.get_all_timeboxs)
                print(self.sender_dict[sender][1] + "时段添加完毕——>{}".format(layout_name.count()))
        elif q.text() == "删除时段":
            btncont = layout_name.count()
            if btncont > 0:
                self.delete_timebox(layout_name)
                print(self.sender_dict[sender][1] + "时段删除完毕——>{}".format(layout_name.count()))
            else:
                mseg = "暂未设置时段数据"
                self.displayMesg(mseg, 'onlyOk')

    def delete_timebox(self, timebox_object, delect_all=False):

        def recursion_delect(timebox_object):
            if timebox_object.count() > 0:
                item_start = timebox_object.itemAt(0)
                item_start.widget().deleteLater()
                timebox_object.removeItem(item_start)
                return recursion_delect(timebox_object)
            else:
                pass

        if delect_all:
            recursion_delect(timebox_object)
        else:
            item_list = list(range(timebox_object.count()))
            item_list.reverse()  # 倒序删除，避免影响布局顺序
            item_start = timebox_object.itemAt(item_list[0])
            item_midd = timebox_object.itemAt(item_list[1])
            item_end = timebox_object.itemAt(item_list[2])
            timebox_object.removeItem(item_start)
            timebox_object.removeItem(item_midd)
            timebox_object.removeItem(item_end)
            if item_start.widget():
                item_start.widget().deleteLater()
                # print("已删除")
            if item_midd.widget():
                item_midd.widget().deleteLater()
                # print("已删除")
            if item_end.widget():
                item_end.widget().deleteLater()
                # print("已删除")

    def add_timebox(self, btncont, sender, time_name):
        """
        添加电价时段
        :param btncont:当前时段添加控件下的时段数目
        :param sender: 当前控件信息的发送者
        :param time_name: 时间控件的名称
        :return: 新创建的一组时段
        """
        if sender == 'menu2':
            box_position = (130, 50 + (btncont) / 3 * (29 * 2), 121, 31)
        elif sender == 'menu3':
            box_position = (397, 50 + (btncont) / 3 * (29 * 2), 121, 31)
        elif sender == 'menu4':
            box_position = (671, 50 + (btncont) / 3 * (29 * 2), 121, 31)
        elif sender == 'menu5':
            box_position = (946, 50 + (btncont) / 3 * (29 * 2), 121, 31)
        if btncont / 3 < 4:
            timeEditbox = QtWidgets.QTimeEdit(self)
            timeEditbox2 = QtWidgets.QTimeEdit(self)

            timeEditbox.setGeometry(QtCore.QRect(box_position[0], box_position[1], box_position[2], box_position[3]))
            font = QtGui.QFont()
            font.setPointSize(12)
            timeEditbox.setFont(font)
            timeEditbox.setDisplayFormat('HH:mm:ss')
            timeEditbox.setObjectName(time_name + "_" + str(btncont / 3 + 1) + "_1")

            connectLine = QtWidgets.QLabel(self)
            connectLine.setGeometry(QtCore.QRect(box_position[0] + box_position[2] + 1, box_position[1] + 8, 15, 15))
            font = QtGui.QFont()
            font.setPointSize(12)
            connectLine.setFont(font)
            connectLine.setObjectName("connectLine1_{}".format(btncont / 3 + 1))
            connectLine.setText("-")

            timeEditbox2.setGeometry(
                QtCore.QRect(box_position[0] + box_position[2] + 11, box_position[1], box_position[2], box_position[3]))
            font = QtGui.QFont()
            font.setPointSize(12)
            timeEditbox2.setFont(font)
            timeEditbox2.setDisplayFormat('HH:mm:ss')
            timeEditbox2.setObjectName(time_name + "_" + str(btncont / 3 + 1) + "_2")
            # print("box_position", box_position)
            timeEditbox.show()
            timeEditbox2.show()  # 显示控件
            connectLine.show()
            # print('timeEditbox', timeEditbox)
            return [timeEditbox, timeEditbox2, connectLine]
        else:
            mseg = time_name + "时段划分最大上限为4组"
            self.displayMesg(mseg, 'onlyOk')
            return None

    def displayMesg(self, messge, param):
        if param == 'onlyOk':
            result = QMessageBox.information(self, "Notice", messge,
                                             QMessageBox.StandardButtons(QMessageBox.Ok))
            if result == QMessageBox.Ok:
                return 1
            else:
                pass
        elif param == 'bothYes_No':
            result = QMessageBox.information(self, "Notice", messge,
                                             QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No))
            if result == QMessageBox.Yes:
                return 1
            else:
                return 0

    def init_timeintervalbox(self):
        #  电价参数配置时间选择控件初始化
        # self.timeEdit_9.setDisplayFormat("HH:mm:ss")  # yyyy-MM-dd|HH:mm:ss
        self.set_time_box_status('read')
        # self.set_price_box_status('read')

    def init_pricemodel_box(self):
        #  电价参数配置模式刷新函数绑定
        self.checkBox_4.clicked.connect(self.set_time_price_box_status)
        self.checkBox_5.clicked.connect(self.set_time_price_box_status)
        self.checkBox_6.clicked.connect(self.set_time_price_box_status)
        self.checkBox_7.clicked.connect(self.set_time_price_box_status)

    #  获得所有时间框的当前数据
    def get_all_timeboxs(self):
        for key, value in self.sender_dict.items():
            #  获取layout布局中的控件数目
            btncont = value[0].count()
            #  获取layout对应的时段名称
            timebox_name = value[1]
            #  时段数据初始化
            time_content = []
            for timebox_id in range(btncont):
                # 遍历layout布局中的控件，筛选出时间控件
                if isinstance(value[0].itemAt(timebox_id).widget(), PyQt5.QtWidgets.QTimeEdit):
                    time_content.append(value[0].itemAt(timebox_id).widget().time())
                elif isinstance(value[0].itemAt(timebox_id).widget(), PyQt5.QtWidgets.QDateTimeEdit):
                    time_content.append(value[0].itemAt(timebox_id).widget().dateTime())
            self.timebox[timebox_name] = time_content
        # print('self.window.timebox', self.window.timebox)
        return self.timebox

    # 获得电价模式复选框状态
    def get_price_box_status(self):
        """
        获得电价模式复选框状态
        :return:
        """
        self.price_box_model['尖峰'] = self.checkBox_7.checkState()
        self.price_box_model['高峰'] = self.checkBox_4.checkState()
        self.price_box_model['平时'] = self.checkBox_5.checkState()
        self.price_box_model['谷时'] = self.checkBox_6.checkState()
        # print(self.window.price_box_model)

    #  设置电价时段输入框编辑属性
    def set_time_box_status(self, model):
        if model == 'read':
            for key, value in self.sender_dict.items():
                btncont = value[0].count()
                for timebox_id in range(btncont):
                    value[0].itemAt(timebox_id).widget().setEnabled(False)
                self.pushButton_2.setEnabled(False)
                self.pushButton_3.setEnabled(False)
                self.pushButton_4.setEnabled(False)
                self.pushButton_5.setEnabled(False)

        elif model == 'write':
            for key, value in self.sender_dict.items():
                btncont = value[0].count()
                for timebox_id in range(btncont):
                    value[0].itemAt(timebox_id).widget().setEnabled(False)
                self.pushButton_2.setEnabled(True)
                self.pushButton_3.setEnabled(True)
                self.pushButton_4.setEnabled(True)
                self.pushButton_5.setEnabled(True)

    def delected_timebox(self, sender, layout):
        btncont = layout.count()
        if btncont > 0:
            self.delete_timebox(layout, delect_all=True)
            print(self.sender_dict[sender][1] + "时段递归删除完毕——>{}".format(layout.count()))

    def set_time_price_box_status(self):
        self.get_price_box_status()
        box_noselected = [i for i, x in self.price_box_model.items() if x == 0]
        box_selected = [i for i, x in self.price_box_model.items() if x == 2]
        # print(box_noselected, box_selected)
        for i in box_noselected:
            if i == '尖峰':  # 尖峰时间框、电价框冻结输入权限
                layout = self.sender_dict["menu2"][0]
                self.delected_timebox("menu2", layout)
                # btncont = layout.count()
                # for timebox_id in range(btncont):
                #     layout.itemAt(timebox_id).widget().setEnabled(False)
                # self.lineEdit_4.setEnabled(False)
                self.pushButton_2.setEnabled(False)
            if i == '高峰':  # 高峰时间框、电价框冻结输入权限
                layout = self.sender_dict["menu3"][0]
                self.delected_timebox("menu3", layout)
                # btncont = layout.count()
                # for timebox_id in range(btncont):
                #     layout.itemAt(timebox_id).widget().setEnabled(False)
                # self.lineEdit.setEnabled(False)
                self.pushButton_3.setEnabled(False)
            if i == '平时':  # 平时时间框、电价框冻结输入权限
                layout = self.sender_dict["menu4"][0]
                self.delected_timebox("menu4", layout)
                # btncont = layout.count()
                # for timebox_id in range(btncont):
                #     layout.itemAt(timebox_id).widget().setEnabled(False)
                # self.lineEdit_2.setEnabled(False)
                self.pushButton_4.setEnabled(False)
            if i == '谷时':  # 谷时时间框、电价框冻结输入权限
                layout = self.sender_dict["menu5"][0]
                self.delected_timebox("menu5", layout)
                # btncont = layout.count()
                # for timebox_id in range(btncont):
                #     layout.itemAt(timebox_id).widget().setEnabled(False)
                # self.lineEdit_3.setEnabled(False)
                self.pushButton_5.setEnabled(False)
        for i in box_selected:
            if i == '尖峰':  # 尖峰时间框、电价框恢复输入权限
                layout = self.sender_dict["menu2"][0]
                btncont = layout.count()
                for timebox_id in range(btncont):
                    layout.itemAt(timebox_id).widget().setEnabled(True)
                # self.lineEdit_4.setEnabled(True)
                self.pushButton_2.setEnabled(True)
            if i == '高峰':  # 高峰时间框、电价框恢复输入权限
                layout = self.sender_dict["menu3"][0]
                btncont = layout.count()
                for timebox_id in range(btncont):
                    layout.itemAt(timebox_id).widget().setEnabled(True)
                # self.lineEdit.setEnabled(True)
                self.pushButton_3.setEnabled(True)
            if i == '平时':  # 平时时间框、电价框恢复输入权限
                layout = self.sender_dict["menu4"][0]
                btncont = layout.count()
                for timebox_id in range(btncont):
                    layout.itemAt(timebox_id).widget().setEnabled(True)
                # self.lineEdit_2.setEnabled(True)
                self.pushButton_4.setEnabled(True)
            if i == '谷时':  # 谷时时间框、电价框恢复输入权限
                layout = self.sender_dict["menu5"][0]
                btncont = layout.count()
                for timebox_id in range(btncont):
                    layout.itemAt(timebox_id).widget().setEnabled(True)
                # self.lineEdit_3.setEnabled(True)
                self.pushButton_5.setEnabled(True)

    #  写入配置好的电价
    def write2dict(self):
        #  初始化电价配置结果标志信息
        self.time_flag = 0
        #  获得所有类型的电价填入数据
        # self.get_price_box_content()
        #  获得所有类型的电价填入时段
        self.get_all_timeboxs()
        #  判断电价配置是否正确
        self.get_final_result()

    def get_final_result(self):
        #  未选择电价模式
        clicked_result = [value for key, value in self.price_box_model.items()]
        all_time_list = []
        if sum(clicked_result) == 0:
            mseg = "请至少选择一种电价模式进行更改！"
            self.displayMesg(mseg, 'onlyOk')
            self.time_flag = -1
        #  选择了电价模式
        else:
            for key, model in self.price_box_model.items():
                #  检查被选中的电价模式框填写的时间格式是否正确
                times = self.timebox[key]
                if (model == 2) and len(self.timebox[key]):
                    for index in range(0, len(times) - 1, 2):
                        if isinstance(times[index], PyQt5.QtWidgets.QDateTimeEdit) == isinstance(times[index + 1],
                                                                                                 PyQt5.QtWidgets.QDateTimeEdit):
                            self.electricity_times[key].append([times[index], times[index + 1]])
                            all_time_list.append([times[index], times[index + 1]])
                            if times[index] < times[index + 1]:
                                if (index % 2 == 0) and (index >= 2):
                                    if times[index] >= times[index - 1]:
                                        pass
                                    else:
                                        messge = key + "时段的结束日期应小于下一时段的开始日期"
                                        self.displayMesg(messge, 'onlyOk')
                                        self.time_flag = -1
                                        break
                                else:
                                    pass
                            elif self.time_flag != -1:
                                messge = key + "时段起始日期应小于结束日期"
                                self.displayMesg(messge, 'onlyOk')
                                self.time_flag = -1
                                break
                        elif self.time_flag != -1:
                            messge = '请检查' + key + "时段格式设置是否正确"
                            self.displayMesg(messge, 'onlyOk')
                            self.time_flag = -1
                            break
                elif (model == 2) and (len(self.timebox[key]) == 0):
                    messge = '请添加' + key + "时段"
                    self.displayMesg(messge, 'onlyOk')
                    self.time_flag = -1
                    break
            # 分时时段是否差值之和是否等于24小时
            if self.time_flag != -1:
                all_time_list.sort()
                check_time = 0
                for i in all_time_list:
                    check_time += i[0].msecsTo(i[1])
                print("[INFO] 24 hour check", check_time, 24 * 60 * 60 * 1000)
                if abs(check_time - (24 * 60 * 60 * 1000)) <= 1000:
                    print("[INFO] electricity_times", self.electricity_times)
                    messge = "分时时段配置完成！"
                    self.displayMesg(messge, 'onlyOk')
                else:
                    messge = "请确认当前各时段是否构成完整的24小时"
                    self.displayMesg(messge, 'onlyOk')
                    self.electricity_times = {"尖峰": [], "高峰": [], "平时": [], "谷时": []}
            else:
                self.electricity_times = {"尖峰": [], "高峰": [], "平时": [], "谷时": []}
