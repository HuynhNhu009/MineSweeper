import tkinter as tk
import random
import time
from tkinter import messagebox
import webbrowser
from playsound import playsound

class Minesweeper:
    def __init__(self, root, rows=10, cols=10, mines=10):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.flags = 0
        self.buttons = []
        self.mine_locations = set()
        self.start_time = None
        self.time_elapsed = 0
        self.game_over = False
        self.flag_mode = False

    
        self.best_score = self.read_best_score()
        
       
        self.timer_label = tk.Label(root, text="Nhấn vào các ô biên dưới để bắt đầu")
        self.timer_label.grid(row=0, column=0, columnspan=cols)
        
      
        best_score_text = f"Kỷ lục hiện tại: {self.best_score} giây" if self.best_score is not None else "Kỷ lục hiện tại: chưa được thiết lập"
        self.best_score_label = tk.Label(self.root, text=best_score_text)
        self.best_score_label.grid(row=1, column=0, columnspan=self.cols)

    
        try:
            self.flag_icon = tk.PhotoImage(file="images/flag.png").zoom(2, 2)
            self.mine_icon = tk.PhotoImage(file="images/mine.png").zoom(2, 2)
        except Exception as e:
            print("Không thể tải ảnh:", e)

 
        self.create_widgets()
        self.place_mines()
        self.update_timer()

        
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
       
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        difficulty_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Độ khó", menu=difficulty_menu)
        difficulty_menu.add_command(label="Dễ (10x10, 10 mìn)", command=lambda: self.set_difficulty(10, 10, 10))
        difficulty_menu.add_command(label="Trung bình (10x12, 20 mìn)", command=lambda: self.set_difficulty(10, 12, 20))
        difficulty_menu.add_command(label="Khó (12x16, 40 mìn)", command=lambda: self.set_difficulty(12, 16, 30))

        help_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Trợ giúp",menu=help_menu )
        help_menu.add_command(label="Cách chơi", command=self.how_to_play)
        help_menu.add_command(label="Giới thiệu", command=self.about_this)

       
        for row in range(self.rows):
            row_buttons = []
            for col in range(self.cols):
                button = tk.Button(self.root, width=4, height=2, command=lambda r=row, c=col: self.click_cell(r, c))
                button.bind("<Button-3>", lambda e, r=row, c=col: self.toggle_flag(r, c))
                button.grid(row=row + 2, column=col)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

      
        self.flag_button = tk.Button(self.root, text="Chế độ đặt cờ: Tắt", command=self.toggle_flag_mode, width=30, height=3, bg="#2D99AE", fg="white", font=("Helvetica", 14, "bold"), padx=10)
        self.flag_button.grid(row=self.rows + 3, column=0, columnspan=self.cols, pady=10)

        self.reset_button = tk.Button(self.root, text="Chơi lại", command=self.reset_game, width=30, height=2, bg='#CED1E6', font=("Helvetica", 10, "bold"))
        self.reset_button.grid(row=self.rows + 4, column=0, columnspan=self.cols, ipadx=10)

    def set_difficulty(self, rows, cols, mines):
        self.rows, self.cols, self.mines = rows, cols, mines
        self.reset_game()

    def place_mines(self):
        self.mine_locations.clear()
        count = 0
        while count < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row, col) not in self.mine_locations:
                self.mine_locations.add((row, col))
                count += 1

    def click_cell(self, row, col):
        if not self.start_time:
            self.start_timer()

        if self.game_over or self.buttons[row][col]["state"] == "disabled":
            return

        if self.flag_mode:
            self.toggle_flag(row, col)
        elif (row, col) in self.mine_locations:
            self.buttons[row][col].config(image=self.mine_icon, bg="#333333", padx=1, pady=1)
            self.end_game(False)
        else:
            self.reveal_cell(row, col)

    def reveal_cell(self, row, col):
        if self.buttons[row][col]["state"] == "disabled":
            return

        self.buttons[row][col].config(state="disabled", relief=tk.SUNKEN)
        adjacent_mines = self.count_adjacent_mines(row, col)
        if adjacent_mines > 0:
            self.buttons[row][col].config(text=str(adjacent_mines))
        else:
            for r in range(max(0, row - 1), min(self.rows, row + 2)):
                for c in range(max(0, col - 1), min(self.cols, col + 2)):
                    if (r, c) != (row, col):
                        self.reveal_cell(r, c)

        if self.check_win():
            self.end_game(True)

    def count_adjacent_mines(self, row, col):
        count = 0
        for r in range(max(0, row - 1), min(self.rows, row + 2)):
            for c in range(max(0, col - 1), min(self.cols, col + 2)):
                if (r, c) in self.mine_locations:
                    count += 1
        return count

    def toggle_flag(self, row, col):
        if self.buttons[row][col]["state"] == "disabled":
            return

        current_image = self.buttons[row][col].cget("image")
        if current_image:
            self.buttons[row][col].config(image="", bg="SystemButtonFace")
            self.flags -= 1
        else:
            self.buttons[row][col].config(image=self.flag_icon)
            self.flags += 1

        if self.check_win():
            self.end_game(True)

    def toggle_flag_mode(self):
        self.flag_mode = not self.flag_mode
        self.flag_button.config(text="Chế độ đặt cờ: Bật" if self.flag_mode else "Chế độ đặt cờ: Tắt", bg="#001C44" if self.flag_mode else "#2D99AE")

    def check_win(self):
        cells_left = sum(button["state"] != "disabled" for row in self.buttons for button in row)
        return cells_left == self.mines

    def end_game(self, win):
        self.game_over = True
        if win:
            self.update_best_score()
            self.timer_label.config(text=f"Thời gian: {self.time_elapsed} giây - Bạn đã thắng!")
            playsound("sounds/ThangRoi.mp3")
            messagebox.showinfo('Thắng rồi!', f'Thời gian của bạn là: {self.time_elapsed} giây')
        else:
            for row, col in self.mine_locations:
                self.buttons[row][col].config(image=self.mine_icon, bg="red")
            self.timer_label.config(text=f"Thời gian: {self.time_elapsed} giây - Game Over")
            playsound("sounds/NoBanhXac.mp3")
            if messagebox.askokcancel("Thua rồi!", "Bạn có muốn chơi lại ngay không?"):
               self.reset_game()
             

    def read_best_score(self, file_path="bestScore.txt"):
        try:
            with open(file_path, "r") as file:
                best_score = file.read().strip()
                return int(best_score) if best_score else None
        except (FileNotFoundError, ValueError):
            return None

    def write_best_score(self, score, file_path="bestScore.txt"):
        with open(file_path, "w") as file:
            file.write(str(score))

    def update_best_score(self):
        if self.time_elapsed is not None and (self.best_score is None or self.time_elapsed < self.best_score):
            self.write_best_score(self.time_elapsed)
            self.best_score_label.config(text=f"Kỷ lục hiện tại: {self.time_elapsed} giây")
            print(f"Cập nhật best score mới: {self.time_elapsed}")

    def reset_game(self):
        self.flags = 0
        self.mine_locations.clear()
        self.game_over = False
        self.start_time = None
        self.time_elapsed = 0
        self.timer_label.config(text="Thời gian: chưa bắt đầu")
    
        for row_buttons in self.buttons:
            for button in row_buttons:
                button.grid_forget()
        self.buttons.clear()

        for row in range(self.rows):
            row_buttons = []
            for col in range(self.cols):
                button = tk.Button(self.root, width=4, height=2, command=lambda r=row, c=col: self.click_cell(r, c))
                button.bind("<Button-3>", lambda e, r=row, c=col: self.toggle_flag(r, c))
                button.grid(row=row + 2, column=col)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

        self.place_mines()
        self.create_layout()



    def create_layout(self):
      
        self.timer_label.grid(row=0, column=0, columnspan=self.cols)
        self.best_score_label.grid(row=1, column=0, columnspan=self.cols)
        self.flag_button.grid(row=self.rows + 3, column=0, columnspan=self.cols, pady=10)
        self.reset_button.grid(row=self.rows + 4, column=0, columnspan=self.cols, ipadx=10)
           
            
    def update_timer(self):
        if not self.game_over and self.start_time:
            self.time_elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Thời gian hiện tại: {self.time_elapsed}")
        self.root.after(1000, self.update_timer)

    def start_timer(self):
        if not self.start_time:
            self.start_time = time.time()
    
    def on_close(self):
        if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát không?"):
             root.destroy() 

    def about_this(self):
        messagebox.showinfo("Giới thiệu", "Đây là phiên bản Dò mìn đầu tay nên khó tránh khỏi những sai sót nhất định.\n Mong bạn luôn có được trải nghiệm tốt nhất.\n Email liên hệ: nhub2110090@student.ctu.edu.vn")

    def how_to_play(self):
        url = "https://vi.wikipedia.org/wiki/D%C3%B2_m%C3%ACn_(tr%C3%B2_ch%C6%A1i)"
        webbrowser.open(url)  

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dò mìn")
    root.iconphoto(False, tk.PhotoImage(file="images/icon.png"))
    root.resizable(False, False)
    game = Minesweeper(root)
    root.mainloop()
