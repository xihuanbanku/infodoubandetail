#!/usr/bin/env python
# coding=utf-8
import re
import time
from random import random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import psycopg2
import requests
import scrapy

from MovieParser import MovieParser
from douban_info.items import DoubanItem
from douban_info.settings import DATABASE


class MovieGatherSpider(scrapy.Spider):
    name = 'douban_info'
    start_urls = ['https://www.baidu.com/']

    def __init__(self):
        self.cookie={}
        cookies = 'dbcl2="104718627:tIX/MLodljJ"'
        for line in cookies.split(';'):
            key,value = line.strip().split('=', 1) #1代表只分一次，得到两个数据
            self.cookie[key] = value.replace('"','')
        self.db = psycopg2.connect(database=DATABASE['database'], user=DATABASE['user'], password=DATABASE['password'], host=DATABASE['ip'], port=DATABASE['port'])
        self.cur = self.db.cursor()
    #读取库里URL任务并更新状态
    def get_movie_links(self):
        links_sql = "select url from public.tb_movie_url_task where flag=0 limit 10"
        self.loggerWithTime(links_sql)
        self.cur.execute(links_sql)
        links = self.cur.fetchall()
        return links

    #详情URL解析
    def parse(self, response):
        self.loggerWithTime("detail_parse")
        movie_item = DoubanItem()
        movie_links = self.get_movie_links()
        for movie_link, in movie_links:
            movie_item['url'] = movie_link
            movie_item['uid'] = re.sub("\D", "", movie_link)
            page_html = requests.get(url =movie_link,cookies = self.cookie).content
            if page_html.find("页面不存在") >=0:
                self.loggerWithTime("[%s]页面不存在" % movie_item['uid'])
                links_sql = "update public.tb_movie_url_task set flag=404 where url ='%s'" % movie_item['url']
                self.cur.execute(links_sql)
                self.db.commit()
                break
            if page_html.find("条目不存在") >=0:
                self.loggerWithTime("[%s]条目不存在" % movie_item['uid'])
                links_sql = "update public.tb_movie_url_task set flag=403 where url ='%s'" % movie_item['url']
                self.cur.execute(links_sql)
                self.db.commit()
                break
            if page_html.find("检测到有异常请求") >=0:
                self.loggerWithTime(page_html)
                self.loggerWithTime("开始休眠")
                time.sleep(random.randrange(10, 180))
                break
            parser = MovieParser(page_html)
            for field in movie_item.fields.keys(): #遍历item中的字段获取到对应字段的值
                if hasattr(parser, field):
                    movie_item[field] = getattr(parser,field)
            movie_item = parser.get_source_link(movie_item) #返回了更新后的 movie_item
            yield movie_item

    def __del__(self):
        self.db.close()
        self.loggerWithTime ("===========cursor close==========")

    #打印当前时间的消息
    def loggerWithTime(self, message):
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print("[%s][%s]" % (now, message))
