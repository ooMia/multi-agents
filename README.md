# instructions

```sh
source .venv/bin/activate
uv sync

ollama create llama3.2 -f ./Modelfile
ollama serve
ollama ps

uv format --preview-features format
uv run main.py

pytest --lf
```

```sh
git init
touch .gitignore
uv venv -p 3.13

ollama pull llama3.2
ollama list

uv add pytest --dev
uv add ollama
```

```sh
git checkout -b develop
```
