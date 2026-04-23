SAVE_FILE = "pet_save_v6.json"

COLORS = {
    "orange": {"main": "#ffb74d", "light": "#ffe9ca"},
    "blue": {"main": "#64b5f6", "light": "#e3f2fd"},
    "green": {"main": "#81c784", "light": "#e8f5e9"},
    "gold": {"main": "#ffd700", "light": "#fff9c4"},
    "purple": {"main": "#ba68c8", "light": "#f3e5f5"}
}

FOOD_TYPES = {
    "🍎 Яблоко": {"cost": 10, "hunger": 20, "energy": 5, "desc": "Полезно и дешево"},
    "🍔 Бургер": {"cost": 25, "hunger": 50, "energy": -10, "desc": "Сытно, но клонит в сон"},
    "☕ Кофе": {"cost": 15, "hunger": 5, "energy": 40, "desc": "Заряд бодрости"},
    "🍰 Торт": {"cost": 40, "hunger": 30, "energy": 10, "desc": "Счастье (+30)"},
    "🧪 Витамин": {"cost": 100, "hunger": 0, "energy": 100, "desc": "Полное восстановление"}
}

ACHIEVEMENTS = {
    "rich": {"title": "Богач", "desc": "Накопить 200 монет", "goal": 200},
    "survivor": {"title": "Выживший", "desc": "Прожить 50 тиков", "goal": 50},
    "glutton": {"title": "Обжора", "desc": "Съесть 10 предметов", "goal": 10}
}

WEATHER_TYPES = {
    "Солнечно": {"drain_mod": 1.0, "icon": "☀️"},
    "Дождь": {"drain_mod": 1.5, "icon": "🌧️"},
    "Гроза": {"drain_mod": 2.0, "icon": "⚡"},
    "Туман": {"drain_mod": 0.8, "icon": "🌫️"}
}