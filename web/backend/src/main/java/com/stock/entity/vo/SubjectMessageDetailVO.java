package com.stock.entity.vo;

import lombok.Data;
import java.io.Serializable;
import java.util.Date;
import java.util.List;

@Data
public class SubjectMessageDetailVO implements Serializable {
    private Date createTime;
    private String categoryCode;
    private String categoryName;
    private Double pctChg;
    private String description;
    private List<SubjectInfoVO> stockList;
}





