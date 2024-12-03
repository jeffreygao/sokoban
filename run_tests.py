import unittest
import sys
import os

# 确保可以导入测试模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入测试用例
from tests.test_levels import TestSokobanLevels

def run_tests():
    # 创建测试加载器
    loader = unittest.TestLoader()
    
    # 创建测试套件
    suite = loader.loadTestsFromTestCase(TestSokobanLevels)
    
    # 创建测试运行器
    runner = unittest.TextTestRunner(verbosity=2)
    
    # 运行测试
    result = runner.run(suite)
    
    # 返回测试是否成功
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
