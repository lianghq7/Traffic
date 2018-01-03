# coding=utf-8  
'''
对受理内容进行预处理，根据主题词自动标记事由，利用有标记的文本训练多标签分类模型，使用这个模型对未打上标签的文本打上标签。把事由写入到excel文件。
'''

import re
import numpy as np
import os
import sys
import csv
import codecs
import shutil
import jieba
import jieba.posseg
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report
from sklearn import metrics

jieba.load_userdict("uniq_local_dict.txt")

def read_from_file(file_name):
    with open(file_name,"r") as fp:
        words = fp.read()
    return words

def stop_words(stop_word_file):
    words = read_from_file(stop_word_file)
    result = jieba.cut(words)
    new_words = []
    for r in result:
        new_words.append(r)
    return set(new_words)

def del_stop_words(words,stop_words_set):
#   words是已经切词但是没有去除停用词的文档。
#   返回的会是去除停用词后的文档
    new_words = []
    for r in words:
        if r not in stop_words_set:
            new_words.append(r)
    return new_words

path = 'com/'
output_path = 'output/'

problem_class = ['非法载客行为','拒载','态度恶劣', '故意绕道', '议价', '危险驾驶']
with open(path+"traffic_3.csv", "r") as csvin, open(path+"traffic_5.csv", "w", newline='') as csvout:
    # firt_row = ['受理内容','受理时间','受理行政区','发生时间','涉及地点','经纬度坐标','结构化地址','类别','事由']
    # writer = csv.DictWriter(csvout, fieldnames=firt_row)
    # writer.writeheader()

    reader = csv.DictReader(csvin)

    corpus_taxi = []
    corpus_taxi_labeled = []
    corpus_taxi_no_label = []
    corpus_no_kind = []
    y_taxi_labeled = []
    count = 0
    for row in reader:
        # if count > 1300:    
        #     break
        count += 1
        print (count)
        content = row['受理内容']
        kind = row['类别']
        if kind == '出租车':
            seg_list = jieba.posseg.cut(content)
            sent = ''
            for word, flag in seg_list:
                if flag == 'x' or flag == 'ns' or flag == 'ul' or flag == 'eng' or flag == 'm' or flag == 'nr'or flag == 'local':
                    continue
                sent += word + ' '
            sent += '\n'
            sent = sent.strip()
            sent += '\n'
            each_word = sent.split()
            stop_word_set = stop_words(path+"stop.txt")
            del_stop = " ".join(del_stop_words(each_word, stop_word_set))#分词、去掉停用词后的句子
            label = []
            if len(re.findall(r'假冒|非法|资格证|冒充|上岗证', content)) > 0:
                label.append(0)
            if len(re.findall(r'拒载|空车|愿载', content)) > 0:
                label.append(1)
            if len(re.findall(r'态度|恶劣|不文明用语', content)) > 0:
                label.append(2)
            if len(re.findall(r'绕路|绕道|绕远|路线', content)) > 0:
                label.append(3)
            if len(re.findall(r'议价|乱收费|不合理|打表|要价', content)) > 0:
                label.append(4)
            if len(re.findall(r'危险驾驶|安全|急刹', content)) > 0:
                label.append(5)
            if len(label) > 0:
                y_taxi_labeled.append(label)
                corpus_taxi_labeled.append(del_stop.strip())#打上标签的句子放进corpus_taxi_labeled
            else:
            	corpus_taxi_no_label.append(del_stop.strip())#没有打上标签的句子放进corpus_taxi_no_label
            
        elif kind == '':
            seg_list = jieba.posseg.cut(content)
            sent = ''
            for word, flag in seg_list:
                if flag == 'x' or flag == 'ns' or flag == 'ul' or flag == 'eng' or flag == 'm' or flag == 'nr'or flag == 'local':
                    continue
                sent += word + ' '
            sent += '\n'
            sent = sent.strip()
            sent += '\n'
            each_word = sent.split()
            stop_word_set = stop_words(path+"stop.txt")
            del_stop = " ".join(del_stop_words(each_word, stop_word_set))#分词、去掉停用词后的句子
            corpus_no_kind.append(del_stop.strip())#没有类别的句子放进corpus_no_kind
    n_corpus_taxi_labeled = len(corpus_taxi_labeled)
    n_corpus_taxi_no_label = len(corpus_taxi_no_label)
    n_corpus_no_kind = len(corpus_no_kind)
    print(n_corpus_taxi_labeled,n_corpus_taxi_no_label,n_corpus_no_kind)
    corpus_taxi = corpus_taxi_labeled+corpus_taxi_no_label+corpus_no_kind

    #将文本中的词语转换为词频矩阵 矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer()
    #该类会统计每个词语的tf-idf权值
    transformer = TfidfTransformer()
    #第一个fit_transform是计算tf-idf 第二个fit_transform是将文本转为词频矩阵
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus_taxi))
    #将tf-idf矩阵抽取出来，元素w[i][j]表示j词在i类文本中的tf-idf权重
    tf_mat = tfidf.toarray()
    x_train = tf_mat[:n_corpus_taxi_labeled,:]
    x_no_label_test = tf_mat[n_corpus_taxi_labeled:n_corpus_taxi_labeled+n_corpus_taxi_no_label,:]
    x_no_kind_test = tf_mat[n_corpus_taxi_labeled+n_corpus_taxi_no_label:n_corpus_taxi_labeled+n_corpus_taxi_no_label+n_corpus_no_kind,:]
    print (x_train.shape,x_no_label_test.shape,x_no_kind_test.shape)
    # x_test = tf_mat[n:m,:]

    y_train = MultiLabelBinarizer().fit_transform(y_taxi_labeled)
    
    print (y_train.shape)

    svm = LinearSVC(random_state=0)
    clf = OneVsRestClassifier(svm,n_jobs=-2)
    clf.fit(x_train,y_train)

    pred_y_no_label_test = clf.predict(x_no_label_test)
    pred_y_no_kind_test = clf.predict(x_no_kind_test)

    
with open(path+"traffic_3.csv", "r") as csvin, open(output_path+"traffic_5.csv", "w", newline='') as csvout:
    firt_row = ['受理内容','受理时间','受理行政区','发生时间','涉及地点','经纬度坐标','结构化地址','类别','事由']
    writer = csv.DictWriter(csvout, fieldnames=firt_row)
    writer.writeheader()

    reader = csv.DictReader(csvin)

    # count = 0
    now_pred_y_no_label = 0
    now_pred_y_no_kind = 0
    for row in reader:
        # if count > 1300:
        #     break
        # count += 1
        reason = ''
        content = row['受理内容']
        kind = row['类别']
        
        if kind == '出租车':
            label = []
            if len(re.findall(r'假冒|非法|资格证|冒充|上岗证', content)) > 0:
                label.append(0)
            if len(re.findall(r'拒载|空车|愿载', content)) > 0:
                label.append(1)
            if len(re.findall(r'态度|恶劣|不文明用语', content)) > 0:
                label.append(2)
            if len(re.findall(r'绕路|绕道|绕远|路线', content)) > 0:
                label.append(3)
            if len(re.findall(r'议价|乱收费|不合理|打表|要价', content)) > 0:
                label.append(4)
            if len(re.findall(r'危险驾驶|安全|急刹', content)) > 0:
                label.append(5)
            if len(label) > 0:
                for j in label:
                    reason += problem_class[j] + ' '
            else:
                pred_y = pred_y_no_label_test[now_pred_y_no_label]
                now_pred_y_no_label += 1
                for j in range(6):
                    if pred_y[j] == 1:
                        reason += problem_class[j] + ' '
                # print("no_labeled:",reason,"y_no_label:",now_pred_y_no_label)
        elif kind == '':
            pred_y = pred_y_no_kind_test[now_pred_y_no_kind]
            now_pred_y_no_kind += 1
            for j in range(6):
                if pred_y[j] == 1:
                    kind = '出租车'
                    reason += problem_class[j] + ' '
            # print("no_kind:",reason,"y_no_kind:",now_pred_y_no_kind)
        reason = reason.strip()
        writer.writerow({'受理内容':row['受理内容'],'受理时间':row['受理时间'],'受理行政区':row['受理行政区'],'发生时间':row['发生时间'],'涉及地点':row['涉及地点'],'经纬度坐标':row['经纬度坐标'],'结构化地址':row['结构化地址'],'类别':kind,'事由':reason})
