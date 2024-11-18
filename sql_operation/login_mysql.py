# encoding: utf-8
import os
import sys
import pymysql
import requests
from base_model.En_DE_cryption import *


# 使用配置文件获取数据库连接信息
# 连接数据库
def connectMysql():
    accountInfo = "accountInfo_meter.json"
    with open(accountInfo, 'r') as load_f:
        load_dict = json.load(load_f)
    pc = prpcrypt('Aslkfsjlsd5SA@#$%sd151dsf!')
    info = load_dict
    host = pc.decrypt(info['host'].encode())  # 主机ip地址
    user = pc.decrypt(info['user'].encode())  # 用户名
    passwd = pc.decrypt(info['passwd'].encode())  # 密码
    db = pc.decrypt(info['db'].encode())  # 数据库名
    charset = pc.decrypt(info['charset'].encode())  # 字符集
    # 建立一个MySQL连接（不使用配置文件，直接填入数据库连接信息）
    try:
        conn = pymysql.connect(host=host, user=user, passwd=passwd, database=db, charset=charset)
        # 创建游标,给数据库发送sql指令,id已经设置为自增
        cursor = conn.cursor()
    except Exception as e:
        print('[INFO ] 数据库连接超时' + str(e))
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        return False, '服务器连接超时' + str(e)
    else:
        return conn, cursor


# 判断是否断网
def isConnected():
    try:
        html = requests.get("http://www.baidu.com", timeout=2)
    except:
        return False
    return True


def readsql(name_en, password):
    """
    infors =
    """
    if isConnected():
        conn, cursor = connectMysql()
        try:
            assert conn != False, cursor
            print('[INFO] 当前输入用户名', name_en)
            sql = "SELECT * FROM count WHERE user = %s" % ('\'' + name_en + '\'')
            # 执行SQL语句
            cursor.execute(sql)
            # print(cursor)
            results = cursor.fetchall()
            # print(results)
            assert len(results) != 0
        except Exception as e:
            print("[INFO] warning: no this user data!")
            except_type, except_value, except_traceback = sys.exc_info()
            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
            exc_dict = {
                "报错类型": except_type,
                "报错信息": except_value,
                "报错文件": except_file,
                "报错行数": except_traceback.tb_lineno,
            }
            print(exc_dict, e)
            if conn != False:
                cursor.close()
                conn.close()
            recall = False
        else:
            recall = True
        #######################
        if recall:
            password_mysql = results[-1][-1]
            # print(password_mysql, password)
            if password == password_mysql:
                print('[INFO] 用户名密码验证成功！')
                # 关闭游标
                cursor.close()
                # # 关闭数据库连接
                conn.close()
                return 0
            else:
                # 关闭游标
                cursor.close()
                # # 关闭数据库连接
                conn.close()
                print('[INFO] 用户名密码验证失败！')
                return 1
        else:
            # 关闭游标
            cursor.close()
            # # 关闭数据库连接
            conn.close()
            print('[INFO] 用户名不存在！')
            return 2
    else:
        print('[INFO] 网络连接异常！')
        return 3


def get_region_relation():
    print("[INFO] 站点信息初始化中……")
    position_dict = {}
    # {'万家邻里地面站': ['2150000001', 'WG583OWAN22090101201', 4, 'SWP-1_1_4', 8], '百购商业广场地下站': ['2150000003',
    # 'WG583OWAN22090101208'
    print("[INFO ] 网络状态确认中…………")
    if isConnected():
        print("[INFO ] 连接数据库中…………")
        conn, cursor = connectMysql()
        try:
            assert conn != False, cursor
            print("[INFO ] 网关信息初始化中…………")
            all_gateway = get_all_gateway(cursor)
            print("[INFO ] 电表等级信息初始化中…………")
            all_meter_level = get_all_meter_level(cursor)
            sql = "SELECT * FROM position_infos"
            # 执行SQL语句
            cursor.execute(sql)
            # print(cursor)
            results = cursor.fetchall()
            assert len(results) != 0
        except Exception as e:
            print("[INFO] warning: no  data!", str(e))
            except_type, except_value, except_traceback = sys.exc_info()
            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
            exc_dict = {
                "报错类型": except_type,
                "报错信息": except_value,
                "报错文件": except_file,
                "报错行数": except_traceback.tb_lineno,
            }
            print(exc_dict, e)
            if conn != False:
                cursor.close()
                conn.close()
            return 'sqlfiled'
        else:
            print("[INFO ] 站点信息映射建立中…………")
            if results:
                position_dict['city'] = {}
                for i in results:
                    if i[7] not in position_dict['city']:
                        position_dict['city'][i[7]] = {'region': {}}
                        position_dict['city'][i[7]]['region'][i[8]] = {'position': {}}
                        if i[1] in all_gateway:
                            position_dict['city'][i[7]]['region'][i[8]]['position'][i[2]] = [i[1], all_gateway[i[1]],
                                                                                             i[-4],
                                                                                             all_meter_level[i[1]],
                                                                                             i[-3]]
                        else:
                            position_dict['city'][i[7]]['region'][i[8]]['position'][i[2]] = [i[1], None, i[-4],
                                                                                             all_meter_level[i[1]],
                                                                                             i[-3]]
                    else:
                        if i[8] not in position_dict['city'][i[7]]['region']:
                            position_dict['city'][i[7]]['region'][i[8]] = {'position': {}}
                            if i[1] in all_gateway:
                                position_dict['city'][i[7]]['region'][i[8]]['position'][i[2]] = [i[1],
                                                                                                 all_gateway[i[1]],
                                                                                                 i[-4],
                                                                                                 all_meter_level[i[1]],
                                                                                                 i[-3]]
                            else:
                                position_dict['city'][i[7]]['region'][i[8]]['position'][i[2]] = [i[1], None, i[-4],
                                                                                                 all_meter_level[i[1]],
                                                                                                 i[-3]]
                        else:
                            if i[1] in all_gateway:
                                position_dict['city'][i[7]]['region'][i[8]]['position'][i[2]] = [i[1],
                                                                                                 all_gateway[i[1]],
                                                                                                 i[-4],
                                                                                                 all_meter_level[i[1]],
                                                                                                 i[-3]]
                            else:
                                position_dict['city'][i[7]]['region'][i[8]]['position'][i[2]] = [i[1], None, i[-4],
                                                                                                 all_meter_level[i[1]],
                                                                                                 i[-3]]
                #print("[INFO] 站点信息初始化完毕\n", position_dict)
                cursor.close()
                conn.close()
                return position_dict
            else:
                cursor.close()
                conn.close()
                return 'sqlfiled'
    else:
        return 'netfiled'


def get_all_meter_level(cursor):
    print("[INFO] 正在查询指定场站电量分项等级信息……")
    meter_level_dict = {}
    sql = "SELECT * FROM electricity_meter_level"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # print(cursor)
        results = cursor.fetchall()
        # print(results)
        assert len(results) != 0
    except Exception as e:
        print("[INFO] warning: no this user data!")
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        results = False
    #######################
    if results:
        for i in results:
            meter_level_dict[i[0]] = {'meter_level': i[1], 'S': i[2], 'W': i[3], 'P': i[4], 'I': i[5], 'O': i[6],
                                      'AC': i[7]}
        #print('meter_level_dict', meter_level_dict)
        return meter_level_dict
    else:
        return 'sqlfiled'


def get_all_gateway(cursor):
    print("[INFO] 正在查询指定场站网关参数信息……")
    gateway_dict = {}
    sql = "SELECT * FROM gateway_infos"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # print(cursor)
        results = cursor.fetchall()
        # print(results)
        assert len(results) != 0
    except Exception as e:
        print("[INFO] warning: no this user data!")
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        results = False
    #######################
    if results:
        for i in results:
            gateway_dict[i[1]] = i[0]
        # print('getway_dict', getway_dict)
        return gateway_dict
    else:
        return 'sqlfiled'

# print(get_all_gateway())
# get_region_relation()
# get_all_meter_level()
# get_region_relation()
