import urllib.request
import re
import telnetlib
import _thread
import time

url = 'http://www.xicidaili.com/nn/'


def get_ip_list(url, headers):
    '''
    从代理网站上获取代理
    :param url: 代理IP的网站
    :param headers:
    :return:
    '''

    # 存放代理IP
    ip_list = []

    # url
    opener = urllib.request.build_opener()
    request = urllib.request.Request(url, headers=headers)
    page = opener.open(request).read().decode("utf8")

    # 匹配代理IP的正则表达式
    re_key = ">\d+.\d+.\d+.\d+<"
    # 编译正则表达式
    re_c = re.compile(re_key)
    ul_list = re.findall(re_c, page)

    # 去除左右<>
    ip_list = []
    for ip in ul_list:
        ip = ip[1:-1]
        ip_list.append(ip)
    print('共找到代理IP：', len(ip_list), '个')
    return ip_list


def get_port_list(url, headers):
    '''
        从代理网站上获取代理IP的端口
        :param url: 代理IP的网站
        :param headers:
        :return:
        '''

    # 存放代理IP
    port_list = []

    # url
    opener = urllib.request.build_opener()
    request = urllib.request.Request(url, headers=headers)
    page = opener.open(request).read().decode("utf8")

    # 匹配代理IP的正则表达式
    re_key = ">\d+<"
    # 编译正则表达式
    re_c = re.compile(re_key)
    ul_list = re.findall(re_c, page)

    # 去除左右<>
    port_list = []
    for port in ul_list:
        port = port[1:-1]
        port_list.append(port)
    port_list = port_list[:-11]
    print('共找到代理端口：', len(port_list), '个')
    return port_list


def find_proxy(url, headers):
    # 分别捕获代理ip和port
    ip_list = get_ip_list(url, headers)
    port_list = get_port_list(url, headers)

    # 如果ip数和端口数不一致，报错并返回空
    if len(ip_list) is not len(port_list):
        print('IP捕获数与端口数不一致！')
        return

    # 如果ip数与端口数一致，则基本确认爬取正常，进行端口和ip的对接
    proxy_list = []
    for i in range(len(ip_list)):
        temp = {}
        temp['ip'] = ip_list[i]
        temp['port'] = port_list[i]
        proxy_list.append(temp)

    print('共捕获代理：', len(proxy_list), '个')

    return proxy_list


def formatProxy(proxy_list):
    '''
    格式化proxy，正确的proxy格式为：
    proxies = {
        http: 'http://114.99.7.122:8752'
        https: 'https://114.99.7.122:8752'
    }
    :param proxy_list:
    :return:
    '''
    list = []
    for proxy in proxy_list:
        temp = {}
        temp['http'] = proxy['ip'] + ':' + proxy['port']
        list.append(temp)

    return list


def get_proxy(url, headers):
    '''
    从西刺代理指定页面中获取代理,并进行可用性过滤
    :param url:
    :param headers:
    :return:
    '''
    # 捕捉proxy
    proxy_list = find_proxy(url, headers)

    # 可用性检查
    ava_proxy_list = check(proxy_list)

    # 格式化proxy
    result = formatProxy(ava_proxy_list[:-20])

    return result


def check(proxy_list):
    ava_proxy_list = []
    threads = 1

    def checkAvailability(proxy):
        '''
        检验单个proxy的可用性
        :param proxy: 代理字典
        :return: 是否可用，True/False
        '''
        try:
            telnetlib.Telnet(proxy['ip'], port=proxy['port'], timeout=20)
        except:
            # print('----', proxy['ip'], ':', proxy['port'], '失效！')
            pass
        else:
            # print('++++', proxy['ip'], ':', proxy['port'], '有效！')
            ava_proxy_list.append(proxy)
        nonlocal threads
        threads -= 1

    i = 1
    while proxy_list:
        # # the crawl is still active
        # for m_thread in threads:
        #     if not m_thread.is_alive():
        #         # remove the stopped threads
        #         threads.remove(m_thread)
        while threads < 40 and proxy_list:
            threads += 1
            # print('线程数：', threads)
            # print('第', i, '个proxy检验中.......')
            proxy = proxy_list.pop()
            _thread.start_new_thread(checkAvailability, (proxy,))
            # print(_thread.start_new_thread(checkAvailability, (proxy,)))
            i += 1
        # time.sleep(0.1)

    # 等待剩余线程结束
    while threads > 1:
        # print('线程数：',threads)
        pass

    print('可用代理有', len(ava_proxy_list), '个')
    return ava_proxy_list
