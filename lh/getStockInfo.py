import requests
import re
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import myLib
import tools

class GetStockInfo:
    def __init__(self, market='A', globalId='786e4c21-70dc-435a-93bb-38'):
        self.globalId = globalId
        self.market = market
        self.filedir_database = f'{myLib.MyLib().data_dir}/database'
        self.filedir_data = f'{myLib.MyLib().data_dir}/data'
        self.filedir_tmp = f'{myLib.MyLib().data_dir}/tmp'
    #转换股票代码
    def generate_market_code(self, stock_code):
        if stock_code.startswith('1.') or stock_code.startswith('0.'):
            return stock_code
        if stock_code[:2] == "60":
            return '1.' + stock_code
        else:
            return '0.' + stock_code

    # 转换股票代码
    def generate_market_code2(self, stock_code):
        if stock_code[:2] == "60":
            return stock_code + '.SH'
        else:
            return stock_code + '.SZ'

    # 获取上个季度最后一天日期
    def get_last_quarter_day(self, stock_code):
        stock_code=self.generate_market_code2(stock_code)
        url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_EH_EQUITY&columns=SECUCODE,END_DATE&filter=(SECUCODE=\"{stock_code}\")&client=APP&source=SECURITIES&sr=-1&st=END_DATE&rdm=rnd_2AB178C36804404781CD0D7BE22CEE7A&v=08002266363218766"
        response_data = requests.get(url)
        data = response_data.json()
        df = pd.DataFrame(data.get('result', {}).get('data', []))
        end_date = pd.to_datetime(df['END_DATE'], errors='coerce').dropna().max()
        return end_date.strftime('%Y-%m-%d')

    #获取股东信息
    def get_holders(self,stockCode):
        url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_EH_EQUITY&columns=SECUCODE,END_DATE&filter=(SECUCODE=\"{stockCode}\")&client=APP&source=SECURITIES&sr=-1&st=END_DATE&rdm=rnd_2AB178C36804404781CD0D7BE22CEE7A&v=08002266363218766"
        response_data = requests.get(url)
        data = response_data.json()
        df = pd.DataFrame(data.get('result', {}).get('data', []))
        endDate = pd.to_datetime(df['END_DATE'], errors='coerce').dropna().max().strftime('%Y-%m-%d')
        
        #url = f'https://datacenter.eastmoney.com/securities/api/data/get?type=RPT_F10_EH_HOLDERS&sty=SECUCODE,END_DATE,HOLDER_NAME,HOLDER_CODE,HOLDER_CODE_OLD,HOLD_NUM,HOLD_NUM_RATIO,HOLD_RATIO_QOQ,HOLDER_RANK,IS_HOLDORG,HOLDER_NEW,NEW_CHANGE_RATIO&filter=(SECUCODE="{stockCode}")(END_DATE=\'{endDate}\')&client=APP&source=SECURITIES&pageNumber=1&pageSize=10&sr=1'
        url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_EH_EQUITY&columns=SECUCODE,END_DATE,CHANGE_REASON,TOTAL_SHARES,UNLIMITED_SHARES,LIMITED_SHARES,LISTED_SHARES_RATIO,LIMITED_SHARES_RATIO,UNLIMITED_SHARES_CHANGE,LIMITED_SHARES_CHANGE,TOTAL_SHARES_CHANGE,IS_FREE_WINDOW,IS_LIMITED_WINDOW&filter=(SECUCODE="{stockCode}")(END_DATE=\'{endDate}\')&client=APP&source=SECURITIES&rdm=rnd_6A2765B2066D47F689D618AEC276A0C0&v=0550904641596483'
        response_data = requests.get(url)
        data = response_data.json()
        try:
            df = pd.DataFrame(data.get('result', {}).get('data', []))
            return df
        except:
            return pd.DataFrame()

    #获取TOP10股东信息
    def get_topholders(self,stockCode):
        url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_EH_HOLDERS&columns=SECUCODE,END_DATE&filter=(SECUCODE=\"{stockCode}\")&client=APP&source=SECURITIES&sr=-1&st=END_DATE&rdm=rnd_2AB178C36804404781CD0D7BE22CEE7A&v=08002266363218766"
        response_data = requests.get(url)
        data = response_data.json()
        df = pd.DataFrame(data.get('result', {}).get('data', []))
        endDate = pd.to_datetime(df['END_DATE'], errors='coerce').dropna().max().strftime('%Y-%m-%d')
        url = f'https://datacenter.eastmoney.com/securities/api/data/get?type=RPT_F10_EH_HOLDERS&sty=SECUCODE,END_DATE,HOLDER_NAME,HOLDER_CODE,HOLDER_CODE_OLD,HOLD_NUM,HOLD_NUM_RATIO,HOLD_RATIO_QOQ,HOLDER_RANK,IS_HOLDORG,HOLDER_NEW,NEW_CHANGE_RATIO,HOLD_NUM_ABBR&filter=(SECUCODE="{stockCode}")(END_DATE=\'{endDate}\')&client=APP&source=SECURITIES&pageNumber=1&pageSize=200&sr=1&st=HOLDER_RANK&rdm=rnd_FAAEC481C6C74A6B94CC45EA056E06E9&v=03857312752562623'
        response_data = requests.get(url)
        data = response_data.json()
        print(data)
        try:
            df = pd.DataFrame(data.get('result', {}).get('data', []))
            return df
        except:
            return pd.DataFrame()

    #获取自由流通股东信息
    def get_freeholders(self,stockCode):
        url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_EH_FREEHOLDERS&columns=SECUCODE,END_DATE&filter=(SECUCODE=\"{stockCode}\")&client=APP&source=SECURITIES&sr=-1&st=END_DATE&rdm=rnd_2AB178C36804404781CD0D7BE22CEE7A&v=08002266363218766"
        response_data = requests.get(url)
        data = response_data.json()
        df = pd.DataFrame(data.get('result', {}).get('data', []))
        endDate = pd.to_datetime(df['END_DATE'], errors='coerce').dropna().max().strftime('%Y-%m-%d')

        url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_EH_FREEHOLDERS&columns=SECUCODE,END_DATE,HOLDER_NAME,HOLDER_CODE,HOLDER_CODE_OLD,HOLD_NUM,FREE_HOLDNUM_RATIO,FREE_RATIO_QOQ,IS_HOLDORG,HOLDER_RANK,HOLDER_NEW,NEW_CHANGE_RATIO&filter=(SECUCODE="{stockCode}")(END_DATE=\'{endDate}\')&client=APP&source=SECURITIES&pageNumber=1&pageSize=10&sr=1'
        response_data = requests.get(url)
        data = response_data.json()
        try:
            df = pd.DataFrame(data.get('result', {}).get('data', []))
            return df
        except:
            return pd.DataFrame()

    #获取机构持股
    def get_orgholders(self,stockCode):
        url = f"https://datacenter.eastmoney.com/securities/api/data/get?type=RPT_F10_MAIN_ORGHOLD&sty=REPORT_DATE,IS_COMPLETE&filter=(SECUCODE=\"{stockCode}\")&client=APP&source=SECURITIES&p=1&ps=200&sr=-1&st=REPORT_DATE&rdm=rnd_1882CDE7DF554BF78D44FB2DB5D00933&v=038116990279504126"
        response_data = requests.get(url)
        data = response_data.json()
        df = pd.DataFrame(data.get('result', {}).get('data', []))
        endDate = pd.to_datetime(df['REPORT_DATE'], errors='coerce').dropna().max().strftime('%Y-%m-%d')
        url = f'https://datacenter.eastmoney.com/securities/api/data/get?type=RPT_MAIN_ORGHOLDDETAIL&sty=SECURITY_CODE,REPORT_DATE,HOLDER_CODE,HOLDER_NAME,TOTAL_SHARES,HOLD_VALUE,FREESHARES_RATIO,ORG_TYPE,SECUCODE,FUND_DERIVECODE,FREE_SHARES&filter=(SECUCODE="{stockCode}")(REPORT_DATE=\'{endDate}\')&p=1&ps=200&sr=-1,1'
        response_data = requests.get(url)
        data = response_data.json()
        try:
            df = pd.DataFrame(data.get('result', {}).get('data', []))
            return df
        except:
            return pd.DataFrame()

    """ #获取收盘价
    def get_stock_close(self, stock_code):
        stock_codes_ad=self.generate_market_code(stock_code)
        url = f'https://push2.eastmoney.com/api/qt/ulist.np/get?ut=f057cbcbce2a86e2866ab8877db1d059&fltt=2&invt=2&fields=f14,f148,f3,f12,f2,f13,f29,f8,f10&secids={stock_codes_ad}'
        response_data = requests.get(url)
        print(response_data.status_code)
        if response_data.status_code != 200:
            return pd.DataFrame()
        else:
            print(response_data.text)
            try:
                data = response_data.json()['data']['diff']
                return data[0]['f2']
            except:
                return pd.DataFrame() 
    """
    def get_limitup_his(self,stockCodes):
        result = []
        for stockCode in stockCodes:
            df = tools.Tools().db_query(f"select * from days_limitup_count where stock_code = '{stockCode}'")
            column_mapping = {'rank_id': '涨停排序', 'stock_code': '代码', 'limitup_count': '涨停数', 'next_limitup_count': '第二天涨次数', 'avg_raise_percent': '平均涨幅'}
            df.rename(columns=column_mapping, inplace=True)
            if not df.empty:
                limit_up_sort = df['涨停排序'].values[0]
                limit_up_count = df['涨停数'].values[0]
                next_day_up_count = df['第二天涨次数'].values[0]
                avg_increase = f"{df['平均涨幅'].values[0]:.1f}%"
                next_day_up_ratio = round(next_day_up_count / limit_up_count * 100)
                result.append((stockCode, f'{limit_up_count}/{next_day_up_ratio}%/{avg_increase}'))
        return pd.DataFrame(result, columns=['代码', '涨停历史'])

    #获取股东信息
    def get_holder_info(self,stockCodes):

        all_df = tools.Tools().db_query(f"select stock_code 代码,concat(float_shares,'/',round(major_shares/float_shares*100,0),'%','/',round(org_shares/float_shares*100,0),'%') as 股本 \
            from quar_holder_info")

        result = pd.DataFrame()
        for stockCode in stockCodes:
            df = all_df[all_df['代码'] == stockCode]
            if not df.empty:
                result = pd.concat([result, df])
            else:
                #获取股票收盘价
                close_df = tools.Tools().db_query(f"select last_price from stock_real sr  where stock_code like '%{stockCode}' limit 1")
                close = float(close_df.iloc[0, 0] or 0)
                #获取股东、流通股东、机构信息
                stockCode = self.generate_market_code2(stockCode)
                holder_df = self.get_holders(stockCode)
                topholder_df = self.get_topholders(stockCode)
                freeholder_df = self.get_freeholders(stockCode)
                orgholder_df = self.get_orgholders(stockCode)

                #计算总股本、流通股本
                try:
                    first_holder = holder_df.iloc[0]
                    total_shares= round(close*float(first_holder['TOTAL_SHARES'])/100000000)
                    unlimited_shares = round(close*first_holder['UNLIMITED_SHARES']/100000000)
                except:
                    total_shares = 0
                    unlimited_shares = 0
                # 计算流通大股东股本
                try:
                    holder_df_5 = topholder_df[(topholder_df['HOLD_NUM_RATIO']>= 5) & (toppholder_df['IS_HOLDORG'] == 0)]
                    freeholder_df_5 = freeholder_df[freeholder_df['HOLDER_NAME'].isin(holder_df_5['HOLDER_NAME'])]
                    freeholder_5_num = round(close*freeholder_df_5['HOLD_NUM'].sum()/100000000)
                except:
                    freeholder_5_num = 0

                #计算流通机构数、机构股本
                try:
                    orgholder_df_5 = orgholder_df[~orgholder_df['HOLDER_NAME'].isin(freeholder_df_5['HOLDER_NAME'])]
                    orgholder_df_num = round(close*orgholder_df_5['TOTAL_SHARES'].sum()/100000000)
                except:
                    orgholder_df_num =0

                stockCode = re.sub(r'\.(SH|SZ|HK)$', '', stockCode)
                df = pd.DataFrame({
                    'stock_code': [stockCode],
                    'total_shares': [total_shares],
                    'float_shares': [unlimited_shares],
                    'major_shares': [freeholder_5_num],
                    'org_num': [len(orgholder_df)],
                    'org_shares': [orgholder_df_num],
                    'small_shares':[unlimited_shares-freeholder_5_num-orgholder_df_num]
                })
                tools.Tools().db_upsert(df, 'quar_holder_info', 'stock_code','')
                df = pd.DataFrame({
                    '代码': [stockCode],
                    '股本': [f"{unlimited_shares}/{round(freeholder_5_num/unlimited_shares*100)}%/{round(orgholder_df_num/unlimited_shares*100)}%"]
                })
                result = pd.concat([result, df])
        return result

    def get_stock_info(self, stock_codes):
        df = self.get_holder_info(stock_codes)
        limitup_sort_df = self.get_limitup_his(stock_codes)
        merged_df = pd.merge(df, limitup_sort_df, on='代码', how='left')
        return merged_df

#pd.set_option('display.max_rows', None)  # 设置显示的最大行数为无限制
#pd.set_option('display.max_columns', None)  # 设置显示的最大列数为无限制
#pd.set_option('display.width', None)  # 设置显示的最大宽度为无限制
#pd.set_option('display.max_colwidth', None)  # 设置最大列宽为无限制
#pd.set_option('display.precision', 10)  # 设置数值的显示精度
#pd.set_option('display.colheader_justify', 'center')

model=GetStockInfo()
stock_codes = ['001311']
df = model.get_stock_info(stock_codes)
print(df)
