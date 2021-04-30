import pymongo
from pymongo.collection import Collection


class DBmongo(object):
    def __init__(self, set_name):
        # 指定一个客户端连接本地mongodb
        pymongo_client = pymongo.MongoClient(host="127.0.0.1", port=27017)
        print("——成功连接到Mongodb——")
        # 指定数据库为farmer
        farmer_db = pymongo_client["farmer"]
        # 创建/连接新闻集合news
        print("——当前数据集合：%s——" % set_name)
        self.farmer = Collection(farmer_db, set_name)

    def insert_date(self, date_list):
        self.farmer.insert_many(date_list)
        print("——数据插入完毕！——")

