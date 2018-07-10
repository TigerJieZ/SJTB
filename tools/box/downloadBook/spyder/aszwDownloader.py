# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse


class Downloader:

    def m_download(self, url,user_agent, cookie, proxy=None, num_retries=2):
        headers = {'User-agent': user_agent,'cookie':cookie['content']}
        request = urllib.request.Request(url, headers=headers)

        opener = urllib.request.build_opener()
        if proxy:
            proxy_params = {urllib.parse.urlparse(url).scheme: proxy}
            opener.add_handler(urllib.request.ProxyHandler(proxy_params))
        try:
            html = opener.open(request).read()
        except urllib.request.URLError as e:
            print('Download error:', e.reason)
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return self.m_download(url,cookie=cookie, user_agent=user_agent, proxy=proxy, num_retries=num_retries - 1)
        return html
