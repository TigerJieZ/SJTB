from django.http import FileResponse
from django.shortcuts import render
from tools.box.downloadBook.db.dbController import dbc
import threading


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

