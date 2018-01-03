#encoding=utf-8
'''
把原csv文件写入到新的csv文件，并增加处理好的列，包括行业类别、发生时间、涉及地点、经纬度坐标和结构化地址
'''
import jieba
import jieba.posseg
import csv
import re
from xml.etree import ElementTree  
import json  
import urllib.request

jieba.load_userdict("uniq_local_dict.txt")
path = 'com/'
output_path = 'output/'

month = [0 for x in range(100)]#统计发生在各个月份的数量，month[0]表示2017年以外的，month[i]表示2017年i月的数量
filew = open(path + 'lat_lng_4.txt','w',encoding='utf-8')
with open(path+"traffic.csv", "r") as csvin, open(output_path + "structured_data.csv", "w", newline='') as csvout:
    firt_row = ['受理内容','受理时间','受理行政区','发生时间','涉及地点','经纬度坐标','结构化地址','类别','事由']
    writer = csv.DictWriter(csvout, fieldnames=firt_row)
    writer.writeheader()

    reader = csv.DictReader(csvin)
    count = 0
    for row in reader:
        if count > 13000:
            break
        count += 1
        # print (count)
        #类别
        content = row['受理内容']
        kind = ''
        if len(re.findall(r'出租车|的士|空车牌|空车标志|咪表|计程器|计程车|司机工号|车费|打表', content)) > 0:
            kind = '出租车'
        elif len(re.findall(r'公交车', content)) > 0:
            kind = '公交车'
        elif len(re.findall(r'驾校', content)) > 0:
            kind = '驾校'
        elif len(re.findall(r'长途客车|长途大巴|长途客运|长途汽车|汽车站|客运站', content)) > 0:
            kind = '客运大巴'

        #发生时间
        time_temp = ''
        time = ''
        jieba.suggest_freq(('分', '在'), True)
        seg_list = jieba.posseg.cut(content)
        sent = ''
        date_str = ''
        time_str = ''
        is_time = 0
        for word, flag in seg_list:
            if is_time == 0 and flag == 'm':
                time_temp += word
                is_time = 1
                continue
            if is_time == 1:
                if word == '，':
                    break
                if flag == 'm' or flag == 't' or flag == 'x':
                    time_temp += word
                else:
                    break
        if len(re.findall(r'年|月|日|:|：|/|-|号|点', time_temp))>0:
            time_temp = time_temp.replace('【','')
            if len(re.findall(r'20\d\d年\d\d?月\d\d?日', time_temp))>0:
                temp = re.findall(r'20\d\d年\d\d?月\d\d?日', time_temp)
                date_str = temp[0]
                temp = re.findall(r'\d\d?月', date_str)[0].replace('月','')
                if temp[0] == '0':
                    temp = temp[1:]
                time += temp +'/'
                temp = re.findall(r'\d\d?日', date_str)[0].replace('日','')
                if temp[0] == '0':
                    temp = temp[1:]
                time += temp +'/'
                temp = re.findall(r'20\d\d年', date_str)[0].replace('年','')
                time += temp + ' '
            elif len(re.findall(r'20\d\d-\d\d?-\d\d?', time_temp))>0:
                temp = re.findall(r'20\d\d-\d\d?-\d\d?', time_temp)
                date_str = temp[0]
                temp = re.findall(r'\d\d?-', date_str)[1].replace('-','')
                if temp[0] == '0':
                    temp = temp[1:]
                time += temp +'/'
                temp = re.findall(r'-\d\d?', date_str)[1].replace('-','')
                if temp[0] == '0':
                    temp = temp[1:]
                time += temp +'/'
                temp = re.findall(r'20\d\d', date_str)[0]
                time += temp + ' '
            elif len(re.findall(r'20\d\d/\d\d?/\d\d?', time_temp))>0:
                temp = re.findall(r'20\d\d/\d\d?/\d\d?', time_temp)
                date_str = temp[0]
                temp = re.findall(r'\d\d?/', date_str)[1].replace('/','')
                if temp[0] == '0':
                    temp = temp[1:]
                time += temp +'/'
                temp = re.findall(r'/\d\d?', date_str)[1].replace('/','')
                if temp[0] == '0':
                    temp = temp[1:]
                time += temp +'/'
                temp = re.findall(r'20\d\d', date_str)[0]
                time += temp + ' '
            elif len(re.findall(r'\d\d?月\d\d?日', time_temp))>0:
                temp = re.findall(r'\d\d?月\d\d?日', time_temp)
                date_str = temp[0]
                temp = re.findall(r'\d\d?月', date_str)[0].replace('月','')
                if temp[0] == '0':
                    temp = temp[1:]
                time += temp +'/'
                temp = re.findall(r'\d\d?日', date_str)[0].replace('日','')
                if temp[0] == '0':
                    temp = temp[1:]
                time += temp +'/'
                temp = '2017'
                time += temp + ' '
            elif len(re.findall(r'\d\d?-\d\d?', time_temp))>0:
                temp = re.findall(r'\d\d?-\d\d?', time_temp)
                date_str = temp[0]
                temp = re.findall(r'\d\d?-', date_str)[0].replace('-','')
                if temp[0] == '0':
                    temp = temp[1:]
                time += temp +'/'
                temp = re.findall(r'-\d\d?', date_str)[0].replace('-','')
                if temp[0] == '0':
                    temp = temp[1:]
                time += temp +'/'
                temp = '2017'
                time += temp + ' '
            if time != '':
                if len(re.findall(r'\d\d?:\d\d?:\d\d?|\d\d?：\d\d?：\d\d?', time_temp))>0:
                    temp = re.findall(r'\d\d?:\d\d?:\d\d?|\d\d?：\d\d?：\d\d?', time_temp)
                    time_str = temp[0].replace('：',':')
                    time += time_str
                elif len(re.findall(r'\d\d?:\d\d?|\d\d?：\d\d?|\d\d?点\d\d?', time_temp))>0:
                    temp = re.findall(r'\d\d?:\d\d?|\d\d?：\d\d?|\d\d?点\d\d?', time_temp)
                    time_str = temp[0].replace('：',':').replace('点',':')
                    time += time_str
        if time == '':
            time = row['受理时间']

        #统计发生在各个月份的数量
        if len(re.findall(r'/2017', time))>0:
            i = int(re.findall(r'\d\d?/', time)[0].replace('/',''))#month[i]表示2017年i月的数量
            month[i] += 1
        else:
            month[0] += 1#month[0]表示2017年以外的

        #涉及地点
        seg_list = jieba.posseg.cut(content)
        local = ''
        location = '' #经纬度坐标
        location_list =[]
        struct_local_list =[]
        before = 'x'
        for word, flag in seg_list:
            if flag == 'local':
                if before == 'local':
                    local += word
                else:
                    local += ' ' + word
            elif (before == 'local' and word =='路') or (before == 'local' and word =='站'):
                local += word
            before = flag
        local_list2 = []
        if local != '':
            local_list = local.split()
            local_list2 = sorted(set(local_list),key=local_list.index)
            # print (local_list2)
            for local_name in local_list2:
                if local_name == row['受理行政区'] or local_name == row['受理行政区'][:-1]:
                    continue
                search=urllib.parse.quote(local_name.encode('utf-8'))              
                region=urllib.parse.quote(row['受理行政区'].encode('utf-8'))  
                url="http://api.map.baidu.com/place/v2/search?query=%s&region=%s&city_limit=false&output=json&ak=RG4LBSa3zgOtvUMv7t70LRDbAvTH9GpW"%(search,region)
                try:
                    req = urllib.request.urlopen(url)
                    res = req.read().decode("utf-8") #将其他编码的字符串解码成unicode
                    place = json.loads(res)
                except(Exception) as ex:
                    print('error:',ex)
                try:
                    if place['results'] != []:
                        location = place['results'][0]['location'] #经纬度坐标
                        if not location in location_list:
                            location_list.append(location)
                except(Exception) as ex:
                    print('error:',ex)
            if len(location_list) > 0:
                for location in location_list:
                    try:
                        lat = str(location['lat'])
                        lng = str(location['lng'])
                        filew.write('\"lng\":' + lng + ',\"lat\":' + lat+ ',\n')
                        url2 = 'http://api.map.baidu.com/geocoder/v2/?callback=renderReverse&location='+lat+','+lng+'&output=xml&pois=1&ak=RG4LBSa3zgOtvUMv7t70LRDbAvTH9GpW'
                        req2 = urllib.request.urlopen(url2)
                        res2 = req2.read().decode("utf-8")#将其他编码的字符串解码成unicode
                        root = ElementTree.fromstring(res2)
                        node_find = root.find('result/formatted_address')  
                        # print(node_find.text)
                        struct_local_list.append(node_find.text)
                    except(Exception) as ex:
                        print('error:',ex)
        print ('类别:', kind,'   发生时间:', time) 
        print ('涉及地点:',local_list2,'   经纬度坐标:',location_list) 
        print ('结构化地址:',struct_local_list,'\n')         

            
        # print(content,date_str, time)
        writer.writerow({'受理内容':row['受理内容'],'受理时间':row['受理时间'],'受理行政区':row['受理行政区'],'类别':kind,'发生时间':time,'涉及地点':local_list2,'经纬度坐标':location_list,'结构化地址':struct_local_list})
for i in range(13):
    print (i, month[i])
filew.close()
