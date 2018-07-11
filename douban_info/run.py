#coding:utf-8
import subprocess
import time

from scrapy import cmdline

while True:
    # cmdline.execute('scrapy crawl videowebset'.split())
    subprocess.call('scrapy crawl douban_info --nolog', shell=True)
    print("starting")
    time.sleep(5)
