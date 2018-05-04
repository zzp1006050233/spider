__author__ = 'zzp'
__date__ = '2018/4/25 16:38'
import requests
from scrapy import Selector
import MySQLdb

conn = MySQLdb.connect(host="127.0.0.1", port=3307, user="root", passwd="root", db="article_spider", charset="utf8")
cursor = conn.cursor()


def crawl_ips():
    # 爬去西刺的免费IP
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"}
    for i in range(600):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")
        ip_list = []

        for tr in all_trs[1:]:
            speed_tr = tr.css(".bar::attr(title)").extract()[0]
            if speed_tr:
                speed = float(speed_tr.split("秒")[0])

            all_text = tr.css("td::text").extract()
            ip = all_text[0]
            port = all_text[1]
            proxy_type = all_text[5]
            ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            cursor.execute(
                "insert proxy_ip(ip, port, speed, proxy_type) VALUES('{0}', '{1}', {2}, 'HTTP') ON DUPLICATE KEY UPDATE speed = VALUES(SPEED) ".format(
                    ip_info[0], ip_info[1], ip_info[3]
                )
            )
            conn.commit()


class GetIp(object):
    # 删除无用ip
    def delete_ip(self, ip):
        delete_sql = """
            DELETE FROM proxy_ip WHERE ip = {0}
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    # 对ip判断观察是否可以用
    def judge_ip(self, ip, port):
        http_url = "https://www.baidu.com/"
        proxy_url =  "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            # 删除ip 返回false
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        # 从数据库中随机去除一条proxy_ip的记录
        random_sql = """
            SELECT * FROM proxy_ip ORDER BY RAND() LIMIT 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            # 对得到的ip数据进行判断，看是否可用
            check_ip = self.judge_ip(ip, port)
            if check_ip:
                return "http://{0}:{1}".format(ip, port)
            else:
                self.get_random_ip()


if __name__ == "__main__":
    get_ip = GetIp()
    get_ip.get_random_ip()