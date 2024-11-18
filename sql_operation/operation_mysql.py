# encoding: utf-8
# 使用配置文件获取数据库连接信息
# 重置主键从0开始，注：此操作会清空表内所有内容 truncate table 表名
import datetime
import os
import sys
import time
import pymysql
import tqdm
from base_model.En_DE_cryption import *
from sql_operation.login_mysql import connectMysql


def write_position_infos_to_sql(position_data=None, gateway_data=None, electricity_data=None, cut_data=None):
    conn, cursor = connectMysql()
    try:
        assert conn is not False, cursor
        now_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
        sql_position_table = "insert into position_infos(id, position_id, position_name, position_province, position_city, position_county, position_postcode, position_place" \
                             ", charge_pile_nums, charge_gun_nums, charge_AC_gun_nums, add_time) values  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        args_position = (position_data["id"],
                         position_data["position_id"], position_data["position_name"],
                         position_data["position_province"],
                         position_data["position_city"], position_data["position_county"],
                         position_data["position_postcode"],
                         position_data["position_place"], position_data["charge_pile_nums"],
                         position_data["charge_gun_nums"], position_data["charge_AC_gun_nums"], now_time)

        sql_getway_table = "insert into gateway_infos(gateway_id, position_id, gateway_brand, gateway_type, " \
                           "heart_interval, add_time) values  (%s, %s, %s, %s, %s, %s) "
        args_getway = (gateway_data['gateway_id'], gateway_data['position_id'], gateway_data['gateway_brand'],
                       gateway_data['gateway_type'], gateway_data['heart_interval'], now_time)
        sql_getway_table_2 = "insert into gateway_status(gateway_id, id) values  (%s, %s) "
        args_getway_2 = (gateway_data['gateway_id'], position_data["id"])
        sql_getway_table_3 = "insert into power_value(gateway_id) values  (%s) "
        args_getway_3 = (gateway_data['gateway_id'])

        sql_electricity_table = "insert into electricity_meter_level(position_id, meter_level, S, W, P, I, O, AC, add_time) values  (" \
                                "%s, %s, %s, %s, %s, %s, %s, %s, %s) "
        args_electricity = (
            electricity_data['position_id'], electricity_data['meter_level'], int(electricity_data['S']),
            int(electricity_data['W']), 0, 0, 0, 0, now_time)

        cursor.execute(sql_position_table, args_position)
        cursor.execute(sql_getway_table, args_getway)
        cursor.execute(sql_getway_table_2, args_getway_2)
        cursor.execute(sql_getway_table_3, args_getway_3)
        cursor.execute(sql_electricity_table, args_electricity)
        for data in cut_data['total_cut']:
            sql_cut_table = "insert into breaker_infos(breaker_id, position_id, breaker_model, breaker_485address," \
                            " breaker_brand, breaker_heart, device_serial_num, variable_name, closing_code," \
                            "opening_code, add_time) values  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            args_cut = (
                position_data["position_id"] + str(data[0]), position_data["position_id"], cut_data['breaker_model'],
                data[2], cut_data['breaker_brand'], cut_data['breaker_heart'], data[0], data[1], 1, 0, now_time)
            cursor.execute(sql_cut_table, args_cut)
        conn.commit()
    except Exception as e:
        if conn is not False:
            conn.rollback()
            conn.close()
            cursor.close()
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno}
        print(exc_dict)
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        return str(e)
    else:
        conn.close()
        cursor.close()
        return True


def query_position_data(gateway_id):
    """
    用于站点配置成功时，检验数据是否上传成功
    @return:
    """
    conn, cursor = connectMysql()
    try:
        assert conn is not False, cursor
        sql_power = "SELECT * FROM power_value WHERE gateway_id = '%s' ORDER BY collection_time desc" % (gateway_id)
        cursor.execute(sql_power)
        query_result_power = cursor.fetchone()
        sql_gateway_status = "SELECT * FROM gateway_status WHERE gateway_id = '%s' ORDER BY heart_time desc" % (gateway_id)
        cursor.execute(sql_gateway_status)
        query_result_gateway_status = cursor.fetchone()
        sql_electrivity_data = "SELECT * FROM electricity_meter_data WHERE gateway_id = '%s' ORDER BY collection_time desc" % (gateway_id)
        cursor.execute(sql_electrivity_data)
        query_result_electrivity_data = cursor.fetchone()
        # assert len(query_result) != 0, '未查询到任何站点信息'
        query_result = {'power': query_result_power, 'gateway_status': query_result_gateway_status,
                        'electrivity_data': query_result_electrivity_data}
        cursor.close()
        conn.close()
    except Exception as e:
        if conn is not False:
            cursor.close()
            conn.close()
        print(e)
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        return [False, str(e)]
    else:
        return [True, query_result]


def query_position_nums():
    conn, cursor = connectMysql()
    try:
        assert conn is not False, cursor
        sql = "SELECT * FROM position_infos"
        cursor.execute(sql)
        query_result = cursor.fetchall()
        # assert len(query_result) != 0, '未查询到任何站点信息'
    except Exception as e:
        if conn is not False:
            cursor.close()
            conn.close()
        print(e)
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        return -1
    else:
        cursor.close()
        conn.close()
        return len(query_result)


# 查询电量
def query_meter(cursor, content):
    #  content = ['', ['2150260002', 'WG583OWAN22090101203', 13, {'meter_level': 'SWP', 'S': '1', 'W': '1', 'P': '13', 'I': '0', 'O': '0', 'AC': '0'}, 26], '2023-03-10 16:
    position_name, gateway_id, begin_datetime, end_datetime = content[0], content[1][1], content[2], content[3]
    # pile_nums = content[1][2]
    gun_nums = content[1][4]

    # "SELECT id FROM electricity_meter_data LEFT JOIN salesinfo ON customerinfo.CustomerID = salesinfo.CustomerID WHERE salesinfo.CustomerID ISNULL"
    sql = "SELECT pile_meter_detail,collection_time FROM electricity_meter_data WHERE gateway_id = '%s' and collection_time >= '%s' and collection_time <='%s'" % (
        gateway_id, begin_datetime, end_datetime)
    try:
        assert content[1][3]["meter_level"] in ["IOSWPAC", "IOSWP", "IOSW", "SWPAC", "SWP",
                                                "SW", "S"], position_name + '充电站未设置电量分项等级'
        meter_nums = sum([int(value) for key, value in content[1][3].items() if key != "meter_level"])
        meter_level = content[1][3]["meter_level"]
        print("[INFO] 开始查询" + position_name, "meter_nums:", meter_nums, "gun_nums:", gun_nums)
        t1 = time.time()
        cursor.execute(sql)
        query_result = cursor.fetchall()
        print("[INFO] " + position_name + "耗时", time.time() - t1)
        assert len(query_result) != 0, '未查询到' + position_name + '电度数相关数据' + str(query_result)
        assert meter_nums == len(json.loads(query_result[-1][0])), position_name + '电量计量分项等级设置存在异常, meter_nums is:' + str(meter_nums) + ' but actually is:' + str(len(json.loads(query_result[0][0])))
        meter_dict = dict()
        meter_dict[position_name] = []
        # print(position_name + '桩数量：', content[1][2])
        for i in query_result:
            #  字符串转字典
            # temp = ast.literal_eval(i[2])
            temp = json.loads(i[0])
            temp['time'] = i[1]
            # 确保电表数据是完整的
            if len(temp) == meter_nums + 1:  # 高压进线侧电+强电+弱电+桩电+时间字段
                if None in temp.values():  # 筛选掉键值为None的字典数据
                    continue
                # 将查询到的每一条记录中的涉及到强、弱电数据分别进行累加
                all_strong = sum([value for key, value in temp.items() if "strong" in key])
                all_weak = sum([value for key, value in temp.items() if "weak" in key])
                all_strong_weak_key = list(
                    [key for key, value in temp.items() if ("strong" in key) or ("weak" in key)])
                for key in all_strong_weak_key:
                    del temp[key]
                temp["strong_meter"] = all_strong
                temp["weak_meter"] = all_weak
                meter_dict[position_name].append(temp)
        if len(meter_dict[position_name]) >= 2:
            first_time = meter_dict[position_name][0]['time']
            second_time = meter_dict[position_name][1]['time']
            if first_time >= second_time:
                del meter_dict[position_name][0]
            else:
                pass
        else:
            pass
    except Exception as e:
        print("[INFO] 数据库查询异常", e)
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        return -1, -1, -1
    else:
        return [meter_dict, meter_level, gun_nums]


#  单桩使用率查询
def query_pile_usage(cursor, content):
    # content [万家邻里地面站，['2150000001', 'WG583OWAN22090101201', 4, {'meter_level': 'SWP', 'S': '1', 'W': '1', 'P': '4',
    # 'I': '0', 'O': '0'}, 8]
    position_name, gateway_id, begin_datetime, end_datetime = content[0], content[1][1], content[2], content[3]
    pile_nums = content[1][2]
    sql = "SELECT pile_I_detail, collection_time FROM electric_current WHERE gateway_id = '%s' and collection_time >= '%s' and collection_time " \
          "<='%s' " % (gateway_id, begin_datetime, end_datetime)  # ORDER BY collection_time DESC
    try:
        assert content[1][3]["meter_level"] in ["IOSWPAC", "IOSWP", "IOSW", "SWPAC", "SWP",
                                                "SW"], position_name + '充电站未设置电量分项等级'
        cursor.execute(sql)
        query_result = cursor.fetchall()
        assert len(query_result) != 0, '未查询到' + position_name + '单桩电流相关数据'
        meter_dict = dict()
        meter_dict[position_name] = []
        # print('query_result', query_result)
        # print(position_name + '桩数量：', content[1][2])
        for i in query_result:
            #  字符串转字典
            # temp = ast.literal_eval(i[2])
            temp = json.loads(i[0])
            # 确保电表数据是完整的
            if len(temp) == pile_nums:  # 桩数量
                if None in temp.values():  # 筛选掉键值为None的字典数据
                    continue
                temp['time'] = i[1]
                meter_dict[position_name].append(temp)
        # print(meter_dict)
    except Exception as e:
        print("[INFO] 单桩使用率查询异常", e)
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        return -1
    else:
        # print(meter_dict)
        return meter_dict


#  充电站线缆温度查询
def query_cables_temp(cursor, content):
    position_name, gateway_id, begin_datetime, end_datetime = content[0], content[1][1], content[2], content[3]
    pile_nums = content[1][2]
    sql = "SELECT cables_temp, collection_time FROM cables_temp WHERE gateway_id = '%s' and collection_time >= '%s' and collection_time " \
          "<='%s' " % (gateway_id, begin_datetime, end_datetime)  # ORDER BY collection_time DESC
    try:
        cursor.execute(sql)
        query_result = cursor.fetchall()
        # print("query_result", query_result)
        assert len(query_result) != 0, '未查询到' + position_name + '线缆温度相关数据'
        meter_dict = dict()
        meter_dict[position_name] = []
        # print('query_result', query_result)
        # print(position_name + '桩数量：', content[1][2])
        for i in query_result:
            #  字符串转字典
            # temp = ast.literal_eval(i[2])
            temp = json.loads(i[0])
            # 确保电表数据是完整的
            if len(temp) == 6:  # 6点测温
                if None in temp.values():  # 筛选掉键值为None的字典数据
                    continue
                temp['time'] = i[1]
                meter_dict[position_name].append(temp)
    except Exception as e:
        print("[INFO] 线缆温度查询异常", e)
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        return -1
    else:
        return meter_dict


#  充电站功率因素查询
def query_power_factor(cursor, content):
    print('[INFO] 查询条件', content)
    # content [万家邻里地面站，['2150000001', 'WG583OWAN22090101201', 4, {'meter_level': 'SWP', 'S': '1', 'W': '1', 'P': '4',
    # 'I': '0', 'O': '0'}, 8]
    position_name, gateway_id, begin_datetime, end_datetime = content[0], content[1][1], content[2], content[3]
    #  pile_nums = content[1][2]
    sql = "SELECT power_factor, collection_time FROM power_factor WHERE gateway_id = '%s' and collection_time >= '%s' and collection_time " \
          "<='%s' " % (gateway_id, begin_datetime, end_datetime)  # ORDER BY collection_time DESC
    try:
        #  确认是否正确配置电量分项等级
        assert content[1][3]["meter_level"] in ["IOSWPAC", "IOSWP", "IOSW", "SWPAC", "SWP",
                                                "SW"], position_name + '充电站未设置电量分项等级'
        meter_nums = int(content[1][3]["S"])
        print("[INFO] 开始执行查询语句……")
        cursor.execute(sql)
        print("[INFO] 查询完毕！")
        query_result = cursor.fetchall()
        # print("query_result", query_result)
        assert len(query_result) != 0, '未查询到' + position_name + '功率因素相关数据'
        meter_dict = dict()
        meter_dict[position_name] = []
        # print('query_result', query_result)
        # print(position_name + '桩数量：', content[1][2])
        print("[INFO] 查询数据预处理中……")
        for i in query_result:
            #  字符串转字典
            # temp = ast.literal_eval(i[2])
            temp = json.loads(i[0])
            # 确保电表数据是完整的
            if len(temp) == int(meter_nums):  # 强电表数量
                if None in temp.values():  # 筛选掉键值为None的字典数据
                    continue
                temp['time'] = i[1]
                meter_dict[position_name].append(temp)
        print("[INFO] 数据预处理完毕！")
    except Exception as e:
        print("[INFO] 功率因素查询异常", e)
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        return -1
    else:
        return meter_dict


#  充电站功率查询
def query_power_value(cursor):
    sql = "SELECT * FROM power_value"  # ORDER BY collection_time DESC
    try:
        #  确认是否正确配置电量分项等级
        print("[INFO] 开始执行功率查询语句……")
        cursor.execute(sql)
        print("[INFO] 查询完毕！")
        query_result = cursor.fetchall()
        # print("query_result", query_result)
        # print('query_result', query_result)
        # print(position_name + '桩数量：', content[1][2])
        all_data = []
        print("[INFO] 查询数据预处理中……")
        for i in query_result:
            data_dict = {}
            #  字符串转字典
            # temp = ast.literal_eval(i[2])
            # 确保电表数据是完整的
            if len(i) == 0:  # 筛选掉键值为None的字典数据
                continue
            data_dict["gateway_id"] = i[0]
            data_dict["current_power"] = float(i[1])
            data_dict["times"] = i[2]
            all_data.append(data_dict)
        print("[INFO] 数据预处理完毕！")
    except Exception as e:
        print("[INFO] 功率查询异常", e)
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {
            "报错类型": except_type,
            "报错信息": except_value,
            "报错文件": except_file,
            "报错行数": except_traceback.tb_lineno,
        }
        print(exc_dict, e)
        return -1
    else:
        # print(all_data)
        return all_data


def sql_data_copy(conn, cursor, content):
    try:
        print('[INFO] 查询条件', content)
        # content: ['万家邻里地面站', ['2150000001', 'WG583LL0722052701376', 4], '2020-09-20 13:53', '2022-09-20 13:53']
        position_name, gateway_id, begin_datetime, end_datetime = content[0], content[1][1], content[2], content[3]
        pile_nums = content[1][2]
        # print(gateway_id, begin_datetime, end_datetime)
        sql = "SELECT * FROM electricity_meter_data WHERE gateway_id = '%s' and collection_time >= '%s' and collection_time <='%s' " % (
            gateway_id, begin_datetime, end_datetime)  # ORDER BY collection_time DESC
        print("[INFO] 开始执行查询语句……")
        cursor.execute(sql)
        print("[INFO] 查询完毕！")
        query_result = cursor.fetchall()
        meter_dict = dict()
        meter_dict[position_name] = []
        # print('query_result', query_result)
        # print(position_name + '桩数量：', content[1][2])
        print("[INFO] 查询数据预处理中……")
        for i in tqdm.tqdm(query_result):
            gateway_id_ob = 'WG583LL07220527013727'
            pile_meter_detial = i[2]
            collection_time = i[3]
            sql = "insert into electricity_meter_data(gateway_id, pile_meter_detial, collection_time) values  (%s, %s, %s) "
            args = (gateway_id_ob, pile_meter_detial, collection_time)
            cursor.execute(sql, args)
            conn.commit()
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
        return e
    else:
        return meter_dict

if __name__ == "__main__":
    conn, cursor = connectMysql()
    query_power_value(cursor)
    content = ['万家邻里地面站', 'WG583LL0722052701376', '2022-07-01 14:41:00', '2024-07-18 08:09:11']
    meter_data = query_meter(cursor, content)
#
# conn, cursor = connectMysql()
# content = ['2150000001', '2022-08-01 14:41:00', '2022-08-07 08:09:11']
# meter_data = query_price(cursor, content)
# conn, cursor = connectMysql()
# dict_data = {"pile_I_01": 0, "pile_I_02": 0, "pile_I_03": 0, "pile_I_04": 0}
# for i in tqdm.tqdm(range(1000)):
#     sql = "insert into electric_current(gateway_id, pile_I_detial, collection_time) values  (%s, %s, %s) "
#     if random.random() > 0.05:
#         dict_data["pile_I_01"] = 10
#     else:
#         dict_data["pile_I_01"] = round(random.random(), 2)
#     if random.random() > 0.05:
#         dict_data["pile_I_02"] = 10
#     else:
#         dict_data["pile_I_02"] = round(random.random(), 2)
#     if random.random() > 0.05:
#         dict_data["pile_I_03"] = 10
#     else:
#         dict_data["pile_I_03"] = round(random.random(), 2)
#     if random.random() > 0.05:
#         dict_data["pile_I_04"] = 10
#     else:
#         dict_data["pile_I_04"] = round(random.random(), 2)
#
#     meter_data = json.dumps(dict_data).encode('utf-8')
#     now_time = datetime.datetime.strptime('20220704050010', "%Y%m%d%H%M%S")
#     new_time = (now_time + datetime.timedelta(seconds=i*30+30)).strftime("%Y-%m-%d %H:%M:%S")
#     args = ('WG583LL0722052701376',  meter_data, new_time)
#     cursor.execute(sql, args)
#     conn.commit()
