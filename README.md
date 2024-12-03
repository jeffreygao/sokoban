# Sokoban Game

A classic puzzle game where you push boxes to their target locations.

## Setup
1. Ensure you have Python 3.8+ installed
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python sokoban.py`

## How to Play
- Use arrow keys to move the player
- Push boxes (red squares) to their target locations (green outlines)
- Complete the level by placing all boxes on targets
- Press R to reset the current level
- Press Z to undo your last move
- Press ESC to return to the menu
- Press SPACE to proceed to the next level when complete

## Features
- 10 challenging levels from Tutorial to Legend
- Level selection menu
- Move and push counter
- Par scores for each level
- High score tracking
- Smooth movement animations
- Undo system
- Sound effects
- Visual feedback for completed boxes
- Level progress tracking

## Game Elements
- Blue Square: Player
- Red Square: Box
- Green Outline: Target
- Black Square: Wall
- Green Box Outline: Box on target
- Yellow Button: Selected menu item

## Controls Summary
- Arrow Keys: Move player
- R: Reset level
- Z: Undo move
- ESC: Return to menu
- SPACE: Next level (when complete)

## 项目组件

### 游戏本体 (sokoban.py)
- 经典推箱子游戏玩法
- 10个由浅入深的挑战关卡
- 关卡选择菜单
- 移动和推箱计数器
- 每关目标分数
- 最高分记录
- 平滑移动动画
- 撤销系统
- 音效
- 完成状态视觉反馈
- 关卡进度跟踪

### 关卡编辑器 (level_editor.py)
- 可视化编辑界面
- 完整的菜单系统（文件、编辑）
- 支持新建、打开、保存关卡
- 支持清空网格
- 工具栏包含：墙、玩家、箱子、目标点、空地
- 鼠标左键放置元素，右键删除元素
- 支持中文界面
- JSON格式关卡存储

## 安装说明
1. 确保已安装 Python 3.8 或更高版本
2. 安装依赖项：
   ```
   pip install -r requirements.txt
   ```

## 游戏控制
- 方向键：移动玩家
- R键：重置关卡
- Z键：撤销移动
- ESC键：返回菜单
- 空格键：完成关卡后进入下一关

## 关卡编辑器控制
- 左键：放置选中的元素
- 右键：删除元素
- 文件菜单：
  - 新建：创建空白关卡
  - 打开：加载已有关卡
  - 保存：保存当前关卡
  - 退出：关闭编辑器
- 编辑菜单：
  - 清空网格：清除所有元素

## 运行说明
### 运行游戏
```
python sokoban.py
```

### 运行关卡编辑器
```
python level_editor.py
```

## 关卡文件格式
关卡以 JSON 格式存储，包含以下字段：
```json
{
    "layout": [
        ["#", "#", "#"],
        ["#", "@", "#"],
        ["#", "#", "#"]
    ]
}
```
其中：
- # 代表墙
- @ 代表玩家
- $ 代表箱子
- . 代表目标点
- 空格代表空地

## 依赖项
- Python 3.8+
- Pygame 2.4.0
- tkinter (Python标准库，用于文件对话框)

## 注意事项
- 确保每个关卡至少包含一个玩家、一个箱子和一个目标点
- 保存关卡前请确保关卡是可完成的
- 建议使用 16x12 的标准网格大小
