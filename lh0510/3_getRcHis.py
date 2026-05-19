import requests
import json
import akshare as ak
import pandas as pd
import datetime
import time
import myLib
import getStockInfo
import tools

print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))                   
pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度            
pd.set_option('display.colheader_justify', 'center')

# 创建Popularity类的实例
model = myLib.MyLib()
# 获取热榜前350名股票 (去掉涨幅超9%的股票)
df = model.get_cond_popu_stocks(250) #350
df = df[df['代码'].str.startswith(('30', '00', '60'))]
df = df[~df['名称'].str.contains('ST')]

df3 = df[['代码','热榜']].rename(columns={'代码':'stock_code','热榜':'pop_rank'})
df3['trade_date'] = datetime.date.today().strftime('%Y%m%d')
tools.Tools.db_upsert(df3, 'stock_pop', 'stock_code', 'trade_date')

df = df.drop(columns=['热榜'])
df2 = model.get_raise_stocks(500)

df = df[~df['代码'].isin(df2['代码'])]

# 筛选近期涨幅小于15%或涨停过的股票
stock_codes = df['代码'].tolist()
df_raise = model.calc_raise_rate_new(stock_codes)
column_mapping = {'stock_code': '代码', 'support_line': '支撑线', 'resis_line': '压力线', 'is_limitup': '涨停'}
df_raise = df_raise.rename(columns=column_mapping)
df = pd.merge(df_raise, df, on='代码', how='left')
print(df)
df = df[df['支撑线'] < 20]
df = df[((df['支撑线'] < 15) | (df['涨停'].str.contains('T') & df['支撑线'] < 20))]
if not df.empty:
    stock_codes = df['代码'].tolist()
    # 获取热榜信息
    rc_lists = model.calc_popu_rate(stock_codes)
    column_mapping = {'stock_code': '代码', 'avg_hot_1': '热榜', 'rc_raise_1': '热榜1日变动', 'rc_raise_3': '热榜3日变动', 'rc_raise_5': '热榜5日变动'}
    rc_lists = rc_lists.rename(columns=column_mapping)
    df = pd.merge(df, rc_lists, on='代码', how='left')
    # 获取标签
    labels_df = model.get_stock_label(stock_codes)
    # 获取九转数据
    stock_codes2 = df[(df['涨停'].str.contains('F') & 
        ((df['热榜'] < 350) & ((df['热榜1日变动'] > 1000) | (df['热榜3日变动'] > 800) | (df['热榜5日变动'] > 600))) )]['代码'].tolist()
    start_date  = model.get_trade_dates(5).iloc[0,0]
    nine_df = model.get_stock_nineturn(stock_codes2,start_date)
    # 获取股本数据
    stockinfo_df = getStockInfo.GetStockInfo().get_stock_info(stock_codes)
    # 合并数据
    df = pd.merge(df, labels_df, on='代码', how='left')
    if not nine_df.empty:
        df = pd.merge(df, nine_df, on='代码', how='left')
    else:
        df['九转'] = None
    df = pd.merge(df, stockinfo_df, on='代码', how='left')

    df['涨幅'] = pd.to_numeric(df['涨幅'], errors='coerce')
    df = df.dropna(subset=['涨幅'])
    new_order = ['代码', '名称', '涨幅', '支撑线','压力线', '热榜', '热榜1日变动','热榜3日变动','热榜5日变动', '九转', '涨停', '标签','股本','涨停历史']
    df = df[new_order]
    print(df)
    rc_df = df[((df['热榜'] < 350) & ((df['热榜1日变动'] > 1000) | (df['热榜3日变动'] > 800) | (df['热榜5日变动'] > 600)))]
    if not rc_df.empty:
        print('热榜350内+最近热榜飙升超1000+支撑线<15%')
        sorted_df = rc_df.sort_values(by='热榜', ascending=True)
        sorted_df = sorted_df[(sorted_df['支撑线'] < 15)]
        sorted_df['支撑线'] = sorted_df['支撑线'].apply(lambda x: f"{x}%")
        sorted_df['涨幅'] = sorted_df['涨幅'].apply(lambda x: f"{x}%")
        sorted_df['压力线'] = sorted_df['压力线'].apply(lambda x: f"{x}%")
        sorted_df.reset_index(drop=True, inplace=True)  # 删除索引列并重置索引
        sorted_df_F = sorted_df[((sorted_df['涨停'].str.contains('F')))]
        sorted_df_T = sorted_df[((sorted_df['涨停'].str.contains('T')))]
        print(model.beautify(sorted_df_F))
        model.output_file(sorted_df_F,'热榜飙升精选1(非涨停+热榜350内+飙升超1000+支撑线<15%)')
        print(model.beautify(sorted_df_T))
        model.output_file(sorted_df_T,'热榜飙升精选2(涨停+热榜350内+飙升超1000+支撑线<15%)',0)

        print('热榜350内+最近热榜飙升超1000+涨停+压力线超5%')
        sorted_df2 = df.sort_values(by='热榜', ascending=True)
        sorted_df2 = sorted_df2[(sorted_df2['涨停'].str.contains('T')) & (sorted_df2['压力线'] < -5)]
        sorted_df2['支撑线'] = sorted_df2['支撑线'].apply(lambda x: f"{x}%")
        sorted_df2['涨幅'] = sorted_df2['涨幅'].apply(lambda x: f"{x}%")
        sorted_df2['压力线'] = sorted_df2['压力线'].apply(lambda x: f"{x}%")
        sorted_df2.reset_index(drop=True, inplace=True)  # 删除索引列并重置索引
        print(model.beautify(sorted_df2))
        model.output_file(sorted_df2,'热榜飙升精选3(热榜350内+飙升超1000+涨停+压力线超5%)')

    limitup_df = df[df['涨停'].str.contains('T')]
    if not limitup_df.empty:
        pd.options.mode.chained_assignment = None
        limitup_df['涨幅'] = limitup_df['涨幅'].apply(lambda x: f"{x}%")
        limitup_df['压力线'] = limitup_df['压力线'].apply(lambda x: f"{x}%")
        print('热榜350内+涨停+支撑线<20%')
        print(model.beautify(limitup_df))
        model.output_file(limitup_df,'热榜飙升精选4(热榜350内+涨停+支撑线<20%)')
'''
        print('热榜500内+最近热榜飙升超1000+支撑线<15%+今日涨幅<7%+压力线超5%(剔除近期涨停、热门板块)
        sorted_df_F_1 = sorted_df_F[(sorted_df_F['热榜变动'] > 1000) & (sorted_df_F['压力线'] < -5)]
        try:
            file_name3 =  f'{model.data_dir}/data/' + datetime.datetime.now().strftime("%m%d%H") + "_bnk.txt"
            bnk_df = pd.read_csv(file_name3, sep='\t')
            bnks = bnk_df['板块'].unique()
            sorted_df_F_1 = sorted_df_F_1[~sorted_df_F_1['标签'].apply(lambda x: any(bnk in x for bnk in bnks))]
            print(sorted_df_F_1)
            model.output_file(sorted_df_F_1,'热榜500内+最近热榜飙升超1000+支撑线<15%+今日涨幅<7%+压力线超5%(剔除近期涨停、热门板块)', 0)
        except:
            print('没有近期涨停文件')
'''