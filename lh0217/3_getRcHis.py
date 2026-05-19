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
df = model.get_cond_popu_stocks(150) #350
df = df[df['代码'].str.startswith(('30', '00', '60'))]
df2 = model.get_raise_stocks(200)
df = df[~df['代码'].isin(df2['代码'])]

# 筛选近期涨幅小于15%
stock_codes = df['代码'].tolist()
df_raise = pd.DataFrame([{'代码': code, **model.calc_raise_rate(code).to_dict('records')[0]} for code in stock_codes])
df_raise.drop('涨幅', axis=1, inplace=True)
df = pd.merge(df_raise, df, on='代码', how='left')
df = df[(df['十日环比'] < 15) | ((df['最近涨停'].str.contains('T')) & (df['最近跌幅'] < -5))]

if not df.empty:
    # 筛选人气飙升超1000
    stock_codes = df['代码'].tolist()
    rc_lists = pd.DataFrame([{'代码': code, **model.calc_popu_rate(code).to_dict('records')[0]} for code in stock_codes])
    df = pd.merge(df, rc_lists, on='代码', how='left')
    df = df[((df['人气排名'] < 350) & ((df['排名变动'] > 1000) | (df['排名变动3'] > 800) | (df['排名变动5'] > 600)))]
    if not df.empty:
        # 获取标签
        stock_codes = df['代码'].tolist()
        labels_df = model.get_stock_label(stock_codes)

        #获取九转数据
        start_date  = datetime.datetime.strptime(model.get_trade_dates(5).iloc[0], "%Y%m%d")
        nine_df = model.get_stock_nineturn(stock_codes,start_date)

        # 获取股本数据
        stockinfo_df = getStockInfo.GetStockInfo().get_stock_info(stock_codes)

        # 合并数据
        df = pd.merge(df, labels_df, on='代码', how='left')
        df = pd.merge(df, nine_df, on='代码', how='left')
        df = pd.merge(df, stockinfo_df, on='代码', how='left')

        df['标签'] = df['标签'].apply(lambda x: str(x).ljust(30))
        df['涨幅'] = pd.to_numeric(df['涨幅'], errors='coerce')
        df = df.dropna(subset=['涨幅'])
        new_order = ['代码', '名称', '涨幅', '十日环比', '人气排名', '排名变动','排名变动3','排名变动5', 'cumu_ud', '最近涨停', '最近跌幅', '标签','股本']
        df = df[new_order]

        #输出数据：排名500内+最近人气飙升超1000+最近涨幅<15%+今日涨幅<7%(去昨日首板)
        sorted_df = df.sort_values(by='人气排名', ascending=True)
        sorted_df = sorted_df[(sorted_df['十日环比'] < 15)]
        sorted_df['十日环比'] = sorted_df['十日环比'].apply(lambda x: f"{x}%")
        sorted_df['涨幅'] = sorted_df['涨幅'].apply(lambda x: f"{x}%")
        sorted_df['最近跌幅'] = sorted_df['最近跌幅'].apply(lambda x: f"{x}%")
        sorted_df.reset_index(drop=True, inplace=True)  # 删除索引列并重置索引
        sorted_df_F = sorted_df[((sorted_df['最近涨停'].str.contains('F')))]
        sorted_df_T = sorted_df[((sorted_df['最近涨停'].str.contains('T')))]
        print(sorted_df_F)
        model.output_file(sorted_df_F,'排名500内+最近人气飙升超1000+最近涨幅<15%+今日涨幅<7%(去昨日首板)')
        print(sorted_df_T)
        model.output_file(sorted_df_T,'',0)

        #输出数据：排名500内+最近人气飙升超1000+最近涨停+最近跌幅超5%
        sorted_df2 = df.sort_values(by='人气排名', ascending=True)
        sorted_df2 = sorted_df2[((sorted_df2['最近涨停'].str.contains('T')) & (sorted_df2['最近跌幅'] < -5))]
        sorted_df2['十日环比'] = sorted_df2['十日环比'].apply(lambda x: f"{x}%")
        sorted_df2['涨幅'] = sorted_df2['涨幅'].apply(lambda x: f"{x}%")
        sorted_df2['最近跌幅'] = sorted_df2['最近跌幅'].apply(lambda x: f"{x}%")
        sorted_df2.reset_index(drop=True, inplace=True)  # 删除索引列并重置索引
        print(sorted_df2)
        model.output_file(sorted_df2,'排名500内+最近人气飙升超1000+最近涨停+最近跌幅超5%')

        #输出数据：排名500内+最近人气飙升超1000+最近涨幅<15%+今日涨幅<7%+最近跌幅超5%
        sorted_df_F_1 = sorted_df_F[(sorted_df_F['排名变动'] > 1000)]
        try:
            file_name3 =  'E:/python_workspace/cf/data/' + datetime.datetime.now().strftime("%m%d%H") + "_bnk.txt"
            bnk_df = pd.read_csv(file_name3, sep='\t')
            bnks = bnk_df['板块'].unique()
            sorted_df_F_1 = sorted_df_F_1[~sorted_df_F_1['标签'].apply(lambda x: any(bnk in x for bnk in bnks))]
        except:
            print('没有近期涨停文件')
        print(sorted_df_F_1)
        model.output_file(sorted_df_F_1,'排名500内+最近人气飙升超1000+最近涨幅<15%+今日涨幅<7%(剔除近期涨停、热门板块)',0)