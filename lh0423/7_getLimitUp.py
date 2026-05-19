import akshare as ak
import pandas as pd
import myLib
from datetime import date,datetime, timedelta
import requests

#获取股票历史数据
def get_stock_his(stock_code, klt,start_date):
    # 构造请求URL
    stock_codes_str = myLib.MyLib().generate_market_code(stock_code)
    end_date = datetime.now().date()
    end_date_str = end_date.strftime('%Y%m%d')
    start_date_str = str(start_date)
    url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={stock_codes_str}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt={klt}&fqt=1&beg={start_date_str}&end={end_date_str}&smplmt=854&lmt=1000000&_='

    response_data = requests.get(url)
    data = response_data.json()['data']['klines']
    stock_codes_name = response_data.json()['data']['name']
    # 初始化结果字典
    parsed_data = []
    for item in data:
        split_data = item.split(',')
        parsed_data.append({
            '代码': response_data.json()['data']['code'],
            '名称': stock_codes_name.ljust(4, '：'),
            '时间': split_data[0],
            '收盘': pd.to_numeric(split_data[2], errors='coerce'),
            '成交量':pd.to_numeric(split_data[5],errors='coerce'),
            '涨幅': pd.to_numeric(split_data[8], errors='coerce')
        })
    df = pd.DataFrame(parsed_data)
    return df

#统计每支股票的涨停次数
def count_stock_limitup(all_limitup_stocks):
    stock_limitup_counts = all_limitup_stocks.groupby('代码').agg({
        'date': ['count', 'min'],
        '名称': 'max'
    }).reset_index()
    stock_limitup_counts.columns = ['代码', '涨停次数', '最早涨停日期', '名称']
    return stock_limitup_counts

pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度
pd.set_option('display.colheader_justify', 'center')
# 获取近期的交易日期
model = myLib.MyLib()
trade_dates = model.get_trade_dates(10,1)
# 获取近期的涨停板数据
all_limitup = model.get_limitup_stocks(trade_dates)
all_limitup = all_limitup[all_limitup['代码'].apply(lambda x: x.startswith(('30', '60', '0')))]
# 统计每支股票的涨停次数、最早涨停时间
all_limitup_num = count_stock_limitup(all_limitup)
all_limitup_num = all_limitup_num[all_limitup_num['涨停次数']<3]
all_limitup_num = all_limitup_num[~(all_limitup_num['最早涨停日期']<=trade_dates['trade_date'].iloc[-7])]
all_limitup_num = all_limitup_num[~(all_limitup_num['最早涨停日期']>=trade_dates['trade_date'].iloc[-2])]
# 去掉涨停以来涨幅超过5%的股票
file_name = f'{model.filedir_database}/stock_spot.db'
his_all_df = pd.read_csv(file_name)
his_all_df['代码'] = his_all_df['代码'].astype(str).str.zfill(6)
for index, row in all_limitup_num.iterrows():
    code = row['代码']
    limitup_date = row['最早涨停日期']
    limitup_count = row['涨停次数']
    limitup_df = his_all_df[(his_all_df['代码'] == code)]
    limitup_df1 = limitup_df[limitup_df['时间'] == limitup_date]
    if not limitup_df1.empty:
        limitup_price = limitup_df1['最新价'].values[0]
        c_df = limitup_df.iloc[-1]
        c = c_df['最新价']
        if (c / limitup_price) >= 0.95 + (limitup_count - 1) * 0.1:
            all_limitup_num.drop(index, inplace=True)
    else:
        all_limitup_num.drop(index, inplace=True)

# 统计涨停分析数据
stats_results = []
for index, row in all_limitup_num.iterrows():
    stock_code = row['代码']
    start_time = row['最早涨停日期']
    df = model.get_stock_his(stock_code, 5, start_time)
    total = df['成交量'].sum()
    result = {
        '代码': stock_code,
        '名称': row['名称'],
        '涨停时间': start_time,
        '涨停次数': row['涨停次数'],
        '涨<1量': round(100 * df[df['涨幅'] < 1]['成交量'].sum() / total, 0),
        '涨>3量': round(100 * df[df['涨幅'] >= 3]['成交量'].sum()/total,0),
        '涨>2量': round(100 * df[(df['涨幅'] >= 2) & (df['涨幅'] < 3)]['成交量'].sum() / total, 0),
        '涨>1量': round(100 * df[(df['涨幅'] >= 1) & (df['涨幅'] < 2)]['成交量'].sum() / total, 0),
    }
    stats_results.append(result)
stats_df = pd.DataFrame(stats_results)
stats_df = stats_df[stats_df['涨<1量'] <= 70]

# 获取涨幅
stock_codes = stats_df['代码'].tolist()
# 获取九转
start_date = trade_dates['trade_date'].iloc[0]
nineturn_df = model.get_stock_nineturn(stock_codes, start_date)
# 获取标签
labels = model.get_stock_label(stock_codes)
# 合并
stats_df = pd.merge(stats_df, nineturn_df, on='代码', how='left')
stats_df = pd.merge(stats_df, labels, on='代码', how='left')
stats_df = stats_df.drop(['时间'], axis=1)
stats_df = stats_df.drop(['收盘'], axis=1)
stats_df = stats_df.drop(['成交量'], axis=1)
sorted_df = stats_df.sort_values(by=['涨停时间', '涨<1量'], ascending=[True, False])
print(model.beautify(sorted_df))
model.output_file(sorted_df,'涨幅后出货少')



