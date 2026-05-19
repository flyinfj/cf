import requests
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import myLib
class GetCaibao:
    def get_caibao(self,start_date):
        start_date = datetime.strptime(start_date, "%Y%m%d")
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date= start_date + timedelta(days=5)
        end_date_str = end_date.strftime("%Y-%m-%d")
        url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_REMIND_PUBLICFNCBXL&columns=SECUCODE,SECURITY_CODE,SECURITY_INNER_CODE,ORG_CODE,NOTICE_DATE,EVENT_TYPE,EVENT_TYPE_CODE,SPECIFIC_EVENTTYPE,LEVEL1_CONTENT&quoteColumns=f14&sortTypes=1,1&sortColumns=NOTICE_DATE,SECUCODE&filter=(NOTICE_DATE>=\'{start_date_str}\')(NOTICE_DATE<\'{end_date_str}\')&source=SECURITIES&client=APP&pageNumber=1&pageSize=100'
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
today = date.today().strftime("%Y%m%d")
df = myClass.get_caibao(today)
df = df[['SECURITY_CODE','f14',  'NOTICE_DATE', 'EVENT_TYPE', 'LEVEL1_CONTENT']]
df['NOTICE_DATE'] = df['NOTICE_DATE'].str.replace(' 00:00:00', '')
file_name = f"{model.filedir_database}/caibao.txt"
df.to_csv(file_name, mode='a', header=True, index=False, sep='\t')
df_all = pd.read_csv(file_name, sep='\t')
df_all = df_all.drop_duplicates(subset=['SECURITY_CODE', 'EVENT_TYPE' ,'NOTICE_DATE'],keep='last')
df_all.to_csv(file_name, mode='w', header=True, index=False, sep='\t')

df = df[df['SECURITY_CODE'].apply(lambda x: x.startswith(('30', '60', '0')))]
df = df[~df['LEVEL1_CONTENT'].str.contains('亏|下降|预减')]
df = df[['SECURITY_CODE','EVENT_TYPE','LEVEL1_CONTENT','NOTICE_DATE']]
df.rename(columns={'SECURITY_CODE':'代码','NOTICE_DATE':'公告时间','EVENT_TYPE':'类型','LEVEL1_CONTENT':'业绩'}, inplace=True)
# 获取涨幅
stock_codes = df['代码'].tolist()
df_raise = model.get_stock_data(stock_codes)
# 合并
df = pd.merge(df,df_raise, on='代码', how='left')
df['涨幅'] = df['涨幅'].apply(lambda x: f"{x}%")
df['业绩'] = df['业绩'].str.ljust(200)

#输出各种业绩
df_pre = df[df['类型'] == '业绩预告']
pattern = r'上升(\d+\.\d+)%.*?上升(\d+\.\d+%)'
pd.options.mode.chained_assignment = None  # 禁用警告
df_pre[['利润','收益']] = df_pre['业绩'].str.extract(pattern)
df_pre['利润'] = pd.to_numeric(df_pre['利润'], errors='coerce')
df_pre = df_pre.sort_values(by=['利润'], ascending=[False])
df_pre['利润'] = df_pre['利润'].apply(lambda x: f"{x}%")
df_pre = df_pre[['代码', '名称',  '涨幅', '换手', '量比', '类型', '利润', '收益', '公告时间','业绩']]
print(model.beautify(df_pre))
model.output_file(df_pre,'业绩预告')

df_quk = df[df['类型'] == '业绩快报']
df_quk = df_quk[['代码', '名称',  '涨幅', '换手', '量比', '类型', '公告时间','业绩']]
print(model.beautify(df_quk))
model.output_file(df_quk,'业绩快报')
