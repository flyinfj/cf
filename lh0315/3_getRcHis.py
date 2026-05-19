import requests
import json
import akshare as ak
import pandas as pd
import datetime
import time
import myLib
import getStockInfo

print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))                   
pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度            
pd.set_option('display.colheader_justify', 'center')

# 创建Popularity类的实例
model = myLib.MyLib()
# 获取人气前350名股票 (去掉涨幅超9%的股票)
df = model.get_cond_popu_stocks(250) #350
df = df[df['代码'].str.startswith(('30', '00', '60'))]
df2 = model.get_raise_stocks(500)
df = df[~df['代码'].isin(df2['代码'])]

# 筛选近期涨幅小于15%或涨停过的股票
stock_codes = df['代码'].tolist()
df_raise = model.calc_raise_rate_new(stock_codes)
df = pd.merge(df_raise, df, on='代码', how='left')
df = df[df['十日环比'] < 20]
df = df[((df['十日环比'] < 15) | (df['最近涨停'].str.contains('T') & df['十日环比'] < 20))]
if not df.empty:
    stock_codes = df['代码'].tolist()
    # 获取人气信息
    rc_lists = pd.DataFrame([{'代码': code, **model.calc_popu_rate(code).to_dict('records')[0]} for code in stock_codes])
    df = pd.merge(df, rc_lists, on='代码', how='left')
    # 获取标签
    labels_df = model.get_stock_label(stock_codes)
    # 获取九转数据
    start_date  = model.get_trade_dates(5).iloc[0,0]
    nine_df = model.get_stock_nineturn(stock_codes,start_date)
    # 获取股本数据
    stockinfo_df = getStockInfo.GetStockInfo().get_stock_info(stock_codes)
    # 合并数据
    df = pd.merge(df, labels_df, on='代码', how='left')
    df = pd.merge(df, nine_df, on='代码', how='left')
    df = pd.merge(df, stockinfo_df, on='代码', how='left')

    df['涨幅'] = pd.to_numeric(df['涨幅'], errors='coerce')
    df = df.dropna(subset=['涨幅'])
    new_order = ['代码', '名称', '涨幅', '十日环比', '人气排名', '人气排名1日变动','人气排名3日变动','人气排名5日变动', '九转', '最近涨停','最近跌幅', '标签','股本']
    df = df[new_order]

    rc_df = df[((df['人气排名'] < 350) & ((df['人气排名1日变动'] > 1000) | (df['人气排名3日变动'] > 800) | (df['人气排名5日变动'] > 600)))]
    if not rc_df.empty:
        print('排名350内+最近人气飙升超1000+最近涨幅<15%')
        sorted_df = rc_df.sort_values(by='人气排名', ascending=True)
        sorted_df = sorted_df[(sorted_df['十日环比'] < 15)]
        sorted_df['十日环比'] = sorted_df['十日环比'].apply(lambda x: f"{x}%")
        sorted_df['涨幅'] = sorted_df['涨幅'].apply(lambda x: f"{x}%")
        sorted_df['最近跌幅'] = sorted_df['最近跌幅'].apply(lambda x: f"{x}%")
        sorted_df.reset_index(drop=True, inplace=True)  # 删除索引列并重置索引
        sorted_df_F = sorted_df[((sorted_df['最近涨停'].str.contains('F')))]
        sorted_df_T = sorted_df[((sorted_df['最近涨停'].str.contains('T')))]
        print(model.beautify(sorted_df_F))
        model.output_file(sorted_df_F,'人气个股信息1(排名350内+最近人气飙升超1000+最近涨幅<15%)')
        print(model.beautify(sorted_df_T))
        model.output_file(sorted_df_T,'人气个股信息2',0)

        print('排名350内+最近人气飙升超1000+最近涨停+最近跌幅超5%')
        sorted_df2 = df.sort_values(by='人气排名', ascending=True)
        sorted_df2 = sorted_df2[(sorted_df2['最近涨停'].str.contains('T')) & (sorted_df2['最近跌幅'] < -5)]
        sorted_df2['十日环比'] = sorted_df2['十日环比'].apply(lambda x: f"{x}%")
        sorted_df2['涨幅'] = sorted_df2['涨幅'].apply(lambda x: f"{x}%")
        sorted_df2['最近跌幅'] = sorted_df2['最近跌幅'].apply(lambda x: f"{x}%")
        sorted_df2.reset_index(drop=True, inplace=True)  # 删除索引列并重置索引
        print(model.beautify(sorted_df2))
        model.output_file(sorted_df2,'人气个股信息3（人气个股信息1排名350内+最近人气飙升超1000+最近涨停+最近跌幅超5%)')

    limitup_df = df[df['最近涨停'].str.contains('T')]
    if not limitup_df.empty:
        pd.options.mode.chained_assignment = None
        limitup_df['涨幅'] = limitup_df['涨幅'].apply(lambda x: f"{x}%")
        limitup_df['最近跌幅'] = limitup_df['最近跌幅'].apply(lambda x: f"{x}%")
        print('排名350内+最近涨停+最近涨幅<20%')
        print(model.beautify(limitup_df))
        model.output_file(limitup_df,'人气个股信息4(排名350内+最近涨停+最近涨幅<20%)')
'''
        print('排名500内+最近人气飙升超1000+最近涨幅<15%+今日涨幅<7%+最近跌幅超5%(剔除近期涨停、热门板块)
        sorted_df_F_1 = sorted_df_F[(sorted_df_F['排名变动'] > 1000) & (sorted_df_F['最近跌幅'] < -5)]
        try:
            file_name3 =  'E:/python_workspace/cf/data/' + datetime.datetime.now().strftime("%m%d%H") + "_bnk.txt"
            bnk_df = pd.read_csv(file_name3, sep='\t')
            bnks = bnk_df['板块'].unique()
            sorted_df_F_1 = sorted_df_F_1[~sorted_df_F_1['标签'].apply(lambda x: any(bnk in x for bnk in bnks))]
            print(sorted_df_F_1)
            model.output_file(sorted_df_F_1,'排名500内+最近人气飙升超1000+最近涨幅<15%+今日涨幅<7%+最近跌幅超5%(剔除近期涨停、热门板块)', 0)
        except:
            print('没有近期涨停文件')
'''