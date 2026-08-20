# 汽车故障诊断与维修推荐系统

基于Hadoop、Hive、Spark的智能故障诊断系统，通过大数据分析实现故障分类、原因分析和维修方案推荐。

## 系统架构

- **数据层**: Hadoop HDFS存储海量故障数据
- **数据仓库**: Hive进行数据整合与预处理
- **分析层**: Spark实现故障分类、原因分析、维修方案关联
- **应用层**: Flask Web框架 + Echarts可视化

## 数据文件说明

- `fault_data.csv`: 故障数据（故障ID、故障代码、故障现象、车型、行驶里程、故障时间）
- `maintenance_data.csv`: 保养数据（保养ID、车型、行驶里程、保养项目、保养时间）
- `maintenance_records.csv`: 维修记录（维修ID、故障ID、维修项目、更换配件、维修费用、维修时间）

## 项目结构

```
├── data/                    # 数据文件
├── hadoop/                  # Hadoop配置和脚本
├── hive/                    # Hive表定义和查询
├── spark/                   # Spark分析程序
├── web/                     # Flask Web应用
├── utils/                   # 工具函数
└── config/                  # 配置文件
```