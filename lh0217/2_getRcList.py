import requests
import json
import pandas as pd
import time
import akshare as ak
import datetime
import numpy as np
import myLib
import getStockInfo

print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))                   
pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度            
pd.set_option('display.colheader_justify', 'center')
model = myLib.MyLib()

#获取今日人气飙升前100+排名350升1000/150升450/50升150
df = model.get_popu_stocks(1)
df = df[(((df['排名'] < 350) & (df['较昨日变动'] > 1000)) | ((df['排名'] < 150) & (df['较昨日变动'] > 450)) | ((df['排名'] < 50) & (df['较昨日变动'] > 150)))]
df = df[df['代码'].apply(lambda x: x.startswith(('30', '60', '0')))]

if df is not None and not df.empty:
    # 获取涨幅
    stock_codes = df['代码'].tolist()
    df_raise = model.get_stock_data(stock_codes)

    # 获取九转
    start_date  = datetime.datetime.strptime(model.get_trade_dates(5).iloc[0], "%Y%m%d")
    df2 = model.get_stock_nineturn(stock_codes,start_date)

    # 获取标签
    labels = model.get_stock_label(stock_codes)

    # 获取股本数据
    stockinfo_df = getStockInfo.GetStockInfo().get_stock_info(stock_codes)

    # 合并
    df_all = pd.merge(df_raise, df2, on='代码', how='left')
    df_all = pd.merge(df_all, df, on='代码', how='left')
    df_all = pd.merge(df_all, labels, on='代码', how='left')
    df_all = pd.merge(df_all, stockinfo_df, on='代码', how='left')

    df_all['涨幅'] = df_all['涨幅'].apply(lambda x: f"{x}%")
    sorted_df = df_all.sort_values(by='排名', ascending=True)
    sorted_df = sorted_df.drop(columns=['时间'])
    sorted_df = sorted_df.drop(columns=['收盘'])
    sorted_df = sorted_df.drop(columns=['最新价'])
    sorted_df.reset_index(drop=True, inplace=True)  # 删除索引列并重置索引
    print(sorted_df)
    model.output_file(sorted_df, '今日人气飙升前100+排名350升1000/150升450/50升150')
