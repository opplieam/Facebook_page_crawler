# -*- coding: utf-8 -*-
import urllib
import re
import demjson
import json

from scrapy.http import FormRequest, Request
from scrapy.exceptions import CloseSpider
from scrapy.selector import Selector

from scrapy.utils.response import open_in_browser
from scrapy.shell import inspect_response

from scrapy.loader.processors import MapCompose

from facebook_crawler.items import (
    FacebookPostItemLoader, FacebookCommentItemLoader
)
from facebook_crawler.spiders.fb_base import FbBaseSpider


class FbPageSpider(FbBaseSpider):
    name = 'fb_page'

    def _create_structed_json_data(self, json_data):
        '''
        Turn unordered post comment into a form of {post_id(1): json_data, post_id(2): json_data}
        '''
        json_data = json_data.get('jsmods').get('pre_display_requires')
        # Get only comment
        json_data = [x for x in json_data if x[1] == 'next']
        result = dict()
        for data in json_data:
            feedback_data = data[3][1].get(
                '__bbox').get('result').get('data').get('feedback')
            post_id = feedback_data.get('subscription_target_id')
            result[post_id] = feedback_data
        return result

    def parse_page(self, response):
        # inspect_response(response, self)
        if 'reaction_units/more' in response.url:
            json_data = json.loads(
                response.body_as_unicode().replace('for (;;);', ''))
            post_html = json_data.get('domops')[0][-1].get('__html')
            structural_json_data = self._create_structed_json_data(json_data)
        else:
            main_content_id = response.css(
                '#pagelet_timeline_main_column>div::attr(id)'
            ).extract_first()
            if not main_content_id:
                raise CloseSpider('Main content id not found')

            main_script = response.xpath(
                f'//script/text()[contains(.,"{main_content_id}") '
                f'and contains(.,"content:")]'
            ).extract_first()
            main_id = re.search(r'container_id\:"(.*?)"', main_script).group(1)
            post_html = response.css(f'#{main_id}').extract_first()
            post_html = post_html.replace('-->', '').replace('<!--', '')

        sel = Selector(text=post_html)
        posts = sel.xpath(
            '//div[@class="_1xnd"]'
            '/div[@class and not(descendant::*[contains(@class,"uiMorePagerPrimary")])]'
        )
        page_name = response.meta.get('page_name') or \
                    response.css('#pageTitle::text').extract_first()
        page_name = page_name.split('-')[0].rstrip()
        page_id = response.meta.get('page_id')

        for post in posts:
            loader = FacebookPostItemLoader(selector=post)
            loader.add_value('page_name', page_name)
            loader.add_value('page_id', page_id)
            loader.add_css('post_id', 'input[name*="identifier"]::attr(value)')
            post_id = loader.get_output_value('post_id')
            loader.add_value(
                'post_url',
                f'https://www.facebook.com/{page_id}/posts/{post_id}'
            )
            loader.add_xpath(
                'post_text',
                './/div[@data-testid="post_message"]'
                '//text()[not(ancestor::span[@class="text_exposed_hide"])]'
            )
            loader.add_css(
                'image_urls', '.mtm a::attr(data-ploi)',
                MapCompose(lambda v: v.split('?')[0])
            )
            loader.add_css(
                'video_url', '.fsm>a::attr(href)',
                MapCompose(
                    response.urljoin,
                    lambda v: v if 'videos' in v else None,
                    lambda v: v.split('?')[0]
                )
            )
            if 'reaction_units/more' in response.url:
                post_json_data = structural_json_data.get(post_id)
            else:
                # inspect_response(response, self)
                post_script = response.xpath(
                    f'//script/text()[contains(.,"{post_id}") '
                    f'and (contains(.,"post_fbid") or contains(.,"photo_fbid"))]'
                ).extract_first()
                post_script = re.search(
                    r'onPageletArrive\((\{.*\})',
                    post_script
                ).group(1).split('all_phases')[0] + '}'
                json_data = demjson.decode(post_script)
                json_data = json_data.get('jsmods').get(
                    'pre_display_requires')[0][3][1].get('__bbox')
                variables = json_data.get('variables')
                post_json_data = json_data.get('result').get('data').get('feedback')

            loader.add_value(
                'comment_count',
                post_json_data.get('comment_count').get('total_count')
            )
            loader.add_value(
                'reaction_count',
                post_json_data.get('reaction_count').get('count')
            )
            loader.add_value(
                'share_count',
                post_json_data.get('share_count').get('count')
            )
            comment_json = post_json_data.get('display_comments')
            edges = comment_json.get('edges')
            for edge in edges:
                comment_loader = FacebookCommentItemLoader()
                node = edge.get('node')
                comment_loader.add_value('comment_id', node.get('id'))
                try:
                    comment_loader.add_value(
                        'comment_text', node.get('body').get('text')
                    )
                except AttributeError:
                    pass
                author = node.get('author')
                comment_loader.add_value('author_name', author.get('name'))
                comment_loader.add_value('author_id', author.get('id'))
                comment_loader.add_value('author_url', author.get('www_url'))
                loader.add_value('comments', comment_loader.load_item())

            yield loader.load_item()

            # TODO: Fetch first 50 comments
            # page_info = comment_json.get('page_info')
            # has_next_comment_page = page_info.get('has_next_page')
            # if has_next_comment_page:
            #     end_cursor = page_info.get('end_cursor')
            #     variables['after'] = end_cursor
            #     variables['before'] = None
            #
            #     # yield Request(
            #     #     url='https://www.facebook.com/api/graphql/',
            #     #     method='POST',
            #     #     body=json.dumps(body),
            #     #     callback=self.parse_next_comment,
            #     #     headers=headers,
            #     # )

        async_get_token = response.xpath(
            '//script/text()[contains(.,"async_get_token")]'
        ).extract_first() or response.body_as_unicode()
        async_get_token = re.search(
            r'"async_get_token"\:"(.*?)"', async_get_token
        ).group(1)

        next_page = sel.css('.uiMorePagerPrimary::attr(ajaxify)').extract_first()
        if next_page:
            next_url = response.urljoin(next_page)
            extra_params = urllib.parse.urlencode(
                {'__a': 1, 'fb_dtsg_ag': async_get_token}
            )
            next_url += '&' + extra_params
            yield Request(
                next_url, callback=self.parse_page,
                meta={
                    'page_name': page_name,
                    'page_id': page_id
                }
            )

