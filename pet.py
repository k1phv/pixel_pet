import json
import os
import random
from constants import SAVE_FILE, FOOD_TYPES, WEATHER_TYPES
from achievements import AchievementManager
from logger import logger

class Pet:
    def __init__(self):
        self.name = "Пиксель"
        self.setup_defaults()
        self.achievements = AchievementManager()
        self.load_progress()
        logger.log(f"Питомец {self.name} инициализирован.")

    def setup_defaults(self):
        """Установка начальных параметров"""
        self.hunger = 100
        self.energy = 100
        self.happiness = 100
        self.is_alive = True
        self.state = "normal"
        self.age_ticks = 0
        self.coins = 50
        self.level = 1
        self.xp = 0
        self.color_name = "orange"
        self.unlocked_colors = ["orange"]
        self.inventory = {} 
        self.food_eaten = 0
        self.current_weather = "Солнечно"

    def reset(self):
        """Метод для бесплатного воскрешения (рестарт параметров)"""
        self.hunger = 100
        self.energy = 100
        self.happiness = 100
        self.is_alive = True
        self.state = "normal"
        logger.log(f"Питомец {self.name} был воскрешен бесплатно.")

    def save_progress(self):
        data = {
            "name": self.name, "hunger": self.hunger, "energy": self.energy,
            "happiness": self.happiness, "is_alive": self.is_alive,
            "age_ticks": self.age_ticks, "coins": self.coins, 
            "level": self.level, "xp": self.xp, "color": self.color_name,
            "unlocked": self.unlocked_colors, "inv": self.inventory,
            "food_eaten": self.food_eaten, "weather": self.current_weather,
            "ach_list": self.achievements.unlocked
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_progress(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    self.name = d.get("name", "Пиксель")
                    self.hunger = d.get("hunger", 100)
                    self.energy = d.get("energy", 100)
                    self.happiness = d.get("happiness", 100)
                    self.is_alive = d.get("is_alive", True)
                    self.age_ticks = d.get("age_ticks", 0)
                    self.coins = d.get("coins", 50)
                    self.level = d.get("level", 1)
                    self.xp = d.get("xp", 0)
                    self.color_name = d.get("color", "orange")
                    self.unlocked_colors = d.get("unlocked", ["orange"])
                    self.inventory = d.get("inv", {})
                    self.food_eaten = d.get("food_eaten", 0)
                    self.current_weather = d.get("weather", "Солнечно")
                    self.achievements.unlocked = d.get("ach_list", [])
            except Exception as e:
                logger.log(f"Ошибка загрузки: {e}", "ERROR")

    def add_xp(self, amount):
        self.xp += amount
        if self.xp >= self.level * 100:
            self.xp -= self.level * 100
            self.level += 1
            logger.log(f"Уровень повышен! Теперь уровень: {self.level}")
            return True
        return False

    def eat_from_inventory(self, item_name):
        if self.inventory.get(item_name, 0) > 0:
            data = FOOD_TYPES[item_name]
            self.inventory[item_name] -= 1
            self.hunger += data["hunger"]
            self.energy += data["energy"]
            self.food_eaten += 1
            if item_name == "🍰 Торт": self.happiness += 30
            self._cap_stats()
            self.state = "happy"
            return f"{self.name} съел {item_name}!"
        return "Предмета нет в рюкзаке."

    def tick(self):
        if not self.is_alive: return None
        
        mod = WEATHER_TYPES[self.current_weather]["drain_mod"]
        self.hunger -= 1 * mod
        self.energy -= 1 * mod
        self.happiness -= 1 * mod
        self.age_ticks += 1
        
        if random.random() < 0.03:
            self.current_weather = random.choice(list(WEATHER_TYPES.keys()))
            logger.log(f"Погода изменилась: {self.current_weather}")

        self._cap_stats()
        if self.hunger <= 0 or self.energy <= 0 or self.happiness <= 0:
            self.is_alive = False
            self.state = "dead"
            logger.log(f"Питомец {self.name} погиб от нехватки ресурсов.", "WARNING")
            
        return self.achievements.check(self)

    def _cap_stats(self):
        self.hunger = max(0, min(100, self.hunger))
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))

    def get_emotion_icon(self):
        if not self.is_alive:
            return "👻"
        if self.hunger < 30:
            return "🍎?" # Хочет есть
        if self.energy < 30:
            return "💤"  # Хочет спать
        if self.happiness < 30:
            return "😢"  # Грустит
        if self.happiness > 85:
            return "❤️"  # Счастлив
        if self.state == "happy":
            return "✨"  # Радость после действия
        return "🙂"      # Всё в порядке