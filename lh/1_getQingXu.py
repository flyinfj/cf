import requests
import json
import akshare as ak
import pandas as pd
from datetime import date,datetime, timedelta
import time
import myLib

def get_stock_vol_rate(stock_his_df):
    if stock_his_df is None or stock_his_df.empty:
        return '-%'
    stock_his_df['时间'] = pd.to_datetime(stock_his_df['时间'], format='%Y-%m-%d %H:%M')
    now_time = datetime.now()
    tod_time = now_time.replace(hour=0, minute=0, second=0, microsecond=0)
    mask_tod_to_now = (stock_his_df['时间'] >= tod_time) & (stock_his_df['时间'] <= now_time)
    data_tod_to_now = stock_his_df.loc[mask_tod_to_now]
    data_yes_to_pre = stock_his_df.iloc[-len(data_tod_to_now)-17:-17]
    yes_volumn = data_yes_to_pre['成交额'].sum()
    now_volumn = data_tod_to_now['成交额'].sum()
    if yes_volumn>0:
        return f'{round(now_volumn/yes_volumn*100-100)}%'
    else:
        return '0%'

print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度            
pd.set_option('display.colheader_justify', 'center')

model = myLib.MyLib()

#获取热门靠前350
df_1 = model.get_cond_popu_stocks(351) #350
if df_1 is not None:
    df_1 = df_1[df_1['代码'].str.startswith(('30', '00', '60'))]
    df_1 = df_1[pd.to_numeric(df_1['涨幅'], errors='coerce').notnull()]
    avg_increase_1 = round(df_1['涨幅'].mean(),2)
    stock_codes_1 = df_1['代码'].tolist()

#获取飙升超1000
df_2 = model.get_popu_stocks(1)
df_2 = df_2[df_2['代码'].apply(lambda x: x.startswith(('30', '60', '0')))]
stock_codes_2 = df_2['代码'].tolist()
df_2 = model.get_stock_data(stock_codes_2)
df_2 = df_2[pd.to_numeric(df_2['涨幅'], errors='coerce').notnull()]
avg_increase_2 = round(df_2['涨幅'].mean(),2)

#获取涨幅超9%
df_3 = model.get_raise_stocks(200) #200
df_3 = df_3[df_3['代码'].str.startswith(('30', '00', '60'))]
df_3 = df_3[pd.to_numeric(df_3['涨幅'], errors='coerce').notnull()]
avg_increase_3 = round(df_3['涨幅'].mean(),2)
stock_codes_3 = df_3['代码'].tolist()

#获取标签
stock_codes_all = list(set(stock_codes_1 + stock_codes_2 + stock_codes_3))
all_labels_df = model.get_stock_label(stock_codes_all)
words_to_remove = ['热榜龙头','概念','市值龙头','业绩龙头',' ']
for word in words_to_remove:
    all_labels_df['标签'] = all_labels_df['标签'].str.replace(word, '', regex=False)

#计算热榜350的情绪
labels_1 = all_labels_df[all_labels_df['代码'].isin(stock_codes_1)]
labels_exploded_1 = pd.Series()
for index, row in labels_1.iterrows():
    labels_exploded_1_1 = pd.Series(row['标签'].split(',')).drop_duplicates()
    labels_exploded_1 = pd.concat([labels_exploded_1, labels_exploded_1_1])
labels_exploded_1 = labels_exploded_1[~labels_exploded_1.str.contains(r'\d|首板')]
label_counts_1 = labels_exploded_1.value_counts()
top_labels_1 = label_counts_1.head(5)
top_list_1 = [f"{label}({int(count)})" for label, count in top_labels_1.items()]
top_str_1 = ','.join(top_list_1)

#计算飙升超1000的情绪
labels_2 = all_labels_df[all_labels_df['代码'].isin(stock_codes_2)]
labels_exploded_2 = pd.Series()
for index, row in labels_2.iterrows():
    labels_exploded_2_2 = pd.Series(row['标签'].split(',')).drop_duplicates()
    labels_exploded_2 = pd.concat([labels_exploded_2, labels_exploded_2_2])
labels_exploded_2 = labels_exploded_2[~labels_exploded_2.str.contains(r'\d|首板')]
label_counts_2 = labels_exploded_2.value_counts()
top_labels_2 = label_counts_2.head(5)
top_list_2 = [f"{label}({int(count)})" for label, count in top_labels_2.items()]
top_str_2 = ','.join(top_list_2)

#计算涨幅超9%的情绪
labels_3 = all_labels_df[all_labels_df['代码'].isin(stock_codes_3)]
labels_exploded_3 = pd.Series()
for index, row in labels_3.iterrows():
    labels_exploded_3_3 = pd.Series(row['标签'].split(',')).drop_duplicates()
    labels_exploded_3 = pd.concat([labels_exploded_3, labels_exploded_3_3])
labels_exploded_3 = labels_exploded_3[~labels_exploded_3.str.contains(r'\d|首板')]
label_counts_3 = labels_exploded_3.value_counts()
top_labels_3 = label_counts_3.head(5)
top_list_3 = [f"{label}({int(count)})" for label, count in top_labels_3.items()]
top_str_3 = ','.join(top_list_3)

#top_labels_1 = []
#print(top_labels_3)
#labels_1 = pd.merge(labels_1, df_1, on='代码', how='left')
#for top_label, count in top_labels_3.items():
#    print(top_label)
#    print(count)
#    print(labels_1)
#    filtered_rows = labels_1[labels_1['标签'].str.contains(top_label)]
#    raise_values = filtered_rows['涨幅'].tolist()
#    vol_values = filtered_rows['量比'].tolist()
#    swith_values = filtered_rows['换手'].tolist()
#    average_raise = sum(raise_values) / len(raise_values) if raise_values else None
#    average_vol = sum(vol_values) / len(vol_values) if vol_values else None
#    average_swith = sum(swith_values) / len(swith_values) if swith_values else None
#
#    top_labels_1.append({
#        'top_label': top_label,
#        '涨幅': average_raise,
#        '量比': average_vol,
#        '换手': average_swith
#    })
#top_labels_1_df = pd.DataFrame(top_labels_1)
#print(top_labels_1_df)

#输出今日情绪(热榜350、飙升100、涨幅超9%)
parsed_data = []
report_data = {
    '类型': '热榜',
    '涨幅/股票数': f"{avg_increase_1}%/{len(stock_codes_1)}",
    '板块(股票数)': top_str_1,
}
parsed_data.append(report_data)
report_data = {
    '类型': '飙升',
    '涨幅/股票数': f"{avg_increase_2}%/{len(stock_codes_2)}",
    '板块(股票数)': top_str_2,
}
parsed_data.append(report_data)
#num_of_stock_codes_3 = len(stock_codes_3)
report_data = {
    '类型': '大涨',
    '涨幅/股票数': f"{avg_increase_3}%/{len(stock_codes_3)}",
    '板块(股票数)': top_str_3,
}
parsed_data.append(report_data)
df = pd.DataFrame(parsed_data)

print(model.beautify(df))
model.output_file(df,'热门板块跟踪(热榜350+飙升100+大涨超9%)' , 0)

file_name3 =  f'{model.filedir_data}/{datetime.now().strftime("%m%d%H")}_bnk.txt'
df = pd.DataFrame(top_labels_2).reset_index()
df.columns = ['板块', '数量']
df.to_csv(file_name3, mode='a', header=True, index=False, sep='\t')
df = pd.DataFrame(top_labels_1).reset_index()
df.columns = ['板块', '数量']
df.to_csv(file_name3, mode='a', header=True, index=False, sep='\t')
df = pd.DataFrame(top_labels_3).reset_index()
df.columns = ['板块', '数量']
df.to_csv(file_name3, mode='a', header=True, index=False, sep='\t')

bnk_df = model.get_vol_bnk()
print(model.beautify(bnk_df))
model.output_file(bnk_df,'资金流入板块统计' , 0)

start_date  = model.get_trade_dates(5).iloc[0,0]
stock_his_df1 = model.get_stock_his('1.000001',15,start_date)
stock_his_df2 = model.get_stock_his('0.399001',15,start_date)
stock_his_df3 = model.get_stock_his('0.399006',15,start_date)
stock_his_df4 = model.get_stock_his('1.000300',15,start_date)
stock_his_df5 = model.get_stock_his('1.000852',15,start_date)
stock_his_df6 = model.get_stock_his('90.BK0475',15,start_date)
v_str = ('\n(今日与昨日量比)上证：' + get_stock_vol_rate(stock_his_df1) +
          ' 深证：' + get_stock_vol_rate(stock_his_df2) +
          ' 创业板：' + get_stock_vol_rate(stock_his_df3) +
          ' 沪深300：'  + get_stock_vol_rate(stock_his_df4) +
          ' 中证1000：' + get_stock_vol_rate(stock_his_df5) +
          ' 银行板块：'  + get_stock_vol_rate(stock_his_df6))
print(v_str)
model.output_str(v_str)