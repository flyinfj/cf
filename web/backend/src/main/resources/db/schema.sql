
CREATE TABLE `stock_rt_k_ms` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `stock_code` varchar(20) NOT NULL COMMENT '股票代码（如600000.SH）',
  `stock_name` varchar(50) DEFAULT '' COMMENT '股票名称',
  `pre_close` decimal(10,2) DEFAULT '0.00' COMMENT '昨收盘价',
  `high` decimal(10,2) DEFAULT '0.00' COMMENT '最高价',
  `open` decimal(10,2) DEFAULT '0.00' COMMENT '开盘价',
  `low` decimal(10,2) DEFAULT '0.00' COMMENT '最低价',
  `close` decimal(10,2) DEFAULT '0.00' COMMENT '当前价/收盘价',
  `vol` bigint(20) DEFAULT '0' COMMENT '成交量（手）',
  `amount` decimal(20,2) DEFAULT '0.00' COMMENT '成交额（元）',
  `change` decimal(10,2) DEFAULT '0.00' COMMENT '涨跌额（需反引号，关键字）',
  `pct_chg` decimal(10,2) DEFAULT '0.00' COMMENT '涨跌幅（%）',
  `vr` decimal(10,2) DEFAULT '0.00' COMMENT '成交量比率',
  `turnover_rate` decimal(10,4) DEFAULT '0.0000' COMMENT '换手率（%，精度提升）',
  `sell_volume` bigint(20) DEFAULT '0' COMMENT '主动卖出量',
  `buy_volume` bigint(20) DEFAULT '0' COMMENT '主动买入量',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据入库时间',
  PRIMARY KEY (`id`),
  KEY `idx_stock_code` (`stock_code`)
) ENGINE=InnoDB AUTO_INCREMENT=18386 DEFAULT CHARSET=utf8mb4 COMMENT='A股毫秒级实时K线数据表';

CREATE TABLE `subject` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fir_category_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '行业编码',
  `fir_category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '行业题材',
  `sec_category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '二级分类',
  `thr_category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '三级分类',
  `category_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '分类',
  `stock_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '股票代码',
  `stock_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '公司名称',
  `reason` text COLLATE utf8mb4_unicode_ci COMMENT '入选理由',
  `remarks` text COLLATE utf8mb4_unicode_ci COMMENT '备注信息',
  `sec_category_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `thr_category_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '写入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42970 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='行业主题分类表';

CREATE TABLE `subject_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `category_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `stock_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `stock_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reason` mediumtext COLLATE utf8mb4_unicode_ci,
  `remarks` mediumtext COLLATE utf8mb4_unicode_ci,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '写入时间',
  PRIMARY KEY (`id`),
  KEY `idx_subject_info_01` (`category_code`)
) ENGINE=InnoDB AUTO_INCREMENT=635009 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `subject_message` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '时间',
  `category_code` varchar(100) NOT NULL COMMENT '题材ID',
  `category_name` varchar(255) NOT NULL COMMENT '题材名称',
  `pct_chg` decimal(10,4) NOT NULL COMMENT '涨幅（百分比，带 4 位小数）',
  `description` text COMMENT '内容/描述',
  PRIMARY KEY (`id`),
  KEY `idx_subject_id` (`category_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1075 DEFAULT CHARSET=utf8mb4 COMMENT='题材消息表';

CREATE TABLE `subject_rel` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `category_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `par_category_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `par_category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category_type` int(10) unsigned DEFAULT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '写入时间',
  PRIMARY KEY (`id`),
  KEY `idx_subject_rel_01` (`category_code`),
  KEY `idx_subject_rel_02` (`par_category_code`)
) ENGINE=InnoDB AUTO_INCREMENT=14086 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `subject_stock` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `stock_code` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '股票代码',
  `stock_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '公司名称',
  `title` varchar(500) NOT NULL COMMENT '业务备注',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '写入时间',
  PRIMARY KEY (`id`),
  KEY `idx_name` (`stock_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5165 DEFAULT CHARSET=utf8mb4;