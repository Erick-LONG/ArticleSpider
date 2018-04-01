# -*- coding: utf-8 -*-
import scrapy
import re,json
from urllib import parse
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuAnswerItem,ZhihuQuestionItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

    header = {
        'HOST': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com',
        'User-Agent': agent,
    }

    def parse(self, response):
        '''
        提取出html页面中所有url，并跟踪这些URL进行进一步爬取
        如果提取的URL格式为/question/xx就下载之后直接进入解析函数
        :param response:
        :return:
        '''
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url,url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith('https') else False,all_urls)
        for url in all_urls:
            match_obj = re.match('(.*zhihu.com.question/(/d+).*)(/|$)',url)
            if match_obj:
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url,headers=self.header,callback=self.parse_question)

    def parse_question(self,response):
        #处理question页面,并提出具体的question item
        if 'QuestionHeader-title' in response.text:
            #处理新版本
            match_obj = re.match('(.*zhihu.com.question/(/d+).*)(/|$)', response.url)
            if match_obj:
                question_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(),response=response)
            item_loader.add_css('title','h1.QuestionHeader-title::text')
            item_loader.add_css('content','.QuestionHeader-detail')
            item_loader.add_value('url',response.url)
            item_loader.add_value('zhihu_id',question_id)
            item_loader.add_css('answer_num', '.List-headerText span::text')
            item_loader.add_css('comment_nums', '.QuestionHeader-actions button::text')
            item_loader.add_css('watch_user_num', '.NumberBoard-value::text')
            item_loader.add_css('topics', '.QuestionHeader-topics .Popover::text')
            question_item = item_loader.load_item()
        else:
            #处理旧版本页面item页面提取
            match_obj = re.match('(.*zhihu.com.question/(/d+).*)(/|$)', response.url)
            if match_obj:
                question_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css('title', '.zh-question-title h2::text')
            item_loader.add_css('content', '#zh-question-detail')
            item_loader.add_value('url', response.url)
            item_loader.add_value('zhihu_id', question_id)
            item_loader.add_css('answer_num', '#zh-question-answer-num::text')
            item_loader.add_css('comment_nums', '#zh-question-meta-wrap a[name="addcomment"]::text')
            item_loader.add_css('watch_user_num', '.#zh-question-side-header-wrap::text')
            item_loader.add_css('topics', '.zm-tag-editor-labels a::text')
            question_item = item_loader.load_item()


    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin',headers=self.header,callback=self.login)]

    def login(self,response):
        response_text = response.text
        match_obj = re.match('.*name="_csrf" value="(.*?)"', response_text,re.DOTALL)
        xsrf = ''
        if match_obj:
            xsrf = match_obj.group(1)

        if xsrf:
            post_url = 'https://www.zhihu.com/login/phone_num'
            post_data = {
                '_xsrf':xsrf,
                'phone_num':'',
                'password':'',
            }

            return [scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.header,
                callback=self.check_login,
            )]

    def check_login(self,response):
        #验证服务器的返回数据,判断是否成功
        test_json = json.loads(response.text)
        if 'msg' in test_json and test_json['msg']=='登录成功':
            for url in self.start_urls:
                yield scrapy.Request(url,dont_filter=True,headers=self.header)