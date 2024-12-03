import json
import os

class HighScores:
    def __init__(self):
        self.scores_file = "highscores.json"
        self.scores = self.load_scores()
    
    def load_scores(self):
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except:
                return self.create_empty_scores()
        return self.create_empty_scores()
    
    def create_empty_scores(self):
        return {str(level): {"moves": float('inf'), "pushes": float('inf')} 
                for level in range(100)}  # Support up to 100 levels
    
    def save_scores(self):
        with open(self.scores_file, 'w') as f:
            json.dump(self.scores, f)
    
    def update_score(self, level, moves, pushes):
        level_str = str(level)
        if level_str not in self.scores:
            self.scores[level_str] = {"moves": float('inf'), "pushes": float('inf')}
        
        score_updated = False
        if moves < self.scores[level_str]["moves"]:
            self.scores[level_str]["moves"] = moves
            score_updated = True
        if pushes < self.scores[level_str]["pushes"]:
            self.scores[level_str]["pushes"] = pushes
            score_updated = True
        
        if score_updated:
            self.save_scores()
        return score_updated
    
    def get_level_best(self, level):
        level_str = str(level)
        if level_str in self.scores:
            return self.scores[level_str]
        return {"moves": float('inf'), "pushes": float('inf')}
