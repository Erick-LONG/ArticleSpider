import requests
from scrapy.selector import Selector
import MySQLdb
conn = MySQLdb.connect(host='127.0.0.1',user = 'root',passwd='root',db = 'article_spider',charset = 'utf8')
cursor = conn.cursor()


def crawl_ips():
    #爬取西刺代理ip
    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

    header = {
        'User-Agent': agent,
    }
    for i in range(1568):
        re = requests.get('http://www.xicidaili.com/nn/{0}'.format(i),headers=header)
        selector = Selector(text=re.text)
        all_trs = selector.css('#ip_list tr')
        ip_list =[]
        for tr in all_trs[1:]:
            speed_str = tr.css('.bar::attr(title)').extract()[0]
            if speed_str:
                speed = float(speed_str.split('秒')[0])
            all_text = tr.css('td::text').extract()
            ip = all_text[0]
            port = all_text[1]
            proxy_type = all_text[5]
            ip_list.append((ip,port,proxy_type,speed))

        for ip_info in ip_list:
            cursor.execute(
                "insert proxy_ip(ip,port,speed,proxy_type) values('{}','{}','{}','HTTP')".format(
                    ip_info[0],ip_info[1],ip_info[3]
                )
            )
            conn.commit()


class GetIp():

    def judge_ip(self,ip,port):
        #判断IP是否可用
        http_url = 'http://www.baidu.com'

    def get_romdom_ip(self):
        #从数据库随机获取可用ip
        random_sql = '''select ip,port from proxy_ip ORDER BY rand() limit 1 '''
        result = cursor.execute(
            random_sql
        )
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
crawl_ips()