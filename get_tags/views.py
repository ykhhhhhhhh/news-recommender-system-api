from django.shortcuts import render
from django.http import HttpResponse
import json
# Create your views here.
import pymssql
import pandas as pd
import numpy as np
from django.views.decorators.csrf import csrf_exempt
import re


# version 2021.4.15

def gettags(text, variety):
    word_lists = pd.read_csv('D:\Projects\新闻推荐\新闻推荐接口\get_tags\word_lists_72_20210404.csv')
    # word_lists = pd.read_csv('C:\\ykh\\djangoroot\\academicinfoapi\\get_tags\\word_lists_72_20210404.csv')
    db = pymssql.connect('47.104.142.34', 'xueshu', '@WSX3edc', 'AcademicExchangePlatform', charset='cp936')
    cursor = db.cursor()
    # LabelSort用不到
    sql = "select ObjectId,LabelSort,TagName,weight,relevancy_threshold from TB_Base_Tag where IsLastStage=1 order by LabelNum desc"
    cursor.execute(sql)
    wr = cursor.fetchall()  # 包含所有字段
    objectid = np.array(wr).T[0]
    labels = np.array(wr).T[2]
    weights = np.array(wr).T[3].astype(np.float)  # 矩阵转置并转换为float
    relevancy_threshold = np.array(wr).T[4].astype(np.float)
    text = text.replace("\n", "")
    text = text.replace(" ", "")
    text = text.replace("\u3000", "")
    n = []
    len_text = len(text)
    unadjusted_len_text = len(text)
    if len_text < 800:
        pass
    elif len_text < 1000:
        len_text = len_text ** (39 / 40)
    else:
        len_text = len_text ** (14 / 15) + 211  # 211约等于1000^(39/40)-1000^(14/15)
    words_freq = []
    for i in range(0, word_lists.shape[1]):
        freq = 0
        for word in word_lists.iloc[:, i]:
            if type(word) != str:
                continue
            if word.encode('utf-8').isalpha():  # 判断是否为纯英文，防止出现apple匹配pl的情况
                if text.find(word) == -1:
                    words_freq.append((word, 0))  # 改进算法速度，因为re正则匹配速度比较慢,太妙了
                else:
                    regex = re.compile(r'[^A-Za-z](' + word + ')[^A-Za-z]')
                    word_freq = len(regex.findall(text))
                    if word_freq:
                        freq += 1
                    words_freq.append((word, word_freq))
            else:
                word_freq = text.count(word)
                if word_freq != 0:
                    freq += 1
                words_freq.append((word, word_freq))
        n.append((i, freq, freq / len_text))  # freq/len_text
    freq_sum = np.dot(np.array(n).T[1], weights)  # 不同学科权重不同，感兴趣的学科freq_sum会有更大的权重，更容易相关
    k = freq_sum / unadjusted_len_text
    r = "相关" if k >= 0.33 else "不相关"
    # n.sort(key=lambda x: x[1], reverse=True) #各学科词表按匹配词数排序,应该按照相关性排！！！！！
    tags = []
    for t in n:
        correlated_rate = t[2] / relevancy_threshold[t[0]]  # 文章标签关联度
        if correlated_rate >= 1:  # 若比值大于阈值
            tags.append([objectid[t[0]], 100])
        elif correlated_rate >= 0.5:
            tags.append([objectid[t[0]], correlated_rate * 100])
        else:
            continue
    words_freq = list(set(words_freq))  # 去除重复值
    words_freq.sort(key=lambda x: x[1], reverse=True)
    keywords = words_freq[0:5]  # 此表中匹配次数前五的词
    tags.sort(key=lambda x: x[1], reverse=True)
    db.close()
    cursor.close()
    if variety:  # 1为普通新闻 0为会议通知
        return r, tags[0:3], keywords
    else:
        for label_name in labels:
            if text.find(label_name) != -1:
                for j in range(0, len(tags)):
                    if tags[j][0] == objectid[labels == label_name]:  # 布尔型索引,相同位置
                        tags[j][1] = 100
                        break
                else:
                    tags.append([objectid[labels == label_name], 100])  # for else语句 else会被break掉
        tags.sort(key=lambda x: x[1], reverse=True)
        r = "相关"
        return r, tags[0:3], keywords


# version 2021.4.15
@csrf_exempt
def post_tags(request):
    if request.method == 'POST':  # 当提交表单时
        dic = {}
        # 判断是否传参
        if request.POST:
            content = request.POST.get('content', "")
            variety = int(request.POST.get('variety', 1))  # 字符串“0”，“1” 用于if判别结果是一样的
            if content:
                res = gettags(content, variety)
                dic['IsRelevant'] = res[0]
                dic['tags'] = res[1]
                dic['keywords'] = res[2]
                dic = json.dumps(dic, ensure_ascii=False)
                return HttpResponse(dic)
            else:
                return HttpResponse('文章内容为空')
        else:
            return HttpResponse('输入为空')

    else:
        return HttpResponse('方法错误')


def gettags_2(text, variety):
    word_lists = pd.read_csv('D:\Projects\新闻推荐\新闻推荐接口\get_tags\word_lists_72_20210404.csv')
    # word_lists = pd.read_csv('C:\\ykh\\djangoroot\\academicinfoapi\\get_tags\\word_lists_72_20210404.csv')
    db = pymssql.connect('47.104.142.34', 'xueshu', '@WSX3edc', 'AcademicExchangePlatform', charset='cp936')
    cursor = db.cursor()
    # LabelSort用不到
    sql = "select ObjectId,LabelSort,TagName,weight,relevancy_threshold from TB_Base_Tag where IsLastStage=1 order by LabelNum desc"
    cursor.execute(sql)
    wr = cursor.fetchall()  # 包含所有字段
    objectid = np.array(wr).T[0]
    labels = np.array(wr).T[2]
    weights = np.array(wr).T[3].astype(np.float)  # 矩阵转置并转换为float
    relevancy_threshold = np.array(wr).T[4].astype(np.float)
    text = text.replace("\n", "")
    text = text.replace(" ", "")
    text = text.replace("\u3000", "")
    n = []
    len_text = len(text)
    unadjusted_len_text = len(text)
    if len_text < 800:
        pass
    elif len_text < 1000:
        len_text = len_text ** (39 / 40)
    else:
        len_text = len_text ** (14 / 15) + 211  # 211约等于1000^(39/40)-1000^(14/15)
    words_freq = []
    for i in range(0, word_lists.shape[1]):
        freq = 0
        for word in word_lists.iloc[:, i]:
            if type(word) != str:
                continue
            if word.encode('utf-8').isalpha():  # 判断是否为纯英文，防止出现apple匹配pl的情况
                if text.find(word) == -1:
                    # if word in text: 慢的很
                    words_freq.append((word, 0))  # 改进算法速度，因为re正则匹配速度比较慢,太妙了
                else:
                    regex = re.compile(r'[^A-Za-z](' + word + ')[^A-Za-z]')
                    word_freq = len(regex.findall(text))
                    if word_freq:
                        freq += 1
                    words_freq.append((word, word_freq))
            else:
                word_freq = text.count(word)
                if word_freq != 0:
                    freq += 1
                words_freq.append((word, word_freq))
        n.append((i, freq, freq / len_text))  # freq/len_text
    freq_sum = np.dot(np.array(n).T[1], weights)  # 不同学科权重不同，感兴趣的学科freq_sum会有更大的权重，更容易相关
    k = freq_sum / unadjusted_len_text
    r = "相关" if k >= 0.33 else "不相关"
    # n.sort(key=lambda x: x[1], reverse=True) #各学科词表按匹配词数排序,应该按照相关性排！！！！！
    tags = []
    for t in n:
        correlated_rate = t[2] / relevancy_threshold[t[0]]  # 文章标签关联度
        if correlated_rate >= 1:  # 若比值大于阈值
            tags.append([labels[t[0]], 100])
        elif correlated_rate >= 0.5:
            tags.append([labels[t[0]], correlated_rate * 100])
        else:
            continue
    words_freq = list(set(words_freq))  # 去除重复值
    words_freq.sort(key=lambda x: x[1], reverse=True)
    keywords = words_freq[0:5]  # 此表中匹配次数前五的词
    tags.sort(key=lambda x: x[1], reverse=True)
    db.close()
    cursor.close()
    if variety:  # 1为普通新闻 0为会议通知
        return r, k, tags[0:3], keywords
    else:
        for label_name in labels:
            if text.find(label_name) != -1:
                for j in range(0, len(tags)):
                    if tags[j][0] == labels[labels == label_name]:  # 布尔型索引,相同位置
                        tags[j][1] = 100  # 这里如果用for tag in tags，修改tag的值不会改变tags
                        break  # 为了提高效率break
                else:
                    tags.append([labels[labels == label_name], 100])  # for else语句 else会被break掉
        tags.sort(key=lambda x: x[1], reverse=True)
        r = "相关"
        return r, k, tags[0:3], keywords


@csrf_exempt
# 测试接口
def post_tags_2(request):
    if request.method == 'POST':  # 当提交表单时
        dic = {}
        # 判断是否传参
        if request.POST:
            content = request.POST.get('content', "")
            variety = int(request.POST.get('variety', 1))  # 字符串“0”，“1” 用于if判别结果是一样的
            if content:
                res = gettags_2(content, variety)
                dic['IsRelevant'] = res[0]
                dic['k'] = res[1]
                dic['tags'] = res[2]
                dic['keywords'] = res[3]
                dic = json.dumps(dic, ensure_ascii=False)
                return HttpResponse(dic)
            else:
                return HttpResponse('文章内容为空')
        else:
            return HttpResponse('输入为空')

    else:
        return HttpResponse('方法错误')


# version 2021.5.4
# version 2021.5.18 加入判断获奖信息
# version 2021.5.25 加大过滤力度，并把关键词放到了文件中
def isActivity(title):
    f=open('无关通讯过滤.txt','r',encoding='utf-8')
    lines=f.readlines()
    for word in [i.strip('\n') for i in lines]:
        regex = re.compile(word)
        if regex.search(title):
            f.close()
            return 1 #1为活动，国家级以下获奖类新闻
    f.close()
    return 0


# 判断工作通讯接口
@csrf_exempt
def is_Activity(request):
    if request.method == 'POST':  # 当提交表单时
        # 判断是否传参
        if request.POST:
            title = request.POST.get('title', "")
            if title:
                res = isActivity(title)
                return HttpResponse(res)
            else:
                return HttpResponse('空标题')
        else:
            return HttpResponse('输入为空')
    else:
        return HttpResponse('方法错误')
