#!/usr/bin/env python3
"""
汽车故障诊断系统 - 简化演示版本
使用Pandas进行数据分析，避免PySpark依赖
"""

import os
import pandas as pd
import json
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import numpy as np

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(project_root, 'web', 'templates')

app = Flask(__name__, template_folder=template_dir)

class DemoFaultAnalysis:
    def __init__(self):
        self.fault_df = None
        self.maintenance_df = None
        self.records_df = None
        self.load_data()
    
    def load_data(self):
        """加载CSV数据"""
        try:
            # 读取数据文件
            data_dir = os.path.join(os.path.dirname(__file__), 'shujv')
            
            self.fault_df = pd.read_csv(os.path.join(data_dir, 'fault_data.csv'))
            self.maintenance_df = pd.read_csv(os.path.join(data_dir, 'maintenance_data.csv'))
            self.records_df = pd.read_csv(os.path.join(data_dir, 'maintenance_records.csv'))
            
            # 转换时间格式
            self.fault_df['故障发生时间'] = pd.to_datetime(self.fault_df['故障发生时间'])
            self.maintenance_df['保养时间'] = pd.to_datetime(self.maintenance_df['保养时间'])
            self.records_df['维修时间'] = pd.to_datetime(self.records_df['维修时间'])
            
            print(f"✅ 数据加载完成: 故障{len(self.fault_df)}条, 保养{len(self.maintenance_df)}条, 维修{len(self.records_df)}条")
            
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            # 创建示例数据
            self.create_sample_data()
    
    def create_sample_data(self):
        """创建示例数据"""
        print("⚠️ 使用示例数据...")
        
        # 故障数据
        fault_data = {
            '故障ID': ['F001', 'F002', 'F003', 'F004', 'F005'],
            '故障代码': ['P0301', 'C0045', 'P0171', 'B1234', 'P0420'],
            '故障现象': ['1缸失火，发动机抖动', '右前轮速传感器故障', '燃油系统过稀', '空调压缩机不工作', '催化转化器效率低'],
            '车型': ['丰田卡罗拉', '大众朗逸', '本田思域', '比亚迪汉', '宝马3系'],
            '行驶里程(km)': [25092, 102969, 28656, 49077, 82589],
            '故障发生时间': pd.date_range('2024-01-01', periods=5, freq='M')
        }
        self.fault_df = pd.DataFrame(fault_data)
        
        # 维修记录
        records_data = {
            '维修ID': ['M001', 'M002', 'M003', 'M004', 'M005'],
            '故障ID': ['F001', 'F002', 'F003', 'F004', 'F005'],
            '维修项目': ['更换火花塞+缸线检查', '更换轮速传感器', '清洗节气门+燃油滤芯更换', '维修空调压缩机', '更换催化转化器'],
            '更换配件': ['铱金火花塞(4支)', '右前轮速传感器', '燃油滤芯', '压缩机电磁阀', '原厂催化转化器'],
            '维修费用(元)': [380, 260, 420, 580, 2800],
            '维修时间': pd.date_range('2024-01-01', periods=5, freq='M') + timedelta(hours=1)
        }
        self.records_df = pd.DataFrame(records_data)
    
    def fault_classification(self):
        """故障类型分类"""
        # 根据故障代码前缀分类
        fault_categories = {
            'P': '动力系统故障',
            'C': '底盘系统故障', 
            'B': '车身系统故障'
        }
        
        results = []
        for prefix, category in fault_categories.items():
            count = len(self.fault_df[self.fault_df['故障代码'].str.startswith(prefix)])
            avg_mileage = self.fault_df[self.fault_df['故障代码'].str.startswith(prefix)]['行驶里程(km)'].mean()
            
            results.append({
                'category_name': category,
                'fault_count': int(count),
                'avg_mileage': round(avg_mileage, 1) if not pd.isna(avg_mileage) else 0
            })
        
        return results
    
    def fault_reason_analysis(self):
        """故障原因分析"""
        # 合并故障和维修数据
        merged_df = pd.merge(self.fault_df, self.records_df, left_on='故障ID', right_on='故障ID')
        
        # 按故障代码分组分析
        analysis = merged_df.groupby('故障代码').agg({
            '故障ID': 'count',
            '维修费用(元)': ['mean', 'min', 'max'],
            '维修项目': lambda x: list(x.unique())
        }).reset_index()
        
        analysis.columns = ['fault_code', 'occurrence_count', 'avg_cost', 'min_cost', 'max_cost', 'common_solutions']
        
        return analysis.to_dict('records')
    
    def cost_trend_analysis(self):
        """维修成本趋势分析"""
        # 按月份分析
        self.records_df['year_month'] = self.records_df['维修时间'].dt.strftime('%Y-%m')
        
        trend = self.records_df.groupby('year_month').agg({
            '维修ID': 'count',
            '维修费用(元)': ['mean', 'sum']
        }).reset_index()
        
        trend.columns = ['year_month', 'maintenance_count', 'avg_cost', 'total_cost']
        
        return trend.to_dict('records')
    
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
        
        return analysis.to_dict('records')
    
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
                return result.to_dict('records')
        
        return []
    
    def generate_analysis_report(self):
        """生成分析报告"""
        return {
            'fault_category': self.fault_classification(),
            'fault_reason': self.fault_reason_analysis(),
            'cost_trend': self.cost_trend_analysis(),
            'car_model_analysis': self.car_model_analysis()
        }

# 创建分析器实例
analyzer = DemoFaultAnalysis()

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/api/fault/categories')
def get_fault_categories():
    """获取故障分类"""
    try:
        categories = analyzer.fault_classification()
        return jsonify({'success': True, 'data': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/fault/reasons')
def get_fault_reasons():
    """获取故障原因"""
    try:
        reasons = analyzer.fault_reason_analysis()
        return jsonify({'success': True, 'data': reasons})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cost/trend')
def get_cost_trend():
    """获取成本趋势"""
    try:
        trend = analyzer.cost_trend_analysis()
        return jsonify({'success': True, 'data': trend})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/car/models')
def get_car_models_analysis():
    """获取车型分析"""
    try:
        models = analyzer.car_model_analysis()
        return jsonify({'success': True, 'data': models})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/recommendation', methods=['POST'])
def get_maintenance_recommendation():
    """获取维修推荐"""
    try:
        data = request.get_json()
        car_model = data.get('car_model', '')
        mileage = data.get('mileage', 0)
        fault_phenomenon = data.get('fault_phenomenon', '')
        
        recommendations = analyzer.maintenance_recommendation(car_model, mileage, fault_phenomenon)
        return jsonify({'success': True, 'data': recommendations})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analysis/report')
def get_analysis_report():
    """获取完整报告"""
    try:
        report = analyzer.generate_analysis_report()
        return jsonify({'success': True, 'data': report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/dashboard')
def dashboard():
    """仪表板"""
    return render_template('dashboard.html')

@app.route('/fault-analysis')
def fault_analysis():
    """故障分析"""
    return render_template('fault_analysis.html')

@app.route('/maintenance-recommendation')
def maintenance_recommendation():
    """维修推荐"""
    return render_template('maintenance_recommendation.html')

@app.route('/cost-analysis')
def cost_analysis():
    """成本分析"""
    return render_template('cost_analysis.html')

if __name__ == '__main__':
    print("🚗 汽车故障诊断系统 - 演示版")
    print("📊 数据统计:")
    print(f"   故障记录: {len(analyzer.fault_df)} 条")
    print(f"   维修记录: {len(analyzer.records_df)} 条")
    print(f"   车型数量: {analyzer.fault_df['车型'].nunique()} 款")
    print("\n🌐 启动Web服务器: http://localhost:5000")
    
    app.run(host='localhost', port=5000, debug=True)