import re
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
    def get_change_tolal(self):
        url = f'https://push2ex.eastmoney.com/getStockCountChanges?type=4,8,16,32,64,128,8193,8194,8201,8204,8202,8203,8207,8208,8209,8210,8211,8212,8213,8214,8215,8216&cb=jQuery35105441543852474179_1742731022024&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wzchanges&_=1742731022025'
        response_data = requests.get(url)
        response_data = response_data.content.decode('utf-8')
        json_str = re.search(r'\((.*?})\)', response_data).group(1)
        try:
            json_str = json.loads(json_str)
            data = json_str['data']['ydlist']
            result = {
                '异动总览' : 
                f" 竞价上涨: {data[12]['ct']}, "         #8207,       
                    f" 竞价下跌: {data[13]['ct']}, "         #8208, 
                #f" 封涨停板: {data[0]['ct']}, "          #4                                                             
                #f" 封跌停板: {data[1]['ct']}, "          #8,       
                #f" 打开涨停: {data[2]['ct']}, "          #16,   
                #f" 打开跌停: {data[3]['ct']}, "          #32,         
                #f" 有大买盘: {data[4]['ct']}, "          #64,         
                #f" 有大卖盘: {data[5]['ct']}, "          #128,        
                #f" 大笔买入: {data[6]['ct']}, "          #8193,       
                #f" 大笔卖出: {data[7]['ct']}, "          #8194,       
                    f" 火箭发射: {data[8]['ct']}, "          #8201,       
                    f" 加速下跌: {data[9]['ct']}, "          #8204,       
                    f" 快速反弹: {data[10]['ct']}, "         #8202,       
                    f" 高台跳水: {data[11]['ct']}, "         #8203,            
                #f" 高开5日线: {data[14]['ct']}, "        #8209,       
                #f" 低开5日线: {data[15]['ct']}, "        #8210,       
                #f" 向上缺口: {data[16]['ct']}, "         #8211,       
                #f" 向下缺口: {data[17]['ct']}, "         #8212,       
                #f" 60日新高: {data[18]['ct']}, "         #8213,       
                #f" 60日新低: {data[19]['ct']}, "         #8214,       
                #f" 60日大幅上涨: {data[20]['ct']}, "     #8215,       
                #f" 60日大幅下跌: {data[21]['ct']}"       #8216, 
            }
            return pd.DataFrame(result, index=[0])
        except:
            return pd.DataFrame()

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

    df = myclass.get_change_tolal()
    print(model.beautify(df))
    model.output_file(df,'异动股票信息',output_stock=0)

    df = myclass.get_stock_changes(1)
    df = df[df['涨幅'] < 1]
    df = df.head(30)
    # 获取九转
    stock_codes = df['代码'].tolist()
    start_date = model.get_trade_dates(1).iloc[0, 0]
    #nineturn_df = model.get_stock_nineturn(stock_codes, start_date,5)
    nineturn_df = pd.DataFrame()
    # 获取标签
    labels_df = model.get_stock_label(stock_codes)
    # 合并
    if not nineturn_df.empty and '代码' in nineturn_df.columns:
        df = pd.merge(df, nineturn_df, on='代码', how='left')
    df = pd.merge(df, labels_df, on='代码', how='left')
    df = df[~df['标签'].str.contains('天').fillna(False) & ~df['标签'].str.contains('板').fillna(False)]
    if '时间' in nineturn_df.columns:
        df = df.drop(columns=['时间'])
    if '收盘' in nineturn_df.columns:        
        df = df.drop(columns=['收盘'])
    if '成交量' in nineturn_df.columns: 
        df = df.drop(['成交量'], axis=1)
    if '九转' in nineturn_df.columns:
        df = df[df['九转'] < 4]
    df['涨幅'] = df['涨幅'].apply(lambda x: f"{x}%")
    df.reset_index(drop=True, inplace=True)  # 删除索引列并重置索引
    print(model.beautify(df))
    model.output_file(df,'异动股票信息(加速下跌、高台跳水+涨幅小于1)')

