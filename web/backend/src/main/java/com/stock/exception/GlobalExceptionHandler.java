package com.stock.exception;

import com.stock.common.Result;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.NoHandlerFoundException;

import javax.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理404错误
     */
    @ExceptionHandler(NoHandlerFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public Result<Map<String, Object>> handleNotFound(NoHandlerFoundException ex, HttpServletRequest request) {
        String path = request.getRequestURI();
        
        Map<String, Object> data = new HashMap<>();
        data.put("error", "未找到请求路径");
        data.put("path", path);
        data.put("message", "请确保路径以 /api 开头");
        
        Map<String, String> availableEndpoints = new HashMap<>();
        availableEndpoints.put("健康检查", "GET /api/health/check");
        availableEndpoints.put("用户登录", "POST /api/auth/login");
        availableEndpoints.put("用户注册", "POST /api/auth/register");
        availableEndpoints.put("获取主题日期", "GET /api/subject/dates");
        availableEndpoints.put("获取主题消息", "GET /api/subject/messages?date=YYYY-MM-DD");
        availableEndpoints.put("API信息", "GET /api/");
        
        data.put("可用接口", availableEndpoints);
        
        Result<Map<String, Object>> result = new Result<>();
        result.setCode(404);
        result.setMessage("未找到请求路径: " + path);
        result.setData(data);
        return result;
    }

    /**
     * 处理其他异常
     */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Result<String> handleException(Exception ex, HttpServletRequest request) {
        String message = "服务器内部错误: " + ex.getMessage();
        // 生产环境可以隐藏详细错误信息
        return Result.error(500, message);
    }
}

