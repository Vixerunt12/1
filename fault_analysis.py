from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.ml.recommendation import ALS
import config.config as config

class FaultAnalysis:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName(config.SPARK_APP_NAME) \
            .master(config.SPARK_MASTER) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        # 加载数据
        self.load_data()
    
    def load_data(self):
        """加载Hive表中的数据"""
        self.fault_df = self.spark.table("fault_analysis_db.fault_data")
        self.maintenance_df = self.spark.table("fault_analysis_db.maintenance_data")
        self.records_df = self.spark.table("fault_analysis_db.maintenance_records")
        self.category_df = self.spark.table("fault_analysis_db.fault_category_dim")
    
    def fault_classification(self):
        """故障类型分类分析"""
        # 根据故障代码前缀分类
        fault_with_category = self.fault_df.alias('f') \
            .join(self.category_df.alias('c'), 
                  substring(col('f.fault_code'), 1, 1) == col('c.fault_code_prefix'))
        
        # 统计各类故障数量
        category_stats = fault_with_category.groupBy('category_name') \
            .agg(
                count('*').alias('fault_count'),
                avg('mileage').alias('avg_mileage'),
                stddev('mileage').alias('std_mileage')
            ) \
            .orderBy(desc('fault_count'))
        
        return category_stats
    
    def fault_reason_analysis(self):
        """故障原因分析"""
        # 关联故障数据和维修记录
        fault_reason = self.fault_df.alias('f') \
            .join(self.records_df.alias('r'), 'fault_id') \
            .join(self.category_df.alias('c'), 
                  substring(col('f.fault_code'), 1, 1) == col('c.fault_code_prefix'))
        
        # 分析故障原因与维修成本的关系
        reason_analysis = fault_reason.groupBy('category_name', 'fault_code') \
            .agg(
                count('*').alias('occurrence_count'),
                avg('maintenance_cost').alias('avg_cost'),
                min('maintenance_cost').alias('min_cost'),
                max('maintenance_cost').alias('max_cost'),
                collect_list('maintenance_item').alias('common_solutions')
            ) \
            .orderBy(desc('occurrence_count'))
        
        return reason_analysis
    
    def maintenance_recommendation(self, car_model, mileage, fault_phenomenon):
        """维修方案推荐"""
        # 基于相似故障的维修方案推荐
        similar_faults = self.fault_df.filter(
            (col('car_model') == car_model) &
            (abs(col('mileage') - mileage) < 10000) &
            (col('fault_phenomenon').contains(fault_phenomenon))
        )
        
        if similar_faults.count() == 0:
            # 如果没有完全匹配，放宽条件
            similar_faults = self.fault_df.filter(
                (col('fault_phenomenon').contains(fault_phenomenon))
            )
        
        # 获取相似故障的维修方案
        recommendations = similar_faults.alias('f') \
            .join(self.records_df.alias('r'), 'fault_id') \
            .groupBy('maintenance_item', 'replaced_parts') \
            .agg(
                count('*').alias('solution_count'),
                avg('maintenance_cost').alias('avg_cost'),
                avg('maintenance_time').alias('avg_time')
            ) \
            .orderBy(desc('solution_count'))
        
        return recommendations.limit(5)
    
    def cost_trend_analysis(self):
        """维修成本趋势分析"""
        # 按月份分析维修成本趋势
        cost_trend = self.records_df \
            .withColumn('year_month', date_format('maintenance_time', 'yyyy-MM')) \
            .groupBy('year_month') \
            .agg(
                count('*').alias('maintenance_count'),
                avg('maintenance_cost').alias('avg_cost'),
                sum('maintenance_cost').alias('total_cost')
            ) \
            .orderBy('year_month')
        
        return cost_trend
    
    def car_model_analysis(self):
        """车型故障分析"""
        # 分析各车型的故障分布
        model_analysis = self.fault_df.alias('f') \
            .join(self.records_df.alias('r'), 'fault_id') \
            .groupBy('car_model') \
            .agg(
                count('*').alias('fault_count'),
                avg('maintenance_cost').alias('avg_cost'),
                avg('mileage').alias('avg_mileage'),
                collect_set('fault_code').alias('common_faults')
            ) \
            .orderBy(desc('fault_count'))
        
        return model_analysis
    
    def generate_analysis_report(self):
        """生成分析报告"""
        report = {}
        
        # 故障分类统计
        report['fault_category'] = self.fault_classification().toPandas().to_dict('records')
        
        # 故障原因分析
        report['fault_reason'] = self.fault_reason_analysis().toPandas().to_dict('records')
        
        # 成本趋势分析
        report['cost_trend'] = self.cost_trend_analysis().toPandas().to_dict('records')
        
        # 车型分析
        report['car_model_analysis'] = self.car_model_analysis().toPandas().to_dict('records')
        
        return report
    
    def close(self):
        """关闭Spark会话"""
        self.spark.stop()

# 使用示例
if __name__ == "__main__":
    analyzer = FaultAnalysis()
    
    try:
        # 生成分析报告
        report = analyzer.generate_analysis_report()
        print("故障分析报告生成完成")
        
        # 示例：维修方案推荐
        recommendation = analyzer.maintenance_recommendation(
            car_model="丰田卡罗拉", 
            mileage=25000, 
            fault_phenomenon="发动机抖动"
        )
        print("维修方案推荐:")
        recommendation.show()
        
    finally:
        analyzer.close()