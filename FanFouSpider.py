import logging
import time
import urllib.request
import zlib

import fire
import pandas as pd
import pymysql
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("FF_spider")


class FanFouSpider(object):
    def __init__(self, table="test"):
        self.headers = {
            "user-agent": None,
            "Cookie": None,
            "Accept": None,
            "Accept-Encoding": None
        }
        self.db = pymysql.connect(host="localhost",
                                  port=3306,
                                  user="root",
                                  password=None,
                                  db="spider",
                                  charset="utf8")
        self.table = table

    def start(self, ff_id):
        self.create_table(self.table)
        latest_time = self.latest_time(self.table)
        url_raw = f"http://fanfou.com/{ff_id}/p."
        i = 1
        while True:
            logger.info(f"Collecting page {i} message...")
            url_new = url_raw + str(i)
            self.get_content(url_new, latest_time)
            i += 1

    def get_content(self, url, latest_time):
        self.db.ping(reconnect=True)
        cursor = self.db.cursor()
        # connection retry
        for i in range(3):
            try:
                request = urllib.request.Request(url, headers=self.headers)
            except:
                if i < 3:
                    logger.warning("URL reconnection...")
                    time.sleep(5)
                    continue
                raise ConnectionError("Can not connect URL")
        html = urllib.request.urlopen(request).read()
        decompressed_data = zlib.decompress(html, 16 + zlib.MAX_WBITS)
        soup = BeautifulSoup(decompressed_data, 'html.parser')
        all_results = soup.find_all("li")
        count_content = 0
        for result in all_results:
            cont = result.find("span", class_="content")
            if cont is None:
                continue
            _time = result.find("span", class_="stamp").find("a")["title"]
            if _time == latest_time:
                raise IndexError("Data-set already updated.")
            count_content += 1
            sql = 'INSERT INTO `{}`(`content`, `time`) VALUES ("{}", "{}")'.format(
                self.table, cont.get_text(), _time)
            try:
                cursor.execute(sql)
                self.db.commit()
            except:
                self.db.rollback()
        if count_content == 0:
            raise IndexError("There is no contents anymore.")

    def create_table(self, table_name):
        """
            Create table if not exist.
        """
        sql = f"CREATE TABLE IF NOT EXISTS `{table_name}`\
              (`id` int(11) NOT NULL AUTO_INCREMENT,\
               `content` varchar(200) NOT NULL,\
               `time` varchar(30) NOT NULL,\
               PRIMARY KEY (`id`))\
               ENGINE=InnoDB DEFAULT CHARSET=utf8 "
        self.db.ping(reconnect=True)
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()

    def latest_time(self, table):
        """
            find the latest twitter in dataset
        """
        sql = f"SELECT time FROM `{table}` ORDER BY time DESC LIMIT 1"
        self.db.ping(reconnect=True)
        cursor = self.db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        if result == ():
            return None
        else:
            latest_time = result[0][0]
            return latest_time

    def key_word(self, table, key_word):
        sql = f"SELECT * FROM `{table}` WHERE content LIKE '%{key_word}%'"
        self.db.ping(reconnect=True)
        cursor = self.db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        for _, content, post_time in results:
            print(f"{content} | {post_time}")
            print("\n")
        self.db.close()

    def dump(self, table):
        sql = f'SELECT * FROM {table};'
        self.db.ping(reconnect=True)
        cur = self.db.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        data = pd.DataFrame(list(result))
        data.to_csv(f"./output/{table}.csv", index=False, sep=",")


if __name__ == '__main__':
    try:
        fire.Fire(FanFouSpider)
    except IndexError as e:
        logger.info(e.args)
        logger.info("OK! All information has been collected!")
