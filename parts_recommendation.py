"""
智能配件推荐模块
基于维修方案推荐适配的汽车配件
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any

class PartsRecommendation:
    def __init__(self, fault_df=None, records_df=None):
        self.fault_df = fault_df
        self.records_df = records_df
        
        # 配件知识库
        self.parts_knowledge_base = self._initialize_parts_knowledge()
        
    def _initialize_parts_knowledge(self):
        """初始化配件知识库"""
        return {
            # 发动机系统配件
            'P0301': ['火花塞', '点火线圈', '高压线'],
            'P0171': ['空气流量传感器', '氧传感器', '燃油滤清器'],
            'P0420': ['三元催化器', '氧传感器', '排气系统密封垫'],
            'P0299': ['涡轮增压器', '进气系统', '中冷器'],
            
            # 底盘系统配件
            'C0045': ['轮速传感器', 'ABS传感器', '轮毂轴承'],
            'C0121': ['刹车压力传感器', '刹车总泵', '刹车分泵'],
            'C0561': ['ABS控制模块', '轮速传感器线束', '刹车系统'],
            
            # 车身系统配件
            'B1234': ['空调压缩机', '空调电磁阀', '制冷剂'],
            'B0081': ['安全带传感器', '安全带总成', '安全气囊模块'],
            'B0100': ['安全气囊控制模块', '碰撞传感器', '安全气囊'],
            'B0200': ['安全气囊传感器', '线束连接器', '控制单元'],
            
            # 通用配件
            '通用': ['机油滤清器', '空气滤清器', '空调滤清器', '刹车片', '刹车盘']
        }
    
    def recommend_parts_by_fault_code(self, fault_code: str, car_model: str = None) -> List[Dict]:
        """基于故障代码推荐配件"""
        recommendations = []
        
        # 根据故障代码获取推荐配件
        fault_prefix = fault_code[0] if fault_code else ''
        
        # 精确匹配故障代码
        if fault_code in self.parts_knowledge_base:
            parts_list = self.parts_knowledge_base[fault_code]
            for part in parts_list:
                recommendations.append({
                    'part_name': part,
                    'fault_code': fault_code,
                    'match_type': '精确匹配',
                    'confidence': 0.9,
                    'estimated_cost': self._estimate_part_cost(part, car_model)
                })
        
        # 前缀匹配（系统级别）
        if fault_prefix in ['P', 'C', 'B']:
            system_parts = []
            for code, parts in self.parts_knowledge_base.items():
                if code.startswith(fault_prefix) and code != '通用':
                    system_parts.extend(parts)
            
            # 去重
            system_parts = list(set(system_parts))
            
            for part in system_parts[:3]:  # 取前3个
                if part not in [r['part_name'] for r in recommendations]:
                    recommendations.append({
                        'part_name': part,
                        'fault_code': fault_code,
                        'match_type': '系统匹配',
                        'confidence': 0.7,
                        'estimated_cost': self._estimate_part_cost(part, car_model)
                    })
        
        # 通用配件推荐
        for part in self.parts_knowledge_base['通用'][:2]:
            if part not in [r['part_name'] for r in recommendations]:
                recommendations.append({
                    'part_name': part,
                    'fault_code': fault_code,
                    'match_type': '通用推荐',
                    'confidence': 0.5,
                    'estimated_cost': self._estimate_part_cost(part, car_model)
                })
        
        # 按置信度排序
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations[:5]  # 返回前5个推荐
    
    def recommend_parts_by_maintenance_item(self, maintenance_item: str, car_model: str = None) -> List[Dict]:
        """基于维修项目推荐配件"""
        # 维修项目与配件的映射关系
        maintenance_to_parts = {
            '更换火花塞': ['火花塞', '点火线圈'],
            '更换轮速传感器': ['轮速传感器', 'ABS传感器'],
            '清洗节气门': ['节气门清洗剂', '进气系统密封垫'],
            '维修空调压缩机': ['空调压缩机', '制冷剂', '密封圈'],
            '更换催化转化器': ['三元催化器', '氧传感器'],
            '更换涡轮增压器电磁阀': ['涡轮电磁阀', '进气管道'],
            '更换刹车压力传感器': ['刹车压力传感器', '刹车油'],
            '更换安全带传感器': ['安全带传感器', '线束连接器'],
            '更换机油压力传感器': ['机油压力传感器', '机油'],
            '维修ABS控制模块': ['ABS控制模块', '轮速传感器'],
            '更换凸轮轴位置传感器': ['凸轮轴传感器', '正时皮带'],
            '维修安全气囊控制模块': ['安全气囊模块', '碰撞传感器']
        }
        
        recommendations = []
        
        # 精确匹配维修项目
        for item, parts in maintenance_to_parts.items():
            if item in maintenance_item:
                for part in parts:
                    recommendations.append({
                        'part_name': part,
                        'maintenance_item': maintenance_item,
                        'match_type': '维修项目匹配',
                        'confidence': 0.8,
                        'estimated_cost': self._estimate_part_cost(part, car_model)
                    })
        
        # 关键词匹配
        keywords = {
            '火花塞': ['火花塞', '点火系统'],
            '传感器': ['相应传感器', '线束'],
            '压缩机': ['压缩机', '制冷剂'],
            '刹车': ['刹车片', '刹车盘', '刹车油'],
            '机油': ['机油', '机油滤清器'],
            '滤清器': ['空气滤清器', '空调滤清器']
        }
        
        for keyword, parts in keywords.items():
            if keyword in maintenance_item:
                for part in parts:
                    if part not in [r['part_name'] for r in recommendations]:
                        recommendations.append({
                            'part_name': part,
                            'maintenance_item': maintenance_item,
                            'match_type': '关键词匹配',
                            'confidence': 0.6,
                            'estimated_cost': self._estimate_part_cost(part, car_model)
                        })
        
        # 按置信度排序
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations[:5]
    
    def _estimate_part_cost(self, part_name: str, car_model: str = None) -> float:
        """估算配件成本"""
        # 配件成本基准（元）
        cost_base = {
            '火花塞': 80, '点火线圈': 200, '高压线': 150,
            '空气流量传感器': 300, '氧传感器': 250, '燃油滤清器': 100,
            '三元催化器': 1500, '排气系统密封垫': 50,
            '涡轮增压器': 3000, '进气系统': 800, '中冷器': 600,
            '轮速传感器': 200, 'ABS传感器': 250, '轮毂轴承': 300,
            '刹车压力传感器': 180, '刹车总泵': 400, '刹车分泵': 250,
            'ABS控制模块': 800, '轮速传感器线束': 100,
            '空调压缩机': 800, '空调电磁阀': 150, '制冷剂': 200,
            '安全带传感器': 120, '安全带总成': 300, '安全气囊模块': 600,
            '安全气囊控制模块': 700, '碰撞传感器': 200, '安全气囊': 500,
            '安全气囊传感器': 180, '线束连接器': 50, '控制单元': 400,
            '机油滤清器': 50, '空气滤清器': 80, '空调滤清器': 100,
            '刹车片': 200, '刹车盘': 300, '节气门清洗剂': 30,
            '进气系统密封垫': 40, '密封圈': 20, '进气管道': 150,
            '刹车油': 80, '机油': 200, '正时皮带': 400
        }
        
        base_cost = cost_base.get(part_name, 100)
        
        # 根据车型调整成本（豪华品牌成本更高）
        if car_model:
            luxury_brands = ['宝马', '奔驰', '奥迪', '保时捷', '路虎']
            if any(brand in car_model for brand in luxury_brands):
                base_cost *= 1.5
            elif '大众' in car_model or '丰田' in car_model or '本田' in car_model:
                base_cost *= 1.0  # 标准价格
            else:
                base_cost *= 0.8  # 国产品牌价格较低
        
        return round(base_cost, 2)
    
    def get_comprehensive_parts_recommendation(self, fault_code: str, maintenance_item: str, 
                                              car_model: str = None) -> Dict:
        """获取综合配件推荐"""
        # 基于故障代码的推荐
        fault_based = self.recommend_parts_by_fault_code(fault_code, car_model)
        
        # 基于维修项目的推荐
        maintenance_based = self.recommend_parts_by_maintenance_item(maintenance_item, car_model)
        
        # 合并推荐结果
        all_recommendations = fault_based + maintenance_based
        
        # 去重并重新排序
        unique_recommendations = []
        seen_parts = set()
        
        for rec in all_recommendations:
            if rec['part_name'] not in seen_parts:
                seen_parts.add(rec['part_name'])
                unique_recommendations.append(rec)
        
        # 按置信度排序
        unique_recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'recommended_parts': unique_recommendations[:8],  # 返回前8个推荐
            'total_recommendations': len(unique_recommendations),
            'recommendation_confidence': self._calculate_overall_confidence(unique_recommendations)
        }
    
    def _calculate_overall_confidence(self, recommendations: List[Dict]) -> float:
        """计算总体推荐置信度"""
        if not recommendations:
            return 0.0
        
        # 取前3个推荐的置信度平均值
        top_confidence = [rec['confidence'] for rec in recommendations[:3]]
        return round(sum(top_confidence) / len(top_confidence), 2)

# 使用示例
if __name__ == "__main__":
    # 创建配件推荐器
    recommender = PartsRecommendation()
    
    # 示例：基于故障代码推荐配件
    fault_code = "P0301"
    recommendations = recommender.recommend_parts_by_fault_code(fault_code, "丰田卡罗拉")
    
    print(f"故障代码 {fault_code} 的配件推荐:")
    for rec in recommendations:
        print(f"  - {rec['part_name']} (置信度: {rec['confidence']}, 预估成本: {rec['estimated_cost']}元)")
    
    # 示例：综合推荐
    comprehensive = recommender.get_comprehensive_parts_recommendation(
        "P0301", "更换火花塞和点火线圈", "丰田卡罗拉"
    )
    
    print(f"\n综合配件推荐 (总体置信度: {comprehensive['recommendation_confidence']}):")
    for rec in comprehensive['recommended_parts']:
        print(f"  - {rec['part_name']} ({rec['match_type']}, 置信度: {rec['confidence']})")