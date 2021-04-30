from selenium import webdriver
from selenium.webdriver import ChromeOptions
from lxml import etree
from agriculture_info.db_connect import DBmongo
import datetime
import progressbar
import re


class PCIFcarc(object):
    def __init__(self, page_num):
        self.page_num = page_num
        self.option = ChromeOptions()
        self.option.add_argument("--headless")
        self.browser = webdriver.Chrome(options=self.option)
        print("——虚拟浏览器已启动——")
        self.db_mongo = DBmongo("purchase")

    # 获取详情页面链接后缀
    def get_href_list(self, page_num):
        href_list = []
        self.show_time('正在抓取链接后缀……')
        for num in progressbar.progressbar(range(page_num)):
            url_cnhnb = "https://www.cnhnb.com/purchase/0-0-0-0-0-%d/" % num
            page = self.browser
            page.get(url_cnhnb)
            source = page.page_source
            html = etree.HTML(source)
            href = html.xpath('//div[@class="eye-renderer__inner"]/a/@href')
            href_list.extend(href)
        self.show_time('链接后缀抓取完毕！')
        return href_list

    # 获取详情页数据
    def get_page_date(self, href_list):
        date_list = []
        self.show_time('正在抓取数据……')
        for href in progressbar.progressbar(href_list):
            url_caigou = "https://www.cnhnb.com%s" % href
            page = self.browser
            page.get(url_caigou)
            source = page.page_source
            html = etree.HTML(source)
            # 发布人
            publisher = html.xpath('//div[@class="userInfo"]/div[1]//span[1]/text()')
            # 发布采购时间
            publish_date = html.xpath('//div[@class="purchase-right"]//div['
                                      '@class="purchase-tr startTime"]/div[2]/text()')
            # 采购品种
            varieties = html.xpath('//div[@class="purchase-table"]//div[@class="eye-renderer__inner"]//text()')
            # 品质规格
            specification = html.xpath('//div[@class="purchase-left"]/div[2]/div[2]/text()')
            # 期望货源地
            supply_address = html.xpath('//div[@class="purchase-left"]/div[3]/div[2]/text()')
            # 收货地址
            shipping_address = html.xpath('//div[@class="purchase-left"]/div[4]/div[2]/text()')
            # 补充说明
            note = html.xpath('//div[@class="purchase-left"]/div[5]/div[2]/text()')
            # 详情页面
            link = url_caigou
            date_dict = {
                'publisher':        self.join_list(publisher),
                'publish_date':     self.join_list(publish_date),
                'varieties':        self.join_list(varieties),
                'specification':    self.join_list(specification),
                'supply_address':   self.join_list(supply_address),
                'shipping_address': self.join_list(shipping_address),
                'note':             self.join_list(note),
                'link':             self.join_list(link)
            }
            # 过滤不完整数据
            if "" not in date_dict.values():
                date_list.append(date_dict)
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
        href = self.get_href_list(page_num)
        date_list = self.get_page_date(href)
        self.db_mongo.insert_date(date_list)
        self.browser.close()


if __name__ == '__main__':
    page_num = 10
    catcher = PCIFcarc(page_num)
    catcher.run()