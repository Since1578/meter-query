# -*- coding: utf-8 -*-
import json
import sys

import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QLineEdit

from add_position import add_position_function
from display_table import display_table_function
from mainwindow import mainwindow_function
from query_meter import query_meter_function
from Login_UI import Ui_widget  # 由.UI文件生成.py文件后，导入创建的GUI类
from sql_operation.login_mysql import  readsql
from set_time_interval import set_times_function


class Login_window(QtWidgets.QMainWindow, Ui_widget):

    # __init__: 析构函数，也就是类被创建后就会预先加载的项目。
    # 马上运行，这个方法可以用来对你的对象做一些你希望的初始化。
    def __init__(self):

        # 这里需要重载一下Login_window，同时也包含了QtWidgets.QMainWindow的预加载项。
        super(Login_window, self).__init__()
        self.count = None
        self.setupUi(self)
        self.setWindowIcon(QIcon("./shell.jpg"))
        self.setFixedSize(335, 180)
        # 将点击事件与槽函数进行连接
        self.pushButton.clicked.connect(self.btn_login_fuc)
        self.lineEdit_2.setContextMenuPolicy(Qt.NoContextMenu)  # 这个语句设置QLineEdit对象的上下文菜单的策略。复制，粘贴，。。。，是否可用
        # self.lineEdit_2.setPlaceholderText(
        # "密码不超15位，只能有数字和字母，必须以字母开头")  # 只要行编辑为空，设置此属性将使行编辑显示为灰色的占位符文本。默认情况下，此属性包含一个空字符串。这是非常好的使用方法，可以在用户输入密码前看到一些小提示信息，但是又不影响使用，非常棒这个方法。
        self.lineEdit_2.setEchoMode(QLineEdit.Password)  # 这条语句设置了如何限定输入框中显示其包含信息的方式，这里设置的是：密码方式，即输入的时候呈现出原点出来。
        self.count_infos()

    def count_infos(self):
        with open('user_count.json', 'r') as load_f:
            load_dict = json.load(load_f)
        load_f.close()
        self.count = load_dict
        if self.count['memory'] == '2':
            self.lineEdit.setText(self.count['name'])
            self.lineEdit_2.setText(self.count['password'])
            self.checkBox.setChecked(True)
        else:
            pass

    def btn_login_fuc(self):

        # 触发账号记忆配置
        if self.count['memory'] != '2' and self.checkBox.checkState() == 2:
            self.count['memory'] = '2'
            self.count['name'] = self.lineEdit.text()
            self.count['password'] = self.lineEdit_2.text()
            with open('user_count.json', 'w') as f:
                json.dump(self.count, f)
            f.close()
            # 1 获取输入的账户和密码
            account = self.lineEdit.text()  # 记得text要打括号（）！
            password = self.lineEdit_2.text()
        # 取消记忆机制
        elif self.count['memory'] == '2' and self.checkBox.checkState() != 2:
            self.count = {'memory': '', 'name': '', 'password': ''}
            with open('user_count.json', 'w') as f:
                json.dump(self.count, f)
            f.close()
            # 1 获取输入的账户和密码
            account = self.lineEdit.text()  # 记得text要打括号（）！
            password = self.lineEdit_2.text()
        # 单次登录机制
        else:
            account = self.lineEdit.text()  # 记得text要打括号（）！
            password = self.lineEdit_2.text()
        # print(account,password)
        if account == "" or password == "":
            reply = QMessageBox.warning(self, "警告", "账号密码不能为空，请输入！")
            return

        # 2 查询数据库，判定是否有匹配
        try:
            result = readsql(account, password)
            if result == 0:

                # 1打开新窗口
                mainwindow.control_name = account
                mainwindow.show()
                # 2关闭本窗口
                self.close()
            elif result == 1:
                reply = QMessageBox.warning(self, "警告", "用户名密码验证失败！")
            elif result == 2:
                reply = QMessageBox.warning(self, "警告", "用户名不存在！")
            elif result == 3:
                reply = QMessageBox.warning(self, "警告", "网络连接异常！")
        except Exception as e:
            print('[INFO] 登录超时', e)
            QMessageBox.warning(self, "警告", "登录超时，请重新登录！")


# 判断是否断网
def isConnected():
    try:
        html = requests.get("http://www.baidu.com", timeout=2)
    except:
        return False
    return True


def displayMesg(mseg):
    QMessageBox_ = QMessageBox()
    QM = QtWidgets.QMainWindow()
    QMessageBox_.setStyleSheet("background-color: rgb(0, 255, 255);")
    result = QMessageBox_.information(QM, "Notice", mseg,
                                      QMessageBox_.StandardButtons(QMessageBox_.Ok))
    if result == QMessageBox_.Ok:
        pass


if __name__ == '__main__':  # 如果这个文件是主程序。
    app = QtWidgets.QApplication(sys.argv)  # QApplication相当于main函数，也就是整个程序（很多文件）的主入口函数。对于GUI程序必须至少有一个这样的实例来让程序运行。
    login_window = Login_window()  # 生成一个登录实例（对象）
    ##
    # setup stylesheet
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'), interval=)
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    print('[INFO] 主窗口界面实例化')
    mainwindow = mainwindow_function.function_realization()  # 生成主窗口的实例
    print('[INFO] 电价配置窗口界面实例化')
    childwindow_1 = set_times_function.function_realization()  # 电价配置窗口实例化
    print('[INFO] 统计汇总表显示窗口界面实例化')
    childwindow_3 = display_table_function.function_realization(mainwindow)  # 统计汇总表显示窗口初始化
    print('[INFO] 电量查询窗口界面实例化')
    childwindow_2 = query_meter_function.function_realization(mainwindow, childwindow_3, childwindow_1)  # 电量查询窗口实例化
    # childwindow_3 = add_position_function.function_realization(mainwindow)  # 站点添加窗口实例化
    # 通过toolButton将两个窗体关联
    print('[INFO] 站点配置界面实例化')
    childwindow_4 = add_position_function.function_realization(childwindow_2)
    btn4 = mainwindow.pushButton_7
    btn4.clicked.connect(childwindow_4.show)
    print('[INFO] 显示分项时段配置窗口界面')
    btn1 = mainwindow.pushButton_5
    btn1.clicked.connect(childwindow_1.show)
    #
    print('[INFO] 显示统计分析表显示窗口界面')
    btn2 = mainwindow.pushButton_4
    btn2.clicked.connect(childwindow_2.show)
    #
    print('[INFO] 显示汇总展示窗口界面')
    btn3 = mainwindow.pushButton_8
    btn3.clicked.connect(childwindow_3.show)
    #
    print('[INFO] 显示登录窗口界面')
    login_window.show()  # 有了实例，就得让它显示。这里的show()是QWidget的方法，用来显示窗口。
    sys.exit(app.exec_())  # 调用sys库的exit退出方法，条件是app.exec_()也就是整个窗口关闭。

