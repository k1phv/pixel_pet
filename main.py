import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

# -----------------------------
# Класс питомца
# -----------------------------
class Pet:
    def __init__(self, name="Pixel"):
        self.name = name
        self.hunger = 50
        self.energy = 70
        self.happiness = 70

    def feed(self):
        self.hunger = max(0, self.hunger - 10)
        self.happiness = min(100, self.happiness + 2)

    def play(self):
        self.happiness = min(100, self.happiness + 10)
        self.energy = max(0, self.energy - 10)
        self.hunger = min(100, self.hunger + 5)

    def sleep(self):
        self.energy = min(100, self.energy + 20)
        self.happiness = max(0, self.happiness - 5)

# -----------------------------
# Основное приложение
# -----------------------------
class PixelPetApp:
    def __init__(self, root):
        self.root = root
        root.title("Pixel Pet — шаг 2 (картинка)")

        self.pet = Pet()

        frame = ttk.Frame(root, padding=15)
        frame.pack()

        # Имя
        self.name_label = ttk.Label(frame, text=f"Имя: {self.pet.name}", font=("Arial", 16))
        self.name_label.grid(row=0, column=0, columnspan=2, pady=5)

        # Картинка питомца
        self.pet_image = self.load_image("assets/pet.png")
        self.image_label = ttk.Label(frame, image=self.pet_image)
        self.image_label.grid(row=1, column=0, columnspan=2, pady=10)

        # Параметры
        self.hunger_var = tk.IntVar(value=self.pet.hunger)
        self.energy_var = tk.IntVar(value=self.pet.energy)
        self.happiness_var = tk.IntVar(value=self.pet.happiness)

        self.add_stat(frame, "Голод", self.hunger_var, 2)
        self.add_stat(frame, "Энергия", self.energy_var, 3)
        self.add_stat(frame, "Счастье", self.happiness_var, 4)

        # Кнопки
        ttk.Button(frame, text="Кормить", width=20, command=self.feed).grid(row=5, column=0, pady=10)
        ttk.Button(frame, text="Играть", width=20, command=self.play).grid(row=5, column=1, pady=10)
        ttk.Button(frame, text="Спать", width=20, command=self.sleep).grid(row=6, column=0, columnspan=2)

        # Сообщение
        self.message = tk.StringVar(value="Привет! Я твой питомец 😊")
        ttk.Label(frame, textvariable=self.message).grid(row=7, column=0, columnspan=2, pady=10)

    # -----------------------------
    # Вспомогательные методы
    # -----------------------------
    def load_image(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Не найдена картинка: {path}")
        img = Image.open(path).resize((128, 128))
        return ImageTk.PhotoImage(img)

    def add_stat(self, frame, label, var, row):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w")
        ttk.Progressbar(frame, orient="horizontal", length=200, variable=var, maximum=100).grid(row=row, column=1)

    def update_stats(self):
        self.hunger_var.set(self.pet.hunger)
        self.energy_var.set(self.pet.energy)
        self.happiness_var.set(self.pet.happiness)

    # -----------------------------
    # Кнопки
    # -----------------------------
    def feed(self):
        self.pet.feed()
        self.update_stats()
        self.message.set("Ты покормил питомца 🍎")

    def play(self):
        self.pet.play()
        self.update_stats()
        self.message.set("Вы играете 🎉")

    def sleep(self):
        self.pet.sleep()
        self.update_stats()
        self.message.set("Питомец спит 😴")

# -----------------------------
# Запуск
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PixelPetApp(root)
    root.mainloop()