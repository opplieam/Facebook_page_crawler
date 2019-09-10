# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity
from scrapy import Item, Field


class FacebookPostItem(Item):
    page_id = Field()
    page_name = Field()
    post_id = Field()
    post_url = Field()
    post_text = Field()
    image_urls = Field()
    video_url = Field()
    comment_count = Field()
    reaction_count = Field()
    share_count = Field()
    comments = Field()


class FacebookPostItemLoader(ItemLoader):
    default_item_class = FacebookPostItem
    default_output_processor = TakeFirst()

    post_text_out = Join()
    image_urls_out = Identity()
    comments_out = Identity()


class FacebookCommentItem(Item):
    comment_id = Field()
    comment_text = Field()
    author_name = Field()
    author_id = Field()
    author_url = Field()


class FacebookCommentItemLoader(ItemLoader):
    default_item_class = FacebookCommentItem
    default_output_processor = TakeFirst()
