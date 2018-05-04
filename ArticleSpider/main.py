__author__ = 'zzp'
__date__ = '2018/4/13 9:30'

from scrapy.cmdline import execute
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "jobbole"])
# execute(["scrapy", "crawl", "lagou"])