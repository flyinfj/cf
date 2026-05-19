import akshare as ak
import pandas as pd
from datetime import datetime
import time
import myLib
import tools

model = myLib.MyLib()
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
if current_time >= datetime.strptime('10:30:00', '%H:%M:%S').time():
    # 获取交易日期
    latest_60_data = myLib.MyLib().get_trade_dates(66,1)
    latest_60_data['trade_date'] = pd.to_numeric(latest_60_data['trade_date'], errors='coerce')
    latest_60_data = latest_60_data.dropna(subset=['trade_date'])
    latest_60_data['trade_date'] = latest_60_data['trade_date'].astype(int)

    # 获取A股所有股票的实时数据
    #new_all_df = tools.Tools().db_query('select * from stock_real')
    #column_mapping = {'stock_code': '代码', 'stock_name': '名称', 'last_price': '最新价', 'change_amount': '涨跌额', 'change_percent': '涨跌幅', 'buy_price': '买入', 'sell_price': '卖出', 'pre_close': '昨收', 'open_price': '今开', 'high_price': '最高', 'low_price': '最低', 'volume': '成交量', 'turnover': '成交额', 'timestamp': '时间戳'}
    #new_all_df = new_all_df.rename(columns=column_mapping)
    new_all_df = ak.stock_zh_a_spot()

    file_name = f'{myLib.MyLib().filedir_database}/stock_real.db'
    #new_all_df = pd.read_csv(file_name)    
    new_all_df.to_csv(file_name, mode='w', header=True, index=False)
    new_all_df['代码'] = new_all_df['代码'].astype(str).str.replace('sh', '').str.replace('sz', '').str.replace('bj', '')

    new_all_df2 = new_all_df
    column_mapping = {'代码': 'stock_code', '名称': 'stock_name', '最新价': 'last_price', '涨跌额': 'change_amount', '涨跌幅': 'change_percent', '买入': 'buy_price', '卖出': 'sell_price', '昨收': 'pre_close', '今开': 'open_price', '最高': 'high_price', '最低': 'low_price', '成交量': 'volume', '成交额': 'turnover', '时间戳': 'timestamp'}
    new_all_df2 = new_all_df2.rename(columns=column_mapping)
    tools.Tools().db_exec('delete from stock_real')
    tools.Tools().db_batchinset(new_all_df2, 'stock_real')

    if current_time >= datetime.strptime('16:30:00', '%H:%M:%S').time():
        new_order2 = ['代码','名称', '最新价','涨跌幅']
        new_all_df2 = new_all_df.reindex(columns=new_order2)
        new_all_df2['时间'] =  latest_60_data['trade_date'].iloc[-1]

        new_all_df21 = new_all_df2
        column_mapping = {'代码': 'stock_code', '名称': 'stock_name', '最新价': 'last_price', '涨跌幅': 'change_percent', '时间': 'trade_date'}
        new_all_df21 = new_all_df21.rename(columns=column_mapping)
        tools.Tools().db_exec(f'delete from tmp_stock_real where trade_date = {latest_60_data["trade_date"].iloc[-1]}')
        tools.Tools().db_batchinset(new_all_df21, 'tmp_stock_real')
        tools.Tools().db_exec(f'delete from tmp_stock_real where trade_date < {latest_60_data["trade_date"].iloc[-5]}')

    new_all_df = new_all_df[new_all_df['代码'].apply(lambda x: x.startswith(('30', '00', '60')))]
    new_all_df = new_all_df[~new_all_df['名称'].astype(str).str.contains('ST', na=False)]
    new_all_df['时间'] =  latest_60_data['trade_date'].iloc[-1]
    #new_order = ['代码', '名称', '时间', '今开', '最高', '最低', '最新价', '成交量', '成交额', '流动股本', '换手率']
    new_order = ['代码', '时间', '最新价']
    new_all_df = new_all_df.reindex(columns=new_order)

    # 获取A股所有股票的历史数据
    his_all_df = tools.Tools().db_query(f'select * from stock_spot where trade_date >= \'{latest_60_data["trade_date"].min()}\' order by trade_date')
    column_mapping = {'stock_code': '代码','trade_date': '时间','close_price': '最新价'}
    his_all_df = his_all_df.rename(columns=column_mapping)
    his_all_df['时间'] = pd.to_numeric(his_all_df['时间'], errors='coerce')
    his_all_df['最新价'] = pd.to_numeric(his_all_df['最新价'], errors='coerce')

    #his_all_df['时间'] = pd.to_datetime(his_all_df['时间'])
    #his_all_df = his_all_df[~(his_all_df['时间'] == latest_60_data['trade_date'].iloc[-1])]
    #his_all_df.to_csv(file_name, mode='w', header=True, index=False)

    #new_all_df=new_all_df.tail(1000)
    print(latest_60_data)
    for index, row in new_all_df.iterrows():
        #获取个股的历史数据
        stock_code = row['代码']
        stock_his_df = his_all_df[his_all_df['代码'] == stock_code]
        stock_his_df = stock_his_df.dropna(subset=['时间'])
        if not stock_his_df.empty:
            start_time = stock_his_df['时间'].max()
            filter_datas = latest_60_data[latest_60_data['trade_date'] > start_time]
            start_time = filter_datas['trade_date'].min()
        else:
            start_time = latest_60_data['trade_date'].min()
        end_time = latest_60_data['trade_date'].iloc[-2]
        #如果个股数据有缺失，则补采集(不含今日）
        if  end_time is not None and start_time is not None and start_time <= end_time:
            print(stock_code)
            if stock_code[:2] == "60":
                v_stock_code = 'sh' + stock_code
            else:
                v_stock_code = 'sz' + stock_code
            start_time = int(start_time)
            end_time = int(end_time)
            stock_daily_df = ak.stock_zh_a_daily(symbol=v_stock_code,
                                                        start_date=str(start_time),
                                                        end_date=str(end_time),
                                                        adjust="qfq")
            stock_daily_df.insert(0, '代码', stock_code)
            stock_daily_df['date'] = stock_daily_df['date'].apply(lambda x: int(x.strftime('%Y%m%d')))
            stock_daily_df = stock_daily_df.drop(columns=['open'])
            stock_daily_df = stock_daily_df.drop(columns=['high'])
            stock_daily_df = stock_daily_df.drop(columns=['low'])
            stock_daily_df = stock_daily_df.drop(columns=['volume'])
            stock_daily_df = stock_daily_df.drop(columns=['amount'])
            stock_daily_df = stock_daily_df.drop(columns=['outstanding_share'])
            stock_daily_df = stock_daily_df.drop(columns=['turnover'])

            stock_daily_df2 = stock_daily_df 
            column_mapping = {'代码': 'stock_code', 'date': 'trade_date', 'close': 'close_price'}
            stock_daily_df2 = stock_daily_df2.rename(columns=column_mapping)
            tools.Tools().db_batchinset(stock_daily_df2, 'stock_spot')

            his_all_df = pd.concat([stock_daily_df, his_all_df], ignore_index=False)
        #最近个股的今日数据
        stock_new_df = new_all_df[new_all_df['代码'] == stock_code]
        current_time = datetime.now().time()
        if (current_time >= datetime.strptime('17:00:00', '%H:%M:%S').time()
                and stock_his_df['时间'].max() < stock_new_df['时间'].iloc[-1]):

            stock_new_df2 = stock_new_df 
            column_mapping = {'代码': 'stock_code', '时间': 'trade_date', '最新价': 'close_price'}
            stock_new_df2 = stock_new_df2.rename(columns=column_mapping)
            tools.Tools().db_batchinset(stock_new_df2, 'stock_spot')
        #如果个数历史的最大时间小于新获取的个股的最大时间，则进行合并
        if stock_his_df['时间'].max() < stock_new_df['时间'].iloc[-1]:
            his_all_df = pd.concat([his_all_df,stock_new_df], ignore_index=False)

    #数据进行计算
    #his_all_df = his_all_df[his_all_df['代码'] == '600546']
    his_all_df = his_all_df.sort_values(by=['代码', '时间'], ascending=[True, True])
    stock_group = his_all_df.groupby('代码', as_index=False).apply(calculate_ma, include_groups=False)
    stock_group = stock_group.reset_index()

    stock_group2 = stock_group
    column_mapping = {'index': 'id', '代码': 'stock_code'}
    stock_group2 = stock_group2.rename(columns=column_mapping)
    tools.Tools().db_upsert(stock_group2, 'stock_stats', 'stock_code','id')

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
        'l20_10_5': [f"{round(l20_10_5/stock_total*100)}%"],
        'l20_5_10': [f"{round(l20_5_10/stock_total*100)}%"],
        'm10_20_5': [f"{round(m10_20_5/stock_total*100)}%"],
        'm10_5_20': [f"{round(m10_5_20/stock_total*100)}%"],
        'h5_20_10': [f"{round(h5_20_10/stock_total*100)}%"],
        'l5_10_20': [f"{round(h5_10_20/stock_total*100)}%"],
        '新高20': [max20],
        '新高60': [max60]
    }
    df = pd.DataFrame(result)
    print(df)
    # 输出文件
    now = datetime.now()
    file_name1 = f'{myLib.MyLib().filedir_data}/html/trend.html'
    # df.to_csv(file_name1, mode='a', header=False, index=False, sep=',', quoting=1, encoding='UTF-8', escapechar='\\')
    html_content = df.to_html(index=False,escape=False, header=False)
    table_content = html_content.split('<table')[1].split('</table>')[0]
    print(html_content)
    with open(file_name1, 'a', encoding='utf-8') as f:
        f.write(f'{table_content}')

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
        filtered_stocks['名称'] = filtered_stocks['名称'].astype(str)
        filtered_stocks = filtered_stocks[~filtered_stocks['名称'].str.contains('ST|退')]
        filtered_stocks = filtered_stocks[['代码', '名称', 'BIAS6', 'BIAS12', 'BIAS24', '标签']]
        file_name = f"{myLib.MyLib().filedir_data}/html/{datetime.now().strftime("%m%d%H")}_oversold.html"
        # model.beautify(filtered_stocks).to_csv(file_name, mode='a', header=False, index=False)
        html_content = model.beautify(filtered_stocks).to_html(index=False,escape=False)
        table_content = html_content.split('<table')[1].split('</table>')[0]
        print(html_content)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(f'<meta charset="UTF-8"><table{table_content}</table>')
    '''
    # 计算KDJ指标
    def calculate_kdj(group, n=9, m1=3, m2=3):
        group = group.tail(20)
        group['HHV'] = group['最新价'].rolling(window=n).max()
        group['LLV'] = group['最新价'].rolling(window=n).min()
        group['RSV'] = round((group['最新价'] - group['LLV']) / (group['HHV'] - group['LLV']) * 100, 2)
        group['K'] = round(group['RSV'].ewm(com=m1 - 1, adjust=False).mean(), 2)
        group['D'] = round(group['K'].ewm(com=m2 - 1, adjust=False).mean(), 2)
        group['J'] = round(3 * group['K'] - 2 * group['D'], 2)
        group = group.tail(1)
        return group

    kdj_group = his_all_df.groupby('代码')[['代码', '时间', '最新价']].apply(calculate_kdj).reset_index(drop=True)
    kdj_df = kdj_group[kdj_group['J'] < 0]
    kdj_df = kdj_df[['代码', 'J']]
    file_name = f"{myLib.MyLib().filedir_data}/{datetime.now.strftime("%m%d%H")}_oversold.txt"
    kdj_df.to_csv(file_name, mode='a', header=False, index=False)
    '''
