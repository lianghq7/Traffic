#encoding=utf-8
'''
按行读取去除停用词后的仅属于某行业类别(出租车)的文本，根据主题词把文本打上事由标签，最后把有标签的文本写入新的文件中。
'''

import re

path = 'com/'

file_taxi = open(path + 'labeled_taxi.txt','w',encoding='utf-8')

y = []
for line in open(path+"use_stop_taxi.txt","r").readlines():
    label = []
    if len(re.findall(r'假冒|非法|资格证|冒充|上岗证', line)) > 0:
        label.append(0)
    if len(re.findall(r'拒载|空车|愿载', line)) > 0:
        label.append(1)
    if len(re.findall(r'态度|恶劣|不文明用语', line)) > 0:
        label.append(2)
    if len(re.findall(r'绕路|绕道|绕远|路线', line)) > 0:
        label.append(3)
    if len(re.findall(r'议价|乱收费|不合理|打表|要价', line)) > 0:
        label.append(4)
    if len(re.findall(r'危险驾驶|安全|急刹', line)) > 0:
        label.append(5)
    if len(label) > 0:
        file_taxi.write(line)
        y.append(label)
    
# print (y[0][0])

file_taxi.close()
