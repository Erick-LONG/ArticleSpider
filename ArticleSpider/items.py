# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime,re
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from ArticleSpider.utils.common import extract_num
from ArticleSpider.settings import SQL_DATE_FORMAT,SQL_DATETIME_FORMAT
from w3lib.html import remove_tags
from ArticleSpider.models.es_types import ArticleType

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match('.*?(\d+).*', value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    #去掉tag中的评论
    if '评论' in value:
        return ''
    else:
        return value


def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    #自定义ITEMloader
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert),
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value),
    )
    front_image_path = scrapy.Field()
    praise_nums =scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    fav_nums =scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    comment_nums =scrapy.Field(
        input_processor=MapCompose(get_nums),
    )
    content =scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor = Join(',')
    )

    def get_insert_sql(self):
        insert_sql = '''
                        insert into jobbole_article(title,url,create_date,fav_nums) VALUES (%s,%s,%s,%s)
                         ON duplicate key UPDATE fav_nums = VALUES (fav_nums)
                    '''
        params = (self['title'], self['url'], self['create_date'], self['fav_nums'])
        return insert_sql,params

    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.create_date = self['create_date']
        article.content = remove_tags(self['content'])
        if 'front_image_path' in self:
            article.front_image_path = self['front_image_path']
        article.front_image_url = self['front_image_url']
        article.praise_nums = self['praise_nums']
        article.fav_nums = self['fav_nums']
        article.comment_nums = self['comment_nums']
        article.url = self['url']
        article.tags = self['tags']
        article.meta.id = self['url_object_id']

        article.save()
        return


class ZhihuQuestionItem(scrapy.Item):
    #知乎的问题item
    zhihu_id=scrapy.Field()
    topics =scrapy.Field()
    url =scrapy.Field()
    title =scrapy.Field()
    content=scrapy.Field()
    answer=scrapy.Field()
    comment_nums =scrapy.Field()
    watch_user_num =scrapy.Field()
    click_num =scrapy.Field()
    crawl_time =scrapy.Field()

    def get_insert_sql(self):
        #插入知乎表
        insert_sql = '''
                        insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,comment_num,
                        watch_user_num,click_num,crawl_time) 
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON duplicate key UPDATE content = VALUES (content),
                        answer_num = VALUES(answer_num),comment_num = VALUES (comment_num)
                        ,watch_user_num = VALUES (watch_user_num),click_num = VALUES (click_num),
                    '''

        zhihu_id = self['zhihu_id'][0]
        topics = ','.join(self['topics'])
        url = self['url'][0]
        title = ''.join(self['title'])
        content = ''.join(self['content'])
        answer_num = extract_num(''.join(self['answer_num']))
        comment_num =extract_num(''.join(self['comment_num']))
        watch_user_num = extract_num(''.join(self['watch_user_num']))
        click_num = extract_num(''.join(self['click_num']))
        crawl_time = datetime.datetime.now().strptime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title,content,answer_num,comment_num,watch_user_num,click_num,crawl_time)
        return insert_sql,params


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id =scrapy.Field()
    author_id=scrapy.Field()
    content=scrapy.Field()
    parise_num=scrapy.Field()
    comment_nums = scrapy.Field()
    create_time =scrapy.Field()
    update_time =scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎表
        insert_sql = '''
                        insert into zhihu_answer(zhihu_id,url,question_id,author_id,content,parise_num,
                        comment_nums,create_time,update_time,crawl_time)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON duplicate key UPDATE content = VALUES (content),
                        comment_nums = VALUES(comment_nums),update_time = VALUES (update_time)
                    '''
        create_time = datetime.datetime.fromtimestamp(self['create_time']).strptime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strptime(SQL_DATETIME_FORMAT)
        params = (self['zhihu_id'],self['url'],self['question_id'],
                  self['author_id'],self['content'],self['parise_num'],
                  self['comment_nums'], create_time, update_time,
                  self['crawl_time'].strptime(SQL_DATETIME_FORMAT)
                  )
        return insert_sql, params

def remove_splash(value):
    #去掉工作城市de 斜杠
    return value.replace('/','')

def handel_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [ item.strip() for item in addr_list if item.strip() != '查看地图']
    return ''.join(addr_list)

class LagouJobItemLoader(ItemLoader):
    #自定义ITEMloader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_obj_id=scrapy.Field()
    salary =scrapy.Field()
    job_city =scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years =scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need =scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type =scrapy.Field()
    publish_time =scrapy.Field()
    job_advantage =scrapy.Field()
    job_desc =scrapy.Field()
    job_addr =scrapy.Field(
        input_processor=MapCompose(remove_tags,handel_jobaddr),
    )
    company_name =scrapy.Field()
    company_url =scrapy.Field()
    tags =scrapy.Field(
        input_processor=Join(',')
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入拉勾表
        insert_sql = '''
                        insert into lagou_job(title,url,question_id,author_id,content,parise_num,
                        comment_nums,create_time,update_time,crawl_time)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON duplicate key UPDATE content = VALUES (content),
                        comment_nums = VALUES(comment_nums),update_time = VALUES (update_time)
                    '''
        params = (self['title'],self['url'],self['question_id'],
                  self['author_id'],self['content'],self['parise_num'],
                  self['comment_nums'],
                  self['crawl_time'].strptime(SQL_DATETIME_FORMAT)
                  )
        return insert_sql, params
