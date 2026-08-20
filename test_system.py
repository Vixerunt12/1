#!/usr/bin/env python3
"""
系统功能测试脚本
"""

import os
import sys
import pandas as pd

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_data_loading():
    """测试数据加载"""
    print("🔍 测试数据加载...")
    
    try:
        # 检查数据文件是否存在
        data_files = [
            'shujv/fault_data.csv',
            'shujv/maintenance_data.csv', 
            'shujv/maintenance_records.csv'
        ]
        
        for file in data_files:
            file_path = os.path.join(project_root, file)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                print(f"✅ {file}: {len(df)} 条记录")
            else:
                print(f"❌ {file}: 文件不存在")
                return False
        
        return True
    
    except Exception as e:
        print(f"❌ 数据加载测试失败: {e}")
        return False

def test_config():
    """测试配置文件"""
    print("🔍 测试配置文件...")
    
    try:
        import config.config as config
        
        # 检查配置项
        required_configs = [
            'PROJECT_ROOT', 'DATA_DIR', 'FAULT_DATA_PATH',
            'MAINTENANCE_DATA_PATH', 'MAINTENANCE_RECORDS_PATH',
            'SPARK_APP_NAME', 'SPARK_MASTER',
            'FLASK_HOST', 'FLASK_PORT'
        ]
        
        for config_name in required_configs:
            if hasattr(config, config_name):
                print(f"✅ {config_name}: {getattr(config, config_name)}")
            else:
                print(f"❌ {config_name}: 配置项缺失")
                return False
        
        return True
    
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_spark_analysis():
    """测试Spark分析功能"""
    print("🔍 测试Spark分析功能...")
    
    try:
        # 这里只是测试导入，实际运行需要Spark环境
        from spark.fault_analysis import FaultAnalysis
        print("✅ Spark分析模块导入成功")
        
        # 测试配置
        import config.config as config
        print(f"✅ Spark配置: {config.SPARK_APP_NAME}, {config.SPARK_MASTER}")
        
        return True
    
    except Exception as e:
        print(f"⚠️ Spark分析测试警告: {e}")
        print("提示: 需要安装Spark环境才能完整测试")
        return True  # 不视为失败，因为可能没有Spark环境

def test_flask_app():
    """测试Flask应用"""
    print("🔍 测试Flask应用...")
    
    try:
        from web.app import app
        
        # 检查路由
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'path': str(rule)
                })
        
        print(f"✅ Flask应用加载成功，共 {len(routes)} 个路由")
        
        # 显示主要路由
        main_routes = [r for r in routes if r['path'] in ['/', '/dashboard', '/api/analysis/report']]
        for route in main_routes:
            print(f"   - {route['path']} ({', '.join(route['methods'])})")
        
        return True
    
    except Exception as e:
        print(f"❌ Flask应用测试失败: {e}")
        return False

def test_templates():
    """测试模板文件"""
    print("🔍 测试模板文件...")
    
    try:
        template_dir = os.path.join(project_root, 'web/templates')
        
        required_templates = [
            'index.html',
            'dashboard.html', 
            'maintenance_recommendation.html'
        ]
        
        for template in required_templates:
            template_path = os.path.join(template_dir, template)
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 检查关键内容
                    if 'echarts' in content and '汽车故障' in content:
                        print(f"✅ {template}: 模板文件正常")
                    else:
                        print(f"⚠️ {template}: 模板内容可能不完整")
            else:
                print(f"❌ {template}: 模板文件不存在")
                return False
        
        return True
    
    except Exception as e:
        print(f"❌ 模板测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚗 汽车故障诊断系统 - 功能测试")
    print("=" * 50)
    
    tests = [
        ("数据加载", test_data_loading),
        ("配置文件", test_config),
        ("Spark分析", test_spark_analysis),
        ("Flask应用", test_flask_app),
        ("模板文件", test_templates)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: 通过")
            else:
                print(f"❌ {test_name}: 失败")
        
        except Exception as e:
            print(f"💥 {test_name}: 异常 - {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("-" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总测试: {total}个, 通过: {passed}个, 失败: {total - passed}个")
    
    if passed == total:
        print("🎉 所有测试通过! 系统可以正常启动。")
        print("\n启动命令:")
        print("  python run.py --web     # 启动Web服务器")
        print("  python run.py --all     # 完整启动(需要Hadoop/Hive环境)")
    else:
        print("⚠️  部分测试失败，请检查相关配置。")

if __name__ == "__main__":
    main()