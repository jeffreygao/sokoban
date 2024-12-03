# 这是一个空的 __init__.py 文件，用于将 levels 目录标记为 Python 包

import os
import json

# 关卡文件目录
LEVELS_DIR = os.path.join(os.path.dirname(__file__))

def load_levels():
    """从levels目录加载所有关卡"""
    levels = []
    level_data = []
    level_files = sorted([f for f in os.listdir(LEVELS_DIR) if f.endswith('.json') and f != '__init__.py'])
    
    for level_file in level_files:
        try:
            with open(os.path.join(LEVELS_DIR, level_file), 'r', encoding='utf-8') as f:
                level_json = json.load(f)
                
                # 检查关卡文件是否包含必要的字段
                if 'layout' in level_json and isinstance(level_json['layout'], list):
                    levels.append(level_json['layout'])
                    level_data.append({
                        'name': level_json.get('name', f'关卡 {len(levels)}'),
                        'difficulty': level_json.get('difficulty', '未知'),
                        'par_moves': level_json.get('par_moves', 0),
                        'par_pushes': level_json.get('par_pushes', 0),
                        'description': level_json.get('description', '')
                    })
                else:
                    print(f"跳过无效的关卡文件：{level_file}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载关卡文件 {level_file} 时出错：{e}")
    
    return levels, level_data

# 加载关卡
LEVELS, LEVEL_DATA = load_levels()
