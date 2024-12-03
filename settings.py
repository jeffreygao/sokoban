import json
import os

class Settings:
    def __init__(self):
        self.settings_file = "settings.json"
        self.default_settings = {
            "music_volume": 0.5,
            "effects_volume": 0.7,
            "music_enabled": True,
            "effects_enabled": True,
            "fullscreen": False,
            "animation_speed": 1.0,
            "show_move_counter": True,
            "show_push_counter": True,
            "show_timer": True,
            "controls": {
                "up": "UP",
                "down": "DOWN",
                "left": "LEFT",
                "right": "RIGHT",
                "undo": "z",
                "reset": "r",
                "menu": "ESCAPE"
            },
            "theme": "classic",
            "language": "zh_CN"
        }
        self.current_settings = self.load_settings()
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # 合并默认设置和加载的设置
                    merged_settings = self.default_settings.copy()
                    merged_settings.update(loaded_settings)
                    return merged_settings
            except:
                print("无法加载设置文件,使用默认设置")
        return self.default_settings.copy()
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=4, ensure_ascii=False)
        except:
            print("无法保存设置")
    
    def get_setting(self, key):
        return self.current_settings.get(key, self.default_settings.get(key))
    
    def set_setting(self, key, value):
        if key in self.default_settings:
            self.current_settings[key] = value
            self.save_settings()
    
    def reset_to_default(self):
        self.current_settings = self.default_settings.copy()
        self.save_settings()
    
    def get_control(self, action):
        return self.current_settings["controls"].get(action, 
                                                   self.default_settings["controls"].get(action))
    
    def set_control(self, action, key):
        if action in self.default_settings["controls"]:
            self.current_settings["controls"][action] = key
            self.save_settings()
