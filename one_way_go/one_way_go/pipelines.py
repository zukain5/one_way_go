# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pathlib
import sqlite3
import time

import slackweb

from .secrets import SLACK_URL


class OneWayGoPipeline:
    """
    参考:https://qiita.com/Chanmoro/items/f4df85eb73b18d902739
    """
    _db = None

    @classmethod
    def get_database(cls):
        cls._db = sqlite3.connect(
            pathlib.Path().cwd() / 'one_way_go.db'
        )

        cur = cls._db.cursor()
        sql = '''
            CREATE TABLE IF NOT EXISTS one_way_go(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                departure_shop TEXT NOT NULL,
                arrival_shop TEXT NOT NULL,
                car_info TEXT NOT NULL,
                car_capacity TEXT NOT NULL,
                departure_since TEXT NOT NULL,
                departure_until TEXT NOT NULL,
                reserve_shop TEXT,
                reserve_number TEXT,
                is_available INTEGER NOT NULL
            );
        '''
        cur.execute(sql)

        return cls._db

    def process_item(self, item, spider):
        is_saved = self.save_item(item)
        if is_saved and item['is_available']:
            self.send_slack(item)
            time.sleep(1)

        return item

    def save_item(self, item):
        if self.find_item(
            item['departure_shop'],
            item['arrival_shop'],
            item['car_info'],
            item['departure_since'],
            item['departure_until']
        ):
            return False

        db = self.get_database()
        sql = '''
            INSERT INTO
                one_way_go
                (departure_shop, arrival_shop, car_info, car_capacity, departure_since,
                 departure_until, reserve_shop, reserve_number, is_available)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        db.execute(sql, (
            item['departure_shop'],
            item['arrival_shop'],
            item['car_info'],
            item['car_capacity'],
            item['departure_since'],
            item['departure_until'],
            item['reserve_shop'],
            item['reserve_number'],
            int(item['is_available']),
        ))
        db.commit()

        return True

    def find_item(self, departure_shop, arrival_shop,
                  car_info, departure_since, departure_until):
        db = self.get_database()
        sql = '''
            SELECT
                *
            FROM
                one_way_go
            WHERE
                departure_shop=?
                AND arrival_shop=?
                AND car_info=?
                AND departure_since=?
                AND departure_until=?
        '''

        cur = db.execute(sql, (
            departure_shop,
            arrival_shop,
            car_info,
            departure_since,
            departure_until,
        ))

        return cur.fetchone()

    def send_slack(self, item):
        slack = slackweb.Slack(url=SLACK_URL)

        departure_shop = item['departure_shop']
        arrival_shop = item['arrival_shop']
        car_info = item['car_info']
        car_capacity = item['car_capacity']
        departure_since = item['departure_since']
        departure_until = item['departure_until']

        attachments = [{
            'color': '#36a64f',
            'fields': [
                {
                    'title': '出発',
                    'value': departure_shop,
                    'short': 'true',
                },
                {
                    'title': '到着',
                    'value': arrival_shop,
                    'short': 'true',
                },
                {
                    'title': '車',
                    'value': f'{car_info}（{car_capacity}）',
                    'short': 'true',
                },
                {
                    'title': '出発期間',
                    'value': f'{departure_since} 〜 {departure_until}',
                    'short': 'true',
                },
            ],
        }]
        slack.notify(text='新しい片道GO!', attachments=attachments)
