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
import tools

headers = {
    "Host": "app.txcfgl.com",
    "Connection": "keep-alive",
    "sec-ch-ua": "Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\"",
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "Authorization": "eyJhbGciOiJIUzUxMiJ9.eyJsb2dpbl91c2VyX2tleSI6InBjOjIxODc3Nzo2OGNjNDMyYi1kNTg5LTQ2NTYtODkwNy1iNGYyNTVjOWE5OWEifQ.1Emqp0yPZEVl63SfRhdSL5AbVxT1XYzKgAShaEIM9OLN24bs1jLvE0Lz3YP8AzBPRJe98vC_Cl3jluUbaTCdrA",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) jyhf/1.3.6 Chrome/108.0.5359.215 Electron/22.3.9 Safari/537.36",
    "sec-ch-ua-platform": "Windows",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip",
    "Accept-Language": "zh-CN"
}
headers2 = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
}
data_dir = myLib.MyLib().data_dir


def load_response_json(response, name):
    raw_text = response.text.strip()
    debug_dir = f'{data_dir}/response'
    os.makedirs(debug_dir, exist_ok=True)
    debug_file = f'{debug_dir}/{name}_raw.txt'
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(raw_text)

    cleaned_text = raw_text.lstrip('\ufeff').strip()
    decoder = json.JSONDecoder()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        start_candidates = [index for index in [cleaned_text.find('{'), cleaned_text.find('[')] if index >= 0]
        if start_candidates:
            start_index = min(start_candidates)
            json_text = cleaned_text[start_index:]
            try:
                parsed_data, _ = decoder.raw_decode(json_text)
                return parsed_data
            except json.JSONDecodeError:
                pass

        raise ValueError(f'Invalid JSON response saved to {debug_file}')

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
    #response = requests.get("https://app.txcfgl.com/api/app/subject/top-history?pageNum=1&pageSize=40", headers=headers, files=None, verify=False)
    response = requests.get("http://111.170.164.89:600/ticailishi?page=1&pageSize=40", headers=headers2, timeout=15)
    if response.status_code == 200:
        data = load_response_json(response, 'ticailishi')
        print(data)
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
    #response = requests.get(f"https://app.txcfgl.com/api/app/subject/child-stock-tree/{subject_id}", headers=headers, files=None, verify=False)
    response = requests.get(f"http://111.170.164.89:600/ticaitupu?id={subject_id}", headers=headers2, timeout=15)
    print(response.text)
    if response.status_code == 200:
        try:
            data = load_response_json(response, f'ticaitupu_{subject_id}')
        except ValueError:
            print(f'跳过非JSON题材响应: {subject_id}')
            return None
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

sql = f"""update subject_stock s_main \
    INNER JOIN ( \
        SELECT t1.title, r.stock_code, r.stock_name \
        FROM (SELECT  t.title, t.trade_date, t.change_percent \
            FROM tmp_subject_stock t \
            WHERE t.title IN ( \
                SELECT s.title \
                FROM subject_stock s \
                JOIN tmp_subject_stock t ON s.title = t.title  \
                WHERE s.stock_name LIKE '%****%' \
                GROUP BY s.title \
                HAVING COUNT(*) > 2 \
            ) \
            AND ( \
                SELECT COUNT(*)  \
                FROM tmp_subject_stock t2 \
                WHERE t2.title = t.title AND t2.trade_date >= t.trade_date \
            ) <= 3  \
        ) t1 \
        INNER JOIN tmp_stock_real r  \
            ON r.trade_date = t1.trade_date  \
            AND round(r.change_percent,2) = CAST(REPLACE(t1.change_percent, '%', '') AS DECIMAL(10,2))   \
        GROUP BY t1.title, r.stock_code,r.stock_name \
        HAVING COUNT(*) = 3 \
    ) t_target ON s_main.title = t_target.title \
    SET s_main.stock_code = t_target.stock_code, \
        s_main.stock_name  = t_target.stock_name;"""
tools.Tools().db_exec(sql)

subject_stock_df = tools.Tools().db_query('select * from subject_stock')
column_mapping = {'stock_code': '代码', 'stock_name': '名称', 'title': '备注'}
subject_stock_df = subject_stock_df.rename(columns=column_mapping)
subject_stock_df['备注'] = subject_stock_df['备注'].str.replace(',', '').str.replace(' ', '')

popu_df = model.get_cond_popu_stocks(351)
popu_df = popu_df.drop(columns=['名称'])
popu_df = popu_df.drop(columns=['涨幅'])
message_df = get_messages()
if message_df is not None:
    message_df2 = message_df
    print(message_df2)
    column_mapping = {"时间": "create_time", "题材ID": "category_code", "题材": "category_name", "涨幅": "pct_chg", "内容": "description"}
    message_df2 = message_df2.rename(columns=column_mapping)
    message_df2['pct_chg'] = pd.to_numeric(message_df2['pct_chg'].astype(str).str.replace('%', ''), errors='coerce')
    tools.Tools().db_upsert(message_df2, 'subject_message', 'create_time', 'subject_id')
    for index, item in message_df.iterrows():
        item_content = f"{item['时间']} {item['题材']} {item['涨幅']} {item['内容'].replace(' ','').replace('\n','')}"
        print(item_content)
        with open(file_name, 'a', encoding='utf-8') as f:
            f.write(f'<h4>{item_content}</h4>\n')
        subject_id = item['题材ID']
        time.sleep(1)
        content = get_subjects(subject_id)
        if not content:
            continue
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
                    column_mapping = {'代码': 'stock_code', '名称': 'stock_name', '备注': 'title'}
                    new_data = new_data.rename(columns=column_mapping)
                    tools.Tools().db_upsert(new_data, 'subject_stock', 'stock_code', 'title')

                subject_info_null = subject_info[subject_info['名称_y'].isnull() | (subject_info['名称_y'] == '****')]
                subject_info_null = subject_info_null[subject_info_null['备注']!='']
                subject_info_null = subject_info_null.drop_duplicates(subset=['备注']) 
                current_time = datetime.datetime.now().time()
                if subject_info_null is not None and not subject_info_null.empty and current_time >= datetime.datetime.strptime('16:30:00', '%H:%M:%S').time():                                  
                    new_data = subject_info_null[['代码_x', '名称_x', '备注', '涨幅']].rename(columns={'代码_x': '代码', '名称_x': '名称'})
                    new_data['trade_date'] = trade_date
                    
                    column_mapping = {'代码': 'stock_code', '名称': 'stock_name', '备注': 'title', '涨幅': 'change_percent', '时间': 'trade_date'}
                    new_data = new_data.rename(columns=column_mapping)
                    tools.Tools().db_upsert(new_data, 'tmp_subject_stock', 'trade_date', 'title')
                    tools.Tools().db_exec(f"delete from tmp_subject_stock   where create_time < NOW() - INTERVAL 30 DAY")

                subject_info = subject_info.drop(columns=['代码_x', '名称_x','代码_y', '名称_y'])  
                df = pd.concat( [df, subject_info], ignore_index=True)

        subject_first = (
            df.reindex(columns=['子类', '分类', '题材'])
            .replace('', pd.NA)
            .bfill(axis=1)
            .iloc[:, 0]
        )
        subject_ids = subject_first.dropna().drop_duplicates().tolist()
        tools.Tools().db_exec(f"delete from subject_info where category_code ={item['题材ID']}")
        
        df2 = df
        print(df2)
        new_order = ['代码','名称','备注','理由']
        df2 = df2.reindex(columns=new_order)
        df2['category_code'] = item['题材ID']
        df2['category'] = item['题材']
        column_mapping = {'代码': 'stock_code', '名称': 'stock_name', '理由': 'reason', '备注': 'remarks'}
        df2 = df2.rename(columns=column_mapping)
        tools.Tools().db_batchinset(df2, 'subject_info')

        if not df.empty:
            stock_codes = df['代码'].drop_duplicates().tolist()
            df_raise = model.calc_raise_rate_new(stock_codes)
            column_mapping = {'stock_code': '代码', 'support_line': '支撑线', 'resis_line': '压力线', 'is_limitup': '涨停'}     
            df_raise = df_raise.rename(columns=column_mapping)

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
