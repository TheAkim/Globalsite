# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 11:01:43 2018

@author: asushj
"""
"""因为要翻译的文本较多，调用百度API的次数多且频繁，
我本人的账号也因此被限制了频率和次数，故可能会有几句没有连接上翻译或远程连接的主机没有反应，请谅解"""

import http.client  
import hashlib  
import json   
import random  
import urllib
import re


class Baidu_Translation:
    def __init__(self):  
        # @description: Baidu_Translation类的初始化函数
        self._q = ''  #抽取的每一行的内容
        self._from = 'auto'  #自动识别源语语种
        self._to = 'zh'      #设定目标语言
        self._appid = '20170518000048294' #API账号 
        self._key = '8MHHdtyFW7eM1aT0oiAM'#API密钥
        self._salt = random.randint(32768, 65536)  #随机数
        self._sign = ''  #签名
        self._dst = ''  #存放翻译结果的字典
        self._enable = True 
        self._httpClient = None
        self._myurl = '' #请求地址

    def Baidu_connect(self,value):  
        # @description: 通过API连接到服务器后获取翻译结果
        # @param string content 获取的要翻译的内容
        # @return json jsonResponse
        # @return string self._dst
        self._q = value
        m = str(self._appid)+self._q+str(self._salt)+self._key  #拼接签名元素
        m_MD5 = hashlib.md5(m.encode())  #请求尾部解码为 UTF-8
        self._sign = m_MD5.hexdigest() #md5加密生成签名sign         
        Url_1 = '/api/trans/vip/translate'  
        Url_2 = '?appid='+str(self._appid)+'&q='+urllib.parse.quote(self._q)+'&from='+self._from+'&to='+self._to+'&salt='+str(self._salt)+'&sign='+self._sign  
        self.myurl = Url_1+Url_2 #拼接报文body
        try:
            self._httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')  
            self._httpClient.request('GET', self.myurl)   # 发送请求，response是HTTPResponse对象  
            response = self._httpClient.getresponse()  
            jsonResponse = response.read().decode("utf-8")# 获得返回的结果，结果为json格式  
            js = json.loads(jsonResponse) #将json格式的结果转换字典结构  
            self._dst = str(js["trans_result"][0]["dst"])  # 字典转为字符串，取得翻译后的文本结果
            Baidu_Translation.result = self._dst  # 声明为类变量，可在其他类中引用
            
        except Exception as e:  
            print(e)  
        finally:  
            if self._httpClient:  
                self._httpClient.close() 


class Extract_Values:
        
    def get_values():
        # @description: 通过运用正则表达式抽取文件中要翻译的内容，去掉不需要翻译的内容
        #               一般来说“=”右边的文本需要翻译，但以.html、.htm、.gif结尾的文件名不需要，以及<>标签内的内容不需要
        #               将获取回来的翻译结果放回原处，不需要翻译的保留原样
        # @return string value  传给API要翻译的字符串
        # @line_attrs list 存储“=”两边的内容
        output = open('LocaleResource_zh_CN.properties','w') #以写入模式新建/打开名为“LocaleResource_zh_CN.properties”的文件
        with open('LocaleResource_en_US.properties', 'r') as input_file: #以只读模式打开原文件
            for line in input_file:

                if line.startswith('#') : #保留原文件中的注释语句
                    output.write(line)
                    continue
                    
                if not line.strip(): #去掉每一行前后的空格
                    continue
                    
                line_attrs = line.strip().split('=') #去掉“=”，并将“=”两边的内容存在列表内
                                                     #列表的第一个元素是不用翻的内容（“=”左边）
                                                     #列表的第二个元素是不用翻的内容（“=”右边）                                   
                if len(line_attrs) == 0: #跳过空行
                    continue
                    
                value = ''.join([_.strip() for _ in line_attrs[1:]]) #将“=”右边的内容拼接为字符串
                reg = re.compile('<[^>]*>') #去掉<>标签及标签内容
                value = reg.sub('',value)
                
                if (value.endswith('.htm') or value.endswith('.html') or value.endswith('.gif')):
                    output.write(line) #保留.html、.htm、.gif结尾的语句
                    continue
                else:
                    Baidu_Translation().Baidu_connect(value) #调用连接API翻译的函数
                    str_convert = ''.join(line_attrs[:1])    #将不需要翻译的“=”左边的内容转为字符串
                    line = str_convert +''+'='+''+Baidu_Translation.result+'\n' #拼接“=”左边的内容和翻译结果
                    output.write(line) #写入文件
                    
                    



if __name__ == '__main__':
    value = Extract_Values.get_values()   