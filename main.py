import tkinter as tk
from tkinter import ttk
import random
import json
import os

SAVE_FILE = "pet_save.json"

# ==========================================
# 1. КЛАСС ПИТОМЦА (Логика)
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
        self.coins = 10 # Стартовый капитал: 10 монеток!

        self.load_progress()

    def save_progress(self):
        data = {
            "hunger": self.hunger, "energy": self.energy,
            "happiness": self.happiness, "is_alive": self.is_alive,
            "state": self.state, "age_ticks": self.age_ticks,
            "coins": self.coins # Сохраняем монетки
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_progress(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.hunger = data.get("hunger", 50)
                self.energy = data.get("energy", 80)
                self.happiness = data.get("happiness", 50)
                self.is_alive = data.get("is_alive", True)
                self.state = data.get("state", "normal")
                self.age_ticks = data.get("age_ticks", 0)
                self.coins = data.get("coins", 10) # Загружаем монетки

    # НОВЫЙ МЕТОД: Покупка еды
    def buy_food(self, food_name, cost, hunger_boost, energy_boost):
        if not self.is_alive: return "Питомец мертв..."
        if self.coins < cost:
            return f"Не хватает монет! Нужно {cost} 💰."
        
        self.coins -= cost
        self.hunger += hunger_boost
        self.energy += energy_boost
        self._cap_stats()
        self.state = "happy"
        return f"Куплено: {food_name}. Ом-ном-ном!"

    def play(self):
        if not self.is_alive: return "Питомец мертв..."
        if self.energy < 20: return f"{self.name} слишком устал!"
        
        earned_coins = random.randint(2, 6) # Случайный заработок от 2 до 6 монет
        self.coins += earned_coins
        
        self.happiness += 20
        self.energy -= 15
        self.hunger -= 10
        self._cap_stats()
        self.state = "happy"
        return f"Поиграли! Вы нашли {earned_coins} 💰."

    def sleep(self):
        if not self.is_alive: return "Питомец мертв..."
        self.energy += 30
        self.hunger -= 15
        self._cap_stats()
        self.state = "sleeping"
        return f"{self.name} поспал и полон сил."

    def tick(self):
        if not self.is_alive: return
            
        self.hunger -= random.randint(1, 3)
        self.energy -= random.randint(1, 2)
        self.happiness -= random.randint(1, 3)
        self.age_ticks += 1
        self._cap_stats()

        if self.hunger <= 0 or self.energy <= 0 or self.happiness <= 0:
            self.is_alive = False
            self.state = "dead"
        elif self.hunger < 30 or self.happiness < 30:
            self.state = "sad"
        elif self.state not in ["sleeping", "happy"]:
            self.state = "normal"

    def _cap_stats(self):
        self.hunger = max(0, min(100, self.hunger))
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))


# ==========================================
# 2. ПИКСЕЛЬНЫЕ АРТЫ
# ==========================================
FRAMES = {
    "normal": ["....bbbb....", "..bbccccbb..", ".bccccccccb.", "bccbbccbbccb", "bccwwccwwccb", "bccbbccbbccb", "bpccccccccpb", ".bccbbbbccb.", "..bbccccbb..", "....bbbb...."],
    "happy": ["....bbbb....", "..bbccccbb..", ".bccccccccb.", "bccbbccbbccb", "bccccccccccb", "bccccccccccb", "bpccbbbbccpb", ".bccbwwbccb.", "..bbccccbb..", "....bbbb...."],
    "sad": ["....bbbb....", "..bbccccbb..", ".bccccccccb.", "bccbbccbbccb", "bccccccccccb", "bccccccccccb", "bpccccccccpb", ".bccbbbbccb.", "..bbccccbb..", "....bbbb...."],
    "sleeping": ["....bbbb....", "..bbccccbb..", ".bccccccccb.", "bccccccccccb", "bccbbccbbccb", "bccccccccccb", "bccccccccccb", ".bccbbbbccb.", "..bbccccbb..", "....bbbb...."],
    "dead": ["....bbbb....", "..bbbbbbbb..", ".bbbbbbbbbb.", "bbbwbbwwbbwb", "bbbwbwbwbwwb", "bbbwbbwwbbwb", "bbbbbbbbbbbb", ".bbbbbbbbbb.", "..bbbbbbbb..", "....bbbb...."]
}

# ==========================================
# 3. КЛАСС ПРИЛОЖЕНИЯ (Графический интерфейс)
# ==========================================
class PetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Pet - Твой виртуальный друг")
        self.root.geometry("450x670")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.pet = Pet("Пиксель")
        
        self.setup_ui()
        self.update_ui()
        self.game_loop()

    def setup_ui(self):
        # Фрейм для информации (Возраст и Монеты)
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=40, pady=(15, 0))
        
        self.age_label = ttk.Label(info_frame, text="Возраст: 0 дн.", font=("Arial", 11, "bold"))
        self.age_label.pack(side=tk.LEFT)
        
        self.coins_label = ttk.Label(info_frame, text="Монеты: 0 💰", font=("Arial", 11, "bold"), foreground="#d4af37")
        self.coins_label.pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(self.root, width=240, height=240, bg="#e0f7fa", highlightthickness=2)
        self.canvas.pack(pady=10)
        
        stats_frame = ttk.Frame(self.root)
        stats_frame.pack(fill=tk.X, padx=40, pady=5)
        
        ttk.Label(stats_frame, text="Сытость:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bar_hunger = ttk.Progressbar(stats_frame, length=200, mode='determinate')
        self.bar_hunger.grid(row=0, column=1, padx=10)
        
        ttk.Label(stats_frame, text="Энергия:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.bar_energy = ttk.Progressbar(stats_frame, length=200, mode='determinate')
        self.bar_energy.grid(row=1, column=1, padx=10)
        
        ttk.Label(stats_frame, text="Счастье:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.bar_happiness = ttk.Progressbar(stats_frame, length=200, mode='determinate')
        self.bar_happiness.grid(row=2, column=1, padx=10)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)
        
        # Кнопка кормить теперь открывает МАГАЗИН
        self.btn_shop = ttk.Button(btn_frame, text="🛒 Магазин", command=self.open_shop)
        self.btn_shop.grid(row=0, column=0, padx=5, ipady=5)
        
        self.btn_play = ttk.Button(btn_frame, text="🎾 Играть", command=self.action_play)
        self.btn_play.grid(row=0, column=1, padx=5, ipady=5)
        
        self.btn_sleep = ttk.Button(btn_frame, text="🛏 Спать", command=self.action_sleep)
        self.btn_sleep.grid(row=0, column=2, padx=5, ipady=5)
        
        self.log_text = tk.Text(self.root, height=5, width=45, state=tk.DISABLED, bg="#f5f5f5", font=("Arial", 10))
        self.log_text.pack(pady=10)

    # --- ЛОГИКА МАГАЗИНА ---
    def open_shop(self):
        """Открывает новое маленькое окно поверх основного."""
        if not self.pet.is_alive: return
        
        shop_win = tk.Toplevel(self.root)
        shop_win.title("Магазин еды")
        shop_win.geometry("260x220")
        shop_win.resizable(False, False)
        
        ttk.Label(shop_win, text="Что купим?", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Лямбда-функции нужны, чтобы передать параметры еды в кнопку
        btn1 = ttk.Button(shop_win, text="🍎 Яблоко (5 💰) [+15 сытость]", 
                          command=lambda: self.buy_and_close(shop_win, "🍎 Яблоко", 5, 15, 0))
        btn1.pack(pady=5, fill=tk.X, padx=20)
        
        btn2 = ttk.Button(shop_win, text="🍔 Бургер (15 💰) [+40 сыт, -5 эн.]", 
                          command=lambda: self.buy_and_close(shop_win, "🍔 Бургер", 15, 40, -5))
        btn2.pack(pady=5, fill=tk.X, padx=20)
        
        btn3 = ttk.Button(shop_win, text="☕ Кофе (10 💰) [+5 сыт, +25 эн.]", 
                          command=lambda: self.buy_and_close(shop_win, "☕ Кофе", 10, 5, 25))
        btn3.pack(pady=5, fill=tk.X, padx=20)

    def buy_and_close(self, window, name, cost, h_boost, e_boost):
        """Вызывает покупку и закрывает окно магазина."""
        result = self.pet.buy_food(name, cost, h_boost, e_boost)
        self.log(result)
        self.update_ui()
        window.destroy()

    # --- ПРОДОЛЖЕНИЕ ИНТЕРФЕЙСА ---
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def action_play(self):
        self.log(self.pet.play())
        self.update_ui()
        
    def action_sleep(self):
        self.log(self.pet.sleep())
        self.update_ui()

    def update_ui(self):
        self.bar_hunger['value'] = self.pet.hunger
        self.bar_energy['value'] = self.pet.energy
        self.bar_happiness['value'] = self.pet.happiness
        
        days = self.pet.age_ticks // 10 
        self.age_label.config(text=f"Возраст: {days} дн.")
        self.coins_label.config(text=f"Монеты: {self.pet.coins} 💰")
        
        if not self.pet.is_alive:
            self.btn_shop.config(state=tk.DISABLED)
            self.btn_play.config(state=tk.DISABLED)
            self.btn_sleep.config(state=tk.DISABLED)
            
        self.draw_pet()

    def draw_pet(self):
        self.canvas.delete("all")
        frame = FRAMES.get(self.pet.state, FRAMES["normal"])
        pixel_size, offset_x, offset_y = 20, 20, 20
        color_map = {'.': "", 'b': "#212121", 'w': "#ffffff", 'c': "#ffb74d", 'p': "#f48fb1"}
        
        for row_idx, row in enumerate(frame):
            for col_idx, char in enumerate(row):
                if char == '.': continue
                x1, y1 = offset_x + col_idx * pixel_size, offset_y + row_idx * pixel_size
                color = color_map.get(char, "black")
                self.canvas.create_rectangle(x1, y1, x1 + pixel_size, y1 + pixel_size, fill=color, outline=color)

    def game_loop(self):
        if self.pet.is_alive:
            self.pet.tick()
            self.update_ui()
            
            if not self.pet.is_alive:
                self.log("О нет! Пиксель отправился в лучший мир...")
                
            self.root.after(3000, self.game_loop)
            
            if self.pet.state in ["happy", "sleeping"]:
                self.pet.state = "normal"

    def on_closing(self):
        self.pet.save_progress()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PetApp(root)
    root.mainloop()