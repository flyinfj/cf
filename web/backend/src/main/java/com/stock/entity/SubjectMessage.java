package com.stock.entity;

import lombok.Data;
import java.io.Serializable;
import java.util.Date;

@Data
public class SubjectMessage implements Serializable {
    private Date createTime;
    private String categoryCode;
    private String categoryName;
    private Double pctChg;
    private String description;
}





