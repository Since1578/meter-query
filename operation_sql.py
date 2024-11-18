# -*- coding: utf-8 -*-
"""
@Time ： 2023/7/31 14:13
@Auth ： DingKun
@File ：SaveToMySQL.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
import json
import logging
import os
import sys
import pymysql
from log import log_create

accountInfo = {"host": "192.168.0.95",
               "user": "root",
               "passwd": "qazWSX123EDC-",
               "db": "emqx_yiwei",
               "charset": "utf8"
               }


def connectMysql():
    # accountInfo = "accountInfo_meter.json"
    # with open(accountInfo, 'r') as load_f:
    #     load_dict = json.load(load_f)
    info = accountInfo  # load_dict
    host = info['host']  # 主机ip地址
    user = info['user']  # 用户名
    passwd = info['passwd']  # 密码
    db = info['db']  # 数据库名
    charset = info['charset']  # 字符集
    # 建立一个MySQL连接（不使用配置文件，直接填入数据库连接信息）
    try:
        conn = pymysql.connect(host=host, user=user, passwd=passwd, database=db, charset=charset)
        # 创建游标,给数据库发送sql指令,id已经设置为自增
        cursor = conn.cursor()
    except Exception as e:
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
        return conn, cursor


def saveToMysql(conn, cursor, topic, data):
    try:
        if "meter_detail" in topic:
            sql = "insert into electricity_meter_data(gateway_id, pile_meter_detail, collection_time) values  (%s, %s, %s)"
            gateway_id, meter_detail, collection_time = data["gateway_id"], json.dumps(data["pile_meter_detail"]), data[
                "collection_time"]
            args = (gateway_id, meter_detail, collection_time)
            cursor.execute(sql, args)
            conn.commit()
        elif "gateway_heart" in topic:
            sql = "update gateway_status set heart_time = %s where gateway_id = %s"
            gateway_id, heart_time = data["gateway_id"], data["heart_time"]
            args = (heart_time, gateway_id)
            cursor.execute(sql, args)
            conn.commit()
        elif "position_branch_box_temperature" in topic:
            sql = "insert into cables_temp(gateway_id, cables_temp, collection_time) values  (%s, %s, %s)"
            gateway_id, cables_temp, collection_time = data["gateway_id"], json.dumps(data["cables_temp"]), data[
                "collection_time"]
            args = (gateway_id, cables_temp, collection_time)
            cursor.execute(sql, args)
            conn.commit()
        elif "position_pile_I" in topic:
            sql = "insert into electric_current(gateway_id, pile_I_detail, collection_time) values  (%s, %s, %s)"
            gateway_id, pile_I_detail, collection_time = data["gateway_id"], json.dumps(data["pile_I_detail"]), data[
                "collection_time"]
            args = (gateway_id, pile_I_detail, collection_time)
            cursor.execute(sql, args)
            conn.commit()
        elif "position_total_power" in topic:
            sql = "update power_value set current_power = %s, collection_time = %s where gateway_id = %s"
            gateway_id, current_power, collection_time = data["gateway_id"], data["current_power"], data[
                "collection_time"]
            args = (current_power, collection_time, gateway_id)
            cursor.execute(sql, args)
            conn.commit()
        elif "position_power_history" in topic:
            sql = "insert into power_value_history(gateway_id, current_power, collection_time) values (%s, %s, %s)"
            gateway_id, current_power, collection_time = data["gateway_id"], data["current_power"], data[
                "collection_time"]
            args = (gateway_id, current_power, collection_time)
            cursor.execute(sql, args)
            conn.commit()
        else:
            pass

    except Exception as e:
        log_create.error('数据库操作失败' + str(e))
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {"报错类型": except_type,
                    "报错信息": except_value,
                    "报错文件": except_file,
                    "报错行数": except_traceback.tb_lineno}
        log_create.error(str(exc_dict), str(e))
