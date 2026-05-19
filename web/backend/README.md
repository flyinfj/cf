# 资讯后端项目

## Maven配置说明

### 环境要求
- JDK 1.8+
- Maven 3.6+

### 快速启动

1. **编译项目**
```bash
mvn clean compile
```

2. **打包项目**
```bash
mvn clean package
```

3. **运行项目**
```bash
mvn spring-boot:run
```

4. **跳过测试打包**
```bash
mvn clean package -DskipTests
```

### 项目配置

#### 数据库配置
修改 `src/main/resources/application.yml` 中的数据库连接信息：
- 数据库地址
- 用户名
- 密码

#### 端口配置
默认端口：8080
上下文路径：/api

### 常用Maven命令

- `mvn clean` - 清理编译文件
- `mvn compile` - 编译项目
- `mvn test` - 运行测试
- `mvn package` - 打包项目（生成jar文件）
- `mvn install` - 安装到本地仓库
- `mvn spring-boot:run` - 运行Spring Boot应用

### 项目结构

```
backend/
├── src/
│   ├── main/
│   │   ├── java/com/stock/
│   │   │   ├── controller/    # 控制器层
│   │   │   ├── service/       # 服务层
│   │   │   ├── dao/           # 数据访问层
│   │   │   └── entity/        # 实体类
│   │   └── resources/
│   │       ├── mapper/        # MyBatis映射文件
│   │       └── application.yml
│   └── pom.xml
```

### 依赖说明

- Spring Boot 2.7.14
- MyBatis 2.3.1
- MySQL Connector 8.0.33
- Lombok
- FastJSON 2.0.40

### 注意事项

1. 确保数据库已创建并执行了建表语句
2. 检查数据库连接配置是否正确
3. 首次运行会下载依赖，可能需要一些时间




