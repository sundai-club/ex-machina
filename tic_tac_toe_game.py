import requests
import json
import time

class TicTacToe:
    def __init__(self):
        self.board = [" " for _ in range(9)]
        self.current_player = "X"
    
    def make_move(self, position):
        if self.board[position] == " ":
            self.board[position] = self.current_player
            self.current_player = "O" if self.current_player == "X" else "X"
            return True
        return False
    
    def check_winner(self):
        # Check rows
        for i in range(0, 9, 3):
            if self.board[i] == self.board[i+1] == self.board[i+2] != " ":
                return self.board[i]
        
        # Check columns
        for i in range(3):
            if self.board[i] == self.board[i+3] == self.board[i+6] != " ":
                return self.board[i]
        
        # Check diagonals
        if self.board[0] == self.board[4] == self.board[8] != " ":
            return self.board[0]
        if self.board[2] == self.board[4] == self.board[6] != " ":
            return self.board[2]
        
        # Check for draw
        if " " not in self.board:
            return "Draw"
        
        return None
    
    def get_board_state(self):
        rows = [self.board[i:i+3] for i in range(0, 9, 3)]
        return "\n-----\n".join(["|".join(row) for row in rows])
    
    def get_valid_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == " "]

def ask_ollama(model_name, prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)  # 30 second timeout
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["response"]
    except requests.Timeout:
        print(f"Request to Ollama timed out after 30 seconds")
        return "timeout"
    except requests.RequestException as e:
        print(f"Error communicating with Ollama: {str(e)}")
        return "error"

def get_move_from_model(model_name, game, player_symbol):
    board_state = game.get_board_state()
    valid_moves = game.get_valid_moves()
    
    prompt = f"""You are playing Tic Tac Toe as player {player_symbol}. Here's the current board state:

{board_state}

Valid moves are the following positions (0-8): {valid_moves}
Choose one position number from the valid moves.
Respond with ONLY the number, nothing else."""
    
    while True:
        try:
            response = ask_ollama(model_name, prompt)
            if response in ["timeout", "error"]:
                continue
            move = int(response.strip())
            if move in valid_moves:
                return move
        except (ValueError, AttributeError):
            continue

def main():
    model1 = "llama3.2:1b"  # First player (X)
    model2 = "llama3.2:3b"  # Second player (O)
    scores = {"X": 0, "O": 0, "Draw": 0}
    
    rounds = 10    # Number of games
    print(f"Starting {rounds} Tic Tac Toe games between {model1} (X) and {model2} (O)")
    
    for game_num in range(rounds):
        game = TicTacToe()
        print(f"\nGame {game_num + 1}/{rounds}")
        
        while True:
            print("\nCurrent board:")
            print(game.get_board_state())
            
            current_model = model1 if game.current_player == "X" else model2
            print(f"\n{current_model}'s turn ({game.current_player})")
            
            move = get_move_from_model(current_model, game, game.current_player)
            game.make_move(move)
            
            winner = game.check_winner()
            if winner:
                print("\nFinal board:")
                print(game.get_board_state())
                
                if winner == "Draw":
                    print("\nGame ended in a draw!")
                    scores["Draw"] += 1
                else:
                    model_name = model1 if winner == "X" else model2
                    print(f"\n{model_name} ({winner}) wins!")
                    scores[winner] += 1
                    
                print(f"\nCurrent scores - {model1} (X): {scores['X']}, {model2} (O): {scores['O']}, Draws: {scores['Draw']}")
                break
    
    print(f"\nFinal scores after {rounds} games:")
    print(f"{model1} (X): {scores['X']} wins")
    print(f"{model2} (O): {scores['O']} wins")
    print(f"Draws: {scores['Draw']}")

if __name__ == "__main__":
    main()