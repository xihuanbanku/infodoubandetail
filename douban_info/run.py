#coding:utf-8
import subprocess
import time

from scrapy import cmdline

while True:
# if 1:
    # cmdline.execute('scrapy crawl videowebset'.split())
    print("starting")
    subprocess.call('scrapy crawl douban_info --nolog', shell=True)
    time.sleep(30)
