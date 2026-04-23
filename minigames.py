import tkinter as tk
from tkinter import messagebox
import random

class GameHub:
    def __init__(self, root, pet, update_cb, log_cb):
        self.root = root
        self.pet = pet
        self.update_ui = update_cb
        self.log = log_cb

    def open_hub(self):
        self.hub = tk.Toplevel(self.root)
        self.hub.title("Игровой центр")
        self.hub.geometry("350x350")
        self.hub.configure(bg="#2c3e50")
        
        tk.Label(self.hub, text="🕹️ ИГРОВЫЕ АВТОМАТЫ", font=("Arial", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=20)
        
        tk.Button(self.hub, text="👾 Поймай Пикселя\n(Бесплатно, награда: 2 💰 за клик)", 
                  command=self.play_catch, bg="#64b5f6", font=("Arial", 10, "bold"), height=3).pack(fill=tk.X, padx=30, pady=10)
                  
        tk.Button(self.hub, text="✂️ Камень-Ножницы\n(Ставка: 10 💰, Победа: 30 💰)", 
                  command=self.play_rps, bg="#ffd700", font=("Arial", 10, "bold"), height=3).pack(fill=tk.X, padx=30, pady=10)

    def play_catch(self):
        game_win = tk.Toplevel(self.hub)
        game_win.title("Поймай Пикселя")
        game_win.geometry("400x400")

        tk.Label(game_win, text="Кликай на кнопку!", font=("Arial", 12, "bold")).pack(pady=10)
        btn = tk.Button(game_win, text="👾", width=4, height=2, bg="orange")
        btn.place(x=150, y=150)

        score = [0]
        def move_btn():
            if not game_win.winfo_exists(): return
            btn.place(x=random.randint(20, 350), y=random.randint(50, 300))
            game_win.after(max(400, 1000 - score[0]*60), move_btn)

        def on_click():
            score[0] += 1
            self.pet.coins += 2
            self.pet.add_xp(5)
            self.pet.drain_stats(hunger_points=1, energy_points=2, happiness_boost=2)
            self.log("Пойман пиксель! +2 💰 -1🍎 -2⚡ +2❤️")
            btn.config(bg=random.choice(["red", "blue", "green", "orange"]))
            if score[0] >= 10:
                messagebox.showinfo("Победа!", "Отличная реакция! Бонус +20 монет!", parent=game_win)
                self.pet.coins += 20
                game_win.destroy()
            self.update_ui()

        btn.config(command=on_click)
        move_btn()

    def play_rps(self):
        if self.pet.coins < 10:
            messagebox.showerror("Упс", "Нужно 10 монет для ставки!", parent=self.hub)
            return
            
        rps_win = tk.Toplevel(self.hub)
        rps_win.title("Камень, Ножницы, Бумага")
        rps_win.geometry("300x250")
        
        tk.Label(rps_win, text="Сделай свой выбор!", font=("Arial", 12, "bold")).pack(pady=20)
        btn_frame = tk.Frame(rps_win)
        btn_frame.pack()
        
        choices = {"Камень": "🪨", "Ножницы": "✂️", "Бумага": "📜"}
        
        def resolve(player_choice):
            self.pet.coins -= 10
            self.pet.drain_stats(hunger_points=5, energy_points=10, happiness_boost=5)
            bot_choice = random.choice(list(choices.keys()))
            result_txt = f"Бот выбрал: {bot_choice}\n\n"
            
            if player_choice == bot_choice:
                self.pet.coins += 10
                result_txt += "Ничья! Ставка возвращена."
            elif (player_choice == "Камень" and bot_choice == "Ножницы") or \
                 (player_choice == "Ножницы" and bot_choice == "Бумага") or \
                 (player_choice == "Бумага" and bot_choice == "Камень"):
                self.pet.coins += 30
                self.pet.happiness += 10
                self.pet.add_xp(20)
                result_txt += "Ты победил! +30 💰"
                self.log("Победа в казино! +30 💰")
            else:
                self.pet.happiness -= 5
                result_txt += "Ты проиграл 10 💰..."
                self.log("Проигрыш ставки...")
                
            messagebox.showinfo("Результат", result_txt, parent=rps_win)
            self.update_ui()
            rps_win.destroy()

        for name, icon in choices.items():
            tk.Button(btn_frame, text=f"{icon}\n{name}", width=8, height=3, 
                      command=lambda n=name: resolve(n)).pack(side=tk.LEFT, padx=5)