import pymysql
from tools.box.downloadBook.spyder import aszwDownloader, aszwParser
import sys


class dbc:
    def __init__(self, dbName):
        # 初始化数据库连接
        self.db = pymysql.connect(host="localhost", user="root", password="123456", port=3306, db=dbName,
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
        print('-----开始插入书籍：',book['name'],'-----')
        cursor = self.db.cursor()
        # 插入书本信息
        sql = "insert into books(bookName,bookCategory,bookAuth,bookWordage,bookURL,source) values(%s,%s,%s,%s,%s,%s,%s)"
        try:
            # 执行插入sql语句
            cursor.execute(sql, (
                book['name'], book['category'], book['auth'],int(book['wordage']),
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
                        print(e)
                print('-----书籍：',book['name'],'插入成功-----')

            except Exception as e:
                s = sys.exc_info()
                print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
                print(e)

        except Exception as e:
            # 若出错，事务回滚
            self.db.rollback()
            s = sys.exc_info()
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
            return False

    def initDatebase(self):
        '''
        初始化数据库：爬取整个书籍网站至数据库，
        :return:
        '''
        # 初始化解析模块
        parser = aszwParser.aszwParser()
        downloader = aszwDownloader.Downloader()

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
                book={}
                book['name'] = title
                book['category'] = category
                book['auth'] = auth
                book['wordage'] = -1
                book['book_url'] = book_url
                book['source']=1
                chapters=[]
                for section_url in sections_url:
                    # 遍历章节页面，解析出章节名和正文
                    html_cont = downloader.m_download(section_url)
                    new_data = parser.parser_Section(html_cont)
                    # 将章节名和章节url存入chapters
                    chapter={'chapter_name':new_data['section_title'],'chapter_url':section_url}
                    chapters.append(chapter)
                # 章节信息列表存入book中
                book['chapters']=chapters
                self.insetBook(book)
                self.book_warehouse.append(book)

