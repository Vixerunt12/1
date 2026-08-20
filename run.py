#!/usr/bin/env python3
"""
汽车故障诊断与维修推荐系统 - 主启动脚本
"""

import os
import sys
import argparse
from utils.data_loader import DataLoader
from web.app import app
import config.config as config

def setup_environment():
    """设置环境变量"""
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # 设置Spark环境变量（如果需要在本地运行）
    os.environ['PYSPARK_PYTHON'] = sys.executable
    os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

def init_database():
    """初始化数据库和数据"""
    print("正在初始化数据库...")
    
    try:
        loader = DataLoader()
        loader.load_data_to_hive()
        loader.close()
        print("✅ 数据库初始化完成!")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        print("请确保Hadoop和Hive服务已启动")

def start_web_server():
    """启动Web服务器"""
    print(f"🚀 启动Web服务器: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    
    try:
        app.run(
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Web服务器启动失败: {e}")

def run_analysis():
    """运行数据分析"""
    print("🔍 运行数据分析...")
    
    try:
        from spark.fault_analysis import FaultAnalysis
        
        analyzer = FaultAnalysis()
        
        # 生成分析报告
        report = analyzer.generate_analysis_report()
        
        print("✅ 分析报告生成完成!")
        print(f"故障类型统计: {len(report['fault_category'])} 类")
        print(f"故障原因分析: {len(report['fault_reason'])} 条")
        print(f"成本趋势数据: {len(report['cost_trend'])} 个月")
        print(f"车型分析数据: {len(report['car_model_analysis'])} 款")
        
        analyzer.close()
        
    except Exception as e:
        print(f"❌ 数据分析失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='汽车故障诊断与维修推荐系统')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--analyze', action='store_true', help='运行数据分析')
    parser.add_argument('--web', action='store_true', help='启动Web服务器')
    parser.add_argument('--all', action='store_true', help='执行所有操作')
    
    args = parser.parse_args()
    
    # 设置环境
    setup_environment()
    
    if args.init or args.all:
        init_database()
    
    if args.analyze or args.all:
        run_analysis()
    
    if args.web or args.all:
        start_web_server()
    
    # 如果没有指定参数，显示帮助信息
    if not any([args.init, args.analyze, args.web, args.all]):
        print("""
🚗 汽车故障诊断与维修推荐系统

使用方法:
    python run.py --init       初始化数据库
    python run.py --analyze    运行数据分析
    python run.py --web        启动Web服务器
    python run.py --all        执行所有操作

示例:
    python run.py --init --analyze  初始化并分析数据
    python run.py --web             启动Web界面
        """)

if __name__ == "__main__":
    main()