import pymongo
import numpy as np # 线性代数库
import pandas as pd # 数据分析库
import matplotlib.pyplot as plt
import seaborn as sns
import wordcloud
import imageio
# %matplotlib inline

plt.rc('font',family=['Arial Unicode MS'])

class GaokaoGradeAnalysis:
    def __init__(self):
        self.MONGO_URI = 'mongodb://127.0.0.1:27017'
        self.client = pymongo.MongoClient(self.MONGO_URI)
        self.database = self.client['test']
        self.collection = self.database['gaokao_crawl_data']
        
    def grade_line(self, area, college):
        if self.collection.count({'area':area, 'college':college, 'branch':'理科'}) < 100:
            return None
        
        cur = self.collection.find({'area':area, 'college':college, 'branch':'理科'})
        item_list = [item for item in cur]
#         item_list.sort(key=lambda x: x['ave_score'])
        df = pd.DataFrame({"Grade": [int(x['ave_score']) for x in item_list if x['ave_score'] != '--'], 
                           "Year":  [int(x['year']) for x in item_list if x['ave_score'] != '--'],
                           "Major": [x['major'] for x in item_list if x['ave_score'] != '--']})
        if len(df) <= 10:
            return None
        f, ax = plt.subplots(figsize = (14, 11))
        ax.set_title('{}在{}省各专业历年分数线变化趋势图'.format(college, area))
        sns.pointplot(x="Year", y="Grade", hue='Major', data=df, ax=ax)
        ax.figure.savefig("images/grade_line/{}_{}.png".format(college, area))
    
    def major_cloud(self):
        mk = imageio.imread("images/chinamap.png")
        w = wordcloud.WordCloud(mask=mk)
        # 构建并配置词云对象w，注意要加scale参数，提高清晰度
        w = wordcloud.WordCloud(width=1000,
                                height=700,
                                background_color='white',
                                font_path='FangZhengHeiTiJianTi-1.ttf',
                                mask=mk,
                                scale=15)

        cur = self.collection.find()
        major_list = []
        [major_list.append(item['major']) for item in cur]
#         print(major_list)
        string = " ".join(major_list)
#         print(string)
        # 将string变量传入w的generate()方法，给词云输入文字
        w.generate(string)
        # 将词云图片导出到当前文件夹
        w.to_file('images/major_cloud.png')


    
    def get_key_list(self, key):
        '''
        key 可为area,college,major
        '''
        cur = self.collection.find()
        key_list = []
        [key_list.append(item[key]) for item in cur if item[key] not in key_list]
        return key_list
    
        
if __name__ == '__main__':    
    model = GaokaoGradeAnalysis()
    area_list = model.get_key_list('area')
    college_list = model.get_key_list('college')
#     for area in area_list:
#         model.grade_line(area, '江南大学')
#         model.grade_line(area, '清华大学')
        
    for college in college_list:
        model.grade_line('江苏', college)
        model.grade_line('湖南', college)
        
#     model.major_cloud()