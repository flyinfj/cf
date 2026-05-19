package com.stock.controller;

import com.stock.common.Result;
import com.stock.entity.SystemUser;
import com.stock.service.SystemUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
public class AuthController {

    @Autowired
    private SystemUserService systemUserService;

    @PostMapping("/login")
    public Result<SystemUser> login(@RequestBody SystemUser user) {
        SystemUser loginUser = systemUserService.login(user.getUserName(), user.getPassword());
        if (loginUser != null) {
            // 不返回密码
            loginUser.setPassword(null);
            return Result.success(loginUser);
        }
        return Result.error("用户名或密码错误");
    }

    @PostMapping("/register")
    public Result<String> register(@RequestBody SystemUser user) {
        if (user.getUserName() == null || user.getPassword() == null) {
            return Result.error("用户名和密码不能为空");
        }
        boolean success = systemUserService.register(user);
        if (success) {
            return Result.success("注册成功");
        }
        return Result.error("注册失败，用户名已存在");
    }
}





