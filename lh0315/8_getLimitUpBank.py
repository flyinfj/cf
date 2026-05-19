import akshare as ak
import pandas as pd
import myLib
from datetime import date,datetime, timedelta
import requests

#获取今日涨幅情况
def get_limitup_summary(start_date):
    v_start_date = datetime.strptime(str(start_date), "%Y%m%d").strftime("%Y-%m-%d")
    url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?source=SECURITIES&client=APP&reportName=RPT_INTSELECTION_LIMITHIS&columns=TRADE_DATE,LIMIT_NUMBERS,NATURAL_LIMIT,DAILY_LIMIT,TOUCH_LIMIT,SEALING_RATE,NATURAL_LIMIT_YES,LIMIT_PER_YES,POSITION_SUGGESTION,MONEYMAKING_EFFECT,SEALING_RATE_YES,LIMIT_DOWN_NUM,CJDT_NUM,DT_FBL&filter=(TRADE_DATE<\'{v_start_date}\')&pageNumber=1&pageSize=1&sortTypes=-1&sortColumns=TRADE_DATE'
    response_data = requests.get(url)
    data = response_data.json()
    if 'result' in data and 'data' in data['result']:
        stock_data = data['result']['data']
        LIMIT_NUMBERS_YES = stock_data[0]['LIMIT_NUMBERS']
        LIMIT_PER_YES_YES = round(stock_data[0]['LIMIT_PER_YES'],2)
        LIMIT_DOWN_NUM_YES = stock_data[0]['LIMIT_DOWN_NUM']
        url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?source=SECURITIES&client=APP&reportName=RPT_CUSTOM_INTSELECTION_MONITOR&columns=ALL&filter=(IS_DECLINELIMITED="1")&pageNumber=1&pageSize=100&sortTypes=-1&sortColumns=ZTJY'
        response_data = requests.get(url)
        data = response_data.json()
        if 'result' in data and 'data' in data['result']:
            LIMIT_DOWN_NUM = len(data['result']['data'])
        url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?source=SECURITIES&client=APP&reportName=RPT_CUSTOM_INTSELECTION_LIMIT&columns=LIMIT_NUMBERS,NATURAL_LIMIT,DAILY_LIMIT,TOUCH_LIMIT,SEALING_RATE,NATURAL_LIMIT_YES,LIMIT_PER_YES,SEALING_RATE_YES'
        response_data = requests.get(url)
        data = response_data.json()
        if 'result' in data and 'data' in data['result']:
            stock_data = data['result']['data']
            security_codes = [{'建议仓位': f'{stock_data[0]['POSITION_SUGGESTION']}',
                               '涨停数(今/昨)': f'{stock_data[0]['LIMIT_NUMBERS']}/{LIMIT_NUMBERS_YES}',
                               '封板率(今/昨)': f'{stock_data[0]['SEALING_RATE']}%/{stock_data[0]['SEALING_RATE_YES']}%',
                               '涨幅(今/昨)': f'{round(stock_data[0]['LIMIT_PER_YES'],2)}%/{LIMIT_PER_YES_YES}%',
                               '跌停数(今/昨)': f'{LIMIT_DOWN_NUM}/{LIMIT_DOWN_NUM_YES}',
                               }]
        df = pd.DataFrame(security_codes, columns=['建议仓位', '涨停数(今/昨)', '封板率(今/昨)', '涨幅(今/昨)','跌停数(今/昨)'])
        return df
    else:
        print("未找到股票信息")

# 获取强势板块
def get_limitup_sector():
    url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?source=SECURITIES&client=APP&reportName=RPT_CUSTOM_INTSELECTION_RELATEDBOARD&pageNumber=1&pageSize=20'
    response_data = requests.get(url)
    data = response_data.json()
    if 'result' in data and 'data' in data['result']:
        stock_data = data['result']['data']
        security_codes = [
            {'板一/天/板数': f'{stock_data[0]['BOARD_NAME']}/{stock_data[0]['HLIMITE_NUM']}/{stock_data[0]['STOCK_HIGH']}',
             '板二/天/板数': f'{stock_data[1]['BOARD_NAME']}/{stock_data[1]['HLIMITE_NUM']}/{stock_data[1]['STOCK_HIGH']}',
             '板三/天/板数': f'{stock_data[2]['BOARD_NAME']}/{stock_data[2]['HLIMITE_NUM']}/{stock_data[2]['STOCK_HIGH']}',
             '板四/天/板数': f'{stock_data[3]['BOARD_NAME']}/{stock_data[3]['HLIMITE_NUM']}/{stock_data[3]['STOCK_HIGH']}',
             '板五/天/板数': f'{stock_data[4]['BOARD_NAME']}/{stock_data[4]['HLIMITE_NUM']}/{stock_data[4]['STOCK_HIGH']}'
             }]
        df = pd.DataFrame(security_codes, columns=['板一/天/板数', '板二/天/板数', '板三/天/板数', '板四/天/板数', '板五/天/板数'])
        return df
    else:
        print("未找到股票信息")

#获取龙头股
def get_limitup_leading():
    url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?source=SECURITIES&client=APP&reportName=RPTA_CUSTOM_APP_CONCEPTLIST&columns=ALL'
    response_data = requests.get(url)
    data = response_data.json()
    if 'result' in data and 'data' in data['result']:
        stock_data = data['result']['data']
        parsed_data = []
        for item in stock_data:
            parsed_data.append( {
                '代码': item['SECURITY_CODE'],
                '名称': item['SECURITY_NAME_ABBR'],
                '板块': item['BOARD_NAME'],
                '板数': item['NDAYS_NLIMITE']
            })
        df = pd.DataFrame(parsed_data)
        return df
    else:
        print("未找到股票信息")

#获取连板天梯
def get_limitup_cons():
    url = f'https://push2.eastmoney.com/api/qt/updown/continuouslimitup/get?fields=f1,f2,f3,f4,f5&fid=f4&ut=f057cbcbce2a86e2866ab8877db1d059&invt=3'
    response_data = requests.get(url)
    data = response_data.json()['data']
    if data is not None:
        results = []
        for item, content in data.items():
            success_count = len(content['success'])
            fail_count = len(content['fail'])
            if int(item) >0:
                results.append({
                    '昨板数': int(item),
                    '今板数': f'->{int(item) + 1}',
                    '涨停数': success_count+fail_count,
                    '连板成功': success_count,
                    '连板成功率': f'{round(success_count/(success_count+fail_count)*100,2)}%'
                })
        df = pd.DataFrame(results)
        return df
    else:
        return None

#获取三板+个股
def get_limitup_hight():
    url = f'https://push2.eastmoney.com/api/qt/updown/continuouslimitup/get?fields=f1,f2,f3,f4,f5&fid=f4&ut=f057cbcbce2a86e2866ab8877db1d059&invt=3'
    response_data = requests.get(url)
    data = response_data.json()['data']
    if data is not None:
        results = []
        for item, content in data.items():
            if int(item) >= 2:
                for item2, content2 in content.items():
                    for content3 in content2:
                        split_data = content3.split(',')
                        results.append({
                            '昨板数': int(item),
                            '今板数': f'->{int(item) + 1}',
                            '成功': item2,
                            '代码': split_data[0],
                            '名称': split_data[2],
                            '涨幅': f'{split_data[4]}%'
            })
        df = pd.DataFrame(results)
        return df
    else:
        return None

def get_limitup_pre(start_date):
    v_start_date = datetime.strptime(str(start_date), "%Y%m%d").strftime("%Y-%m-%d")
    url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?source=SECURITIES&client=APP&reportName=RPT_INTSELECTION_PRETODAY&columns=SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE,CHANGE_RATE,PRE_CONTINUS_UPLIMITS,PRE_UPLIMITS_NUM,IS_DOWNLIMIT,DOWNLIMIT_RATIO,CONTINUS_UPLIMITS,UPLIMITS_NUM&filter=(TRADE_DATE=\'{v_start_date}\')'
    response_data = requests.get(url)
    data = response_data.json()
    if 'result' in data and 'data' in data['result']:
        stock_data = data['result']['data']
        results = []
        for item in stock_data:
            results.append({
                '时间': start_date,
                '代码': item['SECURITY_CODE'],
                '名称': item['SECURITY_NAME_ABBR'],
                '昨板数': item['PRE_CONTINUS_UPLIMITS'],
                '今板数': item['CONTINUS_UPLIMITS'],
                '涨幅': round(item['CHANGE_RATE'],2),
                '是否涨停': item['IS_DOWNLIMIT']
            })
        df = pd.DataFrame(results)
        return df
    else:
        print("未找到股票信息")

import pandas as pd

# 创建示例数据
data1 = {
    '代码': ['000001'] * 30,
    '时间': pd.date_range(start='2024-01-01', periods=30, freq='B'),
    '收盘价': [100] * 30  # 初始收盘价为100
}
data2 = {
    '代码': ['000001'] * 30,
    '时间': pd.date_range(start='2024-01-01', periods=30, freq='B'),
    '收盘价': [100] * 30  # 初始收盘价为100
}

# 异动规则判断函数
def calc_alert_days(stock_codes):
    start_time = myLib.MyLib().get_trade_dates(30,0)
    v_start_date = start_time.iloc[0,0]
    df_z1 = myLib.MyLib().get_stock_his('1.000001',101,v_start_date)
    df_z2 = myLib.MyLib().get_stock_his('0.399001', 101, v_start_date)
    df_z3 = myLib.MyLib().get_stock_his('0.399006', 101, v_start_date)
    file_name = f"{myLib.MyLib().filedir_database}/stock_spot.db"
    df_his = pd.read_csv(file_name)
    df_his['代码'] = df_his['代码'].astype(str).str.zfill(6)
    result = []
    for stock_code in stock_codes:
        # 过滤出对应的股票数据
        stock_data = df_his[df_his['代码'] == stock_code]
        max_date = stock_data['时间'].max()
        df = stock_data.tail(31)
        # 初始化变量
        prices = df['最新价'].iloc[-31:].tolist()  # 存储每天的价格变化
        if stock_code.startswith('60'):
            prices_z = df_z1['收盘'].iloc[-31:].tolist()
        if stock_code.startswith('00'):
            prices_z = df_z2['收盘'].iloc[-31:].tolist()
        if stock_code.startswith('30'):
            prices_z = df_z3['收盘'].iloc[-31:].tolist()
        days = 0  # 计算天数
        alert_days_10 = None  # 10天规则触发天数
        alert_days_30 = None  # 30天规则触发天数
        # 模拟每天的价格变化
        while days < 20:
            # 判断是否触发10天规则
            if alert_days_10 is None and prices[-11]>0:
                for i in range(8,11):
                    deviation_10 = (prices[-1] / prices[-i] - 1) * 100  # 当前价格与10天前价格的涨幅
                    deviation_10_z = (prices_z[-1] / prices_z[-i] - 1) * 100
                    if deviation_10-deviation_10_z >= 100:
                        alert_days_10 = days
                        break
            # 判断是否触发30天规则
            if alert_days_30 is None and prices[-31]>0:
                for i in range(12, 31):
                    deviation_30 = (prices[-1] / prices[-i] - 1) * 100  # 当前价格与30天前价格的涨幅
                    deviation_30_z = (prices_z[-1] / prices_z[-i] - 1) * 100
                    if deviation_30-deviation_30_z >= 200:
                        alert_days_30 = days
                        break
            # 如果两个规则都已触发，退出循环
            if alert_days_10 is not None and alert_days_30 is not None:
                break
            # 增加数据
            days += 1
            if stock_code.startswith('30'):
                new_price = round(prices[-1] * 1.20, 2)  # 每天涨幅20%
            else:
                new_price = round(prices[-1] * 1.10, 2)  # 每天涨幅10%
            prices.append(new_price)  # 更新价格列表
            new_price_z = prices_z[-1]
            prices_z.append(new_price_z)
        result.append({
            '代码': stock_code,
            '警告': f'{alert_days_10}/{alert_days_30}/{max_date}'
        })
    df = pd.DataFrame(result)
    return df

pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度
pd.set_option('display.colheader_justify', 'center')
# 获取近期的交易日期
model = myLib.MyLib()
trade_dates = model.get_trade_dates(1,1)
v_trade_dates = trade_dates.iloc[0,0]
df = get_limitup_summary(v_trade_dates)
print(df)
model.output_file(df,'涨停股统计信息',0)

df = get_limitup_sector()
print(df)
model.output_file(df,'强势板块信息',0)

df = get_limitup_leading()
stock_codes = df['代码'].tolist()
labels = model.get_stock_label(stock_codes)
df = pd.merge(df, labels, on='代码', how='left')
errors = calc_alert_days(stock_codes)
df = pd.merge(df, errors, on='代码', how='left')
print(model.beautify(df))
model.output_file(model.beautify(df),'龙头股信息',0)

df = get_limitup_cons()
df = df.sort_values(by='昨板数', ascending=False)
df.reset_index(drop=True, inplace=True)
print(model.beautify(df))
model.output_file(model.beautify(df),'连板天梯信息',0)

df = get_limitup_hight()
stock_codes = df['代码'].tolist()
labels = model.get_stock_label(stock_codes)
df = pd.merge(df, labels, on='代码', how='left')
errors = calc_alert_days(stock_codes)
df = pd.merge(df, errors, on='代码', how='left')
df = df.sort_values(by=['昨板数', '成功'], ascending=[False, True])
df.reset_index(drop=True, inplace=True)
print(model.beautify(df))
model.output_file(df,'个股连板情况',0)

#获取昨天的的涨停数据到数据库中
file_name = f'{model.filedir_database}/days_limitup_pre.db'
his_all_df = pd.read_csv(file_name)
start_time = his_all_df['时间'].max()
trade_dates = model.get_trade_dates(10)
filter_datas = trade_dates[trade_dates['trade_date'] > start_time]
for index, row in filter_datas.iterrows():
    start_time = row['trade_date']
    df = get_limitup_pre(start_time)
    if df is not None:
        df.to_csv(file_name, mode='a', header=False, index=False)
#统计涨停次数
file_name = f'{model.filedir_database}/days_limitup_pre.db'
df = pd.read_csv(file_name)
df['代码'] = df['代码'].astype(str).str.zfill(6)
count_df = df.groupby('代码').agg(
    涨停数=('涨幅', 'size'),  # 计算每个代码的出现次数
    第二天涨次数=('涨幅', lambda x: (x > 0).sum()),  # 统计涨幅大于 0 的次数
    平均涨幅=('涨幅', 'mean')  # 计算涨幅的平均值
).reset_index()
count_df['平均涨幅'] = (count_df['平均涨幅']).round(1).astype(str) + '%'
count_df = count_df.sort_values(by='涨停数', ascending=False)
count_df.insert(0, '涨停排序', range(1, len(count_df) + 1))
output_file_name = f'{model.filedir_database}/days_limitup_count.db'
count_df.to_csv(output_file_name, mode='w', header=True, index=False, sep='\t')