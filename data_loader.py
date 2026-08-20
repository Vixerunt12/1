import os
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import config.config as config

class DataLoader:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("DataLoader") \
            .master(config.SPARK_MASTER) \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
    
    def load_data_to_hive(self):
        """将CSV数据加载到Hive表中"""
        
        # 定义数据模式
        fault_schema = StructType([
            StructField("fault_id", StringType(), True),
            StructField("fault_code", StringType(), True),
            StructField("fault_phenomenon", StringType(), True),
            StructField("car_model", StringType(), True),
            StructField("mileage", IntegerType(), True),
            StructField("fault_time", StringType(), True)
        ])
        
        maintenance_schema = StructType([
            StructField("maintenance_id", StringType(), True),
            StructField("car_model", StringType(), True),
            StructField("mileage", IntegerType(), True),
            StructField("maintenance_item", StringType(), True),
            StructField("maintenance_time", StringType(), True),
            StructField("last_maintenance_mileage", IntegerType(), True)
        ])
        
        records_schema = StructType([
            StructField("maintenance_id", StringType(), True),
            StructField("fault_id", StringType(), True),
            StructField("maintenance_item", StringType(), True),
            StructField("replaced_parts", StringType(), True),
            StructField("maintenance_cost", DoubleType(), True),
            StructField("maintenance_time", StringType(), True)
        ])
        
        # 读取CSV文件
        fault_df = self.spark.read \
            .option("header", "true") \
            .schema(fault_schema) \
            .csv(config.FAULT_DATA_PATH)
        
        maintenance_df = self.spark.read \
            .option("header", "true") \
            .schema(maintenance_schema) \
            .csv(config.MAINTENANCE_DATA_PATH)
        
        records_df = self.spark.read \
            .option("header", "true") \
            .schema(records_schema) \
            .csv(config.MAINTENANCE_RECORDS_PATH)
        
        # 转换时间格式
        from pyspark.sql.functions import to_timestamp
        
        fault_df = fault_df.withColumn("fault_time", 
            to_timestamp("fault_time", "yyyy-MM-dd HH:mm"))
        
        maintenance_df = maintenance_df.withColumn("maintenance_time", 
            to_timestamp("maintenance_time", "yyyy-MM-dd HH:mm"))
        
        records_df = records_df.withColumn("maintenance_time", 
            to_timestamp("maintenance_time", "yyyy-MM-dd HH:mm"))
        
        # 保存到Hive表
        fault_df.write.mode("overwrite").saveAsTable("fault_analysis_db.fault_data")
        maintenance_df.write.mode("overwrite").saveAsTable("fault_analysis_db.maintenance_data")
        records_df.write.mode("overwrite").saveAsTable("fault_analysis_db.maintenance_records")
        
        print("数据加载完成!")
        print(f"故障数据记录数: {fault_df.count()}")
        print(f"保养数据记录数: {maintenance_df.count()}")
        print(f"维修记录数: {records_df.count()}")
    
    def create_sample_data(self):
        """创建示例数据用于测试"""
        
        # 故障数据示例
        fault_data = [
            ("F020", "P0302", "2缸失火，加速无力", "丰田卡罗拉", 32000, "2024-03-15 14:30"),
            ("F021", "C0046", "左前轮速传感器故障", "大众朗逸", 85000, "2024-04-20 10:15"),
            ("F022", "B1235", "空调制冷效果差", "比亚迪汉", 42000, "2024-05-10 16:45")
        ]
        
        fault_df = self.spark.createDataFrame(fault_data, [
            "fault_id", "fault_code", "fault_phenomenon", "car_model", "mileage", "fault_time"
        ])
        
        # 转换时间格式
        from pyspark.sql.functions import to_timestamp
        fault_df = fault_df.withColumn("fault_time", 
            to_timestamp("fault_time", "yyyy-MM-dd HH:mm"))
        
        # 追加到现有表
        fault_df.write.mode("append").saveAsTable("fault_analysis_db.fault_data")
        
        print("示例数据添加完成!")
    
    def close(self):
        """关闭Spark会话"""
        self.spark.stop()

# 使用示例
if __name__ == "__main__":
    loader = DataLoader()
    
    try:
        # 加载数据到Hive
        loader.load_data_to_hive()
        
        # 添加示例数据
        loader.create_sample_data()
        
    finally:
        loader.close()