# -*- coding: utf-8 -*-
"""
@Time ： 2022/8/30 9:57
@Auth ： DingKun
@File ：menu_test.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""

import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, qApp
from PyQt5.QtGui import QIcon

class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.my_initUI()

    def my_initUI(self):
        exitAct = QAction(QIcon('images/exit.ico'), '退出&(Q)', self)     #创建QAction类的对象exitAct。QAction是一个用于菜单栏、工具栏或自定义快捷键的抽象动作行为
        exitAct.setShortcut('Ctrl+Q')    			#调用对象的方法,为这个动作定义一个快捷键
        exitAct.setStatusTip('退出应用')   	#创建一个当我们鼠标浮于菜单项之上就会显示的一个状态提示
        exitAct.triggered.connect(qApp.quit)      #选中特定的动作，触发信号被发射。信号连接到 QApplication组件的 quit()方法，这样就中断了应用
        # self.statusBar()      					#创建状态栏，用来显示上面的状态提示

        menubar = self.menuBar()            	# menuBar()方法创建了一个菜单栏
        fileMenu = menubar.addMenu('文件&(F)')        #创建一个文件菜单，设置快捷键F
        fileMenu2 = fileMenu.addMenu('test1')
        fileMenu2.setObjectName('test1')
        fileMenu3 = fileMenu.addMenu('test2')
        fileMenu3.setObjectName('test2')
        fileMenu2.addAction('s')                 #将退出动作添加到file菜单中
        fileMenu3.addAction('s')
        #menubar.triggered.connect(self.processtrigger_class_2)
        fileMenu2.triggered[QAction].connect(self.processtrigger_class_2)
        fileMenu3.triggered[QAction].connect(self.processtrigger_class_2)
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle('菜单栏')
        self.show()

    def processtrigger_class_2(self, q):
        print(self.sender().objectName(), q.text())


if __name__=='__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
