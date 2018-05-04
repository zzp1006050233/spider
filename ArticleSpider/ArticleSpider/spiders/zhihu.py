# -*- coding: utf-8 -*-
__author__ = 'Mark'
__date__ = '2018/4/15 10:18'

import hmac
import json
import scrapy
import time
import base64
import re
import datetime
from hashlib import sha1
from urllib import parse
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem
from scrapy.loader import ItemLoader


class ZhihuLoginSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"
    agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    headers = {
        'Connection': 'keep-alive',
        'Host': 'www.zhihu.com',
        'Referer': 'https://www.zhihu.com/signup?next=%2F',
        'User-Agent': agent,
        'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'
    }
    grant_type = 'password'
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    source = 'com.zhihu.web'
    timestamp = str(int(time.time() * 1000))
    timestamp2 = str(time.time() * 1000)

    def get_signature(self, grant_type, client_id, source, timestamp):
        """处理签名"""
        hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
        hm.update(str.encode(grant_type))
        hm.update(str.encode(client_id))
        hm.update(str.encode(source))
        hm.update(str.encode(timestamp))
        return str(hm.hexdigest())

    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        for url in all_urls:
            match_obj = re.match("(.*/question/(\d+)(/|$)).*", url)
            if match_obj:
                question_url = match_obj.group(1)
                question_id = int(match_obj.group(2))
                yield scrapy.Request(question_url, headers=self.headers, meta={'question_id': question_id}, callback=self.parse_question)
            else:
                pass
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        question_id = response.meta.get("question_id", 0)
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", "h1.QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_css("comments_num", ".QuestionHeader-actions button::text")
        item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

        question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        answer_json = json.loads(response.text)
        is_end = answer_json['paging']['is_end']
        next_page = answer_json['paging']['next']
    #   提取回答信息
        for answer in answer_json['data']:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            yield answer_item

        if not is_end:
            yield scrapy.Request(next_page, headers=self.headers, callback=self.parse_answer)

    def start_requests(self):
        # 注释掉模拟登陆
         yield scrapy.Request('https://www.zhihu.com/api/v3/oauth/captcha?lang=en', headers=self.headers, callback=self.is_need_capture)
        # 使用cookie登陆
        # yield scrapy.Request('https://www.zhihu.com/', cookies="q_c1=cb576ec3b4c3452ea11bc50c3d23f060|1505967809000|1505967809000; _zap=a0e4a983-da6c-4284-af7a-0c66dd240431; d_c0='AIACpqCybQyPTnXv9DFA-MNgcG2SPZNHe5I=|1506300122'; _ga=GA1.2.11514142.1510107344; __DAYU_PP=eajifzYnezZEJyIbIf2f65b9baa7a14d; q_c1=cb576ec3b4c3452ea11bc50c3d23f060|1522368941000|1505967809000; __utmv=51854390.100-1|2=registration_date=20140806=1^3=entry_date=20140806=1; aliyungf_tc=AQAAAFE31EYuUg4AhiWHPbmGrgpU1tG/; _xsrf=7d682a5f-401b-45d3-a5ad-a7efa2d86191; __utmc=51854390; l_n_c=1; oauth_from='/'; o_act=login; r_cap_id='OTI4MDViYmQ4MWM4NDFmZjllYzBhMDEwNjRkZTA4ZTM=|1524101830|7035e3cedd960f5831dcf56158e9643a57b296d8'; cap_id='MTAzODIxMTA0ODcwNDdlNGI2ZTFiNTk2MzFmZjFjMTQ=|1524101830|c07fe876e59ab363a829b3359b92aae7ecac8656'; l_cap_id='OTllOGZkN2JmYTM4NDc1MDk4MzlkNmUxZGY0NGM0ZjU=|1524101830|a86059871497f81ab2306e85f2636ea4c2ec08a8'; n_c=1; __utmz=51854390.1524193339.14.13.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/people/you-xia-feng-fan/activities; z_c0='2|1:0|10:1524212790|4:z_c0|92:Mi4xS2U5d0FBQUFBQUFBZ0FLbW9MSnREQ1lBQUFCZ0FsVk5OdkxHV3dEdm9wV0QyV2hSZXQxVWswR2tTMVVtYWE2dC13|2115f7108b594afb455c67937938e371e4a3272d4925ba52cf636ed22c19eb84'; __utma=51854390.11514142.1510107344.1524453820.1524453903.16; capsion_ticket='2|1:0|10:1524463085|14:capsion_ticket|44:NDZlOGQ1MzgzMDMyNGViNWE2NjJhYjZkY2I2MjM0OWM=|030ef9927ddbea9825fe3eee04664caeb35cd5210b27b7cb80ba935e595965d7")

    def is_need_capture(self, response):
        print(response.text)
        need_cap = json.loads(response.body)['show_captcha']
        print(need_cap)

        if need_cap:
            print('需要验证码')
            yield scrapy.Request(
                url='https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
                headers=self.headers,
                callback=self.capture,
                method='PUT'
            )
        else:
            print('不需要验证码')
            post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
            post_data = {
                "client_id": self.client_id,
                "username": "707520322@qq.com",  # 输入知乎用户名
                "password": "worinima1992",  # 输入知乎密码
                "grant_type": self.grant_type,
                "source": self.source,
                "timestamp": self.timestamp,
                "signature": self.get_signature(self.grant_type, self.client_id, self.source, self.timestamp),  # 获取签名
                "lang": "en",
                "ref_source": "homepage",
                "captcha": '',
                "utm_source": "baidu"
            }
            yield scrapy.FormRequest(
                url=post_url,
                formdata=post_data,
                headers=self.headers,
                callback=self.check_login
            )
        # yield scrapy.Request('https://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time() * 1000),
        #                      headers=self.headers, callback=self.capture, meta={"resp": response})
        # yield scrapy.Request('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
        #                      headers=self.headers, callback=self.capture, meta={"resp": response},dont_filter=True)

    def capture(self, response):
        # print(response.body)
        try:
            img = json.loads(response.body)['img_base64']
        except ValueError:
            print('获取img_base64的值失败！')
        else:
            img = img.encode('utf8')
            img_data = base64.b64decode(img)
            # print(img_data)
            with open('zhihu.gif', 'wb') as f:
                f.write(img_data)
                f.close()
        captcha = input('请输入验证码：')
        post_data = {
            'input_text': captcha
        }
        print(captcha)
        yield scrapy.FormRequest(
            url='https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
            formdata=post_data,
            callback=self.captcha_login,
            headers=self.headers
        )

    def captcha_login(self, response):
        try:
            cap_result = json.loads(response.body)['success']
            print(cap_result)
        except ValueError:
            print('关于验证码的POST请求响应失败!')
        else:
            if cap_result:
                print('验证成功!')
        post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        post_data = {
            "client_id": self.client_id,
            "username": "707520322@qq.com",  # 输入知乎用户名
            "password": "worinima1992!",  # 输入知乎密码
            "grant_type": self.grant_type,
            "source": self.source,
            "timestamp": self.timestamp,
            "signature": self.get_signature(self.grant_type, self.client_id, self.source, self.timestamp),  # 获取签名
            "lang": "en",
            "ref_source": "homepage",
            "captcha": '',
            "utm_source": ""
        }
        headers = self.headers
        headers.update({
            'Origin': 'https://www.zhihu.com',
            'Pragma': 'no - cache',
            'Cache-Control': 'no - cache'
        })
        yield scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=headers,
            callback=self.check_login
        )

    def check_login(self, response):
        # 验证是否登录成功
        text_json = json.loads(response.text)
        print(text_json)
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, headers=self.headers)
