import collections
import logging

import fire
import jieba
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from wordcloud import WordCloud

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("anaytics")


def preprocess(table):
    data = pd.read_csv(f"./output/{table}.csv")
    col = ['index', 'content', 'time']
    data.columns = col
    data["time"] = pd.to_datetime(data["time"])
    return data


class Analytics(object):
    def __init__(self):
        pass

    def draw_word_cloud(self, data):
        """
        WordCloud generator
        """
        segs = jieba.cut("".join(data["content"].tolist()))
        f = open('./lib/ignorewords.txt', 'r', encoding='utf-8')
        stopwords = {}.fromkeys(f.read().split('\n'))
        f.close()

        mytext_list = []
        for seg in segs:
            if seg not in stopwords and seg != ' ' and len(seg) != 1:
                mytext_list.append(seg.replace(' ', ''))
        mytext_count = collections.Counter(mytext_list)
        wc = WordCloud(background_color='white',
                       width=1920,
                       height=1080,
                       max_words=2000,
                       font_path='./lib/qingningyouyuan.ttf',
                       min_font_size=15)
        wc.generate_from_frequencies(mytext_count)
        wc.to_file(f'./output/{self.table}_wordcloud.png')
        logger.info("Finish drawing word cloud")

    def draw_day_chart(self, data):
        """
        Post daytime counter
        """
        count_for_24_hours = {}
        for h in range(24):
            for m in ["00", "30"]:
                h_m = str(h) + ":" + m
                count_for_24_hours[h_m] = 0
        i = 0
        for time in data["time"]:
            hour = time.hour
            if time.minute < 30:
                minute = "00"
            else:
                minute = "30"
            post_time = str(hour) + ":" + minute
            count_for_24_hours[post_time] += 1

        len_dict = 24 * 2
        hour_minute = [0 for i in range(len_dict)]
        count_times = [0 for i in range(len_dict)]
        i = 0
        for key, value in count_for_24_hours.items():
            hour_minute[i] = key
            count_times[i] = value
            i += 1

        plt.figure(figsize=(26, 6))
        plt.plot(range(len_dict), count_times, lw=5, marker='o',mec='w')
        plt.xlim(xmin=-0.5, xmax=47.5)
        _, ymax = plt.ylim()
        new_yticks = np.linspace(0, ymax, 5)
        plt.xticks(range(len_dict), hour_minute)
        plt.yticks(new_yticks)
        plt.hlines(new_yticks, -0.5, 47.5, colors="gray", linestyles="dashed")
        plt.xlabel("Post time")
        plt.ylabel("Post number")
        plt.title(f"{self.table} blog's line chart by half hour")
        plt.savefig(f"./output/{self.table}_day_chart.png")
        plt.close()
        logger.info("Finish drawing dayly chart")

    def draw_month_chart(self, data):
        """
        Post month counter
        """
        count_for_month = [0 for i in range(12)]
        for time in data["time"]:
            count_for_month[time.month - 1] += 1
        index_month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        plt.bar(range(1, 13), count_for_month)
        plt.xticks(range(1, 13), index_month)
        plt.title(f"{self.table} blog's line chart by month")
        plt.savefig(f"./output/{self.table}_month_chart.png")
        plt.close()
        logger.info("Finish drawing monthly chart")

    def draw(self, table):
        self.table = table
        data = preprocess(table)
        self.draw_word_cloud(data)
        self.draw_day_chart(data)
        self.draw_month_chart(data)


if __name__ == '__main__':
    fire.Fire(Analytics)
