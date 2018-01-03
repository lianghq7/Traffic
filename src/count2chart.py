#encoding=utf-8
'''
从excel表格中获取发生时间、行业类别、结构化地址和事由，对这些信息进行统计与分析，并把分析结果写入到txt文件和统计图中。
'''

import csv
import re
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from pylab import *
path = 'com/'
output_path = 'output/'

month = [0 for x in range(100)]#统计发生在各个月份的数量，month[0]表示2017年以外的，month[i]表示2017年i月的数量
kind_count = [0 for i in range(6)]
reason_taxi_count = [0 for i in range(20)]
dict_taxi_reason = {'':0,'非法载客行为':1,'拒载':2,'态度恶劣':3,'故意绕道':4,'议价':5,'危险驾驶':6}
reason_bus_count = [0 for i in range(10)]
dict_bus_reason = {'':0,'不按规定停靠':1,'服务态度恶劣':2, '发车时间不合理':3}
dict_kind = {'':0,'出租车':1,'公交车':2,'驾校':3,'客运大巴':4}
list_kind = ['' for x in range(len(dict_kind))]
dict_city = {'其他':0,'广州市':1,'深圳市':2,'珠海市':3,'惠州市':4,'茂名市':5,'清远市':6}
list_city = ['' for x in range(len(dict_city))]
dict_area = {'其他':0,'荔湾区':1,'越秀区':2,'海珠区':3,'天河区':4,'白云区':5,'黄埔区':6,'番禺区':7,'花都区':8,'南沙区':9,'从化区':10,'增城区':11,'福田区':12,'罗湖区':13,'南山区':14,'盐田区':15,'宝安区':16,'龙岗区':17,'龙华区':18,'坪山区':19,'香洲区':20,'金湾区':21,'斗门区':22}
list_area = ['' for x in range(len(dict_area))]
city_count = [0 for i in range(10)]
area_count = [0 for i in range(30)]
for key,i in dict_kind.items():
    list_kind[i] = key
for key,i in dict_city.items():
    list_city[i] = key
for key,i in dict_area.items():
    list_area[i] = key
list_kind[0] = '其他'
list_city[0] = '其他'
list_area[0] = '其他'
kind_key = dict_kind.keys()
city_key = dict_city.keys()
area_key = dict_area.keys()
reason_taxi_key = dict_taxi_reason.keys()
reason_bus_key = dict_bus_reason.keys()
filew = open(output_path + 'chart_out.txt','w',encoding='utf-8')
with open(path+"traffic_7.csv", "r") as csvin:
    # firt_row = ['受理内容','受理时间','受理行政区','发生时间','涉及地点','经纬度坐标','结构化地址','行业类别','事由']
    reader = csv.DictReader(csvin)
    count = 0
    for row in reader:
        # if count > 150:
            # break
        count += 1
        print (count)
        time = row['发生时间']
        if len(re.findall(r'/2017', time))>0:
            i = int(re.findall(r'\d\d?/', time)[0].replace('/',''))#month[i]表示2017年i月的数量
            month[i] += 1
        elif len(re.findall(r'/2016', time))>0:
            month[0] += 1#month[0]表示2017年以外的

        content_kind = row['行业类别']
        if content_kind in kind_key:
            kind_count[dict_kind[content_kind]] += 1

        content_address = row['结构化地址']
        # print('结构化地址:',type(content_address), content_address)
        address_each = re.findall(r'[\u4e00-\u9fa5]+省[\u4e00-\u9fa5]+市[\u4e00-\u9fa5]+区', content_address)
        city_each = re.findall(r'省[\u4e00-\u9fa5]+?市', content_address)
        area_each = re.findall(r'市[\u4e00-\u9fa5]+区', content_address)
        address_set = set()
        city_set = set()
        area_set = set()

        for each in address_each:
            # print(address_temp)
            address_set.add(each)
        for each in city_each:
            city_set.add(each.replace('省',''))
        for each in area_each:
            area_set.add(each.replace('市',''))
        for city in city_set:
            if city in city_key:
                city_count[dict_city[city]] += 1
            else:
                city_count[0] += 1

        for area in area_set:
            if area in area_key:
                area_count[dict_area[area]] += 1
            else:
                area_count[0] += 1
        
        reason = row['事由']
        reason = reason.strip()
        reason_each = reason.split()
        if reason == '' and content_kind == '出租车':
            reason_taxi_count[0] += 1
        if reason == '' and content_kind == '公交车':
            reason_bus_count[0] += 1
        for i in reason_each:
            if (i in reason_taxi_key) and content_kind == '出租车':
                reason_taxi_count[dict_taxi_reason[i]] += 1
            elif (i in reason_bus_key) and content_kind == '公交车':
                reason_bus_count[dict_bus_reason[i]] += 1


filew.write('各类别数目统计情况:\n')
print('各类别数目统计情况:')
for i in range(len(dict_kind)):
    filew.write(list_kind[i] + ' ')
    filew.write(str(kind_count[i]) + '\n')
    print (list_kind[i], kind_count[i])

filew.write('\n各city数目统计情况:\n')
print('各city数目统计情况:')
for i in range(len(dict_city)):
    filew.write(list_city[i] + ' ')
    filew.write(str(city_count[i]) + '\n')
    print (list_city[i], city_count[i])

filew.write('\n各area数目统计情况:\n')
print('各area数目统计情况:')
for i in range(len(dict_area)):
    filew.write(list_area[i] + ' ')
    filew.write(str(area_count[i]) + '\n')
    print (list_area[i], area_count[i])

filew.write('\n各月份数目统计情况:\n')
print('各月份数目统计情况:')    
for i in range(13):
    filew.write(str(i) + ' ')
    filew.write(str(month[i]) + '\n')
    print (i, month[i])

filew.write('\n出租车各事由数目统计情况:\n')
print('出租车各事由数目统计情况:')    
for i in range(8):
    filew.write(str(i) + ' ')
    filew.write(str(reason_taxi_count[i]) + '\n')
    print (i, reason_taxi_count[i])
filew.write('\n公交车各事由数目统计情况:\n')
print('公交车各事由数目统计情况:')    
for i in range(5):
    filew.write(str(i) + ' ')
    filew.write(str(reason_bus_count[i]) + '\n')
    print (i, reason_bus_count[i])


filew.close()
plt.figure(1)
zhfont1 = matplotlib.font_manager.FontProperties(fname='/usr/share/fonts/truetype/arphic/ukai.ttc')
plt.title(u'各月份投诉数据统计图',fontproperties=zhfont1)
plt.xlabel(u'月份',fontproperties=zhfont1)
plt.ylabel(u'数量',fontproperties=zhfont1)
month_labels = [u'2017年之前', u'一月',u'二月',u'三月',u'四月',u'五月',u'六月',u'七月']
x1 = [1, 2, 3, 4, 5, 6, 7, 8]
plt.plot(x1, month[:8],'r', label='month',alpha=0.9)
plt.xticks(x1, month_labels, rotation=0,fontproperties=zhfont1)
# for i in range(len(x1)):
    # plt.text(x1[i], 1.03*month[i], str(month[i]))
plt.savefig('各月份投诉数据统计图.jpg')
plt.show()

plt.figure(2)
plt.title(u'各城市投诉数据统计图',fontproperties=zhfont1)
plt.xlabel(u'城市名',fontproperties=zhfont1)
plt.ylabel(u'数量',fontproperties=zhfont1)
city_labels = [u'广州市', u'深圳市',u'珠海市',u'惠州市',u'茂名市',u'清远市',u'其他']
x2 = [1, 2, 3, 4, 5, 6, 7]
city_count.insert(6,city_count.pop(0))
plt.bar(x2 , city_count[:7], width=0.5 , color='b',alpha=0.5)
plt.xticks(x2, city_labels, rotation=0,fontproperties=zhfont1)
# for i in range(len(x2)):
    # plt.text(x2[i], 1.03*city_count[i], str(city_count[i]),verticalalignment='center')
plt.grid(axis='y')
plt.savefig('各城市投诉数据统计图.jpg')
plt.show()

plt.figure(3)
plt.title(u'广州市各区域投诉数据统计图',fontproperties=zhfont1)
plt.xlabel(u'区域名',fontproperties=zhfont1)
plt.ylabel(u'数量',fontproperties=zhfont1)
area_guangzhou_labels = [u'荔湾区', u'越秀区',u'海珠区',u'天河区',u'白云区',u'黄埔区',u'番禺区', u'花都区',u'南沙区',u'从化区',u'增城区']
x3 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
count_now = area_count[1:12]
plt.bar(x3 , area_count[1:12], width=0.5 , color='b',alpha=0.5)
plt.xticks(x3, area_guangzhou_labels, rotation=0,fontproperties=zhfont1)
# for i in range(len(x3)):
#     plt.text(x3[i], 1.03*count_now[i], str(count_now[i]),verticalalignment='center')
plt.grid(axis='y')
plt.savefig('广州市各区域投诉数据统计图.jpg')
plt.show()

plt.figure(4)
plt.title(u'深圳市各区域投诉数据统计图',fontproperties=zhfont1)
plt.xlabel(u'区域名',fontproperties=zhfont1)
plt.ylabel(u'数量',fontproperties=zhfont1)
area_shenzhen_labels = [u'福田区', u'罗湖区',u'南山区',u'盐田区',u'宝安区',u'龙岗区',u'龙华区', u'坪山区']
x4 = [1, 2, 3, 4, 5, 6, 7, 8]
count_now = area_count[12:20]
plt.bar(x4 , area_count[12:20], width=0.5 , color='b',alpha=0.5)
plt.xticks(x4, area_shenzhen_labels, rotation=0,fontproperties=zhfont1)
# for i in range(len(x4)):
#     plt.text(x4[i], 1.03*count_now[i], str(count_now[i]),verticalalignment='center')
plt.grid(axis='y')
plt.savefig('深圳市各区域投诉数据统计图.jpg')
plt.show()

plt.figure(5)
plt.title(u'珠海市各区域投诉数据统计图',fontproperties=zhfont1)
plt.xlabel(u'区域名',fontproperties=zhfont1)
plt.ylabel(u'数量',fontproperties=zhfont1)
area_zhuhai_labels = [u'香洲区', u'金湾区',u'斗门区']
x5 = [1, 2, 3]
count_now = area_count[20:23]
plt.bar(x5 , area_count[20:23], width=0.2 , color='b',alpha=0.5)
plt.xticks(x5, area_zhuhai_labels, rotation=0,fontproperties=zhfont1)
# for i in range(len(x5)):
    # plt.text(x5[i], 1.03*count_now[i], str(area_count[i]))
plt.grid(axis='y')
plt.savefig('珠海市各区域投诉数据统计图.jpg')
plt.show()

plt.figure(6)
plt.title(u'各行业类别投诉数据统计图',fontproperties=zhfont1)
kind_labels = [u'出租车', u'公交车', u'驾校',u'客运大巴',u'其他']
kind_count.insert(4,kind_count.pop(0))
plt.xlabel(u'行业类别',fontproperties=zhfont1)
plt.ylabel(u'数量',fontproperties=zhfont1)
x6 = [1, 2, 3, 4, 5]
plt.bar(x6 , kind_count[:5], width=0.3 , color='b',alpha=0.5)
plt.xticks(x6, kind_labels, rotation=0,fontproperties=zhfont1)
# for i in range(len(x6)):
    # plt.text(x6[i], 1.03*kind_count[i], str(kind_count[i]))
plt.grid(axis='y')
plt.savefig('各行业类别投诉数据统计图.jpg')
plt.show()

plt.figure(7)
plt.title(u'出租车各事由投诉数据统计图',fontproperties=zhfont1)
plt.xlabel(u'事由',fontproperties=zhfont1)
plt.ylabel(u'数量',fontproperties=zhfont1)
reason_taxi_labels = [u'非法载客行为', u'拒载',u'态度恶劣',u'故意绕道',u'议价',u'危险驾驶',u'其他']
reason_taxi_count.insert(6,reason_taxi_count.pop(0))
x7 = [1, 2, 3, 4, 5, 6, 7]
plt.bar(x7 , reason_taxi_count[:7], width=0.5 , color='b',alpha=0.5)
plt.xticks(x7, reason_taxi_labels, rotation=0,fontproperties=zhfont1)
# for i in range(len(x7)):
    # plt.text(x7[i], 1.03*reason_taxi_count[i], str(reason_taxi_count[i]))
plt.grid(axis='y')
plt.savefig('出租车各事由投诉数据统计图.jpg')
plt.show()

plt.figure(8)
plt.title(u'公交车各事由投诉数据统计图',fontproperties=zhfont1)
plt.xlabel(u'事由',fontproperties=zhfont1)
plt.ylabel(u'数量',fontproperties=zhfont1)
reason_bus_labels = [u'不按规定停靠', u'服务态度恶劣',u'发车时间不合理',u'其他']
reason_bus_count.insert(3,reason_bus_count.pop(0))
x8 = [1, 2, 3, 4]
plt.bar(x8 , reason_bus_count[:4], width=0.3 , color='b',alpha=0.5)
plt.xticks(x8, reason_bus_labels, rotation=0,fontproperties=zhfont1)
# for i in range(len(x8)):
    # plt.text(x8[i], 1.03*reason_bus_count[i], str(reason_bus_count[i]))
plt.grid(axis='y')
plt.savefig('公交车各事由投诉数据统计图.jpg')
plt.show()
