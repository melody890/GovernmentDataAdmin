import requests
from bs4 import BeautifulSoup as bs

base_url = "https://s.weibo.com/weibo?q="
username = "govdataproject@163.com"
password = 'hit12345'


class SinaInfo:
    def __init__(self, keyword):
        self.login_url = ""
        self.session = requests.session()
        self.session.headers = {'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'gzip, deflate',
                                'Accept': '*/*', 'Connection': 'keep-alive'}
        self.username = username
        self.password = password
        info_page = self.get_html(base_url+keyword)
        self.parser_info_html(info_page)

    def get_html(self, t_url):
        try:
            t_html = self.session.get(url=t_url)
            t_html.raise_for_status()
            return t_html.text
        except IOError:
            return ''

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
                        # print(info)
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
        print(info_list)
        return info_list


if __name__ == '__main__':
    test = SinaInfo(keyword="@坪山")