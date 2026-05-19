package com.stock.entity.vo;

import lombok.Data;
import java.io.Serializable;

@Data
public class IndustryCategoryVO implements Serializable {
    private String categoryCode;
    private String category;
    /** 子分类数量，>0 时可展开加载子节点 */
    private Integer childCategory;
    /** 涨幅(%) 平均 */
    private Double pctChg;
    /** 涨幅分布：涨/平/跌 数量，如 "5/0/3" */
    private String pctdis;
    /** 成交量 */
    private Long vol;
    /** 成交额(元) */
    private Long amount;
}
