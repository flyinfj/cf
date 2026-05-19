import requests
import json
import pandas as pd
import time
import akshare as ak
import datetime
import numpy as np
import warnings
import myLib
import os

headers = {
    "Host": "app.txcfgl.com",
    "Connection": "keep-alive",
    "sec-ch-ua": "Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\"",
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "Authorization": "eyJhbGciOiJIUzUxMiJ9.eyJsb2dpbl91c2VyX2tleSI6InBjOjIxODc3NzplOTlmZjk3OC03OWVmLTQ1ZGQtYjViNC0zM2E3MjFhNjdlNTkifQ.JYuegjaV-jNnTAh8OKSftZEJ4-O6L4b-5DkumBPUpXUMiN9y6ljDQ2PHtVhPI0uNRSgzSXjxikZC1t5I_G8vRA",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) jyhf/1.3.6 Chrome/108.0.5359.215 Electron/22.3.9 Safari/537.36",
    "sec-ch-ua-platform": "Windows",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip",
    "Accept-Language": "zh-CN"
}
data_dir = myLib.MyLib().data_dir

def parse_stock(data):
    stocks_info_list = []
    for stock in data['stocks']:
        reason = stock.get('reason')
        remark = stock.get('remark')
        if remark is None:
            remark = ''
        stock_info = {
            '排序': stock.get('sort'),
            '代码': stock.get('stockId'),
            '名称': stock.get('name'),
            '涨幅': f'{stock.get('pctChg')}%',
            '理由': reason[:30].ljust(30) if len(reason) > 30 else reason.ljust(30),
            '备注': remark[:30].ljust(30) if len(remark) > 30 else remark.ljust(30)
        }
        stocks_info_list.append(stock_info)
    stocks_info = pd.DataFrame(stocks_info_list)
    return stocks_info

#解析children信息
def parse_children(data):
    children_info = pd.DataFrame()
    for child in data['children']:
        children_name=child['name']
        if 'stocks' in child  and child['stocks']:
            stocks_info = parse_stock(child)
            stocks_info['分类'] = children_name
            stocks_info['子类'] = ''
            children_info = pd.concat([children_info,stocks_info], ignore_index=True)
        if 'children' in child:
            for child2 in child['children']:
                children2_name = child2['name']
                if 'stocks' in child2:
                    stocks_info = parse_stock(child2)
                    stocks_info['分类'] = children_name
                    stocks_info['子类'] = children2_name
                    children_info = pd.concat([children_info,stocks_info], ignore_index=True)
    return children_info

def parse_subject(data, v_level = 1):
    if 'level' in data:
        level = data['level']
    else:
        level = None

    if 'subjectId' in data:
        subject_id = data['subjectId']
    else:
        subject_id = None

    if 'name' in data:
        name = data['name']
    else:
        name = None

    subject_info = pd.DataFrame()
    if v_level == 1:
        if 'children' in data and level == 1:
            children_info = parse_children(data)
            children_info['编码'] = subject_id
            children_info['题材'] = name
            subject_info = pd.concat( [subject_info, children_info], ignore_index=True)
    if v_level != 1:
        if 'children' in data:
            children_info = parse_children(data)
            children_info['编码'] = subject_id
            children_info['题材'] = name
            subject_info = pd.concat( [subject_info, children_info], ignore_index=True)
        if 'stocks' in data and isinstance(data['stocks'], list) and len(data['stocks']) > 0:
            stocks_info = parse_stock(data)
            stocks_info['编码'] = subject_id
            stocks_info['题材'] = name
            stocks_info['分类'] = ''
            stocks_info['子类'] = ''
            subject_info = pd.concat([subject_info,stocks_info], ignore_index=True)
    return subject_info

def get_messages():
    response = requests.get("https://app.txcfgl.com/api/app/subject/top-history?pageNum=1&pageSize=60", headers=headers, files=None, verify=False)
    if response.status_code == 200:
        data = response.json()
        if 'rows' in data:
            stock_data = data['rows']
            security_codes = [{'时间': item['createTime'], '题材ID': item['subjectId'],
                                #'类型': '新题材' if item['type'] == 2 
                                #    else ('新事件' if item['type'] == 2 
                                #    else item['type']),
                                '题材': item['subjectName'], '涨幅': f'{item['pctChg']}%',
                                '内容': item['description']} for item in stock_data]
            df = pd.DataFrame(security_codes)
            return df
        else:
            print("未找到股票信息")
    else:
        print("请求失败，状态码：", response.status_code)

def get_subjects(subject_id):
    response = requests.get(f"https://app.txcfgl.com/api/app/subject/child-stock-tree/{subject_id}", headers=headers, files=None, verify=False)
    if response.status_code == 200:
        data = response.json()
        res_file_name =  f'{data_dir}/response/{subject_id}'
        with open(res_file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
    else:
        print("请求失败，状态码：", response.status_code)

def beautify(df):
        df = df.astype(str)
        max_lengths = df.apply(lambda x: x.str.len()).max()
        if '名称' in df.columns:
            df['名称'] = df['名称'].apply(lambda x: x if len(x) >= 4 else x + '：' * (4 - len(x)))
        for col in df.columns:
            max_length = max_lengths[col]
            if max_length >0:
                if col not in ['标签', '理由']:
                    df[col] = df[col].str.pad(width=max_length, side='left', fillchar=' ')
                else:
                    df[col] = df[col].str.pad(width=max_length, side='right', fillchar=' ')
        return df
# 测试
pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度
pd.set_option('display.colheader_justify', 'center')
now = datetime.datetime.now()
model = myLib.MyLib()

trade_dates = model.get_trade_dates(1,1)
trade_date = trade_dates['trade_date'].iloc[0]
file_name =  f'{data_dir}/data/html/messages.html'
if os.path.exists(file_name):
    os.remove(file_name)
model.init_html(file_name)
with open(file_name, 'a', encoding='utf-8') as f:
            f.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

file_name2 = f'{model.filedir_database}/subject_stock.csv'
subject_stock_df = pd.read_csv(file_name2)
subject_stock_df['代码'] = subject_stock_df['代码'].astype(str).str.zfill(6)
subject_stock_df['备注'] = subject_stock_df['备注'].str.replace(',', '').str.replace(' ', '')

new_data = subject_stock_df[subject_stock_df['名称'] == '****']
for index, row in new_data.iterrows():
    remark = row['备注']
    file_name3 = f'{model.filedir_database}/tmp_subject_stock.csv'
    df3 = pd.read_csv(file_name3)
    df3['涨幅'] = df3['涨幅'].str.replace('%', '', regex=False).astype(float)
    
    file_name4 = f'{model.filedir_database}/tmp_stock_real.db'
    df4 = pd.read_csv(file_name4)
    df4 = df4.rename(columns={'涨跌幅': '涨幅'})
    df4['涨幅'] = df4['涨幅'].round(2)
    df3_filtered = df3[df3['备注'] == remark].drop_duplicates()
    last_3_records_df3 = df3_filtered.tail(3)
    if len(last_3_records_df3) == 3:
        df4_filtered = df4[df4[['涨幅', '时间']].apply(tuple, axis=1).isin(
            last_3_records_df3[['涨幅', '时间']].apply(tuple, axis=1))]
        groupby_result = df4_filtered.groupby(['代码', '名称']).size().reset_index(name='数量')
        #groupby_result = df4_filtered.groupby(['代码']).size().reset_index(name='数量')
        code_r_name_r = groupby_result[groupby_result['数量'] == 3][['代码', '名称']]
        # 如果代码和名称不为空，则进行以下处理
        if not code_r_name_r.empty and len(code_r_name_r) == 1:
            # 修改 subject_stock_df 的备注=remark的行的、代码、名称为代码code_r、名称name_r
            mask = subject_stock_df['备注'] ==remark
            subject_stock_df.loc[mask, '代码'] = code_r_name_r['代码'].values[0]
            subject_stock_df.loc[mask, '名称'] = code_r_name_r['名称'].values[0]
        subject_stock_df.to_csv(file_name2, mode='w', header=True, index=False)

popu_df = model.get_cond_popu_stocks(351)
popu_df = popu_df.drop(columns=['名称'])
popu_df = popu_df.drop(columns=['涨幅'])
message_df = get_messages()
if message_df is not None:
    for index, item in message_df.iterrows():
        item_content = f"{item['时间']} {item['题材']} {item['涨幅']} {item['内容'].replace(' ','').replace('\n','')}"
        print(item_content)
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write(f'<h4>{item_content}</h4>\n')
        subject_id = item['题材ID']
        time.sleep(1)
        content = get_subjects(subject_id)
        df = pd.DataFrame()
        if 'data' in content and content['data']:
            for subject in content['data']:
                subject_info = parse_subject(subject,0)        
                subject_info['备注'] = subject_info['备注'].str.replace(',', '').str.replace(' ', '')
                mask = subject_stock_df[subject_stock_df['备注'].isin(subject_info['备注'])]
                subject_info = pd.merge(subject_info, mask, on='备注', how='left')
            
                subject_info['代码'] = subject_info['代码_y'].fillna(subject_info['代码_x'])
                subject_info['名称'] = subject_info['名称_y'].fillna(subject_info['名称_x'])
                #如果 代码_y列 为空，则判断备注名在file_name2文件中是否存在，如果不存在，将代码_x列、名称_x列、备注写入 file_name2文件中
                subject_info_null = subject_info[subject_info['名称_y'].isnull()]
                subject_info_null = subject_info_null[subject_info_null['备注']!='']
                subject_info_null = subject_info_null.drop_duplicates(subset=['备注']) 
                current_time = datetime.datetime.now().time()
                if subject_info_null is not None and not subject_info_null.empty :                      
                    new_data = subject_info_null[['代码_x', '名称_x', '备注']].rename(columns={'代码_x': '代码', '名称_x': '名称'})
                    subject_stock_df = pd.concat([subject_stock_df, new_data], ignore_index=True)
                    new_data.to_csv(file_name2, mode='a', header=False, index=False, sep=',', quoting=1, encoding='UTF-8', escapechar='\\')

                subject_info_null = subject_info[subject_info['名称_y'].isnull() | (subject_info['名称_y'] == '****')]
                subject_info_null = subject_info_null[subject_info_null['备注']!='']
                subject_info_null = subject_info_null.drop_duplicates(subset=['备注']) 
                current_time = datetime.datetime.now().time()
                if subject_info_null is not None and not subject_info_null.empty and current_time >= datetime.datetime.strptime('16:30:00', '%H:%M:%S').time():                                  
                    new_data = subject_info_null[['代码_x', '名称_x', '备注', '涨幅']].rename(columns={'代码_x': '代码', '名称_x': '名称'})
                    new_data['trade_date'] = trade_date
                    file_name3 = f'{model.filedir_database}/tmp_subject_stock.csv'
                    new_data.to_csv(file_name3, mode='a', header=False, index=False, sep=',', quoting=1, encoding='UTF-8', escapechar='\\')

                subject_info = subject_info.drop(columns=['代码_x', '名称_x','代码_y', '名称_y'])  
                df = pd.concat( [df, subject_info], ignore_index=True)
        if not df.empty:
            stock_codes = df['代码'].drop_duplicates().tolist()
            df_raise = model.calc_raise_rate_new(stock_codes)
            df = pd.merge(df, df_raise, on='代码', how='left')
            df = pd.merge(df, popu_df, on='代码', how='left')
            df = df.fillna('')
            new_order = ['题材','分类','子类','代码','名称','涨幅','支撑线','压力线','热榜','涨停','理由']
            df = df.reindex(columns=new_order)
            df = beautify(df)
        if not df.empty:
            """
            for line in str(df).splitlines():
                print('    ' + line)
                with open(file_name, 'a', encoding='utf-8') as f:
                    f.write('    ' + line)
                    f.write('\n')
            """
            df['代码'] = df['代码'].apply(lambda x: f'<a href="https://summary.jrj.com.cn/stock/{"sh" if x.startswith("6") else "sz"}/{x}">{x}</a>')
            html_content = df.to_html(index=False,escape=False)
            table_content = html_content.split('<table')[1].split('</table>')[0]
            with open(file_name, 'a', encoding='utf-8') as f:
                f.write(f'<table{table_content}</table>')