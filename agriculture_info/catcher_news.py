import re
import time
import requests
import datetime
import progressbar
from lxml import etree
from agriculture_info.db_connect import DBmongo


class NewsCatcher(object):
    def __init__(self, page_num):
        self.page_num =  page_num
        self.headers = {
            "Host": "www.farmer.com.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KH"
                          "TML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://www.farmer.com.cn/xbpd/xw/list.shtml",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
        }
        self.db_mongo = DBmongo("news")

    # 获取所有新闻详情页面
    def get_news_url(self, page_num):
        url_list = []
        self.show_time('正在获取数据包……')
        bar = progressbar
        for nid in bar.progressbar(range(page_num)):
            time.sleep(0.1)
            news_json_url = "http://www.farmer.com.cn/xbpd/xw/NewsList_%d.json" % nid
            try:
                news_json_source = requests.get(url=news_json_url, headers=self.headers)
            except Warning:
                self.show_time('请求失败')
            news_json = news_json_source.content.decode('UTF-8')
            url_searcher = re.compile(r'"url":"(.*?)"')
            result = url_searcher.findall(news_json)
            url_item = []
            for item in result:
                url_item.append(item.replace('\\', ''))
            url_list.extend(url_item)
        self.show_time('数据包获取完毕！')
        return url_list

    # 获取新闻页面的数据
    def get_news_date(self, url_list):
        self.show_time('正在抓取新闻内容……')
        date_list = []
        bar = progressbar
        for news_url in bar.progressbar(url_list):
            time.sleep(0.1)
            page = requests.get(url=news_url, headers=self.headers)
            page_html = etree.HTML(page.content.decode('UTF-8'))
            # 新闻标题
            title = page_html.xpath('//h1[@class="article-title"]/text()')
            # 新闻来源
            source = page_html.xpath('//div[@class="article-meta-left fl"]/sp'
                                     'an[@class="tag-text tag-text-source"]/text()')
            # 编辑
            editor = page_html.xpath('//span[@class="tag-text"][1]/text()')
            # 作者
            author = page_html.xpath('//span[@class="tag-text"][2]/text()')
            # 图片*(正文中的第一张照片)
            imge = page_html.xpath('//div[@class="article-main"]//img[1]/@src')
            # 正文
            article = page_html.xpath('//div[@id="article_main"]/p/text()')
            date_list.append({
                "title":    self.join_list(title),
                "source":   self.join_list(source),
                "editer":   self.join_list(editor),
                "author":   self.join_list(author),
                "imge":     self.join_list(imge),
                "article":  self.join_list(article)
            })
        self.show_time('数据抓取完毕！')
        return date_list

    # 打印当前进行的事件
    def show_time(self, event):
        dt_ms = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')  # 含微秒的日期时间，来源 比特量化
        print(dt_ms + ": " + str(event))

    def join_list(self, item):
        return "".join(item)

    def run(self):
        page_num = self.page_num
        url_list = self.get_news_url(page_num)
        date_list = self.get_news_date(url_list)
        self.show_time('正在注入数据库……')
        self.db_mongo.insert_date(date_list)
        self.show_time('数据注入完毕！')


if __name__ == '__main__':
    new = NewsCatcher()
    new.run()
