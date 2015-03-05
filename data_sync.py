#!/usr/bin/env python
#-*-coding:utf-8-*-
"""
    从 cp.360.cn 同步时时彩的数据到表 haoma
"""
import datetime
from datetime import timedelta
import time
import torndb
import sys
import requests
import re
from mylogger import get_logger

reload(sys)
sys.setdefaultencoding('utf-8')

DBHOST = "localhost:3306"
SCHEMA = "CAIPIAO"
DBUSER = "user"
DBPASSWD = "passwd"

db = torndb.Connection(host=DBHOST, database=SCHEMA, user=DBUSER, password=DBPASSWD)
cplog = get_logger("caipiao")

class Data_Sync(object):
    ssc_re = re.compile(r'<td class=\'gray\'>(.*?)</td>(<td class=\'red big\'>|<td style=\'width:65px\'>)(.*?)</td>.*?<tr>')

    def __init__(self, start_date="20150101", sleep_secs = 10, run_ever=True, callback=None):
        self.start_date = start_date if start_date > "20130101" else "20150101"
        self.run_ever = run_ever
        self.base_url = "http://chart.cp.360.cn/kaijiang/kaijiang?lotId=255401&spanType=2&span="
        self.latest_date = ''
        self.latest_period = ''
        self.need_sleep = False
        self.sleep_secs = sleep_secs
        self.callback=callback

    def run(self):
        while True:
            if self.need_sleep:
                time.sleep(self.sleep_secs)
                self.need_sleep = False
            else:
                self.sync_data_from_360()
                self.callback()

    def sync_data_from_360(self):
        """ 根据数据库中最新一条数据，从 cp.360.com 同步数据至最新数据 """
        self.get_latest_haoma_from_mysql()

        if not self.latest_date:
            cplog.info("db has no data, so start at {0}".format(self.start_date))
            self.latest_date = self.start_date
            self.latest_period = "000"

        cplog.info("in db, item_date={0}, period={1}".format(self.latest_date, self.latest_period))

        if self.latest_date:
            cur_date = datetime.datetime.utcnow() + timedelta(hours=8)
            latest_date = datetime.datetime.strptime(self.latest_date, "%Y%m%d")
            """
                更新规则:
                1、检查是否同一天，如果不是，就下载数据，执行步骤2，增加天数，直到数据库日期与当前日一致；
                2、检查数据库中的期数与下载回来的数据的最新期是否一致，一致,检查日期是否一致，是就跳过，否则插入数据；
            """
            dl_times = 0
            while (cur_date - latest_date).days > 0:
                if int(self.latest_period) < 120:
                    dl_date = latest_date.strftime("%Y-%m-%d")
                    dl_url = self.base_url + dl_date + "_" + dl_date
                    data = self.download_with_requests(dl_url)
                    if not data:
                        if dl_times < 3:
                            dl_times += 1
                            time.sleep(2)
                            continue
                        else:
                            latest_date += timedelta(1)
                            continue

                    dl_times = 0
                    self.latest_date = latest_date.strftime('%Y%m%d')
                    lottery_numbers = data[int(self.latest_period):]
                    self.insert_into_mysql(self.latest_date, lottery_numbers)
                    latest_date += timedelta(1)
                else:
                    latest_date += timedelta(1)
                    self.latest_period = "000"

            """ 更新当日数据 """
            dl_date = latest_date.strftime("%Y-%m-%d")
            dl_url = self.base_url + dl_date + "_" + dl_date
            data = self.download_with_requests(dl_url)
            if data:
                lottery_numbers = data[int(self.latest_period):]
                self.latest_date = latest_date.strftime('%Y%m%d')
                self.insert_into_mysql(self.latest_date, lottery_numbers)

    def insert_into_mysql(self, item_date, datas):
        insert_datas = []
        for data in datas:
            period = data[0]
            date_period = item_date + period
            lottery_number = data[2]
            if not re.search('\d+', lottery_number):
                continue
            a, b, c, d, e = list(lottery_number)
            ab = a + b
            ac = a + c
            ad = a + d
            ae = a + e
            bc = b + c
            bd = b + d
            be = b + e
            cd = c + d
            ce = c + e
            de = d + e
            insert_data = (item_date, period, date_period, lottery_number, a, b, c, d, e, ab, ac, ad, ae, bc, bd, be, cd, ce, de)
            insert_datas.append(insert_data)

        if insert_datas:
            cplog.info("current insert into haoma:{0}, {1}".format(item_date, datas))
            """ abcde means  lottery_number """
            sql = "insert into haoma(item_date, period, date_period, abcde, a, b, c, d, e, ab, ac, ad, ae, bc, bd, be, cd, ce, de) values(%s, %s, %s, %s, %s,  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            try:
                db.executemany(sql, insert_datas)
            except Exception as e:
                print e
                sys.exit(1)
        else:
            cplog.info("no more new data to sync, wait for {0} seconds".format(self.sleep_secs))
            self.need_sleep = True

    def get_latest_haoma_from_mysql(self):
        sql = "select * from haoma order by date_period desc limit 1"
        ret = db.get(sql)
        if ret:
            self.latest_date = ret.item_date
            self.latest_period = ret.period

    def download_with_requests(self, url):
        cplog.info("download: {0}".format(url))
        data = []
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = self.ssc_re.findall(r.content)
            else:
                cplog.info("download err, http status_code:{0}".format(r.status_code))
        except Exception as e:
            cplog.info("call requests raise Exception: {0}".format(e))
        finally:
            return data

def run():
    from general_run import entry_for_all
    sync = Data_Sync(start_date="20150101", sleep_secs=30, callback=entry_for_all)
    sync.run()

if __name__ == "__main__":
    run()
