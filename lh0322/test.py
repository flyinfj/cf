import akshare as ak
import pandas as pd
from datetime import datetime
import time
import myLib
from ta.trend import MACD
def calculate_ma(group):
    #print(group)
    ma1 = group['最新价'].iloc[-1]  # 最后一列的值
    ma5 = group['最新价'].iloc[-5:].mean()  # 最后5列的平均值
    ma10 = group['最新价'].iloc[-10:].mean()  # 最后10列的平均值
    ma20 = group['最新价'].iloc[-20:].mean()  # 最后20列的平均值
    ma60 = group['最新价'].iloc[-60:].mean()  # 最后60列的平均值
    max20 = group['最新价'].iloc[-26:-6].max()
    min20 = group['最新价'].iloc[-26:-6].min()
    max60 = group['最新价'].iloc[-66:-26].max()
    min60 = group['最新价'].iloc[-66:-26].min()
    df = pd.Series({
        'ma1': ma1,
        'ma5': ma5,
        'ma10': ma10,
        'ma20': ma20,
        'ma60': ma60,
        'max20': max20,
        'min20': min20,
        'max60': max60,
        'min60': min60
    })
    return df


pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度
pd.set_option('display.colheader_justify', 'center')
#
current_time = datetime.now().time()
if current_time >= datetime.strptime('00:00:00', '%H:%M:%S').time():
    # 获取交易日期
    latest_60_data = myLib.MyLib().get_trade_dates(66,1)

    # 获取A股所有股票的实时数据
    file_name = f'{myLib.MyLib().filedir_database}/stock_real.db'
    new_all_df = pd.read_csv(file_name)
    #new_all_df = ak.stock_zh_a_spot()
    new_all_df['代码'] = new_all_df['代码'].str.replace('sh', '').str.replace('sz', '')
    #new_all_df.to_csv(file_name, mode='w', header=True, index=False)
    new_all_df = new_all_df[new_all_df['代码'].apply(lambda x: x.startswith(('30', '00', '60')))]
    new_all_df = new_all_df[~new_all_df['名称'].astype(str).str.contains('ST', na=False)]
    new_all_df['时间'] =  latest_60_data['trade_date'].iloc[-1]
    #new_order = ['代码', '名称', '时间', '今开', '最高', '最低', '最新价', '成交量', '成交额', '流动股本', '换手率']
    new_order = ['代码', '时间', '最新价']
    new_all_df = new_all_df.reindex(columns=new_order)

    # 获取A股所有股票的历史数据
    file_name = f'{myLib.MyLib().filedir_database}/stock_spot.db'
    his_all_df = pd.read_csv(file_name)
    his_all_df['代码'] = his_all_df['代码'].astype(str).str.zfill(6)
    #his_all_df['时间'] = pd.to_datetime(his_all_df['时间'])
    #his_all_df = his_all_df[~(his_all_df['时间'] == latest_60_data['trade_date'].iloc[-1])]
    #his_all_df.to_csv(file_name, mode='w', header=True, index=False)


    #数据进行计算
    his_all_df = his_all_df[his_all_df['代码'] == '603986']
    his_all_df = his_all_df.sort_values(by=['代码', '时间'], ascending=[True, True])
    stock_group = his_all_df.groupby('代码', as_index=False).apply(calculate_ma, include_groups=False)
    stock_group = stock_group.reset_index()
    #file_name = f'{myLib.MyLib().filedir_database}/stock_stats.db'
    #stock_group.to_csv(file_name, mode='w', header=True, index=False)
    """
    break5  = stock_group[(stock_group['ma1'] > stock_group['ma5']) & (stock_group['ma1'] < stock_group['ma10']) & (stock_group['ma5'] < stock_group['ma10'])].shape[0]
    break10 = stock_group[(stock_group['ma1'] > stock_group['ma10']) & (stock_group['ma1'] < stock_group['ma20']) & (stock_group['ma10'] < stock_group['ma20'])].shape[0]
    break20 = stock_group[(stock_group['ma1'] > stock_group['ma20']) & (stock_group['ma1'] < stock_group['ma60']) & (stock_group['ma20'] < stock_group['ma60'])].shape[0]
    break60 = stock_group[(stock_group['ma1'] > stock_group['ma60']) & (stock_group['ma20'] < stock_group['ma60'])].shape[0]
    max0 = stock_group[(stock_group['ma1'] > stock_group['ma5']) & (stock_group['ma5'] > stock_group['ma10']) &
                       (stock_group['ma10'] > stock_group['ma20'])  & (stock_group['ma20'] > stock_group['ma60'])].shape[0]
    max20  = stock_group[(stock_group['ma1'] > stock_group['max20']) & (stock_group['ma1'] < stock_group['max60'])].shape[0]
    max60  = stock_group[(stock_group['ma1'] > stock_group['max20']) & (stock_group['ma1'] > stock_group['max60'])].shape[0]
    fall5  = stock_group[(stock_group['ma1'] < stock_group['ma5']) & (stock_group['ma1'] > stock_group['ma10']) & (stock_group['ma5'] > stock_group['ma10'])].shape[0]
    fall10 = stock_group[(stock_group['ma1'] < stock_group['ma10']) & (stock_group['ma1'] > stock_group['ma20']) & (stock_group['ma10'] > stock_group['ma20'])].shape[0]
    fall20 = stock_group[(stock_group['ma1'] < stock_group['ma20']) & (stock_group['ma1'] > stock_group['ma60']) & (stock_group['ma20'] > stock_group['ma60'])].shape[0]
    fall60 = stock_group[(stock_group['ma1'] < stock_group['ma60']) & (stock_group['ma20'] > stock_group['ma60'])].shape[0]
    min0 = stock_group[(stock_group['ma1'] < stock_group['ma5']) & (stock_group['ma5'] < stock_group['ma10']) &
                       (stock_group['ma10'] < stock_group['ma20'])  & (stock_group['ma20'] < stock_group['ma60'])].shape[0]
    min20 = stock_group[(stock_group['ma1'] < stock_group['min20']) & (stock_group['ma1'] > stock_group['min60'])].shape[0]
    min60 = stock_group[(stock_group['ma1'] < stock_group['min20']) & (stock_group['ma1'] < stock_group['min60'])].shape[0]
    stat_str1 = (f"突5量: {break5}, 突10量: {break10}, 突20量: {break20}, "
                 f"突60量: {break60}, 多头：{max0}, 新高20: {max20}, 新高60: {max60}")
    print(stat_str1)
    stat_str2 = (f"跌5量: {fall5}, 跌10量: {fall10}, 跌20量: {fall20}, "
                 f"跌60量: {fall60}, 空头：{min0}, 新低20: {min20}, 新低60: {min60}\n")
    print(stat_str2)

    now = datetime.now()
    result = {
        '时间'  : [datetime.now().strftime("%Y%m%d")],
        '新低60': [min60],
        '新低20': [min20],
        '空头'  : [min0],
        '跌60量': [fall60],
        '跌20量': [fall20],
        '跌10量': [fall10],
        '跌5量' : [fall5],
        '突5量' : [break5],
        '突10量': [break10],
        '突20量': [break20],
        '突60量': [break60],
        '多头'  : [max0],
        '新高20': [max20],
        '新高60': [max60]
    }
    """
    stock_total = len(stock_group)
    max20 = stock_group[(stock_group['ma1'] > stock_group['max20']) & (stock_group['ma1'] < stock_group['max60'])].shape[0]
    max60 = stock_group[(stock_group['ma1'] > stock_group['max20']) & (stock_group['ma1'] > stock_group['max60'])].shape[0]
    h5_10_20 = stock_group[(stock_group['ma5'] > stock_group['ma10']) & (stock_group['ma10'] > stock_group['ma20'])].shape[0]
    h5_20_10 = stock_group[(stock_group['ma5'] > stock_group['ma20']) & (stock_group['ma20'] > stock_group['ma10'])].shape[0]
    m10_5_20 = stock_group[(stock_group['ma10']> stock_group['ma5'])  & (stock_group['ma5']  > stock_group['ma20'])].shape[0]
    m10_20_5 = stock_group[(stock_group['ma10']> stock_group['ma20']) & (stock_group['ma20'] > stock_group['ma5']) ].shape[0]
    l20_5_10 = stock_group[(stock_group['ma20']> stock_group['ma5'])  & (stock_group['ma5']  > stock_group['ma10'])].shape[0]
    l20_10_5 = stock_group[(stock_group['ma20']> stock_group['ma10']) & (stock_group['ma10'] > stock_group['ma5']) ].shape[0]
    min20 = stock_group[(stock_group['ma1'] < stock_group['min20']) & (stock_group['ma1'] > stock_group['min60'])].shape[0]
    min60 = stock_group[(stock_group['ma1'] < stock_group['min20']) & (stock_group['ma1'] < stock_group['min60'])].shape[0]
    stat_str = (f"新低60: {min60}, 新低20: {min20}, "
                f"20_10_5/20_5_10/10_20_5/10_5_20/5_20_10/5_10_20: "
                f"{round(l20_10_5 / stock_total * 100)}%/{round(l20_5_10 / stock_total * 100)}%/"
                f"{round(m10_20_5 / stock_total * 100)}%/{round(m10_5_20 / stock_total * 100)}%/"
                f"{round(h5_20_10 / stock_total * 100)}%/{round(h5_10_20 / stock_total * 100)}%, "
                f"新高20: {max20}, 新高60: {max60}")
    print(stat_str)

    now = datetime.now()
    result = {
        '时间': [datetime.now().strftime("%Y%m%d")],
        '新低60': [min60],
        '新低20': [min20],
        'l20_10_5': [round(l20_10_5/stock_total*100)],
        'l20_5_10': [round(l20_5_10/stock_total*100)],
        'm10_20_5': [round(m10_20_5/stock_total*100)],
        'm10_5_20': [round(m10_5_20/stock_total*100)],
        'h5_20_10': [round(h5_20_10/stock_total*100)],
        'l5_10_20': [round(h5_10_20/stock_total*100)],
        '新高20': [max20],
        '新高60': [max60]
    }
    df = pd.DataFrame(result)

    # 输出文件
    now = datetime.now()
    file_name1 = f'{myLib.MyLib().filedir_database}/trend.csv'
    #df.to_csv(file_name1, mode='a', header=False, index=False, sep=',', quoting=1, encoding='UTF-8', escapechar='\\')

    # 计算 BIAS 指标
    stock_group['BIAS6']  = round((stock_group['ma1'] - stock_group['ma5']) / stock_group['ma5'] * 100,1)
    stock_group['BIAS12'] = round((stock_group['ma1'] - stock_group['ma10']) / stock_group['ma10'] * 100,1)
    stock_group['BIAS24'] = round((stock_group['ma1'] - stock_group['ma20']) / stock_group['ma20'] * 100,1)
    # 条件：BIAS6 < -6 AND BIAS12 < -10 AND BIAS24 < -16
    filtered_stocks = stock_group[
        (stock_group['BIAS6'] < -6) &
        (stock_group['BIAS12'] < -10) &
        (stock_group['BIAS24'] < -16)
        ]
    # 获取标签
    if not filtered_stocks.empty:
        stock_codes = filtered_stocks['代码'].tolist()
        labels = myLib.MyLib().get_stock_label(stock_codes)
        filtered_stocks = pd.merge(filtered_stocks, labels, on='代码', how='left')
        file_name = f'{myLib.MyLib().filedir_database}/stock_real.db'
        all_df = pd.read_csv(file_name)
        filtered_stocks = pd.merge(filtered_stocks, all_df, on='代码', how='left')
        filtered_stocks = filtered_stocks[~filtered_stocks['名称'].str.contains('ST')]
        filtered_stocks = filtered_stocks[['代码', '名称', 'BIAS6', 'BIAS12', 'BIAS24','标签']]
        print(filtered_stocks)
        file_name = f"{myLib.MyLib().filedir_data}_oversold.txt"
        #filtered_stocks.to_csv(file_name, mode='a', header=False, index=False)

    '''
    # 计算KDJ指标
    def calculate_kdj(group, n=9, m1=3, m2=3):
        group = group.tail(60)
        group['HHV'] = group['最新价'].rolling(window=n).max()
        group['LLV'] = group['最新价'].rolling(window=n).min()
        group['RSV'] = round((group['最新价'] - group['LLV']) / (group['HHV'] - group['LLV']).clip(lower=1e-8) * 100, 2)
        group['K'] = round(group['RSV'].ewm(com=m1 - 1, adjust=False).mean().fillna(50), 2)
        group['D'] = round(group['K'].ewm(com=m2 - 1, adjust=False).mean().fillna(50), 2)
        group['J'] = round(3 * group['K'] - 2 * group['D'], 2)
        print(group)
        group = group.tail(1)
        return group
    print(his_all_df)
    kdj_group = his_all_df.groupby('代码')[['代码', '时间', '最新价']].apply(calculate_kdj).reset_index(drop=True)
    print(kdj_group)
    kdj_df = kdj_group[kdj_group['J'] < 0]
    kdj_df = kdj_df[['代码', 'J']]
    file_name = f"{myLib.MyLib().filedir_data}_oversold.txt"
    kdj_df.to_csv(file_name, mode='a', header=False, index=False)
    '''

    # 定义计算MACD的函数
    def calculate_macd2(data, short_period=12, long_period=26, signal_period=9):
        ema_short = round(data['最新价'].ewm(span=short_period, adjust=False).mean(),4)
        ema_long = round(data['最新价'].ewm(span=long_period, adjust=False).mean(),4)
        dif = ema_short - ema_long
        dea = round(dif.ewm(span=signal_period, adjust=False).mean(),4)
        return dif, dea

    def calculate_macd(df):
        macd_indicator = MACD(close=df['最新价'])
        df['DIF'] = macd_indicator.macd()  # MACD值（DIF）
        df['DEA'] = macd_indicator.macd_signal()  # MACD信号线（DEA）
        df['Hist'] = macd_indicator.macd_diff()  # MACD柱（差值）

        return df

    selected_stocks = pd.DataFrame(columns=['代码', '日期'])
    stock_codes = his_all_df['代码'].unique()
    for stock_code in stock_codes:
        stock_data = his_all_df[his_all_df['代码'] == stock_code].copy()
        df = calculate_macd(stock_data)
        print(df)

