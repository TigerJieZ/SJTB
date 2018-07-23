from django.http import FileResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils.encoding import escape_uri_path

from tools.box.downloadBook.db.dbController import dbc
from tools.box.audioProcess.formatConversion import transAudio
import threading
import pymysql
import os


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

def file_iterator(file_name, chunk_size=8192):
    with open(file_name,'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break

def downloadBookNew(request):
    '''
    下载书籍
    :param request:
    :return:
    '''
    # 获取请求下载书籍的id
    bookID=request.GET.get('id')

    dbC=dbc('bookwarehouse')

    path,file_name=dbC.getBookContext(bookID)

    response = StreamingHttpResponse(file_iterator(path))
    response['Content-Type'] = 'application/octet-stream'
    # 中文名需如此操作才可正常在客户端显示
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(file_name))

    # from django.http import HttpResponseRedirect
    # dict={}
    # dict['file_path']='/static/book/'+file_name
    # dict['file_name']=file_name
    return response



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

def audioTransformView(request):
    '''
    音频格式转换页面
    :param request:
    :return:
    '''

    return render(request,"audioTrans.html")

def audioTransformAction(request):
    type=request.POST.get('audio_type')
    print(type)
    obj = request.FILES.get('audio_file')
    import os

    print(obj.name)
    f = open('/home/ubuntu/Python_Workspace/SJTB/static/audio/'+obj.name, 'wb')
    for chunk in obj.chunks():
        f.write(chunk)

    f.close()

    new_path,new_name=transAudio('/home/ubuntu/Python_Workspace/SJTB/static/audio/'+obj.name,type)

    print(new_path)

    response = StreamingHttpResponse(file_iterator(new_path))
    response['Content-Type'] = 'application/octet-stream'
    # 中文名需如此操作才可正常在客户端显示
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(new_name))

    return response