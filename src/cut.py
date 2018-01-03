#encoding=utf-8
'''
使用加入自定义词典的jieba分词，标注句子分词后每个词的词性，根据词性筛选部分的词，再去掉自定义的停用词。
'''

import jieba
import jieba.posseg

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
# read_line = read_from_file(path+"in.txt")
f = open(path+"sort_taxi.txt","r")
fileflow = open(path + 'use_stop_taxi.txt','w',encoding='utf-8')
lines = f.readlines()
# count = 0
for line in lines:
    # if count > 600:
    #     break
    # count += 1
    seg_list = jieba.posseg.cut(line)
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
    del_stop = " ".join(del_stop_words(each_word, stop_word_set))
    fileflow.write(del_stop + '\n')
# print (del_stop)


fileflow.close()
