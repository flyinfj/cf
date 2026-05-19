import requests
import akshare as ak
import pandas as pd
import datetime
import time
import numpy as np
import json
import myLib
import getStockInfo

print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))                   
pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度  
pd.set_option('display.colheader_justify', 'center')
now = datetime.datetime.now()
file_name1 =  'E:/python_workspace/cf/data/' + now.strftime("%m%d%H") + ".txt"
file_name2 =  'E:/python_workspace/cf/data/' + now.strftime("%m%d%H") + "_stock.txt"
with open(file_name1, 'a', encoding='utf-8') as f:
    f.write('\n')
    f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    f.write('\n大盘买卖点\n')

model = myLib.MyLib()
start_date  = datetime.datetime.strptime(model.get_trade_dates(5).iloc[0], "%Y%m%d")
#获取上证指数30分钟指标
stock_his_df = model.get_stock_his('1.000001',30,start_date)
ud_df = model.calc_niceturn(stock_his_df,4).tail(3)
ud_df = ud_df.drop(['ud'], axis=1)
#ud_df = ud_df[ud_df['cumu_ud'].astype(int).isin([5,6,7, 8, 9,-7,-8,-9])]
ud_df['涨幅'] = ud_df['涨幅'].apply(lambda x: f"{x}%")
ud_df.reset_index(drop=True, inplace=True)       
print(ud_df)
ud_df.to_csv(file_name1, mode='a', header=True, index=False, sep='\t')

#获取上证指数15分钟指标
stock_his_df = model.get_stock_his('1.000001',15,start_date)
ud_df = model.calc_niceturn(stock_his_df,4).tail(3)
ud_df = ud_df.drop(['ud'], axis=1)
#ud_df = ud_df[ud_df['cumu_ud'].astype(int).isin([5,6,7, 8, 9,-7,-8,-9])]
ud_df['涨幅'] = ud_df['涨幅'].apply(lambda x: f"{x}%")
ud_df.reset_index(drop=True, inplace=True)       
print(ud_df)
ud_df.to_csv(file_name1, mode='a', header=True, index=False, sep='\t')

#获取深圳综数30分钟指标
stock_his_df = model.get_stock_his('0.399001',30,start_date)
ud_df = model.calc_niceturn(stock_his_df,4).tail(3)
ud_df = ud_df.drop(['ud'], axis=1)
#ud_df = ud_df[ud_df['cumu_ud'].astype(int).isin([5,6,7, 8, 9,-7,-8,-9])]
ud_df['涨幅'] = ud_df['涨幅'].apply(lambda x: f"{x}%")
ud_df.reset_index(drop=True, inplace=True)       
print(ud_df)
ud_df.to_csv(file_name1, mode='a', header=True, index=False, sep='\t')

#获取深圳综数15分钟指标
stock_his_df = model.get_stock_his('0.399001',15,start_date)
ud_df = model.calc_niceturn(stock_his_df,4).tail(3)
ud_df = ud_df.drop(['ud'], axis=1)
#ud_df = ud_df[ud_df['cumu_ud'].astype(int).isin([5,6,7, 8, 9,-7,-8,-9])]
ud_df['涨幅'] = ud_df['涨幅'].apply(lambda x: f"{x}%")
ud_df.reset_index(drop=True, inplace=True)       
print(ud_df)
ud_df.to_csv(file_name1, mode='a', header=True, index=False, sep='\t')

# 获取人气前350
df = model.get_popu_stocks(1)
df = df[df['代码'].apply(lambda x: x.startswith(('30', '60', '0')))]
stock_codes = df['代码'].tolist()
df2 = model.get_stock_nineturn(stock_codes,start_date,30,1,1)

if df2 is not None and not df2.empty:
    #获取标签
    stock_codes = df2['代码'].tolist()
    labels = model.get_stock_label(stock_codes)

    # 获取股本数据
    stockinfo_df = getStockInfo.GetStockInfo().get_stock_info(stock_codes)

    # 合并数据
    df = pd.merge(df2, df, on='代码', how='left')
    df = pd.merge(df, labels, on='代码', how='left')
    df = pd.merge(df, stockinfo_df, on='代码', how='left')

    #输出热门100的买卖点
    df = df.drop(columns=['时间'])  # 删除 'rc' 列
    df['标签'] = df['标签'].apply(lambda x: str(x).ljust(30))
    print(df)
    model.output_file(df, '热门100的买卖点')
