import pandas as pd
import datetime
import myLib
import time

print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度
pd.set_option('display.colheader_justify', 'center')

# 创建Popularity类的实例
model = myLib.MyLib()
# 获取人气前350名股票
df = model.get_cond_popu_stocks(350)

now = datetime.datetime.now()
file_name =  'E:/python_workspace/cf/data/' + now.strftime("%m%d%H") + "_popu_stock.txt"
df['代码'].to_csv(file_name,mode='a', index=False, header=False)

