from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text,Integer
from elasticsearch_dsl.connections import connections

connections.create_connection(host=['localhost'])

class ArticleType(DocType):
    #伯乐在线文章类型
    title = Text(analyzer = 'ik_max_word')
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    praise_nums = Integer()
    fav_nums =Integer()
    comment_nums =Integer()
    content =Text(analyzer = 'ik_max_word')
    tags = Text(analyzer = 'ik_max_word')

    class Meta:
        index = 'jobbole'
        doc_type = 'article'


if __name__ == '__main__':
    ArticleType.init()
