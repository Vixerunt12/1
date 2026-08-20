"""
Python 3.13兼容性补丁
解决typing.io模块缺失问题
"""

import sys
import importlib

# 检查是否在Python 3.13中运行
if sys.version_info >= (3, 13):
    # 创建模拟的typing.io模块
    class MockIO:
        """模拟typing.io模块"""
        pass
    
    # 将模拟模块添加到sys.modules
    sys.modules['typing.io'] = MockIO()
    
    print("✅ 已应用Python 3.13兼容性补丁")

# 应用补丁的函数
def apply_patch():
    """应用兼容性补丁"""
    if sys.version_info >= (3, 13):
        # 确保typing.io模块存在
        if 'typing.io' not in sys.modules:
            sys.modules['typing.io'] = type('MockIO', (), {})()
        
        # 修复可能的导入问题
        try:
            import typing
            # 确保typing模块没有被覆盖
            if hasattr(typing, 'io'):
                print("✅ typing.io模块已存在")
            else:
                # 添加io属性到typing模块
                typing.io = sys.modules['typing.io']
                print("✅ 已修复typing.io模块引用")
        except ImportError:
            print("⚠️ 无法导入typing模块")

# 自动应用补丁
apply_patch()