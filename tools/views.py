from django.shortcuts import render


# Create your views here.
def downloadBook(request):
    # spider = SpiderMain()
    # spider.craw(20)
    render(request,"SUCCESS.html")