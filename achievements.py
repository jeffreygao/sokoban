import json
import os

class Achievement:
    def __init__(self, name, description, icon_char):
        self.name = name
        self.description = description
        self.icon_char = icon_char
        self.unlocked = False
        self.unlock_time = None

class AchievementManager:
    def __init__(self):
        self.achievements_file = "achievements.json"
        self.achievements = {
            "first_win": Achievement("First Steps", "Complete your first level", "🎯"),
            "speed_demon": Achievement("Speed Demon", "Complete a level under par moves", "⚡"),
            "perfect_push": Achievement("Perfect Push", "Complete a level under par pushes", "💪"),
            "master": Achievement("Master", "Complete all levels", "👑"),
            "undo_master": Achievement("Time Lord", "Use undo 50 times", "⏰"),
            "box_master": Achievement("Box Master", "Push 100 boxes", "📦"),
            "speed_run": Achievement("Speed Runner", "Complete 3 levels in a row under par", "🏃"),
            "no_undo": Achievement("Pure Skill", "Complete a level without using undo", "🎮"),
            "all_par": Achievement("Par Excellence", "Beat all par scores in a level", "🌟"),
            "legend": Achievement("Legend", "Complete the Legend level", "🏆")
        }
        self.load_achievements()
        
        # Statistics for tracking achievements
        self.stats = {
            "total_pushes": 0,
            "total_undos": 0,
            "levels_under_par": 0,
            "consecutive_under_par": 0
        }
    
    def load_achievements(self):
        if os.path.exists(self.achievements_file):
            try:
                with open(self.achievements_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if key in self.achievements:
                            self.achievements[key].unlocked = value.get("unlocked", False)
                            self.achievements[key].unlock_time = value.get("unlock_time", None)
            except:
                print("Could not load achievements")
    
    def save_achievements(self):
        data = {
            key: {
                "unlocked": ach.unlocked,
                "unlock_time": ach.unlock_time
            } for key, ach in self.achievements.items()
        }
        with open(self.achievements_file, 'w') as f:
            json.dump(data, f)
    
    def unlock_achievement(self, achievement_id):
        if achievement_id in self.achievements and not self.achievements[achievement_id].unlocked:
            import time
            self.achievements[achievement_id].unlocked = True
            self.achievements[achievement_id].unlock_time = time.time()
            self.save_achievements()
            return self.achievements[achievement_id]
        return None
    
    def check_level_complete(self, level, moves, pushes, used_undo, par_moves, par_pushes):
        achievements_unlocked = []
        
        # First win
        if not self.achievements["first_win"].unlocked:
            achievements_unlocked.append(self.unlock_achievement("first_win"))
        
        # Speed demon
        if moves <= par_moves:
            self.stats["levels_under_par"] += 1
            self.stats["consecutive_under_par"] += 1
            achievements_unlocked.append(self.unlock_achievement("speed_demon"))
        else:
            self.stats["consecutive_under_par"] = 0
        
        # Perfect push
        if pushes <= par_pushes:
            achievements_unlocked.append(self.unlock_achievement("perfect_push"))
        
        # Speed run
        if self.stats["consecutive_under_par"] >= 3:
            achievements_unlocked.append(self.unlock_achievement("speed_run"))
        
        # No undo
        if not used_undo:
            achievements_unlocked.append(self.unlock_achievement("no_undo"))
        
        # All par
        if moves <= par_moves and pushes <= par_pushes:
            achievements_unlocked.append(self.unlock_achievement("all_par"))
        
        # Legend
        if level == 9:  # Level 10 (0-based index)
            achievements_unlocked.append(self.unlock_achievement("legend"))
        
        return [a for a in achievements_unlocked if a is not None]
    
    def update_stats(self, stat_type):
        self.stats[stat_type] += 1
        
        # Check stat-based achievements
        if stat_type == "total_pushes" and self.stats["total_pushes"] >= 100:
            return self.unlock_achievement("box_master")
        elif stat_type == "total_undos" and self.stats["total_undos"] >= 50:
            return self.unlock_achievement("undo_master")
        return None
    
    def get_all_achievements(self):
        return self.achievements
    
    def get_unlocked_achievements(self):
        return [ach for ach in self.achievements.values() if ach.unlocked]
    
    def get_locked_achievements(self):
        return [ach for ach in self.achievements.values() if not ach.unlocked]
