import requests
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import myLib
import json
import re

class GetYanbao:
    def get_indYanbao(self,start_date,end_date):
        start_date = datetime.strptime(start_date, "%Y%m%d")
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y%m%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        url =f'https://reportapi.eastmoney.com/report/list?cb=datatable8614195&industryCode=*&pageSize=1000&industry=*&rating=*&ratingChange=*&beginTime={start_date_str}&endTime={end_date_str}&pageNo=1&fields=&qType=1&orgCode=&rcode=&p=1&pageNum=1&pageNumber=1&_=1742723291613'
        response_data = requests.get(url)
        response_data = response_data.content.decode('utf-8')
        # 使用正则提取JSON数据
        json_str = re.search(r'\((.*?})\)', response_data).group(1)
        data = json.loads(json_str)
        try:
            df = pd.DataFrame(data.get('data', {}))
            df = df[['publishDate','industryName','orgSName','title']]
            df['publishDate'] = df['publishDate'].astype('string').str.replace(' 00:00:00.000', '')  # 添加类型转换
            df = df.rename(columns={'publishDate':'时间','industryName':'名称','orgSName':'机构','title':'标题'})
            return df
        except:
            return pd.DataFrame()

    def get_stockYanbao(self,start_date,end_date):
        start_date = datetime.strptime(start_date, "%Y%m%d")
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y%m%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        url = f'https://reportapi.eastmoney.com/report/list2'
        data = {
            "beginTime": start_date_str,
            "endTime": end_date_str,
            "industryCode": "*",
            "ratingChange": '',
            "rating": '',
            "orgCode": '',
            "code": "*",
            "rcode": "",
            "pageSize": 1000,
            "p": 1,
            "pageNo": 1,
            "pageNum": 1,
            "pageNumber": 1
        }
        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'content-length': '101',
            'content-type': 'application/json',
            'origin': 'https://vipmoney.eastmoney.com',
            'referer': 'https://vipmoney.eastmoney.com/',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57'
        }
        res = requests.post(url=url, data=json.dumps(data), headers=headers)
        text = res.json()
        try:
            df = pd.DataFrame(text['data'])
            df = df[['publishDate','stockCode','stockName','emRatingName','title']]
            df['publishDate'] = df['publishDate'].astype('string').str.replace(' 00:00:00.000', '')
            df = df.rename(columns={'publishDate':'时间','stockCode':'代码','stockName':'名称','emRatingName':'评级','title':'标题'})
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
myClass = GetYanbao()
file_name = f"{model.filedir_database}/caibao.txt"
file_name_ind = f"{model.filedir_database}/yanbao_ind.txt"
file_name_stock = f"{model.filedir_database}/yanbao_stock.txt"
today = date.today()
for i in range(-4, 2):
    start_date = today + timedelta(days=i)
    end_date = today + timedelta(days=i+1)
    df = myClass.get_indYanbao(start_date.strftime("%Y%m%d"),end_date.strftime("%Y%m%d"))
    if not df.empty:
        df.to_csv(file_name_ind, mode='a', header=False, index=False, sep='\t')
        df_all = pd.read_csv(file_name_ind, sep='\t')
        df_all = df_all.drop_duplicates(subset=['名称' ,'机构' ,'时间'],keep='last')
        df_all = df_all.sort_values(by=['时间'], ascending=False)
        df_all.to_csv(file_name_ind, mode='w', header=True, index=False, sep='\t')

    df = myClass.get_stockYanbao(start_date.strftime("%Y%m%d"),end_date.strftime("%Y%m%d"))
    if not df.empty:
        df.to_csv(file_name_stock, mode='a', header=False, index=False, sep='\t')
        df_all = pd.read_csv(file_name_stock, sep='\t')
        df_all['代码'] = df_all['代码'].astype(str).str.zfill(6)
        df_all = df_all.drop_duplicates(subset=['代码' ,'时间'],keep='last')
        df_all = df_all.sort_values(by=['时间'], ascending=False)
        df_all.to_csv(file_name_stock, mode='w', header=True, index=False, sep='\t')