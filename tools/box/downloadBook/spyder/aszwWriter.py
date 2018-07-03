# -*- coding: utf-8 -*-

import os

class Writer:
    def __init__(self,length):
        self.datas =list(range(0,length))
        self.title=""

    def collect_data(self, data,title):
        if data is None:
            return
        self.datas[data['section_title']]=data
        self.title=title

    def output_html_old(self):
        try:
            os.mkdir("book/"+self.title)
        except:
            print("该书目录已存在")
        i=0
        for data in self.datas:
            if os.path.exists("book/"+self.title + "/" +"%d"%data['section_title']+".txt"):
                print("book/"+self.title + "/" +"%d"%data['section_title']+".txt"+"已存在")
                pass
            else:
                try:
                    fout = open("book/"+self.title + "/" +"%d"%data['section_title']+".txt", 'a')
                    fout.write("%s" %data['text'])
                except:
                    print("%d"%data['section_title']+"写入失败")
                fout.close()

    def output_html(self):
        try:
            os.mkdir("C:/book")
        except:
            print("书包目录已存在")
        if os.path.exists("C:/book/" + self.title + ".txt"):
            print(self.title+"已下载。。。")
        else:
            fout = open("C:/book/" + self.title + ".txt", 'a')
            for data in self.datas:
                try:
                    fout.write("第"+str(data['section_title'])+"章")
                    fout.write("%s"%data['text'])
                except Exception as e:
                    print(e)
                    print(self.title+"写入失败！--")