# mongo to json code
import pymongo
import json

class Transform:
    def __init__(self):
        self.MONGO_URI = 'mongodb://127.0.0.1:27017'
        self.client = pymongo.MongoClient(self.MONGO_URI)
        self.database = self.client['test']
        self.collection = self.database['gaokao_crawl_data']
        
    def write(self, st, num, file_path):
        cur = self.collection.find().skip(st).limit(num)
        with open(file_path.format(), "w") as f:
            for item in cur:
                del item['_id']
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
            print("{}条数据加载入{}文件完成...".format(num, file_path))
            
    def read(self, file_path):
        with open(file_path,'r') as load_f:
            while True:
                line = load_f.readline()
                if line:
                    r = json.loads(line)
                    print(r)
                else:
                    break
                    
    def count(self):
        print(collection.count())

if __name__ == '__main__':
    transform = Transform()
#     transform.count()
#     transform.read("json/record_1.json")
#     for i in range(0, 85):
#         transform.write(i*10000, 10000, "json/record_%03d.json" % i)
