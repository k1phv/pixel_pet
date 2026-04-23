# ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import time
from constants import COLORS, FOOD_TYPES, ACHIEVEMENTS, WEATHER_TYPES
from pet import Pet
from logger import logger
from minigames import GameHub

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Pet: Reborn v6.1")
        self.root.geometry("600x900")
        self.root.configure(bg="#f0f0f0")
 
        self.pet = Pet()
        self.stat_labels = {} 
        self.lbl_coins = None
        self.lbl_level = None
        self.revive_btn = None
        
        self.setup_ui()
        self.update_ui()
        self.game_loop()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.main_tab = tk.Frame(self.tabs, bg="white")
        self.tabs.add(self.main_tab, text="🏠 Питомец")
        self.setup_main_tab()

        self.ach_tab = tk.Frame(self.tabs, bg="#f9f9f9")
        self.tabs.add(self.ach_tab, text="🏆 Успехи")
        self.setup_ach_tab()

    def setup_main_tab(self):
        # Панель заголовка
        header = tk.Frame(self.main_tab, bg="#2c3e50", pady=10)
        header.pack(fill=tk.X)
        
        self.weather_lbl = tk.Label(header, text="", fg="#ecf0f1", bg="#2c3e50", font=("Arial", 10))
        self.weather_lbl.pack(side=tk.RIGHT, padx=10)

        self.name_label = tk.Label(header, text=self.pet.name, fg="white", bg="#2c3e50", font=("Verdana", 14, "bold"))
        self.name_label.pack(side=tk.LEFT, padx=10)

        # Панель инфо
        info_panel = tk.Frame(self.main_tab, bg="white")
        info_panel.pack(pady=10)
        
        self.lbl_coins = tk.Label(info_panel, text="💰 0", font=("Arial", 14, "bold"), fg="#d4af37", bg="white")
        self.lbl_coins.grid(row=0, column=0, padx=30)
        
        self.lbl_level = tk.Label(info_panel, text="Уровень: 1", font=("Arial", 14, "bold"), bg="white")
        self.lbl_level.grid(row=0, column=1, padx=30)

        # Прогресс уровня
        self.xp_bar = ttk.Progressbar(self.main_tab, length=450, mode='determinate')
        self.xp_bar.pack(pady=10)

        # Холст для рисования
        self.canvas = tk.Canvas(self.main_tab, width=320, height=320, bg="white", highlightthickness=1)
        self.canvas.pack(pady=10)

        # Полоски статов
        self.bars = {}
        for stat in ["Голод", "Энергия", "Счастье"]:
            f = tk.Frame(self.main_tab, bg="white")
            f.pack(fill=tk.X, padx=50, pady=2)
            
            tk.Label(f, text=stat, width=10, anchor='w', bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
            bar = ttk.Progressbar(f, length=200, mode='determinate')
            bar.pack(side=tk.LEFT, padx=5)
            
            val_lbl = tk.Label(f, text="0 / 100", width=8, bg="white", font=("Courier", 10, "bold"))
            val_lbl.pack(side=tk.RIGHT)
            
            self.bars[stat] = bar
            self.stat_labels[stat] = val_lbl

        # Кнопки
        btn_container = tk.Frame(self.main_tab, bg="white")
        btn_container.pack(pady=20)
        
        actions = [
            ("🍕 Магазин", self.open_shop), ("🎒 Рюкзак", self.open_inventory),
            ("🎮 Игровой Центр", self.open_games), ("👕 Стиль", self.open_wardrobe)
        ]
        for i, (txt, cmd) in enumerate(actions):
            tk.Button(btn_container, text=txt, width=16, height=2, font=("Arial", 9, "bold"), bg="#e0e0e0", command=cmd).grid(row=i//2, column=i%2, padx=10, pady=5)

        self.log_box = tk.Listbox(self.main_tab, height=5, width=70, bg="#f5f5f5", font=("Arial", 9))
        self.log_box.pack(pady=10)

    def setup_ach_tab(self):
        tk.Label(self.ach_tab, text="Ваши достижения", font=("Arial", 16, "bold"), bg="#f9f9f9").pack(pady=20)
        self.ach_container = tk.Frame(self.ach_tab, bg="#f9f9f9")
        self.ach_container.pack(fill=tk.BOTH, expand=True)

    def refresh_achievements(self):
        for widget in self.ach_container.winfo_children():
            widget.destroy()
        for key, info in ACHIEVEMENTS.items():
            unlocked = key in self.pet.achievements.unlocked
            status = "✅ ОТКРЫТО" if unlocked else "🔒 ЗАБЛОКИРОВАНО"
            color = "#c8e6c9" if unlocked else "#eeeeee"
            f = tk.Frame(self.ach_container, bg=color, bd=1, relief=tk.SOLID, pady=10)
            f.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(f, text=info["title"], font=("Arial", 11, "bold"), bg=color).pack(side=tk.LEFT, padx=10)
            tk.Label(f, text=info["desc"], bg=color).pack(side=tk.LEFT, padx=10)
            tk.Label(f, text=status, font=("Arial", 9, "italic"), bg=color).pack(side=tk.RIGHT, padx=10)

    def open_games(self):
        if not self.pet.is_alive:
            messagebox.showwarning("Мертвые не играют", "Сначала воскресите питомца!")
            return
        hub = GameHub(self.root, self.pet, self.update_ui, self.log)
        hub.open_hub()

    def open_shop(self):
        shop = tk.Toplevel(self.root)
        shop.title("Магазин")
        shop.geometry("350x500")
        for name, data in FOOD_TYPES.items():
            f = tk.LabelFrame(shop, text=name, padx=10, pady=5)
            f.pack(fill=tk.X, padx=15, pady=5)
            tk.Label(f, text=data["desc"], font=("Arial", 8)).pack(side=tk.LEFT)
            tk.Button(f, text=f"Купить ({data['cost']}💰)", command=lambda n=name: self.buy_logic(n, shop)).pack(side=tk.RIGHT)

    def buy_logic(self, name, shop_win):
        cost = FOOD_TYPES[name]["cost"]
        if self.pet.coins >= cost:
            self.pet.coins -= cost
            self.pet.inventory[name] = self.pet.inventory.get(name, 0) + 1
            self.log(f"Куплено: {name}")
            self.update_ui()
        else: messagebox.showerror("Упс", "Недостаточно монет!")

    def open_inventory(self):
        inv_win = tk.Toplevel(self.root)
        inv_win.title("Рюкзак")
        inv_win.geometry("300x400")
        has_items = False
        for item, count in self.pet.inventory.items():
            if count > 0:
                has_items = True
                f = tk.Frame(inv_win); f.pack(fill=tk.X, padx=20, pady=5)
                tk.Label(f, text=f"{item} x{count}").pack(side=tk.LEFT)
                tk.Button(f, text="Съесть", command=lambda i=item: self.use_item(i, inv_win)).pack(side=tk.RIGHT)
        if not has_items: tk.Label(inv_win, text="Рюкзак пуст").pack(pady=20)

    def use_item(self, item, win):
        if not self.pet.is_alive:
            messagebox.showwarning("Упс", "Мертвому это не поможет...")
            win.destroy(); return
        self.log(self.pet.eat_from_inventory(item))
        self.update_ui()
        win.destroy()

    def open_wardrobe(self):
        w = tk.Toplevel(self.root)
        w.title("Стиль")
        for c in COLORS:
            btn = tk.Button(w, text=c.upper(), bg=COLORS[c]["main"], command=lambda n=c: self.set_color(n, w))
            btn.pack(fill=tk.X, padx=20, pady=5)

    def set_color(self, name, win):
        if name in self.pet.unlocked_colors:
            self.pet.color_name = name
            self.update_ui()
        elif self.pet.coins >= 100:
            self.pet.coins -= 100
            self.pet.unlocked_colors.append(name)
            self.pet.color_name = name
            self.update_ui()
            self.log(f"Новый стиль: {name}")
        else: messagebox.showerror("Упс", "Нужно 100 монет!")
        win.destroy()

    def log(self, msg):
        self.log_box.insert(0, f"[{time.strftime('%H:%M:%S')}] {msg}")
        if self.log_box.size() > 50: self.log_box.delete(50, tk.END)

    def update_ui(self):
        self.lbl_coins.config(text=f"💰 {self.pet.coins}")
        self.lbl_level.config(text=f"Уровень: {self.pet.level}")

        stats_map = {"Голод": self.pet.hunger, "Энергия": self.pet.energy, "Счастье": self.pet.happiness}
        for stat, val in stats_map.items():
            self.bars[stat]['value'] = val
            self.stat_labels[stat].config(text=f"{int(val)} / 100")
            self.stat_labels[stat].config(fg="red" if val < 30 else "black")
        
        w_data = WEATHER_TYPES[self.pet.current_weather]
        self.weather_lbl.config(text=f"{w_data['icon']} {self.pet.current_weather}")
        self.xp_bar['value'] = (self.pet.xp / (self.pet.level * 100)) * 100
        
        self.draw_pet()
        self.refresh_achievements()

    def draw_pet(self):
        self.canvas.delete("all")
        
        if self.revive_btn is not None and self.revive_btn.winfo_exists():
            self.revive_btn.destroy()
            self.revive_btn = None

        if not self.pet.is_alive:
            self.canvas.create_text(160, 110, text="👻", font=("Arial", 60))
            self.canvas.create_text(160, 170, text="Игра окончена", font=("Arial", 12, "bold"), fill="red")
            self.revive_btn = tk.Button(self.canvas, text="Начать заново (Бесплатно)", 
                                        bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), 
                                        command=self.revive_pet)
            self.canvas.create_window(160, 220, window=self.revive_btn)
            return

        emotion = self.pet.get_emotion_icon()

        self.canvas.create_oval(230, 70, 270, 110, fill="#f0f0f0", outline="#cccccc") # Основной круг
        self.canvas.create_oval(220, 100, 235, 115, fill="#f0f0f0", outline="#cccccc") # Маленький пузырек
        self.canvas.create_text(250, 90, text=emotion, font=("Arial", 18))

        c = COLORS[self.pet.color_name]["main"]

        self.canvas.create_oval(110, 210, 210, 230, fill="#eeeeee", outline="")

        self.canvas.create_oval(100, 100, 220, 220, fill=c, width=2, outline="#333333")

        eye_color = "black"
        if self.pet.happiness < 30:
            self.canvas.create_line(130, 150, 145, 150, width=2)
            self.canvas.create_line(175, 150, 190, 150, width=2)
        else:
            self.canvas.create_oval(130, 140, 145, 155, fill="white")
            self.canvas.create_oval(175, 140, 190, 155, fill="white")
            self.canvas.create_oval(135, 148, 140, 153, fill="black")
            self.canvas.create_oval(180, 148, 185, 153, fill="black")

        if self.pet.happiness < 30:
            self.canvas.create_arc(140, 170, 180, 190, start=0, extent=180, style=tk.ARC, width=2) # Грустный
        elif self.pet.hunger < 40:
             self.canvas.create_oval(155, 175, 165, 185, fill="#555555") # Удивленный/голодный рот "О"
        else:
            self.canvas.create_arc(140, 160, 180, 180, start=180, extent=180, style=tk.ARC, width=2) # Улыбка

    def revive_pet(self):
        self.pet.reset()
        self.log("Пиксель переродился! Новая жизнь началась.")
        self.update_ui()
        self.game_loop()

    def game_loop(self):
        if self.pet.is_alive:
            new_achs = self.pet.tick()
            if new_achs:
                for a in new_achs:
                    messagebox.showinfo("🏆 ДОСТИЖЕНИЕ!", f"Открыто: {ACHIEVEMENTS[a]['title']}!")
            self.update_ui()
            self.root.after(3000, self.game_loop)

    def on_close(self):
        self.pet.save_progress()
        self.root.destroy()