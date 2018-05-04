__author__ = 'zzp'
__date__ = '2018/4/26 16:54'

from selenium import webdriver
from scrapy.selector import Selector
import time



# chrome 浏览器与selenium配合,并且设置CHROME不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_opt.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome("D:/workSoft/virtualSite/spider/selenium_plugins/chromedriver.exe", chrome_options=chrome_opt)
browser.get("https://www.weibo.com/")


# 滚动设置
time.sleep(5)
for i in range(4):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
    time.sleep(3)

# time.sleep(10)
# browser.quit()
