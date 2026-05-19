package com.stock.controller;

import com.stock.common.Result;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/health")
public class HealthController {

    @GetMapping("/check")
    public Result<Map<String, String>> healthCheck() {
        Map<String, String> data = new HashMap<>();
        data.put("status", "ok");
        data.put("message", "服务运行正常");
        data.put("timestamp", String.valueOf(System.currentTimeMillis()));
        return Result.success(data);
    }
}

