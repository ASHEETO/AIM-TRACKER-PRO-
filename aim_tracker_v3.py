import tkinter as tk
import random
import time


class AimTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Aim Tracker Pro")
        self.root.geometry("1000x700")
        self.root.minsize(700, 500)
        self.root.configure(bg="black")

        self.target_radius = 30
        self.time_limit = 30
        self.score = 0
        self.target_position = None
        self.start_time = None
        self.time_left = self.time_limit
        self.game_active = False
        self.move_job = None
        self.timer_job = None

        self.canvas = tk.Canvas(
            root,
            bg="black",
            highlightthickness=0,
            bd=0
        )
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        
        self.timer_label = tk.Label(
            root,
            text="Time Left: 30s",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="black"
        )
        self.timer_label.place(x=15, y=12)

        self.score_label = tk.Label(
            root,
            text="Score: 0",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="black"
        )
        self.score_label.place(relx=1.0, x=-15, y=12, anchor="ne")

        self.retry_button = tk.Button(
            root,
            text="Play Again",
            font=("Arial", 16, "bold"),
            command=self.retry_game
        )

        self.root.bind("<Button-1>", self.track_click)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)

        self.root.after(200, self.start_game)

    def get_size(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width < 100:
            width = self.root.winfo_width()

        if height < 100:
            height = self.root.winfo_height()

        return max(width, 700), max(height, 500)

    def start_game(self):
        self.cancel_jobs()

        self.canvas.delete("all")
        self.retry_button.place_forget()

        self.canvas.configure(bg="black")

        self.score = 0
        self.time_left = self.time_limit
        self.start_time = time.time()
        self.game_active = True

        self.update_score()
        self.update_timer()
        self.generate_target()

        self.move_job = self.root.after(100, self.move_target)
        self.timer_job = self.root.after(100, self.check_time)

    def generate_target(self):
        self.canvas.delete("target")

        width, height = self.get_size()

        min_x = self.target_radius + 5
        max_x = max(min_x, width - self.target_radius - 5)

        min_y = 65 + self.target_radius
        max_y = max(min_y, height - self.target_radius - 5)

        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)

        self.target_position = (x, y)

        self.canvas.create_oval(
            x - self.target_radius,
            y - self.target_radius,
            x + self.target_radius,
            y + self.target_radius,
            fill="red",
            outline="white",
            width=3,
            tags="target"
        )

    def move_target(self):
        if not self.game_active:
            return

        width, height = self.get_size()

        coords = self.canvas.coords("target")

        if len(coords) != 4:
            self.generate_target()
            coords = self.canvas.coords("target")

        current_x = (coords[0] + coords[2]) / 2
        current_y = (coords[1] + coords[3]) / 2

        new_x = current_x + random.randint(-20, 20)
        new_y = current_y + random.randint(-20, 20)

        new_x = max(
            self.target_radius + 5,
            min(width - self.target_radius - 5, new_x)
        )

        new_y = max(
            65 + self.target_radius,
            min(height - self.target_radius - 5, new_y)
        )

        self.canvas.move(
            "target",
            new_x - current_x,
            new_y - current_y
        )

        self.target_position = (new_x, new_y)

        self.move_job = self.root.after(100, self.move_target)

    def track_click(self, event):
        if not self.game_active or self.target_position is None:
            return

        target_x, target_y = self.target_position

        distance = (
            (event.x - target_x) ** 2 +
            (event.y - target_y) ** 2
        ) ** 0.5

        if distance <= self.target_radius:
            self.score += 1
            self.update_score()
            self.generate_target()

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.time_left = max(0, self.time_limit - elapsed)
        self.timer_label.config(text=f"Time Left: {self.time_left}s")

    def check_time(self):
        if not self.game_active:
            return

        self.update_timer()

        if self.time_left <= 0:
            self.end_game()
        else:
            self.timer_job = self.root.after(100, self.check_time)

    def end_game(self):
        self.game_active = False
        self.cancel_jobs()

        self.canvas.delete("target")
        self.canvas.configure(bg="black")

        width, height = self.get_size()

        self.canvas.create_text(
            width // 2,
            height // 2 - 40,
            fill="white",
            font=("Arial", 30, "bold"),
            text=f"TIME'S UP!\nFinal Score: {self.score}",
            justify="center",
            tags="result"
        )

        self.retry_button.place(
            relx=0.5,
            rely=0.5,
            y=80,
            anchor="center"
        )

    def retry_game(self):
        self.start_game()

    def cancel_jobs(self):
        if self.move_job is not None:
            try:
                self.root.after_cancel(self.move_job)
            except tk.TclError:
                pass
            self.move_job = None

        if self.timer_job is not None:
            try:
                self.root.after_cancel(self.timer_job)
            except tk.TclError:
                pass
            self.timer_job = None

    def toggle_fullscreen(self, event=None):
        current = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current)

    def exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)


root = tk.Tk()
app = AimTracker(root)
root.mainloop()
