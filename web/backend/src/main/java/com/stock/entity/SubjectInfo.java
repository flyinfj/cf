package com.stock.entity;

import lombok.Data;
import java.io.Serializable;

@Data
public class SubjectInfo implements Serializable {
    private Long id;
    private Long categoryCode;
    private String stockCode;
    private String stockName;
}





