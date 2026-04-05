import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

SAVE_FILE = "pet_save.json"

# ==========================================
# 1. КЛАСС ПИТОМЦА (Расширенная логика)
# ==========================================
class Pet:
    def __init__(self, name):
        self.name = name
        self.hunger = 50
        self.energy = 80
        self.happiness = 50
        self.is_alive = True
        self.state = "normal"
        self.age_ticks = 0
        self.coins = 20
        self.level = 1
        self.xp = 0
        self.color_name = "orange" # Текущий цвет
        self.unlocked_colors = ["orange"] # Список купленных цветов

        self.load_progress()

    def save_progress(self):
        data = {
            "hunger": self.hunger, "energy": self.energy,
            "happiness": self.happiness, "is_alive": self.is_alive,
            "state": self.state, "age_ticks": self.age_ticks,
            "coins": self.coins, "level": self.level, "xp": self.xp,
            "color_name": self.color_name, "unlocked_colors": self.unlocked_colors
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_progress(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.hunger = data.get("hunger", 50)
                    self.energy = data.get("energy", 80)
                    self.happiness = data.get("happiness", 50)
                    self.is_alive = data.get("is_alive", True)
                    self.state = data.get("state", "normal")
                    self.age_ticks = data.get("age_ticks", 0)
                    self.coins = data.get("coins", 20)
                    self.level = data.get("level", 1)
                    self.xp = data.get("xp", 0)
                    self.color_name = data.get("color_name", "orange")
                    self.unlocked_colors = data.get("unlocked_colors", ["orange"])
            except: pass

    def add_xp(self, amount):
        """Система прокачки уровня."""
        self.xp += amount
        xp_needed = self.level * 50
        if self.xp >= xp_needed:
            self.xp -= xp_needed
            self.level += 1
            return True # Сигнал о повышении уровня
        return False

    def buy_food(self, food_name, cost, hunger_boost, energy_boost):
        if not self.is_alive: return "Питомец мертв..."
        if self.coins < cost: return f"Нужно {cost} 💰!"
        
        self.coins -= cost
        self.hunger += hunger_boost
        self.energy += energy_boost
        self.add_xp(5)
        self._cap_stats()
        self.state = "happy"
        return f"Куплено: {food_name}!"

    def play(self):
        if not self.is_alive: return "Питомец мертв..."
        if self.energy < 20: return "Слишком мало энергии!"
        
        earned = random.randint(5, 10)
        self.coins += earned
        self.energy -= 15
        self.hunger -= 10
        self.happiness += 25
        upgraded = self.add_xp(15)
        self._cap_stats()
        self.state = "happy"
        msg = f"Поиграли! +{earned} 💰"
        if upgraded: msg += " | НОВЫЙ УРОВЕНЬ!"
        return msg

    def sleep(self):
        if not self.is_alive: return "Питомец мертв..."
        self.energy += 40
        self.hunger -= 20
        self.add_xp(10)
        self._cap_stats()
        self.state = "sleeping"
        return "Питомец отдыхает..."

    def tick(self):
        if not self.is_alive: return
        self.hunger -= 2
        self.energy -= 1
        self.happiness -= 2
        self.age_ticks += 1
        self._cap_stats()

        if self.hunger <= 0 or self.energy <= 0 or self.happiness <= 0:
            self.is_alive = False
            self.state = "dead"
        elif self.hunger < 30: self.state = "sad"
        elif self.state not in ["sleeping", "happy"]: self.state = "normal"

    def _cap_stats(self):
        self.hunger = max(0, min(100, self.hunger))
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))

# ==========================================
# 2. ГРАФИЧЕСКИЕ ДАННЫЕ
# ==========================================
COLOR_PALETTE = {
    "orange": "#ffb74d", "blue": "#64b5f6", 
    "green": "#81c784", "gold": "#ffd700", "purple": "#ba68c8"
}

FRAMES = {
    "normal": ["....bbbb....", "..bbccccbb..", ".bccccccccb.", "bccbbccbbccb", "bccwwccwwccb", "bccbbccbbccb", "bpccccccccpb", ".bccbbbbccb.", "..bbccccbb..", "....bbbb...."],
    "happy": ["....bbbb....", "..bbccccbb..", ".bccccccccb.", "bccbbccbbccb", "bccccccccccb", "bccccccccccb", "bpccbbbbccpb", ".bccbwwbccb.", "..bbccccbb..", "....bbbb...."],
    "sad": ["....bbbb....", "..bbccccbb..", ".bccccccccb.", "bccbbccbbccb", "bccccccccccb", "bccccccccccb", "bpccccccccpb", ".bccbbbbccb.", "..bbccccbb..", "....bbbb...."],
    "sleeping": ["....bbbb....", "..bbccccbb..", ".bccccccccb.", "bccccccccccb", "bccbbccbbccb", "bccccccccccb", "bccccccccccb", ".bccbbbbccb.", "..bbccccbb..", "....bbbb...."],
    "dead": ["....bbbb....", "..bbbbbbbb..", ".bbbbbbbbbb.", "bbbwbbwwbbwb", "bbbwbwbwbwwb", "bbbwbbwwbbwb", "bbbbbbbbbbbb", ".bbbbbbbbbb.", "..bbbbbbbb..", "....bbbb...."]
}

# ==========================================
# 3. ИНТЕРФЕЙС ПРИЛОЖЕНИЯ
# ==========================================
class PetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Pet v3.0 - Level Up Edition")
        self.root.geometry("500x750")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.pet = Pet("Пиксель")
        self.setup_ui()
        self.update_ui()
        self.game_loop()

    def setup_ui(self):
        # Верхняя панель (Уровень и XP)
        self.header = tk.Frame(self.root, bg="#333", height=40)
        self.header.pack(fill=tk.X)
        
        self.lvl_label = tk.Label(self.header, text=f"LVL {self.pet.level}", fg="white", bg="#333", font=("Courier", 12, "bold"))
        self.lvl_label.pack(side=tk.LEFT, padx=10)
        
        self.xp_bar = ttk.Progressbar(self.header, length=300, mode='determinate')
        self.xp_bar.pack(side=tk.LEFT, padx=10)

        # Панель ресурсов
        res_frame = tk.Frame(self.root)
        res_frame.pack(fill=tk.X, padx=20, pady=10)
        self.coin_label = tk.Label(res_frame, text=f"💰 {self.pet.coins}", font=("Arial", 14, "bold"), fg="#b8860b")
        self.coin_label.pack(side=tk.RIGHT)
        
        # Холст
        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Индикаторы
        self.create_stat_bar("Голод", "orange")
        self.create_stat_bar("Энергия", "blue")
        self.create_stat_bar("Счастье", "pink")

        # Кнопки (Сетка 2x2)
        btn_grid = tk.Frame(self.root)
        btn_grid.pack(pady=20)
        
        tk.Button(btn_grid, text="🛒 МАГАЗИН", width=15, height=2, command=self.open_shop, bg="#ffecb3").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_grid, text="🎾 ИГРАТЬ", width=15, height=2, command=self.action_play, bg="#c8e6c9").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_grid, text="👕 ГАРДЕРОБ", width=15, height=2, command=self.open_wardrobe, bg="#e1f5fe").grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_grid, text="💤 СПАТЬ", width=15, height=2, command=self.action_sleep, bg="#d1c4e9").grid(row=1, column=1, padx=5, pady=5)

        # Журнал
        self.log_box = tk.Text(self.root, height=4, width=50, state='disabled', font=("Arial", 9))
        self.log_box.pack(padx=20, pady=10)

    def create_stat_bar(self, name, color):
        f = tk.Frame(self.root)
        f.pack(fill=tk.X, padx=50)
        tk.Label(f, text=name, width=8, anchor='w').pack(side=tk.LEFT)
        bar = ttk.Progressbar(f, length=250, mode='determinate')
        bar.pack(side=tk.RIGHT, pady=2)
        setattr(self, f"bar_{name.lower()}", bar)

    def open_shop(self):
        shop = tk.Toplevel(self.root)
        shop.title("Магазин")
        shop.geometry("300x250")
        
        items = [("Яблоко", 10, 20, 0), ("Пицца", 25, 50, -10), ("Энергетик", 15, 5, 40)]
        for name, price, h, e in items:
            tk.Button(shop, text=f"{name} ({price}💰)\n+{h} сыт. / {e} энерг.", 
                      command=lambda n=name, p=price, h=h, e=e: self.buy_food_logic(n, p, h, e, shop)).pack(fill=tk.X, padx=20, pady=5)

    def buy_food_logic(self, n, p, h, e, win):
        self.log(self.pet.buy_food(n, p, h, e))
        self.update_ui()
        win.destroy()

    def open_wardrobe(self):
        w = tk.Toplevel(self.root)
        w.title("Гардероб")
        w.geometry("300x300")
        
        for name, hex_code in COLOR_PALETTE.items():
            state = "ВЫБРАТЬ" if name in self.pet.unlocked_colors else f"КУПИТЬ (50💰)"
            btn = tk.Button(w, text=f"{name.upper()}\n{state}", bg=hex_code,
                            command=lambda n=name: self.change_color_logic(n, w))
            btn.pack(fill=tk.X, padx=20, pady=5)

    def change_color_logic(self, name, win):
        if name in self.pet.unlocked_colors:
            self.pet.color_name = name
            self.log(f"Цвет изменен на {name}!")
        elif self.pet.coins >= 50:
            self.pet.coins -= 50
            self.pet.unlocked_colors.append(name)
            self.pet.color_name = name
            self.log(f"Куплен новый цвет: {name}!")
        else:
            self.log("Недостаточно монет!")
        self.update_ui()
        win.destroy()

    def log(self, msg):
        self.log_box.config(state='normal')
        self.log_box.insert('1.0', msg + "\n")
        self.log_box.config(state='disabled')

    def action_play(self): self.log(self.pet.play()); self.update_ui()
    def action_sleep(self): self.log(self.pet.sleep()); self.update_ui()

    def update_ui(self):
        self.bar_голод['value'] = self.pet.hunger
        self.bar_энергия['value'] = self.pet.energy
        self.bar_счастье['value'] = self.pet.happiness
        self.xp_bar['value'] = (self.pet.xp / (self.pet.level * 50)) * 100
        self.lvl_label.config(text=f"LVL {self.pet.level}")
        self.coin_label.config(text=f"💰 {self.pet.coins}")
        self.draw_pet()

    def draw_pet(self):
        self.canvas.delete("all")
        f = FRAMES.get(self.pet.state, FRAMES["normal"])
        ps = 25
        c_map = {'.':"", 'b':"#222", 'w':"#fff", 'c':COLOR_PALETTE[self.pet.color_name], 'p':"#ff80ab"}
        for r_idx, row in enumerate(f):
            for c_idx, char in enumerate(row):
                if char in c_map and c_map[char]:
                    x, y = c_idx*ps+25, r_idx*ps+25
                    self.canvas.create_rectangle(x, y, x+ps, y+ps, fill=c_map[char], outline=c_map[char])

    def game_loop(self):
        if self.pet.is_alive:
            self.pet.tick()
            self.update_ui()
            self.root.after(4000, self.game_loop)

    def on_closing(self):
        self.pet.save_progress()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PetApp(root)
    root.mainloop()