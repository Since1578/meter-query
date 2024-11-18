# -*- coding: utf-8 -*-
"""
@Time ： 2023/8/7 13:40
@Auth ： DingKun
@File ：test.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import glob
import json
import os
import sys
import time

import pymysql



def connectMysql():
    accountInfo = "accountInfo_meter.json"
    with open(accountInfo, 'r') as load_f:
        load_dict = json.load(load_f)
    info = load_dict
    host = info['host']  # 主机ip地址
    user = info['user']  # 用户名
    passwd = info['passwd']  # 密码
    db = info['db']  # 数据库名
    charset = info['charset']  # 字符集
    # 建立一个MySQL连接（不使用配置文件，直接填入数据库连接信息）
    try:
        print("连接数据库……")
        conn = pymysql.connect(host=host, user=user, passwd=passwd, database=db, charset=charset)
        # 创建游标,给数据库发送sql指令,id已经设置为自增
        cursor = conn.cursor()
    except Exception as e:
        print("数据库连接超时")
        log_create.error('数据库连接超时' + str(e))
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {"报错类型": except_type,
                    "报错信息": except_value,
                    "报错文件": except_file,
                    "报错行数": except_traceback.tb_lineno}
        log_create.error(str(exc_dict), str(e))
        return False, '服务器连接超时' + str(e)
    else:
        print("数据库连接成功")
        return conn, cursor


if __name__ == "__main__":
    # while True:
    #     conn, cursor = connectMysql()
    #     if conn is not False:
    #         break
    #     else:
    #         time.sleep(2)
    #         conn, cursor = connectMysql()
    #         if conn is not False:
    #             break
    # -*- coding: utf-8 -*-
    old_name = glob.glob("/Volumes/NO NAME/*")
    start_no = 13
    for i in old_name:
        if "00" in i:
            continue
        else:
            new_name = "/" + i.split("/")[1] + "/" + i.split("/")[2] + "/"
            start_no += 1
            new_name = new_name + "{0:0>{1}}".format(start_no, 5) + i.split("/")[3]
            os.rename(i, new_name)
            print(new_name, i.split("/"))


