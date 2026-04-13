import json
import os
import random
from constants import SAVE_FILE, FOOD_TYPES

class Pet:
    def __init__(self):
        self.name = "Пиксель"
        self.hunger = 70
        self.energy = 70
        self.happiness = 70
        self.is_alive = True
        self.state = "normal"
        self.age_ticks = 0
        self.coins = 50
        self.level = 1
        self.xp = 0
        self.color_name = "orange"
        self.unlocked_colors = ["orange"]
        self.inventory = {} 
        
        self.load_progress()

    def save_progress(self):
        data = {
            "name": self.name, "hunger": self.hunger, "energy": self.energy,
            "happiness": self.happiness, "is_alive": self.is_alive,
            "age_ticks": self.age_ticks, "coins": self.coins, 
            "level": self.level, "xp": self.xp, "color": self.color_name,
            "unlocked": self.unlocked_colors, "inv": self.inventory
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_progress(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    self.name = d.get("name", "Пиксель")
                    self.hunger, self.energy = d.get("hunger")
                    self.happiness = d.get("happiness")
                    self.is_alive = d.get("is_alive")
                    self.age_ticks = d.get("age_ticks")
                    self.coins = d.get("coins")
                    self.level, self.xp = d.get("level"), d.get("xp")
                    self.color_name = d.get("color", "orange")
                    self.unlocked_colors = d.get("unlocked", ["orange"])
                    self.inventory = d.get("inv", {})
            except: pass

    def add_xp(self, amount):
        self.xp += amount
        if self.xp >= self.level * 100:
            self.xp = 0
            self.level += 1
            return True
        return False

    def eat_from_inventory(self, item_name):
        if self.inventory.get(item_name, 0) > 0:
            data = FOOD_TYPES[item_name]
            self.inventory[item_name] -= 1
            self.hunger += data["hunger"]
            self.energy += data["energy"]
            if item_name == "🍰 Торт": self.happiness += 30
            self._cap_stats()
            self.state = "happy"
            return f"{self.name} съел {item_name}!"
        return "Предмета нет в инвентаре."

    def tick(self):
        if not self.is_alive: return
        self.hunger -= 1
        self.energy -= 1
        self.happiness -= 1
        self.age_ticks += 1
        
        if random.random() < 0.05: 
            self.coins += 5
            return "Событие: Вы нашли 5 💰 на полу!"

        if self.hunger <= 0 or self.energy <= 0 or self.happiness <= 0:
            self.is_alive = False
            self.state = "dead"
        self._cap_stats()
        return None

    def _cap_stats(self):
        self.hunger = max(0, min(100, self.hunger))
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))