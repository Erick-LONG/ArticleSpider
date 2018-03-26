# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts']

    def parse(self, response):
        '''
        获取文章列表页中的文章URL并交给scrapy下载后并解析
        获取下一页URL并交给scrapy进行下载,下载完成后交给parse
        '''

        #解析列表页中所有文章url
        post_urls = response.css('#archive .floated-thumb .post-thumb a::attr(href)')
        for post_url in post_urls:
            yield Request(url = parse.urljoin(response.url,post_url),callback=self.parse_detail)

        #提取下一页并交给scrapy下载
        next_url = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self,response):
        #提取文章的具体字段
        title = response.css('.entry-header h1::text').extract_first('')
        create_date = response.css('p.entry-meta-hide-on-mobile::text').extract()[0].strip().replace('·','').strip()
        praise_nums = response.css('.vote-post-up h10::text').extract()[0]
        fav_nums = response.css('.bookmark-btn::text').extract()[0]
        match_re = re.match('.*?(\d+).*',fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0

        comment_nums =  response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re = re.match('.*?(\d+).*', comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0

        content = response.css("div.entry").extract()[0]
        taglist = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        taglist = [element for element in taglist if not element.strip().endwith('评论')]
        tags = ','.join(taglist)

