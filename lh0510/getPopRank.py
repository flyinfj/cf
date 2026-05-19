import tools
import pandas as pd
from datetime import datetime

files = {
            'type': (None, 'RPTA_SECURITY_STOCKSELECT'),
            'sty': (None, 'SECUCODE,POPULARITY_RANK'),
            'filter': (None, f'(POPULARITY_RANK>=0)'),
            'p': (None, '1'),
            'ps': (None, '6000'),
            'sr': (None, '-1'),
            'st': (None, 'CHANGE_RATE'),
            'source': (None, 'SELECT_SECURITIES'),
            'client': (None, 'APP')
        }
url = "https://datacenter.eastmoney.com/stock/selection/api/data/get/"
res = tools.Tools.eastmoney_file(url, files=files)
data = res.json()
items = data['result']['data'] if 'result' in data and 'data' in data['result'] else []
trade_date = datetime.now().strftime('%Y%m%d')
tools.Tools.db_exec(f"DELETE FROM stock_pop WHERE trade_date='{trade_date}'")
rows = [{'stock_code': str(item['SECURITY_CODE']), 'trade_date': trade_date, 'pop_rank': int(round(item['POPULARITY_RANK']))} for item in items]
df = pd.DataFrame(rows, columns=['stock_code','trade_date','pop_rank'])
if not df.empty:
    tools.Tools.db_batchinset(df, 'stock_pop')
print(f"Inserted {len(rows)} rows into stock_pop for {trade_date}")