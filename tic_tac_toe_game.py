import requests
import json
import time

class SplitOrSteal:
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
        return "\n---------\n".join(["|".join(row) for row in rows])
    
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

def get_move_from_model(model_name, game):
    # Convert history to text format
    history_text = ""
    for round in game.history:
        history_text += f"Round {round['round']}: User chose {round['user_choice']}, AI chose {round['llm_choice']}\n"
    
    prompt = f"""You are playing Split or Steal game. Here's the game history:

{history_text}

Based on this history, choose either "Split" or "Steal" for the next move.
Also provide a brief explanation for your choice and a prediction about the user's next move.
Format your response exactly like this:
Choice: Split
Explanation: I choose split because of the pattern of cooperation.
Prediction: The user will likely split next round."""
    
    while True:
        try:
            response = ask_ollama(model_name, prompt)
            move = int(response.strip())
            if move in valid_moves:
                return move
        except (ValueError, AttributeError):
            continue

def main():
    model_name = "llama2"  # or whatever model you're using
    game = SplitOrSteal()
    
    print(f"Starting 100 Tic Tac Toe games between {model1} (X) and {model2} (O)")
    
    for game_num in range(100):
        game = TicTacToe()
        print(f"\nGame {game_num + 1}/100")
        
        # Get user input
        while True:
            user_choice = input("\nEnter your choice (Split/Steal): ").capitalize()
            if user_choice in ['Split', 'Steal']:
                break
    
    print("\nFinal scores after 100 games:")
    print(f"{model1} (X): {scores['X']} wins")
    print(f"{model2} (O): {scores['O']} wins")
    print(f"Draws: {scores['Draw']}")

if __name__ == "__main__":
    main()