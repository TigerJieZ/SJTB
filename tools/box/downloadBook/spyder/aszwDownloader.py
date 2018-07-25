# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import time
import requests


class Downloader:

    def m_download(self, url,user_agent, cookie, proxy=None, num_retries=2):
        headers = {'User-agent': user_agent,'cookie':cookie['content']}
        request = urllib.request.Request(url, headers=headers)


        opener = urllib.request.build_opener()
        if proxy:
            # 使用选择的代理构建代理处理器对象
            httpproxy_handler = urllib.request.ProxyHandler(proxy)
            opener = urllib.request.build_opener(httpproxy_handler)
        try:
            html = opener.open(request).read()
        except Exception as e:
            print('Download error:', e)
            print('-----proxy:',proxy,'-----')
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return self.m_download(url,cookie=cookie, user_agent=user_agent, proxy=proxy, num_retries=num_retries - 1)
        # 延时爬取，
        time.sleep(0.1)

        return html
