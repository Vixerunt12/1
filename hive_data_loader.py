"""
Hadoop/Hive数据集成模块
将CSV数据导入到Hive表中，实现大数据存储功能
"""

import os
import subprocess
import pandas as pd
from datetime import datetime

class HiveDataLoader:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shujv')
        self.hive_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hive', 'create_tables.hql')
        
    def check_hadoop_environment(self):
        """检查Hadoop环境是否可用"""
        try:
            # 检查Hadoop命令
            result = subprocess.run(['hadoop', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Hadoop环境可用")
                return True
            else:
                print("❌ Hadoop环境不可用")
                return False
        except FileNotFoundError:
            print("❌ Hadoop未安装或未配置环境变量")
            return False
    
    def check_hive_environment(self):
        """检查Hive环境是否可用"""
        try:
            # 检查Hive命令
            result = subprocess.run(['hive', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Hive环境可用")
                return True
            else:
                print("❌ Hive环境不可用")
                return False
        except FileNotFoundError:
            print("❌ Hive未安装或未配置环境变量")
            return False
    
    def create_hive_tables(self):
        """创建Hive表结构"""
        if not os.path.exists(self.hive_script_path):
            print(f"❌ Hive脚本文件不存在: {self.hive_script_path}")
            return False
            
        try:
            # 执行Hive脚本
            result = subprocess.run(['hive', '-f', self.hive_script_path], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Hive表创建成功")
                return True
            else:
                print(f"❌ Hive表创建失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 执行Hive脚本失败: {e}")
            return False
    
    def upload_to_hdfs(self):
        """上传数据到HDFS"""
        try:
            # 创建HDFS目录
            hdfs_path = "/user/fault_analysis/data"
            subprocess.run(['hadoop', 'fs', '-mkdir', '-p', hdfs_path], capture_output=True)
            
            # 上传数据文件
            for file_name in ['fault_data.csv', 'maintenance_data.csv', 'maintenance_records.csv']:
                local_path = os.path.join(self.data_dir, file_name)
                hdfs_file_path = f"{hdfs_path}/{file_name}"
                
                if os.path.exists(local_path):
                    result = subprocess.run(['hadoop', 'fs', '-put', '-f', local_path, hdfs_file_path], capture_output=True)
                    if result.returncode == 0:
                        print(f"✅ 上传 {file_name} 到HDFS成功")
                    else:
                        print(f"❌ 上传 {file_name} 到HDFS失败: {result.stderr}")
                else:
                    print(f"❌ 数据文件不存在: {local_path}")
            
            return True
        except Exception as e:
            print(f"❌ HDFS上传失败: {e}")
            return False
    
    def load_data_to_hive(self):
        """将HDFS数据加载到Hive表"""
        try:
            # 加载故障数据
            load_fault_sql = """
            LOAD DATA INPATH '/user/fault_analysis/data/fault_data.csv' 
            OVERWRITE INTO TABLE fault_analysis_db.fault_data;
            """
            
            # 加载保养数据
            load_maintenance_sql = """
            LOAD DATA INPATH '/user/fault_analysis/data/maintenance_data.csv' 
            OVERWRITE INTO TABLE fault_analysis_db.maintenance_data;
            """
            
            # 加载维修记录
            load_records_sql = """
            LOAD DATA INPATH '/user/fault_analysis/data/maintenance_records.csv' 
            OVERWRITE INTO TABLE fault_analysis_db.maintenance_records;
            """
            
            # 执行Hive SQL
            for sql, table_name in [(load_fault_sql, 'fault_data'), 
                                   (load_maintenance_sql, 'maintenance_data'),
                                   (load_records_sql, 'maintenance_records')]:
                result = subprocess.run(['hive', '-e', sql], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ 加载数据到 {table_name} 表成功")
                else:
                    print(f"❌ 加载数据到 {table_name} 表失败: {result.stderr}")
            
            return True
        except Exception as e:
            print(f"❌ Hive数据加载失败: {e}")
            return False
    
    def simulate_hadoop_environment(self):
        """模拟Hadoop/Hive环境（用于开发测试）"""
        print("🔧 模拟Hadoop/Hive环境（开发模式）")
        
        # 创建模拟的HDFS目录结构
        hdfs_sim_path = os.path.join(self.data_dir, 'hdfs_simulation')
        os.makedirs(hdfs_sim_path, exist_ok=True)
        
        # 复制数据文件到模拟HDFS目录
        for file_name in ['fault_data.csv', 'maintenance_data.csv', 'maintenance_records.csv']:
            local_path = os.path.join(self.data_dir, file_name)
            sim_path = os.path.join(hdfs_sim_path, file_name)
            
            if os.path.exists(local_path):
                import shutil
                shutil.copy2(local_path, sim_path)
                print(f"✅ 模拟HDFS: 复制 {file_name}")
        
        print("✅ Hadoop/Hive环境模拟完成（开发模式）")
        return True
    
    def initialize_bigdata_environment(self, use_simulation=True):
        """初始化大数据环境"""
        print("🚀 初始化大数据存储环境...")
        
        if use_simulation:
            # 使用模拟环境（开发模式）
            return self.simulate_hadoop_environment()
        else:
            # 使用真实Hadoop/Hive环境
            if not self.check_hadoop_environment():
                return False
            
            if not self.check_hive_environment():
                return False
            
            if not self.create_hive_tables():
                return False
            
            if not self.upload_to_hdfs():
                return False
            
            if not self.load_data_to_hive():
                return False
            
            print("✅ 大数据存储环境初始化完成")
            return True

# 使用示例
if __name__ == "__main__":
    loader = HiveDataLoader()
    
    # 初始化大数据环境（开发模式使用模拟环境）
    loader.initialize_bigdata_environment(use_simulation=True)