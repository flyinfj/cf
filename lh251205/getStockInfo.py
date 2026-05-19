import requests
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import myLib

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
    def get_last_quarter_day(self,n=0):
        today = date.today() - relativedelta(months=3 * n)
        if today.month <= 3:
            end_of_last_quarter = date(today.year - 1, 12, 31)
        elif today.month <= 6:
            end_of_last_quarter = date(today.year, 3, 31)
        elif today.month <= 9:
            end_of_last_quarter = date(today.year, 6, 30)
        else:
            end_of_last_quarter = date(today.year, 9, 30)
        return end_of_last_quarter.strftime('%Y-%m-%d')

    #获取股东信息
    def get_holders(self,stockCode,endDate):
        url = f'https://datacenter.eastmoney.com/securities/api/data/get?type=RPT_F10_EH_HOLDERS&sty=SECUCODE,END_DATE,HOLDER_NAME,HOLDER_CODE,HOLDER_CODE_OLD,HOLD_NUM,HOLD_NUM_RATIO,HOLD_RATIO_QOQ,HOLDER_RANK,IS_HOLDORG,HOLDER_NEW,NEW_CHANGE_RATIO&filter=(SECUCODE="{stockCode}")(END_DATE=\'{endDate}\')&client=APP&source=SECURITIES&pageNumber=1&pageSize=10&sr=1'
        response_data = requests.get(url)
        data = response_data.json()
        try:
            df = pd.DataFrame(data.get('result', {}).get('data', []))
            return df
        except:
            return pd.DataFrame()
    #获取自由流通股东信息
    def get_freeholders(self,stockCode,endDate):
        url = f'https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_EH_FREEHOLDERS&columns=SECUCODE,END_DATE,HOLDER_NAME,HOLDER_CODE,HOLDER_CODE_OLD,HOLD_NUM,FREE_HOLDNUM_RATIO,FREE_RATIO_QOQ,IS_HOLDORG,HOLDER_RANK,HOLDER_NEW,NEW_CHANGE_RATIO&filter=(SECUCODE="{stockCode}")(END_DATE=\'{endDate}\')&client=APP&source=SECURITIES&pageNumber=1&pageSize=10&sr=1'
        response_data = requests.get(url)
        data = response_data.json()
        try:
            df = pd.DataFrame(data.get('result', {}).get('data', []))
            return df
        except:
            return pd.DataFrame()

    #获取机构持股
    def get_orgholders(self,stockCode,endDate):
        url = f'https://datacenter.eastmoney.com/securities/api/data/get?type=RPT_MAIN_ORGHOLDDETAIL&sty=SECURITY_CODE,REPORT_DATE,HOLDER_CODE,HOLDER_NAME,TOTAL_SHARES,HOLD_VALUE,FREESHARES_RATIO,ORG_TYPE,SECUCODE,FUND_DERIVECODE,FREE_SHARES&filter=(SECUCODE="{stockCode}")(REPORT_DATE=\'{endDate}\')&p=1&ps=200&sr=-1,1'
        response_data = requests.get(url)
        data = response_data.json()
        try:
            df = pd.DataFrame(data.get('result', {}).get('data', []))
            return df
        except:
            return pd.DataFrame()

    #获取收盘价
    def get_stock_close(self, stock_code):
        stock_codes_ad=self.generate_market_code(stock_code)
        url = f'https://push2.eastmoney.com/api/qt/ulist.np/get?ut=f057cbcbce2a86e2866ab8877db1d059&fltt=2&invt=2&fields=f14,f148,f3,f12,f2,f13,f29,f8,f10&secids={stock_codes_ad}'
        response_data = requests.get(url)
        try:
            data = response_data.json()['data']['diff']
            return data[0]['f2']
        except:
            return pd.DataFrame()
    def get_limitup_his(self,stockCodes):
        file_name = f"{self.filedir_database}/days_limitup_count.db"
        df = pd.read_csv(file_name, sep='\t')
        df['代码'] = df['代码'].astype(str).str.zfill(6)
        result = []
        for stockCode in stockCodes:
            filtered_row = df[df['代码'] == stockCode]
            if not filtered_row.empty:
                limit_up_sort = filtered_row['涨停排序'].values[0]
                limit_up_count = filtered_row['涨停数'].values[0]
                next_day_up_count = filtered_row['第二天涨次数'].values[0]
                avg_increase = filtered_row['平均涨幅'].values[0]
                next_day_up_ratio = round(next_day_up_count / limit_up_count * 100)
                result.append((stockCode, f'{limit_up_count}/{next_day_up_ratio}%/{avg_increase}'))
        return pd.DataFrame(result, columns=['代码', '涨停历史'])

    #获取股东信息
    def get_holder_info(self,stockCodes):
        file_name = f"{self.filedir_database}/quar_holder_info.db"
        try:
            all_df = pd.read_csv(file_name, sep='\t')
            all_df['代码'] = all_df['代码'].astype(str).str.zfill(6)
        except FileNotFoundError:
            all_df = pd.DataFrame({
                '代码': ['000000'],
                '股本': ['test']
            })
            all_df.to_csv(file_name, mode='a', header=True, index=False, sep='\t')
        result = pd.DataFrame()
        for stockCode in stockCodes:
            df = all_df[all_df['代码'] == stockCode]
            if not df.empty:
                result = pd.concat([result, df])
            else:
                #获取股票收盘价
                close = self.get_stock_close(stockCode)
                if not isinstance(close, (int, float)):
                    close = 0
                #获取上季度最后一天日期
                endDate = self.get_last_quarter_day(0)
                #获取股东、流通股东、机构信息
                stockCode = self.generate_market_code2(stockCode)
                holder_df = self.get_holders(stockCode,endDate)
                if holder_df.empty:
                    endDate = self.get_last_quarter_day(1)
                    holder_df = self.get_holders(stockCode, endDate)
                freeholder_df = self.get_freeholders(stockCode,endDate)
                orgholder_df = self.get_orgholders(stockCode,endDate)

                #计算总股本、流通股本
                try:
                    first_holder = holder_df.iloc[0]
                    total_shares= round(close*float(first_holder['HOLD_NUM'])/float(first_holder['HOLD_NUM_RATIO'])*100/100000000)
                    first_freeholder = freeholder_df.iloc[0]
                    unlimited_shares = round(close*first_freeholder['HOLD_NUM']/first_freeholder['FREE_HOLDNUM_RATIO']*100/100000000)
                except:
                    total_shares = 0
                    unlimited_shares = 0
                # 计算大股东股本
                try:
                    holder_df_5 = holder_df[holder_df['HOLD_NUM_RATIO'] >= 5]
                    freeholder_df_5 = freeholder_df[freeholder_df['HOLDER_NAME'].isin(holder_df_5['HOLDER_NAME'])]
                    freeholder_5_num = round(close*freeholder_df_5['HOLD_NUM'].sum()/100000000)
                except:
                    freeholder_5_num = 0

                #计算机构数、机构股本
                try:
                    orgholder_df_5 = orgholder_df[~orgholder_df['HOLDER_NAME'].isin(holder_df_5['HOLDER_NAME'])]
                    orgholder_df_num = round(close*orgholder_df_5['TOTAL_SHARES'].sum()/100000000)
                except:
                    orgholder_df_num =0

                df = pd.DataFrame({
                    '代码': [stockCode],
                    '股本': [f"{orgholder_df_num}/{unlimited_shares - freeholder_5_num - orgholder_df_num}"]
                    #'股本': [f"{unlimited_shares}-{freeholder_5_num}/{orgholder_df_num}+{unlimited_shares-freeholder_5_num-orgholder_df_num}"]
                    #'总股本': [total_shares],
                    #'流通股': [unlimited_shares],
                    #'大股东': [freeholder_5_num],
                    #'机构数': [len(orgholder_df)],
                    #'机构股': [orgholder_df_num],
                    #'散户':[unlimited_shares-freeholder_5_num-orgholder_df_num]
                })
                df['代码'] = df['代码'].str.replace('.SH', '', regex=False)
                df['代码'] = df['代码'].str.replace('.SZ', '', regex=False)
                df.to_csv(file_name, mode='a', header=False, index=False, sep='\t')
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

#model=GetStockInfo()
#stock_codes = ['300097','000001','000506']
#df = model.get_stock_info(stock_codes)
#print(df)