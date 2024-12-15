# ex-machina

Compare two LLaMA models in a Tic Tac Toe game.

1. Install ollama https://ollama.com/

2. Run:
```
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.2:1b
ollama pull llama3.2:3b
python play.py
```
