import customtkinter as ctk
import threading
import time
from tic_tac_toe_game import TicTacToe, ask_ollama, get_move_from_model

class TicTacToeGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("LLM Tic-Tac-Toe Battle")
        self.window.geometry("600x800")
        
        # Game instance
        self.game = TicTacToe()
        self.buttons = []
        self.game_active = False
        
        # Model settings
        self.model1 = "llama3.2:1b"  # Default model for X
        self.model2 = "llama3.2:3b"  # Default model for O
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Title
        title = ctk.CTkLabel(self.window, text="LLM Tic-Tac-Toe Battle", font=("Arial", 24))
        title.pack(pady=20)
        
        # Model selection frames
        models_frame = ctk.CTkFrame(self.window)
        models_frame.pack(pady=10)
        
        # Model 1 (X) selection
        model1_frame = ctk.CTkFrame(models_frame)
        model1_frame.pack(side="left", padx=10)
        ctk.CTkLabel(model1_frame, text="Player X (First)").pack()
        self.model1_var = ctk.StringVar(value=self.model1)
        model1_entry = ctk.CTkEntry(model1_frame, textvariable=self.model1_var)
        model1_entry.pack()
        
        # Model 2 (O) selection
        model2_frame = ctk.CTkFrame(models_frame)
        model2_frame.pack(side="left", padx=10)
        ctk.CTkLabel(model2_frame, text="Player O (Second)").pack()
        self.model2_var = ctk.StringVar(value=self.model2)
        model2_entry = ctk.CTkEntry(model2_frame, textvariable=self.model2_var)
        model2_entry.pack()
        
        # Game board
        board_frame = ctk.CTkFrame(self.window)
        board_frame.pack(pady=20)
        
        for i in range(3):
            row = []
            for j in range(3):
                button = ctk.CTkButton(
                    board_frame,
                    text="",
                    width=100,
                    height=100,
                    font=("Arial", 40),
                    state="disabled"
                )
                button.grid(row=i, column=j, padx=5, pady=5)
                row.append(button)
            self.buttons.append(row)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.window, text="Press Start to begin the game", font=("Arial", 16))
        self.status_label.pack(pady=20)
        
        # Control buttons
        control_frame = ctk.CTkFrame(self.window)
        control_frame.pack(pady=10)
        
        self.start_button = ctk.CTkButton(
            control_frame,
            text="Start Game",
            command=self.start_game
        )
        self.start_button.pack(side="left", padx=5)
        
        self.reset_button = ctk.CTkButton(
            control_frame,
            text="Reset",
            command=self.reset_game,
            state="disabled"
        )
        self.reset_button.pack(side="left", padx=5)
    
    def update_board(self):
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                self.buttons[i][j].configure(text=self.game.board[idx])
    
    def start_game(self):
        self.game_active = True
        self.start_button.configure(state="disabled")
        self.reset_button.configure(state="normal")
        self.status_label.configure(text="Game started!")
        
        # Start the game in a separate thread
        threading.Thread(target=self.game_loop, daemon=True).start()
    
    def game_loop(self):
        while self.game_active:
            current_model = self.model1_var.get() if self.game.current_player == "X" else self.model2_var.get()
            self.status_label.configure(text=f"Player {self.game.current_player} ({current_model}) is thinking...")
            
            try:
                move = get_move_from_model(current_model, self.game, self.game.current_player)
                if move is not None and self.game.make_move(move):
                    self.window.after(0, self.update_board)
                    time.sleep(1)  # Add delay for better visualization
                    
                    winner = self.game.check_winner()
                    if winner:
                        if winner == "Draw":
                            self.status_label.configure(text="Game Over - It's a Draw!")
                        else:
                            self.status_label.configure(text=f"Game Over - Player {winner} wins!")
                        self.game_active = False
                        break
            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}")
                self.game_active = False
                break
    
    def reset_game(self):
        self.game = TicTacToe()
        self.game_active = False
        self.start_button.configure(state="normal")
        self.reset_button.configure(state="disabled")
        self.status_label.configure(text="Press Start to begin the game")
        self.update_board()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TicTacToeGUI()
    app.run()
