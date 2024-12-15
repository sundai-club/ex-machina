import requests
import json
import time
import random

# Model configurations
MODEL_1 = "llama3.2:3b"
MODEL_1_NAME = "Llama3.2 3B"
MODEL_2 = "llama3.2:1b"
MODEL_2_NAME = "Llama3.2 1B"

def get_ollama_response(model: str, prompt: str) -> str:
    """Get response from Ollama model."""
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        print(f"Error getting response from {model}: {e}")
        return ""

def format_game_history(history):
    """Format game history for model context."""
    if not history:
        return "No previous rounds played."
    
    formatted = "Previous rounds:\n"
    for round_num, round_data in enumerate(history, 1):
        formatted += f"Round {round_num}:\n"
        formatted += f"{MODEL_1_NAME}: {round_data['llama_3b']}\n"
        formatted += f"{MODEL_2_NAME}: {round_data['llama_1b']}\n"
        formatted += f"Result: {round_data['result']}\n"
    return formatted

def get_decision(model: str, model_name: str, opponent_name: str, history: list) -> str:
    """Get split or steal decision from a model."""
    game_context = f"""
You are playing the Split or Steal game with {opponent_name}. 
In this game, both players must choose either 'split' or 'steal'.
- If both players choose 'split', each gets 50 points
- If one chooses 'split' and other 'steal', the one who chose 'steal' gets 100 points, other gets 0
- If both choose 'steal', both get 0 points

{format_game_history(history)}

Make your decision: respond with ONLY the word 'split' or 'steal'.
Think strategically about maximizing your points while considering the opponent's likely behavior.
"""
    
    response = get_ollama_response(model, game_context).lower().strip()
    # Ensure valid response
    if response not in ['split', 'steal']:
        print(f"Invalid response from {model_name}: {response}. Defaulting to split.")
        return 'split'
    return response

def calculate_round_result(decision1: str, decision2: str) -> tuple:
    """Calculate points for both players based on their decisions."""
    if decision1 == 'split' and decision2 == 'split':
        return 50, 50
    elif decision1 == 'steal' and decision2 == 'split':
        return 100, 0
    elif decision1 == 'split' and decision2 == 'steal':
        return 0, 100
    else:  # both steal
        return 0, 0

def play_game(rounds: int = 10):
    """Play the Split or Steal game between {MODEL_1_NAME} and {MODEL_2_NAME}."""
    history = []
    model_1_total = 0
    model_2_total = 0
    
    print(f"Starting Split or Steal game between {MODEL_1_NAME} and {MODEL_2_NAME}")
    print("-" * 50)
    
    for round_num in range(1, rounds + 1):
        print(f"\nRound {round_num}:")
        
        # Get decisions
        model_1_decision = get_decision(MODEL_1, MODEL_1_NAME, MODEL_2_NAME, history)
        model_2_decision = get_decision(MODEL_2, MODEL_2_NAME, MODEL_1_NAME, history)
        
        # Calculate results
        points_1, points_2 = calculate_round_result(model_1_decision, model_2_decision)
        model_1_total += points_1
        model_2_total += points_2
        
        # Record round results
        round_result = f"{MODEL_1_NAME} got {points_1} points, {MODEL_2_NAME} got {points_2} points"
        history.append({
            'llama_3b': model_1_decision,
            'llama_1b': model_2_decision,
            'result': round_result
        })
        
        # Print round results
        print(f"{MODEL_1_NAME} chose: {model_1_decision}")
        print(f"{MODEL_2_NAME} chose: {model_2_decision}")
        print(f"Round result: {round_result}")
        print(f"Current totals - {MODEL_1_NAME}: {model_1_total}, {MODEL_2_NAME}: {model_2_total}")
        
        # Add small delay between rounds
        time.sleep(1)
    
    print("\nGame Over!")
    print("Final scores:")
    print(f"{MODEL_1_NAME}: {model_1_total} points")
    print(f"{MODEL_2_NAME}: {model_2_total} points")
    
    if model_1_total > model_2_total:
        print(f"{MODEL_1_NAME} wins!")
    elif model_2_total > model_1_total:
        print(f"{MODEL_2_NAME} wins!")
    else:
        print("It's a tie!")

if __name__ == "__main__":
    play_game()
