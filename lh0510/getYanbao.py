import requests
from datetime import date,datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import myLib
import json
import re
import tools

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
today = date.today()
for i in range(-4, 2):
    start_date = today + timedelta(days=i)
    end_date = today + timedelta(days=i+1)
    df = myClass.get_indYanbao(start_date.strftime("%Y%m%d"),end_date.strftime("%Y%m%d"))
    if not df.empty:
        column_mapping = {'时间': 'report_date', '名称': 'industry', '机构': 'org', '标题': 'title'}
        df = df.rename(columns=column_mapping)
        tools.Tools().db_upsert(df,'yanbao_ind','report_date','title')
        
    df = myClass.get_stockYanbao(start_date.strftime("%Y%m%d"),end_date.strftime("%Y%m%d"))
    if not df.empty:
        column_mapping = {'时间': 'report_date', '代码': 'stock_code', '名称': 'stock_name', '评级': 'rating', '标题': 'title'}
        df = df.rename(columns=column_mapping)
        tools.Tools().db_upsert(df,'yanbao_stock','report_date','title')