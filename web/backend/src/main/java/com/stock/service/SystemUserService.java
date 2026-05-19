package com.stock.service;

import com.stock.entity.SystemUser;

public interface SystemUserService {
    SystemUser login(String userName, String password);
    boolean register(SystemUser user);
}





