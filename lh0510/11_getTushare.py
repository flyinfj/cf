import minishare as ms
import tools
#实时行情
token = "HDW38b5MGN5Um1Gr5HyXOit6LhbhBAd5VNkURy7UodaqHU0t021alfSq88e378e9"
df = ms.pro_api(token).rt_k_ms(
    ts_code="3*.SZ,6*.SH,0*.SZ,9*.BJ"
)
df['ts_code'] = df['ts_code'].str.replace('.SZ', '').str.replace('.SH', '').str.replace('.BJ', '')
df.rename(columns={'ts_code': 'stock_code'}, inplace=True)
df.rename(columns={'name': 'stock_name'}, inplace=True)
#tools.Tools().db_upsert(df, 'stock_rt_k_ms', 'stock_code','')

tools.Tools().db_batchinset(df, 'stock_rt_k_ms',1)
print(df)
