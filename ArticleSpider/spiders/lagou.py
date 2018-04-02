# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import LagouJobItemLoader,LagouJobItem


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_job', follow=True),
    )

    def parse_job(self, response):
        #解析拉勾网职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(),response=response)
        item_loader.add_css('title','.job-name::attr(title)')
        item_loader.add_css('url', '')
        item_loader.add_value('url_obj_id', '')
        item_loader.add_css('salary', '')
        item_loader.add_css('job_city', '')
        item_loader.add_css('work_years', '')
        item_loader.add_css('degree_need', '')
        item_loader.add_css('job_type', '')
        item_loader.add_css('publish_time', '')
        item_loader.add_css('job_advantage', '')
        item_loader.add_css('job_desc', '.job_bt div')
        item_loader.add_css('job_addr', '.work_addr')
        item_loader.add_css('company_name', '')
        item_loader.add_css('company_url', '')
        item_loader.add_css('tags', '')
        item_loader.add_value('crawl_time', datetime.now())
        job_item = item_loader.load_item()
        return job_item

