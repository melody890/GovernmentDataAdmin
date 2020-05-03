import requests
import re
import urllib
import base64
import binascii
import rsa
from bs4 import BeautifulSoup as bs

base_url = "https://s.weibo.com/weibo"
pre_login_url = "https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack" \
                "&su=&rsakt=mod&client=ssologin.js(v1.4.19)&_=1588379999791"
username = "govdataproject@163.com"
password = 'hit12345'


class SinaInfo:
    def __init__(self, keyword):
        self.login_url = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)"
        self.session = requests.session()
        self.session.headers = {'User-Agent': 'Mozilla/5.0',
                                'Accept-Encoding': 'gzip, deflate',
                                'Accept': '*/*',
                                'Connection': 'keep-alive',
                                }
        self.username = username
        self.password = password
        self.cookies = self.log_in()
        self.get_info(keyword)

    def get_info(self, keyword, start_time=None, end_time=None, number=50):
        base_info_url = base_url + '?q=' + keyword + '&typeall=1' + '&suball=1'
        if start_time or end_time:
            base_info_url += 'timescope=custom:' + str(start_time) + ':' + str(end_time)
        base_info_url += '&page='
        info_list = []
        page = 1
        while len(info_list) < number:
            info_html = self.get_html(base_info_url+str(page))
            info_list.append(self.parser_info_html(info_html))
            page += 1
        info_list = info_list[:199]
        print(info_list)
        return info_list

    def get_html(self, t_url):
        try:
            t_html = self.session.get(url=t_url)
            t_html.raise_for_status()
            return t_html.text
        except IOError:
            print("搜索太过频繁，请稍后再试")
            exit()

    def parser_login_html(self):
        soup = bs(self.get_html(self.login_url), 'html.parser')
        return soup

    # 解析信息页面
    @staticmethod
    def parser_info_html(html):
        soup = bs(html, 'html.parser')
        divs = soup.find_all('div')
        info_list = []
        for div in divs:
            if ['card'] in div.attrs.values():
                info = {}
                for a in div.find_all('a'):
                    if ['name'] in a.attrs.values():
                        info.update({
                            'nickname': a.attrs['nick-name'],
                            'user_link': 'https:' + a.attrs['href']
                        })
                    if 'suda-data' in a.attrs.keys() and a.attrs['suda-data'][-7:] == 'wb_time':
                        info.update({
                            'post_time': a.string.strip(),
                            'info_link': 'https:' + a.attrs['href']
                        })
                for p in div.find_all('p'):
                    if 'node-type' in p.attrs.keys() and p.attrs['node-type'] == 'feed_list_content':
                        content = ""
                        for con in p.contents:
                            if str(type(con)) == "<class 'bs4.element.NavigableString'>":
                                content += str(con).strip()
                        info.update({
                            'content': content
                        })
                info_list.append(info)
        return info_list

    def pre_login(self):
        data = self.session.get(pre_login_url).content.decode('utf-8')
        p = re.compile('\((.*)\)')
        data_str = p.search(data).group(1)
        server_data_dict = eval(data_str)
        pubkey = server_data_dict['pubkey']
        server_time = server_data_dict['servertime']
        nonce = server_data_dict['nonce']
        rsakv = server_data_dict['rsakv']
        return pubkey, server_time, nonce, rsakv

    def rsa_encoder(self):
        pubkey, server_time, nonce, rsakv = self.pre_login()
        su_url = urllib.parse.quote_plus(username)
        su_encoded = su_url.encode('utf-8')
        su = base64.b64encode(su_encoded)
        su = su.decode('utf-8')
        rsa_pubkey = int(pubkey, 16)
        e = int('10001', 16)
        key = rsa.PublicKey(rsa_pubkey, e)
        message = str(server_time) + '\t' + str(nonce) + '\n' + str(self.password)
        en_password = rsa.encrypt(message.encode('utf-8'), key)
        sp = binascii.b2a_hex(en_password)
        return su, sp, nonce, rsakv, server_time

    def post_data(self):
        su, sp, nonce, rsakv, server_time = self.rsa_encoder()
        post_data = {
            'encoding': 'UTF-8',
            'entry': 'weibo',
            'from': '',
            'gateway': '1',
            'nonce': nonce,
            'pagerefer': '',
            'prelt': '645',
            'pwencode': 'rsa2',
            'returntype': 'META',
            'rsakv': rsakv,
            'savestate': '7',
            'servertime': str(server_time),
            'service': 'miniblog',
            'sp': sp,
            'sr': '1920*1080',
            'su': su,
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            # noqa
            'useticket': '1',
            'vsnf': '1',
        }
        return post_data

    def log_in(self):
        post_data = self.post_data()
        response = self.session.post(self.login_url, params=post_data)
        text = response.content.decode('gbk')
        pa = re.compile(r"location\.replace\(\"(.*?)\"\)")
        redirect_url = pa.search(text).group(1)
        response = self.session.get(redirect_url)
        return self.session.cookies


if __name__ == '__main__':
    test = SinaInfo(keyword="@坪山")
