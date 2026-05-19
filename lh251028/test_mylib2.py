#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 MyLib2 重构后的功能
验证各个方法是否正常工作
"""

from myLib2 import MyLib2
import pandas as pd


def test_basic_functionality():
    """测试基本功能"""
    print("=" * 50)
    print("测试 MyLib2 基本功能")
    print("=" * 50)
    
    # 初始化
    lib = MyLib2()
    print(f"✓ 初始化成功")
    print(f"  - 数据目录: {lib.data_dir}")
    print(f"  - 市场类型: {lib.marketType}")
    
    # 测试股票代码格式化
    test_codes = ['000001', '600000', '300001']
    print(f"\n✓ 股票代码格式化测试:")
    for code in test_codes:
        market_code = lib._format_stock_code(code, 'market')
        exchange_code = lib._format_stock_code(code, 'exchange')
        akshare_code = lib._format_stock_code(code, 'akshare')
        print(f"  - {code} -> market: {market_code}, exchange: {exchange_code}, akshare: {akshare_code}")


def test_trade_dates():
    """测试交易日期获取"""
    print("\n" + "=" * 50)
    print("测试交易日期获取")
    print("=" * 50)
    
    lib = MyLib2()
    
    try:
        trade_dates = lib.get_trade_dates(predays=5)
        if not trade_dates.empty:
            print(f"✓ 获取交易日期成功，共 {len(trade_dates)} 条记录")
            print(trade_dates.head())
        else:
            print("⚠ 交易日期数据为空")
    except Exception as e:
        print(f"✗ 获取交易日期失败: {e}")


def test_stock_data():
    """测试股票数据获取"""
    print("\n" + "=" * 50)
    print("测试股票数据获取")
    print("=" * 50)
    
    lib = MyLib2()
    test_codes = ['000001', '600000']
    
    try:
        stock_data = lib.get_stock_data(test_codes)
        if not stock_data.empty:
            print(f"✓ 获取股票数据成功，共 {len(stock_data)} 条记录")
            print(stock_data)
        else:
            print("⚠ 股票数据为空")
    except Exception as e:
        print(f"✗ 获取股票数据失败: {e}")


def test_popular_stocks():
    """测试热门股票获取"""
    print("\n" + "=" * 50)
    print("测试热门股票获取")
    print("=" * 50)
    
    lib = MyLib2()
    
    try:
        # 测试条件选股
        cond_stocks = lib.get_cond_popu_stocks(50)
        if not cond_stocks.empty:
            print(f"✓ 获取条件选股成功，共 {len(cond_stocks)} 条记录")
            print(cond_stocks.head())
        else:
            print("⚠ 条件选股数据为空")
    except Exception as e:
        print(f"✗ 获取条件选股失败: {e}")


def test_technical_analysis():
    """测试技术分析功能"""
    print("\n" + "=" * 50)
    print("测试技术分析功能")
    print("=" * 50)
    
    lib = MyLib2()
    
    # 创建测试数据
    test_data = pd.DataFrame({
        '收盘': [10, 11, 12, 11, 10, 9, 10, 11, 12, 13, 12, 11, 10, 9, 8]
    })
    
    try:
        result = lib.calc_niceturn(test_data, 4)
        if '九转' in result.columns:
            print("✓ 神奇九转计算成功")
            print(result[['收盘', 'ud', '九转']].tail())
        else:
            print("⚠ 九转计算结果异常")
    except Exception as e:
        print(f"✗ 九转计算失败: {e}")


def test_data_export():
    """测试数据导出功能"""
    print("\n" + "=" * 50)
    print("测试数据导出功能")
    print("=" * 50)
    
    lib = MyLib2()
    
    # 创建测试数据
    test_data = {
        'Sheet1': pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}),
        'Sheet2': pd.DataFrame({'C': [7, 8, 9], 'D': [10, 11, 12]})
    }
    
    try:
        lib.export_to_excel(test_data, 'test_export.xlsx')
        print("✓ Excel导出功能测试完成")
    except Exception as e:
        print(f"✗ Excel导出失败: {e}")


def main():
    """主测试函数"""
    print("开始测试 MyLib2 重构后的功能...")
    
    # 运行各项测试
    test_basic_functionality()
    test_trade_dates()
    test_stock_data()
    test_popular_stocks()
    test_technical_analysis()
    test_data_export()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()