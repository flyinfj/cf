package com.stock.dao;

import com.stock.entity.SystemUser;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SystemUserDao {
    SystemUser findByUserName(@Param("userName") String userName);
    int insert(SystemUser user);
}





