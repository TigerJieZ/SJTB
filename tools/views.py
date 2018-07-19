from django.http import FileResponse
from django.shortcuts import render
from tools.box.downloadBook.db.dbController import dbc
import threading
import pymysql


# Create your views here.

def toolsIndex(request):
    '''
    百宝箱首页
    :param request:
    :return:
    '''
    return render(request, "tools_index.html")


def downloadBookView(request):
    '''
    电子书下载器页面
    :param request:
    :return:
    '''
    return render(request, "dlBook.html")


def searchBookAction(request):
    '''
    处理搜索书目的表单
    :param request:
    :return:
    '''
    # 存放数据提交内容
    ctx = {}

    # 若表单内容存在
    if request.POST:
        # 获取书名搜索内容
        ctx['book_name'] = request.POST.get('book_name', False)

        # 查询书名匹配列表
        dbC=dbc('bookwarehouse')
        books=dbC.searchBookKey(ctx['book_name'])
        ctx['books']=books
        return render(request, 'dlBook.html', ctx)


    return render(request,'dlBook.html')

def downloadBookNew(request):
    '''
    下载书籍
    :param request:
    :return:
    '''
    # 存放数据提交内容
    ctx = {}
    bookID=request.GET.get('id')
    dbC=dbc('bookwarehouse')
    path=""

    # 在数据库中查询指定书的主体信息
    sql="select * from books where id=%s"
    db = pymysql.connect(host="localhost", user="root", password="sujie1997", port=3306, db=dbName,
                                  charset='utf8')
    cursor=db.cursor()
    cursor.execute(sql,(bookID))

    row=cursor.fetchone()
    book_name=row[1]
    book_category=row[2]
    book_auth=row[3]

    # 查询书籍内容，并输出成文件形式
    sql="select * from chapters where bookID=%s order by chapterName desc "
    cursor.execute(sql,(bookID))
    row=cursor.fetchone()
    file=open('home/')
    while row:

        row=cursor.fetchone()


def downloadBook(request):
    '''
    下载书籍
    :param request:
    :return:
    '''
    # 存放数据提交内容
    ctx = {}
    bookID=request.GET.get('id')
    dbC=dbc('bookwarehouse')
    path=""

    def get():
        '''
        子线程用于下载小说
        '''
        nonlocal path
        path=dbC.getBook(bookID)
        ctx['path']=path
        response = FileResponse(path)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="example.tar.gz"'

    book_thread=threading.Thread(target=get)

    book_thread.start()

    return render(request,'SUCCESS.html',ctx)

