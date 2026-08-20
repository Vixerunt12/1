-- 创建故障分析数据库
CREATE DATABASE IF NOT EXISTS fault_analysis_db;
USE fault_analysis_db;

-- 故障数据表
CREATE TABLE IF NOT EXISTS fault_data (
    fault_id STRING COMMENT '故障ID',
    fault_code STRING COMMENT '故障代码',
    fault_phenomenon STRING COMMENT '故障现象',
    car_model STRING COMMENT '车型',
    mileage INT COMMENT '行驶里程(km)',
    fault_time TIMESTAMP COMMENT '故障发生时间'
)
COMMENT '故障数据表'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

-- 保养数据表
CREATE TABLE IF NOT EXISTS maintenance_data (
    maintenance_id STRING COMMENT '保养ID',
    car_model STRING COMMENT '车型',
    mileage INT COMMENT '行驶里程(km)',
    maintenance_item STRING COMMENT '保养项目',
    maintenance_time TIMESTAMP COMMENT '保养时间',
    last_maintenance_mileage INT COMMENT '上次保养里程(km)'
)
COMMENT '保养数据表'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

-- 维修记录表
CREATE TABLE IF NOT EXISTS maintenance_records (
    maintenance_id STRING COMMENT '维修ID',
    fault_id STRING COMMENT '故障ID',
    maintenance_item STRING COMMENT '维修项目',
    replaced_parts STRING COMMENT '更换配件',
    maintenance_cost DECIMAL(10,2) COMMENT '维修费用(元)',
    maintenance_time TIMESTAMP COMMENT '维修时间'
)
COMMENT '维修记录表'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

-- 故障类型维度表
CREATE TABLE IF NOT EXISTS fault_category_dim (
    fault_code_prefix STRING COMMENT '故障代码前缀',
    category_name STRING COMMENT '故障类别名称',
    description STRING COMMENT '类别描述'
)
COMMENT '故障类型维度表'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

-- 插入故障类型数据
INSERT INTO fault_category_dim VALUES
('P', '动力系统故障', '发动机、变速箱等动力相关故障'),
('C', '底盘系统故障', '制动、悬挂、转向等底盘相关故障'),
('B', '车身系统故障', '安全气囊、空调、电子设备等车身相关故障');