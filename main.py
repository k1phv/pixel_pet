import tkinter as tk
from tkinter import ttk
import random
import json  # Библиотека для сохранений
import os    # Библиотека для проверки файлов

SAVE_FILE = "pet_save.json" # Имя файла, где будут лежать сохранения

# ==========================================
# 1. КЛАСС ПИТОМЦА (Логика + Сохранения)
# ==========================================
class Pet:
    def __init__(self, name):
        self.name = name
        self.hunger = 50
        self.energy = 80
        self.happiness = 50
        self.is_alive = True
        self.state = "normal"
        self.age_ticks = 0 # Внутренние "часы" питомца

        self.load_progress() # При создании сразу пытаемся загрузить сохранение!

    def save_progress(self):
        """Сохраняет параметры в файл json."""
        data = {
            "hunger": self.hunger,
            "energy": self.energy,
            "happiness": self.happiness,
            "is_alive": self.is_alive,
            "state": self.state,
            "age_ticks": self.age_ticks
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_progress(self):
        """Загружает параметры из файла, если он существует."""
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.hunger = data.get("hunger", 50)
                self.energy = data.get("energy", 80)
                self.happiness = data.get("happiness", 50)
                self.is_alive = data.get("is_alive", True)
                self.state = data.get("state", "normal")
                self.age_ticks = data.get("age_ticks", 0)

    # --- Старые методы (без изменений) ---
    def feed(self):
        if not self.is_alive: return "Питомец мертв..."
        self.hunger += 20
        self.energy -= 5
        self._cap_stats()
        self.state = "happy"
        return f"Вы покормили {self.name}. Ом-ном-ном!"

    def play(self):
        if not self.is_alive: return "Питомец мертв..."
        if self.energy < 20: return f"{self.name} слишком устал для игр!"
        self.happiness += 20
        self.energy -= 15
        self.hunger -= 10
        self._cap_stats()
        self.state = "happy"
        return f"Вы поиграли с {self.name}. Ему весело!"

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
        self.age_ticks += 1 # Питомец становится старше!
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
# 2. ПИКСЕЛЬНЫЕ АРТЫ ДЛЯ ПИТОМЦА
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
        self.root.geometry("450x670") # Чуть увеличили окно
        self.root.resizable(False, False)
        
        # ПЕРЕХВАТ НАЖАТИЯ "КРЕСТИКА" ДЛЯ СОХРАНЕНИЯ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.pet = Pet("Пиксель")
        
        self.setup_ui()
        self.update_ui()
        self.game_loop()

    def setup_ui(self):
        # --- Текст с возрастом ---
        self.age_label = ttk.Label(self.root, text="Возраст: 0 дней", font=("Arial", 12, "bold"))
        self.age_label.pack(pady=(10, 0))

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
        
        self.btn_feed = ttk.Button(btn_frame, text="🍖 Кормить", command=self.action_feed)
        self.btn_feed.grid(row=0, column=0, padx=5, ipady=5)
        
        self.btn_play = ttk.Button(btn_frame, text="🎾 Играть", command=self.action_play)
        self.btn_play.grid(row=0, column=1, padx=5, ipady=5)
        
        self.btn_sleep = ttk.Button(btn_frame, text="🛏 Спать", command=self.action_sleep)
        self.btn_sleep.grid(row=0, column=2, padx=5, ipady=5)
        
        self.log_text = tk.Text(self.root, height=5, width=45, state=tk.DISABLED, bg="#f5f5f5", font=("Arial", 10))
        self.log_text.pack(pady=10)
        
        # Если загрузились живыми, приветствуем
        if self.pet.is_alive:
            self.log(f"С возвращением! {self.pet.name} ждал вас.")
        else:
            self.log("Увы, питомец не дожил до вашего возвращения.")

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def action_feed(self):
        self.log(self.pet.feed())
        self.update_ui()
        
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
        
        # Вычисляем дни (например, каждые 10 тиков = 1 день)
        days = self.pet.age_ticks // 10 
        self.age_label.config(text=f"Возраст: {days} дней")
        
        if not self.pet.is_alive:
            self.btn_feed.config(state=tk.DISABLED)
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
                
            self.root.after(3000, self.game_loop) # 3000 мс = 3 секунды (чуть замедлили)
            
            if self.pet.state in ["happy", "sleeping"]:
                self.pet.state = "normal"

    def on_closing(self):
        """Эта функция срабатывает при нажатии на крестик (закрытие окна)."""
        self.pet.save_progress() # Сохраняем перед выходом
        self.root.destroy()      # Закрываем окно

# ==========================================
# 4. ЗАПУСК ПРОГРАММЫ
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PetApp(root)
    root.mainloop()