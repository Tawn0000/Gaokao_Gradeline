# -*- coding: utf-8 -*-
import re
import scrapy
import logging
import datetime
from gaokao_crawl.items import GaokaoCrawlItem
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class FractionalLineSpider(scrapy.Spider):
    name = 'fractional_line'
    allowed_domains = ['exercise.kingname.info, college.gaokao.com']
    start_urls = ['http://college.gaokao.com/']

    custom_settings = {
        'URLLENGTH_LIMIT': 100000,
        'DOWNLOAD_DELAY': 0.1,
        'TELNETCONSOLE_PORT': [],
        'REDIRECT_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [],
        'DEFAULT_REQUEST_HEADERS': {},
        'DOWNLOADER_MIDDLEWARES': {
        #    'xxxx.middlewares.ua_rotate.RandomUserAgent': 1,
        #    'xxxx.middlewares.abuproxy.ProxyMiddleware': 902,
        },
        # set ua and proxy
        'USER_AGENT_ROTATE_ENABLED': True,
        'USER_AGENT_TYPE': 'PC',
        'PROXY_ENABLED': True,

        'SPIDER_MIDDLEWARES': {
            # 'gaokao_crawl.middlewares.DeltaFetchMiddleware': 901
        },
        # set deltafetch_key
        'DELTAFETCH_ENABLED': True,
        'DELTAFETCH_KEY_NAME': '',
        'DELTAFETCH_DB_NAME': '',
        'DELTAFETCH_COLLECTION_NAME': '',
        'DELTAFETCH_TYPE': 'MONGO',

        'ITEM_PIPELINES': {
            'gaokao_crawl.pipelines.GaokaoCrawlPipeline': 300
        },
        # set pipelines and mongodb
        'MONGO_EXPORT_ENABLED': True,
        'MONGO_COLLECTION': 'gaokao_crawl_data',
        # set cookies
        'COOKIES_ENABLED': True,
        'COOKIES_DEBUG': True,
        # set cocurrent request
        'CONCURRENT_REQUESTS_PER_DOMAIN': 15,
        'CONCURRENT_REQUESTS_PER_IP': 15,
    }

    pre_url = 'http://college.gaokao.com/spepoint/a{}/s{}/y{}/'

    def start_requests(self):
        return self.req_index()

    def req_index(self):
        for a in range(30, 40):
            for s in range(1, 2):
                for y in range(2012, 2018):
                    url = self.pre_url.format(str(a), str(s), str(y))
                    req = scrapy.Request(url=url, callback=self.parse_index, dont_filter=True)
                    req.meta['priority'] = 100
                    yield req

    def parse_index(self, response):
        index_path = '//*[@id="qx"]/text()[1]'
        try:
            page_num = response.xpath(index_path).extract()[0]
            page_num = int(re.search(r'[0-9]+页', page_num)[0][:-1])
            return self.req_page(page_num, resp_url=response.url)
        except:
            # set logger
            self.logger.warning("exception: parse_index, url: {}".format(response.url))
            return None

    def req_page(self, page_num, resp_url):
        for i in range(1, page_num + 1):
            url = resp_url + 'p{}/'.format(str(i))
            # print(url)
            req = scrapy.Request(url=url, callback=self.parse_page, dont_filter=True)
            req.meta['index'] = i
            req.meta['priority'] = 200
            yield req

    def parse_page(self, response):
        # 测试页面是否为空
        try:
            index_path = '//*[@id="qx"]/text()[1]'
            page_num = response.xpath(index_path).extract()[0]
            page_num = int(re.search(r'[0-9]+页', page_num)[0][:-1])
        except:
            self.logger.warning("exception: parse_page, url: {}".format(response.url))
            return None

        # tbdoy 需要删去，会干扰xpath解析
        # college_path = '//*[@id="wrapper"]/div[4]/table/tbody/tr[{}]/td[2]/a/text()'
        # ave_score_path = '//*[@id="wrapper"]/div[4]/table/tbody/tr[{}]/td[3]/a/text()'
        path = '//*[@id="wrapper"]/div[4]/table/tr[{}]/td[{}]/{}text()'
        ed = 150
        for i in range(2, ed):
            if len(response.xpath(path.format(str(i), '2', 'a/')).extract()) <= 0:
                break
            item = GaokaoCrawlItem()
            item['domain'] = 'college.gaokao.com'  # 被爬网站的标识
            item['url'] = response.url  # 爬取url
            item['category'] = 'detail'  # 页面类别，列表页or详情页
            item['scraped_time'] = str(datetime.datetime.now())
            item['college'] = response.xpath(path.format(str(i), '2', 'a/')).extract()[0]  # 录取学校
            item['major'] = response.xpath(path.format(str(i), '1', 'a/')).extract()[0]  # 录取专业
            item['area'] = response.xpath(path.format(str(i), '5', '')).extract()[0]  # 地区
            item['branch'] = response.xpath(path.format(str(i), '6', '')).extract()[0]  # 文理科别
            item['year'] = response.xpath(path.format(str(i), '7', '')).extract()[0]  # 年份
            item['batch'] = response.xpath(path.format(str(i), '8', '')).extract()[0]  # 年份
            item['ave_score'] = response.xpath(path.format(str(i), '3', 'a/')).extract()[0]  # 平均分
            item['hig_score'] = response.xpath(path.format(str(i), '4', '')).extract()[0]  # 最高分
            item['raw_key'] = item['year'] + item['college'] + item['major'] + item['area']  # 被爬取网站的主键
            yield item
            # for key, value in item.items():
            #     print(key, ":  ", value)

        # item = GaokaoCrawlItem()
        # item['raw_key'] = abs(hash(response.url))  # 被爬取网站的主键
        # item['domain'] = 'college.gaokao.com'  # 被爬网站的标识
        # item['url'] = response.url  # 爬取url
        # item['category'] = 'list'  # 页面类别,列表页or详情页
        # item['html'] = response.text
        # item['scraped_time'] = str(datetime.datetime.now())
        # yield item

    # 检查 ua 和 proxy 是否已经设置好
    # def start_requests(self):
    #     # url = 'http://exercise.kingname.info/exercise_middleware_ip/'
    #     import os
    #     print(os.getcwd())
    #     url = 'http://exercise.kingname.info/exercise_middleware_ua/'
    #     for i in range(10):
    #         yield scrapy.Request(url + str(i), callback=self.parse, dont_filter=True)

    def parse(self, response):
        print(response.text)
        pass
