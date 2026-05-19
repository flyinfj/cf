import requests
import json
import pandas as pd
import time
import akshare as ak
import datetime
import numpy as np

class MyLib:
    def __init__(self, data_type='飙升', market='A', globalId='786e4c21-70dc-435a-93bb-38'):
        self.globalId = globalId
        self.data_type = data_type
        self.market = market
        if self.market == 'A':
            self.marketType = ""
        elif self.market == 'HK':
            self.marketType = '000003'
        elif self.market == 'US':
            self.marketType = '000004'
        elif self.market == 'ETF':
            self.marketType = 'etf'
        else:
            self.marketType = ""
        self.filedir_database = 'E:/python_workspace/cf/database'
        self.filedir_data = 'E:/python_workspace/cf/data'
        self.filedir_tmp = 'E:/python_workspace/cf/tmp'
    #股票代码加1.和0.
    def generate_market_code(self, stock_code):
        if stock_code.startswith('1.') or stock_code.startswith('0.') or stock_code.startswith('90.'):
            return stock_code
        if stock_code[:2] == "60":
            return '1.' + stock_code
        else:
            return '0.' + stock_code

    #获取交易日期列表(不含今日)
    def get_trade_dates(self, predays=5, is_today=0):
        file_name = f"{self.filedir_database}/yyyy_trade_dates.db"
        try:
            df = pd.read_csv(file_name)
        except FileNotFoundError:
            trade_dates = ak.tool_trade_date_hist_sina()
            df = pd.DataFrame(trade_dates, columns=['trade_date'])
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d').astype(int)
            df.to_csv(file_name, index=False)
        to_day = int(datetime.datetime.now().strftime('%Y%m%d'))
        if is_today == 0:
            df = df[df['trade_date'] < to_day]
        else:
            df = df[df['trade_date'] <= to_day]
        df = df.tail(predays)
        return df

    #计算申请九转
    def calc_niceturn(self, mkt_data, n1):
        close = mkt_data['收盘']
        close_diff_n1 = close - close.shift(n1)
        ud = np.sign(close_diff_n1).fillna(0)

        cumu_ud = np.zeros(shape=ud.shape)
        add_v = 0
        for i, ud_i in enumerate(ud):
            if add_v == 0:
                add_v = ud_i
                cumu_ud[i] = ud_i
            else:
                if add_v * ud_i < 0:  # ud变符号了
                    cumu_ud[i] = ud_i
                    add_v = ud_i
                else:  # ud没有变符号了
                    if abs(ud_i) != 0:
                        add_v += ud_i
                        if abs(add_v) <= 9:
                            cumu_ud[i] = add_v
                        else:
                            if add_v > 0:
                                cumu_ud[i] = 1
                                add_v = 1
                            else:
                                cumu_ud[i] = -1
                                add_v = -1
                    else:
                        add_v = add_v + 1
        """ 赋值 """
        mkt_data['ud'] = ud
        mkt_data['九转'] = cumu_ud

        return mkt_data

    # 获取人气和人气飙升股票TOP100
    # '代码', '人气排名', '人气较昨日变动'
    def get_popu_stocks(self,data_type):
        if data_type == 1:   #飙升
            url = 'https://emappdata.eastmoney.com/stockrank/getAllHisRcList'
        else:
            url = 'https://emappdata.eastmoney.com/stockrank/getAllCurrentList'
        data = {
            "appId": "appId01",
            "globalId": self.globalId,
            "marketType": self.marketType,
            "pageNo": 1,
            "pageSize": 100
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
        df = pd.DataFrame(text['data'])
        try:
            df.columns = ['代码', '人气排名' , 'rc']
        except:
            df.columns = ['代码', '人气排名', '人气较昨日变动' , 'rc']
        df = df.drop('rc', axis=1)
        df['代码'] = df['代码'].replace({'^SH': '', '^SZ': ''}, regex=True)
        return df

    # 获取条件选股（人气前350）
    # '代码', '名称', '涨幅'
    def get_cond_popu_stocks(self, topn):
        # 构建表单数据
        files = {
            'type': (None, 'RPTA_SECURITY_STOCKSELECT'),
            'sty': (None, 'SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,NEW_PRICE,CHANGE_RATE,POPULARITY_RANK'),
            'filter': (None, f'(POPULARITY_RANK>=0)(POPULARITY_RANK<={topn})'),
            'p': (None, '1'),
            'ps': (None, topn),
            'sr': (None, '-1'),
            'st': (None, 'CHANGE_RATE'),
            'source': (None, 'SELECT_SECURITIES'),
            'client': (None, 'APP')
        }

        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://emrnweb.eastmoney.com',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://emrnweb.eastmoney.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }

        # 发送POST请求
        url = "https://datacenter.eastmoney.com/stock/selection/api/data/get/"
        response = requests.post(url, headers=headers, files=files)
        # 检查响应
        if response.status_code == 200:
            # 解析响应的JSON数据
            data = response.json()
            # 检查数据是否包含股票信息
            if 'result' in data and 'data' in data['result']:
                # 提取股票信息
                stock_data = data['result']['data']
                # 提取SECURITY_CODE、SECURITY_NAME_ABBR列
                security_codes = [{'代码': item['SECURITY_CODE'], '名称': item['SECURITY_NAME_ABBR'].ljust(4, '：'),
                                   '涨幅': item['CHANGE_RATE']} for item in stock_data]
                # 创建DataFrame
                df = pd.DataFrame(security_codes, columns=['代码', '名称', '涨幅'])
                # 打印DataFrame
                return df
            else:
                print("未找到股票信息")
        else:
            print("请求失败，状态码：", response.status_code)

    # 获取条件选择（涨幅超8%）
    # '代码', '名称', '涨幅'
    def get_raise_stocks(self, topn):
        # 构建表单数据
        files = {
            'type': (None, 'RPTA_SECURITY_STOCKSELECT'),
            'sty': (None, 'SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,NEW_PRICE,CHANGE_RATE,POPULARITY_RANK'),
            'filter': (None, '(CHANGE_RATE>=8)(CHANGE_RATE<=21)'),  # (@CHANGE_RATE="LIMIT_UP_PRICE")
            'p': (None, '1'),
            'ps': (None, topn),
            'sr': (None, '-1'),
            'st': (None, 'CHANGE_RATE'),
            'source': (None, 'SELECT_SECURITIES'),
            'client': (None, 'APP')
        }

        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://emrnweb.eastmoney.com',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://emrnweb.eastmoney.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }

        # 发送POST请求
        url = "https://datacenter.eastmoney.com/stock/selection/api/data/get/"
        response = requests.post(url, headers=headers, files=files)
        # 检查响应
        if response.status_code == 200:
            # 解析响应的JSON数据
            data = response.json()
            # 检查数据是否包含股票信息
            if 'result' in data and 'data' in data['result']:
                # 提取股票信息
                stock_data = data['result']['data']
                # 提取SECURITY_CODE、SECURITY_NAME_ABBR列
                security_codes = [{'代码': item['SECURITY_CODE'], '名称': item['SECURITY_NAME_ABBR'].ljust(4, '：'),
                                   '涨幅': item['CHANGE_RATE']} for item in stock_data]
                # 创建DataFrame
                df = pd.DataFrame(security_codes, columns=['代码', '名称', '涨幅'])
                # 打印DataFrame
                return df
            else:
                print("未找到股票信息")
        else:
            print("请求失败，状态码：", response.status_code)

    # 获取股票行情数据
    # '代码','名称','最新价','涨幅','量比','换手'
    def get_stock_data(self, stock_codes):
        # 构造请求URL
        stock_codes_ad = []
        for stock_code in stock_codes:
            stock_codes_ad.append(self.generate_market_code(stock_code))
        stock_codes_str = ','.join(stock_codes_ad)
        url = f'https://push2.eastmoney.com/api/qt/ulist.np/get?ut=f057cbcbce2a86e2866ab8877db1d059&fltt=2&invt=2&fields=f14,f148,f3,f12,f2,f13,f29,f8,f10&secids={stock_codes_str}&_={int(time.time())}'
        response_data = requests.get(url)
        data = response_data.json()['data']['diff']
        # hot_keyword = ak.stock_hot_keyword_em(symbol=stock_code)
        # hot_keywords = ','.join(hot_keyword['概念名称'].astype(str))
        parsed_data = []
        for item in data:
            stock_data = {
                '代码': item['f12'],
                '名称': item['f14'].ljust(4, '：'),  # 假设你想要在名称后面添加冒号和空格 ——
                '最新价': item['f2'],
                '涨幅': item['f3'],
                '换手': item['f8'],
                '量比': item['f10']
                # '概念标签': hot_keywords  # 这一行被注释掉了，因为hot_keywords没有定义
            }

            parsed_data.append(stock_data)
        df = pd.DataFrame(parsed_data)
        return df

    # 获取标签
    # '代码'， '标签'
    def get_stock_label(self,stock_codes):
        stock_codes_ad = ['SH' + code if code.startswith('60') else 'SZ' + code for code in stock_codes]
        stock_groups = [stock_codes_ad[i:i + 90] for i in range(0, len(stock_codes_ad), 90)]
        all_labels = []
        # 对每组股票代码调用模型获取标签
        for group in stock_groups:
            stock_codes_str = ','.join(group)
            url = "https://emappdata.eastmoney.com/label/getSecurityCodeLabelList"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Sec-GPC": "1",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-site",
                "Content-type": "application/json",
                "Priority": "u=4",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            }
            data = {
                "appId": "appId01",
                "globalId": "786e4c21-70dc-435a-93bb-38",
                "securityCodes": stock_codes_str
            }
            response = requests.post(url, headers=headers, json=data)
            # 检查响应状态码
            if response.status_code == 200:
                response_data = response.json()
                # 检查response_data中是否有data字段
                if response_data and 'data' in response_data:
                    # 初始化空列表来存储解析后的数据
                    parsed_data = []
                    # 遍历response_data中的data部分
                    for item in response_data['data']:
                        src_security_code = item.get('srcSecurityCode', '').replace(' ', '')
                        # 将labelItemList中的labelName提取出来，并用逗号隔开
                        label_names = ','.join([lbl.get('labelName', '').replace(' ', '') for lbl in item.get('labelItemList', [])])
                        label_names = label_names[: 20]
                        # 将解析后的数据添加到列表中
                        parsed_data.append({
                            '代码': src_security_code[2:] if src_security_code[:2] in ['SH', 'SZ'] else src_security_code,
                            '标签': label_names
                            #'标签': label_names[:25].ljust(25) if len(label_names) > 25 else label_names.ljust(25)
                        })
                    # 使用解析后的数据创建Pandas DataFrame
                    df = pd.DataFrame(parsed_data)
                    all_labels.append(df)
        all_labels_df = pd.concat(all_labels, ignore_index=True)
        #all_labels_df['标签'] = all_labels_df['标签'].apply(lambda x: str(x).ljust(30))
        return all_labels_df

    # 获取股票分钟数据
    # '代码','名称','时间','收盘','涨幅'
    def get_stock_his(self,stock_code,klt,start_date):
        # 构造请求URL
        stock_codes_str = self.generate_market_code(stock_code)
        end_date = datetime.date.today()
        end_date_str = end_date.strftime('%Y%m%d')
        start_date_str = str(start_date)
        url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={stock_codes_str}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt={klt}&fqt=1&beg={start_date_str}&end={end_date_str}&smplmt=854&lmt=1000000&_='

        response_data = requests.get(url)
        data = response_data.json()['data']['klines']
        stock_codes_name = response_data.json()['data']['name']
        # 初始化结果字典
        parsed_data = []
        for item in data:
            split_data = item.split(',')
            parsed_data.append({
                        '代码': response_data.json()['data']['code'],
                        '名称': stock_codes_name.ljust(4,'：'),       
                        '时间': split_data[0],
                        '收盘': pd.to_numeric(split_data[2], errors='coerce'),
                        '涨幅': split_data[8],
                        '成交额': round(pd.to_numeric(split_data[6], errors='coerce')/100000000,1)
                    })
        df = pd.DataFrame(parsed_data)
        return df

    # 获取九转最新情况
    # '代码', '时间', 'cumn_ud'
    def get_stock_nineturn(self, stock_codes,start_date,klt=30,is_filter=0,is_name=0):
        df = pd.DataFrame()
        for stock_code in stock_codes:
            stock_his_df = self.get_stock_his(stock_code,klt,start_date)
            if stock_his_df is not None and not stock_his_df.empty:
                ud_df = self.calc_niceturn(stock_his_df, 4)
                # ud_df = ud_df[ud_df['九转'].astype(int).isin([-6,-7,-8,-9])]
                # ud_df['涨幅'] = ud_df['涨幅'].apply(lambda x: f"{x}%")
                if is_filter == 0:
                    ud_df = ud_df.tail(1)
                else:
                    t1 = ud_df[ud_df['九转'] >= 2]['时间'].max()
                    t2 = ud_df[ud_df['九转'] <= -7]['时间'].max()
                    if pd.to_datetime(t1) < pd.to_datetime(t2):
                        ud_df = ud_df.tail(1)
                    else:
                        ud_df.drop(ud_df.index, inplace=True)
                ud_df = ud_df.drop(['ud'], axis=1)
                if is_name == 0:
                    ud_df = ud_df.drop(['名称'], axis=1)
                    ud_df = ud_df.drop('涨幅', axis=1)
                df = pd.concat([df, ud_df], ignore_index=True)
        return df

    # 计算指标近期排名情况
    def calc_popu_rate(self, stock):
        # 设置开始日期和结束日期
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=15)

        end_date_str = end_date.strftime('%Y%m%d')
        start_date_str = start_date.strftime('%Y%m%d')
        try:
            # 获取个股人气榜-历史趋势及粉丝特征数据
            if stock.startswith("6"):
                prefixed_stock = "SH" + stock
            elif stock.startswith("0") or stock.startswith("3"):
                prefixed_stock = "SZ" + stock
            else:
                prefixed_stock = stock  # 如果不匹配任何已知前缀，保持原样
            hot_detail_df = ak.stock_hot_rank_detail_em(symbol=prefixed_stock)
            if hot_detail_df is not None and not hot_detail_df.empty and len(
                    hot_detail_df) > 5:
                # 计算最近三天的人气排名平均值
                avg_hot_1 = hot_detail_df.tail(1)['排名'].values[0]
                avg_hot_3 = round(hot_detail_df.tail(3)['排名'].mean())
                avg_hot_5 = round(hot_detail_df.tail(5)['排名'].mean())

                # 计算三天前到10天前的人气排名平均值
                avg_hot_pre_1 = round(hot_detail_df.iloc[-2:-1]['排名'].mean())
                avg_hot_pre_3 = round(hot_detail_df.iloc[-6:-3]['排名'].mean())
                avg_hot_pre_5 = round(hot_detail_df.iloc[-10:-5]['排名'].mean())
                rc_raise_1 = avg_hot_pre_1 - avg_hot_1
                rc_raise_3 = avg_hot_pre_3 - avg_hot_3
                rc_raise_5 = avg_hot_pre_5 - avg_hot_5
                data = {
                    '代码': stock,  # 股票代码
                    '人气排名': avg_hot_1,
                    '人气排名1日变动': rc_raise_1,  # 排名变动
                    '人气排名3日变动': rc_raise_3,  # 排名变动
                    '人气排名5日变动': rc_raise_5  # 排名变动
                }
            else:
                data = {
                    '代码': stock,  # 股票代码
                    '人气排名': 10000,
                    '人气排名1日变动': 0,  # 排名变动,
                    '人气排名3日变动': 0,  # 排名变动,
                    '人气排名5日变动': 0  # 排名变动
                }
        except KeyError:
            data = {
                '代码': stock,  # 股票代码
                '人气排名': 10000,
                '人气排名1日变动': 0,  # 排名变动,
                '人气排名3日变动': 0, # 排名变动,
                '人气排名5日变动': 0  # 排名变动
            }
        df = pd.DataFrame(data, index=[0])
        return df

    # 计算指标近期涨幅情况(ak)
    def calc_raise_rate(self, stock):
        # 设置开始日期和结束日期
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=15)
        end_date_str = end_date.strftime('%Y%m%d')
        start_date_str = start_date.strftime('%Y%m%d')
        try:
            # 获取个股历史行情数据
            stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stock, period="daily", start_date=start_date_str,
                                                    end_date=end_date_str, adjust="qfq")
            print(stock_zh_a_hist_df)
            if stock_zh_a_hist_df is not None and not stock_zh_a_hist_df.empty:
                has_hit_limit_up = 'F0'
                recent_five_days = stock_zh_a_hist_df.tail(6)
                limit_up_rate = 1.198 if stock.startswith('30') else 1.098
                t = 0
                for index in range(1, len(recent_five_days)):
                    current_close = recent_five_days.iloc[index]['收盘']
                    previous_close = recent_five_days.iloc[index - 1]['收盘']
                    if current_close >= previous_close * limit_up_rate:
                        t = t + 1
                        has_hit_limit_up = f'T{t}'
                        break
                recent_high = stock_zh_a_hist_df.iloc[-6:-1]['最高'].max()
                today_close = stock_zh_a_hist_df.iloc[-1]['收盘']
                fall_rate = round(((today_close - recent_high) / recent_high) * 100, 2)

                # 计算最近三天的平均收盘价
                recent_three_days = stock_zh_a_hist_df.tail(3)
                avg_close_recent_three_days = round(recent_three_days['收盘'].mean(), 2)

                # 计算三天前到10天前的平均收盘价
                days_ago_6_to_10 = stock_zh_a_hist_df.iloc[-9:-5]  # 排除最近三天
                avg_close_days_ago_6_to_10 = round(days_ago_6_to_10['收盘'].mean(), 2)
                price_raise = round(100 * avg_close_recent_three_days / avg_close_days_ago_6_to_10 - 100, 2)

                # 今日涨幅
                today_raise = stock_zh_a_hist_df.tail(1)['涨跌幅'].values[0]
                data = {
                    '代码': stock,  # 股票代码
                    '涨幅': today_raise,
                    '十日环比': price_raise,  # 价格变动比例
                    '最近涨停': has_hit_limit_up,
                    '最近跌幅': fall_rate
                }
            else:
                data = {
                    '代码': stock,  # 股票代码
                    '涨幅': 0,
                    '十日环比': 0,  # 价格变动比例
                    '最近涨停': 'F',
                    '最近跌幅': 0
                }
            df = pd.DataFrame(data, index=[0])
            return df
        except KeyError:
            data = {
                '代码': stock,  # 股票代码
                '涨幅': 0,
                '十日环比': 0,  # 价格变动比例
                '最近涨停': 'F',
                '最近跌幅': 0
            }
            df = pd.DataFrame(data, index=[0])
            return df
    def calc_raise_rate_new(self, stock_codes):
        # 获取最近10个交易日
        trade_dates = self.get_trade_dates(10)
        price_raise = 0
        limit_up_count = 0

        pre_price_start_date = trade_dates['trade_date'].iloc[0]  # 最近10个交易日的起始日期
        file_name = f"{self.filedir_database}/stock_spot.db"
        df_his = pd.read_csv(file_name)
        df_his['代码'] = df_his['代码'].astype(str).str.zfill(6)

        limit_up_start_date = trade_dates['trade_date'].iloc[5]  # 最近5个交易日的起始日期
        file_name = f"{self.filedir_database}/days_limitup.db"
        df_limitup_his = pd.read_csv(file_name)
        df_limitup_his['代码'] = df_limitup_his['代码'].astype(str).str.zfill(6)

        result = []
        for stock_code in stock_codes:
            df = df_his[(df_his['代码'] == stock_code) & (df_his['时间'] >= pre_price_start_date)]
            fall_rate = 0
            price_raise = 0
            if not df.empty:
                # 计算最近三天的平均收盘价
                recent_three_days = df.tail(3)
                avg_close_recent_three_days = round(recent_three_days['最新价'].mean(), 2)
                days_ago_6_to_10 = df.iloc[-9:-5]  # 计算三天前到10天前的平均收盘价
                avg_close_days_ago_6_to_10 = round(days_ago_6_to_10['最新价'].mean(), 2)
                if avg_close_days_ago_6_to_10 != 0:
                    price_raise = round(100 * avg_close_recent_three_days / avg_close_days_ago_6_to_10 - 100, 2)
                else:
                    price_raise = 0
                # 计算最近三天的平均收盘价
                recent_one_days = df.tail(1)
                avg_close_recent_one_days = round(recent_one_days['最新价'].mean(), 2)
                days_ago_2_to_5 = df.iloc[-5:-2]  # 计算三天前到10天前的平均收盘价
                max_close_days_ago_2_to_5 = round(days_ago_2_to_5['最新价'].max(), 2)
                if max_close_days_ago_2_to_5!= 0:
                    fall_rate = round(100 * avg_close_recent_one_days / max_close_days_ago_2_to_5 - 100, 2)
                else:
                    fall_rate = 0
            # 获取最近5日来的涨停次数
            limit_up_df = df_limitup_his[(df_limitup_his['代码'] == stock_code) & (df_limitup_his['date'] >= limit_up_start_date)]

            # 构造结果数据
            data = {
                '代码': stock_code,  # 股票代码
                '十日环比': price_raise,  # 价格变动比例
                '最近涨停': f'T{len(limit_up_df)}' if len(limit_up_df) > 0 else f'F',  # 最近涨停次数
                '最近跌幅': fall_rate  # 假设最近跌幅为0，可根据需要计算
            }
            result.append(data)
        df_result = pd.DataFrame(result)
        return df_result

    #获每日涨停股票
    def get_limitup_stocks(self,trade_dates):
        all_limitup_stocks = pd.DataFrame()
        file_name = f"{self.filedir_database}/days_limitup.db"
        try:
            df_his = pd.read_csv(file_name)
            df_his['代码'] = df_his['代码'].astype(str).str.zfill(6)
        except FileNotFoundError:
            date = trade_dates['trade_date'].iloc[-1]
            df_his = ak.stock_zt_pool_em(date)
            df_his['date'] = date
            df_his.to_csv(file_name, mode='a', header=True, index=False)
        for date in trade_dates['trade_date']:
            df = df_his[df_his['date'] == date]
            if df.empty:
                df = ak.stock_zt_pool_em(date=date)
                if not df.empty:
                    df['date'] = date
                    all_limitup_stocks = pd.concat([all_limitup_stocks, df])
                if date != trade_dates['trade_date'].iloc[-1]:
                    df.to_csv(file_name, mode='a', header=False, index=False)
            else:
                all_limitup_stocks = pd.concat([all_limitup_stocks, df])
        return all_limitup_stocks

    #输出文件
    def output_file(self,df,title,output_stock=1):
        now = datetime.datetime.now()
        df = self.beautify(df)
        file_name1 = f"{self.filedir_data}/{now.strftime("%m%d%H")}.txt"
        file_name2 = f"{self.filedir_data}/{now.strftime("%m%d%H")}_stock.txt"
        with open(file_name1, 'a', encoding='utf-8') as f:
            f.write('\n')
            f.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            if title != '':
                f.write(f"{title}：\n")
        df.to_csv(file_name1, mode='a', header=True, index=False, sep='\t')
        if output_stock == 1:
            df['代码'].to_csv(file_name2,mode='a', index=False, header=False)
    def beautify(self,df):
        df = df.astype(str)
        max_lengths = df.apply(lambda x: x.str.len()).max()
        if '名称' in df.columns:
            df['名称'] = df['名称'].apply(lambda x: x if len(x) >= 4 else x + '：' * (4 - len(x)))
        for col in df.columns:
            max_length = max_lengths[col]
            if max_length >0:
                if col not in ['标签', '股本']:
                    df[col] = df[col].str.pad(width=max_length, side='left', fillchar=' ')
                else:
                    df[col] = df[col].str.pad(width=max_length, side='right', fillchar=' ')
        return df
# 测试
#model = MyLib()
#df = model.get_trade_dates(10)
#print(df)
#df = model.calc_raise_rate_new('002841')
#print(df)
#all_limitup = model.get_limitup_stocks(trade_dates)