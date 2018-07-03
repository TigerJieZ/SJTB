import sys
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class WeiboCookies():
    def __init__(self, username, password, browser):
        self.url = 'https://www.23zw.me/login.php'
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password

    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        self.browser.delete_all_cookies()
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
        password = self.wait.until(EC.presence_of_element_located((By.NAME, 'password')))
        submit = self.wait.until(EC.element_to_be_clickable((By.NAME, 'Submit')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        time.sleep(1)
        submit.click()

    def password_error(self):
        """
        判断是否密码错误
        :return:
        """
        try:
            return WebDriverWait(self.browser, 5).until(
                EC.text_to_be_present_in_element((By.ID, 'errorMsg'), '用户名或密码错误'))
        except TimeoutException:
            return False

    def login_successfully(self):
        """
        判断是否登录成功
        :return:
        """
        try:
            return bool(
                WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, self.username))))
        except TimeoutException:
            return False

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        try:
            img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'patt-shadow')))
        except TimeoutException:
            print('未出现验证码')
            self.open()
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_cookies(self):
        """
        获取Cookies
        :return:
        """
        return self.browser.get_cookies()

    def run(self, isWeiboImage=False):
        """
        破解入口
        :return:
        """
        self.open()
        # 如果不需要验证码直接登录成功
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        # 登录成功读取cookie
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        else:
            return {
                'status': 3,
                'content': '登录失败'
            }


# 捕获每个账号的cookie
def run(account_list):
    cookies = []
    print('共需获取cookies数：', len(account_list))
    i = 1
    for account in account_list:
        # 记录每次cookie获取耗时
        now=time.time()
        # cookie获取
        try:
            # 启动display供网页在虚拟窗口中打开
            display = Display(visible=0, size=(800, 800))
            display.start()
            print(account)
            cookies.append(WeiboCookies(account['user_name'], account['password'], webdriver.Chrome()).run())
        except Exception as e:
            s = sys.exc_info()
            print("Error '%s' happened on line %d" % (s[1], s[2].tb_lineno))
            print(e)
            cookies.append(WeiboCookies(account['user_name'], account['password'], webdriver.Chrome()).run())
        finally:
            display.stop()

        print('cookie获取耗时：', time.time() - now)
        print('已获取cookie数：', i)
        print(cookies)
        i += 1
    return cookies


if __name__ == '__main__':
    print(run([{'user_name': 'sujie1997', 'password': 'sujie1997'}]))
    print(run([{'user_name': 'sujie1997', 'password': 'sujie1997'}]))
