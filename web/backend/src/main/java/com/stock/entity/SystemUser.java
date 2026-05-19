package com.stock.entity;

import lombok.Data;
import java.io.Serializable;

@Data
public class SystemUser implements Serializable {
    private Long id;
    private String userName;
    private String password;
}





