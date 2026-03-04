import tkinter as tk
from tkinter import ttk
import random

# ==========================================
# 1. КЛАСС ПИТОМЦА (Логика)
# ==========================================
class Pet:
    def __init__(self, name):
        """Создаем нового питомца со стартовыми параметрами (от 0 до 100)."""
        self.name = name
        self.hunger = 50      # 100 - сыт, 0 - умирает от голода
        self.energy = 80      # 100 - бодр, 0 - падает от усталости
        self.happiness = 50   # 100 - счастлив, 0 - депрессия
        self.is_alive = True
        self.state = "normal" # normal, happy, sad, sleeping, dead

    def feed(self):
        """Метод кормления. Увеличивает сытость, но может немного клонить в сон."""
        if not self.is_alive: return "Питомец мертв..."
        
        self.hunger += 20
        self.energy -= 5  # После еды хочется спать
        self._cap_stats()
        self.state = "happy"
        return f"Вы покормили {self.name}. Ом-ном-ном!"

    def play(self):
        """Метод игры. Увеличивает счастье, но тратит энергию и вызывает голод."""
        if not self.is_alive: return "Питомец мертв..."
        
        if self.energy < 20:
            return f"{self.name} слишком устал для игр!"
            
        self.happiness += 20
        self.energy -= 15
        self.hunger -= 10
        self._cap_stats()
        self.state = "happy"
        return f"Вы поиграли с {self.name}. Ему весело!"

    def sleep(self):
        """Метод сна. Восстанавливает энергию, но питомец становится голодным."""
        if not self.is_alive: return "Питомец мертв..."
        
        self.energy += 30
        self.hunger -= 15
        self._cap_stats()
        self.state = "sleeping"
        return f"{self.name} поспал и полон сил."

    def tick(self):
        """Игровой такт (время идет). Параметры падают сами по себе."""
        if not self.is_alive:
            return
            
        # Параметры постепенно уменьшаются
        self.hunger -= random.randint(1, 3)
        self.energy -= random.randint(1, 2)
        self.happiness -= random.randint(1, 3)
        self._cap_stats()

        # Проверка состояния
        if self.hunger <= 0 or self.energy <= 0 or self.happiness <= 0:
            self.is_alive = False
            self.state = "dead"
        elif self.hunger < 30 or self.happiness < 30:
            self.state = "sad"
        elif self.state not in ["sleeping", "happy"]:
            self.state = "normal"

    def _cap_stats(self):
        """Служебный метод: не дает параметрам выйти за границы 0-100."""
        self.hunger = max(0, min(100, self.hunger))
        self.energy = max(0, min(100, self.energy))
        self.happiness = max(0, min(100, self.happiness))


# ==========================================
# 2. ПИКСЕЛЬНЫЕ АРТЫ ДЛЯ ПИТОМЦА
# ==========================================
# Символы: '.' - пусто, 'b' - черный (граница), 'w' - белый, 'c' - цвет питомца, 'p' - розовый (щечки)
FRAMES = {
    "normal": [
        "....bbbb....",
        "..bbccccbb..",
        ".bccccccccb.",
        "bccbbccbbccb",
        "bccwwccwwccb",
        "bccbbccbbccb",
        "bpccccccccpb",
        ".bccbbbbccb.",
        "..bbccccbb..",
        "....bbbb...."
    ],
    "happy": [
        "....bbbb....",
        "..bbccccbb..",
        ".bccccccccb.",
        "bccbbccbbccb",
        "bccccccccccb",
        "bccccccccccb",
        "bpccbbbbccpb",
        ".bccbwwbccb.",
        "..bbccccbb..",
        "....bbbb...."
    ],
    "sad": [
        "....bbbb....",
        "..bbccccbb..",
        ".bccccccccb.",
        "bccbbccbbccb",
        "bccccccccccb",
        "bccccccccccb",
        "bpccccccccpb",
        ".bccbbbbccb.",
        "..bbccccbb..",
        "....bbbb...."
    ],
    "sleeping": [
        "....bbbb....",
        "..bbccccbb..",
        ".bccccccccb.",
        "bccccccccccb",
        "bccbbccbbccb",
        "bccccccccccb",
        "bccccccccccb",
        ".bccbbbbccb.",
        "..bbccccbb..",
        "....bbbb...."
    ],
    "dead": [
        "....bbbb....",
        "..bbbbbbbb..",
        ".bbbbbbbbbb.",
        "bbbwbbwwbbwb",
        "bbbwbwbwbwwb",
        "bbbwbbwwbbwb",
        "bbbbbbbbbbbb",
        ".bbbbbbbbbb.",
        "..bbbbbbbb..",
        "....bbbb...."
    ]
}

# ==========================================
# 3. КЛАСС ПРИЛОЖЕНИЯ (Графический интерфейс)
# ==========================================
class PetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Pet - Твой виртуальный друг")
        self.root.geometry("450x650")
        self.root.resizable(False, False)
        
        # Настраиваем стили
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Создаем питомца
        self.pet = Pet("Пиксель")
        
        self.setup_ui()
        self.update_ui()
        self.game_loop() # Запускаем таймер игры

    def setup_ui(self):
        """Создает все элементы интерфейса на экране."""
        # --- Холст для отрисовки питомца ---
        self.canvas = tk.Canvas(self.root, width=240, height=240, bg="#e0f7fa", highlightthickness=2)
        self.canvas.pack(pady=20)
        
        # --- Фрейм для индикаторов (Progressbars) ---
        stats_frame = ttk.Frame(self.root)
        stats_frame.pack(fill=tk.X, padx=40, pady=10)
        
        # Индикатор голода
        ttk.Label(stats_frame, text="Сытость:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bar_hunger = ttk.Progressbar(stats_frame, length=200, mode='determinate')
        self.bar_hunger.grid(row=0, column=1, padx=10)
        
        # Индикатор энергии
        ttk.Label(stats_frame, text="Энергия:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.bar_energy = ttk.Progressbar(stats_frame, length=200, mode='determinate')
        self.bar_energy.grid(row=1, column=1, padx=10)
        
        # Индикатор счастья
        ttk.Label(stats_frame, text="Счастье:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.bar_happiness = ttk.Progressbar(stats_frame, length=200, mode='determinate')
        self.bar_happiness.grid(row=2, column=1, padx=10)

        # --- Фрейм для кнопок действий ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        self.btn_feed = ttk.Button(btn_frame, text="🍖 Кормить", command=self.action_feed)
        self.btn_feed.grid(row=0, column=0, padx=5, ipady=5)
        
        self.btn_play = ttk.Button(btn_frame, text="🎾 Играть", command=self.action_play)
        self.btn_play.grid(row=0, column=1, padx=5, ipady=5)
        
        self.btn_sleep = ttk.Button(btn_frame, text="🛏 Спать", command=self.action_sleep)
        self.btn_sleep.grid(row=0, column=2, padx=5, ipady=5)
        
        # --- Текстовое поле для журнала событий ---
        self.log_text = tk.Text(self.root, height=6, width=45, state=tk.DISABLED, bg="#f5f5f5", font=("Arial", 10))
        self.log_text.pack(pady=10)
        self.log("Игра началась! Позаботьтесь о Пикселе.")

    def log(self, message):
        """Добавляет сообщение в журнал на экране."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # Автопрокрутка вниз
        self.log_text.config(state=tk.DISABLED)

    # --- Действия кнопок ---
    def action_feed(self):
        result = self.pet.feed()
        self.log(result)
        self.update_ui()
        
    def action_play(self):
        result = self.pet.play()
        self.log(result)
        self.update_ui()
        
    def action_sleep(self):
        result = self.pet.sleep()
        self.log(result)
        self.update_ui()

    # --- Обновление экрана ---
    def update_ui(self):
        """Обновляет индикаторы и перерисовывает питомца."""
        # Обновляем полоски
        self.bar_hunger['value'] = self.pet.hunger
        self.bar_energy['value'] = self.pet.energy
        self.bar_happiness['value'] = self.pet.happiness
        
        # Блокируем кнопки, если питомец умер
        if not self.pet.is_alive:
            self.btn_feed.config(state=tk.DISABLED)
            self.btn_play.config(state=tk.DISABLED)
            self.btn_sleep.config(state=tk.DISABLED)
            
        self.draw_pet()

    def draw_pet(self):
        """Рисует пиксельного питомца на холсте в зависимости от его состояния."""
        self.canvas.delete("all") # Очищаем холст
        
        frame = FRAMES.get(self.pet.state, FRAMES["normal"])
        pixel_size = 20
        offset_x = 20
        offset_y = 20
        
        color_map = {
            '.': "",          # прозрачный
            'b': "#212121",   # черный
            'w': "#ffffff",   # белый
            'c': "#ffb74d",   # оранжевый (цвет питомца)
            'p': "#f48fb1"    # розовый
        }
        
        # Рисуем по клеточкам
        for row_idx, row in enumerate(frame):
            for col_idx, char in enumerate(row):
                if char == '.': continue
                
                x1 = offset_x + col_idx * pixel_size
                y1 = offset_y + row_idx * pixel_size
                x2 = x1 + pixel_size
                y2 = y1 + pixel_size
                
                color = color_map.get(char, "black")
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    def game_loop(self):
        """Главный цикл. Вызывается автоматически каждую секунду (1000 мс)."""
        if self.pet.is_alive:
            self.pet.tick()
            self.update_ui()
            
            # Если питомец умер на этом тике
            if not self.pet.is_alive:
                self.log("О нет! Пиксель отправился в лучший мир...")
                
            # Запускаем этот же метод снова через 2000 миллисекунд (2 секунды)
            # Чем меньше число, тем быстрее падает здоровье
            self.root.after(2000, self.game_loop)
            
            # Возвращаем нормальное состояние через время, если он смеялся/спал
            if self.pet.state in ["happy", "sleeping"]:
                self.pet.state = "normal"


# ==========================================
# 4. ЗАПУСК ПРОГРАММЫ
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PetApp(root)
    root.mainloop() # Запускает бесконечный цикл окна