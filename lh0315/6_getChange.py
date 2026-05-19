import requests
import json
import pandas as pd
import time
import akshare as ak
import datetime
import numpy as np
import myLib

class MyClass:
    #获取异动股票
    def get_stock_changes(self,type):
        # 构造请求URL
        if type == 0:
            pageindex = 2
        else:
            pageindex = 4

        parsed_data = []
        for i in range(0,pageindex):
            if type == 0:
                url = f'https://push2ex.eastmoney.com/getAllStockChanges?type=8201&8202&ut=7eea3edcaed734bea9cbfc24409ed989&pageindex={i}&pagesize=64&dpt=wzchanges&_=1734755690954'
            else:
                url = f'https://push2ex.eastmoney.com/getAllStockChanges?type=8204&ut=7eea3edcaed734bea9cbfc24409ed989&pageindex={i}&pagesize=64&dpt=wzchanges&_=1734755690954'
            response_data = requests.get(url)
            try:
                data = response_data.json()['data']['allstock']
                for item in data:
                    stock_data = {
                        '代码': item['c'],
                        '名称': item['n'].ljust(4, '：'), # 假设你想要在名称后面添加冒号和空格 ——
                        '涨幅': round(float(item['i'].split(",")[0])*100,2)
                    }
                    parsed_data.append(stock_data)
            except:
                print('error')
        df = pd.DataFrame(parsed_data)
        df = df[df['代码'].apply(lambda x: x.startswith(('30', '60', '0')))]
        df = df[~df['名称'].str.contains('ST')]
        df = df.drop_duplicates(subset=['代码', '名称'])
        return df


pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度
pd.set_option('display.colheader_justify', 'center')
current_time = datetime.datetime.now().time()
if current_time >= datetime.datetime.strptime('11:00:00', '%H:%M:%S').time():
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    myclass = MyClass()
    model = myLib.MyLib()

    df = myclass.get_stock_changes(1)
    df = df[df['涨幅'] < 1]
    df = df.head(30)
    # 获取九转
    stock_codes = df['代码'].tolist()
    start_date = model.get_trade_dates(1).iloc[0, 0]
    nineturn_df = model.get_stock_nineturn(stock_codes, start_date,5)
    # 获取标签
    labels_df = model.get_stock_label(stock_codes)
    # 合并
    df = pd.merge(df, nineturn_df, on='代码', how='left')
    df = pd.merge(df, labels_df, on='代码', how='left')
    df = df[~df['标签'].str.contains('天').fillna(False) & ~df['标签'].str.contains('板').fillna(False)]
    df = df.drop(columns=['时间'])
    df = df.drop(columns=['收盘'])
    df = df[df['九转'] < 4]
    df['涨幅'] = df['涨幅'].apply(lambda x: f"{x}%")
    df.reset_index(drop=True, inplace=True)  # 删除索引列并重置索引
    print(model.beautify(df))
    model.output_file(df,'异动股票信息(加速下跌、高台跳水+涨幅小于1)')

