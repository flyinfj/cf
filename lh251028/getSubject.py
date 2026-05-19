import os
import json
import pandas as pd
import myLib

#解析股票信息
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

pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度
pd.set_option('display.colheader_justify', 'center')
model = myLib.MyLib()
# 列出目录下的所有文件


directory = f"{model.data_dir}/response"
print(directory)
files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
df = pd.DataFrame()

for file_name in files:
    file_path = os.path.join(directory, file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
        if 'data' in content and content['data']:
            for subject in content['data']:
                print(subject)
                subject_info = parse_subject(subject)
                df = pd.concat( [df, subject_info], ignore_index=True)
new_order = ['编码', '题材', '分类', '子类','代码', '名称', '理由', '备注']
df = df.reindex(columns=new_order)
print(df)

file_name =  f'{model.data_dir}/database/subject.csv'
df.to_csv(file_name, index=False, sep=',', quoting=1, encoding='UTF-8', escapechar='\\')
