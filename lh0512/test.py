import requests
import json
import pandas as pd
import time
import akshare as ak
import datetime
import numpy as np
import warnings

def parse_stock(data, parent_name=None, parent_sort=None):
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
def parse_children(data, parent_name=None, parent_sort=None):
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

def parse_subject(data, parent_name=None, parent_sort=None):
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
    if 'children' in data and level == 1:
        children_info = parse_children(data)
        children_info['编码'] = subject_id
        children_info['题材'] = name
        subject_info = pd.concat( [subject_info, children_info], ignore_index=True)
    return subject_info

def get_messages():
    # 修正请求头格式
    headers = {
        "Host": "app.txcfgl.com",
        "Connection": "keep-alive",
        "sec-ch-ua": "Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\"",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua-mobile": "?0",
        "Authorization": "eyJhbGciOiJIUzUxMiJ9.eyJsb2dpbl91c2VyX2tleSI6InBjOjIxODc3NzplZWZjY2VhYS1jNDAyLTRiOGYtYjliNi1lNGQ5NGQwY2IzMTgifQ.umGyHgv48CswZedZxjHf9jFbUaFql87iPj1J58yOIZuhamAzD_UhFRB45ncAaEb_rfHMKzhbgoU7UHy-Wjlogg",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) jyhf/1.3.6 Chrome/108.0.5359.215 Electron/22.3.9 Safari/537.36",
        "sec-ch-ua-platform": "Windows",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip",
        "Accept-Language": "zh-CN"
    }
    response = requests.get("https://app.txcfgl.com/api/app/subject/top-history?pageNum=1&pageSize=20", headers=headers, files=None, verify=False)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if 'rows' in data:
            stock_data = data['rows']
            security_codes = [{'时间': item['createTime'], '题材ID': item['subjectId'],
                                '题材': item['subjectName'], '涨幅': f'{item['pctChg']}%',
                                '内容': item['description']} for item in stock_data]
            df = pd.DataFrame(security_codes)
            return df
        else:
            print("未找到股票信息")
    else:
        print("请求失败，状态码：", response.status_code)

def get_subjects(subject_id):
    # 修正请求头格式
    headers = {
        "Host": "app.txcfgl.com",
        "Connection": "keep-alive",
        "sec-ch-ua": "Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\"",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua-mobile": "?0",
        "Authorization": "eyJhbGciOiJIUzUxMiJ9.eyJsb2dpbl91c2VyX2tleSI6InBjOjIxODc3NzplZWZjY2VhYS1jNDAyLTRiOGYtYjliNi1lNGQ5NGQwY2IzMTgifQ.umGyHgv48CswZedZxjHf9jFbUaFql87iPj1J58yOIZuhamAzD_UhFRB45ncAaEb_rfHMKzhbgoU7UHy-Wjlogg",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) jyhf/1.3.6 Chrome/108.0.5359.215 Electron/22.3.9 Safari/537.36",
        "sec-ch-ua-platform": "Windows",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip",
        "Accept-Language": "zh-CN"
    }
    response = requests.get(f"https://app.txcfgl.com/api/app/subject/child-stock-tree/{subject_id}", headers=headers, files=None, verify=False)
    if response.status_code == 200:
        data = response.json()
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
file_name =  f'{model.data_dir}/data/{now.strftime("%m%d%H")}_messages.txt'
with open(file_name, 'w', encoding='utf-8') as f:
            f.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
message_df = get_messages()

