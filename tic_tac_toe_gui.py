import customtkinter as ctk
import threading
import time
import requests
from tic_tac_toe_game import TicTacToe, ask_ollama, get_move_from_model

def get_ollama_models():
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = [model['name'] for model in response.json()['models']]
            return sorted(models) if models else ["llama2:7b"]  # fallback to default if no models
    except:
        return ["ollama is not running"]  # fallback to default if server not running

class TicTacToeGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("LLM Tic-Tac-Toe Tournament")
        self.window.geometry("600x900")
        
        # Game instance
        self.game = TicTacToe()
        self.buttons = []
        self.game_active = False
        self.tournament_active = False
        self.games_played = 0
        self.total_games = 10
        
        # Scores
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        
        # Get available models
        self.available_models = get_ollama_models()
        
        # Model settings
        self.model1 = self.available_models[0]  # Default model for X
        self.model2 = self.available_models[0]  # Default model for O
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Title
        title = ctk.CTkLabel(self.window, text="LLM Tic-Tac-Toe Tournament", font=("Arial", 24))
        title.pack(pady=20)
        
        # Model selection frames
        models_frame = ctk.CTkFrame(self.window)
        models_frame.pack(pady=10)
        
        # Model 1 (X) selection
        model1_frame = ctk.CTkFrame(models_frame)
        model1_frame.pack(side="left", padx=10)
        ctk.CTkLabel(model1_frame, text="Player X (First)").pack()
        self.model1_var = ctk.StringVar(value=self.model1)
        model1_dropdown = ctk.CTkOptionMenu(
            model1_frame,
            variable=self.model1_var,
            values=self.available_models
        )
        model1_dropdown.pack()
        
        # Model 2 (O) selection
        model2_frame = ctk.CTkFrame(models_frame)
        model2_frame.pack(side="left", padx=10)
        ctk.CTkLabel(model2_frame, text="Player O (Second)").pack()
        self.model2_var = ctk.StringVar(value=self.model2)
        model2_dropdown = ctk.CTkOptionMenu(
            model2_frame,
            variable=self.model2_var,
            values=self.available_models
        )
        model2_dropdown.pack()
        
        # Tournament progress
        self.progress_frame = ctk.CTkFrame(self.window)
        self.progress_frame.pack(pady=10)
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Game 0/10",
            font=("Arial", 16)
        )
        self.progress_label.pack(padx=10)
        
        # Scoreboard
        scoreboard_frame = ctk.CTkFrame(self.window)
        scoreboard_frame.pack(pady=10, padx=10)
        ctk.CTkLabel(scoreboard_frame, text="Scoreboard", font=("Arial", 18)).pack(pady=5,padx=10)
        
        self.score_labels = {}
        for player in ["X", "O", "Draw"]:
            frame = ctk.CTkFrame(scoreboard_frame)
            frame.pack(pady=5, padx=5)
            ctk.CTkLabel(frame, text=f"Player {player}:" if player != "Draw" else "Draws:").pack(side="left", padx=5)
            self.score_labels[player] = ctk.CTkLabel(frame, text="0")
            self.score_labels[player].pack(side="left", padx=5)
        
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
        self.status_label = ctk.CTkLabel(self.window, text="Press Start Tournament to begin", font=("Arial", 16))
        self.status_label.pack(pady=20)
        
        # Control buttons
        control_frame = ctk.CTkFrame(self.window)
        control_frame.pack(pady=10)
        
        self.start_button = ctk.CTkButton(
            control_frame,
            text="Start Tournament",
            command=self.start_tournament
        )
        self.start_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(
            control_frame,
            text="Stop",
            command=self.stop_tournament,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)
    
    def update_board(self):
        for i in range(3):
            for j in range(3):
                idx = i * 3 + j
                self.buttons[i][j].configure(text=self.game.board[idx])
    
    def update_scoreboard(self):
        for player in self.scores:
            self.score_labels[player].configure(text=str(self.scores[player]))
        self.progress_label.configure(text=f"Game {self.games_played}/{self.total_games}")
    
    def start_tournament(self):
        self.tournament_active = True
        self.games_played = 0
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.update_scoreboard()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="Tournament started!")
        
        # Start the tournament in a separate thread
        threading.Thread(target=self.tournament_loop, daemon=True).start()
    
    def stop_tournament(self):
        self.tournament_active = False
        self.game_active = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Tournament stopped!")
    
    def tournament_loop(self):
        while self.tournament_active and self.games_played < self.total_games:
            self.game = TicTacToe()
            self.game_active = True
            self.games_played += 1
            self.window.after(0, self.update_board)
            
            # Run a single game
            while self.game_active and self.tournament_active:
                current_model = self.model1_var.get() if self.game.current_player == "X" else self.model2_var.get()
                self.status_label.configure(
                    text=f"Game {self.games_played}/{self.total_games} - Player {self.game.current_player} ({current_model}) is thinking..."
                )
                
                try:
                    move = get_move_from_model(current_model, self.game, self.game.current_player)
                    if move is not None and self.game.make_move(move):
                        self.window.after(0, self.update_board)
                        time.sleep(0.5)  # Shorter delay for tournament mode
                        
                        winner = self.game.check_winner()
                        if winner:
                            if winner == "Draw":
                                self.scores["Draw"] += 1
                                self.status_label.configure(text=f"Game {self.games_played} ended in a Draw!")
                            else:
                                self.scores[winner] += 1
                                self.status_label.configure(text=f"Game {self.games_played} - Player {winner} wins!")
                            self.window.after(0, self.update_scoreboard)
                            self.game_active = False
                            time.sleep(1)  # Pause between games
                            break
                except Exception as e:
                    self.status_label.configure(text=f"Error: {str(e)}")
                    self.tournament_active = False
                    break
        
        if self.games_played >= self.total_games:
            # Determine the tournament winner
            max_score = max(self.scores["X"], self.scores["O"])
            if self.scores["X"] == self.scores["O"]:
                winner_text = "Tournament ended in a tie!"
            else:
                winner = "X" if self.scores["X"] > self.scores["O"] else "O"
                model_name = self.model1_var.get() if winner == "X" else self.model2_var.get()
                winner_text = f"Tournament Winner: Player {winner} ({model_name})!"
            
            self.status_label.configure(text=winner_text)
            self.tournament_active = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TicTacToeGUI()
    app.run()
