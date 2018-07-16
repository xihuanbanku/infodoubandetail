#coding:utf-8
import random
import subprocess
import time

from scrapy import cmdline

while True:
# if 1:
#     cmdline.execute('scrapy crawl douban_info'.split())
    print("starting...")
    subprocess.call('scrapy crawl douban_info --nolog', shell=True)
    print("休眠")
    time.sleep(random.randrange(10, 30))

