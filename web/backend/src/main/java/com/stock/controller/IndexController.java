package com.stock.controller;

import com.stock.common.Result;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/")
public class IndexController {

    @GetMapping
    public Result<Map<String, Object>> index() {
        Map<String, Object> data = new HashMap<>();
        data.put("name", "资讯后端服务");
        data.put("version", "1.0.0");
        data.put("status", "运行中");
        
        Map<String, String> endpoints = new HashMap<>();
        endpoints.put("健康检查", "/api/health/check");
        endpoints.put("用户登录", "POST /api/auth/login");
        endpoints.put("用户注册", "POST /api/auth/register");
        endpoints.put("获取主题日期", "GET /api/subject/dates");
        endpoints.put("获取主题消息", "GET /api/subject/messages?date=YYYY-MM-DD");
        
        data.put("可用接口", endpoints);
        data.put("提示", "所有接口都需要以 /api 开头");
        
        return Result.success(data);
    }
}




