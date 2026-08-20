import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据文件路径
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
FAULT_DATA_PATH = os.path.join(DATA_DIR, 'fault_data.csv')
MAINTENANCE_DATA_PATH = os.path.join(DATA_DIR, 'maintenance_data.csv')
MAINTENANCE_RECORDS_PATH = os.path.join(DATA_DIR, 'maintenance_records.csv')

# Hadoop配置
HADOOP_HOME = '/usr/local/hadoop'
HDFS_DATA_DIR = '/user/fault_data'

# Hive配置
HIVE_DATABASE = 'fault_analysis_db'

# Spark配置
SPARK_APP_NAME = 'FaultAnalysis'
SPARK_MASTER = 'local[*]'

# Flask配置
FLASK_HOST = 'localhost'
FLASK_PORT = 5000
FLASK_DEBUG = True

# 故障分类配置
FAULT_CATEGORIES = {
    'P': '动力系统故障',
    'C': '底盘系统故障', 
    'B': '车身系统故障'
}

# 维修成本阈值
COST_THRESHOLDS = {
    'low': 500,
    'medium': 1000,
    'high': 2000
}