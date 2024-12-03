import pygame
import os

class SoundManager:
    def __init__(self):
        self.music_volume = 0.5
        self.effects_volume = 0.7
        self.current_music = None
        self.music_enabled = True
        self.effects_enabled = True
        
        # 初始化音效
        self.sounds = {}
        self._load_sound_effects()
        
        # 初始化背景音乐
        self.music_tracks = {
            'menu': 'menu_music.mp3',
            'game': 'game_music.mp3',
            'victory': 'victory_music.mp3'
        }
    
    def _load_sound_effects(self):
        sound_files = {
            'move': 'move.wav',
            'push': 'push.wav',
            'complete': 'complete.wav',
            'undo': 'undo.wav',
            'achievement': 'achievement.wav'
        }
        
        for name, file in sound_files.items():
            try:
                path = os.path.join('assets', file)
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.effects_volume)
            except:
                print(f"无法加载音效: {file}")
    
    def play_music(self, track_name):
        if not self.music_enabled:
            return
            
        if track_name in self.music_tracks:
            try:
                path = os.path.join('assets', self.music_tracks[track_name])
                if os.path.exists(path):
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(-1)  # -1表示循环播放
                    self.current_music = track_name
            except:
                print(f"无法播放音乐: {track_name}")
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None
    
    def play_sound(self, sound_name):
        if not self.effects_enabled:
            return
            
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        elif self.current_music:
            self.play_music(self.current_music)
    
    def toggle_effects(self):
        self.effects_enabled = not self.effects_enabled
    
    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_effects_volume(self, volume):
        self.effects_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.effects_volume)
