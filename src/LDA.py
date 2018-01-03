# coding=utf-8
'''
使用经过分词和去停用词后的文本训练LDA模型，输出各主题对应权重前n位的词。
'''

import os
import re
import sys
import numpy as np
import matplotlib
import scipy
import jieba
import jieba.posseg as pseg
import jieba.analyse
import matplotlib.pyplot as plt
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
jieba.load_userdict("uniq_local_dict.txt")

def stop_words(stop_word_file):
    stop_words_set = []
    fstop = open(stop_word_file)
    for eachWord in fstop:
        stop_words_set.append(eachWord.strip())
    fstop.close()

    # print(stop_words_set)
    return stop_words_set

def del_stop_words(words,stop_words_set):
#   words是已经切词但是没有去除停用词的文档。
#   返回的会是去除停用词后的文档
    line = words.strip()
    result = jieba.cut(line)
    new_words = []
    for r in result:
        if r not in stop_words_set:
            if len(re.findall(r'[\u4e00-\u9fa5]', r)) > 0:
                new_words.append(r)
    return new_words
path = 'com/'
if __name__ == "__main__":
    stop_words_set = stop_words(path+"stop.txt")

    # 存储读取语料 一行预料为一个文档
    # corpus = []
    # for line in open('sort_taxi.txt', 'r').readlines():
    #   doc = del_stop_words(line, stop_words_set)
    #   corpus = corpus + doc
    # 读取语料 一行预料为一个文档
    corpus = []
    for line in open(path+'use_stop_bus.txt', 'r').readlines():
        corpus.append(line.strip())

    # 将文本中的词语转换为词频矩阵 矩阵元素a[i][j] 表示j词在i类文本下的词频
    vectorizer = CountVectorizer(max_df=0.95, min_df=2)

    # fit_transform是将文本转为词频矩阵
    X = vectorizer.fit_transform(corpus)

    # 可选：该fit_transform是计算tf-idf
    # 该类会统计每个词语的tf-idf权值
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))

    # 获取词袋模型中的所有词语
    word = vectorizer.get_feature_names()
    analyze = vectorizer.build_analyzer()
    weight = X.toarray()     # 可替换成 weight = tfidf.toarray()
    # weight = (weight * 100).astype(np.int64)

    # 打印特征向量文本内容
    # print('Features length: ' + str(len(word)))
    # for j in range(len(word)):
    #     print(word[j],end=' ')
    # print('\n')

    #打印每类文本词频矩阵
    # print('TF Weight: ')
    # for i in range(len(weight)):
    #     for j in range(len(word)):
    #         print(weight[i][j],end=' ')
    #     print('\n')

    # LDA算法
    print('LDA:')
    import numpy as np
    import lda
    import lda.datasets

    model = lda.LDA(n_topics=5, n_iter=1000, random_state=1)
    model.fit(np.asarray(weight))  # model.fit_transform(X) is also available
    topic_word = model.topic_word_  # model.components_ also works

    # 文档-主题（Document-Topic）分布
    doc_topic = model.doc_topic_
    print("type(doc_topic): {}".format(type(doc_topic)))
    print("shape: {}".format(doc_topic.shape))

    # 输出主题对应权重前n位的词
    n = 30
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(word)[np.argsort(topic_dist)][:-(n + 1):-1]
        print('*Topic {}\n- {}'.format(i, ' '.join(topic_words)))

    #输出前10篇文章最可能的Topic
    # label = []
    # for n in range(10):
    #     topic_most_pr = doc_topic[n].argmax()
    #     label.append(topic_most_pr)
    #     print("doc: {} topic: {}".format(n, topic_most_pr))

    # 输出Topic下面的文章
    for n in range(len(doc_topic[0])):
        total = 0
        print('topic ' + str(n) + ': ', end='')
        for doc_num in range(len(doc_topic[0:])):
            if doc_topic[doc_num].argmax() == n:
                total = total + 1
                print(doc_num,end=' ')
        print()
        print(total)

    #计算每个主题对应的词权重分布图
    # import matplotlib.pyplot as plt
    #
    # f, ax = plt.subplots(5, 2, figsize=(10, 10), sharex=True, sharey=True)
    # for i, k in enumerate([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]):  # 十个主题
    #     ax[i].stem(topic_word[k, :], linefmt='b-',
    #                markerfmt='bo', basefmt='w-')
    #     ax[i].set_xlim(-2, 20)
    #     ax[i].set_ylim(0, 1)
    #     ax[i].set_ylabel("Prob")
    #     ax[i].set_title("topic {}".format(k))
    #
    # ax[1].set_xlabel("word")

    # plt.tight_layout()
    # plt.show()
