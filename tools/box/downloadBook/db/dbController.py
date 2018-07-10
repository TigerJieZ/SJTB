import pymysql
from tools.box.downloadBook.spyder import aszwDownloader, aszwParser
from tools.box.downloadBook.camouflage import cookies
from tools.box.downloadBook.camouflage import proxies
import sys
import random


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
                    sql = "insert into chapters(bookID, chapterName, chapterUrl) values(%s,%s,%s)"
                    try:
                        # 执行插入sql
                        cursor.execute(sql, (int(id), chapter['chapter_name'], chapter['chapter_url']))
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
        i=1
        for cookie in cookies.run(users):
            self.insertCookie({'content':cookie['content'],'state':True,'userID':i})
            i+=1

    def insertCookie(self,cookie):
        '''
        将cookie存入数据库中
        :param cookie: 应包括的key:content state userID
        :return:
        '''

        # 执行插入cookie的sql语句
        sql="insert into cookies(content, state, userID) VALUES (%s,%s,%s)"
        cursor=self.db.cursor()
        try:
            # 执行插入sql
            print(cookie)
            cursor.execute(sql,(str(cookie['content']),cookie['state'],cookie['userID']))
            # 提交事务
            self.db.commit()
            print('cookie',cookie['userID'],'插入成功→→→→→→→')
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
        user_agent=self.getUserAgent()
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
                book['name'] = title
                book['category'] = category
                book['auth'] = auth
                book['wordage'] = -1
                book['book_url'] = book_url
                book['source'] = 1
                chapters = []
                for section_url in sections_url:
                    # 从cookie库中随机获取一个cookie用于下载页面
                    cookie = cookies[random.randint(0, 10)]
                    proxy = random.choice(proxy_list)
                    # 遍历章节页面，解析出章节名和正文
                    html_cont = downloader.m_download(section_url,cookie=cookie,user_agent=random.choice(user_agent),proxy=proxy)
                    new_data = parser.parser_Section(html_cont)
                    # 将章节名和章节url存入chapters
                    chapter = {'chapter_name': new_data['section_title'], 'chapter_url': section_url}
                    chapters.append(chapter)
                # 章节信息列表存入book中
                book['chapters'] = chapters
                self.insetBook(book)
                self.book_warehouse.append(book)

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
        sql="select * from cookies"
        cursor=self.db.cursor()
        cursor.execute(sql)
        row=cursor.fetchone()
        cookies=[]
        while row:
            cookie={}
            cookie['content']=row[1]
            cookie['state']=row[2]
            id=row[3]
            # 查询user
            cookies.append(cookie)
            row=cursor.fetchone()
        print('数据库中cookie数：',len(cookies))
        return cookies
