import requests
from lxml import etree

class Github(object):
    def __init__(self):
        # init函数中建议放属性、公共变量、配置项、全局需要访问的
        # url
        self.login_url = 'https://github.com/login'
        self.do_login_url = 'https://github.com/session'
        self.profile_url = 'https://github.com/settings/profile'
        # 请求会话
        self.headers = {
            'Host': 'github.com',
            'Referer': 'https://github.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        self.s = requests.Session()
        # 账户相关
        self.authenticity_token = None
        self.login = None
        self.password = None

    def get_csrf_token(self):
        """
        请求表单页,获取authenticity_token（csrf token）
        :return: True
        """
        resp = self.s.get(self.login_url)
        if resp.status_code != requests.codes.ok:
            raise Exception(f"请求{self.login_url}失败，状态码{resp.status_code}")
        html_content = resp.text
        pattern = '//input[@name="authenticity_token"]/@value'
        dom = etree.HTML(html_content)
        authenticity_token = dom.xpath(pattern)[0]
        self.authenticity_token = authenticity_token
        return authenticity_token

    def do_login(self, login, password):
        """
        去登录
        :param authenticity_token: csrf token 组装请求参数所需
        :return: True
        """
        authenticity_token = self.get_csrf_token()
        params = {
            'commit': 'Sign in',
            'utf8': '✓',
            'authenticity_token': authenticity_token,
            'login': login,
            'password': password
        }
        resp = self.s.post(self.do_login_url, headers=self.headers, params=params)
        if resp.status_code != 200:     # 登录成功或失败都会重定向
            raise Exception(f"去登录失败{resp.status_code}")
        # 检测得到的页面是登录成功后的首页而不是登录失败重定向后的登陆页
        html_content = resp.text
        dom = etree.HTML(html_content)
        if dom.xpath('//*[text()="Create an account"]'):
            raise Exception(f"登录失败，页面已重定向到登录页")
        self.login = login
        self.password = password
        print("登录成功")
        return None

    def request_profile(self):
        """
        请求个人设置页
        :return: {str} '<html>...</html>'
        """
        # 请求个人页
        try:
            resp = self.s.get(url=self.profile_url, headers=self.headers)
        except Exception as e:
            raise e
        else:
            if resp.status_code != 200:
                raise Exception(f"请求个人设置页失败,状态码{resp.status_code}")
        return resp.text

    def get_user_email(self, html_content):
        """
        获取个人设置页上的邮箱
        :param html_content: 个人设置页html内容
        :return:
        """
        profile_dom = etree.HTML(html_content)
        pattern = '//select[@id="user_profile_email"]/option[2]/text()'
        email = profile_dom.xpath(pattern)[0]
        return email

    def get_user_name(self, html_content):
        pass

    # 作业：追加需求
    # 获取自己的仓库列表
    # 获取个人收藏夹仓库列表

if __name__ == '__main__':
    github = Github()
    github.do_login(login='969501808@qq.com', password='56tyghbn')
    profile_html_content = github.request_profile()
    email = github.get_user_email(profile_html_content)
    print(email)
