import requests
import json
import pandas as pd
import time
import akshare as ak
import datetime
import numpy as np
import myLib

class MyClass:
    def get_cold_stocks(self, market,turnoverrate,volume_ratio):
        # 构建表单数据
        if market == 1:
            filter_str = f'(MARKET IN ("上交所主板","深交所主板"))(POPULARITY_RANK>=2000)(POPULARITY_RANK<=6000)(CHANGERATE_3DAYS<10)(TURNOVERRATE>={turnoverrate})(VOLUME_RATIO>={volume_ratio})'
        else:
            filter_str = f'(MARKET IN ("深交所创业板"))(POPULARITY_RANK>=2000)(POPULARITY_RANK<=6000)(CHANGERATE_3DAYS<10)(TURNOVERRATE>={turnoverrate})(VOLUME_RATIO>={volume_ratio})'
        files = {
            'type': (None, 'RPTA_SECURITY_STOCKSELECT'),
            'sty': (None, 'SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,NEW_PRICE,CHANGE_RATE,POPULARITY_RANK,TURNOVERRATE,VOLUME_RATIO,DEAL_AMOUNT'),
            'filter': (None, filter_str),
            'p': (None, '1'),
            'ps': (None, 200),
            'sr': (None, '-1'),
            'st': (None, 'CHANGE_RATE'),
            'source': (None, 'SELECT_SECURITIES'),
            'client': (None, 'APP')
        }
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://emrnweb.eastmoney.com',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://emrnweb.eastmoney.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }

        # 发送POST请求
        url = "https://datacenter.eastmoney.com/stock/selection/api/data/get/"
        response = requests.post(url, headers=headers, files=files)

        # 检查响应
        if response.status_code == 200:
            # 解析响应的JSON数据
            data = response.json()

            # 检查数据是否包含股票信息
            if 'result' in data and 'data' in data['result']:
                # 提取股票信息
                stock_data = data['result']['data']

                # 提取SECURITY_CODE、SECURITY_NAME_ABBR列
                security_codes = [{'代码': item['SECURITY_CODE'],
                                   '名称': item['SECURITY_NAME_ABBR'].ljust(4, '：'),
                                   '涨幅': item['CHANGE_RATE'],
                                   '人气': item['POPULARITY_RANK'],
                                   '换手': item['TURNOVERRATE'],
                                   '量比': item['VOLUME_RATIO'],
                                   '成交量': round(item['DEAL_AMOUNT']/100000000,2)}
                                  for item in stock_data]

                # 创建DataFrame
                df = pd.DataFrame(security_codes, columns=['代码', '名称', '涨幅', '人气', '换手', '量比', '成交量'])

                # 打印DataFrame
                return df
            else:
                print("未找到股票信息")
        else:
            print("请求失败，状态码：", response.status_code)

print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度
pd.set_option('display.colheader_justify', 'center')

current_time = datetime.datetime.now().time()
if current_time >= datetime.datetime.strptime('10:00:00', '%H:%M:%S').time():
    model = myLib.MyLib()
    myclass = MyClass()
    bank_df = model.get_stock_data(['1.000852'])
    df1 = myclass.get_cold_stocks(1,2*bank_df.head(1)['换手'].values[0],1.5*bank_df.head(1)['量比'].values[0])
    bank_df = model.get_stock_data(['0.399006'])
    df2 = myclass.get_cold_stocks(2,2*bank_df.head(1)['换手'].values[0],1.5*bank_df.head(1)['量比'].values[0])
    df1 = df1.dropna(axis=1, how='all')
    df2 = df2.dropna(axis=1, how='all')
    df = pd.concat([df1,df2])
    df = df.sort_values(by='量比', ascending=False)
    df = df.head(30)

    if not df.empty:
        stock_codes = df['代码'].tolist()
        # 获取九转
        start_date = datetime.datetime.strptime(model.get_trade_dates(5).iloc[0], "%Y%m%d")
        nineturn_df = model.get_stock_nineturn(stock_codes, start_date)
        # 获取标签
        labels_df = model.get_stock_label(stock_codes)
        # 合并
        df = pd.merge(df, nineturn_df, on='代码', how='left')
        df = pd.merge(df, labels_df, on='代码', how='left')
        df = df.drop(columns=['时间'])
        df = df.drop(columns=['收盘'])
        print(df)
        model.output_file(df,'人气排名2000+高换手率')