from constants import ACHIEVEMENTS

class AchievementManager:
    def __init__(self, unlocked=None):
        self.unlocked = unlocked if unlocked else []

    def check(self, pet):
        new_unlocked = []
        
        if "rich" not in self.unlocked and pet.coins >= ACHIEVEMENTS["rich"]["goal"]:
            new_unlocked.append("rich")
            
        if "survivor" not in self.unlocked and pet.age_ticks >= ACHIEVEMENTS["survivor"]["goal"]:
            new_unlocked.append("survivor")
            
        if "glutton" not in self.unlocked and getattr(pet, 'food_eaten', 0) >= ACHIEVEMENTS["glutton"]["goal"]:
            new_unlocked.append("glutton")

        self.unlocked.extend(new_unlocked)
        return new_unlocked