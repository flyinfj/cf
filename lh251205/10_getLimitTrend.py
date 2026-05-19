import akshare as ak
import pandas as pd
from datetime import datetime
import time
import myLib
import numpy as np

model = myLib.MyLib()
# 1. 从days_limitup_pre文件获取最近15天数据
file_name = f'{model.filedir_database}/days_limitup_pre.db'
limitup_df = pd.read_csv(file_name)
limitup_df['代码'] = limitup_df['代码'].astype(str).str.zfill(6)
limitup_df['时间'] = pd.to_datetime(limitup_df['时间'].astype(str), format='%Y%m%d')
start_date = model.get_trade_dates(10,0).iloc[0,0]
start_date = pd.to_datetime(start_date, format='%Y%m%d')
#limitup_df = limitup_df[limitup_df['时间'].isin(trade_dates)]
#recent_date = pd.Timestamp.now() - pd.Timedelta(days=15)
limitup_df = limitup_df[limitup_df['时间'] > start_date]
limitup_df = limitup_df[limitup_df['代码'].str.startswith(('30', '00', '60'))]
limitup_df = limitup_df[~limitup_df['名称'].str.contains('ST|退')]
# 统计代码出现次数并筛选只出现一次的代码
code_counts = limitup_df['代码'].value_counts()
single_codes = code_counts[code_counts == 1].index
limitup_df = limitup_df[limitup_df['代码'].isin(single_codes)]

# 2. 加载stock_spot数据
file_name = f'{model.filedir_database}/stock_spot.db'
stock_spot_df = pd.read_csv(file_name)
stock_spot_df['代码'] = stock_spot_df['代码'].astype(str).str.zfill(6)

# 3. 获取最后15行数据并转换格式
result_dfs = []
for code in limitup_df['代码'].unique():
    limitup_date = limitup_df[limitup_df['代码'] == code]['时间'].iloc[0]
    code_data = stock_spot_df[stock_spot_df['代码'] == code].tail(15)
    code_data['时间'] = pd.to_datetime(code_data['时间'].astype(str), format='%Y%m%d')
    code_data = code_data[code_data['时间'] >= limitup_date]
    prices = code_data['最新价'].values
    if len(prices) > 0:
        min_idx = np.argmin(prices)
        if min_idx > 0 and prices[min_idx] != 0 and not np.isnan(prices[min_idx]):
            max_before_min = np.max(prices[:min_idx])
            ratio_down = round(100*(max_before_min - prices[min_idx]) / max_before_min)

            max_after_min = np.max(prices[min_idx:])
            ratio_up = round(100*(max_after_min - prices[min_idx]) / prices[min_idx])
            price_df = pd.Series({
                '代码': code,
                'ratio_down': ratio_down,
                'ratio_up': ratio_up
            })
            result_dfs.append(price_df)
final_df = pd.DataFrame(result_dfs)
final_df = final_df.sort_values(by=['ratio_down', 'ratio_up'], ascending=[True, True])# Then perform the analysis on the concatenated DataFrame
ratio_down_bins = [0, 5, 10, 20, 30, float('inf')]
ratio_up_bins = [0, 10, 20, 30, float('inf')]

ratio_down_labels = ['00-05', '05-10', '10-20', '20-30', '30-++']
ratio_up_labels = ['00-10', '10-20', '20-30', '30-++']

result = []
for down_label, down_min, down_max in zip(ratio_down_labels, ratio_down_bins[:-1], ratio_down_bins[1:]):
    filtered = final_df[(final_df['ratio_down'] >= down_min) & (final_df['ratio_down'] < down_max)]
    counts = []

    for up_label, up_min, up_max in zip(ratio_up_labels, ratio_up_bins[:-1], ratio_up_bins[1:]):
        up_mask = filtered[(filtered['ratio_up'] >= up_min) & (filtered['ratio_up'] < up_max)]
        counts.append(len(up_mask))
    
    result.append({
        'ratio_down': down_label,
        'count': sum(counts),
        'up00-10': counts[0],
        'up10-20': counts[1],
        'up20-30': counts[2],
        'up30-++': counts[3]
    })

stats_df = pd.DataFrame(result)
file_name = f'{model.data_dir}/data/html/{datetime.now().strftime("%m%d%H")}_limit_trend.html'

html_content = stats_df.to_html(index=False,escape=False)
table_content = html_content.split('<table')[1].split('</table>')[0]
with open(file_name, 'w', encoding='utf-8') as f:
    f.write(f'<meta charset="UTF-8"><table{table_content}</table>')

final_df['代码'] = final_df['代码'].apply(lambda x: f'<a href="https://summary.jrj.com.cn/stock/{"sh" if x.startswith("6") else "sz"}/{x}">{x}</a>')
   
# 添加dw_label列
final_df['dw_label'] = pd.cut(
    final_df['ratio_down'],
    bins=[0, 5, 10, 20, 30, float('inf')],
    labels=['00-05', '05-10', '10-20', '20-30', '30-++'],
    right=False
)

# 添加up_label列
final_df['up_label'] = pd.cut(
    final_df['ratio_up'],
    bins=[0, 10, 20, 30, float('inf')],
    labels=['00-10', '10-20', '20-30', '30-++'],
    right=False
)

# 按照dw_label和up_label分组并合并代码列
# 修改后的代码，添加observed=False参数
result_series = final_df.groupby(['dw_label', 'up_label'], observed=False)['代码'].apply(lambda x: '   '.join(x))
final_df = result_series.to_frame('代码')
final_df = final_df.reset_index()

html_content = final_df.to_html(index=False,escape=False)
table_content = html_content.split('<table')[1].split('</table>')[0]
with open(file_name, 'a', encoding='utf-8') as f:
    f.write(f'<table{table_content}</table>')