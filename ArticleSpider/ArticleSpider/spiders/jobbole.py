# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from items import JobBoleArticleItem, ArticleItemLoader
from utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        # 解析当前页的文章url
        for post_node in post_nodes:
            img_url = parse.urljoin(response.url, post_node.css("img::attr(src)").extract_first(""))
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_img_url': img_url}, callback=self.parse_detail)

        # 解析下一页的数据
        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url = parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        # title = response.xpath("//div[@class='entry-header']/h1/text()").extract()[0]
        # create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace("·", "").strip()
        # parse_nums = response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0]
        #
        # fav_re = re.match(".*(\d)+.*", response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0])
        # fav_nums = fav_re.group(1) if fav_re else 0
        #
        # comment_re = re.match(".*(\d)+.*", response.xpath("//a[@href='#article-comment']/span/text()").extract()[0])
        # comment_nums = comment_re.group(1) if comment_re else 0
        # content = response.xpath("//div[@class='entry']").extract()[0]

        # article_item = JobBoleArticleItem()
        # # 通过css 提取字段
        # front_image_url = response.meta.get("front_img_url", "")
        # title = response.css(".entry-header h1::text").extract()[0]
        #
        # create_date = response.css(".entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()
        #
        # praise_nums = response.css(".vote-post-up h10::text").extract()[0]
        #
        # fav_re = re.match(".*?(\d)+.*", response.css(".bookmark-btn::text").extract()[0])
        # fav_nums = int(fav_re.group(1)) if fav_re else 0
        #
        # comment_re = re.match(".*?(\d)+.*", response.css("a[href='#article-comment'] span::text").extract()[0])
        # comment_nums = int(comment_re.group(1)) if comment_re else 0
        #
        # content = response.css("div.entry").extract()[0]
        #
        # tags = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # tag_list = [element for element in tags if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["title"] = title
        # article_item["url"] = response.url
        # try:
        #     create_date = datetime.datetime.strptime(create_date, "%Y%m%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        #
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["comments_nums"] = comment_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] = tags
        # article_item["content"] = content
        # yield article_item
        # pass

        # 通过itemloader加载
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_css("create_date", ".entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [response.meta.get("front_img_url", "")])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comments_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()
        yield article_item