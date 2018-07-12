# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import traceback

import psycopg2

from douban_info.items import DoubanItem
from douban_info.settings import DATABASE


class DoubanPipeline(object):
    def __init__(self):
        try:
            self.db = psycopg2.connect(database=DATABASE['database'], user=DATABASE['user'], password=DATABASE['password'], host=DATABASE['ip'], port=DATABASE['port'])
            self.cursor = self.db.cursor()
            self.loggerWithTime(u"==> connect db sucessfully<==")
        except Exception as e:
            self.loggerWithTime(u"==> fail to connect db!!!<==")

    def gen_sql(self, item):
        keys = item.fields.keys()
        

    def process_item(self, item, spider):
        # self.cursor.execute("Select * FROM public.movie_data limit 0")
        # colnames = [desc[0] for desc in self.cursor.description]
        # for i in colnames:
        #     self.loggerWithTime( i
        self.loggerWithTime("in pipeline.........")
        try:
            if isinstance(item, DoubanItem):
                # self.loggerWithTime( json.dumps(dict(item),ensure_ascii=False, indent=4)
                check_sql = "select media_uid from public.tb_media_meta_data2 where media_uid='%s'"
                self.cursor.execute(check_sql%item['uid'])
                result = self.cursor.fetchall()
                if result:
                    self.cursor.execute("UPDATE public.tb_movie_url_task set flag=1, atime=now() WHERE url='{}'".format(item['url'].decode('utf-8')))
                    self.db.commit()
                    self.loggerWithTime('[%s]Movie Data Exist'%item['uid'])
                else:
                    self.cursor.execute("""insert into public.tb_media_meta_data2(\
                     media_uid,
                     media_url,
                     media_type1,
                     media_title,
                     media_director,
                     media_screenwriter,
                     media_starring,
                     media_type2,
                     media_language,
                     media_premiere,
                     media_region,
                     media_length,
                     media_alias, 
                     media_score,
                     media_episodes,
                     media_summary
                     ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                        (item['uid'],
                                         item['url'],
                                         item['movie_type'],
                                         item['title'],
                                         item['directors'],
                                         item['scriptwriters'],
                                         item['actors'],
                                         item['types'],
                                         item['languages'],
                                         item['release_date'],
                                         item['release_region'],
                                         item['duration'],
                                         item['alias'],
                                         item['score'] or 0,
                                         item['media_episoders'],
                                         item['description']))
                    # ["youku_url":14, "iqiyi_url":8, "souhu_url":16, "mgtv_url":5, "tencent_url":13, "pptv_url":6, "letv_url":9, "huashu_url":32, "cntv_url":10];
                    if item['youku_url']:
                        self.inserIntoDB(item['uid'], item['youku_url'], 14)
                    if item['tencent_url']:
                        self.inserIntoDB(item['uid'], item['tencent_url'], 13)
                    if item['iqiyi_url']:
                        self.inserIntoDB(item['uid'], item['iqiyi_url'], 8)
                    if item['letv_url']:
                        self.inserIntoDB(item['uid'], item['letv_url'], 9)
                    if item['huashu_url']:
                        self.inserIntoDB(item['uid'], item['huashu_url'], 32)
                    if item['souhu_url']:
                        self.inserIntoDB(item['uid'], item['souhu_url'], 16)
                    if item['cntv_url']:
                        self.inserIntoDB(item['uid'], item['cntv_url'], 10)
                    if item['pptv_url']:
                        self.inserIntoDB(item['uid'], item['pptv_url'], 16)
                    if item['mgtv_url']:
                        self.inserIntoDB(item['uid'], item['mgtv_url'], 5)
                    self.loggerWithTime("==>[%s] success to insert into tb_media_meta_data2!" %(item['uid']))
                    self.cursor.execute("UPDATE public.tb_movie_url_task set flag=1, atime=now() WHERE url='{}'".format(item['url'].decode('utf-8')))
                    self.db.commit()
                    self.loggerWithTime("==>[%s] success to update tb_movie_url_task!" %(item['uid']))
        except Exception as e:
            self.cursor.execute("UPDATE public.tb_movie_url_task set flag=2, atime=now() WHERE url='{}'".format(item['url'].decode('utf-8')))
            self.loggerWithTime("[%s]DoubanPipeline ERROR update tb_movie_url_task flag=2[%s]" %(item['uid'], e.message))
            self.db.commit()
            traceback.print_exc()

    def _del__(self):
        self.db.close()
        self.loggerWithTime("==>database closed sucess<==")

    def inserIntoDB(self, uid, links, app_id):
        i = 0
        for url_link in links:
            i += 1
            self.cursor.execute("""INSERT INTO "public"."tb_media_meta_url_map" 
                          ("media_uid", "url", "episode", "app_id") 
                          VALUES (%s, %s, %s, %s) on conflict (url) do update set c_count=tb_media_meta_url_map.c_count+1""", \
                                (uid, url_link, i, app_id))
        self.loggerWithTime("[%s]可播放连接入库tb_media_meta_url_map[%s]共[%s]集"%(uid,app_id,i))

    # 打印当前时间的消息
    def loggerWithTime(self, message):
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print("[%s][%s]" % (now, message))