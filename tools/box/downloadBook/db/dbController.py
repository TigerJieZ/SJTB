import _thread

import pymysql
from tools.box.downloadBook.spyder import aszwDownloader, aszwParser, aszwWriter
from tools.box.downloadBook.camouflage import cookies
from tools.box.downloadBook.camouflage import proxies
import sys
import random
import os


class dbc:
    def __init__(self, dbName):
        # 初始化数据库连接
        self.db = pymysql.connect(host="localhost", user="root", password="sujie1997", port=3306, db=dbName,
                                  charset='utf8')
        # 初始化书籍仓库列表
        self.book_warehouse = []

    def __str__(self):
        title = "《《《《《《《电子书数据库》》》》》》》"

        return title

    def insetBook(self, book):
        '''
        接收一个book，插入数据库
        :param book:字典类型，包含key:name(书名)、category(类别)、book_url(书籍url)、chapters_url(章节url列表)
            、auth(作者)、(create_date)书籍初次存入时间、wordage(字数)
        :return:
        '''
        print('-----开始插入书籍：', book['name'], '-----')
        cursor = self.db.cursor()
        # 插入书本信息
        sql = "insert into books(bookName,bookCategory,bookAuth,bookWordage,bookURL,source) values(%s,%s,%s,%s,%s,%s)"
        try:
            # 执行插入sql语句
            cursor.execute(sql, (
                book['name'], book['category'], book['auth'], int(book['wordage']),
                book['book_url'], book['source']))
            # 提交事务
            self.db.commit()
            try:
                # 查询刚刚插入的书籍id
                sql = "select id from books where bookName=%s and bookCategory=%s and bookAuth=%s"
                cursor.execute(sql, (book['name'], book['category'], book['auth']))
                row = cursor.fetchone()
                id = 0
                while row:
                    id = row[0]
                    row = cursor.fetchone()

                # 插入书籍目录信息
                for chapter in book['chapters']:
                    sql = "insert into chapters(bookID, chapterName, chapterUrl,context) values(%s,%s,%s,%s)"
                    try:
                        # 执行插入sql
                        cursor.execute(sql,
                                       (int(id), chapter['chapter_name'], chapter['chapter_url'], chapter['context']))
                        # 提交事务
                        self.db.commit()
                    except Exception as e:
                        # 若出错，回滚事务
                        self.db.rollback()
                        s = sys.exc_info()
                        print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
                print('-----书籍：', book['name'], '插入成功-----')

            except Exception as e:
                s = sys.exc_info()
                print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))

        except Exception as e:
            # 若出错，事务回滚
            self.db.rollback()
            s = sys.exc_info()
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
            return False

    def initCookies(self):
        '''
        使用account表中的用户名和密码获取cookie，存入数据库中
        :return:
        '''

        # 查询account中储存的23zw网的用户
        sql = "select * from account where source=%s"
        cursor = self.db.cursor()
        cursor.execute(sql, (1))
        row = cursor.fetchone()
        users = []
        while row:
            user = {}
            user['user_name'] = row[1]
            user['password'] = row[2]
            users.append(user)
            row = cursor.fetchone()

        # 用账户去模拟登陆23zw网，获取cookie
        i = 1
        for cookie in cookies.run(users):
            self.insertCookie({'content': cookie['content'], 'state': True, 'userID': i})
            i += 1

    def insertCookie(self, cookie):
        '''
        将cookie存入数据库中
        :param cookie: 应包括的key:content state userID
        :return:
        '''

        # 执行插入cookie的sql语句
        sql = "insert into cookies(content, state, userID) VALUES (%s,%s,%s)"
        cursor = self.db.cursor()
        try:
            # 执行插入sql
            print(cookie)
            cursor.execute(sql, (str(cookie['content']), cookie['state'], cookie['userID']))
            # 提交事务
            self.db.commit()
            print('cookie', cookie['userID'], '插入成功→→→→→→→')
        except Exception as e:
            # 若出错，回滚事务
            self.db.rollback()
            s = sys.exc_info()
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))

    def addAccount(self, user):
        '''
        添加一个账户到数据库中
        :param user: user应包含keys: name password source
        :return:
        '''

        # 执行sql语句，讲账户信息插入到数据库中
        sql = "insert into account(name,password,source) values(%s,%s,%s)"
        cursor = self.db.cursor()
        try:
            # 执行插入sql
            cursor.execute(sql, (user['name'], user['password'], user['source']))
            # 提交事务
            self.db.commit()
        except Exception as e:
            # 若出错，回滚事务
            self.db.rollback()
            s = sys.exc_info()
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))

    def initDatebase(self):
        '''
        初始化数据库：爬取整个书籍网站至数据库，
        :return:
        '''
        # 初始化解析模块
        parser = aszwParser.Parser()
        downloader = aszwDownloader.Downloader()
        cookies = self.getCookies()
        user_agent = self.getUserAgent()
        proxy_list = proxies.get_proxy('http://www.xicidaili.com/nn/', {'User-agent': 'Mr.Zhang'})

        # 从傲视中文网的书籍列表中把列表url爬取下来
        list_url = parser.find_list_urls()
        # 遍历列表url得到包含书目录url的列表
        for list in list_url:
            # 从列表页面中解析出书url列表
            books_urls = parser.find_books_urls(list)
            # 遍历书的主页
            for book_url in books_urls:
                # 解析主页得到章节url列表、书名、类别、作者
                sections_url, title, category, auth = parser.find_section_urls(book_url)
                book = {}
                print('----正在爬取书籍：', title)
                book['name'] = title
                book['category'] = category
                book['auth'] = auth
                book['wordage'] = -1
                book['book_url'] = book_url
                book['source'] = 1
                chapters = []

                # 若存在书籍
                if os.path.exists("/home/ubuntu/book/" + title + "_" + auth + ".txt"):
                    print(title + "已下载。。。")
                    continue

                outputer = aszwWriter.Writer(len(sections_url), title, auth)

                # 解析章节信息存入chapters
                def parseSction(section_url):
                    # 从cookie库中随机获取一个cookie用于下载页面
                    cookie = cookies[random.randint(0, 10)]
                    proxy = random.choice(proxy_list)
                    # 遍历章节页面，解析出章节名和正文
                    html_cont = downloader.m_download(section_url, cookie=cookie, user_agent=random.choice(user_agent),
                                                      proxy=proxy)
                    new_data = parser.parser_Section(html_cont)

                    # 使用外部变量
                    nonlocal threads, chapters

                    # 将章节名和章节url存入chapters
                    chapter = {'chapter_name': new_data['section_title'], 'chapter_url': section_url}
                    chapters.append(chapter)

                    # 收集章节内容以便章节爬取结束后写入文件
                    outputer.collect_data(new_data)

                    # 退出线程，线程数-1
                    threads -= 1

                # 多线程访问
                threads = 0
                i = 1
                while sections_url:
                    while sections_url and threads < 40:
                        threads += 1
                        section_url = sections_url.pop()
                        _thread.start_new_thread(parseSction, (section_url,))
                        i += 1
                # for section_url in sections_url:
                #     # 从cookie库中随机获取一个cookie用于下载页面
                #     cookie = cookies[random.randint(0, 10)]
                #     proxy = random.choice(proxy_list)
                #     # 遍历章节页面，解析出章节名和正文
                #     html_cont = downloader.m_download(section_url,cookie=cookie,user_agent=random.choice(user_agent),proxy=proxy)
                #     new_data = parser.parser_Section(html_cont)
                #     # 将章节名和章节url存入chapters
                #     chapter = {'chapter_name': new_data['section_title'], 'chapter_url': section_url}
                #     chapters.append(chapter)
                # 章节信息列表存入book中
                book['chapters'] = chapters
                self.insetBook(book)
                self.book_warehouse.append(book)

                print('开始写入书籍至本地')
                # 写入书籍内容到文件
                print(outputer.output_html())

    def checkBookExist(self, book_url):
        '''
        检查该书籍是否已爬取
        :param book_name:书名
        :param book_auth:作者
        :param book_category:类别
        :return:布尔值，存在返回true，否则返回false
        '''
        sql = "select count(id) from books where bookURL=%s"
        cursor = self.db.cursor()
        cursor.execute(sql, (book_url))
        row = cursor.fetchone()
        if row[0] is 1 or row[0] is '1':
            print('该书籍已爬取，跳过__________')
            return True
        else:
            print('该书籍未爬取，进入爬取_________')
            return False

    def initDatebaseContext(self):
        '''
        初始化数据库：爬取整个书籍网站至数据库，包括章节内容
        :return:
        '''
        # 初始化解析模块
        parser = aszwParser.Parser()
        downloader = aszwDownloader.Downloader()
        cookies = self.getCookies()
        user_agent = self.getUserAgent()
        proxy_list = proxies.get_proxy('http://www.xicidaili.com/nn/',
                                       {'User-agent': 'Mr.Zhang'})

        # 从傲视中文网的书籍列表中把列表url爬取下来
        list_url = parser.find_list_urls()
        # 遍历列表url得到包含书目录url的列表
        for list in list_url:
            # 从列表页面中解析出书url列表
            books_urls = parser.find_books_urls(list)
            # 遍历书的主页
            for book_url in books_urls:
                # 解析主页得到章节url列表、书名、类别、作者
                try:
                    # 若存在书籍
                    if self.checkBookExist(book_url):
                        continue

                    sections_url, title, category, auth = parser.find_section_urls(book_url)
                    book = {}
                    print('----正在爬取书籍：', title)
                    book['name'] = title
                    book['category'] = category
                    book['auth'] = auth
                    book['wordage'] = -1
                    book['book_url'] = book_url
                    book['source'] = 1
                    chapters = []

                    # 书籍字数
                    wordage=0

                    # 解析章节信息存入chapters
                    def parseSction(section_url, i):
                        # 从cookie库中随机获取一个cookie用于下载页面
                        cookie = cookies[random.randint(0, 10)]
                        proxy = random.choice(proxy_list)
                        # 遍历章节页面，解析出章节名和正文
                        html_cont = downloader.m_download(section_url, cookie=cookie,
                                                          user_agent=random.choice(user_agent),
                                                          proxy=proxy)
                        new_data = parser.parser_Section(html_cont)

                        try:
                            # 使用外部变量
                            nonlocal threads, chapters,wordage

                            # 将章节名和章节url存入chapters
                            chapter = {'chapter_name': i, 'chapter_url': section_url,
                                       'context': new_data['text']}
                            chapters.append(chapter)

                            wordage += len(new_data['text']) - new_data['text'].count("    ") * 4 - 25
                        except Exception as e:
                            print(section_url,'-----章节内容获取失败')
                        finally:
                            # 退出线程，线程数-1
                            threads -= 1

                    # 多线程访问
                    threads = 0
                    # 章节url的key值
                    i = 1
                    while sections_url:
                        while sections_url and threads < 20:
                            threads += 1
                            section_url = sections_url.pop(i)
                            _thread.start_new_thread(parseSction, (section_url, self.i2a(i),))
                            i += 1
                    # for section_url in sections_url:
                    #     # 从cookie库中随机获取一个cookie用于下载页面
                    #     cookie = cookies[random.randint(0, 10)]
                    #     proxy = random.choice(proxy_list)
                    #     # 遍历章节页面，解析出章节名和正文
                    #     html_cont = downloader.m_download(section_url,cookie=cookie,user_agent=random.choice(user_agent),proxy=proxy)
                    #     new_data = parser.parser_Section(html_cont)
                    #     # 将章节名和章节url存入chapters
                    #     chapter = {'chapter_name': new_data['section_title'], 'chapter_url': section_url}
                    #     chapters.append(chapter)
                    # 章节信息列表存入book中
                    book['chapters'] = chapters
                    # 书籍字数存入book中
                    book['wordage']=wordage
                    self.insetBook(book)
                    self.book_warehouse.append(book)
                except Exception as e:
                    s = sys.exc_info()
                    print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
                    books_urls.append(book_url)

    def i2a(self, i):
        '''
        讲解析的章节顺序调整成按章节顺序
        :return:
        '''
        remainder = i % 8
        if remainder is 1 or remainder is 0:
            return i
        elif remainder is 2:
            return i + 3
        elif remainder is 3:
            return i - 1
        elif remainder is 4:
            return i + 2
        elif remainder is 5:
            return i - 2
        elif remainder is 6:
            return i + 1
        elif remainder is 7:
            return i - 3

    def getUserAgent(self):
        MY_USER_AGENT = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
            "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        ]
        return MY_USER_AGENT

    def getCookies(self):
        '''
        获取所有cookies
        :return:
        '''
        sql = "select * from cookies"
        cursor = self.db.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        cookies = []
        while row:
            cookie = {}
            cookie['content'] = row[1]
            cookie['state'] = row[2]
            id = row[3]
            # 查询user
            cookies.append(cookie)
            row = cursor.fetchone()
        print('数据库中cookie数：', len(cookies))
        return cookies

    def searchBookKey(self, key_bookName):
        '''
        查询书名匹配列表
        :return:
        '''
        cursor = self.db.cursor()
        sql = "select * from books where bookName like %s"
        cursor.execute(sql, ('%' + key_bookName + '%'))
        books = []
        row = cursor.fetchone()
        while row:
            book = {}
            book['id'] = row[0]
            book['name'] = row[1]
            book['category'] = row[2]
            book['auth'] = row[3]
            book['update_date']=row[5]
            book['wordage']=row[6]
            book['book_url']=row[7]
            book['source'] = row[8]
            books.append(book)
            row = cursor.fetchone()

        return books

    def getBook(self, id):
        '''
        下载书籍至服务器
        :param id:
        :return:
        '''

        # 获取书目url
        cursor = self.db.cursor()
        sql = "select * from books where id = %s"
        cursor.execute(sql, (id))
        row = cursor.fetchone()
        book_url = row[7]

        # 初始化解析模块
        parser = aszwParser.Parser()
        downloader = aszwDownloader.Downloader()
        cookies = self.getCookies()
        user_agent = self.getUserAgent()

        proxy_list = proxies.get_proxy('http://www.xicidaili.com/nn/', {'User-agent': 'Mr.Zhang'})

        # 解析主页得到章节url列表、书名、类别、作者
        sections_url, title, category, auth = parser.find_section_urls(book_url)
        print('----正在爬取书籍：', title)
        chapters = []

        # 若存在书籍
        if os.path.exists("/home/ubuntu/book/" + title + "_" + auth + ".txt"):
            print(title + "已下载。。。")
            return

        # 书籍内容抓取器
        outputer = aszwWriter.Writer(len(sections_url), title, auth)

        # 解析章节信息存入chapters
        def parseSction(section_url):
            try:
                # 从cookie库中随机获取一个cookie用于下载页面
                cookie = cookies[random.randint(0, 10)]
                proxy = random.choice(proxy_list)
                # 遍历章节页面，解析出章节名和正文
                html_cont = downloader.m_download(section_url, cookie=cookie, user_agent=random.choice(user_agent),
                                                  proxy=proxy)
                new_data = parser.parser_Section(html_cont)

                # print('爬取第',new_data['section_title'],'章成功')

                # 收集章节内容以便章节爬取结束后写入文件
                outputer.collect_data(new_data)

                # 使用外部变量
                nonlocal threads, chapters

                # 将章节名和章节url存入chapters
                chapter = {'chapter_name': new_data['section_title'], 'chapter_url': section_url,
                           'chapter_context': new_data['text']}
                chapters.append(chapter)
            except Exception as e:
                print(e)
            finally:
                # threads线程必须放置在finally中-1，否则当该函数出现bug停掉，则threads不会被-1
                # 退出线程，线程数-1
                threads -= 1

        # 多线程解析章节内容
        threads = 0
        print('需解析的章节数:', len(sections_url))
        while sections_url:
            while sections_url and threads < 40:
                # print(threads)
                threads += 1
                section_url = sections_url.pop()
                _thread.start_new_thread(parseSction, (section_url,))

        while threads > 0:
            # print('已爬取',sum1,'已进入爬取',sum2)
            # print(threads)
            pass

        print('开始写入书籍至本地')
        # 写入书籍内容到文件
        print(outputer.output_html())

    def getBookContext(self, bookID):
        # 在数据库中查询指定书的主体信息
        sql = "select * from books where id=%s"
        db = self.db
        cursor = db.cursor()
        cursor.execute(sql, (bookID))

        row = cursor.fetchone()
        book_name = row[1]
        book_category = row[2]
        book_auth = row[3]

        # 查询书籍内容，并输出成文件形式
        sql = "select * from chapters where bookID=%s order by chapterName"
        cursor.execute(sql, (bookID))
        row = cursor.fetchone()
        path = '/home/ubuntu/Python_Workspace/SJTB/static/book/' + book_name + '_' + book_auth + '_' + book_category + '.txt'
        file = open(path, 'w')
        while row:
            title = row[2]
            context = row[4]
            file.writelines('第' + str(title) + '章')
            context = context.replace("    ", "\r\n    ")
            file.write(context)
            row = cursor.fetchone()
        file.close()

        return path, book_name + '_' + book_auth + '_' + book_category + '.txt'

    def wordCount(self):
        '''
        统计书籍的字数
        :return:
        '''

        # 查询未统计字数的书籍ID
        sql="select id from books where bookWordage=%s"
        cursor=self.db.cursor()
        cursor.execute(sql,(-1))
        row=cursor.fetchone()
        book_id_list=[]
        while row:
            book_id_list.append(row[0])
            row=cursor.fetchone()

        for book_id in book_id_list:
            # 查询该书籍的章节内容
            sql = "select context,id from chapters where bookID=%s"
            cursor.execute(sql, (book_id))
            chapter_row = cursor.fetchone()
            wordage=0
            while chapter_row:
                # 减去空格数占用的字数，每段空格数占4个字数,再减去一头一尾的空格字数大约25个字数
                wordage+=len(chapter_row[0])-chapter_row[0].count("    ")*4-25
                chapter_row = cursor.fetchone()
            print('-------',wordage,'-------')

            sql="update books set bookWordage=%s where id=%s"

            try:
                # 执行更新字数sql
                cursor.execute(sql, (wordage, book_id))
                # 提交事务
                self.db.commit()
            except Exception as e:
                # 若出错，回滚事务
                self.db.rollback()
                s = sys.exc_info()
                print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))





