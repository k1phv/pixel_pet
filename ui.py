import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
from constants import COLORS, FOOD_TYPES
from pet import Pet

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Pet Ultra v4.0")
        self.root.geometry("550x850")
        self.root.configure(bg="#f5f5f5")
        
        self.pet = Pet() # Связываем интерфейс с логикой питомца
        self.setup_ui()
        self.update_ui()
        self.game_loop()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        self.top_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        self.top_frame.pack(fill=tk.X)
        
        self.name_label = tk.Label(self.top_frame, text=self.pet.name, fg="white", bg="#2c3e50", font=("Verdana", 14, "bold"))
        self.name_label.pack()
        
        self.xp_bar = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.xp_bar.pack(pady=5)
        
        self.info_panel = tk.Frame(self.root, bg="#f5f5f5")
        self.info_panel.pack(pady=10)
        
        self.lbl_coins = tk.Label(self.info_panel, text=f"💰 {self.pet.coins}", font=("Arial", 12, "bold"), fg="#d4af37")
        self.lbl_coins.grid(row=0, column=0, padx=20)
        
        self.lbl_level = tk.Label(self.info_panel, text=f"Уровень: {self.pet.level}", font=("Arial", 12))
        self.lbl_level.grid(row=0, column=1, padx=20)

        self.canvas = tk.Canvas(self.root, width=320, height=320, bg="white", highlightthickness=1, highlightbackground="#ddd")
        self.canvas.pack(pady=10)

        self.bars = {}
        for stat in ["Голод", "Энергия", "Счастье"]:
            frame = tk.Frame(self.root, bg="#f5f5f5")
            frame.pack(fill=tk.X, padx=80)
            tk.Label(frame, text=stat, width=10, anchor='w', bg="#f5f5f5").pack(side=tk.LEFT)
            bar = ttk.Progressbar(frame, length=250, mode='determinate')
            bar.pack(side=tk.RIGHT, pady=3)
            self.bars[stat] = bar

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

        self.log_box = tk.Listbox(self.root, height=4, width=60, font=("Consolas", 9), bg="#eee")
        self.log_box.pack(pady=10)

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
        self.canvas.create_oval(80, 100, 240, 260, fill=color, outline="#333", width=2)
        self.canvas.create_oval(110, 140, 130, 160, fill="white")
        self.canvas.create_oval(190, 140, 210, 160, fill="white")
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