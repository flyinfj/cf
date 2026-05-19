import requests
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import myLib
import os
import json
import ast
import tools
import time
def _sanitize_json_text(text: str) -> str:
    s = str(text)
    out = []
    in_str = False
    esc = False
    for ch in s:
        if in_str:
            if esc:
                out.append(ch)
                esc = False
            else:
                if ch == '\\\\':
                    out.append(ch)
                    esc = True
                elif ch == '\"':
                    out.append(ch)
                    in_str = False
                elif ch == '\n' or ch == '\r':
                    out.append('\\\\n')
                elif ch == '\t':
                    out.append('\\\\t')
                else:
                    out.append(ch)
        else:
            out.append(ch)
            if ch == '\"':
                in_str = True
    return ''.join(out)

class GetCaibao:
    def get_caibao(self,start_date,end_date):
        start_date = datetime.strptime(start_date, "%Y%m%d")
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date= datetime.strptime(end_date, "%Y%m%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_REMIND_PUBLICFNCBXL&columns=SECUCODE,SECURITY_CODE,SECURITY_INNER_CODE,ORG_CODE,NOTICE_DATE,EVENT_TYPE,EVENT_TYPE_CODE,SPECIFIC_EVENTTYPE,LEVEL1_CONTENT&quoteColumns=f14&sortTypes=1,1&sortColumns=NOTICE_DATE,SECUCODE&filter=(NOTICE_DATE>=\'{start_date_str}\')(NOTICE_DATE<\'{end_date_str}\')&source=SECURITIES&client=APP&pageNumber=1&pageSize=500'
        #url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_REMIND_PUBLICFNCBXL&columns=SECUCODE,SECURITY_CODE,SECURITY_INNER_CODE,ORG_CODE,NOTICE_DATE,EVENT_TYPE,EVENT_TYPE_CODE,SPECIFIC_EVENTTYPE,LEVEL1_CONTENT&quoteColumns=f14&sortTypes=1,1&sortColumns=NOTICE_DATE,SECUCODE&filter=(NOTICE_DATE>=\'2025-01-15\')&source=SECURITIES&client=APP&pageNumber=1&pageSize=100'
        response_data = requests.get(url)
        data = response_data.json()
        try:
            df = pd.DataFrame(data.get('result', {}).get('data', []))
            return df
        except:
            return pd.DataFrame()


pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
pd.set_option('display.precision', 10)  # 设置数值的显示精度
pd.set_option('display.colheader_justify', 'center')

# 获取近期的财报数据
model = myLib.MyLib()
myClass = GetCaibao()
today = date.today()
for i in range(-4, 2):
    start_date = today + timedelta(days=i)
    end_date = today + timedelta(days=i+1)
    df = myClass.get_caibao(start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
    if not df.empty:
        df = df[['SECURITY_CODE','f14',  'NOTICE_DATE', 'EVENT_TYPE', 'LEVEL1_CONTENT']]
        df['NOTICE_DATE'] = df['NOTICE_DATE'].str.replace(' 00:00:00', '')
        df.rename(columns={'SECURITY_CODE':'代码','f14':'名称','NOTICE_DATE':'公告时间','EVENT_TYPE':'类型','LEVEL1_CONTENT':'公告内容'}, inplace=True)
        column_mapping = {'代码': 'stock_code', '名称': 'stock_name', '公告时间': 'notice_time', '类型': 'type', '公告内容': 'content'}
        df = df.rename(columns=column_mapping)
        df['notice_time_type'] = df['notice_time'] + df['type']
df_db = tools.Tools().db_query(f"select * from caibao_info where notice_time >= '{start_date.strftime("%Y-%m-%d")}'")
print(df_db)
if not df_db.empty:
    key_cols = ['stock_code', 'notice_time_type']
    df_db = df_db[key_cols].drop_duplicates()
    existing_keys = pd.MultiIndex.from_frame(df_db[key_cols].astype(str))
    current_keys = pd.MultiIndex.from_frame(df[key_cols].astype(str))
    df = df[~current_keys.isin(existing_keys)]
    print(df)
if not df.empty: 
    contents = df[['stock_code','notice_time_type','content']].drop_duplicates().to_string(index=False, header=False)
    contents = "股票编码 公告类型 公告内容\n" + contents
    json_example = '''
    [
        {
            "stock_code": "000001",
            "notice_time_type": "20250101年报",
            "period": "年报",
            "year": "2025",
            "month": "12"
            "R": "20",
            "P": "30",
            "RR": 0,
            "PR": 30
        }
    ]
    '''

    # 构建提示语
    prompt = f'''
    # 角色
    你是专业的股票数据分析师，专注于从结构化数据中精准提取和整理股票财务信息，能按照用户指定的JSON格式输出包含股票代码、关键财务指标及多周期变化的分析结果。
    # 要求
    根据【contents】中的股票数据内容，提取以下字段并生成指定格式的JSON数组：
    1. 股票代码stock_code、公告类型notice_time_type、周期period（年报/季报）、年份year、月份month、营收（R，单位：亿元，整数）、营收涨幅（RR，单位：%，整数）、利润（P，单位：亿元，整数）、利润涨幅（PR，单位：%，整数）  
    2. 周期period的枚举值为年报、季报,认真分析公告内容，确实是年报，还是Q1/Q2/Q3/Q4的季报
    3. 年份year(公告内容涉及的年份)、月份month(公告内容涉及的月份，年报对应12月，Q1季报对应3月，Q2季报对应6月，Q3季报对应9月，Q4季报对应12月)
    # 限制
    1. 数据缺失处理**：若【contents】中无对应字段（如无季度数据），直接用''填充
    2. 数值精度：R和P保留整数（单位：亿元），RR和PR保留整数（单位：%），无法获取数据时强制填''
    3. **输出约束**：仅返回指定JSON数组，不包含任何解释性文本、Markdown格式或非JSON内容
    # 输出格式：
    严格按照以下JSON模板输出，无任何额外说明或推理内容：
    {json_example}
    #【contents】:
    {contents}
    '''
    print(prompt)
    result = model.get_chat(prompt)           
    if isinstance(result, pd.DataFrame):
        result_df = result
    else:
        try:
            parsed = json.loads(_sanitize_json_text(result))
        except Exception:
            parsed = ast.literal_eval(_sanitize_json_text(result))
        result_df = pd.DataFrame(parsed)
    print(result_df)
    if not result_df.empty:
        print(df)
        df = pd.merge(df, result_df, on=['stock_code','notice_time_type'], how='left')
        print(df)
        tools.Tools().db_upsert(df, "caibao_info", key1="stock_code", key2="notice_time_type")  
sql = f"""
    SELECT 
    ci.stock_code,ci.stock_name,
    CONCAT(ci.notice_time,'\n',ci.type) notice_time_type,
    CONCAT(ci.period,'\n',ci.year,ci.month) period_year_month,
    CONCAT(ci.R, '|', ci.P) R_P,
    CONCAT(ci.RR, '%|', ci.PR, '%') RR_PR,
    t2.Q_R,
    t4.Y_R,
    ci.content
    FROM caibao_info ci
    LEFT JOIN (
    SELECT 
        stock_code,
        CONCAT(
        GROUP_CONCAT(month ORDER BY year DESC, month DESC SEPARATOR ', '), '\n',
        GROUP_CONCAT(RR ORDER BY year DESC, month DESC SEPARATOR '%, '), '%\n',
        GROUP_CONCAT(PR ORDER BY year DESC, month DESC SEPARATOR '%, '), '%'
        ) AS Q_R
    FROM (
        SELECT 
        c.stock_code,
        c.year,
        c.month,
        c.RR,
        c.PR
        FROM caibao_info c
        INNER JOIN (
        SELECT stock_code, year, month, MAX(notice_time) max_time
        FROM caibao_info
        WHERE period = '季报'
        GROUP BY stock_code, year, month
        order by year, month desc 
        limit 3
        ) tmp 
        ON c.stock_code = tmp.stock_code 
        AND c.year = tmp.year 
        AND c.month = tmp.month 
        AND c.notice_time = tmp.max_time
        WHERE c.period = '季报'
    ) t1
    GROUP BY stock_code
    ) t2 ON ci.stock_code = t2.stock_code
    LEFT JOIN (
    SELECT 
        stock_code,
        CONCAT(
        GROUP_CONCAT(month ORDER BY year DESC, month DESC SEPARATOR ', '), '\n',
        GROUP_CONCAT(RR ORDER BY year DESC, month DESC SEPARATOR '%, '), '%\n',
        GROUP_CONCAT(PR ORDER BY year DESC, month DESC SEPARATOR '%, '), '%'
        ) AS Y_R
    FROM (
        SELECT 
        c.stock_code,
        c.year,
        '' month,
        c.RR,
        c.PR
        FROM caibao_info c
        INNER JOIN (
        SELECT stock_code, year, month, MAX(notice_time) max_time
        FROM caibao_info
        WHERE period = '年报'
        GROUP BY stock_code, year, month
        order by year, month desc 
        limit 1
        ) tmp 
        ON c.stock_code = tmp.stock_code 
        AND c.year = tmp.year 
        AND c.month = tmp.month 
        AND c.notice_time = tmp.max_time
        WHERE c.period = '年报'
    ) t3
    GROUP BY stock_code
    ) t4 ON ci.stock_code = t4.stock_code
    WHERE ci.notice_time >= '{start_date.strftime("%Y-%m-%d")}'
  """
df = tools.Tools().db_query(sql)
df.rename(columns={'stock_code': '代码'}, inplace=True)
df.rename(columns={'stock_name': '名称'}, inplace=True)
df.rename(columns={'notice_time_type': '公告类型'}, inplace=True)
df.rename(columns={'period_year_month': '周期'}, inplace=True)
df.rename(columns={'R_P': '营收/利润'}, inplace=True)
df.rename(columns={'RR_PR': '营收/利润比'}, inplace=True)
df.rename(columns={'Q_R': '近三季度财报'}, inplace=True)
df.rename(columns={'Y_R': '最近一年财报'}, inplace=True)
df.rename(columns={'content': '公告内容'}, inplace=True)
current_month = datetime.now().month
print(df)
model.output_file(df,'业绩预测',0)

#输出各种业绩
sql = f"SELECT stock_code,stock_name,type,RR,PR,notice_time,content  FROM caibao_info WHERE type = '业绩预告' and (RR > 0 or PR > 0) AND notice_time >= '{start_date.strftime('%Y-%m-%d')}'"
df = tools.Tools().db_query(sql)
if not df.empty:
    df.rename(columns={'stock_code': '代码'}, inplace=True)
    df.rename(columns={'stock_name': '名称'}, inplace=True)
    df.rename(columns={'type': '公告类型'}, inplace=True)
    df.rename(columns={'RR': '营收比'}, inplace=True)
    df.rename(columns={'PR': '利润比'}, inplace=True)
    df.rename(columns={'notice_time': '公告时间'}, inplace=True)
    df.rename(columns={'content': '公告内容'}, inplace=True)
    print(model.beautify(df))
    model.output_file(df,'业绩预告')

sql = f"SELECT stock_code,stock_name,type,RR,PR,notice_time,content  FROM caibao_info WHERE type = '业绩快报' and (RR > 0 or PR > 0) AND notice_time >= '{start_date.strftime('%Y-%m-%d')}'"
df = tools.Tools().db_query(sql)
if not df.empty:
    df.rename(columns={'stock_code': '代码'}, inplace=True)
    df.rename(columns={'stock_name': '名称'}, inplace=True)
    df.rename(columns={'type': '公告类型'}, inplace=True)
    df.rename(columns={'RR': '营收比'}, inplace=True)
    df.rename(columns={'PR': '利润比'}, inplace=True)
    df.rename(columns={'notice_time': '公告时间'}, inplace=True)
    df.rename(columns={'content': '公告内容'}, inplace=True)
    print(model.beautify(df))
    model.output_file(df,'业绩快报')
