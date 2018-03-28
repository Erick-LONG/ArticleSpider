import requests

import http.cookiejar as cookielib
import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')

try:
    session.cookies.load(ignore_discard = True)
except:
    print('cookies 未能加载')

agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
header = {
    'HOST':'www.zhihu.com',
    'Referer':'https://www.zhihu.com',
    'User-Agent':agent,
}


def get_xsrf():
    #获取csrf_code
    response = session.get('http://www.zhihu.com',headers = header)
    text = response.text
    match_obj = re.match('.*name="_csrf" value="(.*?)"',text)
    if match_obj:
        return match_obj.group(1)
    else:
        return ''


def get_index():
    response = session.get('http://www.zhihu.com', headers=header)
    with open('index_page.html','wb') as f:
        f.write(response.text.encode('utf-8'))
    print('ok')


def zhihu_login(account,password):
    #知乎登录
    if re.match('^1\d{10}',account):
        print('手机号码登录')
        post_url = ''
        post_data = {
            '_xsrf':get_xsrf(),
            'phone_num':account,
            'password':password,
        }
        response_text = session.post(post_url,post_data,headers=header)
        session.cookies.save()