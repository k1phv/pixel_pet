import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
import time

SAVE_FILE = "pet_save_v4.json"

# ==========================================
# 1. КОНСТАНТЫ И НАСТРОЙКИ
# ==========================================
COLORS = {
    "orange": {"main": "#ffb74d", "light": "#ffe9ca"},
    "blue": {"main": "#64b5f6", "light": "#e3f2fd"},
    "green": {"main": "#81c784", "light": "#e8f5e9"},
    "gold": {"main": "#ffd700", "light": "#fff9c4"},
    "purple": {"main": "#ba68c8", "light": "#f3e5f5"}
}

FOOD_TYPES = {
    "🍎 Яблоко": {"cost": 10, "hunger": 20, "energy": 5, "desc": "Полезно и дешево"},
    "🍔 Бургер": {"cost": 25, "hunger": 50, "energy": -10, "desc": "Очень сытно, но тянет в сон"},
    "☕ Кофе": {"cost": 15, "hunger": 5, "energy": 40, "desc": "Заряд бодрости на весь день"},
    "🍰 Торт": {"cost": 40, "hunger": 30, "energy": 10, "desc": "Дарит много счастья (+30)"}
}

# ==========================================
# 2. ЯДРО ПИТОМЦА
# ==========================================
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
        self.inventory = {} # Формат: {"Яблоко": 2, "Кофе": 1}
        
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
                    self.hunger, self.energy = d.get("hunger"), d.get("energy")
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
        
        # Рандомные события
        if random.random() < 0.05: # 5% шанс события
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

# ==========================================
# 3. ИНТЕРФЕЙС И МИНИ-ИГРЫ
# ==========================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Pet Ultra v4.0")
        self.root.geometry("550x850")
        self.root.configure(bg="#f5f5f5")
        
        self.pet = Pet()
        self.setup_ui()
        self.update_ui()
        self.game_loop()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        # Верхний статус
        self.top_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        self.top_frame.pack(fill=tk.X)
        
        self.name_label = tk.Label(self.top_frame, text=self.pet.name, fg="white", bg="#2c3e50", font=("Verdana", 14, "bold"))
        self.name_label.pack()
        
        self.xp_bar = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.xp_bar.pack(pady=5)
        
        # Статы
        self.info_panel = tk.Frame(self.root, bg="#f5f5f5")
        self.info_panel.pack(pady=10)
        
        self.lbl_coins = tk.Label(self.info_panel, text=f"💰 {self.pet.coins}", font=("Arial", 12, "bold"), fg="#d4af37")
        self.lbl_coins.grid(row=0, column=0, padx=20)
        
        self.lbl_level = tk.Label(self.info_panel, text=f"Уровень: {self.pet.level}", font=("Arial", 12))
        self.lbl_level.grid(row=0, column=1, padx=20)

        # Холст питомца
        self.canvas = tk.Canvas(self.root, width=320, height=320, bg="white", highlightthickness=1, highlightbackground="#ddd")
        self.canvas.pack(pady=10)

        # Прогресс-бары (динамическое создание)
        self.bars = {}
        for stat in ["Голод", "Энергия", "Счастье"]:
            frame = tk.Frame(self.root, bg="#f5f5f5")
            frame.pack(fill=tk.X, padx=80)
            tk.Label(frame, text=stat, width=10, anchor='w', bg="#f5f5f5").pack(side=tk.LEFT)
            bar = ttk.Progressbar(frame, length=250, mode='determinate')
            bar.pack(side=tk.RIGHT, pady=3)
            self.bars[stat] = bar

        # Кнопочная панель (Сетка)
        self.btn_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.btn_frame.pack(pady=20)
        
        btns = [
            ("🍕 Магазин", self.open_shop, 0, 0),
            ("🎒 Рюкзак", self.open_inventory, 0, 1),
            ("🎮 Игры", self.open_games, 1, 0),
            ("👕 Стиль", self.open_wardrobe, 1, 1)
        ]
        
        for text, cmd, r, c in btns:
            tk.Button(self.btn_frame, text=text, width=18, height=2, font=("Arial", 10, "bold"),
                      command=cmd, bg="white", relief=tk.GROOVE).grid(row=r, column=c, padx=5, pady=5)

        # Лог событий
        self.log_box = tk.Listbox(self.root, height=4, width=60, font=("Consolas", 9), bg="#eee")
        self.log_box.pack(pady=10)

    # --- МИНИ-ИГРА: Угадай число ---
    def open_games(self):
        game_win = tk.Toplevel(self.root)
        game_win.title("Мини-игры")
        game_win.geometry("300x350")
        
        tk.Label(game_win, text="Угадай число (1-10)", font=("Arial", 12, "bold")).pack(pady=10)
        
        entry = tk.Entry(game_win, font=("Arial", 14))
        entry.pack(pady=10)
        
        def play():
            try:
                val = int(entry.get())
                secret = random.randint(1, 10)
                if val == secret:
                    reward = 20
                    self.pet.coins += reward
                    messagebox.showinfo("Победа!", f"Верно! Это было {secret}. Вы получили {reward} 💰")
                else:
                    messagebox.showwarning("Мимо", f"Нет, это было {secret}. Попробуйте еще раз!")
                self.pet.happiness += 10
                self.pet.energy -= 5
                self.update_ui()
                game_win.destroy()
            except: pass

        tk.Button(game_win, text="Проверить удачу!", command=play, bg="#a5d6a7").pack(pady=10)

    # --- ИНВЕНТАРЬ ---
    def open_inventory(self):
        inv_win = tk.Toplevel(self.root)
        inv_win.title("Ваш рюкзак")
        inv_win.geometry("300x400")
        
        if not self.pet.inventory or sum(self.pet.inventory.values()) == 0:
            tk.Label(inv_win, text="Рюкзак пуст...").pack(pady=20)
            return

        for item, count in self.pet.inventory.items():
            if count > 0:
                f = tk.Frame(inv_win)
                f.pack(fill=tk.X, padx=20, pady=5)
                tk.Label(f, text=f"{item} (x{count})").pack(side=tk.LEFT)
                tk.Button(f, text="Съесть", command=lambda i=item: self.use_item(i, inv_win)).pack(side=tk.RIGHT)

    def use_item(self, item, win):
        msg = self.pet.eat_from_inventory(item)
        self.log(msg)
        self.update_ui()
        win.destroy()

    def open_shop(self):
        shop = tk.Toplevel(self.root)
        shop.title("Магазин еды")
        shop.geometry("350x450")
        
        for name, data in FOOD_TYPES.items():
            f = tk.LabelFrame(shop, text=name, padx=10, pady=5)
            f.pack(fill=tk.X, padx=15, pady=5)
            tk.Label(f, text=data["desc"], font=("Arial", 8, "italic")).pack(side=tk.LEFT)
            tk.Button(f, text=f"Купить ({data['cost']}💰)", 
                      command=lambda n=name: self.buy_logic(n)).pack(side=tk.RIGHT)

    def buy_logic(self, name):
        cost = FOOD_TYPES[name]["cost"]
        if self.pet.coins >= cost:
            self.pet.coins -= cost
            self.pet.inventory[name] = self.pet.inventory.get(name, 0) + 1
            self.log(f"Куплено: {name}. Добавлено в рюкзак.")
            self.update_ui()
        else:
            messagebox.showerror("Ошибка", "Маловато золотишка!")

    def open_wardrobe(self):
        w = tk.Toplevel(self.root)
        w.title("Гардероб")
        for color_name, vals in COLORS.items():
            f = tk.Frame(w, bg=vals["light"], pady=5)
            f.pack(fill=tk.X)
            if color_name in self.pet.unlocked_colors:
                btn_text = "Надеть"
                cmd = lambda n=color_name: self.set_color(n)
            else:
                btn_text = "Купить (100 💰)"
                cmd = lambda n=color_name: self.buy_color(n)
            
            tk.Label(f, text=color_name.upper(), bg=vals["light"], width=15).pack(side=tk.LEFT)
            tk.Button(f, text=btn_text, command=cmd).pack(side=tk.RIGHT, padx=10)

    def set_color(self, name):
        self.pet.color_name = name
        self.log(f"Цвет изменен на {name}")
        self.update_ui()

    def buy_color(self, name):
        if self.pet.coins >= 100:
            self.pet.coins -= 100
            self.pet.unlocked_colors.append(name)
            self.set_color(name)
        else: self.log("Нужно больше монет!")

    def log(self, msg):
        self.log_box.insert(0, f"[{time.strftime('%H:%M')}] {msg}")

    def update_ui(self):
        self.bars["Голод"]['value'] = self.pet.hunger
        self.bars["Энергия"]['value'] = self.pet.energy
        self.bars["Счастье"]['value'] = self.pet.happiness
        self.xp_bar['value'] = (self.pet.xp / (self.pet.level * 100)) * 100
        self.lbl_coins.config(text=f"💰 {self.pet.coins}")
        self.lbl_level.config(text=f"Уровень: {self.pet.level}")
        self.draw_pet()

    def draw_pet(self):
        self.canvas.delete("all")
        if not self.pet.is_alive:
            self.canvas.create_text(160, 160, text="👻", font=("Arial", 80))
            return
        
        color = COLORS[self.pet.color_name]["main"]
        # Рисуем тело (упрощенный пиксельный стиль через круги и квадраты)
        self.canvas.create_oval(80, 100, 240, 260, fill=color, outline="#333", width=2)
        # Глаза
        self.canvas.create_oval(110, 140, 130, 160, fill="white")
        self.canvas.create_oval(190, 140, 210, 160, fill="white")
        # Зрачки (меняются от состояния)
        p_y = 155 if self.pet.state == "sad" else 150
        self.canvas.create_oval(118, p_y-2, 122, p_y+2, fill="black")
        self.canvas.create_oval(198, p_y-2, 202, p_y+2, fill="black")

    def game_loop(self):
        if self.pet.is_alive:
            event = self.pet.tick()
            if event: self.log(event)
            self.update_ui()
            self.root.after(5000, self.game_loop)

    def on_close(self):
        self.pet.save_progress()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    app = App(root)
    root.mainloop()