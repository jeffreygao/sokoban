import pygame

class SpriteSheet:
    def __init__(self, size):
        self.size = size
        self.sheet = pygame.Surface((size * 5, size), pygame.SRCALPHA)
        self.generate_sprites()
    
    def generate_sprites(self):
        # Player sprite (SVG character)
        try:
            player_svg = pygame.image.load('assets/player.svg')
            player_surface = pygame.transform.scale(player_svg, (self.size, self.size))
            self.sheet.blit(player_surface, (0, 0))
        except:
            # 如果加载SVG失败，使用备用的矩形图形
            player_rect = pygame.Rect(0, 0, self.size, self.size)
            pygame.draw.rect(self.sheet, (0, 0, 255), player_rect.inflate(-8, -8))
            pygame.draw.circle(self.sheet, (100, 100, 255), player_rect.center, self.size//4)
        
        # Box sprite (wooden crate)
        box_rect = pygame.Rect(self.size, 0, self.size, self.size)
        # Main box
        pygame.draw.rect(self.sheet, (139, 69, 19), box_rect.inflate(-4, -4))
        # Wood grain
        for i in range(3):
            y = box_rect.top + (i + 1) * self.size//4
            pygame.draw.line(self.sheet, (101, 67, 33), 
                           (box_rect.left + 4, y),
                           (box_rect.right - 4, y), 2)
        
        # Wall sprite (brick pattern)
        wall_rect = pygame.Rect(self.size * 2, 0, self.size, self.size)
        # Base wall
        pygame.draw.rect(self.sheet, (128, 128, 128), wall_rect)
        # Brick pattern
        brick_height = self.size // 4
        for i in range(4):
            offset = (i % 2) * self.size//2
            y = wall_rect.top + i * brick_height
            for x in range(2):
                brick_x = wall_rect.left + x * self.size//2 + offset
                if brick_x + self.size//2 <= wall_rect.right:
                    pygame.draw.rect(self.sheet, (169, 169, 169),
                                   (brick_x, y, self.size//2 - 2, brick_height - 2))
        
        # Target sprite (green target)
        target_rect = pygame.Rect(self.size * 3, 0, self.size, self.size)
        # Outer circle
        pygame.draw.circle(self.sheet, (0, 255, 0), target_rect.center, self.size//3, 2)
        # Inner circle
        pygame.draw.circle(self.sheet, (0, 255, 0), target_rect.center, self.size//6, 2)
        # Cross
        cross_size = self.size//4
        center = target_rect.center
        pygame.draw.line(self.sheet, (0, 255, 0), 
                        (center[0] - cross_size, center[1]),
                        (center[0] + cross_size, center[1]), 2)
        pygame.draw.line(self.sheet, (0, 255, 0),
                        (center[0], center[1] - cross_size),
                        (center[0], center[1] + cross_size), 2)
        
        # 地板精灵（浅灰色背景）
        floor_rect = pygame.Rect(self.size * 4, 0, self.size, self.size)
        pygame.draw.rect(self.sheet, (240, 240, 240), floor_rect)  # 浅灰色
        # 添加细微的网格线
        for i in range(4):
            x = floor_rect.left + i * self.size//4
            pygame.draw.line(self.sheet, (220, 220, 220), 
                            (x, floor_rect.top), 
                            (x, floor_rect.bottom), 1)
            y = floor_rect.top + i * self.size//4
            pygame.draw.line(self.sheet, (220, 220, 220), 
                            (floor_rect.left, y), 
                            (floor_rect.right, y), 1)
    
    def get_sprite(self, index):
        return self.sheet.subsurface(pygame.Rect(index * self.size, 0, self.size, self.size))
    
    @property
    def player(self):
        return self.get_sprite(0)
    
    @property
    def box(self):
        return self.get_sprite(1)
    
    @property
    def wall(self):
        return self.get_sprite(2)
    
    @property
    def target(self):
        return self.get_sprite(3)
    
    @property
    def floor(self):
        return self.get_sprite(4)
