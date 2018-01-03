# coding=utf-8  
'''
利用有标记的文本中的大部分来训练多标签分类模型，少部分用来作测试集，把具体的标签和文本对应写入到txt文件中。
'''

import re
import numpy as np
import os
import sys
import codecs
import shutil
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

'''
sklearn里面的TF-IDF主要用到了两个函数：CountVectorizer()和TfidfTransformer()。
    CountVectorizer是通过fit_transform函数将文本中的词语转换为词频矩阵。
    矩阵元素weight[i][j] 表示j词在第i个文本下的词频，即各个词语出现的次数。
    通过get_feature_names()可看到所有文本的关键字，通过toarray()可看到词频矩阵的结果。
    TfidfTransformer也有个fit_transform函数，它的作用是计算tf-idf值。
'''

if __name__ == "__main__":
    corpus = [] #文档预料 空格连接
    n = 0
    #读取预料 一行预料为一个文档
    train_num = 13000
    for line in open('labeled_taxi.txt', 'r').readlines():
        corpus.append(line.strip())
        n += 1
        if n == train_num:
            break
    m = n
    for line in open('test_taxi.txt', 'r').readlines():
        corpus.append(line.strip())
        m += 1
    
    #将文本中的词语转换为词频矩阵 矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer()

    #该类会统计每个词语的tf-idf权值
    transformer = TfidfTransformer()

    #第一个fit_transform是计算tf-idf 第二个fit_transform是将文本转为词频矩阵
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))
    #获取词袋模型中的所有词语
    word = vectorizer.get_feature_names()

    #将tf-idf矩阵抽取出来，元素w[i][j]表示j词在i类文本中的tf-idf权重
    tf_mat = tfidf.toarray()
    first_line = tf_mat[:1,:]
    print ('first_line.size:',first_line.size)
    x_train = tf_mat[:n,:]
    print ('x_train.size:',x_train[:,0:1].size)
    x_test = tf_mat[n:m,:]
    print ('x_test.size:',x_test[:,0:1].size)
    
    y = []
    y_test = []
    n = 0
    for line in open("labeled_taxi.txt","r").readlines():
        n += 1
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
        if len(label) > 0 and n <= train_num:
            y.append(label)
        if n > train_num:
            y_test.append(label)

    y_train = MultiLabelBinarizer().fit_transform(y)
    y_test = MultiLabelBinarizer().fit_transform(y_test)
    print (y_train)
    
    # forest = RandomForestClassifier(n_estimators=200, random_state=1)
    # clf = OneVsRestClassifier(LogisticRegression(),n_jobs=-2)

    svm = LinearSVC(random_state=0)
    multi_target_forest = OneVsRestClassifier(svm,n_jobs=-2)
    clf = multi_target_forest
    clf.fit(x_train,y_train)

    pred_y = clf.predict(x_test)
    print (pred_y)
    print (np.mean(pred_y == y_test))
    print('Train set:',train_num, ' ','Test set:',m - train_num)
    print (metrics.classification_report(y_test,pred_y))

    i = 0
    problem_class = ['非法载客行为','拒载','态度恶劣', '故意绕道', '议价', '危险驾驶']
    pred_taxi = open('pred_taxi.txt','w',encoding='utf-8')
    
    be_labeled = 0
    for line in open('test_taxi.txt', 'r').readlines():
        has_label = 0
        for j in range(6):
            if pred_y[i][j] == 1:
                has_label = 1
                pred_taxi.write(problem_class[j] + ' ')
        pred_taxi.write(': ' +line)
        if has_label == 1:
            be_labeled += 1
        i += 1
    print ('test count:', i, 'labeled count:', be_labeled)
