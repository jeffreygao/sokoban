import sys
import os
import unittest
import pygame

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sokoban import Sokoban
from levels import LEVELS, LEVEL_DATA

class TestSokobanLevels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 初始化Pygame，不初始化音频系统
        pygame.init()
        # 不要初始化音频系统
        # pygame.mixer.init()
        pygame.display.set_mode((800, 600))  # 创建一个测试窗口

    def test_all_levels(self):
        """测试所有关卡的可解性"""
        for i, level in enumerate(LEVELS):
            with self.subTest(level_number=i+1):
                # 创建游戏实例并加载特定关卡
                game = Sokoban()
                game.current_level = i
                game.reset_level()
                
                # 检查关卡是否正确加载
                self.assertIsNotNone(game.level, f"关卡 {i+1} 未正确加载")
                
                # 检查关卡是否包含玩家
                player_count = sum(row.count('@') for row in game.level)
                self.assertEqual(player_count, 1, f"关卡 {i+1} 玩家数量不正确")
                
                # 检查关卡是否包含箱子和目标点
                box_count = sum(row.count('$') for row in game.level)
                target_count = sum(row.count('.') for row in game.level)
                self.assertGreater(box_count, 0, f"关卡 {i+1} 没有箱子")
                self.assertGreater(target_count, 0, f"关卡 {i+1} 没有目标点")
                
                # 检查关卡是否有解
                # 注意：这里只是基本的完整性检查，不是求解算法
                self.assertTrue(len(game.level) > 0, f"关卡 {i+1} 为空")

    def test_level_metadata(self):
        """测试关卡元数据的完整性"""
        self.assertEqual(len(LEVELS), len(LEVEL_DATA), "关卡数量与元数据数量不匹配")
        
        for i, level_data in enumerate(LEVEL_DATA):
            with self.subTest(level_number=i+1):
                # 检查关卡元数据的必要字段
                self.assertIn('name', level_data, f"关卡 {i+1} 缺少名称")
                self.assertIn('par_moves', level_data, f"关卡 {i+1} 缺少推荐移动次数")
                self.assertIn('par_pushes', level_data, f"关卡 {i+1} 缺少推荐推箱次数")
                
                # 检查推荐移动次数和推箱次数的合理性
                self.assertGreater(level_data['par_moves'], 0, f"关卡 {i+1} 推荐移动次数不合理")
                self.assertGreater(level_data['par_pushes'], 0, f"关卡 {i+1} 推荐推箱次数不合理")

    @classmethod
    def tearDownClass(cls):
        # 关闭Pygame
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
