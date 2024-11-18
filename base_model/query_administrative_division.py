# -*- coding: utf-8 -*-
"""
@Time ： 2023/5/19 16:42
@Auth ： DingKun
@File ：query_administrative_division.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)
"""
# coding = utf-8
"""
@autor: Felix
"""
import json
import requests
from sql_operation.operation_mysql import connectMysql


def update_didtrict_data(province: list):
    conn, cursor = connectMysql()
    header = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36'
    }
    provinces = ['北京市', '天津市', '河北省', '山西省', '内蒙古自治区', '辽宁省', '吉林省', '黑龙江省', '上海市', '江苏省', '浙江省', '安徽省', '福建省', '江西省',
                 '山东省', '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区', '海南省', '重庆市', '四川省', '贵州省', '云南省', '西藏自治区', '陕西省', '甘肃省',
                 '青海省', '宁夏回族自治区', '新疆维吾尔自治区', '台湾省', '香港特别行政区', '澳门特别行政区']
    for i in province:
        code_url = 'https://restapi.amap.com/v3/config/district?key=&keywords={}&subdistrict=3&extensions=base'.format(
            i)
        res = requests.get(code_url, headers=header)
        # print(code_url)
        # print(res.text)
        province = json.loads(res.text)['districts']
        adcode = province[0]['adcode']
        pname = province[0]['name']
        center = province[0]['center']
        pcitycode = province[0]['citycode']
        level = province[0]['level']
        lng = province[0]['center'].split(',')[0]
        lat = province[0]['center'].split(',')[1]
        city_list = province[0]['districts']
        #
        # print(pname, pcitycode, adcode, lng, lat, level)
        for city in city_list:
            citycode = city['citycode']
            adcode = city['adcode']
            name_c = city['name']
            level = city['level']
            lng = city['center'].split(',')[0]
            lat = city['center'].split(',')[1]
            district_list = city['districts']
            # print(name_c, district_list)
            # updatedb(insert_city_sql, districtpid, pname, name_c, name_c, name_c, citycode, adcode, lng, lat, level)
            # citypid = selectdb(select_sql, adcode).fetchone()[0]
            for district in district_list:
                citycode = district['citycode']
                adcode = district['adcode']
                name_d = district['name']
                level = district['level']
                lng = district['center'].split(',')[0]
                lat = district['center'].split(',')[1]
                street_list = district['districts']
                print(i, name_c, name_d)
                # sql = "insert into district_data(province, cityname, districtname) values  (%s, %s, %s) "
                # args = (i, name_c, name_d)
                # cursor.execute(sql, args)
                # conn.commit()
                # if level in ['district']:
                #     updatedb(insert_city_sql, citypid, pname, name_c, name_d, name_d, citycode, adcode, lng, lat, level)
                #     print(pname, name_c, name_d, name_d, citycode, adcode, lng, lat, level)
                #     streetpid = selectdb(select_sql, adcode).fetchone()[0]
                #     for street in street_list:
                #         citycode = street['citycode']
                #         adcode = street['adcode']
                #         name_s = street['name']
                #         level = street['level']
                #         lng = street['center'].split(',')[0]
                #         lat = street['center'].split(',')[1]
                #         # street_list = street['districts']
                #         if level in ['street']:
                #             updatedb(insert_city_sql, streetpid, pname, name_c, name_d, name_s, citycode, adcode, lng, lat,
                #                      level)
                #             print(pname, name_c, name_d, name_s, citycode, adcode, lng, lat, level)
                # elif level in ['street']:
                #     updatedb(insert_city_sql, citypid, pname, name_c, '', name_d, citycode, adcode, lng, lat, level)
                #     print(pname, name_c, name_d, name_d, citycode, adcode, lng, lat, level)
    cursor.close()
    conn.close()
def Baidu_Search(position_name):
    # 接口地址
    url = "https://api.map.baidu.com/place/v2/search"
    # 此处填写你在控制台-应用管理-创建应用后获取的AK
    ak = "您的AK"
    params = {
        "query": position_name,
        "tag": "",
        "region": "city_limit",
        "output": "json",
        "ak": ak,

    }
    response = requests.get(url=url, params=params)
    if response:
        print(response.json())

def Gaode_Search(position_name):
    header = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Mobile Safari/537.36'
    }
    code_url = 'https://restapi.amap.com/v5/place/text?key=718eb72a1f4d3533eb986028590752be&keywords={}'.format(position_name)
    res = requests.get(code_url, headers=header)
    print(res.text)
    result = json.loads(res.text)["pois"]
    temp_list = []
    for position_infos in result:
        temp_dict = {"pname": position_infos["pname"], "cityname": position_infos["cityname"],
                     "adname": position_infos["adname"], "position": position_infos["name"],
                     "address": position_infos["address"], "adcode": position_infos["adcode"]}
        temp_list.append(temp_dict)
    #print(temp_list)
    print(temp_list)
    return temp_list

if __name__ == "__main__":
    Gaode_Search("汽车充电站")
