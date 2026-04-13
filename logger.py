import datetime

class GameLogger:
    def __init__(self, filename="game.log"):
        self.filename = filename

    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"[{timestamp}] [{level}] {message}\n"
        print(formatted_msg.strip())
        
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(formatted_msg)

    def clear_logs(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("")

logger = GameLogger()