import pygame
import sys
import json
import os
from tkinter import filedialog
import tkinter as tk
from sprites import SpriteSheet

# Constants
TILE_SIZE = 64
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GRID_COLS = 16
GRID_ROWS = 12
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (200, 200, 200)

class MenuItem:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False

    def draw(self, screen, font):
        # 绘制按钮背景
        color = LIGHT_GRAY if self.is_hovered else WHITE
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 1)
        
        # 绘制文本
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Menu:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.items = []
        self.visible = False
        self.item_height = 30

    def add_item(self, text):
        item_y = self.rect.top + len(self.items) * self.item_height
        item = MenuItem(text, self.rect.left, item_y, self.rect.width, self.item_height)
        self.items.append(item)

    def draw(self, screen, font):
        if not self.visible:
            return
            
        # 绘制菜单背景
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 1)
        
        # 绘制菜单项
        for item in self.items:
            item.draw(screen, font)

class LevelEditor:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        # 初始化中文字体
        try:
            if os.name == 'nt':  # Windows系统
                self.font = pygame.font.SysFont('SimHei', 28)
                self.menu_font = pygame.font.SysFont('SimHei', 24)
                self.title_font = pygame.font.SysFont('SimHei', 36)
            else:  # 其他系统
                self.font = pygame.font.SysFont('notosanscjk', 28)
                self.menu_font = pygame.font.SysFont('notosanscjk', 24)
                self.title_font = pygame.font.SysFont('notosanscjk', 36)
        except:
            print("未找到中文字体，使用默认字体")
            self.font = pygame.font.Font(None, 28)
            self.menu_font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 36)
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("推箱子关卡编辑器")
        self.clock = pygame.time.Clock()
        
        # 隐藏 tkinter 主窗口
        self.root = tk.Tk()
        self.root.withdraw()
        
        # 初始化精灵
        self.sprites = SpriteSheet(TILE_SIZE)
        
        # 初始化网格
        self.grid = [[' ' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.current_tile = '#'
        self.grid_offset_x = (SCREEN_WIDTH - GRID_COLS * TILE_SIZE) // 2
        self.grid_offset_y = 80  # 为菜单栏留出空间
        
        # 当前编辑的文件路径
        self.current_file_path = None
        
        # 初始化工具栏
        self.tools = [
            {'char': '#', 'name': '墙', 'sprite': self.sprites.wall},
            {'char': '@', 'name': '玩家', 'sprite': self.sprites.player},
            {'char': '$', 'name': '箱子', 'sprite': self.sprites.box},
            {'char': '.', 'name': '目标', 'sprite': self.sprites.target},
            {'char': ' ', 'name': '空地', 'sprite': None}
        ]
        self.tool_rects = []
        self.setup_tool_palette()
        
        # 初始化菜单
        self.file_menu = Menu(10, 30, 150, 150)  # 增加菜单大小
        self.file_menu.add_item("新建")
        self.file_menu.add_item("打开")
        self.file_menu.add_item("保存")
        self.file_menu.add_item("退出")

        self.edit_menu = Menu(140, 30, 150, 60)  # 增加菜单大小
        self.edit_menu.add_item("清空网格")

        # 菜单按钮
        self.file_button = MenuItem("文件", 10, 0, 120, 30)
        self.edit_button = MenuItem("编辑", 140, 0, 120, 30)
        
        # 当前活动的菜单
        self.active_menu = None

        # 消息系统
        self.message = ""
        self.message_time = 0

    def handle_menu_click(self, pos):
        """处理菜单点击"""
        # 检查主菜单按钮点击
        if self.file_button.rect.collidepoint(pos):
            self.file_menu.visible = not self.file_menu.visible
            self.edit_menu.visible = False
            self.active_menu = self.file_menu if self.file_menu.visible else None
            return True
        elif self.edit_button.rect.collidepoint(pos):
            self.edit_menu.visible = not self.edit_menu.visible
            self.file_menu.visible = False
            self.active_menu = self.edit_menu if self.edit_menu.visible else None
            return True

        # 检查子菜单项点击
        if self.file_menu.visible:
            for i, item in enumerate(self.file_menu.items):
                if item.rect.collidepoint(pos):
                    if i == 0:  # 新建
                        self.clear_grid()
                    elif i == 1:  # 打开
                        self.load_level_from_file()
                    elif i == 2:  # 保存
                        self.save_level_to_file()
                    elif i == 3:  # 退出
                        pygame.quit()
                        sys.exit()
                    self.file_menu.visible = False
                    self.active_menu = None
                    return True

        if self.edit_menu.visible:
            for i, item in enumerate(self.edit_menu.items):
                if item.rect.collidepoint(pos):
                    if i == 0:  # 清空网格
                        self.clear_grid()
                    self.edit_menu.visible = False
                    self.active_menu = None
                    return True

        # 如果点击在菜单外部，关闭所有菜单
        if self.active_menu:
            self.file_menu.visible = False
            self.edit_menu.visible = False
            self.active_menu = None
            return True

        return False

    def draw_menus(self):
        """绘制菜单"""
        # 绘制菜单背景
        pygame.draw.rect(self.screen, WHITE, (0, 0, SCREEN_WIDTH, 40))
        pygame.draw.line(self.screen, BLACK, (0, 40), (SCREEN_WIDTH, 40))
        
        # 绘制主菜单按钮
        self.file_button.draw(self.screen, self.menu_font)
        self.edit_button.draw(self.screen, self.menu_font)
        
        # 绘制子菜单
        if self.file_menu.visible:
            pygame.draw.rect(self.screen, WHITE, self.file_menu.rect)
            pygame.draw.rect(self.screen, BLACK, self.file_menu.rect, 1)
            for item in self.file_menu.items:
                color = LIGHT_GRAY if item.is_hovered else WHITE
                pygame.draw.rect(self.screen, color, item.rect)
                pygame.draw.rect(self.screen, BLACK, item.rect, 1)
                text = self.menu_font.render(item.text, True, BLACK)
                text_rect = text.get_rect(center=item.rect.center)
                self.screen.blit(text, text_rect)
        
        if self.edit_menu.visible:
            pygame.draw.rect(self.screen, WHITE, self.edit_menu.rect)
            pygame.draw.rect(self.screen, BLACK, self.edit_menu.rect, 1)
            for item in self.edit_menu.items:
                color = LIGHT_GRAY if item.is_hovered else WHITE
                pygame.draw.rect(self.screen, color, item.rect)
                pygame.draw.rect(self.screen, BLACK, item.rect, 1)
                text = self.menu_font.render(item.text, True, BLACK)
                text_rect = text.get_rect(center=item.rect.center)
                self.screen.blit(text, text_rect)

    def update_menu_hover(self, pos):
        """更新菜单项的悬停状态"""
        # 更新主菜单按钮的悬停状态
        self.file_button.is_hovered = self.file_button.rect.collidepoint(pos)
        self.edit_button.is_hovered = self.edit_button.rect.collidepoint(pos)
        
        # 更新子菜单项的悬停状态
        if self.file_menu.visible:
            for item in self.file_menu.items:
                item.is_hovered = item.rect.collidepoint(pos)
        if self.edit_menu.visible:
            for item in self.edit_menu.items:
                item.is_hovered = item.rect.collidepoint(pos)

    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()
            
            # 更新菜单悬停状态
            self.update_menu_hover(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键
                        # 先检查菜单点击
                        if not self.handle_menu_click(event.pos):
                            # 如果不是点击菜单，则处理网格点击
                            self.handle_mouse_click(event.pos)
                    elif event.button == 3:  # 右键
                        self.handle_mouse_click(event.pos, right_click=True)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # 绘制界面
            self.screen.fill(GRAY)
            
            # 绘制菜单
            self.draw_menus()
            
            # 绘制标题
            title_text = self.title_font.render("推箱子关卡编辑器", True, BLACK)
            title_rect = title_text.get_rect(centerx=SCREEN_WIDTH//2, top=45)
            self.screen.blit(title_text, title_rect)
            
            self.draw_grid()
            self.draw_tool_palette()
            self.draw_controls()
            
            # 显示消息
            if self.message and current_time - self.message_time < 3000:
                msg_surface = self.font.render(self.message, True, BLACK)
                self.screen.blit(msg_surface, (10, SCREEN_HEIGHT - 50))
            
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()
        self.root.destroy()

    def new_level(self):
        """创建新关卡"""
        self.grid = [[' ' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.current_file_path = None
        self.message = "已创建新关卡"
        self.message_time = pygame.time.get_ticks()

    def load_level_from_file(self):
        """通过文件对话框选择并加载关卡文件"""
        try:
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择关卡文件",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir=os.path.join(os.path.dirname(__file__), 'levels')
            )
            
            if not file_path:
                self.message = "未选择文件"
                self.message_time = pygame.time.get_ticks()
                return
            
            # 记住当前文件路径
            self.current_file_path = file_path
            
            # 读取关卡文件
            with open(file_path, 'r', encoding='utf-8') as f:
                level_data = json.load(f)
            
            # 支持 layout 和 map 两种字段
            level_layout = level_data.get('layout') or level_data.get('map')
            
            if not level_layout or not isinstance(level_layout, list):
                self.message = "无效的关卡文件格式"
                self.message_time = pygame.time.get_ticks()
                return
            
            # 清空当前网格
            self.grid = [[' ' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
            
            # 加载关卡布局
            for row_idx, row_str in enumerate(level_layout):
                if row_idx >= GRID_ROWS:
                    break
                for col_idx, cell in enumerate(row_str):
                    if col_idx >= GRID_COLS:
                        break
                    self.grid[row_idx][col_idx] = cell
            
            self.message = f"成功加载关卡文件：{os.path.basename(file_path)}"
            self.message_time = pygame.time.get_ticks()
        
        except Exception as e:
            self.message = f"加载关卡文件时出错：{e}"
            self.message_time = pygame.time.get_ticks()

    def save_level_to_file(self):
        """通过文件对话框选择保存关卡文件"""
        # 验证关卡
        player_count = sum(row.count('@') for row in self.grid)
        box_count = sum(row.count('$') for row in self.grid)
        target_count = sum(row.count('.') for row in self.grid)
        
        if player_count != 1:
            self.message = "关卡必须有且只有一个玩家"
            self.message_time = pygame.time.get_ticks()
            return
        
        if box_count == 0:
            self.message = "关卡必须至少有一个箱子"
            self.message_time = pygame.time.get_ticks()
            return
        
        if box_count != target_count:
            self.message = "箱子数量必须与目标点数量相同"
            self.message_time = pygame.time.get_ticks()
            return
        
        try:
            # 如果是已经打开的文件，直接保存
            if self.current_file_path:
                save_path = self.current_file_path
            else:
                # 打开文件保存对话框
                save_path = filedialog.asksaveasfilename(
                    title="保存关卡文件",
                    defaultextension=".json",
                    filetypes=[("JSON文件", "*.json")],
                    initialdir=os.path.join(os.path.dirname(__file__), 'levels'),
                    initialfile=f"custom_level{len(os.listdir(os.path.join(os.path.dirname(__file__), 'levels'))) + 1}.json"
                )
            
            if not save_path:
                self.message = "取消保存"
                self.message_time = pygame.time.get_ticks()
                return
            
            # 记住当前文件路径
            self.current_file_path = save_path
            
            # 保存关卡
            level_data = {
                "name": os.path.splitext(os.path.basename(save_path))[0],
                "layout": self.grid_to_level(),
                "difficulty": "自定义",
                "par_moves": sum(row.count('$') for row in self.grid) * 10,
                "par_pushes": sum(row.count('$') for row in self.grid) * 4
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(level_data, f, ensure_ascii=False, indent=4)
            
            self.message = f"关卡已保存到：{save_path}"
            self.message_time = pygame.time.get_ticks()
        
        except Exception as e:
            self.message = f"保存关卡时出错：{e}"
            self.message_time = pygame.time.get_ticks()

    def grid_to_level(self):
        """将网格转换为关卡布局"""
        level = []
        for row in self.grid:
            level.append(''.join(row))
        return level

    def draw_controls(self):
        controls = [
            "控制说明:",
            "左键 - 放置方块",
            "右键 - 删除方块",
            "L - 加载关卡",
            "S - 保存关卡",
            "C - 清空网格",
            "ESC - 退出"
        ]
        
        y = SCREEN_HEIGHT - 150
        for text in controls:
            surface = self.font.render(text, True, BLACK)
            self.screen.blit(surface, (10, y))
            y += 25

    def draw_grid(self):
        # Draw background
        self.screen.fill(GRAY)
        
        # Draw grid
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = self.grid_offset_x + col * TILE_SIZE
                y = self.grid_offset_y + row * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                
                # Draw cell background
                pygame.draw.rect(self.screen, WHITE, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)
                
                # Draw cell content
                cell = self.grid[row][col]
                if cell != ' ':
                    sprite = None
                    for tool in self.tools:
                        if tool['char'] == cell:
                            sprite = tool['sprite']
                            break
                    if sprite:
                        self.screen.blit(sprite, rect)

    def draw_tool_palette(self):
        for tool, rect in zip(self.tools, self.tool_rects):
            # Draw tool background
            color = RED if tool['char'] == self.current_tile else WHITE
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            
            # Draw tool sprite or character
            if tool['sprite']:
                self.screen.blit(tool['sprite'], rect)
            
            # Draw tool name
            text = self.font.render(tool['name'], True, BLACK)
            text_rect = text.get_rect(midleft=(rect.right + 10, rect.centery))
            self.screen.blit(text, text_rect)

    def handle_mouse_click(self, pos, right_click=False):
        # Check tool palette
        for i, rect in enumerate(self.tool_rects):
            if rect.collidepoint(pos):
                if not right_click:
                    self.current_tile = self.tools[i]['char']
                return
        
        # Check grid
        grid_rect = pygame.Rect(self.grid_offset_x, self.grid_offset_y,
                              GRID_COLS * TILE_SIZE, GRID_ROWS * TILE_SIZE)
        if grid_rect.collidepoint(pos):
            grid_x = (pos[0] - self.grid_offset_x) // TILE_SIZE
            grid_y = (pos[1] - self.grid_offset_y) // TILE_SIZE
            
            if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
                if right_click:
                    self.grid[grid_y][grid_x] = ' '
                else:
                    # If placing a player, remove the old one
                    if self.current_tile == '@':
                        for row in range(GRID_ROWS):
                            for col in range(GRID_COLS):
                                if self.grid[row][col] == '@':
                                    self.grid[row][col] = ' '
                    self.grid[grid_y][grid_x] = self.current_tile

    def setup_tool_palette(self):
        tool_size = TILE_SIZE
        spacing = 10
        start_x = 10
        start_y = 80
        
        self.tool_rects = []
        for tool in self.tools:
            rect = pygame.Rect(start_x, start_y, tool_size, tool_size)
            self.tool_rects.append(rect)
            start_y += tool_size + spacing

    def clear_grid(self):
        """清空网格"""
        self.grid = [[' ' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.current_file_path = None
        self.message = "网格已清空"
        self.message_time = pygame.time.get_ticks()

if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
