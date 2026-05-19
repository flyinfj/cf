import requests
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import myLib
import os
from openai import OpenAI
import json
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

    def get_chat(self,context):
        client = OpenAI(
            api_key="sk-f6517b7c4f3f4d2b9ab2292a6e13a261",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {'role': 'system', 'content': f'{context}'}],
        )
        data = json.loads(completion.model_dump_json())
        data = data['choices'][0]['message']['content']
        data = data.replace('```json', '').replace('```', '')
        try:
            data = json.loads(data)
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            print(data)
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
file_name = f"{model.filedir_database}/caibao.txt"
today = date.today()
for i in range(-4, 2):
    start_date = today + timedelta(days=i)
    end_date = today + timedelta(days=i+1)
    df = myClass.get_caibao(start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
    if not df.empty:
        df = df[['SECURITY_CODE','f14',  'NOTICE_DATE', 'EVENT_TYPE', 'LEVEL1_CONTENT']]
        df['NOTICE_DATE'] = df['NOTICE_DATE'].str.replace(' 00:00:00', '')
        df.rename(columns={'SECURITY_CODE':'代码','f14':'名称','NOTICE_DATE':'公告时间','EVENT_TYPE':'类型','LEVEL1_CONTENT':'公告内容'}, inplace=True)
        df.to_csv(file_name, mode='a', header=True, index=False, sep='\t')
        df_all = pd.read_csv(file_name, sep='\t')
        df_all['代码'] = df_all['代码'].astype(str).str.zfill(6)
        df_all = df_all.drop_duplicates(subset=['代码', '类型' ,'公告时间'],keep='last')
        df_all.to_csv(file_name, mode='w', header=True, index=False, sep='\t')

# 获取近期的财报数据
end_date = today + timedelta(days=3)
df = myClass.get_caibao(today.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
df = df[df['SECURITY_CODE'].apply(lambda x: x.startswith(('30', '60', '0')))]
df = df[~df['LEVEL1_CONTENT'].str.contains('亏|下降|预减')]
df['f14'] = df['f14'].astype(str).fillna('')
df = df[~df['f14'].str.contains('ST')]
df = df[['SECURITY_CODE','EVENT_TYPE','LEVEL1_CONTENT','NOTICE_DATE']]
df['NOTICE_DATE'] = df['NOTICE_DATE'].str.replace(' 00:00:00', '')
df.rename(columns={'SECURITY_CODE':'代码','NOTICE_DATE':'公告时间','EVENT_TYPE':'类型','LEVEL1_CONTENT':'公告内容'}, inplace=True)

stock_codes = df['代码'].tolist()
result_dfs = pd.DataFrame()
df_all = pd.read_csv(file_name, sep='\t')
df_all['代码'] = df_all['代码'].astype(str).str.zfill(6)
json_example = '''
    [
        {
            "代码": "000001",
            "Q3_R": 0,
            "Q3_RR": 0,
            "Q3_P": 20,
            "Q3_PR": 30,
            "Y_R": 0,
            "Y_RR": 0,
            "Y_P": 20,
            "Y_PR": 30,
            "Q1_R": 0,
            "Q1_RR": 0,
            "Q1_P": 0,
            "Q1_PR": 0
        }
    ]
'''
contents=''
batch_size = 10
result_dfs = pd.DataFrame()
for i in range(0, len(stock_codes), batch_size):
    batch_codes = stock_codes[i:i + batch_size]
    contents = ""
    for stock_code in batch_codes:
        stock_df = df_all[df_all['代码'] == stock_code].tail(6)
        cstr = "\n".join([f"{stock_code} : {content}" for content in stock_df["公告内容"].astype('str')])
        contents = f'{contents}\n{cstr}'
    # 构建提示语
    prompt = f'''
    请根据以下信息，输出所有股票的代码 CODE、2024 年第三季度营收 Q3_R、2024 年第三季度营收涨幅 Q3_RR、2024 年第三季度净利润 Q3_P、2024 年第三季度净利润涨幅 Q3_PR、2024 年全年营收 Y_R、2024 年全年营收涨幅 Y_RR、2024 年全年净利润 Y_P、2024 年全年净利润涨幅 Y_PR、2025 年第一季度营收 Q1_R、2025 年第一季度营收涨幅 Q1_RR、2025 年第一季度净利润 Q1_P、2025 年第一季度净利润涨幅 Q1_PR。
    说明:
    1. 无法获取的数据用 "0" 表示。
    2. 营收和净利润单位均为亿元，涨幅单位为%，均只保留整数部分。
    3. 输出结果为 JSON 格式，只需要 JSON 信息，不需要其他任何推理信息，格式如下：
    {json_example}
    数据来源:
    {contents}
    '''
    result_df = myClass.get_chat(prompt)
    if not result_df.empty:
        result_dfs = pd.concat([result_dfs, result_df], ignore_index=True)

# 合并结果到原数据框
df = pd.merge(df, result_dfs, on='代码', how='left')

# 获取涨幅
stock_codes = df['代码'].tolist()
df_raise = model.get_stock_data(stock_codes)
# 合并
df = pd.merge(df,df_raise, on='代码', how='left')
df['涨幅'] = df['涨幅'].apply(lambda x: f"{x}%")
df['公告内容'] = df['公告内容'].str.ljust(200)
new_order = ['代码','名称','类型','公告时间','涨幅','Q3_R', 'Q3_RR', 'Q3_P', 'Q3_PR','Y_R', 'Y_RR', 'Y_P', 'Y_PR','Q1_R', 'Q1_RR', 'Q1_P', 'Q1_PR', '公告内容']
df = df[new_order]
df = df[(df["Y_RR"] > 30) | (df["Y_PR"] > 30) | (df["Q3_PR"] > 30) | (df["Q3_RR"] > 30)]
df['Q3_RR'] = df['Q3_RR'].apply(lambda x: f"{x}%")
df['Q3_PR'] = df['Q3_PR'].apply(lambda x: f"{x}% | ")
df['Y_RR'] = df['Y_RR'].apply(lambda x: f"{x}%")
df['Y_PR'] = df['Y_PR'].apply(lambda x: f"{x}% | ")
df['Q1_RR'] = df['Q1_RR'].apply(lambda x: f"{x}%")
df['Q1_PR'] = df['Q1_PR'].apply(lambda x: f"{x}%")
print(df)

#输出各种业绩
df_pre = df[df['类型'] == '业绩预告']
pattern = r'上升(\d+\.\d+)%.*?上升(\d+\.\d+%)'
pd.options.mode.chained_assignment = None  # 禁用警告
df_pre[['利润','收益']] = df_pre['公告内容'].str.extract(pattern)
df_pre['利润'] = pd.to_numeric(df_pre['利润'], errors='coerce')
df_pre = df_pre.sort_values(by=['利润'], ascending=[False])
df_pre['利润'] = df_pre['利润'].apply(lambda x: f"{x}%")
df_pre = df_pre[['代码', '名称',  '涨幅', '类型', '利润', '收益', '公告时间','公告内容']]
print(model.beautify(df_pre))
model.output_file(df_pre,'业绩预告')

df_quk = df[df['类型'] == '业绩快报']
df_quk = df_quk[['代码', '名称',  '涨幅', '类型', '公告时间','公告内容']]
print(model.beautify(df_quk))
model.output_file(df_quk,'业绩快报')
