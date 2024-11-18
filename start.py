# -*- coding: utf-8 -*-
"""
@Time ： 2023/7/27 15:16
@Auth ： DingKun
@File ：start.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
# 当代理响应订阅请求时被调用。
import datetime
import json
import os
import sys
import threading
import time
from log import log_create
import paho.mqtt.client as mqtt
from operation_sql import connectMysql, saveToMysql

a = {"devList": [{"varList": {"weak_meter": 132.25, "strong_meter": 12095.72},
                  "devSn": "WG583OWAN23062902724", "devSort": "meter_total", "ts": 1690360200}],
     "cmdId": 103, "type": 0, "ver": "0.5.1.0", "seq": "ff233cfe-48cc-46fa-8386-b22d990bb7f6",
     "time": "2023-07-26 16:30:02"}
#  场站各级电表数据信息详情
#  eg: {"devList":[{"varList":{"weak_meter":132.25,"strong_meter":12095.72},
# "devSn":"WG583OWAN23062902724","devSort":"meter_total","ts":1690360200}],
# "cmdId":103,"type":0,"ver":"0.5.1.0","seq":"ff233cfe-48cc-46fa-8386-b22d990bb7f6","time":"2023-07-26 16:30:02"}
mqtt_msg_electricity_detial = []
#  场站总功率信息
mqtt_msg_position_power = []
#  场站网关心跳时间信息
mqtt_msg_gateway_heart = []
#  场站充电桩A项电流数据信息详情，用于统计单桩使用率
mqtt_msg_electrical_A = []
#  场站分支箱线缆温度
mqtt_msg_cables_temp = []
#  场站总功率历史
mqtt_msg_position_power_history = []
#  订阅主题
sub_topic_electricity_detial = 'emqx_mqtt_send/meter_detail'
sub_topic_gateway_heart = 'emqx_mqtt_send/gateway_heart'
sub_topic_position_branch_box_temperature = 'emqx_mqtt_send/position_branch_box_temperature'
sub_topic_position_pile_I = 'emqx_mqtt_send/position_pile_I'
sub_topic_position_power_history = 'emqx_mqtt_send/position_power_history'
#  sub_topic_position_total_power = 'emqx_mqtt_send/position_total_power'
#  sub_topic_position_total_power,
#  sub_topic_position_total_power: "recv_position_total_power"
#  sub_topic_position_total_power: mqtt_msg_position_power
sub_topic = [sub_topic_electricity_detial,
             sub_topic_gateway_heart,
             sub_topic_position_branch_box_temperature,
             sub_topic_position_pile_I,
             sub_topic_position_power_history
             ]

user_name_list = {sub_topic_electricity_detial: 'recv_electricity_meter',
                  sub_topic_gateway_heart: "recv_gateway_heart",
                  sub_topic_position_branch_box_temperature: "recv_position_branch_box_temperature",
                  sub_topic_position_pile_I: "recv_position_pile_I",
                  sub_topic_position_power_history: "recv_position_power_history"
                  }

topic_mesg_dict = {sub_topic_electricity_detial: mqtt_msg_electricity_detial,
                   sub_topic_gateway_heart: mqtt_msg_gateway_heart,
                   sub_topic_position_branch_box_temperature: mqtt_msg_cables_temp,
                   sub_topic_position_pile_I: mqtt_msg_electrical_A,
                   sub_topic_position_power_history: mqtt_msg_position_power_history
                   }


# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         log_create.info(f"{client} 连接成功")
#     else:
#         log_create.error(f"{client} 连接失败")
#     log_create.info(f"Connected with result code {rc}")

def on_connect(client, userdata, flag, rc):
    if rc == 0:
        # 连接成功
        log_create.info(f"{client} 连接成功")
    elif rc == 1:
        # 协议版本错误
        log_create.error(f"Connected with result code {rc}: Protocol version error")
    elif rc == 2:
        # 无效的客户端标识
        log_create.error(f"Connected with result code {rc}: Invalid client identity")
    elif rc == 3:
        # 服务器无法使用
        log_create.error(f"Connected with result code {rc}: server unavailable")
    elif rc == 4:
        # 错误的用户名或密码
        log_create.error(f"Connected with result code {rc}: Wrong user name or password")
    elif rc == 5:
        # 未经授权
        log_create.error(f"Connected with result code {rc}: unaccredited")


# 当代理响应订阅请求时被调用
def on_subscribe(client, userdata, mid, granted_qos):
    log_create.info(f"Subscribed: {mid} {granted_qos}")


# 当使用使用publish()发送的消息已经传输到代理时被调用。
def on_publish(client, obj, mid):
    log_create.info(f"OnPublish, mid: {mid}")


# 当收到关于客户订阅的主题的消息时调用。 message是一个描述所有消息参数的MQTTMessage。
def on_message(client, userdata, msg):
    log_create.info(f"接收主题消息内容 \n {msg.topic} {msg.payload}")
    decode_msg = json.loads(msg.payload)
    try:
        if "meter_detail" in msg.topic:
            save_data = {"pile_meter_detail": decode_msg["varList"], "gateway_id": decode_msg["gateway_id"],
                         "collection_time": decode_msg["time"]}
            topic_mesg_dict[msg.topic].append(save_data)
            # mqtt_msg.append(json.loads(msg.payload))
        elif "gateway_heart" in msg.topic:
            save_data = {"gateway_id": decode_msg["gateway_id"], "heart_time": decode_msg["time"]}
            topic_mesg_dict[msg.topic].append(save_data)
        elif "position_branch_box_temperature" in msg.topic:
            save_data = {"gateway_id": decode_msg["gateway_id"], "cables_temp": decode_msg["varList"],
                         "collection_time": decode_msg["time"]}
            topic_mesg_dict[msg.topic].append(save_data)
        elif "position_pile_I" in msg.topic:
            save_data = {"gateway_id": decode_msg["gateway_id"], "pile_I_detail": decode_msg["varList"],
                         "collection_time": decode_msg["time"]}
            topic_mesg_dict[msg.topic].append(save_data)
        elif "position_total_power" in msg.topic:
            save_data = {"gateway_id": decode_msg["gateway_id"], "current_power": decode_msg["current_power"],
                         "collection_time": decode_msg["time"]}
            topic_mesg_dict[msg.topic].append(save_data)
        elif "position_power_history" in msg.topic:
            if "power_total" in decode_msg["varList"]:
                save_data = {"gateway_id": decode_msg["gateway_id"], "current_power": decode_msg["varList"]["power_total"],
                             "collection_time": decode_msg["time"]}
                topic_mesg_dict[msg.topic].append(save_data)
            else:
                pass
        else:
            pass
    except Exception as e:
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {"报错类型": except_type,
                    "报错信息": except_value,
                    "报错文件": except_file,
                    "报错行数": except_traceback.tb_lineno}
        log_create.error(str(exc_dict), str(e))


# 当客户端有日志信息时调用
def on_log(client, obj, level, string):
    # print(f"[INFO]: {datetime.datetime.now()}: Log Information  {client} + {' '} + {string}")
    pass


def task_thread(sub_topic):
    # step
    broker = '123.60.89.151'
    port = 1884
    client_id = f'python-mqtt-{datetime.datetime.now()}'
    # 如果 broker 需要鉴权，设置用户名密码
    # username = 'SaveToMySQL'
    password = '5847588'
    try:
        client = mqtt.Client(client_id)
        client.username_pw_set(user_name_list[sub_topic], password)
        # client.username_pw_set("admin", "password")
        # 回调函数
        client.on_connect = on_connect
        client.on_subscribe = on_subscribe
        client.on_message = on_message
        client.on_log = on_log
        # host为启动的broker地址 举例本机启动的ip 端口默认1883
        client.connect(host=broker, port=port, keepalive=60)  # 订阅频道
        time.sleep(1)
        # 多个主题采用此方式
        # client.subscribe([("demo", 0), ("test", 2)])      #  test主题，订阅者订阅此主题，即可接到发布者发布的数据
        # 订阅主题 实现双向通信中接收功能，qs质量等级为2
        client.subscribe((sub_topic, 2))
        client.loop_start()
        log_create.info(f"{sub_topic}  订阅线程启动")
        temp_data = []
    except Exception as e:
        except_type, except_value, except_traceback = sys.exc_info()
        except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
        exc_dict = {"报错类型": except_type,
                    "报错信息": except_value,
                    "报错文件": except_file,
                    "报错行数": except_traceback.tb_lineno}
        log_create.error(str(exc_dict), str(e))
    else:
        while True:
            # log_create.info(f" 线程循环 {sub_topic}  {topic_mesg_dict[sub_topic]} {len(topic_mesg_dict[sub_topic])} ")
            #  判断来自EMQX MQTT桥接的主题消息是否在持续发送中
            if len(topic_mesg_dict[sub_topic]) > 0:
                #  添加每一条主题消息至临时变量
                temp_data.append(topic_mesg_dict[sub_topic][0])
                #  清除已添加的主题消息
                del topic_mesg_dict[sub_topic][0]
            #  判断mqtt主题消息是否已接收完毕
            else:
                # 接收完毕则进行存储操作
                if len(temp_data) != 0 and len(topic_mesg_dict[sub_topic]) == 0:
                    """
                    保存数据至数据库
                    """
                    #  连接数据库
                    # log_create.info(f"{sub_topic}  数据存储——连接数据库")
                    while True:
                        conn, cursor = connectMysql()
                        # log_create.info(f"{sub_topic}  数据存储——连接状态 {conn, cursor}")
                        if conn is not False:
                            break
                        else:
                            time.sleep(2)
                            conn, cursor = connectMysql()
                            if conn is not False:
                                break

                    # log_create.info(f"{sub_topic}  数据存储——连接成功")
                    #  数据存储
                    for index, data in enumerate(temp_data):
                        try:
                            t1 = time.time()
                            # log_create.info(f'{sub_topic} begining save mysql operation!')
                            saveToMysql(conn, cursor, sub_topic, data)
                        except Exception as e:
                            except_type, except_value, except_traceback = sys.exc_info()
                            except_file = os.path.split(except_traceback.tb_frame.f_code.co_filename)[1]
                            exc_dict = {"报错类型": except_type,
                                        "报错信息": except_value,
                                        "报错文件": except_file,
                                        "报错行数": except_traceback.tb_lineno}
                            log_create.error(str(exc_dict), str(e))
                        else:
                            log_create.info(
                                f'{sub_topic} save mysql success! {round((index + 1) / len(temp_data), 4) * 100}%'
                                f' one cycle cost time {round(time.time() - t1, 3)}')
                    #  清空temp_data
                    temp_data = []
                    if conn is not False:
                        cursor.close()
                        conn.close()
                else:
                    time.sleep(0.001)


def run():
    for topic in sub_topic:
        thread_ = threading.Thread(target=task_thread, args=[topic, ])
        thread_.setDaemon(True)
        thread_.start()
        if "meter_detail" in topic:
            thread_.setName('meter_detail')
        elif "gateway_heart" in topic:
            thread_.setName('gateway_heart')
        elif "position_branch_box_temperature" in topic:
            thread_.setName('position_branch_box_temperature')
        elif "position_pile_I" in topic:
            thread_.setName('position_pile_I')
        elif "position_power_history" in topic:
            thread_.setName('position_power_history')
        else:
            pass
        time.sleep(1.5)
    # 启动接受主题消息线程函数
    # 实例化


if __name__ == "__main__":
    run()
    while True:
        log_create.error(f"当前线程总数 {len(threading.enumerate())} {threading.enumerate()}")
        time.sleep(3600)
