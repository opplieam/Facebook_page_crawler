# -*- coding: utf-8 -*-
import scrapy


class FbPageSpider(scrapy.Spider):
    name = 'fb_page'
    allowed_domains = ['facebook.com']
    start_urls = ['https://facebook.com/']

    def parse(self, response):
        pass
