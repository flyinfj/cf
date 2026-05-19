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
model = myLib.MyLib()
now = datetime.datetime.now()
file_name1 =  '{model.data_dir}/data/' + now.strftime("%m%d%H") + ".txt"
file_name2 =  '{model.data_dir}/data/' + now.strftime("%m%d%H") + "_stock.txt"

start_date  = model.get_trade_dates(5).iloc[0,0]
#获取上证指数30分钟指标
def get_bank_ud(stock_code,klt):
    if  klt == 102:
        s_klt = '周'
        start_date = model.get_trade_dates(75).iloc[0, 0]
    if klt == 101:
        s_klt = '日'
        start_date = model.get_trade_dates(15).iloc[0, 0]
    if klt == 30:
        s_klt = '30分'
        start_date = model.get_trade_dates(4).iloc[0, 0]
    if klt == 15:
        s_klt = '15分'
        start_date = model.get_trade_dates(2).iloc[0, 0]
    stock_his_df = model.get_stock_his(stock_code, klt, start_date)
    ud_df = model.calc_niceturn(stock_his_df, 4).tail(5)
    pd.options.mode.chained_assignment = None
    df = ud_df[['代码','涨幅','九转']]
    df['涨幅'] = df['涨幅'].apply(lambda x: f"{float(x):6.2f}%")
    df['九转'] = df['九转'].astype(str)
    df.columns = [f'代码',f'涨幅({s_klt})',f'九转({s_klt})']
    df.reset_index(drop='True',inplace=True)
    df.reset_index(inplace=True)
    return df
def get_bank_uds(stock_code):
    df_102 = get_bank_ud(stock_code,102)
    df_101 = get_bank_ud(stock_code,101)
    df_30 = get_bank_ud(stock_code,30)
    df_15 = get_bank_ud(stock_code,15)
    df = pd.merge(df_102, df_101, on=['index','代码'])
    df = pd.merge(df, df_30, on=['index','代码'])
    df = pd.merge(df, df_15, on=['index','代码'])
    return df
df = get_bank_uds('1.000001')
df['名称'] = '上证指数'
df = df[['代码','名称','涨幅(周)','九转(周)','涨幅(日)','九转(日)','涨幅(30分)','九转(30分)','涨幅(15分)','九转(15分)']]
print(model.beautify(df))
model.output_file(model.beautify(df),'上证神奇九转指数情况',0)

df = get_bank_uds('0.399001')
df['名称'] = '深证综指'
df = df[['代码','名称','涨幅(周)','九转(周)','涨幅(日)','九转(日)','涨幅(30分)','九转(30分)','涨幅(15分)','九转(15分)']]
print(model.beautify(df))
model.output_file(model.beautify(df),'深证神奇九转指数情况',0)
'''
stock_his_df = model.get_stock_his('1.000001',30,start_date)
ud_df = model.calc_niceturn(stock_his_df,4).tail(5)
ud_df = ud_df.drop(['ud'], axis=1)
#ud_df = ud_df[ud_df['九转'].astype(int).isin([5,6,7, 8, 9,-7,-8,-9])]
ud_df['涨幅'] = ud_df['涨幅'].apply(lambda x: f"{x}%")
ud_df.reset_index(drop=True, inplace=True)       
print(ud_df)
ud_df.to_csv(file_name1, mode='a', header=True, index=False, sep='\t')

#获取上证指数15分钟指标
stock_his_df = model.get_stock_his('1.000001',15,start_date)
ud_df = model.calc_niceturn(stock_his_df,4).tail(3)
ud_df = ud_df.drop(['ud'], axis=1)
#ud_df = ud_df[ud_df['九转'].astype(int).isin([5,6,7, 8, 9,-7,-8,-9])]
ud_df['涨幅'] = ud_df['涨幅'].apply(lambda x: f"{x}%")
ud_df.reset_index(drop=True, inplace=True)       
print(ud_df)
ud_df.to_csv(file_name1, mode='a', header=True, index=False, sep='\t')

#获取深圳综数30分钟指标
stock_his_df = model.get_stock_his('0.399001',30,start_date)
ud_df = model.calc_niceturn(stock_his_df,4).tail(3)
ud_df = ud_df.drop(['ud'], axis=1)
#ud_df = ud_df[ud_df['九转'].astype(int).isin([5,6,7, 8, 9,-7,-8,-9])]
ud_df['涨幅'] = ud_df['涨幅'].apply(lambda x: f"{x}%")
ud_df.reset_index(drop=True, inplace=True)       
print(ud_df)
ud_df.to_csv(file_name1, mode='a', header=True, index=False, sep='\t')

#获取深圳综数15分钟指标
stock_his_df = model.get_stock_his('0.399001',15,start_date)
ud_df = model.calc_niceturn(stock_his_df,4).tail(3)
ud_df = ud_df.drop(['ud'], axis=1)
#ud_df = ud_df[ud_df['九转'].astype(int).isin([5,6,7, 8, 9,-7,-8,-9])]
ud_df['涨幅'] = ud_df['涨幅'].apply(lambda x: f"{x}%")
ud_df.reset_index(drop=True, inplace=True)       
print(ud_df)
ud_df.to_csv(file_name1, mode='a', header=True, index=False, sep='\t')
'''

# 获取热榜前100
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
    df['涨幅'] = df['涨幅'].apply(lambda x: f"{x}%")
    df = df.drop(columns=['时间'])  # 删除 'rc' 列
    print(model.beautify(df))
    model.output_file(df, '热榜100短期神奇指数低点')
