package com.stock.service.impl;

import com.stock.dao.SystemUserDao;
import com.stock.entity.SystemUser;
import com.stock.service.SystemUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class SystemUserServiceImpl implements SystemUserService {

    @Autowired
    private SystemUserDao systemUserDao;

    @Override
    public SystemUser login(String userName, String password) {
        SystemUser user = systemUserDao.findByUserName(userName);
        if (user != null && password.equals(user.getPassword())) {
            return user;
        }
        return null;
    }

    @Override
    public boolean register(SystemUser user) {
        SystemUser existUser = systemUserDao.findByUserName(user.getUserName());
        if (existUser != null) {
            return false;
        }
        return systemUserDao.insert(user) > 0;
    }
}





