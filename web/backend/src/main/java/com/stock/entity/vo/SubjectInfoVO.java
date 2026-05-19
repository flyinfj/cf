package com.stock.entity.vo;

import lombok.Data;
import java.io.Serializable;

@Data
public class SubjectInfoVO implements Serializable {
    private String category1;  // 题材
    private String category2;  // 分类
    private String category3;  // 子类
    private String stockCode;  // 代码
    private String stockName;  // 名称
    private String remarks;    // 备注
    // 关联 stock_rt_k_ms 实时行情
    private java.math.BigDecimal preClose;     // 昨收盘价
    private java.math.BigDecimal high;          // 最高价
    private java.math.BigDecimal open;          // 开盘价
    private java.math.BigDecimal low;           // 最低价
    private java.math.BigDecimal close;         // 当前价
    private Long vol;                           // 成交量（手）
    private java.math.BigDecimal amount;        // 成交额（元）
    private java.math.BigDecimal pctChg;        // 涨跌幅（%）
    private java.math.BigDecimal vr;            // 量比
    private java.math.BigDecimal turnoverRate;  // 换手率（%）
}


