# -*- coding: utf-8 -*-
import threading
import time
import os

from tools.box.downloadBook.spyder import aszwDownloader, aszwParser, aszwWriter

# 小说目录
home = "http://www.23zw.me/olread/68/68913/"
SLEEP_TIME=0.5
SLEEP_TIME2=0.1

class SpiderMain(object):
    def __init__(self):
        self.downloader = aszwDownloader.Downloader()
        self.parser = aszwParser.aszwParser()

    def process_book(self,section_urls,title):
        print('setction nume is:' + str(len(section_urls)))
        i = 0
        self.outputer = aszwWriter.Writer(len(section_urls))

        def process_section(url, title):
            try:
                html_cont = self.downloader.m_download(url)
                new_data = self.parser.parser_Section(html_cont)
                self.outputer.collect_data(new_data, title)
                print("第"+"%d"%new_data['section_title']+"章"+"下载中...")
            except Exception as e:
                print(e)
                print("下载失败!!!")

        threads = []
        while threads or section_urls:
            # the crawl is still active
            for thread in threads:
                if not thread.is_alive():
                    # remove the stopped threads
                    threads.remove(thread)
            while len(threads) < 20 and section_urls:
                url=section_urls.pop()
                thread=threading.Thread(target=process_section(url,title))
                thread.setDaemon(True)
                thread.start()
                threads.append(thread)
            time.sleep(SLEEP_TIME2)

        '''for url in section_urls:
            #try:
            i += 1
            html_cont = self.downloader.download(url)
            print('Downloading section' + str(i))
            new_data = self.parser.parser_Section(html_cont)
            self.outputer.collect_data(new_data, title)
            #except:
            #    print('Section ' + str(i) + ' downloading Error!')'''
        self.outputer.output_html()

    def craw(self,max_threads):
        list_urls=self.parser.find_list_urls()
        for list_url in list_urls:
            book_urls=self.parser.find_books_urls(list_url)
            threads=[]
            print("共有"+str(len(book_urls))+"本书")
            while threads or book_urls:
                for thread in threads:
                    if not thread.is_alive():
                        threads.remove(thread)
                while len(threads) < max_threads and book_urls:
                    print('进程数为:'+str(len(threads)))
                    book_url=book_urls.pop()
                    section_urls,title=self.parser.find_section_urls(book_url)
                    if os.path.exists("C:/book/" + title + ".txt"):
                        print(title+'已下载')
                    else:
                        thread = threading.Thread(target=self.process_book(section_urls,title))
                        thread.setDaemon(True)
                        thread.start()
                        threads.append(thread)
                time.sleep(SLEEP_TIME)

if __name__ == '__main__':
    spider=SpiderMain()
    spider.craw(20)