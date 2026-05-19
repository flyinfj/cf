-- MySQL建表SQL语句
-- 根据项目中的文件和数据字段生成

-- 1. 板块信息表 (对应 1_getQingXu.py 中的 _bnk.txt)
CREATE TABLE IF NOT EXISTS `bnk` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `板块` VARCHAR(100) NOT NULL COMMENT '板块名称',
    `数量` INT DEFAULT 0 COMMENT '数量',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_板块` (`板块`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='板块信息表';

-- 2. 财报信息表 (对应 getCaibao.py 中的 caibao.txt)
CREATE TABLE IF NOT EXISTS `caibao` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `公告时间` VARCHAR(50) COMMENT '公告时间',
    `类型` VARCHAR(50) COMMENT '类型',
    `公告内容` TEXT COMMENT '公告内容',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY `uk_代码_类型_公告时间` (`代码`, `类型`, `公告时间`),
    INDEX `idx_代码` (`代码`),
    INDEX `idx_公告时间` (`公告时间`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='财报信息表';

-- 3. 研报行业信息表 (对应 getYanbao.py 中的 yanbao_ind.txt)
CREATE TABLE IF NOT EXISTS `yanbao_ind` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `时间` VARCHAR(50) NOT NULL COMMENT '发布时间',
    `名称` VARCHAR(100) NOT NULL COMMENT '行业名称',
    `机构` VARCHAR(100) NOT NULL COMMENT '机构名称',
    `标题` VARCHAR(500) COMMENT '标题',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY `uk_名称_机构_时间` (`名称`, `机构`, `时间`),
    INDEX `idx_时间` (`时间`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='研报行业信息表';

-- 4. 研报股票信息表 (对应 getYanbao.py 中的 yanbao_stock.txt)
CREATE TABLE IF NOT EXISTS `yanbao_stock` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `时间` VARCHAR(50) NOT NULL COMMENT '发布时间',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `评级` VARCHAR(50) COMMENT '评级',
    `标题` VARCHAR(500) COMMENT '标题',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY `uk_代码_时间` (`代码`, `时间`),
    INDEX `idx_代码` (`代码`),
    INDEX `idx_时间` (`时间`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='研报股票信息表';

-- 5. 题材信息表 (对应 getSubject.py 中的 subject.csv)
CREATE TABLE IF NOT EXISTS `subject` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `编码` VARCHAR(50) COMMENT '编码',
    `题材` VARCHAR(100) COMMENT '题材名称',
    `分类` VARCHAR(100) COMMENT '分类',
    `子类` VARCHAR(100) COMMENT '子类',
    `代码` VARCHAR(10) COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `理由` VARCHAR(500) COMMENT '理由',
    `备注` VARCHAR(500) COMMENT '备注',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_编码` (`编码`),
    INDEX `idx_代码` (`代码`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题材信息表';

-- 6. 题材股票关联表 (对应 9_getMessage.py 中的 subject_stock.csv)
CREATE TABLE IF NOT EXISTS `subject_stock` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `排序` INT COMMENT '排序',
    `代码` VARCHAR(10) COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `涨幅` VARCHAR(20) COMMENT '涨幅',
    `理由` VARCHAR(500) COMMENT '理由',
    `备注` VARCHAR(500) COMMENT '备注',
    `分类` VARCHAR(100) COMMENT '分类',
    `子类` VARCHAR(100) COMMENT '子类',
    `编码` VARCHAR(50) COMMENT '编码',
    `题材` VARCHAR(100) COMMENT '题材',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_代码` (`代码`),
    INDEX `idx_备注` (`备注`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题材股票关联表';

-- 7. 临时题材股票表 (对应 9_getMessage.py 中的 tmp_subject_stock.csv)
CREATE TABLE IF NOT EXISTS `tmp_subject_stock` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `备注` VARCHAR(500) COMMENT '备注',
    `涨幅` DECIMAL(10,2) COMMENT '涨幅',
    `trade_date` VARCHAR(20) COMMENT '交易日期',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_代码` (`代码`),
    INDEX `idx_备注` (`备注`),
    INDEX `idx_trade_date` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='临时题材股票表';

-- 8. 涨停历史表 (对应 7_getLimitUp.py 和 8_getLimitUpBank.py 中的 days_limitup_pre.db)
CREATE TABLE IF NOT EXISTS `days_limitup_pre` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `时间` VARCHAR(20) NOT NULL COMMENT '交易日期',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `昨板数` INT COMMENT '昨日板数',
    `今板数` INT COMMENT '今日板数',
    `涨幅` DECIMAL(10,2) COMMENT '涨幅',
    `是否涨停` VARCHAR(10) COMMENT '是否涨停',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_时间` (`时间`),
    INDEX `idx_代码` (`代码`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='涨停历史表';

-- 9. 涨停统计表 (对应 7_getLimitUp.py 和 8_getLimitUpBank.py 中的 days_limitup_count.db)
CREATE TABLE IF NOT EXISTS `days_limitup_count` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `涨停排序` INT COMMENT '涨停排序',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `涨停数` INT DEFAULT 0 COMMENT '涨停数',
    `第二天涨次数` INT DEFAULT 0 COMMENT '第二天涨次数',
    `平均涨幅` VARCHAR(20) COMMENT '平均涨幅',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY `uk_代码` (`代码`),
    INDEX `idx_涨停排序` (`涨停排序`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='涨停统计表';

-- 10. 股票实时行情表 (对应 getTrend.py 中的 stock_spot.db)
CREATE TABLE IF NOT EXISTS `stock_spot` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `时间` VARCHAR(20) NOT NULL COMMENT '交易日期',
    `最新价` DECIMAL(10,2) COMMENT '最新价',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_代码_时间` (`代码`, `时间`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票实时行情表';

-- 11. 股票统计表 (对应 getTrend.py 中的 stock_stats.db)
CREATE TABLE IF NOT EXISTS `stock_stats` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `ma1` DECIMAL(10,2) COMMENT 'MA1',
    `ma5` DECIMAL(10,2) COMMENT 'MA5',
    `ma10` DECIMAL(10,2) COMMENT 'MA10',
    `ma20` DECIMAL(10,2) COMMENT 'MA20',
    `ma60` DECIMAL(10,2) COMMENT 'MA60',
    `max20` DECIMAL(10,2) COMMENT 'MAX20',
    `min20` DECIMAL(10,2) COMMENT 'MIN20',
    `max60` DECIMAL(10,2) COMMENT 'MAX60',
    `min60` DECIMAL(10,2) COMMENT 'MIN60',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY `uk_代码` (`代码`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票统计表';

-- 12. 股票实时数据表 (对应 getTrend.py 中的 stock_real.db)
CREATE TABLE IF NOT EXISTS `stock_real` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `最新价` DECIMAL(10,2) COMMENT '最新价',
    `涨跌幅` DECIMAL(10,2) COMMENT '涨跌幅',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_代码` (`代码`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票实时数据表';

-- 13. 临时股票实时表 (对应 getTrend.py 中的 tmp_stock_real.db)
CREATE TABLE IF NOT EXISTS `tmp_stock_real` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `涨幅` DECIMAL(10,2) COMMENT '涨幅',
    `时间` VARCHAR(20) COMMENT '交易日期',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_代码_时间` (`代码`, `时间`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='临时股票实时表';

-- 14. 股东信息表 (对应 getStockInfo.py 中的 quar_holder_info.db)
CREATE TABLE IF NOT EXISTS `quar_holder_info` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `股本` VARCHAR(100) COMMENT '股本信息',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY `uk_代码` (`代码`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股东信息表';

-- 15. 涨停股统计信息表 (对应 7_getLimitUp.py 中的涨停股统计信息)
CREATE TABLE IF NOT EXISTS `limitup_summary` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `建议仓位` VARCHAR(50) COMMENT '建议仓位',
    `涨停数今昨` VARCHAR(50) COMMENT '涨停数(今/昨)',
    `封板率今昨` VARCHAR(50) COMMENT '封板率(今/昨)',
    `涨幅今昨` VARCHAR(50) COMMENT '涨幅(今/昨)',
    `跌停数今昨` VARCHAR(50) COMMENT '跌停数(今/昨)',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='涨停股统计信息表';

-- 16. 强势板块信息表 (对应 7_getLimitUp.py 中的强势板块信息)
CREATE TABLE IF NOT EXISTS `limitup_sector` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `板一板数高度` VARCHAR(100) COMMENT '板一/板数/高度',
    `板二板数高度` VARCHAR(100) COMMENT '板二/板数/高度',
    `板三板数高度` VARCHAR(100) COMMENT '板三/板数/高度',
    `板四板数高度` VARCHAR(100) COMMENT '板四/板数/高度',
    `板五板数高度` VARCHAR(100) COMMENT '板五/板数/高度',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='强势板块信息表';

-- 17. 龙头股信息表 (对应 7_getLimitUp.py 中的龙头股信息)
CREATE TABLE IF NOT EXISTS `limitup_leading` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `板块` VARCHAR(100) COMMENT '板块',
    `高度` INT COMMENT '高度',
    `标签` VARCHAR(500) COMMENT '标签',
    `警告` VARCHAR(100) COMMENT '警告',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_代码` (`代码`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='龙头股信息表';

-- 18. 连板天梯信息表 (对应 7_getLimitUp.py 中的连板天梯信息)
CREATE TABLE IF NOT EXISTS `limitup_cons` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `昨板数` INT COMMENT '昨板数',
    `今板数` VARCHAR(10) COMMENT '今板数',
    `昨涨停数` INT COMMENT '昨涨停数',
    `连板成功` INT COMMENT '连板成功',
    `连板成功率` VARCHAR(20) COMMENT '连板成功率',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='连板天梯信息表';

-- 19. 个股连板情况表 (对应 7_getLimitUp.py 中的个股连板情况)
CREATE TABLE IF NOT EXISTS `limitup_stock` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `昨板数` INT COMMENT '昨板数',
    `今板数` VARCHAR(10) COMMENT '今板数',
    `成功` VARCHAR(10) COMMENT '成功',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `涨幅` VARCHAR(20) COMMENT '涨幅',
    `标签` VARCHAR(500) COMMENT '标签',
    `警告` VARCHAR(100) COMMENT '警告',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_代码` (`代码`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个股连板情况表';

-- 20. 昨日涨停成交量分析表 (对应 7_getLimitUp.py 中的昨日涨停成交量分析)
CREATE TABLE IF NOT EXISTS `limitup_vol_analysis` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `涨幅` VARCHAR(20) COMMENT '涨幅',
    `昨套牢` VARCHAR(20) COMMENT '昨套牢',
    `昨获利` VARCHAR(20) COMMENT '昨获利',
    `今套牢` VARCHAR(20) COMMENT '今套牢',
    `今获利` VARCHAR(20) COMMENT '今获利',
    `今正常` VARCHAR(20) COMMENT '今正常',
    `今总量` VARCHAR(20) COMMENT '今总量',
    `标签` VARCHAR(500) COMMENT '标签',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_代码` (`代码`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='昨日涨停成交量分析表';

-- 21. 涨停趋势统计表 (对应 10_getLimitTrend.py)
CREATE TABLE IF NOT EXISTS `limit_trend_stats` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `ratio_down` VARCHAR(20) COMMENT '下跌比例区间',
    `count` INT COMMENT '总数',
    `up00_10` INT COMMENT 'up00-10',
    `up10_20` INT COMMENT 'up10-20',
    `up20_30` INT COMMENT 'up20-30',
    `up30_plus` INT COMMENT 'up30-++',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='涨停趋势统计表';

-- 22. 涨停趋势详情表 (对应 10_getLimitTrend.py)
CREATE TABLE IF NOT EXISTS `limit_trend_detail` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `dw_label` VARCHAR(20) COMMENT '下跌标签',
    `up_label` VARCHAR(20) COMMENT '上涨标签',
    `代码` TEXT COMMENT '股票代码列表',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='涨停趋势详情表';

-- 23. 趋势统计表 (对应 getTrend.py 中的 trend.html)
CREATE TABLE IF NOT EXISTS `trend` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `时间` VARCHAR(20) COMMENT '交易日期',
    `新低60` INT COMMENT '新低60',
    `新低20` INT COMMENT '新低20',
    `l20_10_5` VARCHAR(20) COMMENT 'l20_10_5',
    `l20_5_10` VARCHAR(20) COMMENT 'l20_5_10',
    `m10_20_5` VARCHAR(20) COMMENT 'm10_20_5',
    `m10_5_20` VARCHAR(20) COMMENT 'm10_5_20',
    `h5_20_10` VARCHAR(20) COMMENT 'h5_20_10',
    `l5_10_20` VARCHAR(20) COMMENT 'l5_10_20',
    `新高20` INT COMMENT '新高20',
    `新高60` INT COMMENT '新高60',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_时间` (`时间`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='趋势统计表';

-- 24. 超卖股票表 (对应 getTrend.py 中的超卖股票)
CREATE TABLE IF NOT EXISTS `oversold_stock` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `名称` VARCHAR(50) COMMENT '股票名称',
    `BIAS6` DECIMAL(10,2) COMMENT 'BIAS6',
    `BIAS12` DECIMAL(10,2) COMMENT 'BIAS12',
    `BIAS24` DECIMAL(10,2) COMMENT 'BIAS24',
    `标签` VARCHAR(500) COMMENT '标签',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_代码` (`代码`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='超卖股票表';

-- 注意：以下表由于数据字段动态变化较大，建议根据实际输出字段动态创建
-- 或者使用通用表结构存储JSON格式数据

-- 25. 通用数据表 (用于存储动态字段的数据，如通过output_file输出的各种数据)
CREATE TABLE IF NOT EXISTS `general_data` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `数据类型` VARCHAR(100) COMMENT '数据类型/标题',
    `数据内容` JSON COMMENT '数据内容(JSON格式)',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_数据类型` (`数据类型`),
    INDEX `idx_创建时间` (`创建时间`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通用数据表';

-- 26. 股票代码列表表 (用于存储只包含代码的文件，如 _popu_stock.txt, _stock.txt)
CREATE TABLE IF NOT EXISTS `stock_code_list` (
    `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    `代码` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `数据类型` VARCHAR(100) COMMENT '数据类型',
    `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_代码` (`代码`),
    INDEX `idx_数据类型` (`数据类型`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票代码列表表';


