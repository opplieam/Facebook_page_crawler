# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from scrapy.exceptions import CloseSpider


class FacebookPostgresPipeline(object):

    def __init__(self, db, user, password, host, port):
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        if not hasattr(crawler.spider, 'database'):
            return None

        db_settings = crawler.settings.getdict('DB_SETTINGS')
        if not db_settings:
            raise CloseSpider('Please provide DB_SETTINGS in settings.py file')
        return cls(
            db=db_settings['db'],
            user=db_settings['user'],
            password=db_settings['password'],
            host=db_settings['host'],
            port=db_settings['port']
        )

    def open_spider(self, spider):
        try:
            self.connection = psycopg2.connect(
                user=self.user, password=self.password, host=self.host,
                port=self.port, database=self.db
            )
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT version();")
            record = self.cursor.fetchone()
            spider.logger.info(f"You are connected to - {record}", )
        except (Exception, psycopg2.Error) as error:
            raise CloseSpider(error)

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        posts_upsert = """
            INSERT INTO posts (
            post_id, page_id, page_name, post_url, 
            post_text, video_url, comment_count, 
            reaction_count, share_count
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (post_id)
            DO UPDATE SET
            page_id = %s,
            page_name = %s,
            post_text = %s,
            comment_count = %s,
            reaction_count = %s,
            share_count = %s
        """
        image_urls_insert = """
            INSERT INTO image_urls (
            post_id, image_url
            )
            VALUES (%s, %s)
            ON CONFLICT (post_id, image_url)
            DO NOTHING
        """
        comments_upsert = """
            INSERT INTO comments (
            comment_id, post_id, comment_text, author_name, 
            author_id, author_url
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (comment_id)
            DO UPDATE SET
            comment_text = %s,
            author_name = %s,
            author_url = %s
        """
        page_id = item.get('page_id')
        page_name = item.get('page_name')
        post_id = item.get('post_id')
        post_url = item.get('post_url')
        post_text = item.get('post_text')
        video_url = item.get('video_url')
        comment_count = item.get('comment_count')
        reaction_count = item.get('reaction_count')
        share_count = item.get('share_count')
        self.cursor.execute(
            posts_upsert,
            (
                post_id,
                page_id,
                page_name,
                post_url,
                post_text,
                video_url,
                comment_count,
                reaction_count,
                share_count,
                page_id,
                page_name,
                post_text,
                comment_count,
                reaction_count,
                share_count
            )
        )

        image_urls = item.get('image_urls')
        if image_urls:
            for image_url in image_urls:
                self.cursor.execute(
                    image_urls_insert,
                    (
                        post_id,
                        image_url
                    )
                )

        comments = item.get('comments')
        if comments:
            for comment in comments:
                comment_id = comment.get('comment_id')
                comment_text = comment.get('comment_text')
                author_name = comment.get('author_name')
                author_id = comment.get('author_id')
                author_url = comment.get('author_url')
                self.cursor.execute(
                    comments_upsert,
                    (
                        comment_id,
                        post_id,
                        comment_text,
                        author_name,
                        author_id,
                        author_url,
                        comment_text,
                        author_name,
                        author_url
                    )
                )
        self.connection.commit()
        return item
