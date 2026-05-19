import pandas as pd
import numpy as np
import pymysql
from typing import Optional, List

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

    def db_upsert_dataframe(
        df: pd.DataFrame,
        table_name: str,
        key1: Optional[str] = None,
        key2: Optional[str] = None
    ):
        conn = db_get_mysql_conn()
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

    def db_query_dataframe(sql: str) -> pd.DataFrame:
        conn = db_get_mysql_conn()
        try:
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()