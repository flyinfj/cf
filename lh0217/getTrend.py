import akshare as ak
import pandas as pd
from datetime import datetime
import time
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

def delete_duplicate_rows():
    file_name = 'E:/python_workspace/cf/database/stock_spot.db'
    his_all_df = pd.read_csv(file_name)
    his_all_df = his_all_df.drop_duplicates()
    his_all_df.to_csv(file_name, mode='w', header=True, index=False)
    return his_all_df

def insert_new():
    #new_all_df = ak.stock_zh_a_spot()
    file_name = 'E:/python_workspace/cf/database/stock_real.db'
    new_all_df = pd.read_csv(file_name)
    new_all_df = new_all_df[new_all_df['代码'].apply(lambda x: x.startswith(('sz30', 'sz00', 'sh60')))]
    new_all_df['时间'] = '2025-12-16'
    new_order = ['代码', '时间', '最新价']
    new_all_df = new_all_df.reindex(columns=new_order)
    file_name = 'E:/python_workspace/cf/database/stock_spot.db'
    new_all_df.to_csv(file_name, mode='a', header=False, index=False)
    return new_all_df

pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度
pd.set_option('display.colheader_justify', 'center')
#
current_time = datetime.now().time()
if current_time >= datetime.strptime('10:30:00', '%H:%M:%S').time():
    # 获取交易日期
    trade_dates = ak.tool_trade_date_hist_sina()
    trade_dates['trade_date'] = pd.to_datetime(trade_dates['trade_date'])
    today = datetime.now().date()
    trade_dates = trade_dates[trade_dates['trade_date'].dt.date <= today]
    latest_60_data = trade_dates.tail(66)

    # 获取A股所有股票的实时数据
    file_name = 'E:/python_workspace/cf/database/stock_real.db'
    #new_all_df = pd.read_csv(file_name)
    new_all_df = ak.stock_zh_a_spot()
    new_all_df.to_csv(file_name, mode='w', header=True, index=False)
    new_all_df = new_all_df[new_all_df['代码'].apply(lambda x: x.startswith(('sz30', 'sz00', 'sh60')))]
    new_all_df = new_all_df[~new_all_df['名称'].astype(str).str.contains('ST', na=False)]
    new_all_df['时间'] =  latest_60_data['trade_date'].iloc[-1]
    #new_order = ['代码', '名称', '时间', '今开', '最高', '最低', '最新价', '成交量', '成交额', '流动股本', '换手率']
    new_order = ['代码', '时间', '最新价']
    new_all_df = new_all_df.reindex(columns=new_order)

    # 获取A股所有股票的历史数据
    file_name = 'E:/python_workspace/cf/database/stock_spot.db'
    his_all_df = pd.read_csv(file_name)
    his_all_df['时间'] = pd.to_datetime(his_all_df['时间'])
    #his_all_df = his_all_df[~(his_all_df['时间'] == latest_60_data['trade_date'].iloc[-1])]
    #his_all_df.to_csv(file_name, mode='w', header=True, index=False)

    #new_all_df=new_all_df.tail(1000)
    for index, row in new_all_df.iterrows():
        #获取个股的历史数据
        stock_code = row['代码']
        stock_his_df = his_all_df[his_all_df['代码'] == stock_code]
        if not stock_his_df.empty:
            start_time = stock_his_df['时间'].max()
            filter_datas = latest_60_data[latest_60_data['trade_date'] > start_time]
            start_time = filter_datas['trade_date'].min()
        else:
            start_time = latest_60_data['trade_date'].min()
        end_time = latest_60_data['trade_date'].iloc[-2]
        #如果个股数据有缺失，则补采集
        if start_time <= end_time and end_time is not None:
            print(stock_code)
            stock_daily_df = ak.stock_zh_a_daily(symbol=stock_code,
                                                        start_date=start_time,
                                                        end_date=end_time,
                                                        adjust="qfq")
            stock_daily_df.insert(0, '代码', stock_code)
            stock_daily_df = stock_daily_df.drop(columns=['open'])
            stock_daily_df = stock_daily_df.drop(columns=['high'])
            stock_daily_df = stock_daily_df.drop(columns=['low'])
            stock_daily_df = stock_daily_df.drop(columns=['volume'])
            stock_daily_df = stock_daily_df.drop(columns=['amount'])
            stock_daily_df = stock_daily_df.drop(columns=['outstanding_share'])
            stock_daily_df = stock_daily_df.drop(columns=['turnover'])
            stock_daily_df.to_csv(file_name, mode='a', header=False, index=False)
            his_all_df = pd.concat([stock_daily_df, his_all_df], ignore_index=False)
        #最近个股的数据
        stock_new_df = new_all_df[new_all_df['代码'] == stock_code]
        current_time = datetime.now().time()
        if (current_time >= datetime.strptime('17:00:00', '%H:%M:%S').time()
                and stock_his_df['时间'].max() < stock_new_df['时间'].iloc[-1]):
            stock_new_df.to_csv(file_name, mode='a', header=False, index=False)
        if stock_his_df['时间'].max() < stock_new_df['时间'].iloc[-1]:
            his_all_df = pd.concat([his_all_df,stock_new_df], ignore_index=False)

    #数据进行计算
    #his_all_df = his_all_df[his_all_df['代码'] == 'sh600546']
    his_all_df = his_all_df.sort_values(by=['代码', '时间'], ascending=[True, True])
    stock_group = his_all_df.groupby('代码', as_index=False).apply(calculate_ma, include_groups=False)
    stock_group = stock_group.reset_index()
    file_name = 'E:/python_workspace/cf/database/stock_stats.db'
    stock_group.to_csv(file_name, mode='w', header=True, index=False)

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
        '时间'  : [datetime.now().strftime("%Y-%m-%d")],
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
    df = pd.DataFrame(result)

    # 输出文件
    now = datetime.now()
    file_name1 = 'E:/python_workspace/cf/data/trend.csv'
    df.to_csv(file_name1, mode='a', header=False, index=False, sep=',', quoting=1, encoding='UTF-8', escapechar='\\')
