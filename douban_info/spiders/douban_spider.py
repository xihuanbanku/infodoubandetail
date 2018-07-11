#!/usr/bin/env python
# coding=utf-8
import re
import time

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
        cookies = 'gr_user_id=b0d9a237-aa82-4b1f-9def-c87653259ea4; ll="108288"; viewed="5337254_26993157_10590856_25779298"; bid=MbIatP8Uy9k; __yadk_uid=pzXMbRXdx2O9a6H11yW0Ov8dwQY35iF7; ps=y; dbcl2="174643900:UD/7+sfcADQ"; ct=y; ck=f-sV; ap=1; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1520404252%2C%22https%3A%2F%2Fwww.douban_info.com%2F%22%5D; as="https://sec.douban_info.com/b?r=https%3A%2F%2Fmovie.douban_info.com%2F"; _pk_id.100001.4cf6=84f120e21ffdaba9.1519269036.32.1520405069.1520397782.; _pk_ses.100001.4cf6=*; __utma=30149280.1789096787.1478770268.1520397757.1520404253.59; __utmb=30149280.0.10.1520404253; __utmc=30149280; __utmz=30149280.1520404253.59.31.utmcsr=douban_info.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=223695111.1772094035.1519269036.1520397782.1520404253.32; __utmb=223695111.0.10.1520404253; __utmc=223695111; __utmz=223695111.1520404253.32.12.utmcsr=douban_info.com|utmccn=(referral)|utmcmd=referral|utmcct=/; push_noty_num=0; push_doumail_num=0; _vwo_uuid_v2=39E6F0B28328A4287CEDDE656A81EE0D|651218b2e691a30aa8f71f79fc9e9382'
        for line in cookies.split(';'):
            key,value = line.strip().split('=', 1) #1代表只分一次，得到两个数据
            self.cookie[key] = value.replace('"','')
        self.db = psycopg2.connect(database=DATABASE['database'], user=DATABASE['user'], password=DATABASE['password'], host=DATABASE['ip'], port=DATABASE['port'])
        self.cur = self.db.cursor()
    #读取库里URL任务并更新状态
    def get_movie_links(self):
        links_sql = 'select url from public.tb_movie_url_task where flag=0 limit 50'
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
            movie_item['uid'] = re.sub("\D", "",movie_link)
            page_html = requests.get(url =movie_link,cookies = self.cookie).content
            parser = MovieParser(page_html)
            for field in movie_item.fields.keys(): #遍历item中的字段获取到对应字段的值
                if hasattr(parser,field):
                    movie_item[field] = getattr(parser,field)
            movie_item = parser.get_source_link(movie_item) #返回了更新后的 movie_item
            yield movie_item

    def __del__(self):
        self.db.close()
        self.loggerWithTime ("===========cursor close==========")

    #打印当前时间的消息
    def loggerWithTime(self, message):
        now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        print("[%s][%s]"%(now, message))
