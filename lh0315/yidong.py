import pandas as pd
import myLib
import datetime
import numpy as np

def calc_alert_days(stock_codes):
    filedir_database = 'E:/python_workspace/cf/database'
    file_name = f"{filedir_database}/stock_spot.db"
    df_his = pd.read_csv(file_name)
    df_his['代码'] = df_his['代码'].astype(str).str.zfill(6)
    result = []
    for stock_code in stock_codes:
        # 过滤出对应的股票数据
        stock_data = df_his[df_his['代码'] == stock_code]
        max_date = stock_data['时间'].max()
        df = stock_data.tail(40)
        # 初始化变量
        prices = df['最新价'].iloc[-30:].tolist()  # 存储每天的价格变化
        days = 0  # 计算天数
        alert_days_10 = None  # 10天规则触发天数
        alert_days_30 = None  # 30天规则触发天数
        # 模拟每天的价格变化
        while True:
            days += 1
            new_price = prices[-1] * 1.10  # 每天涨幅10%
            prices.append(new_price)  # 更新价格列表
            # 判断是否触发10天规则
            if alert_days_10 is None:
                deviation_10 = (prices[-1] / prices[-11] - 1) * 100  # 当前价格与10天前价格的涨幅
                if deviation_10 >= 100:
                    alert_days_10 = days
            # 判断是否触发30天规则
            if alert_days_30 is None:
                deviation_30 = (prices[-1] / prices[-31] - 1) * 100  # 当前价格与30天前价格的涨幅
                if deviation_30 >= 200:
                    alert_days_30 = days
            # 如果两个规则都已触发，退出循环
            if alert_days_10 is not None and alert_days_30 is not None:
                break
        result.append({
            '代码': stock_code,
            '警告': f'{max_date}/{alert_days_10}/{alert_days_30}'
        })
    df = pd.DataFrame(result)
    return df

# 调用函数计算触发天数
df = calc_alert_days(['605100','000002'])

print(df)
