"""
纯Python版本的故障分析模块
完全绕过PySpark依赖，使用Pandas进行数据分析
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

class FaultAnalysisPure:
    def __init__(self):
        self.fault_df = None
        self.maintenance_df = None
        self.records_df = None
        self.load_data()
        print("✅ 纯Python故障分析器初始化完成")
    
    def load_data(self):
        """加载CSV数据"""
        try:
            # 读取数据文件
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shujv')
            
            self.fault_df = pd.read_csv(os.path.join(data_dir, 'fault_data.csv'))
            self.maintenance_df = pd.read_csv(os.path.join(data_dir, 'maintenance_data.csv'))
            self.records_df = pd.read_csv(os.path.join(data_dir, 'maintenance_records.csv'))
            
            # 转换时间格式
            self.fault_df['故障发生时间'] = pd.to_datetime(self.fault_df['故障发生时间'])
            self.maintenance_df['保养时间'] = pd.to_datetime(self.maintenance_df['保养时间'])
            self.records_df['维修时间'] = pd.to_datetime(self.records_df['维修时间'])
            
            print(f"✅ 数据加载完成: 故障{len(self.fault_df)}条, 维修{len(self.records_df)}条")
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            # 创建示例数据
            self.create_sample_data()
    
    def create_sample_data(self):
        """创建示例数据"""
        print("⚠️ 使用示例数据...")
        
        # 故障数据
        fault_data = {
            '故障ID': ['F001', 'F002', 'F003', 'F004', 'F005', 'F006', 'F007', 'F008', 'F009', 'F010'],
            '故障代码': ['P0301', 'C0045', 'P0171', 'B1234', 'P0420', 'P0299', 'C0121', 'B0081', 'P0521', 'C0561'],
            '故障现象': ['1缸失火，发动机抖动', '右前轮速传感器故障', '燃油系统过稀', '空调压缩机不工作', 
                       '催化转化器效率低', '涡轮增压器压力不足', '刹车压力传感器信号异常', 
                       '主驾驶安全带传感器故障', '机油压力传感器电路范围故障', 'ABS系统控制模块故障'],
            '车型': ['丰田卡罗拉', '大众朗逸', '本田思域', '比亚迪汉', '宝马3系', '福特蒙迪欧', 
                    '吉利星越L', '奥迪A4L', '长城哈弗H6', '奔驰C级'],
            '行驶里程(km)': [25092, 102969, 28656, 49077, 82589, 32976, 76273, 145233, 44409, 87221],
            '故障发生时间': pd.date_range('2024-01-01', periods=10, freq='D')
        }
        self.fault_df = pd.DataFrame(fault_data)
        
        # 维修记录
        records_data = {
            '维修ID': ['M001', 'M002', 'M003', 'M004', 'M005', 'M006', 'M007', 'M008', 'M009', 'M010'],
            '故障ID': ['F001', 'F002', 'F003', 'F004', 'F005', 'F006', 'F007', 'F008', 'F009', 'F010'],
            '维修项目': ['更换火花塞+缸线检查', '更换轮速传感器', '清洗节气门+燃油滤芯更换', '维修空调压缩机', 
                       '更换催化转化器', '更换涡轮增压器电磁阀', '更换刹车压力传感器', '更换安全带传感器',
                       '更换机油压力传感器', '维修ABS控制模块'],
            '更换配件': ['铱金火花塞(4支)', '右前轮速传感器', '燃油滤芯', '压缩机电磁阀', '原厂催化转化器',
                       '涡轮电磁阀', '刹车压力传感器', '主驾驶安全带传感器', '机油压力传感器', 'ABS控制模块维修包'],
            '维修费用(元)': [380, 260, 420, 580, 2800, 850, 480, 320, 450, 1200],
            '维修时间': pd.date_range('2024-01-01', periods=10, freq='D') + timedelta(hours=1)
        }
        self.records_df = pd.DataFrame(records_data)
    
    def fault_classification(self):
        """故障类型分类分析"""
        # 根据故障代码前缀分类
        fault_categories = {
            'P': '动力系统故障',
            'C': '底盘系统故障', 
            'B': '车身系统故障'
        }
        
        results = []
        for prefix, category in fault_categories.items():
            mask = self.fault_df['故障代码'].str.startswith(prefix)
            count = mask.sum()
            avg_mileage = self.fault_df.loc[mask, '行驶里程(km)'].mean()
            std_mileage = self.fault_df.loc[mask, '行驶里程(km)'].std()
            
            results.append({
                'category_name': category,
                'fault_count': int(count),
                'avg_mileage': round(avg_mileage, 1) if not pd.isna(avg_mileage) else 0,
                'std_mileage': round(std_mileage, 1) if not pd.isna(std_mileage) else 0
            })
        
        return pd.DataFrame(results)
    
    def fault_reason_analysis(self):
        """故障原因分析"""
        # 合并故障和维修数据
        merged_df = pd.merge(self.fault_df, self.records_df, left_on='故障ID', right_on='故障ID')
        
        # 故障分类
        def get_fault_category(code):
            prefix = code[0] if code else ''
            categories = {'P': '动力系统故障', 'C': '底盘系统故障', 'B': '车身系统故障'}
            return categories.get(prefix, '其他故障')
        
        merged_df['category_name'] = merged_df['故障代码'].apply(get_fault_category)
        
        # 按故障代码分组分析
        analysis = merged_df.groupby(['category_name', '故障代码']).agg({
            '故障ID': 'count',
            '维修费用(元)': ['mean', 'min', 'max'],
            '维修项目': lambda x: list(x.unique())
        }).reset_index()
        
        # 重命名列
        analysis.columns = ['category_name', 'fault_code', 'occurrence_count', 'avg_cost', 'min_cost', 'max_cost', 'common_solutions']
        
        return analysis.sort_values('occurrence_count', ascending=False)
    
    def cost_trend_analysis(self):
        """维修成本趋势分析"""
        # 按月份分析
        self.records_df['year_month'] = self.records_df['维修时间'].dt.strftime('%Y-%m')
        
        trend = self.records_df.groupby('year_month').agg({
            '维修ID': 'count',
            '维修费用(元)': ['mean', 'sum']
        }).reset_index()
        
        trend.columns = ['year_month', 'maintenance_count', 'avg_cost', 'total_cost']
        
        return trend.sort_values('year_month')
    
    def car_model_analysis(self):
        """车型故障分析"""
        # 合并数据
        merged_df = pd.merge(self.fault_df, self.records_df, left_on='故障ID', right_on='故障ID')
        
        analysis = merged_df.groupby('车型').agg({
            '故障ID': 'count',
            '维修费用(元)': 'mean',
            '行驶里程(km)': 'mean',
            '故障代码': lambda x: list(x.unique())
        }).reset_index()
        
        analysis.columns = ['car_model', 'fault_count', 'avg_cost', 'avg_mileage', 'common_faults']
        
        return analysis.sort_values('fault_count', ascending=False)
    
    def maintenance_recommendation(self, car_model, mileage, fault_phenomenon):
        """维修方案推荐"""
        # 查找相似故障
        similar_faults = self.fault_df[
            (self.fault_df['车型'] == car_model) &
            (abs(self.fault_df['行驶里程(km)'] - mileage) < 10000) &
            (self.fault_df['故障现象'].str.contains(fault_phenomenon, na=False))
        ]
        
        if len(similar_faults) == 0:
            # 放宽条件
            similar_faults = self.fault_df[
                self.fault_df['故障现象'].str.contains(fault_phenomenon, na=False)
            ]
        
        if len(similar_faults) > 0:
            # 获取维修方案
            fault_ids = similar_faults['故障ID'].tolist()
            recommendations = self.records_df[self.records_df['故障ID'].isin(fault_ids)]
            
            if len(recommendations) > 0:
                result = recommendations.groupby(['维修项目', '更换配件']).agg({
                    '维修ID': 'count',
                    '维修费用(元)': 'mean',
                    '维修时间': 'mean'
                }).reset_index()
                
                result.columns = ['maintenance_item', 'replaced_parts', 'solution_count', 'avg_cost', 'avg_time']
                return result.sort_values('solution_count', ascending=False).head(5)
        
        # 返回默认推荐
        default_recommendations = [
            {
                'maintenance_item': '专业诊断检查',
                'replaced_parts': '诊断设备',
                'solution_count': 0,
                'avg_cost': 100,
                'avg_time': 0.5
            }
        ]
        return pd.DataFrame(default_recommendations)
    
    def generate_analysis_report(self):
        """生成分析报告"""
        return {
            'fault_category': self.fault_classification().to_dict('records'),
            'fault_reason': self.fault_reason_analysis().to_dict('records'),
            'cost_trend': self.cost_trend_analysis().to_dict('records'),
            'car_model_analysis': self.car_model_analysis().to_dict('records')
        }
    
    def close(self):
        """清理资源"""
        print("✅ 纯Python分析器已关闭")

# 使用示例
if __name__ == "__main__":
    analyzer = FaultAnalysisPure()
    
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
        print(recommendation)
        
    finally:
        analyzer.close()