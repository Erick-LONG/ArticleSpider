# -*- coding: utf-8 -*-
import scrapy
import re


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/112048/']

    def parse(self, response):
        title = response.css('.entry-header h1::text').extract_first('')
        create_date = response.css('p.entry-meta-hide-on-mobile::text').extract()[0].strip().replace('·','').strip()
        praise_nums = response.css('.vote-post-up h10::text').extract()[0]
        fav_nums = response.css('.bookmark-btn::text').extract()[0]
        match_re = re.match('.*?(\d+).*',fav_nums)
        if match_re:
            fav_nums = match_re.group(1)

        comment_nums =  response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re = re.match('.*?(\d+).*', comment_nums)
        if match_re:
            comment_nums = match_re.group(1)

        content = response.css("div.entry").extract()[0]
        taglist = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        taglist = [element for element in taglist if not element.strip().endwith('评论')]
        tags = ','.join(taglist)


        pass
