import pygame
import sys
import os
import json  # 添加json导入
from highscores import HighScores
from collections import deque
import math
from sprites import SpriteSheet
from achievements import AchievementManager
from sound_manager import SoundManager
from settings import Settings
from levels import LEVELS, LEVEL_DATA

# Game constants
TILE_SIZE = 64
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 100, 0)

# Animation constants
MOVE_ANIMATION_SPEED = 8
ANIMATION_FRAMES = TILE_SIZE // MOVE_ANIMATION_SPEED

class GameState:
    def __init__(self, player_pos, boxes, moves, pushes):
        self.player_pos = player_pos.copy()
        self.boxes = [box.copy() for box in boxes]
        self.moves = moves
        self.pushes = pushes

class Animation:
    def __init__(self, start_pos, end_pos, frames, is_box=False):
        self.start_pos = start_pos.copy()
        self.end_pos = end_pos.copy()
        self.current_pos = start_pos.copy()
        self.frames_left = frames
        self.total_frames = frames
        self.is_box = is_box
        
    def update(self):
        if self.frames_left > 0:
            progress = (self.total_frames - self.frames_left) / self.total_frames
            self.current_pos.x = self.start_pos.x + (self.end_pos.x - self.start_pos.x) * progress
            self.current_pos.y = self.start_pos.y + (self.end_pos.y - self.start_pos.y) * progress
            self.frames_left -= 1
            return True
        return False

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Sokoban:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.settings = Settings()
        if self.settings.get_setting("fullscreen"):
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("推箱子")
        self.clock = pygame.time.Clock()
        
        # 调试日志控制
        self.debug_logging = False
        
        # 初始化字体，使用系统默认中文字体
        try:
            if os.name == 'nt':  # Windows系统
                self.font = pygame.font.SysFont('SimHei', 28)
                self.title_font = pygame.font.SysFont('SimHei', 48)
            else:  # 其他系统
                self.font = pygame.font.SysFont('notosanscjk', 28)
                self.title_font = pygame.font.SysFont('notosanscjk', 48)
        except:
            print("未找到中文字体，使用默认字体")
            self.font = pygame.font.Font(None, 28)
            self.title_font = pygame.font.Font(None, 48)
        
        # 音效相关属性
        self.move_sound = None
        self.push_sound = None
        self.complete_sound = None
        self.undo_sound = None
        
        try:
            # 尝试加载音效文件
            sound_dir = os.path.join(os.path.dirname(__file__), 'assets')
            
            move_path = os.path.join(sound_dir, 'move.wav')
            push_path = os.path.join(sound_dir, 'push.wav')
            complete_path = os.path.join(sound_dir, 'complete.wav')
            
            if os.path.exists(move_path):
                self.move_sound = pygame.mixer.Sound(move_path)
            if os.path.exists(push_path):
                self.push_sound = pygame.mixer.Sound(push_path)
            if os.path.exists(complete_path):
                self.complete_sound = pygame.mixer.Sound(complete_path)
            
            # 如果没有单独的撤销音效，复用移动音效
            self.undo_sound = self.move_sound
        except Exception as e:
            print(f"音效加载错误: {e}")
            print("将使用静音模式")
        
        # 初始化精灵
        self.sprites = SpriteSheet(64)  # 64px tile size
        
        # 初始化成就系统
        self.achievement_manager = AchievementManager()
        
        # 加载自定义关卡
        self.add_custom_levels()
        
        # 游戏状态
        self.current_level = 0
        self.moves = 0
        self.pushes = 0
        self.level_complete = False
        self.show_menu = True
        self.high_scores = HighScores()
        self.show_achievements = False
        self.used_undo = False
        
        # 添加 level 属性
        self.level = None
        
        # 撤销系统
        self.history = deque(maxlen=50)  # 最多保存50步历史
        
        # 动画系统
        self.current_animation = None
        self.animated_box = None
        
        # 创建按钮
        self.buttons = []
        self.create_buttons()
        
        # 初始化关卡
        self.reset_level()
        
        # 初始化声音管理器
        self.sound_manager = SoundManager()
        self.sound_manager.set_music_volume(self.settings.get_setting("music_volume"))
        self.sound_manager.set_effects_volume(self.settings.get_setting("effects_volume"))
        
        # 播放音乐
        self.sound_manager.play_music("menu")

    def create_buttons(self):
        button_width = 200
        button_height = 40
        x_start = (SCREEN_WIDTH - button_width) // 2
        y_start = 200
        spacing = 50
        
        self.buttons = []
        
        # 标准关卡按钮
        for i, level_data in enumerate(LEVEL_DATA[:10]):  # 限制为前10个标准关卡
            button = Button(x_start, y_start + i * spacing, button_width, button_height,
                          f"关卡 {i+1}：{level_data['name']}", WHITE, YELLOW)
            self.buttons.append(button)
        
        # 自定义关卡按钮
        custom_levels = self.load_custom_levels()
        if custom_levels:
            custom_levels_button = Button(
                x_start, 
                y_start + len(self.buttons) * spacing, 
                button_width, 
                button_height, 
                f"自定义关卡 ({len(custom_levels)}个)", 
                WHITE, 
                GREEN
            )
            self.buttons.append(custom_levels_button)
    
    def save_state(self):
        state = GameState(
            player_pos=self.player_pos,
            boxes=self.boxes,
            moves=self.moves,
            pushes=self.pushes
        )
        self.history.append(state)
    
    def undo(self):
        if self.history:
            state = self.history.pop()
            self.player_pos = state.player_pos
            self.boxes = state.boxes
            self.moves = state.moves
            self.pushes = state.pushes
            self.used_undo = True
            return True
        return False
    
    def parse_level(self):
        """解析当前关卡数据"""
        # 获取关卡数据
        level_data = LEVEL_DATA[self.current_level]
        self.level_name = level_data.get('name', f'Level {self.current_level + 1}')
        self.par_moves = level_data.get('par_moves', 0)
        self.par_pushes = level_data.get('par_pushes', 0)
        
        # 获取关卡布局
        self.layout = LEVELS[self.current_level]
        
        # 重置游戏状态
        self.moves = 0
        self.pushes = 0
        self.level_complete = False
        
        # 初始化游戏地图
        self.walls = set()
        self.boxes = set()
        self.targets = set()
        self.player_pos = None
        
        # 计算关卡尺寸
        self.level_width = len(self.layout[0]) if self.layout else 0
        self.level_height = len(self.layout)
        
        # 解析布局
        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                if cell == '#':
                    self.walls.add((x, y))
                elif cell == '$':
                    self.boxes.add((x, y))
                elif cell == '.':
                    self.targets.add((x, y))
                elif cell == '@':
                    self.player_pos = (x, y)
                elif cell == '*':  # 箱子在目标点上
                    self.boxes.add((x, y))
                    self.targets.add((x, y))
                elif cell == '+':  # 玩家在目标点上
                    self.player_pos = (x, y)
                    self.targets.add((x, y))
        
        self.log_debug(f"关卡尺寸：{self.level_width}x{self.level_height}")
        self.log_debug(f"玩家初始位置：{self.player_pos}")
        self.log_debug(f"墙壁位置：{self.walls}")
        self.log_debug(f"箱子位置：{self.boxes}")
        self.log_debug(f"目标位置：{self.targets}")
    
    def reset_level(self):
        """重置当前关卡"""
        # 重置游戏状态
        self.moves = 0
        self.pushes = 0
        self.used_undo = False
        self.level_complete = False
        
        # 加载当前关卡的具体信息
        if 0 <= self.current_level < len(LEVEL_DATA):
            # 设置 level 属性
            self.level = LEVEL_DATA[self.current_level]
            
            # 解析关卡布局
            self.parse_level()
        else:
            print(f"错误：无效的关卡索引 {self.current_level}")
            self.level = None

    def draw_menu(self):
        """绘制主菜单"""
        # 设置背景色
        self.screen.fill((200, 200, 200))  # 浅灰色背景
        
        # 设置标题
        title = self.title_font.render("推箱子", True, (0, 0, 0))
        title_rect = title.get_rect(centerx=SCREEN_WIDTH // 2, y=50)
        self.screen.blit(title, title_rect)
        
        # 绘制关卡选择按钮
        button_width = 300
        button_height = 40
        button_margin = 15
        start_y = 150
        
        # 显示关卡名称
        for i, level_data in enumerate(LEVEL_DATA):
            button_rect = pygame.Rect(
                (SCREEN_WIDTH - button_width) // 2,
                start_y + i * (button_height + button_margin),
                button_width,
                button_height
            )
            
            # 绘制按钮边框和背景
            if i == self.current_level:
                pygame.draw.rect(self.screen, (100, 100, 100), button_rect)
                pygame.draw.rect(self.screen, (50, 50, 50), button_rect, 2)
            else:
                pygame.draw.rect(self.screen, (150, 150, 150), button_rect)
                pygame.draw.rect(self.screen, (100, 100, 100), button_rect, 2)
            
            # 绘制关卡名称
            level_name = level_data.get("name", f"关卡 {i + 1}")
            text = self.font.render(level_name, True, (0, 0, 0))
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
        
        # 自定义关卡按钮
        # custom_button_rect = pygame.Rect(
        #     (SCREEN_WIDTH - button_width) // 2,
        #     start_y + len(LEVEL_DATA) * (button_height + button_margin),
        #     button_width,
        #     button_height
        # )
        # pygame.draw.rect(self.screen, (150, 150, 150), custom_button_rect)
        # pygame.draw.rect(self.screen, (100, 100, 100), custom_button_rect, 2)
        # custom_text = self.font.render("自定义关卡", True, (0, 0, 0))
        # custom_text_rect = custom_text.get_rect(center=custom_button_rect.center)
        # self.screen.blit(custom_text, custom_text_rect)

        # 关卡编辑器按钮
        editor_button_rect = pygame.Rect(
            (SCREEN_WIDTH - button_width) // 2,
            start_y + (len(LEVEL_DATA) + 1) * (button_height + button_margin),
            button_width,
            button_height
        )
        pygame.draw.rect(self.screen, (150, 150, 150), editor_button_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), editor_button_rect, 2)
        editor_text = self.font.render("关卡编辑器", True, (0, 0, 0))
        editor_text_rect = editor_text.get_rect(center=editor_button_rect.center)
        self.screen.blit(editor_text, editor_text_rect)

        # 绘制最佳成绩
        scores = self.load_scores()
        scores_x = SCREEN_WIDTH - 250
        scores_y = 150
        self.screen.blit(self.font.render("最佳成绩:", True, (0, 0, 0)), (scores_x, scores_y))
        
        for i in range(len(LEVEL_DATA)):
            level_key = str(i + 1)
            score = scores.get(level_key, {"moves": "未完成", "pushes": "未完成"})
            score_text = f"关卡 {level_key}: 移动: {score['moves']}, 推箱: {score['pushes']}"
            self.screen.blit(
                self.font.render(score_text, True, (0, 0, 0)),
                (scores_x, scores_y + 30 + i * 25)
            )
        
        # 绘制调试日志选择框
        debug_x = SCREEN_WIDTH - 250
        debug_y = scores_y + len(LEVEL_DATA) * 25 + 50
        debug_rect = pygame.Rect(debug_x, debug_y, 20, 20)
        pygame.draw.rect(self.screen, (255, 255, 255), debug_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), debug_rect, 2)
        
        if self.debug_logging:
            # 绘制勾选标记
            pygame.draw.line(self.screen, (0, 0, 0), 
                           (debug_rect.left + 4, debug_rect.centery),
                           (debug_rect.centerx - 2, debug_rect.bottom - 4), 2)
            pygame.draw.line(self.screen, (0, 0, 0),
                           (debug_rect.centerx - 2, debug_rect.bottom - 4),
                           (debug_rect.right - 4, debug_rect.top + 4), 2)
        
        debug_text = self.font.render("启用调试日志", True, (0, 0, 0))
        self.screen.blit(debug_text, (debug_x + 30, debug_y))

    def handle_menu_events(self, event):
        """处理主菜单事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查调试日志选择框点击
            debug_x = SCREEN_WIDTH - 250
            debug_y = 150 + len(LEVEL_DATA) * 25 + 50
            debug_rect = pygame.Rect(debug_x, debug_y, 20, 20)
            if debug_rect.collidepoint(mouse_pos):
                self.debug_logging = not self.debug_logging
                self.log_debug(f"调试日志已{'启用' if self.debug_logging else '禁用'}")
                return
            
            # 检查关卡按钮点击
            button_width = 300
            button_height = 40
            button_margin = 15
            start_y = 150
            
            for i, level_data in enumerate(LEVEL_DATA):
                button_rect = pygame.Rect(
                    (SCREEN_WIDTH - button_width) // 2,
                    start_y + i * (button_height + button_margin),
                    button_width,
                    button_height
                )
                if button_rect.collidepoint(mouse_pos):
                    self.current_level = i
                    self.show_menu = False
                    self.reset_level()
                    return

            # 检查自定义关卡按钮点击
            custom_button_rect = pygame.Rect(
                (SCREEN_WIDTH - button_width) // 2,
                start_y + len(LEVEL_DATA) * (button_height + button_margin),
                button_width,
                button_height
            )
            if custom_button_rect.collidepoint(mouse_pos):
                self.load_custom_levels()
                self.show_menu = False
                self.reset_level()
                return

            # 检查关卡编辑器按钮点击
            editor_button_rect = pygame.Rect(
                (SCREEN_WIDTH - button_width) // 2,
                start_y + (len(LEVEL_DATA) + 1) * (button_height + button_margin),
                button_width,
                button_height
            )
            if editor_button_rect.collidepoint(mouse_pos):
                self.run_level_editor()
                return
    
    def load_custom_levels(self):
        """加载自定义关卡"""
        import os
        import json

        # 自定义关卡列表
        custom_levels = []

        # 关卡文件目录
        levels_dir = os.path.join(os.path.dirname(__file__), 'levels')

        # 遍历目录中的文件
        for filename in os.listdir(levels_dir):
            # 检查文件是否以 custom 开头且为 JSON 文件
            if filename.startswith('custom') and filename.endswith('.json'):
                try:
                    file_path = os.path.join(levels_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        level_data = json.load(f)
                        
                        # 如果是列表，直接扩展；如果是单个关卡，追加
                        if isinstance(level_data, list):
                            custom_levels.extend(level_data)
                        else:
                            custom_levels.append(level_data)
                except Exception as e:
                    print(f"加载自定义关卡文件 {filename} 时出错: {e}")

        # 如果找到自定义关卡
        if custom_levels:
            # 将自定义关卡添加到全局关卡列表
            LEVEL_DATA.extend(custom_levels)
            
            # 切换到第一个自定义关卡
            self.current_level = len(LEVEL_DATA) - len(custom_levels)
            self.reset_level()
            self.show_menu = False
        else:
            # 如果没有找到自定义关卡
            print("未找到自定义关卡文件")
            # 可以添加一个弹窗或者其他提示用户的方式

    def run_level_editor(self):
        """运行关卡编辑器"""
        import subprocess
        subprocess.Popen(['python', 'level_editor.py'])

    def log_debug(self, message):
        """打印调试日志"""
        if self.debug_logging:
            print(f"[DEBUG] {message}")

    def load_scores(self):
        """从文件加载最高分记录"""
        try:
            with open('scores.txt', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            # 如果文件不存在或损坏，返回默认值
            return {str(i+1): {"moves": "未完成", "pushes": "未完成"} for i in range(len(LEVEL_DATA))}

    def save_scores(self, scores):
        """保存最高分记录到文件"""
        with open('scores.txt', 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False)

    def update_score(self):
        """更新当前关卡的最高分记录"""
        scores = self.load_scores()
        level_key = str(self.current_level + 1)
        
        if level_key not in scores:
            scores[level_key] = {"moves": "未完成", "pushes": "未完成"}
        
        current_moves = str(self.moves)
        current_pushes = str(self.pushes)
        
        # 如果当前成绩更好，或者之前是"未完成"，则更新记录
        if (scores[level_key]["moves"] == "未完成" or 
            (scores[level_key]["moves"] != "未完成" and int(current_moves) < int(scores[level_key]["moves"]))):
            scores[level_key]["moves"] = current_moves
            scores[level_key]["pushes"] = current_pushes
            self.save_scores(scores)
            self.log_debug(f"更新关卡{level_key}最高分：移动{current_moves}步，推箱{current_pushes}次")

    def draw_level(self):
        """绘制关卡"""
        # 计算居中偏移
        offset_x = (SCREEN_WIDTH - self.level_width * TILE_SIZE) // 2
        offset_y = (SCREEN_HEIGHT - self.level_height * TILE_SIZE) // 2
        
        # 绘制地图
        for y in range(self.level_height):
            for x in range(self.level_width):
                rect = pygame.Rect(
                    offset_x + x * TILE_SIZE,
                    offset_y + y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                
                cell = ' '
                if (x, y) in self.walls:
                    cell = '#'
                elif (x, y) in self.targets:
                    cell = '.'
                
                if cell == '#':
                    # 绘制墙壁
                    self.screen.blit(self.sprites.wall, rect)
                elif cell == ' ':
                    # 绘制空地
                    self.screen.blit(self.sprites.floor, rect)
                elif cell == '.':
                    # 绘制目标点
                    self.screen.blit(self.sprites.floor, rect)
                    self.screen.blit(self.sprites.target, rect)

        # 绘制箱子
        for box in self.boxes:
            box_rect = pygame.Rect(
                offset_x + box[0] * TILE_SIZE, 
                offset_y + box[1] * TILE_SIZE, 
                TILE_SIZE, 
                TILE_SIZE
            )
            self.screen.blit(self.sprites.box, box_rect)
            if box in self.targets:
                pygame.draw.rect(self.screen, (0, 255, 0), box_rect, 2)

        # 绘制玩家
        player_rect = pygame.Rect(
            offset_x + self.player_pos[0] * TILE_SIZE, 
            offset_y + self.player_pos[1] * TILE_SIZE, 
            TILE_SIZE, 
            TILE_SIZE
        )
        self.screen.blit(self.sprites.player, player_rect)

        # 绘制关卡信息
        level_info = self.get_current_level_info()
        level_text = self.font.render(
            f"关卡：{level_info['name']} (难度：{level_info['difficulty']})", 
            True, 
            (0, 0, 0)
        )
        moves_text = self.font.render(
            f"移动：{self.moves} 推动：{self.pushes}", 
            True, 
            (0, 0, 0)
        )
        par_text = self.font.render(
            f"目标移动：{level_info.get('par_moves', '无')} 目标推动：{level_info.get('par_pushes', '无')}", 
            True, 
            (0, 128, 0)
        )
        
        self.screen.blit(level_text, (10, 10))
        self.screen.blit(moves_text, (10, 50))
        self.screen.blit(par_text, (10, 90))
    
    def draw_game(self):
        """绘制游戏画面"""
        self.screen.fill((255, 255, 255))  # 白色背景
        self.draw_level()
        
        # 显示关卡完成提示
        if self.level_complete:
            # 计算半透明背景的位置和大小
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((255, 255, 255))
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))

            # 显示成功信息
            success_text = self.title_font.render("恭喜过关！", True, (0, 128, 0))
            text_rect = success_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(success_text, text_rect)

            # 创建按钮
            button_width = 200
            button_height = 40
            button_margin = 20
            buttons_start_y = SCREEN_HEIGHT // 2 + 20

            # 判断是否是最后一关
            is_last_level = self.current_level == len(LEVEL_DATA) - 1

            if is_last_level:
                # 最后一关完成，显示特殊信息
                complete_text = self.font.render("恭喜你完成了所有关卡！", True, (0, 128, 0))
                complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, buttons_start_y - 40))
                self.screen.blit(complete_text, complete_rect)

                # 创建"重试本关"和"返回主菜单"按钮
                retry_button = pygame.Rect(
                    SCREEN_WIDTH // 2 - button_width - button_margin // 2,
                    buttons_start_y,
                    button_width,
                    button_height
                )
                menu_button = pygame.Rect(
                    SCREEN_WIDTH // 2 + button_margin // 2,
                    buttons_start_y,
                    button_width,
                    button_height
                )

                # 绘制按钮
                pygame.draw.rect(self.screen, (200, 200, 200), retry_button)
                pygame.draw.rect(self.screen, (200, 200, 200), menu_button)
                pygame.draw.rect(self.screen, (100, 100, 100), retry_button, 2)
                pygame.draw.rect(self.screen, (100, 100, 100), menu_button, 2)

                # 绘制按钮文字
                retry_text = self.font.render("重试本关", True, (0, 0, 0))
                menu_text = self.font.render("返回主菜单", True, (0, 0, 0))
                self.screen.blit(retry_text, retry_text.get_rect(center=retry_button.center))
                self.screen.blit(menu_text, menu_text.get_rect(center=menu_button.center))
            else:
                # 普通关卡完成，显示"下一关"和"重试本关"按钮
                next_button = pygame.Rect(
                    SCREEN_WIDTH // 2 - button_width - button_margin // 2,
                    buttons_start_y,
                    button_width,
                    button_height
                )
                retry_button = pygame.Rect(
                    SCREEN_WIDTH // 2 + button_margin // 2,
                    buttons_start_y,
                    button_width,
                    button_height
                )

                # 绘制按钮
                pygame.draw.rect(self.screen, (200, 200, 200), next_button)
                pygame.draw.rect(self.screen, (200, 200, 200), retry_button)
                pygame.draw.rect(self.screen, (100, 100, 100), next_button, 2)
                pygame.draw.rect(self.screen, (100, 100, 100), retry_button, 2)

                # 绘制按钮文字
                next_text = self.font.render("下一关", True, (0, 0, 0))
                retry_text = self.font.render("重试本关", True, (0, 0, 0))
                self.screen.blit(next_text, next_text.get_rect(center=next_button.center))
                self.screen.blit(retry_text, retry_text.get_rect(center=retry_button.center))

            # 显示当前关卡成绩
            score_text = self.font.render(f"移动次数: {self.moves}  推箱子次数: {self.pushes}", True, (0, 0, 0))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, buttons_start_y + button_height + 30))
            self.screen.blit(score_text, score_rect)

        if self.show_achievements:
            self.draw_achievements()
    
    def draw_achievements(self):
        achievements = self.achievement_manager.get_all_achievements()
        y = 50
        for achievement in achievements.values():
            color = (0, 255, 0) if achievement.unlocked else (128, 128, 128)
            text = f"{achievement.icon_char} {achievement.name}: {achievement.description}"
            text_surface = self.font.render(text, True, color)
            self.screen.blit(text_surface, (20, y))
            y += 30
    
    def draw(self):
        if self.show_menu:
            self.draw_menu()
        else:
            self.draw_level()
            self.draw_game()
        pygame.display.flip()
    
    def start_animation(self, start_pos, end_pos, is_box=False):
        self.current_animation = Animation(start_pos, end_pos, ANIMATION_FRAMES, is_box)
    
    def move_player(self, dx, dy):
        """移动玩家
        dx, dy: 移动方向 (-1,0)左, (1,0)右, (0,-1)上, (0,1)下
        返回是否移动成功
        """
        if not self.player_pos:
            self.log_debug("错误：未找到玩家位置")
            return False
            
        current_x, current_y = self.player_pos
        new_x = current_x + dx
        new_y = current_y + dy
        
        self.log_debug("\n尝试移动")
        self.log_debug(f"当前玩家位置：{self.player_pos}")
        self.log_debug(f"尝试移动到：({new_x}, {new_y})")
        self.log_debug(f"关卡范围：x(0-{self.level_width-1}), y(0-{self.level_height-1})")
        
        # 检查是否越界
        if not (0 <= new_x < self.level_width and 0 <= new_y < self.level_height):
            self.log_debug(f"移动位置越界：new_x={new_x}, new_y={new_y}")
            return False
            
        # 检查是否撞墙
        if (new_x, new_y) in self.walls:
            self.log_debug(f"新位置是墙壁：({new_x}, {new_y})")
            return False
            
        # 检查是否推箱子
        if (new_x, new_y) in self.boxes:
            box_new_x = new_x + dx
            box_new_y = new_y + dy
            
            # 检查箱子新位置是否有效
            if not (0 <= box_new_x < self.level_width and 0 <= box_new_y < self.level_height):
                self.log_debug(f"箱子新位置越界：({box_new_x}, {box_new_y})")
                return False
                
            # 检查箱子新位置是否有墙或其他箱子
            if (box_new_x, box_new_y) in self.walls or (box_new_x, box_new_y) in self.boxes:
                self.log_debug(f"箱子无法移动到：({box_new_x}, {box_new_y})")
                return False
                
            # 移动箱子
            self.boxes.remove((new_x, new_y))
            self.boxes.add((box_new_x, box_new_y))
            self.pushes += 1
            self.log_debug(f"推动箱子到：({box_new_x}, {box_new_y})")
            
        # 移动玩家
        self.player_pos = (new_x, new_y)
        self.moves += 1
        self.log_debug(f"玩家移动到：{self.player_pos}")
        
        # 检查是否完成关卡
        if self.check_win():
            self.log_debug("恭喜！关卡完成！")
            self.level_complete = True
            
        return True
    
    def get_box_at_pos(self, x, y):
        """获取指定位置的箱子索引"""
        for i, box in enumerate(self.boxes):
            box_x, box_y = box
            if box_x == x and box_y == y:
                return i
        return None

    def check_win(self):
        """检查是否完成关卡"""
        if all(box in self.targets for box in self.boxes):
            self.log_debug(f"关卡{self.current_level + 1}完成！移动{self.moves}步，推箱{self.pushes}次")
            self.update_score()
            return True
        return False
    
    def next_level(self):
        """切换到下一个关卡"""
        if self.current_level < len(LEVELS) - 1:
            self.current_level += 1
            self.parse_level()
            self.level_complete = False  # 重置关卡完成状态
            return True
        return False

    def get_current_level_info(self):
        """获取当前关卡的详细信息"""
        if 0 <= self.current_level < len(LEVEL_DATA):
            return LEVEL_DATA[self.current_level]
        return {
            'name': '未知关卡',
            'difficulty': '未知',
            'par_moves': 0,
            'par_pushes': 0,
            'description': ''
        }
    
    def update_animation(self):
        """更新动画状态"""
        if self.current_animation:
            # 更新动画帧
            if not self.current_animation.update():
                # 动画结束
                self.current_animation = None
                self.animated_box = None
                
                # 检查是否完成关卡
                self.check_win()
    
    def handle_level_complete_events(self, event):
        """处理关卡完成后的事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查调试日志选择框点击
            debug_x = SCREEN_WIDTH - 250
            debug_y = 150 + len(LEVEL_DATA) * (40 + 20) + len(LEVEL_DATA) * 25 + 70
            debug_rect = pygame.Rect(debug_x, debug_y, 20, 20)
            if debug_rect.collidepoint(mouse_pos):
                self.debug_logging = not self.debug_logging
                return
            
            # 检查关卡按钮点击
            button_width = 300
            button_height = 40
            button_margin = 20
            start_y = 150
            
            for i, level_data in enumerate(LEVEL_DATA):
                button_rect = pygame.Rect(
                    (SCREEN_WIDTH - button_width) // 2,
                    start_y + i * (button_height + button_margin),
                    button_width,
                    button_height
                )
                if button_rect.collidepoint(mouse_pos):
                    self.current_level = i
                    self.show_menu = False
                    self.reset_level()
                    return
    
    def handle_level_complete(self):
        """处理关卡完成后的逻辑"""
        # 计算半透明背景的位置和大小
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        # 显示成功信息
        success_text = self.title_font.render("恭喜过关！", True, (0, 128, 0))
        text_rect = success_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(success_text, text_rect)

        # 创建按钮
        button_width = 200
        button_height = 40
        button_margin = 20
        buttons_start_y = SCREEN_HEIGHT // 2 + 20

        # 判断是否是最后一关
        is_last_level = self.current_level == len(LEVEL_DATA) - 1

        if is_last_level:
            # 最后一关完成，显示特殊信息
            complete_text = self.font.render("恭喜你完成了所有关卡！", True, (0, 128, 0))
            complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, buttons_start_y - 40))
            self.screen.blit(complete_text, complete_rect)

            # 创建"重试本关"和"返回主菜单"按钮
            retry_button = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width - button_margin // 2,
                buttons_start_y,
                button_width,
                button_height
            )
            menu_button = pygame.Rect(
                SCREEN_WIDTH // 2 + button_margin // 2,
                buttons_start_y,
                button_width,
                button_height
            )

            # 绘制按钮
            pygame.draw.rect(self.screen, (200, 200, 200), retry_button)
            pygame.draw.rect(self.screen, (200, 200, 200), menu_button)
            pygame.draw.rect(self.screen, (100, 100, 100), retry_button, 2)
            pygame.draw.rect(self.screen, (100, 100, 100), menu_button, 2)

            # 绘制按钮文字
            retry_text = self.font.render("重试本关", True, (0, 0, 0))
            menu_text = self.font.render("返回主菜单", True, (0, 0, 0))
            self.screen.blit(retry_text, retry_text.get_rect(center=retry_button.center))
            self.screen.blit(menu_text, menu_text.get_rect(center=menu_button.center))
        else:
            # 普通关卡完成，显示"下一关"和"重试本关"按钮
            next_button = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width - button_margin // 2,
                buttons_start_y,
                button_width,
                button_height
            )
            retry_button = pygame.Rect(
                SCREEN_WIDTH // 2 + button_margin // 2,
                buttons_start_y,
                button_width,
                button_height
            )

            # 绘制按钮
            pygame.draw.rect(self.screen, (200, 200, 200), next_button)
            pygame.draw.rect(self.screen, (200, 200, 200), retry_button)
            pygame.draw.rect(self.screen, (100, 100, 100), next_button, 2)
            pygame.draw.rect(self.screen, (100, 100, 100), retry_button, 2)

            # 绘制按钮文字
            next_text = self.font.render("下一关", True, (0, 0, 0))
            retry_text = self.font.render("重试本关", True, (0, 0, 0))
            self.screen.blit(next_text, next_text.get_rect(center=next_button.center))
            self.screen.blit(retry_text, retry_text.get_rect(center=retry_button.center))

        # 显示当前关卡成绩
        score_text = self.font.render(f"移动次数: {self.moves}  推箱子次数: {self.pushes}", True, (0, 0, 0))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, buttons_start_y + button_height + 30))
        self.screen.blit(score_text, score_rect)

    def show_achievement_notification(self, achievement):
        # Add achievement notification animation code here
        pass
    
    def load_custom_levels(self):
        try:
            with open('custom_levels.json', 'r', encoding='utf-8') as f:
                custom_levels_data = json.load(f)
                
                # 验证自定义关卡的格式
                validated_levels = []
                for level_data in custom_levels_data:
                    # 支持两种格式：简单列表和带元数据的字典
                    if isinstance(level_data, dict) and 'layout' in level_data:
                        level = level_data['layout']
                    elif isinstance(level_data, list):
                        level = level_data
                    else:
                        continue
                    
                    # 确保每个关卡都有正确的格式
                    if isinstance(level, list) and all(isinstance(row, str) for row in level):
                        # 检查关卡是否有效（包含玩家、箱子和目标）
                        player_count = sum(row.count('@') for row in level)
                        box_count = sum(row.count('$') for row in level)
                        target_count = sum(row.count('.') for row in level)
                        
                        if player_count == 1 and box_count > 0 and target_count > 0:
                            validated_levels.append(level)
                
                return validated_levels
        except FileNotFoundError:
            print("未找到自定义关卡文件")
            return []
        except json.JSONDecodeError:
            print("自定义关卡文件格式错误")
            return []
        except Exception as e:
            print(f"加载自定义关卡时发生错误: {e}")
            return []
    
    def add_custom_levels(self):
        # 将自定义关卡添加到现有关卡中
        custom_levels = self.load_custom_levels()
        if custom_levels:
            # 在原有关卡后追加自定义关卡
            LEVELS.extend(custom_levels)
            
            # 为每个自定义关卡添加默认元数据
            for _ in range(len(custom_levels)):
                LEVEL_DATA.append({
                    "name": "自定义关卡", 
                    "par_moves": 50, 
                    "par_pushes": 25
                })
            
            print(f"成功加载 {len(custom_levels)} 个自定义关卡")

    def toggle_fullscreen(self):
        is_fullscreen = self.settings.get_setting("fullscreen")
        if is_fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.set_setting("fullscreen", not is_fullscreen)

    def run(self):
        """游戏主循环"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # 菜单状态下的事件处理
                if self.show_menu:
                    self.handle_menu_events(event)
                    continue
                
                # 关卡完成状态下的事件处理
                if self.level_complete:
                    self.handle_level_complete_events(event)
                    continue
                
                # 正常游戏状态下的事件处理
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move_player(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_player(1, 0)
                    elif event.key == pygame.K_UP:
                        self.move_player(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.move_player(0, 1)
                    elif event.key == pygame.K_r:
                        self.reset_level()
                    elif event.key == pygame.K_ESCAPE:
                        self.show_menu = True
                    elif event.key == pygame.K_TAB:
                        self.show_achievements = not self.show_achievements
            
            # 更新动画
            self.update_animation()
            
            # 检查是否完成关卡
            if not self.level_complete and not self.show_menu:
                self.level_complete = self.check_win()
            
            # 绘制游戏画面
            if self.show_menu:
                self.screen.fill((200, 200, 200))  # 浅灰色背景
                self.draw_menu()
            else:
                self.draw_game()
            
            pygame.display.flip()
            self.clock.tick(30)  # 限制帧率
        
        pygame.quit()

import os
import json

# 关卡文件目录
LEVELS_DIR = os.path.join(os.path.dirname(__file__), 'levels')

def load_levels():
    """从levels目录加载所有关卡"""
    levels = []
    level_data = []
    level_files = sorted([f for f in os.listdir(LEVELS_DIR) if f.endswith('.json') and f != '__init__.py'])
    
    for level_file in level_files:
        try:
            with open(os.path.join(LEVELS_DIR, level_file), 'r', encoding='utf-8') as f:
                level_json = json.load(f)
                
                # 支持 layout 和 map 两种字段
                level_layout = level_json.get('layout') or level_json.get('map')
                
                # 检查关卡文件是否包含必要的字段
                if level_layout and isinstance(level_layout, list):
                    # 确保每个关卡至少有一个玩家
                    if not any('@' in row for row in level_layout):
                        print(f"警告：关卡文件 {level_file} 没有玩家('@')，已跳过")
                        continue
                    
                    levels.append(level_layout)
                    level_data.append({
                        'name': level_json.get('name', f'关卡 {len(levels)}'),
                        'difficulty': level_json.get('difficulty', '未知'),
                        'par_moves': level_json.get('par_moves', 50),
                        'par_pushes': level_json.get('par_pushes', 25)
                    })
                else:
                    print(f"警告：关卡文件 {level_file} 格式不正确，已跳过")
        except Exception as e:
            print(f"加载关卡文件 {level_file} 时出错: {e}")
    
    return levels, level_data

# 替换原有的LEVELS和LEVEL_DATA定义
LEVELS, LEVEL_DATA = load_levels()

if __name__ == "__main__":
    game = Sokoban()
    game.run()
