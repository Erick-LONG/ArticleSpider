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


def is_login():
    #通过个人中心状态码判断页面是否为登录状态
    inbox_url = 'http://www.zhihu.com/inbox'
    response = session.get(inbox_url,headers = header,allow_redirects=False)
    if response.status_code != 200:
        return False
    else:
        return True


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

def get_captcha():
    import time
    t= str(int(time.time()*1000))
    captcha_url = "https://www.zhihu.com/api/v3/oauth/captcha?lang=cn"
    t = session.get(captcha_url,headers=header)
    with open('captcha.jpg','wb') as f:
        f.write(t.content)
        f.close()
    from PIL import Image
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except :
        pass
    captcha = input('输入验证码：')
    return captcha

def zhihu_login(account,password):
    #知乎登录
    if re.match('^1\d{10}',account):
        print('手机号码登录')
        post_url = 'http://www.zhihu.com/login/phone_num'

        post_data = {
            '_xsrf':get_xsrf(),
            'phone_num':account,
            'password':password,
            'captcha':get_captcha()
        }
    else:
        if "@" in account:
            print('邮箱方式登录')
            post_url = 'http://www.zhihu.com/login/email'
            post_data = {
                '_xsrf': get_xsrf(),
                'email': account,
                'password': password,
            }
    response_text = session.post(post_url, post_data, headers=header)
    session.cookies.save()