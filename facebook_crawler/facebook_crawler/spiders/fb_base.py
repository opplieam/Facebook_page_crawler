# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import FormRequest, Request


class FbBaseSpider(Spider):

    allowed_domains = ['facebook.com']
    start_urls = ['https://www.facebook.com/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        if not self.username or not self.password:
            raise CloseSpider('Please provide username or password')
        self.page_id = kwargs.get('page_id')
        if not self.page_id:
            raise CloseSpider('Please provide page_id')

        if ',' in self.page_id:
            self.page_id = self.page_id.split(',')
        else:
            self.page_id = [self.page_id]

    def parse(self, response):
        yield FormRequest.from_response(
            response=response,
            formid='login_form',
            formdata={
                'email': self.username,
                'pass': self.password
            },
            callback=self.parse_login
        )

    def parse_login(self, response):
        for page_id in self.page_id:
            url = f'https://www.facebook.com/{page_id}/posts/'
            yield Request(
                url=url, callback=self.parse_page, meta={'page_id': page_id}
            )
