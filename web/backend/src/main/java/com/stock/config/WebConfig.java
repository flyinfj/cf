package com.stock.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Value("${cors.allowed-origins}")
    private String allowedOrigins;
    
    @Value("${cors.enable-all-origins:false}")
    private boolean enableAllOrigins;
    
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        if (enableAllOrigins) {
            // 开发/调试模式：允许所有来源（不推荐用于生产环境）
            registry.addMapping("/**")
                    .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH")
                    .allowedHeaders("*")
                    .allowCredentials(true)
                    .maxAge(3600) // 预检请求缓存时间（秒）
                    .allowedOriginPatterns("*");
        } else {
            // 生产模式：使用配置的允许来源列表
            String[] origins = allowedOrigins.split(",");
            // 使用 allowedOriginPatterns 支持更灵活的匹配（Spring Boot 2.4+）
            // 这样可以支持通配符模式，如 http://*.example.com
            registry.addMapping("/**")
                    .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH")
                    .allowedHeaders("*")
                    .allowCredentials(true)
                    .maxAge(3600) // 预检请求缓存时间（秒）
                    .allowedOriginPatterns(origins);
        }
    }
}





