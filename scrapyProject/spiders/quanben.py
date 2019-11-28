# -*- coding: utf-8 -*-
import scrapy
import re
import json
from scrapyProject.config import BASER_URL, DETAIL_CONTENT_URL, OVER_WRITE_FLAG
from scrapyProject.items import QuanBenItem
from scrapyProject.io_redis import ioRedis


class QuanbenSpider(scrapy.Spider):
    name = 'quanben'
    allowed_domains = ['quanben.io']
    start_urls = ['http://quanben.io/']

    def start_requests(self):
        urls = [
            'http://quanben.io/c/xuanhuan.html',  # 玄幻分类
            'http://quanben.io/c/dushi.html',  # 都市分类
            'http://quanben.io/c/yanqing.html',  # 言情分类
            'http://quanben.io/c/chuanyue.html',  # 穿越分类
            'http://quanben.io/c/qingchun.html',  # 青春分类
            'http://quanben.io/c/xianxia.html',  # 仙侠分类
            'http://quanben.io/c/lingyi.html',  # 灵异分类
            'http://quanben.io/c/xuanyi.html',  # 悬疑分类
            'http://quanben.io/c/lishi.html',  # 历史分类
            'http://quanben.io/c/junshi.html',  # 军事分类
            'http://quanben.io/c/youxi.html',  # 游戏分类
            'http://quanben.io/c/jingji.html',  # 竞技分类
            'http://quanben.io/c/kehuan.html',  # 科幻分类
            'http://quanben.io/c/zhichang.html',  # 职场分类
            'http://quanben.io/c/guanchang.html',  # 官场分类
            'http://quanben.io/c/xianyan.html',  # 现言分类
            'http://quanben.io/c/danmei.html',  # 耽美分类
            'http://quanben.io/c/qita.html'  # 其他分类
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_type)

    def parse_type(self, response):
        """
        爬取每个类别的数据，有下一页和每一本小说
        :param response:
        :return:
        """
        # 翻页的请求
        next_url = response.xpath('//p[@class="page_next"]/a/@href').extract_first()
        if next_url:
            yield scrapy.Request(url=BASER_URL + next_url, callback=self.parse_type)

        # 每一本小说的页面
        book_list = response.xpath('//div[@class="row"]//h3/a/@href')
        for book in book_list:
            book_url = book.extract()
            yield scrapy.Request(url=BASER_URL + book_url, callback=self.parse_book)

        # 爬取一个本书
        # book_url = book_list[0].extract()
        # yield scrapy.Request(url=BASER_URL + book_url, callback=self.parse_book)

    def parse_book(self, response):
        """爬取每本书的url"""
        book_chapter_list_url = response.xpath(
            '//div/div["@class=tool_button"]/a["@class=button"]/@href').extract_first()
        book_author = response.xpath(
            '//div[@class="box"]//span[@itemprop="author"]/text()').extract_first()
        # print(book_chapter_list_url)

        if book_chapter_list_url:
            yield scrapy.Request(url=BASER_URL + book_chapter_list_url, meta={"book_author": book_author},
                                 callback=self.parse_book_list)

    def parse_book_list(self, response):
        chapter_list_url = response.xpath("//li/a/@href")

        book_title = response.xpath("//h3/span/text()").extract_first()

        for chapter in chapter_list_url:
            chapter_url = chapter.extract()
            url = BASER_URL + chapter_url
            yield scrapy.Request(url=url, meta={"book_title": book_title, "request_url": url,
                                                "book_author": response.meta.get("book_author")},
                                 callback=self.parse_book_content)
            # for chapter in chapter_list_url:
            # chapter_url = chapter_list_url[0].extract()
            # url = BASER_URL + chapter_url
            # # 将作者传递下去
            # yield scrapy.Request(url=url, meta={"book_title": book_title, "request_url": url,
            #                                     "book_author": response.meta.get("book_author")},
            #                      callback=self.parse_book_content)

    def parse_book_content(self, response):
        """爬取每一章的数据"""
        # print('*' * 10)
        meta = response.meta
        text = response.text
        # print(text)
        # 通过正则表达式获取callback的值

        try:
            # 开始获取参数callback，pinyin,chapter_id
            rule = r'read.jsonp&callback=(.*?)&pinyin'
            p1 = re.compile(rule, re.S)  # 最小匹配
            cb = re.findall(p1, text)[0]
            rule = r"load_more\('(.*?)'"
            p1 = re.compile(rule, re.S)  # 最小匹配
            res_args = response.xpath('//div[@class="more"]/a/@onclick').extract_first()
            rule = r"load_more\('(.*?)'"
            p1 = re.compile(rule, re.S)  # 最小匹配
            pinyin = re.findall(p1, res_args)[0]
            rule = r",'(.*?)'"
            p1 = re.compile(rule, re.S)  # 最小匹配
            chapter_id = re.findall(p1, res_args)[0]
        except Exception as e:
            print(e)
            print("链接出错了没法获取请自己查看", meta['request_url'])
            return
        # 章节列表
        chapter_title = response.xpath("//div/h1/text()").extract_first()
        if not chapter_title:
            print('该章节可能没有了请自行查看', meta['request_url'])
            return

        content_detail_url = DETAIL_CONTENT_URL + '?c=book&a=read.jsonp&callback=%s&pinyin=%s&id=%s' % (
            cb, pinyin, chapter_id)
        print(content_detail_url)
        lis = response.xpath("//div/div[@id='content']/p")
        tmp = ''
        for i in range(len(lis)):
            tmp += '<p>%s</p>' % lis[i].xpath('./text()').extract_first()
        # 上半部分的content
        meta['chapter_content'] = tmp
        meta['chapter_id'] = chapter_id
        meta['chapter_title'] = chapter_title

        yield scrapy.Request(url=content_detail_url, meta=meta,
                             callback=self.parse_book_content_detail)

    def parse_book_content_detail(self, response):
        text = response.text
        # p1 = re.compile(r'[(](.*?)[)]', re.S)  # 最小匹配
        # # 获取返回字符串里面的数据
        # data = re.findall(p1, text)
        # 因为json.loads老是报错莫名奇妙然后换成re提取
        p2 = re.compile(r'[:]["](.*?)["][}]', re.S)  # 最小匹配
        d = re.findall(p2, text)
        content_detal = d[0].replace(r"\/", "/")
        meta = response.meta
        meta["chapter_content"] = meta["chapter_content"] +content_detal

        quanben_item = QuanBenItem()
        quanben_item['chapter_title'] = meta['chapter_title']
        quanben_item['chapter_id'] = meta['chapter_id']
        quanben_item['chapter_content'] = meta['chapter_content']
        quanben_item['book_title'] = meta['book_title']
        quanben_item['book_author'] = meta['book_author']
        if quanben_item['chapter_id'] and quanben_item['chapter_content'] and quanben_item['book_title']:
            key = 'book-%s-%s' % (quanben_item['book_title'], quanben_item['chapter_id'])
            self.save_data(key, quanben_item)

    @staticmethod
    def save_data(key, data):
        """
        数据存储
        :param data: 字典数据
        :param title: 小说标题
        :param key: 大键值 默认给个book
        :return:
        """
        io_redis = ioRedis()
        redis_result = io_redis.hgetall(key)
        print(data['book_title'])
        io_redis.sadd('book_title', data['book_title'])
        # print('~' * 10, redis_result)
        # print('~' * 10, data)
        if redis_result:
            if OVER_WRITE_FLAG is True:
                io_redis.hmset(key, data)
        else:
            # print(data)
            io_redis.hmset(key, data)
