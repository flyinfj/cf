import pandas as pd
import numpy as np
import pymysql
import warnings
from typing import Optional, List
import time
import requests
import subprocess
import json
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
class Tools:

    def db_get_mysql_conn():
        return pymysql.connect(
            host="120.27.198.74",
            port=3306,
            user="cfuser",
            password="Cf@123321",
            database="cfdb",
            charset="utf8mb4",
        )

    @staticmethod
    def db_upsert(
        df: pd.DataFrame,
        table_name: str,
        key1: Optional[str] = None,
        key2: Optional[str] = None
    ):
        conn = Tools.db_get_mysql_conn()
        cur = conn.cursor()
        ph = "%s"

        cols: List[str] = [c for c in df.columns]
        def q(col: str) -> str:
            return f'`{col}`'

        def norm(v):
            if v is None:
                return None
            if isinstance(v, float) and np.isnan(v):
                return None
            if isinstance(v, (np.generic,)):
                try:
                    return v.item()
                except Exception:
                    return v
            return v

        for _, row in df.iterrows():
            where_cols: List[str] = []
            where_vals: List[object] = []
            if key1 and key1 in cols and pd.notna(row[key1]):
                where_cols.append(key1)
                where_vals.append(norm(row[key1]))
            if key2 and key2 in cols and pd.notna(row[key2]):
                where_cols.append(key2)
                where_vals.append(norm(row[key2]))

            if where_cols:
                where_clause = " AND ".join([f"{q(k)}={ph}" for k in where_cols])
                cur.execute(
                    f"SELECT COUNT(*) FROM `{table_name}` WHERE {where_clause}",
                    where_vals,
                )

                exists = (cur.fetchone() or [0])[0] > 0
                if exists:
                    set_cols = [c for c in cols if c not in where_cols]
                    if set_cols:
                        set_clause = ", ".join([f"{q(c)}={ph}" for c in set_cols])
                        params = [norm(row[c]) for c in set_cols] + where_vals
                        cur.execute(
                            f"UPDATE `{table_name}` SET {set_clause} WHERE {where_clause}",
                            params,
                        )
                    else:
                        pass
                else:
                    insert_cols = ",".join([q(c) for c in cols])
                    placeholders = ",".join([ph] * len(cols))
                    params = [norm(row[c]) for c in cols]
                    cur.execute(
                        f"INSERT INTO `{table_name}` ({insert_cols}) VALUES ({placeholders})",
                        params,
                    )
            else:
                insert_cols = ",".join([q(c) for c in cols])
                placeholders = ",".join([ph] * len(cols))
                params = [norm(row[c]) for c in cols]
                cur.execute(
                    f"INSERT INTO `{table_name}` ({insert_cols}) VALUES ({placeholders})",
                    params,
                )
        conn.commit()
        conn.close()
    
    @staticmethod
    def db_batchinset(
        df: pd.DataFrame,
        table_name: str,
        if_delete: bool = False
    ):
        conn = Tools.db_get_mysql_conn()
        cur = conn.cursor()
        ph = "%s"

        cols: List[str] = [c for c in df.columns]
        def q(col: str) -> str:
            return f'`{col}`'

        def norm(v):
            if v is None:
                return None
            if isinstance(v, float) and np.isnan(v):
                return None
            if isinstance(v, (np.generic,)):
                try:
                    return v.item()
                except Exception:
                    return v
            return v
            
        if if_delete:
            cur.execute(f"delete from `{table_name}`")

        insert_cols = ",".join([q(c) for c in cols])
        placeholders = ",".join([ph] * len(cols))
        sql = f"INSERT INTO `{table_name}` ({insert_cols}) VALUES ({placeholders})"
        batch = []
        batch_size = 500
        count = 0
        for _, row in df.iterrows():
            batch.append([norm(row[c]) for c in cols])
            count += 1
            if count % batch_size == 0:
                cur.executemany(sql, batch)
                conn.commit()
                batch = []
        if batch:
            cur.executemany(sql, batch)
            conn.commit()
        conn.close()
        

    @staticmethod
    def db_query(sql: str,is_id:bool = False) -> pd.DataFrame:
        conn = Tools.db_get_mysql_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message=".*Using a non-tuple sequence for multidimensional indexing is deprecated.*",
                    category=FutureWarning,
                )
                warnings.filterwarnings(
                    "ignore",
                    message=".*Passing a BlockManager to DataFrame is deprecated.*",
                    category=FutureWarning,
                )
                warnings.filterwarnings(
                    "ignore",
                    message=".*Passing a SQLAlchemy connectable is deprecated.*",
                    category=UserWarning,
                )
                start_time = time.time()
                
                cursor.execute(sql)
                data = cursor.fetchall()
                df = pd.DataFrame(data)

                end_time = time.time()
                print(f"查询时间: {end_time - start_time} 秒")
                if not is_id and 'id' in df.columns:
                    df = df.drop(columns=['id'])
                if 'create_time' in df.columns:
                    df = df.drop(columns=['create_time'])
                return df
        finally:
            cursor.close()
            conn.close()
            
    
    @staticmethod
    def db_exec(sql: str) -> None:
        conn = Tools.db_get_mysql_conn()
        try:
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
        finally:
            conn.close()


    @staticmethod
    def eastmoney_curl(url: str,data:dict = None):
        data = data or {
            "appId": "appId01",
            "globalId": '786e4c21-70dc-435a-93bb-38',
            "marketType": "",
            "pageNo": 1,
            "pageSize": 100
        }
        headers = {
            'Host': 'emappdata.eastmoney.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'Referer': 'https://vipmoney.eastmoney.com/',
            'Origin': 'https://vipmoney.eastmoney.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        cmd = ['curl', url]
        for k, v in headers.items():
            cmd += ['-H', f'{k}: {v}']
        cmd += ['--data', json.dumps(data), '--compressed']
        start_time = time.time()
        res = subprocess.run(cmd, capture_output=True, text=True)
        Tools.ins_log(
            app="eastmoney",
            start_time=start_time,
            stop_time=time.time(),
            url=url,
            method="CURL",
            headers=headers,
            body='',
            res_status=res.returncode,
            res_data=res.stdout,
        )
        return res.stdout

    @staticmethod
    def eastmoney_curlget(url: str):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://quote.eastmoney.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive'
        }
        cmd = ['curl', url]
        for k, v in headers.items():
            cmd += ['-H', f'{k}: {v}']
        start_time = time.time()
        print(cmd)
        res = subprocess.run(cmd, capture_output=True, text=True)
        Tools.ins_log(
            app="eastmoney",
            start_time=start_time,
            stop_time=time.time(),
            url=url,
            method="CURLGET",
            headers=headers,
            body='',
            res_status=res.returncode,
            res_data=res.stdout,
        )
        return res.stdout

    @staticmethod
    def eastmoney_post(url: str,data:dict = None):
        data = data or {
            "appId": "appId01",
            "globalId": "",
            "marketType": "",
            "pageNo": 1,
            "pageSize": 100
        }
        headers = {
            'Host': 'emappdata.eastmoney.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'Referer': 'https://vipmoney.eastmoney.com/',
            'Origin': 'https://vipmoney.eastmoney.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        start_time = time.time()
        res = requests.post(url=url,headers=headers,data=json.dumps(data))
        Tools.ins_log(
            app="eastmoney",
            start_time=start_time,
            stop_time=time.time(),
            url=url,
            method="POST",
            headers=headers,
            body='',
            res_status=res.status_code,
            res_data=res.text,
        )
        return res

    @staticmethod
    def eastmoney_get(url: str):
        headers = {
            'Host': 'push2.eastmoney.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://quote.eastmoney.com/',
            'Origin': 'https://quote.eastmoney.com',
            'Connection': 'close',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }

        start_time = time.time()
        print(url)
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=1,
            allowed_methods=frozenset(['GET']),
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        last_error = None
        res = None
        for _ in range(3):
            session = requests.Session()
            session.mount('https://', adapter)
            session.mount('http://', adapter)
            session.trust_env = False
            try:
                res = session.get(url=url, headers=headers, timeout=(5, 15))
                res.raise_for_status()
                break
            except requests.exceptions.RequestException as error:
                res = None
                last_error = error
                time.sleep(1)
            finally:
                session.close()

        if res is None:
            raise requests.exceptions.ConnectionError(
                f'eastmoney_get failed after retries: {url}'
            ) from last_error

        Tools.ins_log(
            app="eastmoney",
            start_time=start_time,
            stop_time=time.time(),
            url=url,
            method="GET",
            headers=headers,
            res_status=res.status_code,
            res_data=res.text,
        )
        return res

    @staticmethod
    def tencent_get(url: str):
        start_time = time.time()
        print(url)
        res = requests.get(url=url)
        Tools.ins_log(
            app="tencent",
            start_time=start_time,
            stop_time=time.time(),
            url=url,
            method="GET",
            headers="",
            res_status=res.status_code,
            res_data=res.text,
        )
        return res

    @staticmethod
    def eastmoney_file(url: str,files: dict):
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
        start_time = time.time()
        res = requests.post(url, headers=headers, files=files)
        Tools.ins_log(
            app="eastmoney",
            start_time=start_time,
            stop_time=time.time(),
            url=url,
            method="FILE",
            headers=headers,
            body=res.text[0:4000],
            res_status=res.status_code,
            res_data=res.text[0:4000],
        )
        return res

    @staticmethod
    def ins_log(
        app: str,
        start_time,
        url: str,
        method: str,
        stop_time=None,
        headers: Optional[dict] = None,
        body: Optional[str] = None,
        res_status: Optional[int] = None,
        res_data: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        def fmt_dt(x):
            if x is None:
                return None
            if isinstance(x, (int, float)):
                try:
                    return datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    return None
            if isinstance(x, str):
                return x
            if isinstance(x, datetime):
                return x.strftime('%Y-%m-%d %H:%M:%S')
            try:
                return x.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                return None
        
        conn = Tools.db_get_mysql_conn()
        try:
            cur = conn.cursor()
            sql = (
                "INSERT INTO `api_log` (`app`,`start_time`,`stop_time`,`exec_time`,`url`,`method`,`headers`,`body`,`res_status`,`res_data`,`error_message`) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            )
            st_raw = start_time
            et_raw = stop_time if stop_time is not None else time.time()
            try:
                if isinstance(st_raw, datetime) and isinstance(et_raw, datetime):
                    exec_time = (et_raw - st_raw).total_seconds()
                else:
                    exec_time = float(et_raw) - float(st_raw)
            except Exception:
                exec_time = None
            params = [
                app,
                fmt_dt(start_time),
                fmt_dt(stop_time),
                exec_time,
                url,
                method,
                json.dumps(headers, ensure_ascii=False) if headers is not None else None,
                body,
                res_status,
                res_data,
                error_message,
            ]
            cur.execute(sql, params)
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def db_output(df: pd.DataFrame, title: str):
        conn = Tools.db_get_mysql_conn()
        try:
            cur = conn.cursor()
            # Upsert column mappings
            for i in range(len(df.columns)):
                if i >= 20:
                    break
                col_name = str(df.columns[i])
                col_id = f"col{i+1}"
                
                check_sql = "SELECT `id` FROM `output_column` WHERE `title` = %s AND `column_id` = %s"
                cur.execute(check_sql, (title, col_id))
                row = cur.fetchone()
                
                if row:
                    update_sql = "UPDATE `output_column` SET `column_name` = %s WHERE `id` = %s"
                    cur.execute(update_sql, (col_name, row[0]))
                else:
                    insert_col_sql = "INSERT INTO `output_column` (`title`, `column_id`, `column_name`) VALUES (%s, %s, %s)"
                    cur.execute(insert_col_sql, (title, col_id, col_name))
            
            # Delete existing data for title and today
            del_sql = "DELETE FROM `output` WHERE `title` = %s AND DATE(`create_time`) = CURDATE()"
            cur.execute(del_sql, (title,))
            
            # Insert new data
            insert_cols = ["`title`"] + [f"`col{i}`" for i in range(1, 21)]
            cols_str = ",".join(insert_cols)
            ph_str = ",".join(["%s"] * len(insert_cols))
            
            insert_sql = f"INSERT INTO `output` ({cols_str}) VALUES ({ph_str})"
            
            batch_data = []
            for _, row in df.iterrows():
                row_vals = []
                row_vals.append(title)
                for i in range(20):
                    if i < len(df.columns):
                        val = row.iloc[i]
                        if pd.isna(val):
                            val = None
                        else:
                            val = str(val)
                        row_vals.append(val)
                    else:
                        row_vals.append(None)
                batch_data.append(row_vals)
                
            if batch_data:
                cur.executemany(insert_sql, batch_data)
                
            conn.commit()
        finally:
            conn.close()
