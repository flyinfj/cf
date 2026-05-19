import requests
import json
import pandas as pd
import time
import akshare as ak
import datetime
import numpy as np
import warnings
import os
import platform
from openai import OpenAI
from typing import List, Dict, Optional, Union


class MyLib2:
    """
    重构后的股票数据获取和处理类
    优化了代码结构，抽取了公共方法，提高了代码复用性
    """
    
    def __init__(self, data_type='飙升', market='A', globalId='786e4c21-70dc-435a-93bb-38'):
        self.globalId = globalId
        self.data_type = data_type
        self.market = market
        self.marketType = self._get_market_type()
        self.data_dir = self._get_data_dir()
        self._init_directories()
    
    def _get_market_type(self) -> str:
        """获取市场类型代码"""
        market_mapping = {
            'A': "",
            'HK': '000003',
            'US': '000004',
            'ETF': 'etf'
        }
        return market_mapping.get(self.market, "")
    
    def _get_data_dir(self) -> str:
        """根据操作系统获取数据目录"""
        system = platform.system()
        if system == 'Windows':
            return 'E:/python_workspace/cf'
        elif system in ['Linux', 'Darwin']:
            return '/root/cf'
        else:
            raise OSError("Unsupported operating system")
    
    def _init_directories(self):
        """初始化目录路径"""
        self.filedir_database = f'{self.data_dir}/database'
        self.filedir_data = f'{self.data_dir}/data'
        self.filedir_tmp = f'{self.data_dir}/tmp'
    
    # ==================== 公共工具方法 ====================
    
    def _make_http_request(self, url: str, method: str = 'GET', 
                          headers: Optional[Dict] = None, 
                          data: Optional[Dict] = None,
                          files: Optional[Dict] = None) -> Optional[Dict]:
        """
        统一的HTTP请求方法
        
        Args:
            url: 请求URL
            method: 请求方法 ('GET' 或 'POST')
            headers: 请求头
            data: POST数据
            files: 表单文件数据
            
        Returns:
            响应的JSON数据或None
        """
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            else:
                if files:
                    response = requests.post(url, headers=headers, files=files)
                elif data:
                    response = requests.post(url, headers=headers, 
                                           data=json.dumps(data) if isinstance(data, dict) else data)
                else:
                    response = requests.post(url, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"HTTP请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None
    
    def _get_default_headers(self, content_type: str = 'application/json') -> Dict[str, str]:
        """获取默认请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Content-Type': content_type
        }
    
    def _format_stock_code(self, stock_code: str, prefix_type: str = 'market') -> str:
        """
        格式化股票代码
        
        Args:
            stock_code: 原始股票代码
            prefix_type: 前缀类型 ('market', 'exchange', 'akshare', 'tencent')
            
        Returns:
            格式化后的股票代码
        """
        if prefix_type == 'market':
            return self._generate_market_code(stock_code)
        elif prefix_type == 'exchange':
            return 'SH' + stock_code if stock_code.startswith('60') else 'SZ' + stock_code
        elif prefix_type == 'akshare':
            return f"sh{stock_code}" if stock_code.startswith("60") else f"sz{stock_code}"
        elif prefix_type == 'tencent':
            return f"sh{stock_code}" if stock_code.startswith("60") else f"sz{stock_code}"
        else:
            return stock_code
    
    def _generate_market_code(self, stock_code: str) -> str:
        """股票代码加前缀1.和0."""
        if stock_code.startswith(('1.', '0.', '90.')):
            return stock_code
        return '1.' + stock_code if stock_code.startswith('60') else '0.' + stock_code
    
    def _create_dataframe_from_list(self, data_list: List[Dict], columns: Optional[List[str]] = None) -> pd.DataFrame:
        """从字典列表创建DataFrame"""
        if not data_list:
            return pd.DataFrame()
        
        df = pd.DataFrame(data_list)
        if columns:
            df = df.reindex(columns=columns, fill_value=None)
        return df
    
    def _save_to_csv(self, df: pd.DataFrame, filename: str, index: bool = False):
        """保存DataFrame到CSV文件"""
        try:
            filepath = os.path.join(self.filedir_data, filename)
            df.to_csv(filepath, index=index, encoding='utf-8')
        except Exception as e:
            print(f"保存CSV文件失败: {e}")
    
    def _load_from_csv(self, filename: str) -> pd.DataFrame:
        """从CSV文件加载DataFrame"""
        try:
            filepath = os.path.join(self.filedir_database, filename)
            return pd.read_csv(filepath)
        except FileNotFoundError:
            return pd.DataFrame()
        except Exception as e:
            print(f"加载CSV文件失败: {e}")
            return pd.DataFrame()
    
    def _format_name_with_padding(self, name: str, width: int = 4, padding: str = '：') -> str:
        """格式化名称并添加填充"""
        return name.ljust(width, padding)
    
    # ==================== 交易日期相关方法 ====================
    
    def get_trade_dates(self, predays: int = 5, is_today: int = 0) -> pd.DataFrame:
        """
        获取交易日期列表
        
        Args:
            predays: 获取前几天的数据
            is_today: 是否包含今日 (0: 不包含, 1: 包含)
            
        Returns:
            包含交易日期的DataFrame
        """
        file_name = "yyyy_trade_dates.db"
        df = self._load_from_csv(file_name)
        
        if df.empty:
            try:
                trade_dates = ak.tool_trade_date_hist_sina()
                df = pd.DataFrame(trade_dates, columns=['trade_date'])
                df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d').astype(int)
                self._save_to_csv(df, file_name)
            except Exception as e:
                print(f"获取交易日期失败: {e}")
                return pd.DataFrame()
        
        today = int(datetime.datetime.now().strftime('%Y%m%d'))
        if is_today == 0:
            df = df[df['trade_date'] < today]
        else:
            df = df[df['trade_date'] <= today]
        
        return df.tail(predays)
    
    # ==================== 技术分析方法 ====================
    
    def calc_niceturn(self, mkt_data: pd.DataFrame, n1: int) -> pd.DataFrame:
        """
        计算神奇九转指标
        
        Args:
            mkt_data: 市场数据DataFrame，需包含'收盘'列
            n1: 计算周期
            
        Returns:
            添加了'ud'和'九转'列的DataFrame
        """
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
                            cumu_ud[i] = 1 if add_v > 0 else -1
                            add_v = 1 if add_v > 0 else -1
                    else:
                        add_v = add_v + 1

        mkt_data['ud'] = ud
        mkt_data['九转'] = cumu_ud
        return mkt_data
    
    # ==================== 股票数据获取方法 ====================
    
    def get_vol_bnk(self) -> pd.DataFrame:
        """
        获取成交量板块数据
        
        Returns:
            包含板块信息的DataFrame
        """
        url = 'https://push2.eastmoney.com/api/qt/clist/get?np=1&fltt=1&invt=2&fs=m:90+t:2+f:!50&fields=f3,f10,f12,f14&fid=f10&pn=1&pz=5&po=1&dect=1'
        
        data = self._make_http_request(url)
        if not data or 'data' not in data or 'diff' not in data['data']:
            return pd.DataFrame()
        
        parsed_data = []
        for item in data['data']['diff']:
            stock_data = {
                '名称': f"{item['f14']}({round(item['f10']/100,1)}/{round(item['f3']/100,1)})"
            }
            parsed_data.append(stock_data)
        
        top_str_3 = ','.join([stock['名称'] for stock in parsed_data])
        report_data = {'板块(量比/涨幅)': top_str_3}
        
        return self._create_dataframe_from_list([report_data])
    
    def get_popu_stocks(self, data_type: int) -> pd.DataFrame:
        """
        获取热榜股票数据
        
        Args:
            data_type: 数据类型 (1: 飙升, 其他: 当前热榜)
            
        Returns:
            包含热榜股票信息的DataFrame
        """
        url = ('https://emappdata.eastmoney.com/stockrank/getAllHisRcList' 
               if data_type == 1 
               else 'https://emappdata.eastmoney.com/stockrank/getAllCurrentList')
        
        data = {
            "appId": "appId01",
            "globalId": self.globalId,
            "marketType": self.marketType,
            "pageNo": 1,
            "pageSize": 100
        }
        
        headers = self._get_default_headers()
        headers.update({
            'origin': 'https://vipmoney.eastmoney.com',
            'referer': 'https://vipmoney.eastmoney.com/',
        })
        
        response_data = self._make_http_request(url, 'POST', headers, data)
        if not response_data or 'data' not in response_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response_data['data'])
        
        # 动态设置列名
        if len(df.columns) == 3:
            df.columns = ['代码', '热榜', 'rc']
        elif len(df.columns) == 4:
            df.columns = ['代码', '热榜', '热榜较昨日变动', 'rc']
        
        df = df.drop('rc', axis=1, errors='ignore')
        df['代码'] = df['代码'].str.replace(r'^(SH|SZ)', '', regex=True)
        
        return df
    
    def _get_stock_selection_data(self, filter_condition: str, topn: str, 
                                 columns: List[str]) -> pd.DataFrame:
        """
        获取股票筛选数据的通用方法
        
        Args:
            filter_condition: 筛选条件
            topn: 返回数量
            columns: 返回的列名
            
        Returns:
            筛选后的股票DataFrame
        """
        files = {
            'type': (None, 'RPTA_SECURITY_STOCKSELECT'),
            'sty': (None, 'SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,NEW_PRICE,CHANGE_RATE,POPULARITY_RANK'),
            'filter': (None, filter_condition),
            'p': (None, '1'),
            'ps': (None, topn),
            'sr': (None, '-1'),
            'st': (None, 'CHANGE_RATE'),
            'source': (None, 'SELECT_SECURITIES'),
            'client': (None, 'APP')
        }
        
        headers = self._get_default_headers()
        headers.update({
            'Origin': 'https://emrnweb.eastmoney.com',
            'Referer': 'https://emrnweb.eastmoney.com/'
        })
        
        url = "https://datacenter.eastmoney.com/stock/selection/api/data/get/"
        response_data = self._make_http_request(url, 'POST', headers, files=files)
        
        if (not response_data or 'result' not in response_data 
            or 'data' not in response_data['result']):
            return pd.DataFrame()
        
        stock_data = response_data['result']['data']
        parsed_data = []
        
        for item in stock_data:
            stock_info = {
                '代码': item['SECURITY_CODE'],
                '名称': self._format_name_with_padding(item['SECURITY_NAME_ABBR']),
                '涨幅': item['CHANGE_RATE']
            }
            
            if 'POPULARITY_RANK' in item:
                stock_info['热榜'] = round(item['POPULARITY_RANK'])
            
            parsed_data.append(stock_info)
        
        return self._create_dataframe_from_list(parsed_data, columns)
    
    def get_cond_popu_stocks(self, topn: int) -> pd.DataFrame:
        """
        获取条件选股（热榜前N名）
        
        Args:
            topn: 获取前N名
            
        Returns:
            包含股票信息的DataFrame
        """
        filter_condition = f'(POPULARITY_RANK>=0)(POPULARITY_RANK<={topn})'
        columns = ['代码', '名称', '涨幅', '热榜']
        return self._get_stock_selection_data(filter_condition, str(topn), columns)
    
    def get_raise_stocks(self, topn: int) -> pd.DataFrame:
        """
        获取涨幅超8%的股票
        
        Args:
            topn: 获取数量
            
        Returns:
            包含股票信息的DataFrame
        """
        filter_condition = '(CHANGE_RATE>=8)(CHANGE_RATE<=21)'
        columns = ['代码', '名称', '涨幅']
        return self._get_stock_selection_data(filter_condition, str(topn), columns)
    
    def get_stock_data(self, stock_codes: List[str]) -> pd.DataFrame:
        """
        获取股票行情数据
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            包含股票行情的DataFrame
        """
        stock_codes_formatted = [self._format_stock_code(code, 'market') for code in stock_codes]
        stock_codes_str = ','.join(stock_codes_formatted)
        
        url = (f'https://push2.eastmoney.com/api/qt/ulist.np/get?'
               f'ut=f057cbcbce2a86e2866ab8877db1d059&fltt=2&invt=2&'
               f'fields=f14,f148,f3,f12,f2,f13,f29,f8,f10&'
               f'secids={stock_codes_str}&_={int(time.time())}')
        
        response_data = self._make_http_request(url)
        if not response_data or 'data' not in response_data or 'diff' not in response_data['data']:
            return pd.DataFrame()
        
        parsed_data = []
        for item in response_data['data']['diff']:
            stock_data = {
                '代码': item['f12'],
                '名称': self._format_name_with_padding(item['f14']),
                '最新价': item['f2'],
                '涨幅': item['f3'],
                '换手': item['f8'],
                '量比': item['f10']
            }
            parsed_data.append(stock_data)
        
        return self._create_dataframe_from_list(parsed_data)
    
    def get_stock_label(self, stock_codes: List[str]) -> pd.DataFrame:
        """
        获取股票标签信息
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            包含股票标签的DataFrame
        """
        stock_codes_formatted = [self._format_stock_code(code, 'exchange') for code in stock_codes]
        stock_groups = [stock_codes_formatted[i:i + 90] for i in range(0, len(stock_codes_formatted), 90)]
        all_labels = []
        
        for group in stock_groups:
            stock_codes_str = ','.join(group)
            url = "https://emappdata.eastmoney.com/label/getSecurityCodeLabelList"
            
            headers = self._get_default_headers()
            data = {
                "appId": "appId01",
                "globalId": self.globalId,
                "securityCodes": stock_codes_str
            }
            
            response_data = self._make_http_request(url, 'POST', headers, data)
            if not response_data or 'data' not in response_data:
                continue
            
            parsed_data = []
            for item in response_data['data']:
                src_security_code = item.get('srcSecurityCode', '').replace(' ', '')
                label_names = ','.join([
                    lbl.get('labelName', '').replace(' ', '') 
                    for lbl in item.get('labelItemList', [])
                ])
                label_names = label_names[:20]
                
                parsed_data.append({
                    '代码': src_security_code[2:] if src_security_code[:2] in ['SH', 'SZ'] else src_security_code,
                    '标签': label_names
                })
            
            if parsed_data:
                df = self._create_dataframe_from_list(parsed_data)
                all_labels.append(df)
        
        return pd.concat(all_labels, ignore_index=True) if all_labels else pd.DataFrame()
    
    # ==================== 历史数据获取方法 ====================
    
    def get_stock_his(self, stock_code: str, klt: int, start_date: str) -> pd.DataFrame:
        """
        获取股票历史数据（东方财富接口）
        
        Args:
            stock_code: 股票代码
            klt: K线类型
            start_date: 开始日期
            
        Returns:
            包含历史数据的DataFrame
        """
        stock_code_formatted = self._format_stock_code(stock_code, 'market')
        end_date = datetime.date.today().strftime('%Y%m%d')
        
        url = (f'https://push2his.eastmoney.com/api/qt/stock/kline/get?'
               f'secid={stock_code_formatted}&'
               f'fields1=f1,f2,f3,f4,f5,f6&'
               f'fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&'
               f'klt={klt}&fqt=1&beg={start_date}&end={end_date}&'
               f'smplmt=854&lmt=1000000&_=')
        
        # 记录请求日志
        log_file = os.path.join(self.data_dir, 'data', 'stock_his.txt')
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f'{stock_code} {klt}\n')
        except Exception:
            pass  # 忽略日志写入错误
        
        response_data = self._make_http_request(url)
        if (not response_data or 'data' not in response_data 
            or 'klines' not in response_data['data']):
            return pd.DataFrame()
        
        klines = response_data['data']['klines']
        stock_name = response_data['data']['name']
        
        parsed_data = []
        for item in klines:
            split_data = item.split(',')
            parsed_data.append({
                '代码': response_data['data']['code'],
                '名称': self._format_name_with_padding(stock_name),
                '时间': split_data[0],
                '收盘': pd.to_numeric(split_data[2], errors='coerce'),
                '涨幅': pd.to_numeric(split_data[8]),
                '成交量': pd.to_numeric(split_data[5], errors='coerce'),
                '成交额': round(pd.to_numeric(split_data[6], errors='coerce') / 100000000, 3)
            })
        
        return self._create_dataframe_from_list(parsed_data)
    
    def get_stock_his_ak(self, stock_code: str, klt: str, start_date: str) -> pd.DataFrame:
        """
        获取股票历史数据（akshare接口）
        
        Args:
            stock_code: 股票代码
            klt: K线类型
            start_date: 开始日期
            
        Returns:
            包含历史数据的DataFrame
        """
        stock_code_formatted = self._format_stock_code(stock_code, 'akshare')
        
        try:
            ak_df = ak.stock_zh_a_minute(symbol=stock_code_formatted, period=klt, adjust="qfq")
            if ak_df.empty:
                return pd.DataFrame()
            
            df = ak_df[ak_df["day"].astype(str).str.replace("-", "").str[:8] >= start_date]
            
            with warnings.catch_warnings():
                warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)
                df['day'] = df['day'].astype(str).str[:-3]
                df['代码'] = stock_code
                df = df.rename(columns={
                    'day': '时间',
                    'close': '收盘',
                    'volume': '成交量'
                })
                df = df[['代码', '时间', '收盘', '成交量']]
            
            return df
        except Exception as e:
            print(f"获取akshare数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_his_tx(self, stock_code: str, klt: int, start_date: str, days: int) -> pd.DataFrame:
        """
        获取股票历史数据（腾讯接口）
        
        Args:
            stock_code: 股票代码
            klt: K线类型（分钟）
            start_date: 开始日期
            days: 天数
            
        Returns:
            包含历史数据的DataFrame
        """
        stock_code_formatted = self._format_stock_code(stock_code, 'tencent')
        klinenum = days * 60 * 4 / klt
        
        url = (f'https://ifzq.gtimg.cn/appstock/app/kline/mkline?'
               f'param={stock_code_formatted},m{klt},,{klinenum}&'
               f'_var=m{klt}_today&r=0.746391768382973')
        
        try:
            response = requests.get(url)
            response_text = response.content.decode('utf-8')
            json_str = response_text.replace(f"m{klt}_today=", "")
            data = json.loads(json_str)
            
            if (not data or 'data' not in data 
                or stock_code_formatted not in data['data']
                or f'm{klt}' not in data['data'][stock_code_formatted]):
                return pd.DataFrame()
            
            klines = data['data'][stock_code_formatted][f'm{klt}']
            
            parsed_data = []
            for item in klines:
                time_str = item[0]
                formatted_time = f"{time_str[:4]}-{time_str[4:6]}-{time_str[6:8]} {time_str[8:10]}:{time_str[10:]}"
                
                parsed_data.append({
                    '代码': stock_code,
                    '名称': '',
                    '时间': formatted_time,
                    '收盘': pd.to_numeric(item[2], errors='coerce'),
                    '涨幅': 0,
                    '成交量': round(pd.to_numeric(item[5], errors='coerce')),
                    '成交额': 0
                })
            
            return self._create_dataframe_from_list(parsed_data)
        except Exception as e:
            print(f"获取腾讯数据失败: {e}")
            return pd.DataFrame()
    
    # ==================== 九转分析方法 ====================
    
    def get_niceturn_latest(self, stock_codes: List[str], klt: int = 101, 
                           start_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取九转最新情况
        
        Args:
            stock_codes: 股票代码列表
            klt: K线类型
            start_date: 开始日期
            
        Returns:
            包含九转分析的DataFrame
        """
        if start_date is None:
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y%m%d')
        
        all_results = []
        
        for stock_code in stock_codes:
            his_data = self.get_stock_his(stock_code, klt, start_date)
            if his_data.empty:
                continue
            
            # 计算九转
            his_data_with_turn = self.calc_niceturn(his_data, 4)
            
            # 获取最新的九转值
            latest_turn = his_data_with_turn.iloc[-1]
            
            result = {
                '代码': stock_code,
                '时间': latest_turn['时间'],
                '九转': latest_turn['九转']
            }
            all_results.append(result)
        
        return self._create_dataframe_from_list(all_results)
    
    # ==================== AI相关方法 ====================
    
    def get_ai_analysis(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """
        使用AI进行分析
        
        Args:
            prompt: 分析提示
            model: 使用的模型
            
        Returns:
            AI分析结果
        """
        try:
            client = OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI分析失败: {e}")
            return ""
    
    # ==================== 数据导出方法 ====================
    
    def export_to_excel(self, data_dict: Dict[str, pd.DataFrame], filename: str):
        """
        导出多个DataFrame到Excel文件
        
        Args:
            data_dict: 包含sheet名称和DataFrame的字典
            filename: 输出文件名
        """
        try:
            filepath = os.path.join(self.filedir_data, filename)
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, df in data_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"数据已导出到: {filepath}")
        except Exception as e:
            print(f"导出Excel失败: {e}")
    
    def get_summary_report(self, stock_codes: List[str]) -> Dict[str, pd.DataFrame]:
        """
        获取股票综合报告
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            包含多个分析结果的字典
        """
        report = {}
        
        # 基本行情数据
        report['基本行情'] = self.get_stock_data(stock_codes)
        
        # 标签信息
        report['概念标签'] = self.get_stock_label(stock_codes)
        
        # 九转分析
        report['九转分析'] = self.get_niceturn_latest(stock_codes)
        
        return report